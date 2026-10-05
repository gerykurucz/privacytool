import os
import time
import cv2
import numpy as np
import win32api
import win32con


def _get_screen_size():
    """Primary-monitor size without the heavy pyautogui dependency."""
    try:
        return (win32api.GetSystemMetrics(win32con.SM_CXSCREEN),
                win32api.GetSystemMetrics(win32con.SM_CYSCREEN))
    except Exception:
        from pyautogui import size as _pyautogui_size
        screen_size = _pyautogui_size()
        return (screen_size.width, screen_size.height)


class CaptureBackend:
    """Common capture interface. grab() takes a (left, top, right, bottom)
    region and returns a BGR numpy image, or None if no fresh frame is
    available yet. Hard failures raise."""
    name = 'base'

    def grab(self, region):
        raise NotImplementedError

    def release(self):
        pass


class DXCamBackend(CaptureBackend):
    """Fast GPU (DXGI) capture. Unavailable where DXGI desktop duplication
    is unsupported (RDP sessions, VMs, some drivers) - see MSSBackend."""
    name = 'dxcam'

    def __init__(self):
        self.cam = None
        import dxcam
        cam = dxcam.create(output_color='BGR')
        if cam is None:
            raise RuntimeError('dxcam.create() returned None')
        self.cam = cam

    def grab(self, region):
        return self.cam.grab(region)

    def release(self):
        cam, self.cam = self.cam, None
        if cam is not None:
            try:
                cam.release()
            except Exception:
                pass


class MSSBackend(CaptureBackend):
    """Slower GDI-based capture, but works where DXGI duplication is
    unsupported (RDP, VMs, problem drivers)."""
    name = 'mss'

    def __init__(self):
        self.sct = None
        try:
            import mss as _mss
            self.sct = _mss.MSS()
        except ImportError as e:
            raise RuntimeError('mss library is required for the fallback capture '
                               'backend (pip install mss)') from e

    def grab(self, region):
        left, top, right, bottom = (int(v) for v in region)
        width = max(right - left, 1)
        height = max(bottom - top, 1)
        shot = self.sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        # frombuffer() is read-only; copy so callers can draw overlays in place
        bgra = np.frombuffer(shot.bgra, dtype=np.uint8).reshape(shot.height, shot.width, 4).copy()
        return cv2.cvtColor(bgra, cv2.COLOR_BGRA2BGR)

    def release(self):
        sct, self.sct = self.sct, None
        if sct is not None:
            try:
                sct.close()
            except Exception:
                pass


class Screen:
    def __init__(self, config, backend=None):
        self.cfg = config
        # Auto mode (default): try dxcam, fall back to mss. Force one with
        # the backend parameter or the SNAPPY_CAPTURE env var ('dxcam'/'mss').
        if backend is None:
            backend = os.environ.get('SNAPPY_CAPTURE', '').strip().lower() or None
        self._auto_backend = backend is None
        self.backend = None
        self._fallback_active = False
        self._create_backend(backend)

        if self.cfg.auto_detect_resolution:
            self.screen = _get_screen_size()
        else:
            self.screen = (self.cfg.resolution_x, self.cfg.resolution_y)

        self.screen_center = (self.screen[0] // 2, self.screen[1] // 2)
        self.screen_region = (0, 0, self.screen[0], self.screen[1])
        self.area = (self.cfg.capture_area_x, self.cfg.capture_area_y)
        self.area_center = (self.area[0] // 2, self.area[1] // 2)
        self.area_region = (
            self.screen_center[0] - self.area[0] // 2,
            self.screen_center[1] - self.area[1] // 2 - self.cfg.screen_center_offset,
            self.screen_center[0] + self.area[0] // 2,
            self.screen_center[1] + self.area[1] // 2 - self.cfg.screen_center_offset
        )
        self.dilated = None
        self.target = None
        self.closest_contour = None
        self.closest_rect = None
        self.img = None
        self.focus_area = (self.cfg.focus_area_x, self.cfg.focus_area_y)
        self.dilate_kernel = np.ones(
            (self.cfg.group_close_target_blobs_threshold[0], self.cfg.group_close_target_blobs_threshold[1]),
            np.uint8
        )
        self.click_test_points = [
            (self.area_center[0], self.area_center[1]),
            (self.area_center[0] + self.cfg.click_threshold, self.area_center[1]),
            (self.area_center[0] - self.cfg.click_threshold, self.area_center[1]),
            (self.area_center[0], self.area_center[1] + self.cfg.click_threshold),
            (self.area_center[0], self.area_center[1] - self.cfg.click_threshold),
        ]

        # Setup debug display
        if self.cfg.debug:
            self.display_mode = self.cfg.display_mode
            self.window_name = 'Python'
            self.window_resolution = (self.screen[0] // 2, self.screen[1] // 2)
            cv2.namedWindow(self.window_name)

    def _create_backend(self, backend):
        """Create the requested backend; in auto mode fall back to mss."""
        if backend is None:
            candidates = ('dxcam', 'mss')
        elif backend in ('dxcam', 'mss'):
            candidates = (backend,)
        else:
            raise ValueError(f"Unknown capture backend: {backend!r} (expected 'dxcam' or 'mss')")
        errors = []
        for name in candidates:
            try:
                self.backend = DXCamBackend() if name == 'dxcam' else MSSBackend()
                if errors:
                    self._fallback_active = True
                    print(f'WARNING: capture backend {candidates[0]!r} failed ({errors[0]}); '
                          f'using {name!r} fallback')
                else:
                    print(f'Capture backend: {name}')
                return
            except Exception as e:
                errors.append(e)
        raise RuntimeError(f'No working capture backend (tried {", ".join(candidates)}): {errors[0]}')

    def _switch_to_fallback(self, error):
        """Swap a dying dxcam backend for mss at runtime. Returns True on success."""
        if not self._auto_backend or self._fallback_active:
            return False
        try:
            new_backend = MSSBackend()
        except Exception:
            return False
        old, self.backend = self.backend, new_backend
        try:
            old.release()
        except Exception:
            pass
        self._fallback_active = True
        print(f'WARNING: capture backend failed ({error}); switched to mss fallback')
        return True

    def close(self):
        backend, self.backend = self.backend, None
        if backend is not None:
            try:
                backend.release()
            except Exception:
                pass
        if self.cfg.debug:
            try:
                cv2.destroyWindow(self.window_name)
            except Exception:
                pass

    def screenshot(self, region):
        if self.backend is None:
            raise RuntimeError('Screen capture backend is closed')
        deadline = time.monotonic() + 5.0
        backend_error = None
        while True:
            try:
                image = self.backend.grab(region)
            except Exception as e:
                image = None
                backend_error = e
                if self._switch_to_fallback(e):
                    backend_error = None
                    continue
            if image is not None:
                return image
            if time.monotonic() >= deadline:
                raise RuntimeError(f'Screen capture timed out ({self.backend.name}): {backend_error}')
            time.sleep(0.001)

    @staticmethod
    def get_region(region, help_offset):
        return (
            region[0],
            region[1] - help_offset,
            region[2],
            region[3] - help_offset
        )

    def _is_within_focus_area(self, x, y):
        """Check if a point is within the focus area bounds."""
        return -self.focus_area[0] <= x <= self.focus_area[0] and -self.focus_area[1] <= y <= self.focus_area[1]

    def _check_click(self, contour, rect):
        """Check if the crosshair is inside the target contour with a bounding-box pre-filter."""
        cx, cy, cw, ch = rect
        if not (
            cx <= self.area_center[0] - self.cfg.click_threshold and
            self.area_center[0] + self.cfg.click_threshold <= cx + cw and
            cy <= self.area_center[1] - self.cfg.click_threshold and
            self.area_center[1] + self.cfg.click_threshold <= cy + ch
        ):
            return False

        points = self.click_test_points
        return all(cv2.pointPolygonTest(contour, pt, False) >= 0 for pt in points)

    def get_target(self, help_offset):
        help_offset = int(help_offset)

        self.target = None
        click = False
        self.closest_contour = None
        self.closest_rect = None

        self.img = self.screenshot(self.get_region(self.area_region, help_offset))
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.cfg.lower_color, self.cfg.upper_color)

        self.dilated = cv2.dilate(mask, self.dilate_kernel, iterations=5)

        contours, _ = cv2.findContours(self.dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) != 0:
            min_distance_sq = float('inf')
            for contour in contours:
                rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
                x = rect_x + rect_w // 2 - self.area_center[0]
                y = int(rect_y + rect_h * (1 - self.cfg.focus_height)) - self.area_center[1]

                distance_sq = x * x + y * y
                if distance_sq < min_distance_sq:
                    min_distance_sq = distance_sq
                    self.closest_contour = contour
                    self.closest_rect = (rect_x, rect_y, rect_w, rect_h)
                    if self._is_within_focus_area(x, y):
                        self.target = (x, y)

            if self.closest_contour is not None and self._check_click(self.closest_contour, self.closest_rect):
                click = True

        if self.cfg.debug:
            self.run_debug_window(help_offset)

        return self.target, click

    def _draw_target_overlay(self, debug_img):
        """Draw target line and bounding box on the debug image."""
        if self.target is not None:
            debug_img = cv2.line(
                debug_img,
                self.area_center,
                (self.target[0] + self.area_center[0], self.target[1] + self.area_center[1]),
                (0, 255, 0),
                2
            )

        if self.closest_contour is not None:
            x, y, w, h = self.closest_rect
            debug_img = cv2.rectangle(
                debug_img,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

        return debug_img

    def _draw_area_overlay(self, debug_img):
        """Draw area and focus area rectangles on the debug image."""
        debug_img = cv2.rectangle(
            debug_img,
            (0, 0),
            (self.area[0], self.area[1]),
            (0, 255, 0),
            2
        )

        debug_img = cv2.rectangle(
            debug_img,
            (
                self.area[0] // 2 - self.focus_area[0] // 2,
                self.area[1] // 2 - self.focus_area[1] // 2
            ),
            (
                self.area[0] // 2 + self.focus_area[0] // 2,
                self.area[1] // 2 + self.focus_area[1] // 2
            ),
            (0, 255, 255),
            2
        )

        return debug_img

    def _show_fullscreen_debug(self, debug_img, help_offset):
        """Show the debug overlay composited onto a full-screen screenshot."""
        full_img = self.screenshot(self.screen_region)

        offset_x = (self.screen[0] - self.area[0]) // 2
        offset_y = (self.screen[1] - self.area[1]) // 2 - self.cfg.screen_center_offset - help_offset
        full_img[offset_y:offset_y+debug_img.shape[0], offset_x:offset_x+debug_img.shape[1]] = debug_img

        full_img = cv2.rectangle(
            full_img,
            (self.screen_center[0] - 5, self.screen_center[1] - 5),
            (self.screen_center[0] + 5, self.screen_center[1] + 5),
            (255, 255, 255),
            1
        )
        full_img = cv2.resize(full_img, self.window_resolution)
        cv2.imshow(self.window_name, full_img)

    def _show_area_debug(self, debug_img):
        """Show only the area region debug overlay."""
        debug_img = cv2.line(
            debug_img,
            (self.area_center[0] - 5, self.area_center[1]),
            (self.area_center[0] + 5, self.area_center[1]),
            (255, 255, 255),
            1
        )
        debug_img = cv2.line(
            debug_img,
            (self.area_center[0], self.area_center[1] - 5),
            (self.area_center[0], self.area_center[1] + 5),
            (255, 255, 255),
            1
        )
        cv2.imshow(self.window_name, debug_img)

    def run_debug_window(self, help_offset):
        if self.display_mode == 'game':
            debug_img = self.img
        else:
            debug_img = cv2.cvtColor(self.dilated, cv2.COLOR_GRAY2BGR)

        debug_img = self._draw_target_overlay(debug_img)
        debug_img = self._draw_area_overlay(debug_img)

        if self.cfg.debug_fullscreen_capture:
            self._show_fullscreen_debug(debug_img, help_offset)
        else:
            self._show_area_debug(debug_img)

        cv2.waitKey(1)
