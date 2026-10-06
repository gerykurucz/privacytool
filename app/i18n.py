"""Runtime localisation (v8.39).

The GUI is translatable WITHOUT restarting: every user-visible string
goes through L(key), and a language change re-runs the GUI's registered
re-text closures, so tabs, buttons, labels and the status bar switch
while the window stays open.  The choice persists in config.json as
"language".

Catalogs are partial by design and fall back key-by-key:

    L(key)  ->  STRINGS[current][key]  ->  STRINGS["en"][key]  ->  key

and for setting labels/descriptions the GUI falls back once more to the
English META table, so a locale may ship the chrome only and still show
a complete (mixed) interface instead of missing text.  The language
window prints each locale's coverage, computed over the key list the
GUI registers at start-up, so nobody is lied to about completeness.

Adding a language is a data-only change: one entry in LANGUAGES and one
dict in STRINGS.  Nothing else in the product knows about languages.
"""

FALLBACK = "en"

# (code, native name, English name) - the chooser shows the native name
# first, because that is the one a person recognises as "mine".
LANGUAGES = [
    ("en", "English", "English"),
    ("de", "Deutsch", "German"),
    ("es", "Español", "Spanish"),
    ("fr", "Français", "French"),
    ("it", "Italiano", "Italian"),
    ("pt", "Português", "Portuguese"),
    ("nl", "Nederlands", "Dutch"),
    ("pl", "Polski", "Polish"),
    ("ru", "Русский", "Russian"),
    ("uk", "Українська", "Ukrainian"),
    ("tr", "Türkçe", "Turkish"),
    ("sw", "Kiswahili", "Swahili"),
    ("hu", "Magyar", "Hungarian"),
    ("zh", "中文（简体）", "Chinese (Simplified)"),
    ("ja", "日本語", "Japanese"),
    ("ko", "한국어", "Korean"),
]

STRINGS = {
    # ---------------- English: the source of truth ----------------
    "en": {
        "st.defaults_restored": "Defaults restored.",
        "btn.apply": "Apply",
        "btn.export": "Export Config",
        "btn.import": "Import Config",
        "btn.language": "Language: %s",
        "btn.launch": "Launch",
        "btn.logout": "Log Out",
        "btn.pause": "Pause",
        "btn.restore": "Restore Defaults",
        "col.accent": "Accent",
        "col.add_pref": "Add to preferred colours",
        "col.add_ref": "Add to refused colours",
        "col.chip_desc": "rgb(%d, %d, %d) in %s - click the box to "
            "remove this colour.",
        "col.chip_off": "%s holds no colours - the crossed-out box "
            "means off. Pick a colour below and press the matching "
            "add button.",
        "col.exclude": "Exclude",
        "col.pick": "Pick color from screen",
        "col.suggest": "Suggest colors from screen",
        "desc.default": "Hover over a setting name to see what it "
            "does.",
        "lang.close": "Close",
        "lang.coverage": "%d%% translated",
        "lang.current": "Current: %s",
        "lang.progress": "Still being translated, offered as soon as "
            "complete: %s",
        "lang.prompt": "Changes apply immediately - the window stays "
            "open so you can try several.",
        "lang.title": "Language",
        "lbl.key_play_n": "Hotkey: Play recording #%d",
        "lbl.macro_action": "Macro %d: sends combo",
        "lbl.macro_key": "Macro %d: trigger key",
        "mac.delete": "Delete",
        "mac.empty": "No recordings yet - launch, press your record "
            "shortcut and work normally: every key, click and cursor "
            "move is captured.",
        "mac.export": "Export",
        "mac.import": "Import",
        "mac.keys_head": "Key macros",
        "mac.loop": "Repeat until stopped",
        "mac.recordings": "Recordings",
        "mac.rename": "Rename",
        "mac.sends": "sends",
        "mac.steps": "%d steps",
        "st.color_added": "Added rgb(%d, %d, %d) to %s - press Apply "
            "to save.",
        "st.color_already": "rgb(%d, %d, %d) is already in %s.",
        "st.color_full": "%s already holds 15 colours - click one of "
            "its boxes to remove a colour first.",
        "st.color_removed": "Removed rgb(%d, %d, %d) from %s - press "
            "Apply to save.",
        "st.follow": "  |  follow %ds ago",
        "st.line": "Assisted %d  |  passed %d%s  |  theme: %s",
        "st.running": "Running..",
        "st.standby": "Standby..",
        "tab.advanced": "Advanced",
        "tab.assist": "Assistance",
        "tab.colors": "Colors",
        "tab.experimental": "Experimental",
        "tab.handler": "Handler",
        "tab.help": "Help",
        "tab.hotkeys": "Keybindings",
        "tab.macros": "Macros",
        "word.off": "Off",
        "word.on": "On",
    },
    "de": {
        "btn.apply": "Übernehmen",
        "btn.export": "Konfiguration exportieren",
        "btn.import": "Konfiguration importieren",
        "btn.language": "Sprache: %s",
        "btn.launch": "Starten",
        "btn.logout": "Abmelden",
        "btn.pause": "Pause",
        "btn.restore": "Standard wiederherstellen",
        "col.accent": "Akzent",
        "col.add_pref": "Als bevorzugt hinzufügen",
        "col.add_ref": "Als abgelehnt hinzufügen",
        "col.chip_desc": "rgb(%d, %d, %d) in %s - klicken Sie das "
            "Feld an, um diese Farbe zu entfernen.",
        "col.chip_off": "%s enthält keine Farben - das "
            "durchgestrichene Feld bedeutet aus. Wählen Sie unten "
            "eine Farbe und drücken Sie den passenden "
            "Hinzufügen-Knopf.",
        "col.exclude": "Ausschluss",
        "col.pick": "Farbe vom Bildschirm holen",
        "col.rgb.desc": "Drei Felder zeigen die Farbe, die gerade im "
            "Mischer steht: das erste leuchtet umso heller, je mehr "
            "Rot sie enthält, das zweite für Grün, das dritte für "
            "Blau - heller bedeutet mehr. Die Zeile folgt dem "
            "Mischer, den Fertigtönen und den Bildschirm-Tasten; "
            "tippen ist nicht möglich.",
        "col.rgb.name": "Aktueller RGB-Wert",
        "col.suggest": "Bildschirmfarben finden",
        "desc.accent_boost": "Wie sehr Ihre Farbe den Wert eines "
            "Elements hebt (0-3). Erhöhen Sie auf 1,5-2, wenn "
            "trotzdem das falsche Element gewinnt.",
        "desc.accent_coherent": "Ihre Farbe muss einen "
            "zusammenhängenden Fleck bilden, um zu zählen - "
            "verstreute Dither- oder Kompressions-Spritzer "
            "qualifizieren kein Element, boosten keins und setzen "
            "keins auf die Niemals-Klick-Liste.",
        "desc.accent_color": "Die Farbe, die Snappy AI bevorzugen "
            "soll, gezeigt als Farbfelder rechts. Wählen Sie unten "
            "eine Farbe und drücken Sie «Als bevorzugt hinzufügen», "
            "um sie hinzuzufügen - höchstens fünfzehn Felder; ein "
            "Klick auf ein Feld entfernt die Farbe wieder. Elemente "
            "mit einer davon gewinnen bei Gleichstand. Eine leere "
            "Liste zeigt ein durchgestrichenes Feld und schaltet "
            "aus.",
        "desc.accent_matcher": "Wie Farben verglichen werden. "
            "Perzeptuell ordnet nach dem tatsächlichen Aussehen und "
            "ist empfohlen; Klassisch ist das ältere Verfahren zum "
            "Vergleich.",
        "desc.accent_only": "Nur Elemente, die Ihre Farbe enthalten, "
            "werden assistiert; Klicks woanders gehen unverändert an "
            "Windows.",
        "desc.accent_soft": "0-100: Wie stark hellere, dunklere oder "
            "verwaschene Versionen Ihrer Farbe dennoch zählen. 0 = "
            "nur exakte Töne.",
        "desc.accent_tolerance": "Wie nahe eine Farbe Ihrer kommen "
            "muss (4-90). Niedriger = strenger.",
        "desc.accent_variants": "Hellere und dunklere Kopien Ihrer "
            "Farbe zählen mit, damit Hover-, Drück- und "
            "Dimm-Zustände gelten, ohne die Farbton-Toleranz zu "
            "weiten. Nur Helligkeit - ein falscher Farbton kann nie "
            "mitfahren.",
        "desc.adaptive_threshold": "Dunkle Designs und verwaschene "
            "Dokumente senken ihre eigene Erkennungslatte "
            "automatisch, damit auch schwache Elemente gefunden "
            "werden. Empfohlen.",
        "desc.auto_click": "Eingeschaltet klickt das Programm alle 0,1 Sekunden von selbst auf "
            "das beste Element im beobachteten Bereich – zuerst nach Kontrast "
            "sortiert. Ist eine Akzentfarbe gesetzt, kommen nur Elemente mit "
            "dieser Farbe infrage; ohne Farbe werden nur sehr scharf "
            "gezeichnete Elemente geklickt. Dasselbe Feld nicht zweimal, "
            "eigenes Fenster nie.",
        "desc.auto_click_interval": "Wie oft der Bildschirm nach "
            "Ihrer Farbe schaut (0,5-60). Eine langsame Zahl ist die "
            "sichere: 2-5 passt zu einem Dialog, den Sie beobachten.",
        "desc.auto_click_max_clicks": "Wie oft es nach dem Starten "
            "von selbst klicken darf (1-200). Am Limit hält es an "
            "und meldet sich, damit eine falsche Einstellung nicht "
            "davonlaufen kann.",
        "desc.auto_click_min_contrast": "Auf derselben Skala wie "
            "»Mindeste Schärfe einer Kante«. Beim Standard beginnen "
            "und erhöhen, wenn Falsches geklickt wird: Nur starke, "
            "klar gezeichnete Elemente zählen dann.",
        "desc.auto_click_radius": "Auto-Klick sucht um die "
            "Bildschirmmitte (40-600 px). Größer für ein volles "
            "Fenster; kleiner, damit es nur das eine Bedienelement "
            "in der Mitte je sieht.",
        "desc.auto_click_repeat_px": "Nach einem Auto-Klick wird ein "
            "Ziel innerhalb so vieler Pixel in Ruhe gelassen "
            "(0-400). Ohne das würde eine Schaltfläche, die stehen "
            "bleibt, immer wieder geklickt.",
        "desc.auto_click_settle_ms": "Der Cursor ruht so lange auf "
            "dem Ziel (0-2000 ms), bevor der Klick fällt, damit das "
            "Programm die Markierung zuerst sieht. 120 passt für die "
            "meisten Fenster.",
        "desc.block_bound_keys": "Aus (Standard): Ein Kürzel ohne "
            "Strg/Alt/Shift - wie 1 oder V - wirkt in jedem Programm "
            "UND tippt die Taste normal, löst also mitten im Satz "
            "auch die Aktion aus. An: Die Aktion feuert weiterhin "
            "überall, aber die Taste tippt nicht mehr.",
        "desc.capture_backend": "Wie der Bildschirm fotografiert "
            "wird. Automatisch nutzt die Kompatibel-Methode und sieht damit fast alle Fenster; "
            "Kompatibel funktioniert immer, auch mit Remotedesktop "
            "und virtuellen Maschinen. Gilt nach Neustart.",
        "desc.color_adapt": "Jedes Element wird vor dem Abgleich am "
            "eigenen Hintergrund weißabgeglichen, damit Nachtmodus "
            "und Design-Färbungen Ihre Farbe nicht aus der Toleranz "
            "schieben. Nur zum Vergleich mit dem unangepassten "
            "Verfahren ausschalten.",
        "desc.contrast_threshold": "Niedriger findet schwächere "
            "Elemente (und mehr Rauschen); höher verlangt kräftigere "
            "Kanten.",
        "desc.default": "Zeigen Sie auf einen Einstellungsnamen, um "
            "seine Wirkung zu lesen.",
        "desc.exclude_color": "Elemente mit diesen Farben werden nie "
            "assistiert: Klicks darauf gehen direkt an Windows, in "
            "beiden Modi. Gezeigt als Farbfelder rechts - wählen Sie "
            "unten eine Farbe und drücken Sie «Als abgelehnt "
            "hinzufügen», um eines zu ergänzen (höchstens fünfzehn); "
            "ein Klick auf ein Feld entfernt es. Eine leere Liste "
            "zeigt ein durchgestrichenes Feld und schaltet aus.",
        "desc.follow_boost": "Wie stark das gemerkte Element bei "
            "Gleichstand gewinnt: 100% kann seinen Wert frisch "
            "verdoppeln, 25% ist ein leichter Schub.",
        "desc.follow_enabled": "Nach einem erfolgreichen Snap "
            "gewinnen ähnlich aussehende Elemente oder Elemente am "
            "selben Platz eine Zeit lang - praktisch für "
            "Scrollbalken und wiederholte Klicks auf ein "
            "Bedienelement.",
        "desc.follow_learn": "Nur Elemente in meiner Farbe: Ein "
            "Fehlklick woanders kann die Erinnerung nicht umlenken. "
            "Jeder erfolgreiche Snap: das alte, vertrauende "
            "Verhalten.",
        "desc.follow_seconds": "Sekunden, in denen das gemerkte "
            "Element nach Ihrem letzten erfolgreichen Snap bevorzugt "
            "bleibt (1-120).",
        "desc.glide_ms": "0 (Standard) springt sofort - am "
            "schnellsten. 40-120 gleitet, damit Sie zusehen können; "
            "eigene Mausbewegung bricht das Gleiten ab.",
        "desc.hold_follow": "Solange Sie die linke Taste direkt nach "
            "einem Snap gedrückt halten - oder auf dem gemerkten "
            "Element erneut drücken - bleibt der Cursor auf der "
            "Farbe dieses Elements; das beruhigt Ziehaktionen wie "
            "Scrollbalken. Drucke woanders werden nie angetastet.",
        "desc.key_launch": "Format: ctrl+l, f5, space, ctrl+alt+1 "
            "... Tasten: ctrl, alt, shift, win. Gilt nach "
            "Übernehmen.",
        "desc.key_mode1": "Kommagetrennt, z. B. '1, f1, ctrl+f1, v'. "
            "Was der Klassik-Modus tut, erklärt der Tab "
            "Tastenkürzel.",
        "desc.key_mode2": "Kommagetrennt, z. B. '2, f2, ctrl+f2, b'. "
            "Was der Führungs-Modus tut, erklärt der Tab "
            "Tastenkürzel.",
        "desc.key_pause": "Maus und Tastatur gehören wieder ganz "
            "Ihnen, bis Sie starten.",
        "desc.key_play": "Spielt die in der Makro-Liste gewählte "
            "Aufzeichnung, sonst die neueste. Bei einer "
            "wiederholenden Aufzeichnung stoppt es sie.",
        "desc.key_play_n": "Spielt Aufzeichnung #%d der nummerierten "
            "Liste auf dem Tab Makros, nach ihrer Position. Ist die "
            "Liste kürzer, passiert nichts.",
        "desc.key_record": "Zeichnet alles auf, was Sie tun - jede "
            "Taste, jeden Mausklick und jede Zeigerbewegung -, "
            "während Ihre Eingaben trotzdem Ihre Programme "
            "erreichen, bis das Stopp-Kürzel alles in die "
            "Makro-Liste speichert. Nur im gestarteten Zustand "
            "scharf.",
        "desc.key_record_stop": "Stoppt die Aufnahme, speichert die "
            "Folge in die Makro-Liste und beendet eine laufende "
            "Wiedergabe.",
        "desc.luminance_norm": "Kanten werden im Verhältnis zur "
            "Helligkeit ihrer Umgebung gewertet, sodass dunkle "
            "Designs wie helle funktionieren. Empfohlen.",
        "desc.macro_action": "Die Kombination, die pro Auslösedruck "
            "für Sie gedrückt wird (ein Druck = ein Kombi-Druck): "
            "'ctrl+c', 'ctrl+shift+s', 'space', 'f5' ... Leer = "
            "Makro aus.",
        "desc.macro_key": "Die Taste, die das Makro MEINT statt zu "
            "tippen: 'b', 'f7', 'ctrl+b' ... Im gestarteten Zustand "
            "sendet ein Druck die Kombination daneben genau einmal "
            "und die Taste erreicht Ihre Programme nicht. Pausiert "
            "tippt sie normal. Leer = Makro aus.",
        "desc.max_area": "Größere Flecken werden ignoriert - meist "
            "ganze Fenster oder Hintergrund, keine klickbaren "
            "Elemente.",
        "desc.max_dim": "Elemente breiter oder höher als das werden "
            "ignoriert; Elemente an einer Bildschirmkante, wie "
            "Scrollbalken, bekommen das Doppelte.",
        "desc.merge_distance": "Teile, die näher beieinander liegen "
            "(kaputte Umrisse, Symbol neben Beschriftung), werden "
            "ein Element. Zwei vollständige Elemente werden nie "
            "verklebt.",
        "desc.min_area": "Kleinere Flecken werden als Spritzer "
            "ignoriert, außer sie werden an ein größeres Element "
            "geklebt.",
        "desc.min_contrast": "Ein Element muss mindestens so scharf "
            "sein, um überhaupt klickbar zu sein. Werte unter 28 "
            "gelten als 28: eine eingebaute Qualitätsuntergrenze "
            "hält Rauschen davon ab, klickbar zu werden.",
        "desc.motion_3d": "Bewegte Elemente werden mit Position UND "
            "Größe verfolgt statt mit Geraden-Fit: Einzelne Fehscans "
            "werden ignoriert statt den Folger zu blenden, Kurven "
            "werden mitgenommen, und ein plötzlicher Größensprung "
            "startet die Spur neu (dann hat der Scanner ein anderes "
            "Element erwischt). Gleiche Tempo-Schwellen, gleiche "
            "80-px-Kappe - nur schlauere Logik. Läuft auch allein.",
        "desc.motion_lead_ms": "Millisekunden Vorsprung für ein "
            "bewegtes Element (0-300): 40-80 für langsames Scrollen, "
            "100-150 für schnelle Videobalken. Maximal 80 px, "
            "ausgeschaltet bei langsamer oder drehender Bewegung.",
        "desc.motion_predict": "Bei Elementen, die sich beim Klicken "
            "bewegen (scrollende Listen, Video-Balken), zielt Snappy "
            "AI etwas voraus, damit der Klick auf dem Element "
            "landet. Stehende Elemente bleiben unverändert.",
        "desc.mouse2_action": "Was ein kurzer Rechtsklick ZUSÄTZLICH "
            "tut - der Rechtsklick selbst behält immer seine normale "
            "Windows-Funktion. Standard: nichts.",
        "desc.mouse2_hold_action": "Dieselben Möglichkeiten, "
            "ausgelöst wenn Sie die rechte Taste etwa eine halbe "
            "Sekunde HALTEN statt zu klicken. Ein Druck ist entweder "
            "Klick oder Halten, nie beides. Standard: nichts.",
        "desc.on_target_dist": "Liegt Ihr Klick innerhalb so vieler "
            "Pixel um die Elementmitte, bewegt sich nichts - Sie "
            "haben getroffen.",
        "desc.radius": "Suchumkreis in Pixeln (40-400). Größer, wenn "
            "das gewünschte Element knapp außer Reichweite sitzt; "
            "kleiner, wenn der falsche Nachbar gewinnt.",
        "desc.rapid_click_snap": "Aus (Standard): Während ein Klick "
            "läuft, gehen weitere Klicks an Windows. An: Jeder "
            "Linksklick wird assistiert.",
        "desc.snap_offset_x": "Verschiebt den Klickpunkt seitlich "
            "aus der Elementmitte (-200 bis 200, negativ geht "
            "links). Für Bedienelemente, deren Mitte tot ist - "
            "geteilte Schaltfläche, Schieberegler - den Klick einmal "
            "auf die lebendige Stelle drehen statt bei jedem Snap zu "
            "kämpfen.",
        "desc.snap_offset_y": "Verschiebt den Klickpunkt senkrecht "
            "aus der Elementmitte (-200 bis 200, negativ geht hoch). "
            "Wie die seitliche Verschiebung: auf dem lebendigen Teil "
            "des Elements landen.",
        "desc.stall_pause_seconds": "Wenn ein Scan je hängt, "
            "pausiert die Assistenz so lang und jeder gehaltene "
            "Klick wird Ihnen zurückgegeben.",
        "desc.watcher_seconds": "Im Klassik-Modus wird ein zweiter "
            "Snap nahe derselben Stelle innerhalb dieser Zeit zu "
            "einem Doppelklick auf das Element.",
        "ent.cancel_line": "aktiv bis %s - wird NICHT verlängert",
        "ent.canceled_line": "Abo beendet%s",
        "ent.expired_line": "am %s abgelaufen - auf Stripe "
            "verlängern",
        "ent.past_due_line": "Zahlung fehlgeschlagen - Karte in der "
            "Stripe-Quittung beheben; der Zugriff kehrt zurück, "
            "sobald die Rechnung zahlt",
        "ent.plan": " (%s)",
        "ent.refunded_line": "erstattet / zurückgebucht - "
            "Freischaltung entzogen",
        "ent.st.active": "aktiv",
        "ent.st.canceled": "beendet",
        "ent.st.canceling": "aktiv, aber kündend",
        "ent.st.grant": "Support-Gewährung",
        "ent.st.past_due": "ZAHLUNG FEHLGESCHLAGEN",
        "ent.st.refunded": "erstattet / zurückgebucht",
        "ent.st.trial": "Test",
        "ent.st.unsubscribed": "kein Abo",
        "ent.until": " bis %s",
        "err.auth_unreachable": "Der Snappy-AI-Auth-Server ist nicht "
            "erreichbar:\n%s\n\nSnappy AI läuft nur mit einer "
            "lebenden Antwort davon.\nErneut versuchen?",
        "err.start_fail": "Snappy AI konnte nicht starten.\nMit "
            "--console ausführen, um Details zu sehen.",
        "gate.btn.monthly": "Monats-Abo für 9,99€",
        "gate.btn.trial": "Testkauf für 1,99€",
        "gate.head.canceled": "Dieses Abo wurde gekündigt - starten "
            "Sie auf Stripe ein neues, um weiterzumachen.",
        "gate.head.canceling": "Ihr Abo endet zum %s - bis dahin "
            "bleibt es aktiv, danach sperrt diese Anmeldung erneut, "
            "sofern Sie nicht verlängern.",
        "gate.head.email_mismatch": "Die Zahlung lief über eine "
            "andere E-Mail als Ihr Discord-Konto. Abos funktionieren "
            "nur auf der unten gezeigten Discord-E-Mail - damit "
            "erneut abbuchen oder den Support kontaktieren.",
        "gate.head.expired": "Das Abo dieser Anmeldung ist "
            "abgelaufen - auf Stripe verlängern, um weiterzumachen.",
        "gate.head.none": "Sie sind angemeldet, aber diese Anmeldung "
            "hat kein aktives Abo. Zahlen Sie mit DIESER "
            "Discord-E-Mail - ein Kauf auf einer anderen Adresse "
            "kann sie nicht freischalten.",
        "gate.head.past_due": "Die letzte Abo-Zahlung schlug fehl - "
            "auf Stripe beheben, dann wird diese Anmeldung wieder "
            "freigeschaltet.",
        "gate.head.refunded": "Dieser Kauf wurde erstattet oder "
            "zurückgebucht, die Freischaltung wurde entzogen. Ein "
            "neues Abo auf dieser Discord-E-Mail schaltet wieder "
            "frei.",
        "gate.head.shared": "Dieses Konto läuft GERADE auf einem "
            "ANDEREN Computer. Snappy AI bleibt aus, solange "
            "dasselbe Discord-Konto an zwei Orten läuft - schließen "
            "Sie die andere Sitzung und prüfen Sie erneut. Geteilte "
            "Abos treiben die Preise; bitte nicht.",
        "gate.msg.active": "Abo aktiv - Snappy AI startet...",
        "gate.msg.checking": "Prüfe mit dem Server...",
        "gate.msg.no_link": "Dieser Zahlungs-Link ist in diesem "
            "Build nicht konfiguriert.",
        "gate.msg.open_fail": "Kein Browser startbar. Diesen Link "
            "von Hand öffnen:\n%s",
        "gate.msg.open_ok": "Stripe ist im Browser geöffnet - zahlen Sie dort. Dieses Fenster bemerkt die Zahlung von selbst und startet die Engine.",
        "gate.msg.session_gone": "Sitzung weg - bitte erneut "
            "anmelden.",
        "gate.msg.still_none": "Weiterhin kein aktives Abo für diese "
            "Anmeldung.",
        "gate.msg.still_shared": "Weiterhin auf einem anderen "
            "Computer in use - diese Sitzung schließen, dann erneut "
            "prüfen.",
        "gate.msg.unreachable": "Auth-Server nicht erreichbar: %s",
        "gate.note": "Die Engine startet, sobald das Abo aktiv ist - "
            "dieses Fenster prüft alle 30 Sekunden von selbst. "
            "Schließen führt zurück zur Anmeldung.",
        "gate.prices": "2-Tage-Test: 1,99€ (einmalig)  -  Abo: 9,99€ "
            "/ Monat.\nDie Freischaltung landet bis zu ~10 Minuten "
            "nach der Zahlung; Verlängerungen schalten dieselbe "
            "Anmeldung automatisch wieder frei.",
        "gate.title": "%s - Abo%s",
        "hdr.build": "Build %s",
        "help.1.b": "Snappy AI betrachtet den Bildschirm um Ihren "
            "Cursor, findet die festen, elementförmigen Dinge in der "
            "Nähe - Knöpfe, Symbole, Links - und wählt das beste: "
            "scharfe Kanten, vernünftige Größe und Nähe zum Cursor "
            "gewinnen. Ihre Farbe, die Niemals-Klick-Liste und die "
            "Erinnerung an Ihren letzten Klick können die Wahl "
            "beeinflussen. Der Cursor zielt dann auf die Mitte des "
            "Elements, nicht auf eine Ecke seines Rahmens.",
        "help.1.t": "Was beim Klicken passiert",
        "help.10.b": "1. Ist gestartet? Pausiert bedeutet, nichts "
            "wird abgefangen - 'Kürzel: Assistenz starten' (Standard "
            "Strg+L) ist das einzige Ein/Aus.  2. Halten Sie Shift "
            "für einen Klick, um zu prüfen, ob die Assistenz das "
            "Problem war.  3. Falsches Element gewinnt: 'Suchumkreis "
            "um den Cursor' verkleinern, dann 'Meine Farbe(n)' "
            "setzen oder 'Stärke des Farb-Vorteils' erhöhen.  4. "
            "Nichts wird gefunden: 'Wie schwach eine Kante sein "
            "darf' und 'Mindeste Schärfe einer Kante' senken, "
            "'Größte Breite oder Höhe' oder 'Nahe Teile "
            "zusammenkleben' erhöhen.  5. Etwas darf nie assistiert "
            "werden: seine Farbe in Niemals-Klick-Farbe(n)' legen.  "
            "6. Immer noch falsch: melden Sie es dem Support, was "
            "Sie geklickt haben und was stattdessen passieren "
            "sollte, und legen Sie die Logdatei bei, die Snappy AI "
            "in seinen Datenordner schreibt.",
        "help.10.t": "Wenn etwas klemmt, in dieser Reihenfolge",
        "help.2.b": "Der Führungs-Modus (Standard) isst keinen "
            "Klick: Ihr Klick erreicht das Programm, und nach dem "
            "Loslassen fährt der Cursor auf das nächste klare "
            "Element. Der Klassik-Modus ist stärker: Ein Fehlgriff "
            "nahe einem Element wird abgefangen, der Cursor rastet "
            "ein und Snappy AI klickt für Sie. 'Suchumkreis um den "
            "Cursor' bestimmt den Suchkreis - größer, wenn das "
            "gewünschte Element knapp außer Reichweite sitzt, "
            "kleiner, wenn der falsche Nachbar gewinnt. Gedrücktes "
            "Shift umgeht einen Klick in beiden Modi.",
        "help.2.t": "Zuerst: Modus und Suchumkreis",
        "help.3.b": "Auf dem Tab Behandlung bestimmen 'Wie schwach "
            "eine Kante sein darf' und 'Mindeste Schärfe einer "
            "Kante', welche Kanten überhaupt zählen: niedriger "
            "findet Schwächeres, höher ignoriert Rauschen. 'Kleinste "
            "Elementgröße', 'Größte Elementfläche' und 'Größte "
            "Breite oder Höhe' sortieren Spritzer und ganze Fenster "
            "aus. 'Nahe Teile zusammenkleben' fügt einen kaputzen "
            "Umriss oder ein Symbol neben seiner Beschriftung zu "
            "einem Element. Auf dem Tab Assistenz sorgen "
            "'Automatisch für dunkle Bildschirme anpassen' und "
            "'Kanten nach relativer Helligkeit werten' dafür, dass "
            "dunkle Designs wie helle funktionieren - beide "
            "anlassen.",
        "help.3.t": "Nichts wird gefunden - oder zu viel",
        "help.4.b": "Auf dem Tab Farben ist 'Meine Farbe(n)' die "
            "bevorzugte Farbe und 'Niemals-Klick-Farbe(n)' absolut: "
            "Elemente damit werden nie assistiert. 'Nur meine Farbe "
            "assistieren' beschränkt die Assistenz auf passende "
            "Elemente. Auf dem Tab Behandlung sagt 'Strenge der "
            "Farbübereinstimmung', wie nahe ein Ton kommen muss, "
            "'Ähnliche Farbtöne akzeptieren' lässt hellere oder "
            "verwaschene Varianten teilweise zählen, und 'Stärke des "
            "Farb-Vorteils' bestimmt, wie sehr Ihre Farbe ein "
            "Element hebt - erhöhen Sie sie, wenn trotzdem das "
            "falsche gewinnt.",
        "help.4.t": "Mit Farben arbeiten",
        "help.5.b": "'Zuletzt geklicktes Element merken' bevorzugt "
            "weiterhin das Element, auf dem Ihr letzter "
            "erfolgreicher Klick landete, für 'Wie lange merken' "
            "Sekunden - das macht Scrollbalken und Dialogknöpfe "
            "angenehm. 'Stärke der Erinnerung' sagt, wie stark es "
            "gewinnt, und 'Was die Erinnerung lernen darf' schützt "
            "sie: Mit 'Nur Elemente in meiner Farbe' kann ein "
            "Fehlklick sie nicht umlenken. 'Bei gedrückter Taste am "
            "Element bleiben' beruhigt Ziehaktionen; die "
            "Rechtsklick-Aktionen auf dem Tab Experimentell können "
            "die Erinnerung per Maus folgen oder löschen.",
        "help.5.t": "Wiederholte Klicks auf ein Bedienelement",
        "help.6.b": "'Bewegte Elemente vorhalten' misst, wie schnell "
            "das gewählte Element wandert, und zielt um 'Wie weit "
            "voraus zielen' Millisekunden voraus, damit der Klick "
            "auf einer scrollenden Liste oder einem Videobalken "
            "landet statt dahinter. Der Vorsprung endet bei 80 "
            "Pixeln und schaltet sich bei stehenden oder drehenden "
            "Elementen selbst ab.",
        "help.6.t": "Bewegte Dinge klicken",
        "help.7.b": "'Cursorbewegung animieren' = 0 springt sofort; "
            "40-120 gleitet, damit Sie zusehen können, und eigene "
            "Mausbewegung bricht das Gleiten ab. "
            "'Doppelklick-Fenster' macht im Klassik-Modus aus einem "
            "zweiten Snap nahe derselben Stelle einen Doppelklick. "
            "'Jeden Klick einer schnellen Serie assistieren' "
            "assistiert jeden Klick einer Serie statt nur des "
            "ersten. 'Pause nach einem Hänger' ist das "
            "Sicherheitsventil, das einen gehaltenen Klick "
            "zurückgibt, falls ein Scan je hängt.",
        "help.7.t": "Wie Klicks sich anfühlen",
        "help.8.b": "Der Tab Tastenkürzel erklärt die beiden Modi "
            "und das Aufzeichnen. Kurz: Kürzel mit Strg, Alt, Shift "
            "oder Win sind systemweit reserviert; bloße Einzeltasten "
            "feuern überall und tippen trotzdem. Ein Makro macht aus "
            "einem blockierten Tastendruck eine ganze Kombination. "
            "Aufzeichnungen fangen Ihre echten Eingaben - jede "
            "Taste, jeden Mausklick und jede Zeigerbewegung - und "
            "spielen sie vom Tab Makros ab, je mit eigenem Schalter "
            "für einmalig oder wiederholen bis gestoppt.",
        "help.8.t": "Tasten, Makros und Aufzeichnungen",
        "help.9.b": "Der Knopf Sprache neben 'Konfiguration "
            "exportieren' - auch im Anmelde- und im Abo-Fenster - "
            "stellt die gesamte Oberfläche sofort um, ohne Neustart, "
            "und merkt sich Ihre Wahl. Sprachen, die noch übersetzt "
            "werden, stehen nicht zur Auswahl; was Sie wählen "
            "können, ist vollständig.",
        "help.9.t": "Sprache",
        "help.sub": "Jede Einstellung mit dem Namen, den Sie auf "
            "ihrem Tab sehen, in der Reihenfolge, in der Sie sie "
            "brauchen. Der Zeiger über einem Namen zeigt die "
            "Kurzbeschreibung; diese Seite ist die Langform.",
        "help.tail": "Einstellungen gelten nach einem Druck auf "
            "Übernehmen. Eine config.ini neben dem Programm "
            "überschreibt config.json. Diese Seite erklärt; sie "
            "stellt nichts ein.",
        "help.title": "Snappy AI in einfachen Worten einstellen",
        "kb.keys.b": "Ein Kürzel mit Strg, Alt, Shift oder Win ist "
            "systemweit reserviert: nur Snappy AI sieht es. Eine "
            "bloße Einzeltaste (wie 1 oder 2) wirkt in jedem "
            "Programm UND tippt normal - der Preis: Tippen Sie die "
            "Taste mitten im Satz, löst sie ihre Aktion ebenfalls "
            "aus. Klassisches Verhalten erhalten Sie mit "
            "'Einzel-Tastenkürzel schlucken die Taste' auf dem Tab "
            "Assistenz. Makros gehen noch weiter: Im gestarteten "
            "Zustand wird die Auslösetaste geschluckt und die "
            "Kombination daneben genau einmal gesendet.",
        "kb.keys.t": "Einzeltasten gegen Tastenkombinationen",
        "kb.mode.b": "Führungs-Modus (Standard, Kürzel 2): Ihr Klick "
            "erreicht das Programm immer unangetastet; nach dem "
            "Loslassen fährt der Cursor auf das nächste klare "
            "Element, Ihr nächster Klick startet also dort. Nichts "
            "wird je geschluckt - der sicherste Modus.  "
            "Klassik-Modus (Kürzel 1): Klicken Sie nahe einem "
            "Element, wird dieser Fehlklick abgefangen, der Cursor "
            "rastet auf dem Element ein und Snappy AI klickt es für "
            "Sie; ist nichts in der Nähe, bekommen Sie Ihren Klick "
            "unverändert zurück.  In beiden Modi umgeht gedrücktes "
            "Shift beim Klicken die Assistenz für diesen einen "
            "Klick.",
        "kb.mode.t": "Was die beiden Modi tun",
        "kb.rec.b": "Im gestarteten Zustand drücken Sie das "
            "Aufnahme-Kürzel (Standard Strg+Alt+R): Jede gedrückte "
            "Taste, jeder Mausklick und jede Zeigerbewegung wird "
            "aufgezeichnet UND erreicht weiterhin Ihre Programme, "
            "Sie arbeiten also normal weiter. Das Stopp-Kürzel "
            "(Strg+Alt+S) speichert alles in die Liste auf dem Tab "
            "Makros - fünf Aufzeichnungen passen hinein. Klicken Sie "
            "eine Aufzeichnung an, um sie zu wählen, «Umbenennen» "
            "oder «Exportieren» zu nutzen und ihren eigenen "
            "«Wiederholen bis gestoppt»-Schalter zu setzen. Das "
            "Wiedergabe-Kürzel (Strg+Alt+M) spielt die dort gewählte "
            "Aufzeichnung; Strg+1 bis Strg+5 spielen nach Position "
            "in der Liste. Pausiert wird nichts aufgezeichnet und "
            "nichts eingefügt - Ihre Eingaben gehören ganz Ihnen.",
        "kb.rec.t": "Eigene Tasten- und Mauseingaben aufzeichnen und "
            "abspielen",
        "lang.close": "Schließen",
        "lang.coverage": "%d %% übersetzt",
        "lang.current": "Aktuell: %s",
        "lang.progress": "Noch in Übersetzung, angeboten sobald "
            "vollständig: %s",
        "lang.prompt": "Änderungen gelten sofort - das Fenster "
            "bleibt offen, damit Sie mehrere ausprobieren können.",
        "lang.title": "Sprache",
        "lbl.accent_boost": "Stärke des Farb-Vorteils",
        "lbl.accent_coherent": "Verstreute Farbspritzer ignorieren",
        "lbl.accent_color": "Meine Farbe(n)",
        "lbl.accent_matcher": "Farbabgleich-Verfahren",
        "lbl.accent_only": "Nur meine Farbe assistieren",
        "lbl.accent_soft": "Ähnliche Farbtöne akzeptieren",
        "lbl.accent_tolerance": "Strenge der Farbübereinstimmung",
        "lbl.accent_variants": "Helle und dunkle Zustände meiner "
            "Farbe erkennen",
        "lbl.adaptive_threshold": "Automatisch für dunkle "
            "Bildschirme anpassen",
        "lbl.auto_click": "Klickt selbst auf Elemente",
        "lbl.auto_click_interval": "Sekunden zwischen Auto-Klicks",
        "lbl.auto_click_max_clicks": "Auto-Klick-Limit pro Sitzung",
        "lbl.auto_click_min_contrast": "Wie scharf ein "
            "Auto-Klick-Ziel sein muss",
        "lbl.auto_click_radius": "Wie weit von der Mitte suchen",
        "lbl.auto_click_repeat_px": "Dieselbe Stelle nicht erneut "
            "anklicken",
        "lbl.auto_click_settle_ms": "Pause vor einem Auto-Klick",
        "lbl.block_bound_keys": "Einzel-Tastenkürzel schlucken die "
            "Taste",
        "lbl.capture_backend": "Bildschirm-Aufnahmeverfahren",
        "lbl.color_adapt": "An Bildschirmlicht anpassen",
        "lbl.contrast_threshold": "Wie schwach eine Kante sein darf",
        "lbl.exclude_color": "Niemals-Klick-Farbe(n)",
        "lbl.follow_boost": "Stärke der Erinnerung",
        "lbl.follow_enabled": "Zuletzt geklicktes Element merken",
        "lbl.follow_learn": "Was die Erinnerung lernen darf",
        "lbl.follow_seconds": "Wie lange merken",
        "lbl.glide_ms": "Cursorbewegung animieren",
        "lbl.hold_follow": "Bei gedrückter Taste am Element bleiben",
        "lbl.key_launch": "Kürzel: Assistenz starten",
        "lbl.key_mode1": "Kürzel: Klassik-Modus (bis 4 Tasten)",
        "lbl.key_mode2": "Kürzel: Führungs-Modus (bis 4 Tasten)",
        "lbl.key_pause": "Kürzel: pausieren",
        "lbl.key_play": "Kürzel: gewählte Aufzeichnung abspielen",
        "lbl.key_play_n": "Kürzel: Aufzeichnung #%d abspielen",
        "lbl.key_record": "Kürzel: Aufzeichnung starten",
        "lbl.key_record_stop": "Kürzel: Aufzeichnung stoppen und "
            "speichern",
        "lbl.luminance_norm": "Kanten nach relativer Helligkeit "
            "werten",
        "lbl.macro_action": "Makro %d: sendet stattdessen",
        "lbl.macro_key": "Makro %d: diese Taste drücken",
        "lbl.max_area": "Größte Elementfläche",
        "lbl.max_dim": "Größte Breite oder Höhe eines Elements",
        "lbl.merge_distance": "Nahe Teile zusammenkleben",
        "lbl.min_area": "Kleinste Elementgröße",
        "lbl.min_contrast": "Mindeste Schärfe einer Kante",
        "lbl.motion_3d": "Intelligenteres Folgen bei bewegten "
            "Elementen",
        "lbl.motion_lead_ms": "Wie weit voraus zielen",
        "lbl.motion_predict": "Bewegte Elemente vorhalten",
        "lbl.watch_center_only": "Nur die Bildschirmmitte beobachten",
        "desc.watch_center_only": "Die Hilfe beachtet nur ein festes Quadrat in der Mitte des "
            "Bildschirms (Größe = Suchdistanz, standardmäßig 150×150 px) – egal "
            "wo der Cursor steht. Klicks außerhalb dieses Quadrats bleiben "
            "unberührt.",
        "lbl.center_follow": "Bildschirm folgt dem Ziel",
        "desc.center_follow": "Wenn „Nur die Bildschirmmitte beobachten“ an ist: Nach dem "
            "Einrasten auf ein Element bewegt die Hilfe den Bildschirm mit, "
            "damit das Ziel in der Mitte bleibt – besonders bei scrollenden "
            "Flächen. Bewege den Bildschirm selbst, um die Verfolgung "
            "loszulassen.",
        "lbl.input_backend": "Eingabemethode",
        "desc.input_backend": "Windows-Einspeisung (Standard) funktioniert überall. Interception "
            "sendt über den Treiber und wird von Spielen als echte Maus erkannt "
            "– erfordert den installierten Interception-Treiber und "
            "interception.dll neben dem Programm; sonst automatisch "
            "Windows-Einspeisung.",
        "val.input_backend.win32": "Windows-Einspeisung",
        "val.input_backend.interception": "Interception (Treiber)",
        "lbl.mouse2_action": "Zusatzaktion für Rechtsklick",
        "lbl.mouse2_hold_action": "Zusatzaktion für Rechts-Halten",
        "lbl.on_target_dist": "Abstand für 'schon getroffen'",
        "lbl.radius": "Suchumkreis um den Cursor",
        "lbl.rapid_click_snap": "Jeden Klick einer schnellen Serie "
            "assistieren",
        "lbl.snap_offset_x": "Klickpunkt: nach links / rechts "
            "verschieben",
        "lbl.snap_offset_y": "Klickpunkt: nach oben / unten "
            "verschieben",
        "lbl.stall_pause_seconds": "Pause nach einem Hänger",
        "lbl.watcher_seconds": "Doppelklick-Fenster",
        "login.failed": "%s-Anmeldung nicht abgeschlossen - erneut "
            "versuchen.",
        "login.no_provider": "In dieser Kopie ist kein "
            "Anmelde-Anbieter eingebaut.",
        "login.not_configured": "Die Abo-Datei ist in diesem Build "
            "noch nicht konfiguriert.",
        "login.note": "Die Anmeldung öffnet Ihren Browser und kommt "
            "von selbst zu diesem Fenster zurück.",
        "login.provider": "Mit %s anmelden",
        "login.signedin": "Angemeldet als %s.",
        "login.sub": "Mit Discord anmelden - Ihr Abo ist an dieses "
            "Konto gebunden, und Zahlungen müssen dessen "
            "E-Mail-Adresse nutzen. Kein Passwort hier.",
        "login.title": "%s - Anmelden",
        "login.unreachable": "Auth-Server nicht erreichbar: %s",
        "login.waiting": "Warten auf den Browser - %s-Anmeldung "
            "abschließen...",
        "mac.delete": "Löschen",
        "mac.empty": "Noch keine Aufzeichnungen - starten Sie, "
            "drücken Sie das Aufnahme-Kürzel und arbeiten Sie "
            "normal: Jede Taste, jeder Klick und jede Zeigerbewegung "
            "wird erfasst.",
        "mac.export": "Exportieren",
        "mac.import": "Importieren",
        "mac.keys_head": "Tastenmakros",
        "mac.loop": "Wiederholen bis gestoppt",
        "mac.recordings": "Aufzeichnungen",
        "mac.rename": "Umbenennen",
        "mac.row": "Makro %d",
        "mac.sends": "sendet",
        "mac.steps": "%d Schritte",
        "note.advanced": "Abstands- und Zeit-Einstellungen, die "
            "ändern, wie Klicks sich anfühlen, nicht was gefunden "
            "wird. Die meisten Menschen müssen hier nichts ändern; "
            "die Standardwerte sind die getesteten.",
        "note.assist": "Jeder Schalter, der das Verhalten im "
            "gestarteten Zustand ändert. Die beiden Modi wechseln "
            "mit Ihren Modus-Tasten - der Tab Tastenkürzel erklärt, "
            "was jeder Modus tut. Die Assistenz startet immer "
            "pausiert; Starten ist das einzige Ein/Aus. Wo die "
            "Engine schaut und wie Klicks sich anfühlen, steht unter "
            "Erweitert; was als Element zählt, unter Behandlung.",
        "note.colors": "Die beiden Listen oben bestimmen, welche "
            "Farben Snappy AI bevorzugt oder ablehnt. Jede zeigt "
            "ihre Farben als Felder rechts, höchstens fünfzehn, und "
            "ein Klick auf ein Feld entfernt die Farbe wieder; eine "
            "leere Liste zeigt ein durchgestrichenes Feld und gilt "
            "als aus. «Als bevorzugt hinzufügen» und «Als abgelehnt "
            "hinzufügen» legen die im Mischer stehende Farbe in die "
            "passende Liste. Aktueller RGB-Wert zeigt drei Felder - "
            "jedes so breit wie fünf Farbfelder, die Zeile "
            "überspannt also dieselben fünfzehn Felder wie alles "
            "darunter -, die umso heller leuchten, je mehr Rot, Grün "
            "und Blau die Farbe im Mischer enthält; die Zeile folgt "
            "dem Mischer und kann nicht getippt werden. Der Mischer "
            "darunter mischt eine Farbe wie ein Malprogramm; alles "
            "daneben sitzt am rechten Fensterrand, mit demselben "
            "Abstand zur Kante wie die Einstellungen oben, und jede "
            "Zeile überspannt dieselbe Fünfzehn-Felder-Breite: die "
            "hohe Anzeige mit dem #Wert darin, dann die fünfzehn "
            "Fertigtöne, die beiden Hinzufügen-Knöpfe und die "
            "Bildschirm-Zeile - «Farbe vom Bildschirm holen» holt "
            "die einzelne Farbe unter dem Zeiger, «Bildschirmfarben "
            "finden» füllt fünfzehn eigene Felder mit Farben, die es "
            "um den Zeiger herum findet, und ein Klick darauf lädt "
            "sie in den Mischer. Die Anzeige ist darum so hoch: So "
            "enden die Vorschlagsfelder genau auf der Höhe des "
            "Farbreglers links.",
        "note.experimental": "Engine-Auswahl, je mit getestetem "
            "Standard. Ändern Sie diese nur zum Vergleichen, auf "
            "ungewöhnlicher Hardware oder wenn der Support es bittet "
            "- das Aufnahmeverfahren gilt nach Neustart.",
        "note.handler": "Was als klickbares Element zählt: wie "
            "schwach eine Kante sein darf, wie scharf sie sein muss "
            "und wie groß oder klein ein Element sein darf. Nichts "
            "gefunden? Lockern Sie diese Werte. Falsches gefunden? "
            "Straffen Sie sie, oder nutzen Sie Ihre Farbe auf dem "
            "Tab Farben.",
        "note.keybindings": "Jedes Kürzel - und darunter, was die "
            "beiden Modi tun, wie Sie eigene Tasten- und "
            "Mauseingaben aufzeichnen und wie sich Einzeltasten von "
            "Kombinationen unterscheiden.",
        "note.macros": "Ein Makro macht aus einem Tastendruck eine "
            "ganze Kombination, solange gestartet. Daneben Ihre "
            "Aufzeichnungen: bis zu fünf benannte Mitschnitte von "
            "allem, was Sie getan haben - jede Taste, jeder "
            "Mausklick und jede Zeigerbewegung -, die genau wie "
            "aufgenommen ablaufen. Klicken Sie eine Aufzeichnung an, "
            "um sie zu wählen; jede Zeile trägt ihren eigenen "
            "«Wiederholen bis gestoppt»-Schalter, und «Umbenennen», "
            "«Exportieren», «Importieren» und «Löschen» sitzen unten "
            "in der Box.",
        "note.macros_keys": "Die Aufnahme-/Wiedergabe-Kürzel liegen "
            "auf dem Tab Tastenkürzel (Standard: Strg+Alt+R "
            "Aufnahme, Strg+Alt+S stoppen und speichern, Strg+Alt+M "
            "abspielen, Strg+1..5 spielen die Positionen der Liste).",
        "online.cancelled": "Die Discord-Authentifizierung wurde "
            "abgebrochen (oder schlug fehl). Bitte erneut versuchen.",
        "rec.export_fail": "Export fehlgeschlagen: %r",
        "rec.exported": "Exportiert nach %s",
        "rec.import_fail": "Import fehlgeschlagen: %r",
        "rec.imported": "%d Aufzeichnung(en) importiert%s.",
        "rec.imported_none": " (keine war gültig)",
        "rec.no_sel": "Nichts gewählt zum Exportieren.",
        "rec.notfile": "Import fehlgeschlagen: keine "
            "Aufzeichnungsdatei.",
        "shared.back": "Willkommen zurück - Starten, wenn bereit.",
        "shared.body": "Dieses Discord-Konto führt Snappy AI gerade "
            "auf einem anderen Computer aus.\nDie Assistenz pausiert "
            "hier, bis nur noch eine Sitzung übrig ist.\n\nEin Abo, "
            "eine Maschine gleichzeitig - das hält\nden Preis "
            "niedrig und die Entwicklung am Laufen.",
        "shared.close": "Schließen",
        "shared.recheck": "Jetzt erneut prüfen",
        "shared.still": "Weiterhin anderswo in Benutzung - bleibe "
            "pausiert.",
        "shared.title": "Konto anderswo in Benutzung",
        "shared.unreachable": "Server nicht erreichbar - wird erneut "
            "geprüft.",
        "st.all_files": "Alle Dateien",
        "st.color_added": "rgb(%d, %d, %d) zu %s hinzugefügt - "
            "Übernehmen speichert.",
        "st.color_already": "rgb(%d, %d, %d) ist bereits in %s.",
        "st.color_full": "%s enthält bereits 15 Farben - klicken Sie "
            "zuerst ein Feld an, um eine Farbe zu entfernen.",
        "st.color_removed": "rgb(%d, %d, %d) aus %s entfernt - "
            "Übernehmen speichert.",
        "st.delete_confirm": "Aufzeichnung %r löschen?\nDas lässt "
            "sich nicht rückgängig machen.",
        "st.deleted": "Aufzeichnung gelöscht.",
        "st.engine_dead": "Engine-Thread nicht verfügbar - Kürzel "
            "reagieren nicht.",
        "st.ent_paused": "Abo %s - Assistenz pausiert. Auf Stripe "
            "erneuern, dann neu starten.",
        "st.ent_unreachable": "Abo-Prüfung: Server nicht erreichbar "
            "(Sitzung läuft weiter).",
        "st.export_fail": "Export fehlgeschlagen: %r",
        "st.export_rec_title": "Aufzeichnung exportieren",
        "st.export_title": "Einstellungen exportieren",
        "st.exported": "Einstellungen exportiert nach %s",
        "st.file_rec": "Snappy-AI-Aufzeichnung",
        "st.file_settings": "Snappy-AI-Einstellungen",
        "st.follow": "  |  Folge vor %d s",
        "st.import_fail": "Import fehlgeschlagen: %r",
        "st.import_notfile": "Import fehlgeschlagen: keine "
            "Einstellungsdatei.",
        "st.import_rec_title": "Aufzeichnung(en) importieren",
        "st.import_title": "Einstellungen importieren",
        "st.imported": "%d Einstellung(en) importiert%s.",
        "st.imported_ignored": ", ignoriert: %s",
        "st.ini_over": "Übernommen, aber config.ini überschreibt: %s",
        "st.lib_empty": "Die Liste ist leer - nichts zu exportieren.",
        "st.line": "Assistiert %d  |  durchgelassen %d%s  |  Design: "
            "%s",
        "st.loop_desc": "Wiedergabeart DIESER Aufzeichnung: aus = "
            "einmal abspielen; an = wiederholen, bis Sie das "
            "Wiedergabe-Kürzel erneut drücken. Jede Aufzeichnung hat "
            "ihren eigenen Schalter, gespeichert mit der "
            "Aufzeichnung selbst.",
        "st.name_empty": "Der Name darf nicht leer sein.",
        "st.pick_err": "Aufnahme fehlgeschlagen: %r",
        "st.pick_fail": "Aufnahme fehlgeschlagen - erneut versuchen.",
        "st.pick_ok": "rgb(%d, %d, %d) bei (%d, %d) aufgenommen.",
        "st.pick_wait": "Cursor auf die Farbe bewegen - Aufnahme in "
            "3 s...",
        "st.preset_desc": "Fertigton: %s - klicken, um ihn in die "
            "Mischung zu laden.",
        "st.rec_count": "%d von 5 Aufzeichnungen",
        "st.rec_now": "%r jetzt: %s.",
        "st.rec_once": "spielt einmal",
        "st.rec_playing": "Spiele %r...",
        "st.rec_playing_loop": "Spiele %r bis gestoppt",
        "st.rec_recording": "AUFNAHME - %s stoppt und speichert",
        "st.rec_repeats": "wiederholen bis gestoppt",
        "st.registered": "Registriert auf: %s    Status: %s",
        "st.rename_prompt": "Neuer Name für Aufzeichnung #%d:",
        "st.renamed": "Aufzeichnung umbenannt.",
        "st.reset_confirm": "Alle Einstellungen auf Standard "
            "zurücksetzen?\nKonten bleiben erhalten; das betrifft "
            "nur Einstellungen.",
        "st.rgb_bad": "Zuerst gültige R/G/B-Werte eingeben.",
        "st.running": "Läuft..",
        "st.saved": "Gespeichert und übernommen.",
        "st.defaults_restored": "Standardeinstellungen wiederhergestellt.",
        "st.saved_bad": "Gespeichert, aber ungültig (alt behalten): "
            "%s",
        "st.select_rec": "Zuerst eine Aufzeichnung wählen.",
        "st.shared_paused": "KONTO ANDERSWO IN BENUTZUNG - Assistenz "
            "pausiert; ein Abo = eine Maschine.",
        "st.standby": "Bereit..",
        "st.sug_fail": "Vorschlag fehlgeschlagen: %r",
        "st.sug_loaded": "Vorschlag rgb(%d, %d, %d) steht im Mischer "
            "- mit den Knöpfen oben in eine Liste aufnehmen.",
        "st.sug_loaded_desc": "Vorgeschlagene UI-Farbe rgb(%d, %d, "
            "%d) - %d%% des Bereichs. Klicken, um sie in die "
            "Mischung zu laden.",
        "st.sug_none": "Keine Farbvorschläge aus diesem Bereich.",
        "st.sug_ok": "%d Vorschläge - einen klicken, um ihn in den "
            "Mischer zu laden.",
        "st.sug_wait": "Auf die app zeigen, in der Sie arbeiten - "
            "Analyse in 3 s...",
        "tab.advanced": "Erweitert",
        "tab.assist": "Assistenz",
        "tab.colors": "Farben",
        "tab.experimental": "Experimentell",
        "tab.handler": "Behandlung",
        "tab.help": "Hilfe",
        "tab.hotkeys": "Tastenkürzel",
        "tab.macros": "Makros",
        "theme.dark": "Dunkel",
        "theme.light": "Hell",
        "val.accent_matcher.hsv": "Klassisch - der ältere Engine",
        "val.accent_matcher.oklab": "Perzeptuell - wie Farben "
            "aussehen (empfohlen)",
        "val.capture_backend.auto": "Automatisch - schnellstes mit "
            "sicherem Fallback",
        "val.capture_backend.dxcam": "Desktop Duplication - sehr schnell, aber "
            "schnellstes auf den meisten PCs",
        "val.capture_backend.mss": "Kompatibel - funktioniert immer "
            "(Remote Desktop, VMs)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "experimentell",
        "val.follow_learn.accent": "Nur Elemente in meiner Farbe",
        "val.follow_learn.any": "Jeder erfolgreiche Snap",
        "val.mouse2_action.1": "Aktuelle Folgeaufgabe löschen",
        "val.mouse2_action.2": "Der zuletzt gesnappten Farbe folgen",
        "val.mouse2_action.3": "Farbe unter dem Cursor wählen, dann "
            "folgen",
        "val.mouse2_action.4": "Nichts tun",
        "val.mouse2_hold_action.1": "Aktuelle Folgeaufgabe löschen",
        "val.mouse2_hold_action.2": "Der zuletzt gesnappten Farbe "
            "folgen",
        "val.mouse2_hold_action.3": "Farbe unter dem Cursor wählen, "
            "dann folgen",
        "val.mouse2_hold_action.4": "Nichts tun",
        "word.off": "Aus",
        "word.on": "An",
    },
    "hu": {
        "btn.apply": "Alkalmaz",
        "btn.export": "Beállítások exportálása",
        "btn.import": "Beállítások importálása",
        "btn.language": "Nyelv: %s",
        "btn.launch": "Indítás",
        "btn.logout": "Kijelentkezés",
        "btn.pause": "Szünet",
        "btn.restore": "Alapértékek visszaállítása",
        "col.accent": "Kiemelő",
        "col.add_pref": "Kedvelt szín hozzáadása",
        "col.add_ref": "Tiltott szín hozzáadása",
        "col.chip_desc": "rgb(%d, %d, %d) ebben: %s - kattintson a "
            "mezőre a szín eltávolításához.",
        "col.chip_off": "A(z) %s nem tartalmaz színt - az áthúzott "
            "mező jelentése: ki. Válasszon színt lent, és nyomja meg "
            "a hozzá tartozó hozzáadás gombot.",
        "col.exclude": "Kizárt",
        "col.pick": "Szín vétele a képernyőről",
        "col.rgb.desc": "Három mező mutatja a keverőben éppen álló "
            "színt: az első annál jobban ragyog, minél több vöröset "
            "tartalmaz, a második a zöldet, a harmadik a kéket - a "
            "fényesebb többet jelent. A sor követi a keverőt, a kész "
            "színeket és a képernyő gombjait; gépelni nem lehet.",
        "col.rgb.name": "Jelenlegi RGB-érték",
        "col.suggest": "Színjavaslat a képernyőről",
        "desc.accent_boost": "Mennyit emel az elem értékén a saját "
            "színe (0-3). Emelje 1,5-2 felé, ha mégis a rossz elem "
            "nyer.",
        "desc.accent_coherent": "Színének összefüggő foltot kell "
            "alkotnia, hogy számítson - a szétszórt dither- vagy "
            "tömörítési pöttyök nem minősítenek elemet, nem "
            "erősítenek és nem tesznek a soha-nem-kattintható "
            "listára.",
        "desc.accent_color": "A szín, amelyet a Snappy AI előnyben "
            "részesít, színmezőkként mutatva jobbra. Válasszon színt "
            "lent, és nyomja meg a «Kedvelt szín hozzáadása» gombot "
            "a hozzáadáshoz - legfeljebb tizenöt mező; egy mezőre "
            "kattintva a szín újra kikerül. Az ezeket tartalmazó "
            "elemek nyerik az egyenlő állást. Az üres lista áthúzott "
            "mezőt mutat, és kikapcsolja a beállítást.",
        "desc.accent_matcher": "Hogyan hasonlítjuk a színeket. A "
            "perceptuális a tényleges látvány szerint rangsorol, ez "
            "az ajánlott; a klasszikus a régebbi motor, "
            "összehasonlításra.",
        "desc.accent_only": "Csak a saját színét tartalmazó elemek "
            "asszisztálhatók; a máshol tett kattintás változatlanul "
            "a Windowshoz megy.",
        "desc.accent_soft": "0-100: mennyire számítanak a saját "
            "színe világosabb, sötétebb vagy fakóbb változatai. 0 = "
            "csak pontos árnyalat.",
        "desc.accent_tolerance": "Mennyire kell közel lennie egy "
            "színnek (4-90). Kisebb = szigorúbb.",
        "desc.accent_variants": "Színe világosabb és sötétebb "
            "másolatai is számítanak, így a rámutatás, lenyomás és "
            "halvány állapotok érvényesek a színezet-tűrés tágítása "
            "nélkül. Csak világosság - rossz színezet sosem "
            "kapaszkodhat fel.",
        "desc.adaptive_threshold": "Sötét témák és fakó dokumentumok "
            "automatikusan lejjebb viszik a saját felismerési "
            "küszöbüket, így a halvány elemek is meglesznek. "
            "Ajánlott.",
        "desc.auto_click": "Bekapcsolva a program minden 0,1 másodpercben magától kattint a "
            "figyelt terület legjobb elemére, a kontraszt az elsőbbségi "
            "szempont. Ha alapszín be van állítva, csak a színes elemek "
            "jöhetnek szóba; szín nélkül csak a nagyon élesen rajzolt elemekre "
            "kattint. Ugyanoda sosem kétszer, és saját ablakaira soha.",
        "desc.auto_click_interval": "Milyen gyakran nézi a képernyőt "
            "az ön színe után (0,5-60). A lassú szám a biztonságos: "
            "2-5 egy figyelt párbeszédhez való.",
        "desc.auto_click_max_clicks": "Hányszor kattinthat magától "
            "indítás után (1-200). A határnál megáll és szól, így "
            "egy rossz beállítás nem szaladhat el.",
        "desc.auto_click_min_contrast": "Ugyanazon a skálán, mint a "
            "»Minimális él-élesség«. Induljon az alapról, és emelje, "
            "ha rosszat kattint: csak erős, tisztán rajzolt elemek "
            "számítanak.",
        "desc.auto_click_radius": "Az auto-kattintás a képernyő "
            "közepe körül keres (40-600 px). Nagyobb zsúfolt "
            "ablakhoz; kisebb, hogy csak a középső egy vezérlőt "
            "lássa.",
        "desc.auto_click_repeat_px": "Auto-kattintás után az ezen "
            "belüli célt békén hagyja (0-400). Enélkül egy képernyőn "
            "maradó gombot újra meg újra kattintana.",
        "desc.auto_click_settle_ms": "A kurzor ennyit pihen a célon "
            "(0-2000 ms) a kattintás előtt, hogy a program előbb "
            "lássa a kijelölést. 120 a legtöbb ablakhoz jó.",
        "desc.block_bound_keys": "Ki (alap): egy Ctrl/Alt/Shift "
            "nélküli gyorsbillentyű - mint 1 vagy V - minden "
            "programban működik ÉS normálisan gépel, tehát mondat "
            "közben is kiváltja a műveletét. Be: a művelet továbbra "
            "is mindenhol elsül, de a gomb többé nem gépel.",
        "desc.capture_backend": "Hogyan fényképeződik a képernyő. Az "
            "automatikus a kompatibilis módot használja, amely majdnem minden ablakot lát; a "
            "kompatibilis mindig működik, távoli asztalnál és "
            "virtuális gépeken is. Újraindítás után lép életbe.",
        "desc.color_adapt": "Minden elem a saját hátteréhez "
            "fehéregyensúlyozva lesz illesztve, így az éjszakai fény "
            "és a témák színezése nem tolja ki a színét a tűrésből. "
            "Csak az összehasonlításhoz kapcsolja ki.",
        "desc.contrast_threshold": "Alacsonyabb halványabb elemeket "
            "talál (és több zajt); magasabb élesebb éleket kíván.",
        "desc.default": "Vigye az egeret egy beállítás neve fölé, "
            "hogy lássa, mit csinál.",
        "desc.exclude_color": "Az ilyen színű elemek soha nem "
            "asszisztáltak: a kattintás rájuk közvetlenül a "
            "Windowshoz megy, mindkét módban. Színmezőkként mutatva "
            "jobbra - válasszon színt lent, és nyomja meg a «Tiltott "
            "szín hozzáadása» gombot egy hozzáadásához (legfeljebb "
            "tizenöt); egy mezőre kattintva az kikerül. Az üres "
            "lista áthúzott mezőt mutat, és kikapcsolja a "
            "beállítást.",
        "desc.follow_boost": "Mennyire erősen nyer az emlékezett "
            "elem: 100% frissen megduplázhatja az értékét, 25% csak "
            "enyhe lökés.",
        "desc.follow_enabled": "Sikeres snap után a hasonló kinézetű "
            "vagy ugyanott lévő elemek egy ideig nyernek - "
            "görgetősávok és ismételt kattintások esetén hasznos.",
        "desc.follow_learn": "Csak a saját színem elemei: egy "
            "félrekattintás nem tudja átirányítani az emlékezetet. "
            "Minden sikeres snap: a régi, bizakodó viselkedés.",
        "desc.follow_seconds": "Másodpercek, ameddig az emlékezett "
            "elem előnyben marad az utolsó sikeres snap után "
            "(1-120).",
        "desc.glide_ms": "0 (alap) azonnal ugrik - leggyorsabb. "
            "40-120 csúszik, hogy látni lehessen; saját egérmozgás "
            "megszakítja.",
        "desc.hold_follow": "Amíg a bal gombot egy snap után nyomva "
            "tartja - vagy az emlékezett elemen újra lenyomja - a "
            "kurzor az elem színén marad; ez stabilizálja a "
            "húzásokat, például a görgetősávot. Máshol lenyomva "
            "sosem nyúl hozzá.",
        "desc.key_launch": "Formátum: ctrl+l, f5, space, ctrl+alt+1 "
            "... Módosítók: ctrl, alt, shift, win. Alkalmazásra lép "
            "életbe.",
        "desc.key_mode1": "Vesszővel elválasztva, pl. '1, f1, "
            "ctrl+f1, v'. Hogy mit csinál a klasszikus mód, a "
            "Billentyűk lap mondja el.",
        "desc.key_mode2": "Vesszővel elválasztva, pl. '2, f2, "
            "ctrl+f2, b'. Hogy mit csinál a vezető mód, a Billentyűk "
            "lap mondja el.",
        "desc.key_pause": "Az egér és a billentyűzet újra teljesen "
            "az Öné, amíg el nem indítja.",
        "desc.key_play": "A Makrók listában kiválasztott felvételt "
            "játssza, ha nincs kiválasztva, a legújabbat. Ismétlődő "
            "felvételnél leállítja azt.",
        "desc.key_play_n": "A Makrók lap sorszámozott listájának "
            "#%d. felvételét játssza, a lista szerinti helye "
            "alapján. Ha a lista rövidebb, semmi sem történik.",
        "desc.key_record": "Rögzít mindent, amit csinál - minden "
            "billentyűt, egérkattintást és kurzormozgást -, miközben "
            "a bemenete továbbra is eljut a programokba, amíg a "
            "leállító gyorsbillentyű el nem menti a Makrók listába. "
            "Csak indított állapotban éles.",
        "desc.key_record_stop": "Leállítja a rögzítést, elmenti a "
            "sort a Makrók listába, és leállítja a futó lejátszást.",
        "desc.luminance_norm": "Az éleket a környezetük fényerejéhez "
            "mérten bírálja, így a sötét témák úgy működnek, mint a "
            "világosak. Ajánlott.",
        "desc.macro_action": "Az a kombináció, amelyet nyomásonként "
            "Ön helyett nyomunk le (egy nyomás = egy kombi-nyomás): "
            "'ctrl+c', 'ctrl+shift+s', 'space', 'f5' ... Üres = "
            "makró kikapcsolva.",
        "desc.macro_key": "A gomb, amely a makrót JELENTI gépelés "
            "helyett: 'b', 'f7', 'ctrl+b' ... Indított állapotban "
            "egy nyomás pontosan egyszer küldi el a mellette lévő "
            "kombinációt, és maga a gomb nem jut el a programjaiba. "
            "Szünetben normálisan gépel. Üres = makró kikapcsolva.",
        "desc.max_area": "A nagyobb foltok kiesnek - általában egész "
            "ablakok vagy háttér, nem kattintható elemek.",
        "desc.max_dim": "Az ennél szélesebb vagy magasabb elemek "
            "kiesnek; a képernyő szélén lévők, mint a görgetősávok, "
            "kétszeresét kapják.",
        "desc.merge_distance": "Az ennél közelebbi darabok (tört "
            "körvonal, ikon a címkéje mellett) egy elemmé lesznek. "
            "Két teljes elem sosem ragad össze.",
        "desc.min_area": "A kisebb foltok pacaként esnek ki, hacsak "
            "nem ragadnak nagyobb elemhez.",
        "desc.min_contrast": "Egy elemnek legalább ennyire élesnek "
            "kell lennie, hogy egyáltalán kattintható legyen. 28 "
            "alatti értékek 28-nak számítanak: egy beépített "
            "minőségi küszöb tartja távol a zajt a "
            "kattinthatóságtól.",
        "desc.motion_3d": "Mozgó elemeket pozícióVAL ÉS méretTEL "
            "követi egyenes illesztés helyett: az egyedi hibás "
            "scannelések figyelmen kívül maradnak a követő "
            "megvakítása helyett, a kanyarokat végigköveti, és egy "
            "hirtelen méretugrás újraindítja a sávot (az a szkenner "
            "másik elemet fogott). Ugyanazok a sebességkapuk, "
            "ugyanaz a 80 px-es sapka - csak okosabb logika. Magában "
            "is működik.",
        "desc.motion_lead_ms": "Ezredmásodperc előrejelzés mozgó "
            "elemnél (0-300): 40-80 lassú görgetéshez, 100-150 gyors "
            "videósávhoz. Maximum 80 px, lassú vagy forduló "
            "mozgásnál kikapcsol.",
        "desc.motion_predict": "Mozgó elemeknél (görgő listák, videó "
            "sávok) kicsit előre céloz, hogy a kattintás az elemen "
            "landoljon. Álló elemeket nem érint.",
        "desc.mouse2_action": "Mit csinál MÉG egy rövid jobb "
            "kattintás - maga a jobb kattintás mindig megtartja a "
            "normál Windows funkcióját. Alap: semmit.",
        "desc.mouse2_hold_action": "Ugyanazok a lehetőségek, amikor "
            "a jobb gombot fél másodpercig NYOMVA TARTJA kattintás "
            "helyett. Egy nyomás vagy kattintás, vagy tartás, sosem "
            "mindkettő. Alap: semmit.",
        "desc.on_target_dist": "Ha a kattintás ennyi pixelen belül "
            "landol az elem közepétől, semmi sem mozdul - eltalálta.",
        "desc.radius": "Keresési távolság pixelben (40-400). "
            "Növelje, ha a kívánt elem éppen kívül esik; csökkentse, "
            "ha a rossz szomszéd nyer.",
        "desc.rapid_click_snap": "Ki (alap): amíg egy kattintás fut, "
            "a többi a Windowsé. Be: minden bal kattintás "
            "asszisztált.",
        "desc.snap_offset_x": "A kattintási pontot oldalra tolja az "
            "elem közepéből (-200-tól 200-ig, a negatív balra). "
            "Olyan vezérlőhöz, amelynek közepe halott - osztott "
            "gomb, csúszka -, tekerje a kattintást egyszer az élő "
            "pontra ahelyett, hogy minden snappel küzdene.",
        "desc.snap_offset_y": "A kattintási pontot függőlegesen "
            "tolja az elem közepéből (-200-tól 200-ig, a negatív "
            "felfelé). Ugyanaz, mint az oldalsó tolás: az élő részre "
            "érkezzen.",
        "desc.stall_pause_seconds": "Ha egy beolvasás elakad, az "
            "asszisztencia ennyi ideig szünetel, és minden nyomva "
            "tartott kattintás vissza kerül Önhöz.",
        "desc.watcher_seconds": "Klasszikus módban egy második snap "
            "ugyanazon hely közelében ennyi időn belül dupla "
            "kattintássá válik az elemen.",
        "ent.cancel_line": "aktív %s-ig - NEM újítódik meg",
        "ent.canceled_line": "az előfizetés véget ért%s",
        "ent.expired_line": "%s-n lejárt - újítsa meg a Stripe-on",
        "ent.past_due_line": "a fizetés sikertelen - javítsa a "
            "kártyát a Stripe nyugta e-mailben; a hozzáférés "
            "visszatér, ha a számla kifizetődik",
        "ent.plan": " (%s)",
        "ent.refunded_line": "visszatérítve / visszakövetelve - az "
            "aktiválás visszavonva",
        "ent.st.active": "aktív",
        "ent.st.canceled": "vége",
        "ent.st.canceling": "aktív, de lemondásra áll",
        "ent.st.grant": "támogatói engedély",
        "ent.st.past_due": "FIZETÉS SIKERTELEN",
        "ent.st.refunded": "visszatérítve / visszakövetelve",
        "ent.st.trial": "próba",
        "ent.st.unsubscribed": "nincs előfizetés",
        "ent.until": " eddig: %s",
        "err.auth_unreachable": "A Snappy AI hitelesítő szervere nem "
            "érhető el:\n%s\n\nA Snappy AI csak élő válasszal "
            "fut.\nÚjra?",
        "err.start_fail": "A Snappy AI nem tudott "
            "elindulni.\nFuttassa --console kapcsolóval a "
            "részletekért.",
        "gate.btn.monthly": "Havi előfizetés 9,99€-ért",
        "gate.btn.trial": "Próbavásárlás 1,99€-ért",
        "gate.head.canceled": "Ez az előfizetés le lett mondva - "
            "indítson újat a Stripe-on a folytatáshoz.",
        "gate.head.canceling": "Az előfizetése lemondásra áll - "
            "%s-ig aktív marad, utána ez a bejelentkezés újra zár, "
            "hacsak nem újítja meg.",
        "gate.head.email_mismatch": "A fizetés másik e-mail címről "
            "történt, mint a Discord-fiókja. Az előfizetés csak az "
            "alul látható Discord e-mailen működik - azzal fizessen "
            "újra, vagy keresse a támogatást.",
        "gate.head.expired": "Ennek a bejelentkezésnek az "
            "előfizetése lejárt - újítsa meg a Stripe-on a "
            "folytatáshoz.",
        "gate.head.none": "Bejelentkezett, de ennek a "
            "bejelentkezésnek nincs aktív előfizetése. EZZEL a "
            "Discord e-maillel fizessen - más címen történő vásárlás "
            "nem aktiválhatja.",
        "gate.head.past_due": "Az utolsó előfizetési fizetés "
            "sikertelen - javítsa a Stripe-on, ettől lesz újra aktív "
            "ez a bejelentkezés.",
        "gate.head.refunded": "Ezt a vásárlást visszatérítették vagy "
            "visszakövetelték, így az aktiválás visszavonva. Egy új "
            "előfizetés ezen a Discord e-mailen újra aktivál.",
        "gate.head.shared": "Ez a fiók MOST egy MÁSIK gépen futtatja "
            "a Snappy AI-t. Amíg ugyanaz a Discord-fiók két helyen "
            "fut, a Snappy AI kikapcsolva marad - zárja be a másik "
            "munkamenetet, majd ellenőrizzen újra. A megosztott "
            "előfizetés emeli az árakat; kérjük, ne.",
        "gate.msg.active": "Az előfizetés aktív - a Snappy AI "
            "indul...",
        "gate.msg.checking": "Ellenőrzés a szerverrel...",
        "gate.msg.no_link": "Ez a fizetési link nincs beállítva ezen "
            "a builden.",
        "gate.msg.open_fail": "Nem indult böngésző. Nyissa meg ezt a "
            "linket kézzel:\n%s",
        "gate.msg.open_ok": "A Stripe megnyílt a böngészöben - fizessen ott. Ez az ablak magártál felfigyel a fizetésre, és elindítja a motort.",
        "gate.msg.session_gone": "A munkamenet eltűnt - jelentkezzen "
            "be újra.",
        "gate.msg.still_none": "Ennél a bejelentkezésnél továbbra "
            "sem aktív előfizetés.",
        "gate.msg.still_shared": "Továbbra is használatban van egy "
            "másik gépen - zárja be azt a munkamenetet, majd "
            "ellenőrizzen.",
        "gate.msg.unreachable": "A hitelesítő szerver nem érhető el: "
            "%s",
        "gate.note": "A motor azonnal indul, amint az előfizetés "
            "aktív - ez az ablak 30 másodpercenként maga is "
            "ellenőriz. A bezárás visszavisz a bejelentkezéshez.",
        "gate.prices": "2 napos próba: 1,99€ (egyszeri)  -  "
            "előfizetés: 9,99€ / hó.\nAz aktiválás a fizetés után "
            "legfeljebb ~10 perccel érkezik; a megújítások ugyanazt "
            "a bejelentkezést automatikusan újra aktiválják.",
        "gate.title": "%s - Előfizetés%s",
        "hdr.build": "build %s",
        "help.1.b": "A Snappy AI a kurzor körüli képernyőt nézi, "
            "megkeresi a közelben lévő tömör, elem alakú dolgokat - "
            "gombokat, ikonokat, linkeket - és a legjobbat "
            "választja: éles élek, tisztességes méret és a kurzor "
            "közelsége nyer. A saját színe, a soha-nem-kattintható "
            "lista és az utolsó kattintás emléke befolyásolhatja a "
            "választást. A kurzor ezután az elem közepére céloz, nem "
            "a kerete sarkára.",
        "help.1.t": "Mi történik kattintáskor",
        "help.10.b": "1. Indítva van? A szünet azt jelenti, semmi "
            "sem kerül elfogásra - a 'Gyorsbillentyű: asszisztencia "
            "indítása' (alap Ctrl+L) az egyetlen be/ki.  2. Tartsa a "
            "Shiftet egy kattintásnál, hogy ellenőrizze, az "
            "asszisztencia volt-e a gond.  3. Rossz elem nyer: "
            "csökkentse a 'Keresési távolság a kurzortól' értékét, "
            "azután állítsa be a 'Saját szín(ek)'-t vagy emelje a "
            "'Színelőny ereje'-t.  4. Semmit sem talál: csökkentse a "
            "'Milyen halvány él számít' és a 'Minimális él-élesség' "
            "értékét, növelje a 'Legnagyobb szélesség vagy "
            "magasság'-ot vagy a 'Közeli darabok összeragasztása'-t. "
            " 5. Valamit soha nem szabad asszisztálni: tegye a "
            "színét a a 'Soha-nem-kattintható szín(ek)' közé.  6. "
            "Még mindig rossz: jelölje be a támogatásnak, hova "
            "kattintott és mit várt helyette, és mellékelje a "
            "naplófájlt, amelyet a Snappy AI az adatmappájába ír.",
        "help.10.t": "Ha valami nem stimmel, ebben a sorrendben",
        "help.2.b": "A vezető mód (alap) nem eszi meg a kattintást: "
            "a kattintás eljut a programba, elengedés után pedig a "
            "kurzor a legközelebbi tiszta elemre megy. A klasszikus "
            "mód erősebb: egy elem közelében történt félrekattintást "
            "elkap, a kurzor rátapad, és a Snappy AI Ön helyett "
            "kattint. A 'Keresési távolság a kurzortól' adja a "
            "keresési kört - növelje, ha a kívánt elem éppen kívül "
            "esik, csökkentse, ha a rossz szomszéd nyer. A Shift "
            "nyomvatartása egy kattintást mindkét módban kikerül.",
        "help.2.t": "Először: mód és keresési távolság",
        "help.3.b": "A Kezelő lapon a 'Milyen halvány él számít' és "
            "a 'Minimális él-élesség' dönti el, mely élek "
            "számítanak: lejjebb halványabbakat talál, feljebb a "
            "zajt hagyja ki. A 'Legkisebb elemméret', 'Legnagyobb "
            "elemterület' és 'Legnagyobb szélesség vagy magasság' "
            "kipotyogtatja a pacákat és a teljes ablakokat. A "
            "'Közeli darabok összeragasztása' egy törött körvonalat "
            "vagy egy ikon a címkéje mellett egy elemmé fűz. Az "
            "Asszisztencia lapon az 'Automatikus igazítás halvány "
            "képernyőkhöz' és az 'Éleket relatív fényerő szerint "
            "bírálja' teszi a sötét témákat a világosakhoz hasonlóvá "
            "- mindkettő maradjon bekapcsolva.",
        "help.3.t": "Semmit sem talál - vagy túl sokat",
        "help.4.b": "A Színek lapon a 'Saját szín(ek)' a kedvelt "
            "szín, a 'Soha-nem-kattintható szín(ek)' pedig abszolút: "
            "az ilyen színű elemek soha nem asszisztáltak. A 'Csak a "
            "saját színemet asszisztálja' a megfelelő elemekre "
            "korlátoz. A Kezelő lapon a 'Színegyezés szigorúsága' "
            "mondja meg, mennyire kell közel lennie egy árnyalatnak, "
            "a 'Hasonló árnyalatok elfogadása' részben beszámítja a "
            "világosabb vagy fakóbb változatokat, a 'Színelőny "
            "ereje' pedig, mennyit emel az elemen a saját színe - "
            "emelje, ha mégis a rossz nyer.",
        "help.4.t": "Munka a színekkel",
        "help.5.b": "Az 'Emlékezzen az utolsó kattintott elemre' "
            "továbbra is azt az elemet részesíti, amelyen az utolsó "
            "sikeres kattintása landolt, a 'Meddig emlékezzen' "
            "másodpercig - ettől kellemesek a görgetősávok és a "
            "párbeszédgombok. Az 'Emlékezet ereje' megadja, mennyire "
            "erősen nyer, a 'Mit tanulhat az emlékezet' pedig védi: "
            "a 'Csak a saját színem elemei' mellett egy "
            "félrekattintás nem irányíthatja át. A 'Nyomva tartott "
            "gombnál marad az elemen' stabilizálja a húzásokat, a "
            "Kísérleti lap jobb gomb műveletei pedig egérrel "
            "követhetik vagy törölhetik az emlékezetet.",
        "help.5.t": "Ismételt kattintások egy kezelőszerven",
        "help.6.b": "A 'Mozgó célok megelőzése' méri, milyen gyorsan "
            "halad a kiválasztott elem, és a 'Mennyivel előre "
            "célozzon' ezredmásodpercnyivel előre céloz, hogy a "
            "kattintás egy görgő listán vagy videósávon landoljon, "
            "ne mötte. Az előrejelzés 80 pixelnél tetőzik, és álló "
            "vagy forduló elemnél magától kikapcsol.",
        "help.6.t": "Mozgó dolgok kattintása",
        "help.7.b": "'Kurzormozgás animálása' = 0 azonnal ugrik; "
            "40-120 csúszik, hogy látni lehessen, és a saját "
            "egérmozgás megszakítja. A 'Dupla kattintás ablaka' "
            "klasszikus módban egy második, közeli snapet dupla "
            "kattintássá alakít. A 'Minden gyors kattintást "
            "asszisztál' egy gyors sorozat minden kattintását "
            "asszisztálja az első helyett. A 'Szünet akadás után' az "
            "a biztonsági szelep, amely visszaadja a nyomva tartott "
            "kattintást, ha egy beolvasás elakad.",
        "help.7.t": "Hogyan érződnek a kattintások",
        "help.8.b": "A Gyorsbillentyűk lap elmagyarázza a két módot "
            "és a felvételi folyamatot. Röviden: a Ctrl, Alt, Shift "
            "vagy Win billentyűket tartalmazó gyorsbillentyűk "
            "rendszerszinten foglaltak; a puszta egygombos "
            "billentyűk mindenütt aktiválódnak, de a karaktert is "
            "beírják. Egy makró egy gombnyomást teljes kombinációvá "
            "alakít. A felvételek rögzítik a valódi bemenetet - "
            "minden gombot, egérkattintást és kurzormozgást -, és a "
            "Makrók lapról játsszák le, mindegyik saját egyszeri "
            "vagy ismétlődő kapcsolóval.",
        "help.8.t": "Gombok, makrók és felvételek",
        "help.9.b": "A Nyelv gomb a 'Beállítások exportálása' "
            "mellett - valamint a bejelentkező és az előfizetői "
            "ablakban - azonnal átállítja a teljes felületet, "
            "újraindítás nélkül, és megjegyzi a választását. A még "
            "fordítás alatt álló nyelvek nem választhatók, így ami "
            "választható, az teljes.",
        "help.9.t": "Nyelv",
        "help.sub": "Minden beállítás azzal a névvel, ahogy a lapján "
            "látja, abban a sorrendben, ahogy szüksége lesz rájuk. A "
            "név fölé vitt egér mutatja a rövid leírást; ez az oldal "
            "a hosszú változat.",
        "help.tail": "A beállítások az Alkalmaz megnyomására lépnek "
            "életbe. A program melletti config.ini felülírja a "
            "config.json-t. Ez az oldal magyaráz, nem beállít.",
        "help.title": "A Snappy AI beállítása közérthetően",
        "kb.keys.b": "A Ctrl, Alt, Shift vagy Win billentyűt "
            "tartalmazó gyorsbillentyű rendszerszinten foglalt: csak "
            "a Snappy AI látja. Egy puszta egyetlen gomb (mint 1 "
            "vagy 2) minden programban működik ÉS normálisan gépel - "
            "az ára, hogy mondat közben lenyomva a műveletét is "
            "kiváltja. Klasszikus viselkedést az 'Egygombos "
            "gyorsbillentyűk elnyelik a gombot' kapcsoló ad a "
            "Asszisztencia lapon. A makrók tovább mennek: indított "
            "állapotban a kiváltó gomb elnyelődik, és a mellette "
            "lévő kombináció pontosan egyszer kerül elküldésre.",
        "kb.keys.t": "Egygombos gyorsbillentyűk és kombinációk",
        "kb.mode.b": "Vezető mód (alap, 2-es gyorsbillentyű): a "
            "kattintása mindig érintetlenül jut el a programba; "
            "elengedés után a kurzor a legközelebbi tiszta elemre "
            "megy, így a következő kattintás onnan indul. Semmi sem "
            "nyelődik el - ez a legbiztonságosabb mód.  Klasszikus "
            "mód (1-es gyorsbillentyű): ha egy elem közelében "
            "kattint, azt a félrekattintást elkapjuk, a kurzor az "
            "elemre tapad, és a Snappy AI Ön helyett kattint; ha "
            "nincs közelben elem, a kattintás érintetlenül vissza "
            "kerül.  Mindkét módban a Shift nyomvatartása kattintás "
            "közben egy kattintásra kikapcsolja az asszisztenciát.",
        "kb.mode.t": "Mit csinál a két mód",
        "kb.rec.b": "Indított állapotban nyomja meg a felvétel "
            "gyorsbillentyűt (alapértelmezés Ctrl+Alt+R): minden "
            "lenyomott gomb, minden egérkattintás és minden "
            "kurzormozgás rögzítésre kerül ÉS továbbra is eljut a "
            "programjaiba, így normálisan dolgozhat felvétel közben. "
            "A leállító gyorsbillentyű (Ctrl+Alt+S) menti a Makrók "
            "lap listájába - öt felvétel fér el ott. Kattintson egy "
            "felvételre a kiválasztásához, az «Átnevezés» vagy "
            "«Exportálás» használatához, és állítsa be saját "
            "«Ismétlés leállításig» kapcsolóját. A lejátszás "
            "gyorsbillentyű (Ctrl+Alt+M) a ott kiválasztott "
            "felvételt játssza; a Ctrl+1..Ctrl+5 a lista szerinti "
            "pozíció szerint. Szünetben semmi sem rögzítődik és "
            "semmi sem kerül beszúrásra - a bemenet teljesen az Öné.",
        "kb.rec.t": "Saját billentyű- és egérműveletek felvétele és "
            "lejátszása",
        "lang.close": "Bezárás",
        "lang.coverage": "%d%% lefordítva",
        "lang.current": "Jelenleg: %s",
        "lang.progress": "Még fordítás alatt, ha kész, megjelenik: "
            "%s",
        "lang.prompt": "A váltás azonnal él - az ablak nyitva marad, "
            "hogy többet is kipróbálhasson.",
        "lang.title": "Nyelv",
        "lbl.accent_boost": "Színelőny ereje",
        "lbl.accent_coherent": "Szétszórt színpöttyök mellőzése",
        "lbl.accent_color": "Saját szín(ek)",
        "lbl.accent_matcher": "Színegyeztető motor",
        "lbl.accent_only": "Csak a saját színemet asszisztálja",
        "lbl.accent_soft": "Hasonló árnyalatok elfogadása",
        "lbl.accent_tolerance": "Színegyezés szigorúsága",
        "lbl.accent_variants": "Saját szín világos és sötét "
            "állapotai",
        "lbl.adaptive_threshold": "Automatikus igazítás halvány "
            "képernyőkhöz",
        "lbl.auto_click": "Magától kattint az elemekre",
        "lbl.auto_click_interval": "Másodperc az automatikus "
            "kattintások közt",
        "lbl.auto_click_max_clicks": "Automatikus kattintások határa "
            "munkamenetenként",
        "lbl.auto_click_min_contrast": "Milyen éles legyen az "
            "automatikus cél",
        "lbl.auto_click_radius": "Milyen messzire nézzen a középtől",
        "lbl.auto_click_repeat_px": "Ne kattintson újra ugyanarra a "
            "helyre",
        "lbl.auto_click_settle_ms": "Szünet az automatikus kattintás "
            "előtt",
        "lbl.block_bound_keys": "Az egygombos gyorsbillentyűk "
            "elnyelik a gombot",
        "lbl.capture_backend": "Képernyőrögzítő motor",
        "lbl.color_adapt": "Alkalmazkodás a képernyő fényéhez",
        "lbl.contrast_threshold": "Milyen halvány él számít",
        "lbl.exclude_color": "Soha-nem-kattintható szín(ek)",
        "lbl.follow_boost": "Emlékezet ereje",
        "lbl.follow_enabled": "Emlékezzen az utolsó kattintott "
            "elemre",
        "lbl.follow_learn": "Mit tanulhat az emlékezet",
        "lbl.follow_seconds": "Meddig emlékezzen",
        "lbl.glide_ms": "Kurzormozgás animálása",
        "lbl.hold_follow": "Nyomva tartott gombnál marad az elemen",
        "lbl.key_launch": "Gyorsbillentyű: asszisztencia indítása",
        "lbl.key_mode1": "Gyorsbillentyű: klasszikus mód (max 4 "
            "gomb)",
        "lbl.key_mode2": "Gyorsbillentyű: vezető mód (max 4 gomb)",
        "lbl.key_pause": "Gyorsbillentyű: szünet",
        "lbl.key_play": "Gyorsbillentyű: kiválasztott felvétel "
            "lejátszása",
        "lbl.key_play_n": "Gyorsbillentyű: %d. felvétel lejátszása",
        "lbl.key_record": "Gyorsbillentyű: felvétel indítása",
        "lbl.key_record_stop": "Gyorsbillentyű: felvétel leállítása "
            "és mentése",
        "lbl.luminance_norm": "Éleket relatív fényerő szerint "
            "bírálja",
        "lbl.macro_action": "%d. makró: ezt küldi helyette",
        "lbl.macro_key": "%d. makró: ezt a gombot nyomja",
        "lbl.max_area": "Legnagyobb elemterület",
        "lbl.max_dim": "Legnagyobb szélesség vagy magasság",
        "lbl.merge_distance": "Közeli darabok összeragasztása",
        "lbl.min_area": "Legkisebb elemméret",
        "lbl.min_contrast": "Minimális él-élesség",
        "lbl.motion_3d": "Okosabb követés mozgó elemeknél",
        "lbl.motion_lead_ms": "Mennyivel előre célozzon",
        "lbl.motion_predict": "Mozgó célok megelőzése",
        "lbl.watch_center_only": "Csak a képernyő közepét figyelje",
        "desc.watch_center_only": "A segítség csak a képernyő közepén lévő rögzített négyzetet "
            "figyeli (méret = keresési távolság, alapértelmezés szerint 150×150 "
            "px), függetlenül a kurzor helyétől. A négyzeten kívüli kattintások "
            "érintetlenek maradnak.",
        "lbl.center_follow": "A képernyő követi a célt",
        "desc.center_follow": "Ha a „Csak a képernyő közepét figyelje” be van kapcsolva: egy elem "
            "megragadása után a segítség mozgatja a képernyőt, hogy középen "
            "maradjon – különösen görgetett felületeknél. Mozgasd magad a "
            "képernyőt a követés elengedéséhez.",
        "lbl.input_backend": "Beviteli mód",
        "desc.input_backend": "A Windows-befecskendezés (alapértelmezett) mindenhol működik. Az "
            "Interception illesztőprogramon keresztül küld, és a játékok valódi "
            "egérként ismerik fel; telepített Interception-illesztőprogramot és "
            "az interception.dll-t igényli a program mellett; hiányában "
            "automatikusan a Windows-befecskendezést használja.",
        "val.input_backend.win32": "Windows-befecskendezés",
        "val.input_backend.interception": "Interception (illesztő)",
        "lbl.mouse2_action": "Jobb gomb kiegészítő művelete",
        "lbl.mouse2_hold_action": "Jobb gomb nyomvatartásának "
            "művelete",
        "lbl.on_target_dist": "„Már eltalálva” távolság",
        "lbl.radius": "Keresési távolság a kurzortól",
        "lbl.rapid_click_snap": "Minden gyors kattintást asszisztál",
        "lbl.snap_offset_x": "Kattintási pont: balra / jobbra tolás",
        "lbl.snap_offset_y": "Kattintási pont: fel / le tolás",
        "lbl.stall_pause_seconds": "Szünet akadás után",
        "lbl.watcher_seconds": "Dupla kattintás ablaka",
        "login.failed": "A(z) %s bejelentkezés nem fejeződött be - "
            "próbálja újra.",
        "login.no_provider": "Ebbe a példányba nincs bejelentkező "
            "szolgáltató beépítve.",
        "login.not_configured": "Az előfizetési fájl ezen a builden "
            "még nincs beállítva.",
        "login.note": "A bejelentkezés megnyitja a böngészőt, és "
            "magától visszaér ebbe az ablakba.",
        "login.provider": "Bejelentkezés ezzel: %s",
        "login.signedin": "Bejelentkezve mint %s.",
        "login.sub": "Bejelentkezés Discorddal - az előfizetése "
            "ehhez a fiókhoz kötődik, és a fizetésnek ennek az "
            "e-mail címét kell használnia. Itt nincs jelszó.",
        "login.title": "%s - Bejelentkezés",
        "login.unreachable": "A hitelesítő szerver nem érhető el: %s",
        "login.waiting": "Várakozás a böngészőre - fejezze be a(z) "
            "%s bejelentkezést...",
        "mac.delete": "Törlés",
        "mac.empty": "Még nincs felvétel - indítsa el, nyomja meg a "
            "felvétel gyorsbillentyűt és dolgozzon szokás szerint: "
            "minden gomb, kattintás és kurzormozgás rögzítésre "
            "kerül.",
        "mac.export": "Exportálás",
        "mac.import": "Importálás",
        "mac.keys_head": "Billentyűmakrók",
        "mac.loop": "Ismétlés leállításig",
        "mac.recordings": "Felvételek",
        "mac.rename": "Átnevezés",
        "mac.row": "%d. makró",
        "mac.sends": "küld",
        "mac.steps": "%d lépés",
        "note.advanced": "Távolság- és időzítés-beállítások, amelyek "
            "a kattintás érzetét változtatják, nem azt, mi található "
            "meg. A legtöbben sosem nyúlnak ezekhez; az alapértékek "
            "a teszteltek.",
        "note.assist": "Minden kapcsoló, amely indított állapotban a "
            "viselkedést változtatja. A két mód a mód-gombjaival "
            "vált - a Billentyűk lap elmondja, mit csinál egyik és "
            "másik. Az asszisztencia mindig szünettel indul; az "
            "Indítás az egyetlen be/ki. Hogy hová néz a motor és "
            "milyenek a kattintások, a Haladó lapon; mi számít "
            "elemnek, a Kezelőn.",
        "note.colors": "A két lista felül dönti el, mely színek a "
            "kedveltek és melyek a tiltottak a Snappy AI számára. "
            "Mindkettő a színeit mezőkként mutatja a jobb oldalon, "
            "legfeljebb tizenötöt, és egy mezőre kattintva az a szín "
            "újra kikerül; az üres lista áthúzott mezőt mutat, és "
            "kikapcsoltnak számít. A «Kedvelt szín hozzáadása» és a "
            "«Tiltott szín hozzáadása» a keverőben álló színt teszi "
            "a megfelelő listába. A Jelenlegi RGB-érték három mezőt "
            "mutat - mindegyik öt színmezőnyi széles, így a sor "
            "ugyanazt a tizenöt mezőt íveli át, mint minden alatta "
            "-, amelyek annál jobban ragyognak, minél több vöröset, "
            "zöldet, illetve kéket tartalmaz a keverőben álló szín; "
            "a sor követi a keverőt, és nem gépelhető. A keverő "
            "alatta úgy kever színt, mint egy festőprogram; minden, "
            "ami mellette van, az ablak jobb oldalán áll, "
            "ugyanakkora hézaggal a szélig, mint a beállítások "
            "felül, és minden sor ugyanazt a tizenöt mezős "
            "szélességet íveli át: a magas bemutató a benne rajzolt "
            "#értékkel, majd a tizenöt kész szín, a két hozzáadás "
            "gomb és a képernyő sor - a «Szín vétele a képernyőről» "
            "a kurzor alatti egyetlen színt veszi, a «Színjavaslat a "
            "képernyőről» tizenöt saját mezőt tölt meg a kurzor "
            "körül talált színekkel, és egyre kattintva az a "
            "keverőbe kerül. A bemutató ezért magas: így a "
            "javaslatmezők pontosan a bal oldali színcsúszka aljáig "
            "érnek.",
        "note.experimental": "Motorválasztások, mindegyik tesztelt "
            "alappal. Csak akkor módosítsa, ha motorokat hasonlít "
            "össze, szokatlan hardveren fut, vagy a támogatás kéri - "
            "a rögzítő motor újraindítás után lép életbe.",
        "note.handler": "Mi számít kattintható elemnek: milyen "
            "halvány lehet egy él, mennyire kell élesnek lennie, és "
            "mekkora elem fér bele. Semmit sem talál? Lazítson "
            "ezeken. Rosszat talál? Szigorítson, vagy használja a "
            "saját színét a Színek lapon.",
        "note.keybindings": "Minden gyorsbillentyű - alatta pedig, "
            "mit csinál a két mód, hogyan vegyen fel saját "
            "billentyű- és egérműveleteket, és miben tér el az "
            "egygombos gyorsbillentyű a kombinációtól.",
        "note.macros": "Egy makró egy gombnyomást teljes "
            "kombinációvá alakít indított állapotban. A makrók "
            "mellett a felvételek: legfeljebb öt, névvel ellátott "
            "rögzítés mindenről, amit tett - minden gomb, "
            "egérkattintás és kurzormozgás -, pontosan úgy "
            "lejátszva, ahogy rögzítette. Kattintson egy felvételre "
            "a kiválasztásához; minden sor saját «Ismétlés "
            "leállításig» kapcsolót hordoz, a «Átnevezés», "
            "«Exportálás», «Importálás» és «Törlés» gombok pedig a "
            "doboz alján ülnek.",
        "note.macros_keys": "A felvétel/lejátszás gyorsbillentyűk a "
            "Billentyűk lapon vannak (alap: Ctrl+Alt+R felvétel, "
            "Ctrl+Alt+S leállítás és mentés, Ctrl+Alt+M lejátszás, "
            "Ctrl+1..5 a lista szerinti lejátszás).",
        "online.cancelled": "A Discord hitelesítés megszakadt (vagy "
            "sikertelen volt). Próbálja újra.",
        "rec.export_fail": "Az export nem sikerült: %r",
        "rec.exported": "Exportálva ide: %s",
        "rec.import_fail": "Az import nem sikerült: %r",
        "rec.imported": "%d felvétel importálva%s.",
        "rec.imported_none": " (egyik sem volt érvényes)",
        "rec.no_sel": "Nincs kiválasztva semmi az exporthoz.",
        "rec.notfile": "Az import nem sikerült: nem felvételi fájl.",
        "shared.back": "Isten hozott - ha kész, indítson.",
        "shared.body": "Ez a Discord-fiók most egy MÁSIK gépen "
            "futtatja a Snappy AI-t.\nAz asszisztencia itt szünetel, "
            "amíg csak egy munkamenet marad.\n\nEgy előfizetés, egy "
            "gép egyszerre - ez tartja alacsonyan az árat és életben "
            "a fejlesztést.",
        "shared.close": "Bezárás",
        "shared.recheck": "Ellenőrzés most",
        "shared.still": "Továbbra is máshol használatban - "
            "szünetelek.",
        "shared.title": "Fiók máshol használatban",
        "shared.unreachable": "A szerver nem érhető el - "
            "újraellenőrzök.",
        "st.all_files": "Minden fájl",
        "st.color_added": "rgb(%d, %d, %d) hozzáadva ehhez: %s - az "
            "Alkalmaz menti.",
        "st.color_already": "rgb(%d, %d, %d) már benne van: %s.",
        "st.color_full": "%s már 15 színt tartalmaz - előbb "
            "kattintson az egyik mezőre egy szín eltávolításához.",
        "st.color_removed": "rgb(%d, %d, %d) eltávolítva innen: %s - "
            "az Alkalmaz menti.",
        "st.delete_confirm": "Törli a(z) %r felvételt?\nEz nem "
            "vonható vissza.",
        "st.deleted": "A felvétel törölve.",
        "st.engine_dead": "A motor szála nem elérhető - a "
            "gyorsbillentyűk nem reagálnak.",
        "st.ent_paused": "Az előfizetés %s - az asszisztencia "
            "szünetel. Újítson a Stripe-on, majd indítsa újra.",
        "st.ent_unreachable": "Előfizetés-ellenőrzés: a szerver nem "
            "érhető el (a munkamenet fut tovább).",
        "st.export_fail": "Exportálás nem sikerült: %r",
        "st.export_rec_title": "Felvételek exportálása",
        "st.export_title": "Beállítások exportálása",
        "st.exported": "Beállítások exportálva: %s",
        "st.file_rec": "Snappy AI felvétel",
        "st.file_settings": "Snappy AI beállítások",
        "st.follow": "  |  követés %d mp",
        "st.import_fail": "Az import nem sikerült: %r",
        "st.import_notfile": "Az import nem sikerült: nem beállítási "
            "fájl.",
        "st.import_rec_title": "Felvételek importálása",
        "st.import_title": "Beállítások importálása",
        "st.imported": "%d beállítás importálva%s.",
        "st.imported_ignored": ", kihagyva: %s",
        "st.ini_over": "Alkalmazva, de a config.ini felülírja: %s",
        "st.lib_empty": "A lista üres - nincs mit exportálni.",
        "st.line": "Asszisztált %d  |  átengedett %d%s  |  téma: %s",
        "st.loop_desc": "ENNEK a felvételnek a lejátszási módja: ki "
            "= egyszer játssza le; be = ismétli, amíg újra meg nem "
            "nyomja a lejátszás-gyorsbillentyűt. Minden felvételnek "
            "saját kapcsolója van, a felvétellel mentve.",
        "st.name_empty": "A név nem lehet üres.",
        "st.pick_err": "Vételezés nem sikerült: %r",
        "st.pick_fail": "Rögzítés nem sikerült - próbálja újra.",
        "st.pick_ok": "rgb(%d, %d, %d) vételezve itt: (%d, %d).",
        "st.pick_wait": "Vigye a kurzort a színre - rögzítés 3 mp "
            "múlva...",
        "st.preset_desc": "Előbeállítás: %s - kattintson, hogy a "
            "keverőbe töltse.",
        "st.rec_count": "%d / 5 felvétel",
        "st.rec_now": "%r most: %s.",
        "st.rec_once": "egyszer játssza le",
        "st.rec_playing": "%r lejátszása...",
        "st.rec_playing_loop": "%r lejátszása leállításig",
        "st.rec_recording": "FELVÉTEL - %s leállítja és menti",
        "st.rec_repeats": "ismétli leállításig",
        "st.registered": "Regisztrálva: %s    Állapot: %s",
        "st.rename_prompt": "Új név a(z) #%d. felvételnek:",
        "st.renamed": "A felvétel átnevezve.",
        "st.reset_confirm": "Minden beállítás visszaáll az "
            "alapértékre?\nA fiókok megmaradnak; ez csak a "
            "beállításokat érinti.",
        "st.rgb_bad": "Előbb érvényes R/G/B értékeket adjon meg.",
        "st.running": "Fut..",
        "st.saved": "Mentve és alkalmazva.",
        "st.defaults_restored": "Az alapértelmezett beállítások visszaállítva.",
        "st.saved_bad": "Mentve, de érvénytelen (a régi maradt): %s",
        "st.select_rec": "Előbb válasszon felvételt.",
        "st.shared_paused": "A FIÓK MÁSHOL HASZNÁLATBAN - az "
            "asszisztencia szünetel; egy előfizetés = egy gép.",
        "st.standby": "Készenlét..",
        "st.sug_fail": "Javaslat nem sikerült: %r",
        "st.sug_loaded": "A javasolt rgb(%d, %d, %d) a keverőben van "
            "- a fenti gombokkal vegye fel egy listára.",
        "st.sug_loaded_desc": "Javasolt felületszín: rgb(%d, %d, %d) "
            "- a mintavett terület %d%%-a. Kattintson, hogy a "
            "keverékbe töltse.",
        "st.sug_none": "Nincs színjavaslat ebből a régióból.",
        "st.sug_ok": "%d javaslat - kattintson egyre, hogy a "
            "keverőbe töltse.",
        "st.sug_wait": "Mutasson arra az appra, amelyben dolgozik - "
            "mintavétel 3 mp múlva...",
        "tab.advanced": "Haladó",
        "tab.assist": "Asszisztencia",
        "tab.colors": "Színek",
        "tab.experimental": "Kísérleti",
        "tab.handler": "Kezelő",
        "tab.help": "Súgó",
        "tab.hotkeys": "Billentyűk",
        "tab.macros": "Makrók",
        "theme.dark": "Sötét",
        "theme.light": "Világos",
        "val.accent_matcher.hsv": "Klasszikus - a régi motor",
        "val.accent_matcher.oklab": "Perceptuális - ahogy a színek "
            "látszanak (ajánlott)",
        "val.capture_backend.auto": "Automatikus - leggyorsabb "
            "biztonságos tartalékkal",
        "val.capture_backend.dxcam": "Desktop Duplication - "
            "leggyorsabb a legtöbb gépen",
        "val.capture_backend.mss": "Kompatibilis - mindig működik "
            "(távoli asztal, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "kísérleti",
        "val.follow_learn.accent": "Csak a saját színem elemei",
        "val.follow_learn.any": "Minden sikeres snap",
        "val.mouse2_action.1": "A követési feladat törlése",
        "val.mouse2_action.2": "Az utoljára elkapott szín követése",
        "val.mouse2_action.3": "A kurzor alatti szín vétele, majd "
            "követése",
        "val.mouse2_action.4": "Ne csináljon semmit",
        "val.mouse2_hold_action.1": "A követési feladat törlése",
        "val.mouse2_hold_action.2": "Az utoljára elkapott szín "
            "követése",
        "val.mouse2_hold_action.3": "A kurzor alatti szín vétele, "
            "majd követése",
        "val.mouse2_hold_action.4": "Ne csináljon semmit",
        "word.off": "Ki",
        "word.on": "Be",
    },
    "es": {
        "btn.apply": "Aplicar",
        "btn.export": "Exportar configuración",
        "btn.import": "Importar configuración",
        "btn.language": "Idioma: %s",
        "btn.launch": "Iniciar",
        "btn.logout": "Cerrar sesión",
        "btn.pause": "Pausa",
        "btn.restore": "Restaurar valores",
        "col.accent": "Acento",
        "col.add_pref": "Añadir a colores preferidos",
        "col.add_ref": "Añadir a colores rechazados",
        "col.chip_desc": "rgb(%d, %d, %d) en %s - haga clic en el "
            "cuadro para eliminar este color.",
        "col.chip_off": "%s no tiene colores - el cuadro tachado "
            "significa apagado. Elija un color abajo y pulse el "
            "botón de añadir correspondiente.",
        "col.exclude": "Exclusión",
        "col.pick": "Tomar color de la pantalla",
        "col.rgb.desc": "Tres cuadros muestran el color que hay "
            "ahora en el mezclador: el primero brilla según el rojo "
            "que contiene, el segundo según el verde, el tercero "
            "según el azul - más brillo significa más cantidad. La "
            "fila sigue al mezclador, a los tonos listos y a los "
            "botones de pantalla; no se puede escribir en ella.",
        "col.rgb.name": "Valor RGB actual",
        "col.suggest": "Sugerir colores en pantalla",
        "desc.accent_boost": "Cuánto eleva su color la puntuación de "
            "un elemento (0-3). Súbalo a 1,5-2 si aún gana el "
            "elemento equivocado.",
        "desc.accent_coherent": "Su color debe formar una mancha "
            "conectada para contar - motas dispersas de tramado o "
            "compresión nunca cualifican un elemento, ni lo "
            "potencian, ni lo ponen en la lista jamás clicable.",
        "desc.accent_color": "El color que Snappy AI debe preferir, "
            "mostrado como cuadros de color a la derecha. Elija un "
            "color abajo y pulse «Añadir a colores preferidos» para "
            "agregarlo - quince cuadros como mucho; haga clic en un "
            "cuadro para eliminar ese color de nuevo. Los elementos "
            "que contienen uno de ellos ganan los empates. Una lista "
            "vacía muestra un cuadro tachado y desactiva el ajuste.",
        "desc.accent_matcher": "Cómo se comparan los colores. "
            "Perceptual ordena por cómo se ven realmente y es el "
            "recomendado; Clásico es el motor antiguo, para "
            "comparar.",
        "desc.accent_only": "Solo los elementos con su color pueden "
            "asistirse; los clics en otro sitio pasan intactos a "
            "Windows.",
        "desc.accent_soft": "0-100: cuánto cuentan las versiones más "
            "claras, oscuras o lavadas de su color. 0 = solo tonos "
            "exactos.",
        "desc.accent_tolerance": "Cuán cerca debe estar un color "
            "para contar como suyo (4-90). Más bajo = más estricto.",
        "desc.accent_variants": "Copias más claras y más oscuras de "
            "su color también valen, para que los estados de paso, "
            "pulsado y atenuado cuenten sin ampliar la tolerancia de "
            "tono. Solo luminosidad - un tono erróneo nunca se "
            "cuela.",
        "desc.adaptive_threshold": "Los temas oscuros y documentos "
            "lavados bajan solos su listón de detección, así los "
            "elementos tenues también se encuentran. Recomendado "
            "activado.",
        "desc.auto_click": "Activado, el programa hace clic por sí solo cada 0,1 segundos en "
            "el mejor elemento del área observada, priorizando el contraste. "
            "Con color de acento definido, solo cuentan los elementos con ese "
            "color; sin color, solo se clican los dibujados con gran nitidez. "
            "Nunca dos veces en el mismo sitio ni en ventanas propias.",
        "desc.auto_click_interval": "Cada cuánto se busca su color "
            "en pantalla (0,5-60). Un número lento es el seguro: 2-5 "
            "va bien para un diálogo que usted observa.",
        "desc.auto_click_max_clicks": "Cuántas veces puede pulsar "
            "solo tras iniciar (1-200). Al llegar al límite se "
            "detiene y avisa, para que un mal ajuste no se "
            "descontrole.",
        "desc.auto_click_min_contrast": "En la misma escala que "
            "»Nitidez mínima del borde«. Empiece por el valor base y "
            "súbalo si pulsa lo incorrecto: solo valdrán elementos "
            "fuertes y bien dibujados.",
        "desc.auto_click_radius": "El clic automático busca "
            "alrededor del centro de la pantalla (40-600 px). Más "
            "para una ventana llena; menos para que solo vea el "
            "único control del centro.",
        "desc.auto_click_repeat_px": "Tras un clic automático, un "
            "objetivo dentro de estos píxeles se deja en paz "
            "(0-400). Sin esto, un botón que sigue en pantalla se "
            "pulsaría una y otra vez.",
        "desc.auto_click_settle_ms": "El cursor descansa así sobre "
            "el objetivo (0-2000 ms) antes del clic, para que el "
            "programa vea el resaltado primero. 120 va bien en casi "
            "todas las ventanas.",
        "desc.block_bound_keys": "No (predeterminado): un atajo sin "
            "Ctrl/Alt/Shift - como 1 o V - funciona en cada programa "
            "Y sigue escribiendo con normalidad, así que pulsarlo en "
            "mitad de una frase también dispara su acción. Sí: la "
            "acción sigue disparándose en todas partes, pero la "
            "tecla ya no escribe.",
        "desc.capture_backend": "Cómo se fotografía la pantalla. "
            "Automático usa el método compatible, que ve casi todas las ventanas; Compatible "
            "funciona siempre, incluso en Escritorio remoto y "
            "máquinas virtuales. Se aplica al reiniciar.",
        "desc.color_adapt": "Cada elemento se equilibra en blancos "
            "con su propio fondo antes de comparar, para que la luz "
            "nocturna y los tintes del tema dejen de sacar su color "
            "de la tolerancia. Apáguelo solo para comparar con el "
            "comparador sin adaptar.",
        "desc.contrast_threshold": "Más bajo encuentra elementos más "
            "tenues (y más ruido); más alto exige bordes más "
            "nítidos.",
        "desc.default": "Pase el cursor sobre un ajuste para ver qué "
            "hace.",
        "desc.exclude_color": "Los elementos con estos colores nunca "
            "se asisten: los clics sobre ellos van directos a "
            "Windows, en ambos modos. Se muestran como cuadros de "
            "color a la derecha - elija un color abajo y pulse "
            "«Añadir a colores rechazados» para agregar uno (quince "
            "como mucho); haga clic en un cuadro para eliminarlo. "
            "Una lista vacía muestra un cuadro tachado y desactiva "
            "el ajuste.",
        "desc.follow_boost": "Con qué fuerza gana el elemento "
            "recordado: 100% puede doblar su puntuación mientras "
            "está fresco, 25% es un empujón leve.",
        "desc.follow_enabled": "Tras un enganche correcto, los "
            "elementos parecidos o en el mismo sitio ganan durante "
            "un rato - útil para barras de desplazamiento y clics "
            "repetidos sobre un control.",
        "desc.follow_learn": "Solo elementos de mi color: un clic "
            "fallado no puede reorientar el recuerdo. Cada enganche "
            "correcto: el comportamiento antiguo y confiado.",
        "desc.follow_seconds": "Segundos que el elemento recordado "
            "sigue preferido tras su último enganche correcto "
            "(1-120).",
        "desc.glide_ms": "0 (predeterminado) salta al instante - lo "
            "más rápido. 40-120 desliza para que lo vea; mover el "
            "ratón usted mismo cancela el desliz.",
        "desc.hold_follow": "Mientras mantiene pulsado el botón "
            "izquierdo justo tras un enganche - o pulsa de nuevo "
            "sobre el elemento recordado - el cursor permanece en el "
            "color de ese elemento; esto estabiliza arrastres como "
            "los manijas de barras de desplazamiento. Las "
            "pulsaciones en otro sitio no se tocan.",
        "desc.key_launch": "Formato: ctrl+l, f5, space, ctrl+alt+1 "
            "... Modificadores: ctrl, alt, shift, win. Se aplica al "
            "pulsar Aplicar.",
        "desc.key_mode1": "Separado por comas, p. ej. '1, f1, "
            "ctrl+f1, v'. Qué hace el modo clásico lo explica la "
            "pestaña Atajos.",
        "desc.key_mode2": "Separado por comas, p. ej. '2, f2, "
            "ctrl+f2, b'. Qué hace el modo guía lo explica la "
            "pestaña Atajos.",
        "desc.key_pause": "El ratón y el teclado vuelven a ser suyos "
            "por completo hasta que inicie.",
        "desc.key_play": "Reproduce la grabación elegida en la lista "
            "de Macros, o la más reciente si no hay ninguna elegida. "
            "Sobre una grabación que repite, la detiene.",
        "desc.key_play_n": "Reproduce la grabación #%d de la lista "
            "numerada de la pestaña Macros, por su posición. Si la "
            "lista es más corta, no ocurre nada.",
        "desc.key_record": "Captura todo lo que hace - cada tecla, "
            "cada clic de ratón y cada movimiento del cursor - "
            "mientras su entrada sigue llegando a sus programas, "
            "hasta que el atajo de parar la guarda en la lista de "
            "Macros. Solo armado mientras está iniciado.",
        "desc.key_record_stop": "Detiene la captura, guarda la "
            "secuencia en la lista de Macros y para una reproducción "
            "en curso.",
        "desc.luminance_norm": "Los bordes se puntúan contra el "
            "brillo de su entorno, así los temas oscuros rinden como "
            "los claros. Recomendado activado.",
        "desc.macro_action": "La combinación pulsada por usted en "
            "cada pulsación del disparo (una pulsación = una "
            "combinación): 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' "
            "... Vacío = macro apagado.",
        "desc.macro_key": "La tecla que SIGNIFICA el macro en vez de "
            "escribir: 'b', 'f7', 'ctrl+b' ... Iniciado, una "
            "pulsación envía la combinación de al lado exactamente "
            "una vez y la tecla no llega a sus programas. En pausa, "
            "escribe normal. Vacío = macro apagado.",
        "desc.max_area": "Las manchas mayores se ignoran - suelen "
            "ser ventanas enteras o fondo, no elementos clicables.",
        "desc.max_dim": "Los elementos más anchos o altos que esto "
            "se ignoran; los que tocan un borde de pantalla, como "
            "las barras de desplazamiento, reciben el doble.",
        "desc.merge_distance": "Las piezas más cercanas que esto (un "
            "contorno roto, un icono junto a su rótulo) se vuelven "
            "un elemento. Dos elementos completos nunca se pegan.",
        "desc.min_area": "Las manchas menores se ignoran como "
            "motitas, salvo que se peguen a un elemento mayor.",
        "desc.min_contrast": "Un elemento debe ser al menos así de "
            "nítido para poder clicarse. Los valores bajo 28 valen "
            "como 28: un umbral de calidad interno impide que el "
            "ruido sea clicable.",
        "desc.motion_3d": "Sigue los elementos móviles con posición "
            "Y tamaño en vez de un ajuste recto: los análisis malos "
            "aislados se ignoran en vez de cegar al seguidor, las "
            "curvas se siguen, y un salto brusco de tamaño reinicia "
            "la pista (el escáner cogió otro elemento). Mismos "
            "límites de velocidad, mismo tope de 80 px - solo "
            "cerebros nuevos. Funciona por sí solo.",
        "desc.motion_lead_ms": "Milisegundos de recorrido con los "
            "que anticipar un elemento móvil (0-300): 40-80 para "
            "rodar lento, 100-150 para barras rápidas. Tope de 80 "
            "px, desactivado con movimiento lento o que gira.",
        "desc.motion_predict": "Para elementos que se mueven "
            "mientras clica (listas que ruedan, barras de vídeo), "
            "apunta un poco por delante para que el clic caiga en el "
            "elemento. Los quietos no cambian.",
        "desc.mouse2_action": "Qué hace ADEMÁS un clic derecho corto "
            "- el clic derecho en sí siempre conserva su función "
            "normal de Windows. Predeterminado: nada.",
        "desc.mouse2_hold_action": "Las mismas opciones, disparadas "
            "al MANTENER el botón derecho medio segundo en vez de "
            "clicarlo. Una pulsación es clic o mantenimiento, nunca "
            "ambos. Predeterminado: nada.",
        "desc.on_target_dist": "Si su clic cae dentro de estos "
            "píxeles del centro del elemento, nada se mueve - ya "
            "acertó.",
        "desc.radius": "Distancia de búsqueda en píxeles (40-400). "
            "Súbala si el elemento que quiere queda justo fuera de "
            "alcance; bájela si gana el vecino equivocado.",
        "desc.rapid_click_snap": "No (predeterminado): mientras un "
            "clic se procesa, los demás van a Windows. Sí: se asiste "
            "cada clic izquierdo.",
        "desc.snap_offset_x": "Desplaza el punto de clic "
            "lateralmente desde el centro del elemento (-200 a 200, "
            "negativo a la izquierda). Para un control cuyo centro "
            "está muerto - botón dividido, barra deslizante - gire "
            "el clic al punto vivo una vez en vez de pelear cada "
            "snap.",
        "desc.snap_offset_y": "Desplaza el punto de clic "
            "verticalmente desde el centro del elemento (-200 a 200, "
            "negativo hacia arriba). Como el desplazamiento lateral: "
            "caiga en la parte viva del control.",
        "desc.stall_pause_seconds": "Si un escaneo se atasca, la "
            "asistencia pausa este tiempo y cualquier clic mantenido "
            "se le devuelve.",
        "desc.watcher_seconds": "En modo clásico, un segundo "
            "enganche cerca del mismo sitio dentro de este tiempo se "
            "vuelve un doble clic sobre el elemento.",
        "ent.cancel_line": "activa hasta %s - NO se renovará",
        "ent.canceled_line": "suscripción terminada%s",
        "ent.expired_line": "caducó el %s - renueve en Stripe",
        "ent.past_due_line": "pago fallido - arregle la tarjeta en "
            "el correo-recibo de Stripe; el acceso vuelve cuando la "
            "factura se paga",
        "ent.plan": " (%s)",
        "ent.refunded_line": "reembolsada / repercutida - activación "
            "revocada",
        "ent.st.active": "activa",
        "ent.st.canceled": "terminada",
        "ent.st.canceling": "activa pero cancelándose",
        "ent.st.grant": "concesión de soporte",
        "ent.st.past_due": "PAGO FALLIDO",
        "ent.st.refunded": "reembolsada / repercutida",
        "ent.st.trial": "prueba",
        "ent.st.unsubscribed": "sin suscripción",
        "ent.until": " hasta %s",
        "err.auth_unreachable": "El servidor de autenticación de "
            "Snappy AI no es accesible:\n%s\n\nSnappy AI solo "
            "funciona con una respuesta viva de él.\n¿Reintentar?",
        "err.start_fail": "Snappy AI no pudo arrancar.\nEjecute con "
            "--console para ver los detalles.",
        "gate.btn.monthly": "Suscripción mensual por 9,99€",
        "gate.btn.trial": "Compra de prueba por 1,99€",
        "gate.head.canceled": "Esta suscripción se canceló - cree "
            "una nueva en Stripe para continuar.",
        "gate.head.canceling": "Su suscripción está marcada para "
            "cancelar - sigue activa hasta %s; después este acceso "
            "se bloquea de nuevo salvo que renueve.",
        "gate.head.email_mismatch": "El pago se hizo con un correo "
            "distinto del de su cuenta de Discord. Las suscripciones "
            "solo funcionan con el correo de Discord mostrado abajo "
            "- suscríbase con él o contacte al soporte.",
        "gate.head.expired": "La suscripción de este acceso caducó - "
            "renuévela en Stripe para continuar.",
        "gate.head.none": "Ha entrado, pero este acceso no tiene "
            "suscripción activa. Pague con ESTE correo de Discord - "
            "una compra con otra dirección no puede activarlo.",
        "gate.head.past_due": "El último pago de la suscripción "
            "falló - arréglelo en Stripe para reactivar este acceso.",
        "gate.head.refunded": "Esta compra se reembolsó o se "
            "repercutió en contra, así que la activación se revocó. "
            "Una suscripción nueva con este correo de Discord la "
            "reactiva.",
        "gate.head.shared": "Esta cuenta se usa AHORA en OTRO "
            "ordenador. Snappy AI sigue apagado mientras la misma "
            "cuenta de Discord corre en dos sitios a la vez - cierre "
            "la otra sesión y compruebe de nuevo. Compartir "
            "suscripciones encarece el precio; por favor, no lo "
            "haga.",
        "gate.msg.active": "Suscripción activa - arrancando Snappy "
            "AI...",
        "gate.msg.checking": "Comprobando con el servidor...",
        "gate.msg.no_link": "Ese enlace de pago no está configurado "
            "en esta compilación.",
        "gate.msg.open_fail": "No se pudo abrir un navegador. Abra "
            "este enlace a mano:\n%s",
        "gate.msg.open_ok": "Stripe está abierto en su navegador: pague allí. Esta ventana detecta el pago por sí sola e inicia el motor.",
        "gate.msg.session_gone": "La sesión se perdió - entre de "
            "nuevo.",
        "gate.msg.still_none": "Sigue sin suscripción activa para "
            "este acceso.",
        "gate.msg.still_shared": "Sigue en uso en otro ordenador - "
            "cierre esa sesión y compruebe de nuevo.",
        "gate.msg.unreachable": "Servidor de autenticación "
            "inaccesible: %s",
        "gate.note": "El motor arranca en cuanto la suscripción está "
            "activa - esta ventana se comprueba sola cada 30 "
            "segundos. Cerrarla vuelve al acceso.",
        "gate.prices": "Prueba de 2 días: 1,99€ (una vez)  -  "
            "suscripción: 9,99€ / mes.\nLa activación llega hasta "
            "~10 minutos tras el pago; las renovaciones reactivan "
            "este mismo acceso automáticamente.",
        "gate.title": "%s - Suscripción%s",
        "hdr.build": "compilación %s",
        "help.1.b": "Snappy AI mira la pantalla alrededor de su "
            "cursor, encuentra las cosas sólidas con forma de "
            "elemento que hay cerca - botones, iconos, enlaces - y "
            "elige la mejor: ganan bordes nítidos, tamaño decente y "
            "cercanía al cursor. Su color, la lista de jamás "
            "clicables y el recuerdo de su último clic pueden "
            "inclinar la elección. El cursor apunta luego al centro "
            "del elemento, no a la esquina de su caja.",
        "help.1.t": "Qué pasa cuando clica",
        "help.10.b": "1. ¿Está iniciado? En pausa nada se intercepta "
            "- «Atajo: iniciar asistencia» (Ctrl+L por omisión) es "
            "el único encendido/apagado.  2. Mantenga Shift un clic "
            "para confirmar que el problema era la asistencia.  3. "
            "Gana el elemento equivocado: baje «Distancia de "
            "búsqueda desde el cursor», luego fije «Mi color» o suba "
            "«Fuerza de la ventaja de color».  4. No se encuentra "
            "nada: baje «Qué tan tenue puede ser un borde» y "
            "«Nitidez mínima del borde», suba «Ancho o alto máximo» "
            "o «Pegar piezas cercanas».  5. Algo no debe asistirse "
            "nunca: ponga su color en color en «Color(es) jamás "
            "clicables».  6. Sigue mal: informe al soporte qué clicó "
            "y qué esperaba, y adjunte el archivo de registro que "
            "Snappy AI escribe en su carpeta de datos.",
        "help.10.t": "Si algo va mal, compruebe en este orden",
        "help.2.b": "El modo guía (predeterminado) no se come ningún "
            "clic: su clic llega al programa y, al soltar, el cursor "
            "se mueve al elemento despejado más cercano. El modo "
            "clásico es más fuerte: un clic fallado cerca de un "
            "elemento se captura, el cursor se engancha y Snappy AI "
            "clica por usted. «Distancia de búsqueda desde el "
            "cursor» fija el círculo de búsqueda - súbala si el "
            "elemento que quiere queda justo fuera de alcance, "
            "bájela si gana el vecino equivocado. Mantener Shift "
            "evita un clic en ambos modos.",
        "help.2.t": "Empiece aquí: modo y distancia de búsqueda",
        "help.3.b": "En la pestaña Procesado, «Qué tan tenue puede "
            "ser un borde» y «Nitidez mínima del borde» deciden qué "
            "bordes cuentan: más bajos encuentran tenues, más altos "
            "ignoran ruido. «Tamaño mínimo de elemento», «Área "
            "máxima de elemento» y «Ancho o alto máximo» descartan "
            "motitas y ventanas enteras. «Pegar piezas cercanas» une "
            "un contorno roto, o un icono junto a su rótulo, en un "
            "elemento. En la pestaña Asistencia, «Ajuste automático "
            "para pantallas tenues» y «Juzgar bordes por brillo "
            "relativo» hacen que los temas oscuros se porten como "
            "los claros - déjelos activados.",
        "help.3.t": "No se encuentra nada - o se encuentra de más",
        "help.4.b": "En la pestaña Colores, «Mi color» es el color "
            "que Snappy AI prefiere y «Color(es) jamás clicables» es "
            "absoluto: esos elementos nunca se asisten. «Asistir "
            "solo mi color» restringe la asistencia a elementos que "
            "coinciden. En Procesado, «Rigor de coincidencia de "
            "color» dice cuán cerca debe estar un tono, «Aceptar "
            "tonos parecidos» deja contar en parte a versiones más "
            "claras o lavadas, y «Fuerza de la ventaja de color» "
            "dice cuánto eleva su color a un elemento - súbala si "
            "aún gana el equivocado.",
        "help.4.t": "Trabajar con colores",
        "help.5.b": "«Recordar el último elemento clicado» sigue "
            "prefiriendo el elemento donde cayó su último clic "
            "correcto, durante «Cuánto tiempo recordar» segundos - "
            "esto vuelve agradables las barras de desplazamiento y "
            "los botones de diálogo. «Fuerza del recuerdo» dice con "
            "cuánta fuerza gana, y «Qué puede aprender el recuerdo» "
            "lo protege: con «Solo elementos de mi color», un clic "
            "fallado no puede reorientarlo. «Seguir el elemento con "
            "el botón mantenido» estabiliza arrastres, y las "
            "acciones del botón derecho en Experimental pueden "
            "seguir o despejar el recuerdo con el ratón.",
        "help.5.t": "Clics repetidos sobre un control",
        "help.6.b": "«Anticipar elementos en movimiento» mide cuán "
            "rápido viaja el elemento elegido y apunta por delante "
            "«Cuánto anticipar el blanco» milisegundos, para que el "
            "clic caiga sobre una lista que rueda o una barra de "
            "vídeo en vez de detrás. La anticipación tiene tope de "
            "80 píxeles y se apaga sola con elementos quietos o que "
            "giran.",
        "help.6.t": "Clicar cosas que se mueven",
        "help.7.b": "«Animar el movimiento del cursor» = 0 salta al "
            "instante; 40-120 desliza para que lo vea, y mover el "
            "ratón usted mismo cancela el desliz. «Ventana de doble "
            "clic» convierte en modo clásico un segundo enganche "
            "cerca del mismo sitio en un doble clic. «Asistir cada "
            "clic de una ráfaga rápida» asiste cada clic de una "
            "serie en vez de solo el primero. «Pausa tras un atasco» "
            "es la válvula que devuelve un clic mantenido si un "
            "escaneo se atasca.",
        "help.7.t": "Cómo se sienten los clics",
        "help.8.b": "La pestaña Atajos explica los dos modos y el "
            "flujo de grabación. En resumen: los atajos con Ctrl, "
            "Alt, Shift o Win están reservados en todo el sistema; "
            "las teclas solas se disparan en todas partes y siguen "
            "escribiendo. Un macro convierte una pulsación bloqueada "
            "en una combinación entera. Las grabaciones capturan su "
            "entrada real - cada tecla, clic de ratón y movimiento "
            "del cursor - y la reproducen desde la pestaña Macros, "
            "cada una con su propio interruptor de una vez o repetir "
            "hasta detener.",
        "help.8.t": "Teclas, macros y grabaciones",
        "help.9.b": "El botón Idioma junto a «Exportar "
            "configuración» - también en las ventanas de acceso y de "
            "suscripción - cambia toda la interfaz al momento, sin "
            "reiniciar, y recuerda su elección. Los idiomas aún en "
            "traducción no se ofrecen, así que cualquiera que pueda "
            "elegir está completo.",
        "help.9.t": "Idioma",
        "help.sub": "Cada ajuste con el nombre que ve en su pestaña, "
            "en el orden en que lo querrá. Pase el cursor sobre un "
            "nombre para ver su descripción de una línea; esta "
            "página es la forma larga.",
        "help.tail": "Los ajustes se aplican al pulsar Aplicar. Un "
            "config.ini junto al programa sustituye a config.json. "
            "Esta página explica; no configura.",
        "help.title": "Ajustar Snappy AI con palabras sencillas",
        "kb.keys.b": "Un atajo con Ctrl, Alt, Shift o Win queda "
            "reservado en todo el sistema: solo lo ve Snappy AI. Una "
            "tecla sola (como 1 o 2) funciona en cada programa Y "
            "sigue escribiendo - el precio es que pulsarla en mitad "
            "de una frase también dispara su acción. Si prefiere el "
            "comportamiento clásico, active «Los atajos de una tecla "
            "tragan la tecla» en la pestaña Asistencia. Los macros "
            "van más allá: iniciado, la tecla disparo se traga y la "
            "combinación de al lado se envía exactamente una vez.",
        "kb.keys.t": "Teclas solas frente a combinaciones",
        "kb.mode.b": "Modo guía (predeterminado, atajo 2): su clic "
            "siempre llega intacto al programa; al soltar el botón, "
            "el cursor se mueve al elemento despejado más cercano, "
            "así su próximo clic arranca desde ahí. Nada se traga "
            "jamás - el modo más seguro.  Modo clásico (atajo 1): si "
            "clica cerca de un elemento, ese clic fallado se "
            "captura, el cursor se engancha al elemento y Snappy AI "
            "clica por usted; si no hay nada cerca, su clic se "
            "devuelve intacto.  En ambos modos, mantener Shift al "
            "clicar evita la asistencia para ese clic.",
        "kb.mode.t": "Qué hacen los dos modos",
        "kb.rec.b": "Mientras está iniciado, pulse su atajo de "
            "inicio de grabación (Ctrl+Alt+R por defecto): cada "
            "tecla que pulsa, cada botón del ratón que pulsa y cada "
            "movimiento del cursor se captura Y sigue llegando a sus "
            "programas, así que puede trabajar con normalidad "
            "mientras graba. Pulse el atajo de parada (Ctrl+Alt+S) "
            "para guardarla en la lista de la pestaña Macros - caben "
            "cinco grabaciones. Haga clic en una grabación para "
            "elegirla, usar «Renombrar» o «Exportar» y ajustar su "
            "propio interruptor «Repetir hasta detener». El atajo de "
            "reproducción (Ctrl+Alt+M) reproduce la grabación "
            "elegida allí; Ctrl+1 a Ctrl+5 reproducen por posición "
            "en la lista. En pausa, nada se graba y nada se inyecta "
            "- su entrada es enteramente suya.",
        "kb.rec.t": "Cómo grabar y reproducir sus propias "
            "pulsaciones y movimientos",
        "lang.close": "Cerrar",
        "lang.coverage": "%d %% traducido",
        "lang.current": "Actual: %s",
        "lang.progress": "Aún en traducción, se ofrecerá al "
            "completarse: %s",
        "lang.prompt": "El cambio se aplica al momento; la ventana "
            "sigue abierta para probar varios.",
        "lang.title": "Idioma",
        "lbl.accent_boost": "Fuerza de la ventaja de color",
        "lbl.accent_coherent": "Ignorar motas de color dispersas",
        "lbl.accent_color": "Mi color (colores)",
        "lbl.accent_matcher": "Motor de coincidencia de color",
        "lbl.accent_only": "Asistir solo mi color",
        "lbl.accent_soft": "Aceptar tonos parecidos",
        "lbl.accent_tolerance": "Rigor de coincidencia de color",
        "lbl.accent_variants": "Estados claros y oscuros de mi color",
        "lbl.adaptive_threshold": "Ajuste automático para pantallas "
            "tenues",
        "lbl.auto_click": "Clicar elementos él solo",
        "lbl.auto_click_interval": "Segundos entre clics automáticos",
        "lbl.auto_click_max_clicks": "Límite de clics automáticos "
            "por sesión",
        "lbl.auto_click_min_contrast": "Cuán nítido debe ser un "
            "destino automático",
        "lbl.auto_click_radius": "Buscar alrededor del centro",
        "lbl.auto_click_repeat_px": "No volver a pulsar el mismo "
            "sitio",
        "lbl.auto_click_settle_ms": "Pausa antes del clic automático",
        "lbl.block_bound_keys": "Los atajos de una tecla tragan la "
            "tecla",
        "lbl.capture_backend": "Motor de captura de pantalla",
        "lbl.color_adapt": "Adaptarse a la luz de la pantalla",
        "lbl.contrast_threshold": "Qué tan tenue puede ser un borde",
        "lbl.exclude_color": "Color(es) jamás clicables",
        "lbl.follow_boost": "Fuerza del recuerdo",
        "lbl.follow_enabled": "Recordar el último elemento clicado",
        "lbl.follow_learn": "Qué puede aprender el recuerdo",
        "lbl.follow_seconds": "Cuánto tiempo recordar",
        "lbl.glide_ms": "Animar el movimiento del cursor",
        "lbl.hold_follow": "Seguir el elemento con el botón "
            "mantenido",
        "lbl.key_launch": "Atajo: iniciar asistencia",
        "lbl.key_mode1": "Atajo: modo clásico (hasta 4 teclas)",
        "lbl.key_mode2": "Atajo: modo guía (hasta 4 teclas)",
        "lbl.key_pause": "Atajo: pausa",
        "lbl.key_play": "Atajo: reproducir la grabación elegida",
        "lbl.key_play_n": "Atajo: reproducir grabación #%d",
        "lbl.key_record": "Atajo: iniciar grabación",
        "lbl.key_record_stop": "Atajo: detener y guardar grabación",
        "lbl.luminance_norm": "Juzgar bordes por brillo relativo",
        "lbl.macro_action": "Macro %d: envía en su lugar",
        "lbl.macro_key": "Macro %d: pulse esta tecla",
        "lbl.max_area": "Área máxima de elemento",
        "lbl.max_dim": "Ancho o alto máximo de elemento",
        "lbl.merge_distance": "Pegar piezas cercanas",
        "lbl.min_area": "Tamaño mínimo de elemento",
        "lbl.min_contrast": "Nitidez mínima del borde",
        "lbl.motion_3d": "Seguimiento más inteligente en movimiento",
        "lbl.motion_lead_ms": "Cuánto anticipar el blanco",
        "lbl.motion_predict": "Anticipar elementos en movimiento",
        "lbl.watch_center_only": "Vigilar solo el centro de la pantalla",
        "desc.watch_center_only": "La ayuda solo observa un cuadrado fijo en el centro de la pantalla "
            "(tamaño = distancia de búsqueda, 150×150 px por defecto), sin "
            "importar dónde esté el cursor. Los clics fuera de ese cuadrado no "
            "se modifican.",
        "lbl.center_follow": "La pantalla sigue al objetivo",
        "desc.center_follow": "Con «Vigilar solo el centro de la pantalla» activado: tras "
            "enganchar un elemento, la ayuda mueve la pantalla para mantenerlo "
            "en el centro, especialmente en planos que se desplazan. Mueve tú "
            "la pantalla para soltar el seguimiento.",
        "lbl.input_backend": "Método de entrada",
        "desc.input_backend": "Inyección de Windows (predeterminado) funciona en todas partes. "
            "Interception envía a través del controlador y los juegos lo "
            "reconocen como ratón real; requiere el controlador instalado y "
            "interception.dll junto al programa; si falta, usa la inyección de "
            "Windows automáticamente.",
        "val.input_backend.win32": "Inyección de Windows",
        "val.input_backend.interception": "Interception (controlador)",
        "lbl.mouse2_action": "Acción extra del clic derecho",
        "lbl.mouse2_hold_action": "Acción extra de mantener el "
            "derecho",
        "lbl.on_target_dist": "Distancia de «ya acertado»",
        "lbl.radius": "Distancia de búsqueda desde el cursor",
        "lbl.rapid_click_snap": "Asistir cada clic de una ráfaga "
            "rápida",
        "lbl.snap_offset_x": "Punto de clic: desplazar a izquierda / "
            "derecha",
        "lbl.snap_offset_y": "Punto de clic: desplazar arriba / "
            "abajo",
        "lbl.stall_pause_seconds": "Pausa tras un atasco",
        "lbl.watcher_seconds": "Ventana de doble clic",
        "login.failed": "El acceso con %s no se completó - inténtelo "
            "de nuevo.",
        "login.no_provider": "Esta copia no trae proveedor de "
            "acceso.",
        "login.not_configured": "El archivo de suscripción aún no "
            "está configurado en esta compilación.",
        "login.note": "El acceso abre su navegador y vuelve solo a "
            "esta ventana.",
        "login.provider": "Entrar con %s",
        "login.signedin": "Sesión iniciada como %s.",
        "login.sub": "Entre con Discord - su suscripción queda "
            "ligada a esta cuenta, y los pagos deben usar su correo. "
            "Aquí no hay contraseña.",
        "login.title": "%s - Iniciar sesión",
        "login.unreachable": "Servidor de autenticación inaccesible: "
            "%s",
        "login.waiting": "Esperando al navegador - termine el acceso "
            "con %s...",
        "mac.delete": "Eliminar",
        "mac.empty": "Aún no hay grabaciones - inicie, pulse su "
            "atajo de grabar y trabaje con normalidad: se captura "
            "cada tecla, clic y movimiento del cursor.",
        "mac.export": "Exportar",
        "mac.import": "Importar",
        "mac.keys_head": "Macros de teclas",
        "mac.loop": "Repetir hasta detener",
        "mac.recordings": "Grabaciones",
        "mac.rename": "Renombrar",
        "mac.row": "Macro %d",
        "mac.sends": "envía",
        "mac.steps": "%d pasos",
        "note.advanced": "Ajustes de distancia y tiempo que cambian "
            "cómo se sienten los clics, no qué se encuentra. La "
            "mayoría nunca necesita tocarlos; los valores "
            "predeterminados son los probados.",
        "note.assist": "Cada interruptor que cambia el "
            "comportamiento mientras está iniciado. Los dos modos se "
            "cambian con sus teclas de modo - la pestaña Atajos "
            "explica qué hace cada uno. La asistencia siempre "
            "arranca en pausa; Iniciar es el único "
            "encendido/apagado. Dónde mira el motor y cómo se "
            "sienten los clics vive en Avanzado; qué cuenta como "
            "elemento, en Procesado.",
        "note.colors": "Las dos listas de arriba eligen qué colores "
            "prefiere o rechaza Snappy AI. Cada una muestra sus "
            "colores como cuadros a la derecha, quince como mucho, y "
            "hacer clic en un cuadro elimina ese color de nuevo; una "
            "lista vacía muestra un cuadro tachado y cuenta como "
            "apagada. «Añadir a colores preferidos» y «Añadir a "
            "colores rechazados» ponen el color que está en el "
            "mezclador en la lista correspondiente. Valor RGB actual "
            "muestra tres cuadros - cada uno tan ancho como cinco "
            "cuadros de color, así que la fila abarca las mismas "
            "quince casillas que todo lo de abajo - que brillan con "
            "cuánto rojo, verde y azul tiene el color del mezclador; "
            "la fila sigue al mezclador y no se puede escribir. El "
            "mezclador de abajo mezcla un color como un programa de "
            "pintura; todo lo que está a su lado se coloca en el "
            "lado derecho de la ventana, con el mismo hueco hasta el "
            "borde que los ajustes de arriba, y cada fila abarca el "
            "mismo ancho de quince cuadros: el escaparate alto con "
            "su #valor dibujado dentro, luego los quince tonos "
            "hechos, los dos botones de añadir y la fila de pantalla "
            "- «Tomar color de la pantalla» coge el único color bajo "
            "el cursor, «Sugerir colores en pantalla» llena quince "
            "cuadros propios con colores que encuentra alrededor del "
            "cursor, y hacer clic en uno lo carga en el mezclador. "
            "El escaparate es alto a propósito: así los cuadros "
            "sugeridos terminan exactamente a la altura del "
            "deslizador de color de la izquierda.",
        "note.experimental": "Elecciones de motor, cada una con un "
            "valor probado. Cámbielas solo para comparar motores, en "
            "hardware inusual o si el soporte lo pide - el motor de "
            "captura se aplica al reiniciar.",
        "note.handler": "Qué cuenta como elemento clicable: qué tan "
            "tenue puede ser un borde, qué tan nítido debe ser y qué "
            "tamaño puede tener. ¿No encuentra nada? Afloje estos "
            "valores. ¿Encuentra lo que no es? Apriételos, o use su "
            "color en la pestaña Colores.",
        "note.keybindings": "Cada atajo - y debajo, qué hacen los "
            "dos modos, cómo grabar sus propias pulsaciones y "
            "movimientos de ratón y en qué se distingue una tecla "
            "sola de una combinación.",
        "note.macros": "Un macro convierte una pulsación en una "
            "combinación entera mientras está iniciado. Junto a los "
            "macros, sus grabaciones: hasta cinco capturas con "
            "nombre de todo lo que hizo - cada tecla, clic de ratón "
            "y movimiento del cursor - que se reproducen exactamente "
            "como se grabaron. Haga clic en una grabación para "
            "elegirla; cada fila lleva su propio interruptor "
            "«Repetir hasta detener», y «Renombrar», «Exportar», "
            "«Importar» y «Eliminar» están en la parte inferior de "
            "la caja.",
        "note.macros_keys": "Los atajos de grabar/reproducir están "
            "en la pestaña Atajos (predeterminados: Ctrl+Alt+R "
            "grabar, Ctrl+Alt+S detener y guardar, Ctrl+Alt+M "
            "reproducir, Ctrl+1..5 reproducir por posición).",
        "online.cancelled": "La autenticación con Discord se canceló "
            "(o falló). Inténtelo de nuevo.",
        "rec.export_fail": "Falló la exportación: %r",
        "rec.exported": "Exportado a %s",
        "rec.import_fail": "Falló la importación: %r",
        "rec.imported": "%d grabación(es) importada(s)%s.",
        "rec.imported_none": " (ninguna era válida)",
        "rec.no_sel": "Nada elegido para exportar.",
        "rec.notfile": "Falló la importación: no es un archivo de "
            "grabación.",
        "shared.back": "Bienvenido de nuevo - pulse Iniciar cuando "
            "esté listo.",
        "shared.body": "Esta cuenta de Discord ejecuta Snappy AI en "
            "otro ordenador ahora mismo.\nLa asistencia queda en "
            "pausa aquí hasta que quede una sola sesión.\n\nUna "
            "suscripción, una máquina a la vez - eso mantiene\nel "
            "precio bajo y el desarrollo en marcha.",
        "shared.close": "Cerrar",
        "shared.recheck": "Comprobar ahora",
        "shared.still": "Sigue en uso en otro sitio - permanecemos "
            "en pausa.",
        "shared.title": "Cuenta en uso en otro sitio",
        "shared.unreachable": "Servidor inaccesible - se "
            "recomprobará.",
        "st.all_files": "Todos los archivos",
        "st.color_added": "Añadido rgb(%d, %d, %d) a %s - Aplicar "
            "guarda.",
        "st.color_already": "rgb(%d, %d, %d) ya está en %s.",
        "st.color_full": "%s ya tiene 15 colores - haga clic primero "
            "en uno de sus cuadros para eliminar un color.",
        "st.color_removed": "Eliminado rgb(%d, %d, %d) de %s - "
            "Aplicar guarda.",
        "st.delete_confirm": "¿Eliminar la grabación %r?\nEsto no "
            "puede deshacerse.",
        "st.deleted": "Grabación eliminada.",
        "st.engine_dead": "Hilo del motor no disponible - los atajos "
            "no responden.",
        "st.ent_paused": "Suscripción %s - asistencia en pausa. "
            "Renueve en Stripe y reinicie.",
        "st.ent_unreachable": "Recomprobación de suscripción: "
            "servidor inaccesible (la sesión sigue).",
        "st.export_fail": "Falló la exportación: %r",
        "st.export_rec_title": "Exportar grabación",
        "st.export_title": "Exportar configuración",
        "st.exported": "Configuración exportada a %s",
        "st.file_rec": "Grabación de Snappy AI",
        "st.file_settings": "Configuración de Snappy AI",
        "st.follow": "  |  seguimiento hace %d s",
        "st.import_fail": "Falló la importación: %r",
        "st.import_notfile": "Falló la importación: no es un archivo "
            "de configuración.",
        "st.import_rec_title": "Importar grabación(es)",
        "st.import_title": "Importar configuración",
        "st.imported": "%d ajuste(s) importado(s)%s.",
        "st.imported_ignored": ", ignorados: %s",
        "st.ini_over": "Aplicado, pero config.ini sustituye: %s",
        "st.lib_empty": "La lista está vacía - nada que exportar.",
        "st.line": "Asistidos %d  |  dejados pasar %d%s  |  tema: %s",
        "st.loop_desc": "Estilo de reproducción de ESTA grabación: "
            "apagado = se reproduce una vez; encendido = repite "
            "hasta que vuelva a pulsar el atajo de reproducir. Cada "
            "grabación tiene su propio interruptor, guardado con la "
            "grabación misma.",
        "st.name_empty": "El nombre no puede estar vacío.",
        "st.pick_err": "Falló la captura: %r",
        "st.pick_fail": "Falló la captura - inténtelo de nuevo.",
        "st.pick_ok": "Tomado rgb(%d, %d, %d) en (%d, %d).",
        "st.pick_wait": "Lleve el cursor al color - captura en 3 "
            "s...",
        "st.preset_desc": "Muestra hecha: %s - clique para cargarla "
            "en el mezclador.",
        "st.rec_count": "%d de 5 grabaciones",
        "st.rec_now": "%r ahora: %s.",
        "st.rec_once": "se reproduce una vez",
        "st.rec_playing": "Reproduciendo %r...",
        "st.rec_playing_loop": "Reproduciendo %r hasta detener",
        "st.rec_recording": "GRABANDO - %s detiene y guarda",
        "st.rec_repeats": "repite hasta detener",
        "st.registered": "Registrado en: %s    Estado: %s",
        "st.rename_prompt": "Nombre nuevo para la grabación #%d:",
        "st.renamed": "Grabación renombrada.",
        "st.reset_confirm": "¿Restablecer todos los ajustes a sus "
            "valores?\nLas cuentas se conservan; solo afecta a los "
            "ajustes.",
        "st.rgb_bad": "Introduzca antes valores R/G/B válidos.",
        "st.running": "Activo..",
        "st.saved": "Guardado y aplicado.",
        "st.defaults_restored": "Se restauraron los valores predeterminados.",
        "st.saved_bad": "Guardado, pero no válido (se mantiene lo "
            "antiguo): %s",
        "st.select_rec": "Elija antes una grabación.",
        "st.shared_paused": "CUENTA EN USO EN OTRO SITIO - "
            "asistencia en pausa; una suscripción = una máquina.",
        "st.standby": "En espera..",
        "st.sug_fail": "Falló la sugerencia: %r",
        "st.sug_loaded": "La sugerencia rgb(%d, %d, %d) está en el "
            "mezclador - añádala a una lista con los botones de "
            "arriba.",
        "st.sug_loaded_desc": "Color de interfaz sugerido rgb(%d, "
            "%d, %d) - %d%% de la región muestreada. Clique para "
            "cargarlo en el mezclador.",
        "st.sug_none": "Sin sugerencias de color de esta región.",
        "st.sug_ok": "%d sugerencias - haga clic en una para "
            "cargarla en el mezclador.",
        "st.sug_wait": "Apunte a la app en la que trabaja - muestreo "
            "en 3 s...",
        "tab.advanced": "Avanzado",
        "tab.assist": "Asistencia",
        "tab.colors": "Colores",
        "tab.experimental": "Experimental",
        "tab.handler": "Procesado",
        "tab.help": "Ayuda",
        "tab.hotkeys": "Atajos",
        "tab.macros": "Macros",
        "theme.dark": "Oscuro",
        "theme.light": "Claro",
        "val.accent_matcher.hsv": "Clásico - el motor antiguo",
        "val.accent_matcher.oklab": "Perceptual - como se ven los "
            "colores (recomendado)",
        "val.capture_backend.auto": "Automático - el más rápido con "
            "respaldo seguro",
        "val.capture_backend.dxcam": "Desktop Duplication - el más "
            "rápido en la mayoría de PC",
        "val.capture_backend.mss": "Compatible - funciona siempre "
            "(Remote Desktop, MV)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "experimental",
        "val.follow_learn.accent": "Solo elementos de mi color",
        "val.follow_learn.any": "Cada enganche correcto",
        "val.mouse2_action.1": "Borrar la tarea de seguimiento "
            "actual",
        "val.mouse2_action.2": "Seguir el último color enganchado",
        "val.mouse2_action.3": "Tomar el color bajo el cursor y "
            "seguirlo",
        "val.mouse2_action.4": "No hacer nada",
        "val.mouse2_hold_action.1": "Borrar la tarea de seguimiento "
            "actual",
        "val.mouse2_hold_action.2": "Seguir el último color "
            "enganchado",
        "val.mouse2_hold_action.3": "Tomar el color bajo el cursor y "
            "seguirlo",
        "val.mouse2_hold_action.4": "No hacer nada",
        "word.off": "No",
        "word.on": "Sí",
    },
    "fr": {
        "btn.apply": "Appliquer",
        "btn.export": "Exporter la configuration",
        "btn.import": "Importer la configuration",
        "btn.language": "Langue : %s",
        "btn.launch": "Démarrer",
        "btn.logout": "Se déconnecter",
        "btn.pause": "Pause",
        "btn.restore": "Restaurer les défauts",
        "col.accent": "Accent",
        "col.add_pref": "Ajouter aux préférées",
        "col.add_ref": "Ajouter aux refusées",
        "col.chip_desc": "rgb(%d, %d, %d) dans %s - cliquez sur la "
            "case pour retirer cette couleur.",
        "col.chip_off": "%s ne contient aucune couleur - la case "
            "barrée signifie désactivé. Choisissez une couleur "
            "ci-dessous et appuyez sur le bouton d'ajout "
            "correspondant.",
        "col.exclude": "Exclusion",
        "col.pick": "Prendre la couleur à l'écran",
        "col.rgb.desc": "Trois cases montrent la couleur qui se "
            "trouve dans le mélangeur en ce moment : la première "
            "brille selon sa quantité de rouge, la deuxième de vert, "
            "la troisième de bleu - plus c'est brillant, plus il y "
            "en a. La ligne suit le mélangeur, les nuances prêtes et "
            "les boutons d'écran ; on ne peut pas y taper.",
        "col.rgb.name": "Valeur RVB actuelle",
        "col.suggest": "Couleurs d'écran suggérées",
        "desc.accent_boost": "Combien votre couleur élève la d'un "
            "élément (0-3). Montez vers 1,5-2 si le mauvais élément "
            "gagne encore.",
        "desc.accent_coherent": "Votre couleur doit former une tache "
            "connectée pour compter - les taches éparses de tramage "
            "ou de compression ne qualifient aucun élément, ne le "
            "boostent ni ne le mettent sur la liste jamais "
            "cliquable.",
        "desc.accent_color": "La couleur que Snappy AI doit "
            "préférer, montrée en cases de couleur à droite. "
            "Choisissez une couleur ci-dessous et appuyez sur « "
            "Ajouter aux préférées » pour l'ajouter - quinze cases "
            "au plus ; un clic sur une case retire à nouveau cette "
            "couleur. Les éléments qui en contiennent une gagnent "
            "les égalités. Une liste vide montre une case barrée et "
            "désactive le réglage.",
        "desc.accent_matcher": "Comment les couleurs sont comparées. "
            "Perceptuel classe selon l'apparence réelle des couleurs "
            "et est recommandé ; Classique est l'ancien moteur, "
            "gardé pour comparaison.",
        "desc.accent_only": "Seuls les éléments contenant votre "
            "couleur peuvent être assistés ; les clics ailleurs "
            "passent intacts à Windows.",
        "desc.accent_soft": "0-100 : dans quelle mesure les versions "
            "plus claires, sombres ou délavées de votre couleur "
            "comptent quand même. 0 = teintes exactes seulement.",
        "desc.accent_tolerance": "À quel point une couleur doit être "
            "proche pour compter comme la vôtre (4-90). Plus bas = "
            "plus strict.",
        "desc.accent_variants": "Des copies plus claires et plus "
            "sombres de votre couleur comptent aussi, pour que les "
            "états de survol, pressé et atténué comptent sans "
            "élargir la tolérance de teinte. Luminosité seulement - "
            "une teinte fausse ne passe jamais.",
        "desc.adaptive_threshold": "Les thèmes sombres et documents "
            "délavés abaissent seuls leur seuil de détection, si "
            "bien que les éléments pâles sont trouvés aussi. "
            "Recommandé activé.",
        "desc.auto_click": "Activé, le programme clique seul toutes les 0,1 s sur le meilleur "
            "élément de la zone surveillée, en privilégiant le contraste. Avec "
            "une couleur d'accent définie, seuls les éléments porteurs comptent "
            "; sans couleur, seuls les éléments très nets sont cliqués. Jamais "
            "deux fois au même endroit ni dans ses propres fenêtres.",
        "desc.auto_click_interval": "Tous les combien l'écran est "
            "examiné pour votre couleur (0,5-60). Un nombre lent est "
            "le plus sûr : 2-5 convient à un dialogue que vous "
            "regardez.",
        "desc.auto_click_max_clicks": "Combien de fois il peut "
            "cliquer seul après le démarrage (1-200). À la limite il "
            "s'arrête et le dit, pour qu'un mauvais réglage ne "
            "s'emballe pas.",
        "desc.auto_click_min_contrast": "Sur la même échelle que « "
            "Netteté minimale du bord ». Partez du défaut et montez "
            "si le mauvais élément est cliqué : seuls les éléments "
            "forts et bien dessinés compteront.",
        "desc.auto_click_radius": "Le clic automatique cherche "
            "autour du centre de l'écran (40-600 px). Plus large "
            "pour une fenêtre chargée ; plus étroit pour ne voir que "
            "le seul contrôle du milieu.",
        "desc.auto_click_repeat_px": "Après un clic automatique, une "
            "cible dans ces pixels est laissée tranquille (0-400). "
            "Sans cela, un bouton resté à l'écran serait cliqué sans "
            "fin.",
        "desc.auto_click_settle_ms": "Le curseur repose ainsi sur la "
            "cible (0-2000 ms) avant le clic, pour que le programme "
            "voie la surbrillance d'abord. 120 convient à la plupart "
            "des fenêtres.",
        "desc.block_bound_keys": "Non (défaut) : un raccourci sans "
            "Ctrl/Alt/Shift - comme 1 ou V - agit dans chaque "
            "programme ET continue de s'écrire normalement, donc le "
            "taper au milieu d'une phrase déclenche aussi son "
            "action. Oui : l'action se déclenche toujours partout, "
            "mais la touche ne s'écrit plus.",
        "desc.capture_backend": "Comment l'écran est photographié. "
            "Automatique utilise la méthode compatible, qui voit presque toutes les fenêtres ; "
            "Compatible marche toujours, y compris Bureau à distance "
            "et machines virtuelles. Appliqué au redémarrage.",
        "desc.color_adapt": "Chaque élément est équilibré en blancs "
            "sur son propre fond avant comparaison, pour que la "
            "lumière nocturne et les teintes du thème cessent de "
            "sortir votre couleur de la tolérance. Ne l'éteignez que "
            "pour comparer avec le comparateur non adapté.",
        "desc.contrast_threshold": "Plus bas trouve des éléments "
            "plus pâles (et plus de bruit) ; plus haut exige des "
            "bords plus nets.",
        "desc.default": "Survolez le nom d'un réglage pour voir son "
            "effet.",
        "desc.exclude_color": "Les éléments contenant ces couleurs "
            "ne sont jamais assistés : les clics dessus partent "
            "directement à Windows, dans les deux modes. Montrés en "
            "cases de couleur à droite - choisissez une couleur "
            "ci-dessous et appuyez sur « Ajouter aux refusées » pour "
            "en ajouter une (quinze au plus) ; un clic sur une case "
            "la retire. Une liste vide montre une case barrée et "
            "désactive le réglage.",
        "desc.follow_boost": "Avec quelle force l'élément mémorisé "
            "gagne les égalités : 100% peut doubler son score tant "
            "qu'il est frais, 25% est une poussée légère.",
        "desc.follow_enabled": "Après un accrochage réussi, les "
            "éléments semblables ou au même endroit gagnent pendant "
            "un moment - pratique pour les barres de défilement et "
            "les clics répétés sur un contrôle.",
        "desc.follow_learn": "Seulement les éléments de ma couleur : "
            "un clic raté ne peut pas rediriger le souvenir. Chaque "
            "accrochage réussi : l'ancien comportement confiant.",
        "desc.follow_seconds": "Secondes pendant lesquelles "
            "l'élément mémorisé reste préféré après votre dernier "
            "accrochage réussi (1-120).",
        "desc.glide_ms": "0 (défaut) saute instantanément - le plus "
            "rapide. 40-120 glisse pour que vous puissiez suivre ; "
            "bouger la souris vous-même annule le glissement.",
        "desc.hold_follow": "Tant que vous gardez le bouton gauche "
            "appuyé juste après un accrochage - ou que vous rappuyez "
            "sur l'élément mémorisé - le curseur reste sur la "
            "couleur de cet élément ; cela stabilise les glissements "
            "comme les poignées de barre de défilement. Les appuis "
            "ailleurs ne sont jamais touchés.",
        "desc.key_launch": "Format : ctrl+l, f5, space, ctrl+alt+1 "
            "... Modificateurs : ctrl, alt, shift, win. Appliqué sur "
            "Appliquer.",
        "desc.key_mode1": "Séparé par des virgules, ex. '1, f1, "
            "ctrl+f1, v'. Ce que fait le mode classique est expliqué "
            "dans l'onglet Raccourcis.",
        "desc.key_mode2": "Séparé par des virgules, ex. '2, f2, "
            "ctrl+f2, b'. Ce que fait le mode guide est expliqué "
            "dans l'onglet Raccourcis.",
        "desc.key_pause": "La souris et le clavier redeviennent "
            "entièrement vôtres, jusqu'au démarrage.",
        "desc.key_play": "Lit l'enregistrement choisi dans la liste "
            "des Macros, ou le plus récent si rien n'est choisi. Sur "
            "un enregistrement qui répète, il l'arrête.",
        "desc.key_play_n": "Lit l'enregistrement #%d de la liste "
            "numérotée de l'onglet Macros, selon sa position. Si la "
            "liste est plus courte, rien ne se passe.",
        "desc.key_record": "Capture tout ce que vous faites - chaque "
            "touche, chaque clic de souris et chaque mouvement du "
            "curseur - pendant que vos entrées atteignent toujours "
            "vos programmes, jusqu'à ce que le raccourci d'arrêt les "
            "sauvegarde dans la liste des Macros. Armé seulement "
            "pendant le fonctionnement.",
        "desc.key_record_stop": "Arrête la capture, sauvegarde la "
            "séquence dans la liste des Macros et stoppe une lecture "
            "en cours.",
        "desc.luminance_norm": "Les bords sont notés par rapport à "
            "la luminosité de leur entourage, si bien que les thèmes "
            "sombres se comportent comme les clairs. Recommandé "
            "activé.",
        "desc.macro_action": "La combinaison pressée pour vous à "
            "chaque pression du déclencheur (une pression = une "
            "combinaison) : 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' "
            "... Vide = macro désactivée.",
        "desc.macro_key": "La touche qui SIGNIFIE la macro au lieu "
            "d'écrire : 'b', 'f7', 'ctrl+b' ... En fonctionnement, "
            "une pression envoie la combinaison d'à côté exactement "
            "une fois et la touche n'atteint pas vos programmes. En "
            "pause, elle écrit normalement. Vide = macro désactivée.",
        "desc.max_area": "Les taches plus grandes sont ignorées - "
            "souvent des fenêtres entières ou le fond, pas des "
            "éléments cliquables.",
        "desc.max_dim": "Les éléments plus larges ou plus hauts que "
            "ceci sont ignorés ; ceux qui touchent un bord d'écran, "
            "comme les barres de défilement, reçoivent le double.",
        "desc.merge_distance": "Les morceaux plus proches que ceci "
            "(contour cassé, icône près de son libellé) deviennent "
            "un élément. Deux éléments complets ne sont jamais "
            "collés.",
        "desc.min_area": "Les taches plus petites sont ignorées "
            "comme des mouchetures, sauf si elles se collent à un "
            "élément plus grand.",
        "desc.min_contrast": "Un élément doit être au moins aussi "
            "net pour être cliquable du tout. Les valeurs sous 28 "
            "valent 28 : un plancher de qualité intégré empêche le "
            "bruit de devenir cliquable.",
        "desc.motion_3d": "Suit les éléments mobiles avec position "
            "ET taille au lieu d'un ajustement droit : les mauvaises "
            "analyses isolées sont ignorées au lieu d'aveugler le "
            "suiveur, les virages sont suivis, et un saut brusque de "
            "taille relance la piste (le scanneur a pris un autre "
            "élément). Mêmes seuils de vitesse, même plafond de 80 "
            "px - seuls les cerveaux changent. Fonctionne seul.",
        "desc.motion_lead_ms": "Millisecondes de trajet dont on "
            "anticipe un élément mobile (0-300) : 40-80 pour un "
            "défilement lent, 100-150 pour une barre rapide. Plafond "
            "de 80 px, désactivé pour un mouvement lent ou qui "
            "tourne.",
        "desc.motion_predict": "Pour les éléments qui bougent "
            "pendant le clic (listes qui défilent, barres vidéo), "
            "vise un peu en avant pour que le clic tombe sur "
            "l'élément. Les éléments immobiles ne changent pas.",
        "desc.mouse2_action": "Ce qu'un clic droit court fait EN "
            "PLUS - le clic droit lui-même garde toujours sa "
            "fonction Windows normale. Défaut : rien.",
        "desc.mouse2_hold_action": "Les mêmes choix, déclenchés "
            "quand vous MAINTENEZ le bouton droit environ une "
            "demi-seconde au lieu de cliquer. Un appui est soit un "
            "clic soit un maintien, jamais les deux. Défaut : rien.",
        "desc.on_target_dist": "Si votre clic tombe dans ce nombre "
            "de pixels du centre de l'élément, rien ne bouge - vous "
            "avez touché.",
        "desc.radius": "Distance de recherche en pixels (40-400). "
            "Montez-la si l'élément voulu est juste hors de portée ; "
            "descendez-la si le mauvais voisin gagne.",
        "desc.rapid_click_snap": "Non (défaut) : pendant qu'un clic "
            "se traite, les autres vont à Windows. Oui : chaque clic "
            "gauche est assisté.",
        "desc.snap_offset_x": "Décale le point de clic latéralement "
            "depuis le centre de l'élément (-200 à 200, négatif vers "
            "la gauche). Pour un contrôle dont le centre est mort - "
            "bouton partagé, barre de défilement - réglez le clic "
            "sur le point vivant une fois au lieu de lutter à chaque "
            "snap.",
        "desc.snap_offset_y": "Décale le point de clic verticalement "
            "depuis le centre de l'élément (-200 à 200, négatif vers "
            "le haut). Comme le décalage latéral : atterrissez sur "
            "la partie vivante du contrôle.",
        "desc.stall_pause_seconds": "Si un balayage se bloque un "
            "jour, l'assistance fait une pause de cette durée et "
            "tout clic maintenu vous est rendu.",
        "desc.watcher_seconds": "En mode classique, un second "
            "accrochage près du même endroit dans ce délai devient "
            "un double-clic sur l'élément.",
        "ent.cancel_line": "actif jusqu'au %s - NE se renouvellera "
            "PAS",
        "ent.canceled_line": "abonnement terminé%s",
        "ent.expired_line": "expiré le %s - renouvelez sur Stripe",
        "ent.past_due_line": "paiement échoué - corrigez la carte "
            "dans le courriel de reçu Stripe ; l'accès revient quand "
            "la facture est payée",
        "ent.plan": " (%s)",
        "ent.refunded_line": "remboursé / contesté - activation "
            "révoquée",
        "ent.st.active": "actif",
        "ent.st.canceled": "terminé",
        "ent.st.canceling": "actif mais en annulation",
        "ent.st.grant": "accord de support",
        "ent.st.past_due": "PAIEMENT ÉCHOUÉ",
        "ent.st.refunded": "remboursé / contesté",
        "ent.st.trial": "essai",
        "ent.st.unsubscribed": "aucun abonnement",
        "ent.until": " jusqu'au %s",
        "err.auth_unreachable": "Le serveur d'authentification de "
            "Snappy AI est injoignable :\n%s\n\nSnappy AI ne "
            "fonctionne qu'avec une réponse vivante de "
            "celui-ci.\nRéessayer ?",
        "err.start_fail": "Snappy AI n'a pas pu démarrer.\nLancez "
            "avec --console pour voir les détails.",
        "gate.btn.monthly": "Abonnement mensuel à 9,99€",
        "gate.btn.trial": "Achat d'essai à 1,99€",
        "gate.head.canceled": "Cet abonnement a été annulé - "
            "commencez-en un nouveau sur Stripe pour continuer.",
        "gate.head.canceling": "Votre abonnement est programmé pour "
            "annulation - il reste actif jusqu'au %s, puis cette "
            "connexion se verrouille à moins de renouveler.",
        "gate.head.email_mismatch": "Le paiement a été fait avec un "
            "e-mail différent de celui de votre compte Discord. Les "
            "abonnements ne marchent que sur l'e-mail Discord montré "
            "ci-dessous - réabonnez-vous avec lui, ou contactez le "
            "support.",
        "gate.head.expired": "L'abonnement de cette connexion a "
            "expiré - renouvelez-le sur Stripe pour continuer.",
        "gate.head.none": "Vous êtes connecté, mais cette connexion "
            "n'a pas d'abonnement actif. Payez avec CET e-mail "
            "Discord - un achat sur une autre adresse ne peut pas "
            "l'activer.",
        "gate.head.past_due": "Le dernier paiement d'abonnement a "
            "échoué - corrigez-le sur Stripe pour réactiver cette "
            "connexion.",
        "gate.head.refunded": "Cet achat a été remboursé ou "
            "contesté, donc l'activation a été révoquée. Un nouvel "
            "abonnement sur cet e-mail Discord la réactive.",
        "gate.head.shared": "Ce compte est utilisé EN CE MOMENT sur "
            "un AUTRE ordinateur. Snappy AI reste éteint tant que le "
            "même compte Discord tourne à deux endroits - fermez "
            "l'autre session puis revérifiez. Partager les "
            "abonnements fait monter les prix ; merci de ne pas le "
            "faire.",
        "gate.msg.active": "Abonnement actif - démarrage de Snappy "
            "AI...",
        "gate.msg.checking": "Vérification auprès du serveur...",
        "gate.msg.no_link": "Ce lien de paiement n'est pas configuré "
            "sur cette version.",
        "gate.msg.open_fail": "Impossible d'ouvrir un navigateur. "
            "Ouvrez ce lien à la main :\n%s",
        "gate.msg.open_ok": "Stripe est ouvert dans votre navigateur - payez-y. Cette fenêtre remarque le paiement toute seule et démarre le moteur.",
        "gate.msg.session_gone": "Session perdue - reconnectez-vous.",
        "gate.msg.still_none": "Toujours aucun abonnement actif pour "
            "cette connexion.",
        "gate.msg.still_shared": "Toujours utilisé sur un autre "
            "ordinateur - fermez cette session puis revérifiez.",
        "gate.msg.unreachable": "Serveur d'authentification "
            "injoignable : %s",
        "gate.note": "Le moteur démarre dès que l'abonnement est "
            "actif - cette fenêtre se revérifie seule toutes les 30 "
            "secondes. La fermer revient à la connexion.",
        "gate.prices": "Essai 2 jours : 1,99€ (une fois)  -  "
            "abonnement : 9,99€ / mois.\nL'activation arrive jusqu'à "
            "~10 minutes après le paiement ; les renouvellements "
            "réactivent automatiquement cette même connexion.",
        "gate.title": "%s - Abonnement%s",
        "hdr.build": "build %s",
        "help.1.b": "Snappy AI regarde l'écran autour de votre "
            "curseur, trouve les choses solides en forme d'élément "
            "qui sont près - boutons, icônes, liens - et choisit la "
            "meilleure : bords nets, taille correcte et proximité du "
            "curseur gagnent. Votre couleur, la liste des "
            "jamais-cliquables et le souvenir de votre dernier clic "
            "peuvent infléchir le choix. Le curseur vise ensuite le "
            "milieu de l'élément, pas le coin de sa boîte.",
        "help.1.t": "Ce qui se passe quand vous cliquez",
        "help.10.b": "1. Est-ce démarré ? En pause, rien n'est "
            "intercepté - « Raccourci : démarrer l'assistance » "
            "(Ctrl+L par défaut) est le seul marche/arrêt.  2. "
            "Maintenez Shift sur un clic pour confirmer que "
            "l'assistance était le problème.  3. Le mauvais élément "
            "gagne : descendez « Distance de recherche depuis le "
            "curseur », puis fixez « Ma couleur » ou montez « Force "
            "de l'avantage de couleur ».  4. Rien n'est trouvé : "
            "descendez « Quelle pâleur de bord est admise » et « "
            "Netteté minimale du bord », montez « Largeur ou hauteur "
            "maximale » ou « Coller les morceaux proches ».  5. Une "
            "chose ne doit jamais être assistée : mettez sa couleur "
            "dans dans « Couleur(s) jamais cliquables ».  6. "
            "Toujours faux : dites au support ce que vous avez "
            "cliqué et ce que vous attendiez, et joignez le fichier "
            "journal que Snappy AI écrit dans son dossier de "
            "données.",
        "help.10.t": "Si quelque chose va mal, vérifiez dans cet "
            "ordre",
        "help.2.b": "Le mode guide (défaut) ne mange aucun clic : "
            "votre clic atteint le programme et, après relâchement, "
            "le curseur va sur l'élément dégagé le plus proche. Le "
            "mode classique est plus fort : un clic raté près d'un "
            "élément est capturé, le curseur s'accroche et Snappy AI "
            "clique pour vous. « Distance de recherche depuis le "
            "curseur » fixe le cercle de recherche - montez-la si "
            "l'élément voulu est juste hors de portée, descendez-la "
            "si le mauvais voisin gagne. Maintenir Shift évite un "
            "clic dans les deux modes.",
        "help.2.t": "Commencez ici : mode et distance de recherche",
        "help.3.b": "Dans l'onglet Traitement, « Quelle pâleur de "
            "bord est admise » et « Netteté minimale du bord » "
            "décident quels bords comptent : plus bas trouve plus "
            "pâle, plus haut ignore le bruit. « Taille minimale "
            "d'élément », « Aire maximale d'élément » et « Largeur "
            "ou hauteur maximale » écartent mouchetures et fenêtres "
            "entières. « Coller les morceaux proches » réunit un "
            "contour cassé, ou une icône près de son libellé, en un "
            "élément. Dans l'onglet Assistance, « Réglage auto pour "
            "écrans ternes » et « Juger les bords par luminosité "
            "relative » font que les thèmes sombres se comportent "
            "comme les clairs - laissez-les activés.",
        "help.3.t": "Rien n'est trouvé - ou trop l'est",
        "help.4.b": "Dans l'onglet Couleurs, « Ma couleur » est la "
            "couleur préférée et « Couleur(s) jamais cliquables » "
            "est absolu : ces éléments ne sont jamais assistés. « "
            "N'assister que ma couleur » restreint l'assistance aux "
            "éléments correspondants. Dans Traitement, « Rigueur de "
            "la correspondance » dit à quel point une teinte doit "
            "être proche, « Accepter les teintes proches » laisse "
            "compter en partie les versions claires ou délavées, et "
            "« Force de l'avantage de couleur » dit combien votre "
            "couleur élève un élément - montez-la si le mauvais "
            "gagne encore.",
        "help.4.t": "Travailler avec les couleurs",
        "help.5.b": "« Se souvenir du dernier élément cliqué » "
            "continue de préférer l'élément où votre dernier clic "
            "réussi est tombé, pendant « Durée du souvenir » "
            "secondes - c'est ce qui rend agréables barres de "
            "défilement et boutons de dialogue. « Force du souvenir "
            "» dit avec quelle force il gagne, et « Ce que le "
            "souvenir peut apprendre » le protège : avec « Seulement "
            "les éléments de ma couleur », un clic raté ne peut pas "
            "le rediriger. « Suivre l'élément tant que le bouton est "
            "maintenu » stabilise les glissements, et les actions du "
            "bouton droit dans Expérimental peuvent suivre ou "
            "effacer le souvenir à la souris.",
        "help.5.t": "Clics répétés sur un contrôle",
        "help.6.b": "« Anticiper les éléments mobiles » mesure la "
            "vitesse de déplacement de l'élément choisi et vise en "
            "avant de « Quelle avance pour le tir » millisecondes, "
            "pour que le clic tombe sur une liste qui défile ou une "
            "barre vidéo au lieu de derrière. L'avance est plafonnée "
            "à 80 pixels et se coupe seule pour les éléments "
            "immobiles ou qui tournent.",
        "help.6.t": "Cliquer des choses qui bougent",
        "help.7.b": "« Animer le déplacement du curseur » = 0 saute "
            "instantanément ; 40-120 glisse pour que vous puissiez "
            "suivre, et bouger la souris vous-même annule le "
            "glissement. « Fenêtre de double-clic » transforme en "
            "mode classique un second accrochage près du même "
            "endroit en double-clic. « Assister chaque clic d'une "
            "rafale » assiste chaque clic d'une série au lieu du "
            "premier seul. « Pause après un blocage » est la soupape "
            "qui rend un clic maintenu si un balayage se bloque.",
        "help.7.t": "Comment se sentent les clics",
        "help.8.b": "L'onglet Raccourcis explique les deux modes et "
            "le flux d'enregistrement. En bref : les raccourcis avec "
            "Ctrl, Alt, Shift ou Win sont réservés système ; les "
            "touches simples se déclenchent partout et continuent de "
            "taper. Une macro transforme une pression bloquée en une "
            "combinaison entière. Les enregistrements capturent vos "
            "entrées réelles - chaque touche, clic de souris et "
            "mouvement du curseur - et les rejouent depuis l'onglet "
            "Macros, chacun avec son propre interrupteur une fois ou "
            "répéter jusqu'à l'arrêt.",
        "help.8.t": "Touches, macros et enregistrements",
        "help.9.b": "Le bouton Langue à côté de « Exporter la "
            "configuration » - aussi dans les fenêtres de connexion "
            "et d'abonnement - bascule toute l'interface d'un coup, "
            "sans redémarrer, et se souvient de votre choix. Les "
            "langues encore en traduction ne sont pas proposées, "
            "donc tout ce que vous pouvez choisir est complet.",
        "help.9.t": "Langue",
        "help.sub": "Chaque réglage sous le nom que vous voyez sur "
            "son onglet, dans l'ordre où vous en aurez besoin. "
            "Survolez un nom pour sa description d'une ligne ; cette "
            "page est la forme longue.",
        "help.tail": "Les réglages s'appliquent en pressant "
            "Appliquer. Un config.ini à côté du programme remplace "
            "config.json. Cette page explique ; elle ne configure "
            "pas.",
        "help.title": "Régler Snappy AI avec des mots simples",
        "kb.keys.b": "Un raccourci avec Ctrl, Alt, Shift ou Win est "
            "réservé à l'échelle du système : seul Snappy AI le "
            "voit. Une touche nue (comme 1 ou 2) agit dans chaque "
            "programme ET continue de s'écrire - le prix est que la "
            "taper au milieu d'une phrase déclenche aussi son "
            "action. Pour le comportement classique, activez « Les "
            "raccourcis à une touche avalent la touche » dans "
            "l'onglet Assistance. Les macros vont plus loin : en "
            "fonctionnement, la touche déclencheur est avalée et la "
            "combinaison d'à côté est envoyée exactement une fois.",
        "kb.keys.t": "Touches seules contre combinaisons",
        "kb.mode.b": "Mode guide (défaut, raccourci 2) : votre clic "
            "arrive toujours intact au programme ; après le "
            "relâchement, le curseur va sur l'élément dégagé le plus "
            "proche, si bien que votre prochain clic part de là. "
            "Rien n'est jamais avalé - le mode le plus sûr.  Mode "
            "classique (raccourci 1) : si vous cliquez près d'un "
            "élément, ce clic raté est capturé, le curseur "
            "s'accroche à l'élément et Snappy AI clique pour vous ; "
            "s'il n'y a rien près, votre clic est rendu intact.  "
            "Dans les deux modes, maintenir Shift en cliquant évite "
            "l'assistance pour ce clic-là.",
        "kb.mode.t": "Ce que font les deux modes",
        "kb.rec.b": "Pendant le fonctionnement, appuyez sur votre "
            "raccourci de démarrage d'enregistrement (Ctrl+Alt+R par "
            "défaut) : chaque touche pressée, chaque bouton de "
            "souris cliqué et chaque mouvement du curseur est "
            "capturé ET continue d'atteindre vos programmes, vous "
            "pouvez donc travailler normalement pendant "
            "l'enregistrement. Appuyez sur le raccourci d'arrêt "
            "(Ctrl+Alt+S) pour le sauvegarder dans la liste de "
            "l'onglet Macros - cinq enregistrements y tiennent. "
            "Cliquez sur un enregistrement pour le choisir, utiliser "
            "« Renommer » ou « Exporter », et régler son propre "
            "interrupteur « Répéter jusqu'à l'arrêt ». Le raccourci "
            "de lecture (Ctrl+Alt+M) rejoue l'enregistrement choisi "
            "là ; Ctrl+1 à Ctrl+5 rejouent selon la position dans la "
            "liste. En pause, rien n'est enregistré et rien n'est "
            "injecté - vos entrées sont entièrement les vôtres.",
        "kb.rec.t": "Enregistrer et rejouer vos propres frappes et "
            "mouvements de souris",
        "lang.close": "Fermer",
        "lang.coverage": "%d %% traduit",
        "lang.current": "Actuelle : %s",
        "lang.progress": "Encore en traduction, proposé dès qu'il "
            "est complet : %s",
        "lang.prompt": "Le changement est immédiat ; la fenêtre "
            "reste ouverte pour en essayer plusieurs.",
        "lang.title": "Langue",
        "lbl.accent_boost": "Force de l'avantage de couleur",
        "lbl.accent_coherent": "Ignorer les taches de couleur "
            "éparses",
        "lbl.accent_color": "Ma couleur (couleurs)",
        "lbl.accent_matcher": "Moteur de correspondance des couleurs",
        "lbl.accent_only": "N'assister que ma couleur",
        "lbl.accent_soft": "Accepter les teintes proches",
        "lbl.accent_tolerance": "Rigueur de la correspondance de "
            "couleur",
        "lbl.accent_variants": "États clairs et sombres de ma "
            "couleur",
        "lbl.adaptive_threshold": "Réglage auto pour écrans ternes",
        "lbl.auto_click": "Cliquer les éléments tout seul",
        "lbl.auto_click_interval": "Secondes entre les clics "
            "automatiques",
        "lbl.auto_click_max_clicks": "Limite de clics automatiques "
            "par session",
        "lbl.auto_click_min_contrast": "Netteté requise d'une cible "
            "automatique",
        "lbl.auto_click_radius": "Chercher autour du centre",
        "lbl.auto_click_repeat_px": "Ne pas recliquer le même "
            "endroit",
        "lbl.auto_click_settle_ms": "Pause avant le clic automatique",
        "lbl.block_bound_keys": "Les raccourcis à une touche avalent "
            "la touche",
        "lbl.capture_backend": "Moteur de capture d'écran",
        "lbl.color_adapt": "S'adapter à la lumière de l'écran",
        "lbl.contrast_threshold": "Quelle pâleur de bord est admise",
        "lbl.exclude_color": "Couleur(s) jamais cliquables",
        "lbl.follow_boost": "Force du souvenir",
        "lbl.follow_enabled": "Se souvenir du dernier élément cliqué",
        "lbl.follow_learn": "Ce que le souvenir peut apprendre",
        "lbl.follow_seconds": "Durée du souvenir",
        "lbl.glide_ms": "Animer le déplacement du curseur",
        "lbl.hold_follow": "Suivre l'élément tant que le bouton est "
            "maintenu",
        "lbl.key_launch": "Raccourci : démarrer l'assistance",
        "lbl.key_mode1": "Raccourci : mode classique (4 touches max)",
        "lbl.key_mode2": "Raccourci : mode guide (4 touches max)",
        "lbl.key_pause": "Raccourci : pause",
        "lbl.key_play": "Raccourci : lire l'enregistrement choisi",
        "lbl.key_play_n": "Raccourci : lire l'enregistrement #%d",
        "lbl.key_record": "Raccourci : démarrer un enregistrement",
        "lbl.key_record_stop": "Raccourci : arrêter et sauvegarder "
            "l'enregistrement",
        "lbl.luminance_norm": "Juger les bords par luminosité "
            "relative",
        "lbl.macro_action": "Macro %d : envoie à la place",
        "lbl.macro_key": "Macro %d : appuyez sur cette touche",
        "lbl.max_area": "Aire maximale d'élément",
        "lbl.max_dim": "Largeur ou hauteur maximale d'élément",
        "lbl.merge_distance": "Coller les morceaux proches",
        "lbl.min_area": "Taille minimale d'élément",
        "lbl.min_contrast": "Netteté minimale du bord",
        "lbl.motion_3d": "Suivi plus intelligent des éléments "
            "mobiles",
        "lbl.motion_lead_ms": "Quelle avance pour le tir",
        "lbl.motion_predict": "Anticiper les éléments mobiles",
        "lbl.watch_center_only": "Surveiller uniquement le centre de l'écran",
        "desc.watch_center_only": "L'assistance n'observe qu'un carré fixe au centre de l'écran "
            "(taille = distance de recherche, 150×150 px par défaut), où que "
            "soit le curseur. Les clics hors de ce carré restent inchangés.",
        "lbl.center_follow": "L'écran suit la cible",
        "desc.center_follow": "Quand « Surveiller uniquement le centre de l'écran » est activé : "
            "après l'accrochage d'un élément, l'assistance déplace l'écran pour "
            "le garder au centre, surtout sur les plans défilants. Déplacez "
            "vous-même l'écran pour relâcher le suivi.",
        "lbl.input_backend": "Méthode d'entrée",
        "desc.input_backend": "Injection Windows (par défaut) fonctionne partout. Interception "
            "envoie via le pilote et les jeux le reconnaissent comme une vraie "
            "souris ; nécessite le pilote Interception installé et "
            "interception.dll à côté du programme ; sinon l'injection Windows "
            "est utilisée automatiquement.",
        "val.input_backend.win32": "Injection Windows",
        "val.input_backend.interception": "Interception (pilote)",
        "lbl.mouse2_action": "Action supplémentaire du clic droit",
        "lbl.mouse2_hold_action": "Action du maintien du clic droit",
        "lbl.on_target_dist": "Distance « déjà dessus »",
        "lbl.radius": "Distance de recherche depuis le curseur",
        "lbl.rapid_click_snap": "Assister chaque clic d'une rafale "
            "rapide",
        "lbl.snap_offset_x": "Point de clic : décaler à gauche / "
            "droite",
        "lbl.snap_offset_y": "Point de clic : décaler en haut / bas",
        "lbl.stall_pause_seconds": "Pause après un blocage",
        "lbl.watcher_seconds": "Fenêtre de double-clic",
        "login.failed": "La connexion %s ne s'est pas terminée - "
            "réessayez.",
        "login.no_provider": "Aucun fournisseur de connexion n'est "
            "intégré à cette copie.",
        "login.not_configured": "Le fichier d'abonnement n'est pas "
            "encore configuré sur cette version.",
        "login.note": "La connexion ouvre votre navigateur et "
            "revient toute seule à cette fenêtre.",
        "login.provider": "Se connecter avec %s",
        "login.signedin": "Connecté en tant que %s.",
        "login.sub": "Connectez-vous avec Discord - votre abonnement "
            "est lié à ce compte, et les paiements doivent utiliser "
            "son adresse e-mail. Pas de mot de passe ici.",
        "login.title": "%s - Connexion",
        "login.unreachable": "Serveur d'authentification injoignable "
            ": %s",
        "login.waiting": "En attente du navigateur - terminez la "
            "connexion %s...",
        "mac.delete": "Supprimer",
        "mac.empty": "Aucun enregistrement pour l'instant - lancez, "
            "appuyez sur votre raccourci d'enregistrement et "
            "travaillez normalement : chaque touche, clic et "
            "mouvement du curseur est capturé.",
        "mac.export": "Exporter",
        "mac.import": "Importer",
        "mac.keys_head": "Macros de touches",
        "mac.loop": "Répéter jusqu'à l'arrêt",
        "mac.recordings": "Enregistrements",
        "mac.rename": "Renommer",
        "mac.row": "Macro %d",
        "mac.sends": "envoie",
        "mac.steps": "%d étapes",
        "note.advanced": "Réglages de distance et de temps qui "
            "changent comment se sentent les clics, pas ce qui est "
            "trouvé. La plupart des gens n'y touchent jamais ; les "
            "valeurs par défaut sont celles testées.",
        "note.assist": "Chaque interrupteur qui change le "
            "comportement en fonctionnement. Les deux modes se "
            "changent avec vos touches de mode - l'onglet Raccourcis "
            "explique ce que fait chacun. L'assistance démarre "
            "toujours en pause ; Démarrer est le seul marche/arrêt. "
            "Où regarde le moteur et comment se sentent les clics "
            "vit dans Avancé ; ce qui compte comme élément, dans "
            "Traitement.",
        "note.colors": "Les deux listes en haut choisissent les "
            "couleurs que Snappy AI préfère ou refuse. Chacune "
            "montre ses couleurs sous forme de cases à droite, "
            "quinze au plus, et un clic sur une case retire à "
            "nouveau cette couleur ; une liste vide montre une case "
            "barrée et compte comme désactivée. « Ajouter aux "
            "préférées » et « Ajouter aux refusées » rangent la "
            "couleur du nuanceur dans la liste correspondante. "
            "Valeur RVB actuelle montre trois cases - chacune aussi "
            "large que cinq cases de couleur, la rangée couvre donc "
            "les mêmes quinze cases que tout ce qui suit - qui "
            "brillent selon la part de rouge, de vert et de bleu de "
            "la couleur du nuanceur ; la ligne suit le nuanceur et "
            "ne se tape pas. Le nuanceur ci-dessous mélange une "
            "couleur comme un logiciel de peinture ; tout ce qui "
            "l'accompagne siège sur le côté droit de la fenêtre, "
            "avec le même écart au bord que les réglages du haut, et "
            "chaque rangée couvre la même largeur de quinze cases : "
            "la haute vitrine avec sa #valeur dessinée dedans, puis "
            "les quinze teintes prêtes, les deux boutons d'ajout et "
            "la rangée écran - « Prendre la couleur à l'écran » "
            "prend l'unique couleur sous le curseur, « Couleurs "
            "d'écran suggérées » remplit ses quinze cases avec les "
            "couleurs trouvées autour du curseur, et un clic sur "
            "l'une d'elles la charge dans le nuanceur. La vitrine "
            "est haute exprès : les cases suggérées finissent ainsi "
            "exactement au niveau du curseur de couleur de gauche.",
        "note.experimental": "Choix de moteurs, chacun avec un "
            "défaut testé. Ne les changez que pour comparer des "
            "moteurs, sur du matériel inhabituel, ou si le support "
            "le demande - le moteur de capture s'applique au "
            "redémarrage.",
        "note.handler": "Ce qui compte comme élément cliquable : "
            "quelle pâleur de bord est admise, quelle netteté est "
            "requise, et quelle taille un élément peut faire. Rien "
            "trouvé ? Desserrez ces valeurs. Trouvé ce qu'il ne "
            "fallait pas ? Resserrez-les, ou utilisez votre couleur "
            "dans l'onglet Couleurs.",
        "note.keybindings": "Chaque raccourci - et dessous, ce que "
            "font les deux modes, comment enregistrer vos propres "
            "frappes et mouvements de souris, et en quoi une touche "
            "seule diffère d'une combinaison.",
        "note.macros": "Une macro transforme une pression de touche "
            "en toute une combinaison pendant le fonctionnement. À "
            "côté des macros, vos enregistrements : jusqu'à cinq "
            "captures nommées de tout ce que vous avez fait - chaque "
            "touche, clic de souris et mouvement du curseur - "
            "rejouées exactement comme enregistrées. Cliquez sur un "
            "enregistrement pour le choisir ; chaque ligne porte son "
            "propre interrupteur « Répéter jusqu'à l'arrêt », et « "
            "Renommer », « Exporter », « Importer » et « Supprimer » "
            "se trouvent en bas de la boîte.",
        "note.macros_keys": "Les raccourcis enregistrer/lire sont "
            "dans l'onglet Raccourcis (défauts : Ctrl+Alt+R "
            "enregistrer, Ctrl+Alt+S arrêter et sauvegarder, "
            "Ctrl+Alt+M lire, Ctrl+1..5 lire par position).",
        "online.cancelled": "L'authentification Discord a été "
            "annulée (ou a échoué). Veuillez réessayer.",
        "rec.export_fail": "Échec de l'export : %r",
        "rec.exported": "Exporté vers %s",
        "rec.import_fail": "Échec de l'import : %r",
        "rec.imported": "%d enregistrement(s) importé(s)%s.",
        "rec.imported_none": " (aucun n'était valide)",
        "rec.no_sel": "Rien de choisi à exporter.",
        "rec.notfile": "Échec de l'import : ce n'est pas un fichier "
            "d'enregistrement.",
        "shared.back": "Bon retour - pressez Démarrer quand vous "
            "êtes prêt.",
        "shared.body": "Ce compte Discord exécute Snappy AI sur un "
            "autre ordinateur en ce moment.\nL'assistance est en "
            "pause ici jusqu'à ce qu'une seule session reste.\n\nUn "
            "abonnement, une machine à la fois - c'est ce qui "
            "garde\nle prix bas et le développement en route.",
        "shared.close": "Fermer",
        "shared.recheck": "Vérifier maintenant",
        "shared.still": "Toujours utilisé ailleurs - on reste en "
            "pause.",
        "shared.title": "Compte utilisé ailleurs",
        "shared.unreachable": "Serveur injoignable - on revérifiera.",
        "st.all_files": "Tous les fichiers",
        "st.color_added": "rgb(%d, %d, %d) ajouté à %s - Appliquer "
            "sauvegarde.",
        "st.color_already": "rgb(%d, %d, %d) est déjà dans %s.",
        "st.color_full": "%s contient déjà 15 couleurs - cliquez "
            "d'abord sur une de ses cases pour retirer une couleur.",
        "st.color_removed": "rgb(%d, %d, %d) retiré de %s - "
            "Appliquer sauvegarde.",
        "st.delete_confirm": "Supprimer l'enregistrement %r ?\nCeci "
            "est irréversible.",
        "st.deleted": "Enregistrement supprimé.",
        "st.engine_dead": "Fil du moteur indisponible - les "
            "raccourcis ne répondent pas.",
        "st.ent_paused": "Abonnement %s - assistance en pause. "
            "Renouvelez sur Stripe, puis redémarrez.",
        "st.ent_unreachable": "Revérification d'abonnement : serveur "
            "injoignable (la session continue).",
        "st.export_fail": "Échec de l'export : %r",
        "st.export_rec_title": "Exporter l'enregistrement",
        "st.export_title": "Exporter les réglages",
        "st.exported": "Réglages exportés vers %s",
        "st.file_rec": "Enregistrement Snappy AI",
        "st.file_settings": "Réglages Snappy AI",
        "st.follow": "  |  suivi il y a %d s",
        "st.import_fail": "Échec de l'import : %r",
        "st.import_notfile": "Échec de l'import : ce n'est pas un "
            "fichier de réglages.",
        "st.import_rec_title": "Importer le(s) enregistrement(s)",
        "st.import_title": "Importer les réglages",
        "st.imported": "%d réglage(s) importé(s)%s.",
        "st.imported_ignored": ", ignorés : %s",
        "st.ini_over": "Appliqué, mais config.ini remplace : %s",
        "st.lib_empty": "La liste est vide - rien à exporter.",
        "st.line": "Assistés %d  |  laissés passer %d%s  |  thème : "
            "%s",
        "st.loop_desc": "Style de lecture de CET enregistrement : "
            "désactivé = lire une fois ; activé = répéter jusqu'à ce "
            "que vous rappuyiez sur le raccourci de lecture. Chaque "
            "enregistrement a son propre interrupteur, sauvegardé "
            "avec l'enregistrement lui-même.",
        "st.name_empty": "Le nom ne peut pas être vide.",
        "st.pick_err": "Échec de la prise : %r",
        "st.pick_fail": "Échec de la prise - réessayez.",
        "st.pick_ok": "Pris rgb(%d, %d, %d) en (%d, %d).",
        "st.pick_wait": "Amenez le curseur sur la couleur - capture "
            "dans 3 s...",
        "st.preset_desc": "Nuance prête : %s - cliquez pour la "
            "charger dans le mélangeur.",
        "st.rec_count": "%d enregistrements sur 5",
        "st.rec_now": "%r maintenant : %s.",
        "st.rec_once": "se lit une fois",
        "st.rec_playing": "Lecture de %r...",
        "st.rec_playing_loop": "Lecture de %r jusqu'à l'arrêt",
        "st.rec_recording": "ENREGISTREMENT - %s arrête et "
            "sauvegarde",
        "st.rec_repeats": "répète jusqu'à l'arrêt",
        "st.registered": "Enregistré à : %s    Statut : %s",
        "st.rename_prompt": "Nouveau nom pour l'enregistrement #%d :",
        "st.renamed": "Enregistrement renommé.",
        "st.reset_confirm": "Remettre tous les réglages à leurs "
            "défauts ?\nLes comptes sont conservés ; cela ne touche "
            "que les réglages.",
        "st.rgb_bad": "Saisissez d'abord des valeurs R/G/B valides.",
        "st.running": "Actif..",
        "st.saved": "Sauvegardé et appliqué.",
        "st.defaults_restored": "Paramètres par défaut restaurés.",
        "st.saved_bad": "Sauvegardé, mais invalide (l'ancien est "
            "gardé) : %s",
        "st.select_rec": "Choisissez d'abord un enregistrement.",
        "st.shared_paused": "COMPTE UTILISÉ AILLEURS - assistance en "
            "pause ; un abonnement = une machine.",
        "st.standby": "Veille..",
        "st.sug_fail": "Échec de la suggestion : %r",
        "st.sug_loaded": "La suggestion rgb(%d, %d, %d) est dans le "
            "nuanceur - ajoutez-la à une liste avec les boutons "
            "ci-dessus.",
        "st.sug_loaded_desc": "Couleur d'interface suggérée rgb(%d, "
            "%d, %d) - %d%% de la région échantillonnée. Cliquez "
            "pour la charger dans le mélangeur.",
        "st.sug_none": "Aucune suggestion de couleur depuis cette "
            "région.",
        "st.sug_ok": "%d suggestions - cliquez sur l'une pour la "
            "charger dans le nuanceur.",
        "st.sug_wait": "Pointez l'application où vous travaillez - "
            "échantillonnage dans 3 s...",
        "tab.advanced": "Avancé",
        "tab.assist": "Assistance",
        "tab.colors": "Couleurs",
        "tab.experimental": "Expérimental",
        "tab.handler": "Traitement",
        "tab.help": "Aide",
        "tab.hotkeys": "Raccourcis",
        "tab.macros": "Macros",
        "theme.dark": "Sombre",
        "theme.light": "Clair",
        "val.accent_matcher.hsv": "Classique - l'ancien moteur",
        "val.accent_matcher.oklab": "Perceptuel - comment les "
            "couleurs apparaissent (recommandé)",
        "val.capture_backend.auto": "Automatique - le plus rapide "
            "avec repli sûr",
        "val.capture_backend.dxcam": "Desktop Duplication - le plus "
            "rapide sur la plupart des PC",
        "val.capture_backend.mss": "Compatible - marche toujours "
            "(Bureau à distance, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "expérimental",
        "val.follow_learn.accent": "Seulement les éléments de ma "
            "couleur",
        "val.follow_learn.any": "Chaque accrochage réussi",
        "val.mouse2_action.1": "Effacer la tâche de suivi en cours",
        "val.mouse2_action.2": "Suivre la dernière couleur accrochée",
        "val.mouse2_action.3": "Prendre la couleur sous le curseur, "
            "puis la suivre",
        "val.mouse2_action.4": "Ne rien faire",
        "val.mouse2_hold_action.1": "Effacer la tâche de suivi en "
            "cours",
        "val.mouse2_hold_action.2": "Suivre la dernière couleur "
            "accrochée",
        "val.mouse2_hold_action.3": "Prendre la couleur sous le "
            "curseur, puis la suivre",
        "val.mouse2_hold_action.4": "Ne rien faire",
        "word.off": "Non",
        "word.on": "Oui",
    },
    "pl": {
        "btn.apply": "Zastosuj",
        "btn.export": "Eksportuj ustawienia",
        "btn.import": "Importuj ustawienia",
        "btn.language": "Język: %s",
        "btn.launch": "Uruchom",
        "btn.logout": "Wyloguj",
        "btn.pause": "Pauza",
        "btn.restore": "Przywróć domyślne",
        "col.accent": "Akcent",
        "col.add_pref": "Dodaj do preferowanych",
        "col.add_ref": "Dodaj do odrzuconych",
        "col.chip_desc": "rgb(%d, %d, %d) w %s - kliknij pole, aby "
            "usunąć ten kolor.",
        "col.chip_off": "%s nie zawiera kolorów - przekreślone pole "
            "oznacza wyłączone. Wybierz kolor poniżej i naciśnij "
            "pasujący przycisk dodawania.",
        "col.exclude": "Wykluczenie",
        "col.pick": "Pobierz kolor z ekranu",
        "col.rgb.desc": "Trzy pola pokazują kolor, który właśnie "
            "jest w mikserze: pierwsze świeci tym mocniej, im więcej "
            "ma czerwieni, drugie zieleni, trzecie błękitu - jaśniej "
            "znaczy więcej. Wiersz podąża za mikserem, gotowymi "
            "tonami i przyciskami z ekranu; nie da się w nim pisać.",
        "col.rgb.name": "Bieżąca wartość RGB",
        "col.suggest": "Zasugeruj kolory z ekranu",
        "desc.accent_boost": "Jak bardzo Twój kolor podbija element "
            "(0-3). Podnieś do 1,5-2, gdy nadal wygrywa zły element.",
        "desc.accent_coherent": "Twój kolor musi tworzyć spójną "
            "plamę, by się liczyć - rozproszone plamki rasteru czy "
            "kompresji nigdy nie kwalifikują elementu, nie "
            "wzmacniają go ani nie wkładają na listę nigdy "
            "nieklikalną.",
        "desc.accent_color": "Kolor, który Snappy AI ma preferować, "
            "pokazany jako pola kolorów po prawej. Wybierz kolor "
            "poniżej i naciśnij «Dodaj do preferowanych», aby go "
            "dodać - najwyżej piętnaście pól; kliknięcie pola znów "
            "usuwa ten kolor. Elementy zawierające jeden z nich "
            "wygrywają remisy. Pusta lista pokazuje przekreślone "
            "pole i wyłącza ustawienie.",
        "desc.accent_matcher": "Jak porównywane są kolory. "
            "Percepcyjny porządkuje według tego, jak kolory naprawdę "
            "wyglądają i jest zalecany; klasyczny to starszy silnik "
            "do porównań.",
        "desc.accent_only": "Wspomagane są tylko elementy "
            "zawierające Twój kolor; kliknięcia gdzie indziej idą "
            "nietknięte do Windows.",
        "desc.accent_soft": "0-100: jak bardzo jaśniejsze, "
            "ciemniejsze lub wyblakłe wersje Twojego koloru wciąż "
            "się liczą. 0 = tylko dokładne odcienie.",
        "desc.accent_tolerance": "Jak blisko musi być kolor, by się "
            "liczył (4-90). Mniej = surowiej.",
        "desc.accent_variants": "Jaśniejsze i ciemniejsze kopie "
            "Twojego koloru też się liczą, by stany najechania, "
            "wciśnięcia i przygaszenia obowiązywały bez poszerzania "
            "tolerancji odcienia. Tylko jasność - zły odcień nigdy "
            "się nie prześliźnie.",
        "desc.adaptive_threshold": "Ciemne motywy i wyblakłe "
            "dokumenty same obniżają swój próg wykrywania, więc "
            "blade elementy też są znajdowane. Zalecane wł.",
        "desc.auto_click": "Włączone: program sam klika co 0,1 sekundy w najlepszy element "
            "obserwowanego obszaru, przedkładając kontrast. Ustawiony kolor "
            "akcentu oznacza, że kwalifikują się tylko kolorowe elementy; bez "
            "koloru klikane są wyłącznie bardzo wyraziste. Nigdy dwa razy w tym "
            "samym miejscu ani we własnych oknach.",
        "desc.auto_click_interval": "Jak często ekran jest "
            "sprawdzany pod kątem Twojego koloru (0,5-60). Wolna "
            "liczba to bezpieczna: 2-5 pasuje do obserwowanego okna "
            "dialogowego.",
        "desc.auto_click_max_clicks": "Ile razy może kliknąć samo po "
            "uruchomieniu (1-200). Na limicie zatrzymuje się i "
            "melduje, więc zła konfiguracja nie wymknie się.",
        "desc.auto_click_min_contrast": "W tej samej skali co "
            "»Minimalna wyrazistość krawędzi«. Zacznij od wartości "
            "domyślnej i podnieś, jeśli klika źle: liczyć się będą "
            "tylko mocne, wyraźne elementy.",
        "desc.auto_click_radius": "Autoklik szuka wokół środka "
            "ekranu (40-600 px). Szerzej w pełnym oknie; węziej, by "
            "widział tylko ten jeden kontroler na środku.",
        "desc.auto_click_repeat_px": "Po autokliku cel w tylu "
            "pikselach zostaje w spokoju (0-400). Bez tego przycisk "
            "stojący na ekranie byłby klikany w kółko.",
        "desc.auto_click_settle_ms": "Kursor odpoczywa tak na celu "
            "(0-2000 ms) przed klikiem, by program najpierw zobaczył "
            "podświetlenie. 120 pasuje do większości okien.",
        "desc.block_bound_keys": "Wył. (domyślnie): skrót bez "
            "Ctrl/Alt/Shift - jak 1 lub V - działa w każdym "
            "programie I nadal pisze, więc w środku zdania też "
            "wyzwoli akcję. Wł.: akcja nadal działa wszędzie, ale "
            "klawisz nie pisze.",
        "desc.capture_backend": "Jak fotografowany jest ekran. "
            "Automatycznie używa metody zgodnej, która widzi prawie wszystkie okna; "
            "Kompatybilny działa zawsze, także w Pulpicie zdalnym i "
            "maszynach wirtualnych. Obowiązuje po ponownym "
            "uruchomieniu.",
        "desc.color_adapt": "Każdy element jest balansowany bieli o "
            "własne tło przed porównaniem, by nocne światło i "
            "zabarwienia motywu przestały wypychać Twój kolor z "
            "tolerancji. Wyłączaj tylko do porównania z "
            "niedostosowanym porównywaczem.",
        "desc.contrast_threshold": "Niżej znajduje bledsze elementy "
            "(i więcej szumu); wyżej wymaga wyrazistszych krawędzi.",
        "desc.default": "Najedź na nazwę ustawienia, aby zobaczyć, "
            "co robi.",
        "desc.exclude_color": "Elementy z tymi kolorami nigdy nie są "
            "wspomagane: kliknięcia w nie idą prosto do Windows, w "
            "obu trybach. Pokazane jako pola kolorów po prawej - "
            "wybierz kolor poniżej i naciśnij «Dodaj do "
            "odrzuconych», aby dodać jeden (najwyżej piętnaście); "
            "kliknięcie pola go usuwa. Pusta lista pokazuje "
            "przekreślone pole i wyłącza ustawienie.",
        "desc.follow_boost": "Jak mocno zapamiętany element wygrywa "
            "remisy: 100% może świeżo podwoić jego wynik, 25% to "
            "lekkie pchnięcie.",
        "desc.follow_enabled": "Po udanym przyciągnięciu podobne "
            "elementy lub elementy w tym samym miejscu wygrywają "
            "przez chwilę - wygodne przy suwakach i powtarzanych "
            "kliknięciach jednego przycisku.",
        "desc.follow_learn": "Tylko elementy w moim kolorze: "
            "pudłowanie gdzie indziej nie przekieruje pamięci. Każde "
            "udane przyciągnięcie: stare, ufne zachowanie.",
        "desc.follow_seconds": "Sekundy, przez które zapamiętany "
            "element pozostaje preferowany po ostatnim udanym "
            "przyciągnięciu (1-120).",
        "desc.glide_ms": "0 (domyślnie) skacze od razu - "
            "najszybciej. 40-120 płynie, byś widział ruch; własny "
            "ruch myszy przerywa płynięcie.",
        "desc.hold_follow": "Dopóki trzymasz lewy przycisk tuż po "
            "przyciągnięciu - lub naciśniesz ponownie na "
            "zapamiętanym elemencie - kursor zostaje na kolorze tego "
            "elementu; to uspokaja przeciąganie np. suwaków. "
            "Naciśnięcia gdzie indziej nie są ruszane.",
        "desc.key_launch": "Format: ctrl+l, f5, space, ctrl+alt+1 "
            "... Modyfikatory: ctrl, alt, shift, win. Obowiązuje po "
            "Zastosuj.",
        "desc.key_mode1": "Oddzielone przecinkami, np. '1, f1, "
            "ctrl+f1, v'. Co robi tryb klasyczny, wyjaśnia zakładka "
            "Skróty klawiszowe.",
        "desc.key_mode2": "Oddzielone przecinkami, np. '2, f2, "
            "ctrl+f2, b'. Co robi tryb prowadzenia, wyjaśnia "
            "zakładka Skróty klawiszowe.",
        "desc.key_pause": "Mysz i klawiatura znów są w pełni Twoje, "
            "do czasu uruchomienia.",
        "desc.key_play": "Odtwarza nagranie wybrane na liście Makr, "
            "a gdy nic nie wybrano - najnowsze. Przy nagraniu "
            "powtarzalnym zatrzymuje je.",
        "desc.key_play_n": "Odtwarza nagranie #%d z numerowanej "
            "listy na zakładce Makra, według pozycji. Gdy lista jest "
            "krótsza, nic się nie dzieje.",
        "desc.key_record": "Przechwytuje wszystko, co robisz - każdy "
            "klawisz, każde kliknięcie myszy i każdy ruch kursora - "
            "a Twój wkład nadal dociera do programów, dopóki skrót "
            "stop nie zapisze go na liście Makr. Uzbrojone tylko "
            "podczas pracy.",
        "desc.key_record_stop": "Zatrzymuje nagrywanie, zapisuje "
            "sekwencję na liście Makr i zatrzymuje trwające "
            "odtwarzanie.",
        "desc.luminance_norm": "Krawędzie są oceniane względem "
            "jasności otoczenia, więc ciemne motywy działają jak "
            "jasne. Zalecane wł.",
        "desc.macro_action": "Kombinacja wciskana za Ciebie przy "
            "każdym naciśnięciu wyzwalacza (jedno naciśnięcie = "
            "jedna kombinacja): 'ctrl+c', 'ctrl+shift+s', 'space', "
            "'f5' ... Puste = makro wył.",
        "desc.macro_key": "Klawisz, który OZNACZA makro zamiast "
            "pisać: 'b', 'f7', 'ctrl+b' ... Podczas pracy jedno "
            "naciśnięcie wysyła kombinację obok dokładnie raz, a sam "
            "klawisz nie trafia do programów. W pauzie pisze "
            "normalnie. Puste = makro wył.",
        "desc.max_area": "Większe plamki są ignorowane - zwykle całe "
            "okna lub tapeta, nie elementy do klikania.",
        "desc.max_dim": "Elementy szersze lub wyższe niż to są "
            "ignorowane; elementy przy krawędzi ekranu, jak suwaki, "
            "dostają podwójnie.",
        "desc.merge_distance": "Kawałki bliższe niż to (przerwany "
            "obrys, ikona obok etykiety) stają się jednym elementem. "
            "Dwa kompletne elementy nigdy nie są sklejane.",
        "desc.min_area": "Mniejsze plamki są ignorowane jako śmieci, "
            "chyba że skleją się z większym elementem.",
        "desc.min_contrast": "Element musi być co najmniej tak "
            "wyrazisty, by w ogóle dało się w niego kliknąć. "
            "Wartości poniżej 28 liczą się jako 28: wbudowany próg "
            "jakości nie pozwala, by szum dał się klikać.",
        "desc.motion_3d": "Śledzi ruchome elementy pozycją I "
            "rozmiarem zamiast prostego dopasowania: pojedyncze złe "
            "skany są ignorowane zamiast oślepiać śledzenie, zakręty "
            "są prowadzone, a nagły skok rozmiaru restartuje tor "
            "(skaner złapał inny element). Te same progi prędkości, "
            "ten sam limit 80 px - zmienia się tylko spryt. Działa "
            "samodzielnie.",
        "desc.motion_lead_ms": "Milisekundy ruchu, o które "
            "wyprzedzać ruchomy element (0-300): 40-80 dla wolnego "
            "przewijania, 100-150 dla szybkich pasków. Maks. 80 px, "
            "wyłączone przy wolnym lub zmieniającym kierunek ruchu.",
        "desc.motion_predict": "Dla elementów ruszających się "
            "podczas klikania (przewijane listy, paski wideo) celuje "
            "nieco naprzód, by kliknienie trafiło w element. "
            "Elementy nieruchome bez zmian.",
        "desc.mouse2_action": "Co KRÓTKI prawy klik robi DODATKOWO - "
            "sam prawy klik zawsze zachowuje normalną funkcję "
            "Windows. Domyślnie: nic.",
        "desc.mouse2_hold_action": "Te same możliwości, wyzwalane "
            "gdy PRZYTRZYMASZ prawy przycisk około pół sekundy "
            "zamiast kliknąć. Naciśnięcie to albo klik, albo "
            "trzymanie, nigdy oba. Domyślnie: nic.",
        "desc.on_target_dist": "Jeśli Twój klik trafia w tę liczbę "
            "pikseli od środka elementu, nic się nie rusza - "
            "trafiłeś.",
        "desc.radius": "Zasięg szukania w pikselach (40-400). "
            "Większy, gdy нужный element jest tuż poza zasięgiem; "
            "mniejszy, gdy wygrywa zły sąsiad.",
        "desc.rapid_click_snap": "Wył. (domyślnie): podczas "
            "przetwarzania kliknięcia kolejne idą do Windows. Wł.: "
            "każde lewe kliknięcie jest wspomagane.",
        "desc.snap_offset_x": "Przesuwa punkt kliknięcia w bok od "
            "środka elementu (-200 do 200, ujemne w lewo). Dla "
            "kontrolki o martwym środku - dzielony przycisk, suwak - "
            "ustaw klik na żywe miejsce raz zamiast walczyć przy "
            "każdym snapie.",
        "desc.snap_offset_y": "Przesuwa punkt kliknięcia w pionie od "
            "środka elementu (-200 do 200, ujemne w górę). Jak "
            "przesunięcie boczne: ląduj na żywej części kontrolki.",
        "desc.stall_pause_seconds": "Jeśli skan kiedyś się zatnie, "
            "asysta pauzuje na ten czas, a trzymany klik wraca do "
            "Ciebie.",
        "desc.watcher_seconds": "W trybie klasycznym drugie "
            "przyciągnięcie blisko tego samego miejsca w tym czasie "
            "staje się podwójnym kliknięciem elementu.",
        "ent.cancel_line": "aktywna do %s - NIE odnowi się",
        "ent.canceled_line": "subskrypcja zakończona%s",
        "ent.expired_line": "wygasła %s - odnów na Stripe",
        "ent.past_due_line": "płatność nieudana - napraw kartę w "
            "mailu od Stripe; dostęp wróci, gdy faktura się opłaci",
        "ent.plan": " (%s)",
        "ent.refunded_line": "zwrócona / obciążenie cofnięte - "
            "aktywacja unieważniona",
        "ent.st.active": "aktywna",
        "ent.st.canceled": "zakończona",
        "ent.st.canceling": "aktywna, ale kończy się",
        "ent.st.grant": "grant wsparcia",
        "ent.st.past_due": "PŁATNOŚĆ NIEUDANA",
        "ent.st.refunded": "zwrócona / obciążenie cofnięte",
        "ent.st.trial": "test",
        "ent.st.unsubscribed": "brak subskrypcji",
        "ent.until": " do %s",
        "err.auth_unreachable": "Serwer uwierzytelniania Snappy AI "
            "jest nieosiągalny:\n%s\n\nSnappy AI działa tylko z żywą "
            "odpowiedzią z niego.\nPonowić?",
        "err.start_fail": "Snappy AI nie mógł wystartować.\nUruchom "
            "z --console, aby zobaczyć szczegóły.",
        "gate.btn.monthly": "Subskrypcja miesięczna za 9,99€",
        "gate.btn.trial": "Zakup testowy za 1,99€",
        "gate.head.canceled": "Ta subskrypcja została anulowana - "
            "załóż nową na Stripe, by kontynuować.",
        "gate.head.canceling": "Twoja subskrypcja kończy się %s - do "
            "tego czasu działa, potem to logowanie znów się "
            "zablokuje, chyba że odnowisz.",
        "gate.head.email_mismatch": "Płatność poszła z innego "
            "e-maila niż Twoje konto Discord. Subskrypcje działają "
            "tylko na e-mailu Discord pokazanym niżej - zapłać z "
            "niego lub skontaktuj się ze wsparciem.",
        "gate.head.expired": "Subskrypcja tego logowania wygasła - "
            "odnów ją na Stripe, by kontynuować.",
        "gate.head.none": "Jesteś zalogowany, ale to logowanie nie "
            "ma aktywnej subskrypcji. Zapłać TYM e-mailem Discord - "
            "zakup na innym adresie nie aktywuje go.",
        "gate.head.past_due": "Ostatnia płatność subskrypcji nie "
            "przeszła - napraw ją na Stripe, by odblokować to "
            "logowanie.",
        "gate.head.refunded": "Ten zakup zwrócono lub obciążenie "
            "cofnięto, więc aktywację unieważniono. Nowa subskrypcja "
            "na tym e-mail Discord aktywuje ponownie.",
        "gate.head.shared": "To konto działa TERAZ na INNYM "
            "komputerze. Snappy AI pozostaje wyłączone, dopóki to "
            "samo konto Discord działa w dwóch miejscach - zamknij "
            "drugą sesję i sprawdź ponownie. Współdzielone "
            "subskrypcje podnoszą ceny; prosimy, nie rób tego.",
        "gate.msg.active": "Subskrypcja aktywna - Snappy AI "
            "startuje...",
        "gate.msg.checking": "Sprawdzanie z serwerem...",
        "gate.msg.no_link": "Ten link płatności nie jest "
            "skonfigurowany w tej wersji.",
        "gate.msg.open_fail": "Nie udało się otworzyć przeglądarki. "
            "Otwórz ten link ręcznie:\n%s",
        "gate.msg.open_ok": "Stripe jest otwarty w przeglądarce - zapłać tam. To okno samo zauważy płatność i uruchomi silnik.",
        "gate.msg.session_gone": "Sesja zniknęła - zaloguj się "
            "ponownie.",
        "gate.msg.still_none": "Nadal brak aktywnej subskrypcji dla "
            "tego logowania.",
        "gate.msg.still_shared": "Nadal używane na innym komputerze "
            "- zamknij tamtą sesję i sprawdź ponownie.",
        "gate.msg.unreachable": "Serwer uwierzytelniania "
            "nieosiągalny: %s",
        "gate.note": "Silnik rusza, gdy subskrypcja jest aktywna - "
            "to okno samo sprawdza co 30 sekund. Zamknięcie wraca do "
            "logowania.",
        "gate.prices": "Test 2-dniowy: 1,99€ (jednorazowo)  -  "
            "subskrypcja: 9,99€ / mies.\nAktywacja trafia do ~10 "
            "minut po płatności; odnowienia reaktywują to samo "
            "logowanie automatycznie.",
        "gate.title": "%s - Subskrypcja%s",
        "hdr.build": "kompilacja %s",
        "help.1.b": "Snappy AI patrzy na ekran wokół kursora, "
            "znajduje pobliskie zwarte, podobne do elementów rzeczy "
            "- przyciski, ikony, linki - i wybiera najlepszą: "
            "wyraziste krawędzie, sensowny rozmiar i bliskość "
            "kursora wygrywają. Twój kolor, lista "
            "nigdy-nie-klikalnych i pamięć ostatniego kliknięcia "
            "mogą przechylić wybór. Kursor celuje potem w środek "
            "elementu, nie w róg jego ramki.",
        "help.1.t": "Co się dzieje przy kliknięciu",
        "help.10.b": "1. Czy uruchomione? Pauza znaczy, że nic nie "
            "jest przechwytywane - 'Skrót: rozpocznij asystę' "
            "(domyślnie Ctrl+L) to jedyne wł./wył.  2. Przytrzymaj "
            "Shift przy jednym kliknięciu, by sprawdzić, czy to "
            "asysta była problemem.  3. Wygrywa zły element: "
            "zmniejsz 'Jak daleko od kursora szukać', potem ustaw "
            "'Mój kolor' lub podnieś 'Siłę przewagi koloru'.  4. Nic "
            "nie znaleziono: obniż 'Jak blada może być krawędź' i "
            "'Minimalną wyrazistość krawędzi', podnieś 'Największą "
            "szerokość lub wysokość' albo 'Sklejaj pobliskie "
            "kawałki'.  5. Coś nigdy nie może być wspomagane: włóż "
            "jego kolor w jego kolor w 'Kolor(y) nigdy nieklikalne'. "
            " 6. Nadal źle: zgłoś wsparciu, co kliknąłeś i czego "
            "oczekiwałeś, i dołącz plik dziennika, który Snappy AI "
            "zapisuje w swoim folderze danych.",
        "help.10.t": "Gdy coś nie gra, sprawdzaj w tej kolejności",
        "help.2.b": "Tryb prowadzenia (domyślny) nie zjada "
            "kliknięcia: trafia ono do programu, a po puszczeniu "
            "kursor jedzie na najbliższy czysty element. Tryb "
            "klasyczny jest silniejszy: chybiący klik blisko "
            "elementu jest łapany, kursor przyciąga się i Snappy AI "
            "klika za Ciebie. 'Jak daleko od kursora szukać' "
            "wyznacza krąg - powiększ, gdy element jest tuż poza "
            "zasięgiem, zmniejsz, gdy wygrywa zły sąsiad. Shift "
            "omija jedno kliknięcie w obu trybach.",
        "help.2.t": "Najpierw: tryb i zasięg szukania",
        "help.3.b": "Na zakładce Przetwarzanie 'Jak blada może być "
            "krawędź' i 'Minimalna wyrazistość krawędzi' decydują, "
            "które krawędzie się liczą: niżej znajdzie bledsze, "
            "wyżej odrzuci szum. 'Najmniejszy rozmiar elementu', "
            "'Największa powierzchnia elementu' i 'Największa "
            "szerokość lub wysokość' odsiewają śmieci i całe okna. "
            "'Sklejaj pobliskie kawałki' łączy przerwany obrys lub "
            "ikonę obok etykiety w jeden element. Na zakładce Asysta "
            "'Automatyczne dopasowanie do przyciemnionych ekranów' i "
            "'Oceniaj krawędzie wg względnej jasności' sprawiają, że "
            "ciemne motywy działają jak jasne - zostaw włączone.",
        "help.3.t": "Nic nie znaleziono - albo za dużo",
        "help.4.b": "Na zakładce Kolory 'Mój kolor (kolory)' to "
            "kolor preferowany, a 'Kolor(y) nigdy nieklikalne' są "
            "absolutne: takie elementy nigdy nie są wspomagane. "
            "'Wspomagaj tylko mój kolor' ogranicza asystę do "
            "pasujących elementów. Na zakładce Przetwarzanie "
            "'Surowość dopasowania koloru' mówi, jak blisko musi być "
            "odcień, 'Akceptuj podobne odcienie' pozwala jaśniejszym "
            "lub wyblakłym liczyć się częściowo, a 'Siła przewagi "
            "koloru' określa, jak bardzo Twój kolor podbija element "
            "- podnieś, gdy nadal wygrywa zły.",
        "help.4.t": "Praca z kolorami",
        "help.5.b": "'Pamiętaj ostatnio kliknięty element' nadal "
            "preferuje element, na którym wylądowało Twoje ostatnie "
            "udane kliknięcie, przez 'Jak długo pamiętać' sekund - "
            "to czyni suwaki i przyciski okien przyjemnymi. 'Siła "
            "pamięci' mówi, jak mocno wygrywa, a 'Czego pamięć może "
            "się uczyć' chroni ją: przy 'Tylko elementy w moim "
            "kolorze' pudłowanie nie przekieruje pamięci. 'Trzymanie "
            "przycisku trzyma kursor na elemencie' uspokaja "
            "przeciąganie, a akcje prawego przycisku na zakładce "
            "Eksperymentalne mogą śledzić pamięć myszą lub ją "
            "czyścić.",
        "help.5.t": "Powtarzane kliknięcia jednego przycisku",
        "help.6.b": "'Wyprzedzaj ruchome elementy' mierzy, jak "
            "szybko wędruje wybrany element i celuje o 'Jak bardzo "
            "wyprzedzać' milisekund naprzód, by kliknięcie "
            "wylądowało na przewijanej liście lub pasku wideo, nie "
            "za nimi. Wyprzedzenie ma górny limit 80 pikseli i "
            "wyłącza się przy elementach stojących lub skręcających.",
        "help.6.t": "Klikanie ruchomych rzeczy",
        "help.7.b": "'Animuj ruch kursora' = 0 skacze od razu; "
            "40-120 płynie, byś widział, a własny ruch myszy "
            "przerywa płynięcie. 'Okno podwójnego kliknięcia' "
            "zamienia w trybie klasycznym drugie przyciągnięcie "
            "blisko tego samego miejsca w podwójne kliknięcie. "
            "'Wspomagaj każde kliknięcie szybkiej serii' wspomaga "
            "każde kliknięcie serii, nie tylko pierwsze. 'Pauza po "
            "zacięciu' to zawór bezpieczeństwa oddający trzymany "
            "klik, gdy skan się zatnie.",
        "help.7.t": "Jak czują się kliknięcia",
        "help.8.b": "Zakładka Skróty wyjaśnia dwa tryby i proces "
            "nagrywania. W skrócie: skróty z Ctrl, Alt, Shift lub "
            "Win są zarezerwowane systemowo; pojedyncze klawisze "
            "działają wszędzie i nadal wpisują. Makro zamienia jedno "
            "zablokowane naciśnięcie w całą kombinację. Nagrania "
            "przechwytują Twój rzeczywisty wkład - każdy klawisz, "
            "kliknięcie myszy i ruch kursora - i odtwarzają go z "
            "zakładki Makra, każde z własnym przełącznikiem raz lub "
            "powtarzaj do zatrzymania.",
        "help.8.t": "Klawisze, makra i nagrania",
        "help.9.b": "Przycisk Język obok 'Eksportuj ustawienia' - "
            "także w oknie logowania i oknie subskrypcji - przełącza "
            "cały interfejs od razu, bez restartu, i pamięta wybór. "
            "Języki wciąż tłumaczone nie są oferowane, więc każdy "
            "wybrany jest kompletny.",
        "help.9.t": "Język",
        "help.sub": "Każde ustawienie pod nazwą widzianą na jego "
            "zakładce, w kolejności, w jakiej będzie potrzebne. "
            "Najedź na nazwę, by zobaczyć krótki opis; ta strona to "
            "długa forma.",
        "help.tail": "Ustawienia obowiązują po naciśnięciu Zastosuj. "
            "Plik config.ini obok programu nadpisuje config.json. Ta "
            "strona wyjaśnia, niczego nie ustawia.",
        "help.title": "Strajanie Snappy AI prostymi słowami",
        "kb.keys.b": "Skrót z Ctrl, Alt, Shift lub Win jest "
            "zarezerwowany systemowo: widzi go tylko Snappy AI. "
            "Pojedynczy klawisz (jak 1 lub 2) działa w każdym "
            "programie I nadal pisze - cena: naciśnięcie go w środku "
            "zdania też wyzwoli akcję. Klasyczne zachowanie daje "
            "'Skróty jednogombikowe pochłaniają klawisz' na zakładce "
            "Asysta. Makra idą dalej: podczas pracy klawisz "
            "wyzwalacza jest połykany, a kombinacja obok wysyłana "
            "dokładnie raz.",
        "kb.keys.t": "Pojedyncze klawisze a kombinacje",
        "kb.mode.b": "Tryb prowadzenia (domyślny, skrót 2): Twój "
            "klik zawsze dociera do programu nietknięty; po "
            "puszczeniu przycisku kursor jedzie na najbliższy czysty "
            "element, więc następny klik zaczyna tam. Nic nigdy nie "
            "jest połykane - najbezpieczniejszy tryb.  Tryb "
            "klasyczny (skrót 1): jeśli klikniesz blisko elementu, "
            "ten chybiący klik jest łapany, kursor przyciąga się do "
            "elementu i Snappy AI klika za Ciebie; jeśli nic nie ma "
            "blisko, klik wraca nietknięty.  W obu trybach "
            "przytrzymanie Shift podczas klikania omija asystę dla "
            "tego jednego kliknięcia.",
        "kb.mode.t": "Co robią dwa tryby",
        "kb.rec.b": "Podczas pracy naciśnij skrót rozpoczęcia "
            "nagrywania (domyślnie Ctrl+Alt+R): każdy naciśnięty "
            "klawisz, każdy przycisk myszy i każdy ruch kursora jest "
            "przechwytywany I nadal dociera do Twoich programów, "
            "więc możesz pracować normalnie podczas nagrywania. "
            "Naciśnij skrót stop (Ctrl+Alt+S), aby zapisać nagranie "
            "na liście w zakładce Makra - mieści się tam pięć "
            "nagrań. Kliknij nagranie, aby je wybrać, użyj «Zmień "
            "nazwę» lub «Eksportuj» i ustaw własny przełącznik "
            "«Powtarzaj do zatrzymania». Skrót odtwarzania "
            "(Ctrl+Alt+M) odtwarza wybrane tam nagranie; Ctrl+1 do "
            "Ctrl+5 odtwarzają według pozycji na liście. Wstrzymane: "
            "nic nie jest nagrywane ani wstrzykiwane - Twój wkład "
            "należy wyłącznie do Ciebie.",
        "kb.rec.t": "Jak nagrać i odtworzyć własne klawisze i ruchy "
            "myszy",
        "lang.close": "Zamknij",
        "lang.coverage": "%d%% przetłumaczone",
        "lang.current": "Bieżący: %s",
        "lang.progress": "W trakcie tłumaczenia, pojawi się gdy "
            "będzie gotowe: %s",
        "lang.prompt": "Zmiana działa od razu - okno zostaje "
            "otwarte, można wypróbować kilka.",
        "lang.title": "Język",
        "lbl.accent_boost": "Siła przewagi koloru",
        "lbl.accent_coherent": "Ignoruj rozproszone plamki koloru",
        "lbl.accent_color": "Mój kolor (kolory)",
        "lbl.accent_matcher": "Silnik dopasowania kolorów",
        "lbl.accent_only": "Wspomagaj tylko mój kolor",
        "lbl.accent_soft": "Akceptuj podobne odcienie",
        "lbl.accent_tolerance": "Surowość dopasowania koloru",
        "lbl.accent_variants": "Jasne i ciemne stany mojego koloru",
        "lbl.adaptive_threshold": "Automatyczne dopasowanie do "
            "przyciemnionych ekranów",
        "lbl.auto_click": "Klikna elementy samoistnie",
        "lbl.auto_click_interval": "Sekundy między kliknięciami auto",
        "lbl.auto_click_max_clicks": "Limit kliknięć auto na sesję",
        "lbl.auto_click_min_contrast": "Jak wyraźny musi być cel "
            "auto",
        "lbl.auto_click_radius": "Szukać od środka ekranu",
        "lbl.auto_click_repeat_px": "Nie klikaj ponownie tego samego "
            "miejsca",
        "lbl.auto_click_settle_ms": "Pauza przed kliknięciem auto",
        "lbl.block_bound_keys": "Skróty jednogombikowe pochłaniają "
            "klawisz",
        "lbl.capture_backend": "Silnik przechwytywania ekranu",
        "lbl.color_adapt": "Dostosuj do światła ekranu",
        "lbl.contrast_threshold": "Jak blada może być krawędź",
        "lbl.exclude_color": "Kolor(y) nigdy nieklikalne",
        "lbl.follow_boost": "Siła pamięci",
        "lbl.follow_enabled": "Pamiętaj ostatnio kliknięty element",
        "lbl.follow_learn": "Czego pamięć może się uczyć",
        "lbl.follow_seconds": "Jak długo pamiętać",
        "lbl.glide_ms": "Animuj ruch kursora",
        "lbl.hold_follow": "Trzymanie przycisku trzyma kursor na "
            "elemencie",
        "lbl.key_launch": "Skrót: rozpocznij asystę",
        "lbl.key_mode1": "Skrót: tryb klasyczny (do 4 klawiszy)",
        "lbl.key_mode2": "Skrót: tryb prowadzenia (do 4 klawiszy)",
        "lbl.key_pause": "Skrót: pauza",
        "lbl.key_play": "Skrót: odtwórz wybrane nagranie",
        "lbl.key_play_n": "Skrót: odtwórz nagranie #%d",
        "lbl.key_record": "Skrót: rozpocznij nagrywanie",
        "lbl.key_record_stop": "Skrót: zatrzymaj i zapisz nagranie",
        "lbl.luminance_norm": "Oceniaj krawędzie wg względnej "
            "jasności",
        "lbl.macro_action": "Makro %d: wysyła zamiast tego",
        "lbl.macro_key": "Makro %d: naciśnij ten klawisz",
        "lbl.max_area": "Największa powierzchnia elementu",
        "lbl.max_dim": "Największa szerokość lub wysokość elementu",
        "lbl.merge_distance": "Sklejaj pobliskie kawałki",
        "lbl.min_area": "Najmniejszy rozmiar elementu",
        "lbl.min_contrast": "Minimalna wyrazistość krawędzi",
        "lbl.motion_3d": "Inteligentniejsze śledzenie w ruchu",
        "lbl.motion_lead_ms": "Jak bardzo wyprzedzać",
        "lbl.motion_predict": "Wyprzedzaj ruchome elementy",
        "lbl.watch_center_only": "Obserwuj tylko środek ekranu",
        "desc.watch_center_only": "Asystent obserwuje wyłącznie stały kwadrat w środku ekranu "
            "(rozmiar = dystans wyszukiwania, domyślnie 150×150 px), "
            "niezależnie od położenia kursora. Kliknięcia poza tym kwadratem "
            "pozostają bez zmian.",
        "lbl.center_follow": "Ekran podąża za celem",
        "desc.center_follow": "Przy włączonym «Obserwuj tylko środek ekranu»: po przyciągnięciu "
            "elementu asystent przesuwa ekran, aby utrzymać go w środku, "
            "zwłaszcza na przewijanych płaszczyznach. Przesuń ekran "
            "samodzielnie, aby zwolnić podążanie.",
        "lbl.input_backend": "Metoda wprowadzania",
        "desc.input_backend": "Wstrzykiwanie Windows (domyślne) działa wszędzie. Interception "
            "wysyła przez sterownik i gry rozpoznają je jako prawdziwą mysz; "
            "wymaga zainstalowanego sterownika Interception i pliku "
            "interception.dll obok programu; w przeciwnym razie automatycznie "
            "używa wstrzykiwania Windows.",
        "val.input_backend.win32": "Wstrzykiwanie Windows",
        "val.input_backend.interception": "Interception (sterownik)",
        "lbl.mouse2_action": "Dodatkowa akcja prawego przycisku",
        "lbl.mouse2_hold_action": "Akcja przytrzymania prawego "
            "przycisku",
        "lbl.on_target_dist": "Dystans „już trafiony”",
        "lbl.radius": "Jak daleko od kursora szukać",
        "lbl.rapid_click_snap": "Wspomagaj każde kliknięcie szybkiej "
            "serii",
        "lbl.snap_offset_x": "Punkt kliknięcia: w lewo / w prawo",
        "lbl.snap_offset_y": "Punkt kliknięcia: w górę / w dół",
        "lbl.stall_pause_seconds": "Pauza po zacięciu",
        "lbl.watcher_seconds": "Okno podwójnego kliknięcia",
        "login.failed": "Logowanie %s nie zakończone - spróbuj "
            "ponownie.",
        "login.no_provider": "W tej kopii nie wbudowano dostawcy "
            "logowania.",
        "login.not_configured": "Plik subskrypcji nie jest jeszcze "
            "skonfigurowany w tej wersji.",
        "login.note": "Logowanie otwiera przeglądarkę i samo wraca "
            "do tego okna.",
        "login.provider": "Zaloguj przez %s",
        "login.signedin": "Zalogowano jako %s.",
        "login.sub": "Zaloguj się Discordem - subskrypcja jest "
            "przypisana do tego konta, a płatności muszą używać jego "
            "adresu e-mail. Bez hasła.",
        "login.title": "%s - Logowanie",
        "login.unreachable": "Serwer uwierzytelniania nieosiągalny: "
            "%s",
        "login.waiting": "Czekam na przeglądarkę - dokończ logowanie "
            "%s...",
        "mac.delete": "Usuń",
        "mac.empty": "Brak nagrań - uruchom, naciśnij skrót "
            "nagrywania i pracuj normalnie: każdy klawisz, "
            "kliknięcie i ruch kursora jest przechwytywany.",
        "mac.export": "Eksportuj",
        "mac.import": "Importuj",
        "mac.keys_head": "Makra klawiszowe",
        "mac.loop": "Powtarzaj do zatrzymania",
        "mac.recordings": "Nagrania",
        "mac.rename": "Zmień nazwę",
        "mac.row": "Makro %d",
        "mac.sends": "wysyła",
        "mac.steps": "%d kroków",
        "note.advanced": "Ustawienia odległości i czasu, które "
            "zmieniają odczucie kliknięcia, nie to, co jest "
            "znajdowane. Większość osób nigdy ich nie rusza; "
            "domyślne są przetestowane.",
        "note.assist": "Każdy przełącznik zmieniający zachowanie "
            "podczas pracy. Tryby zmieniają się Twoimi klawiszami "
            "trybów - zakładka Skróty klawiszowe wyjaśnia, co robi "
            "każdy. Asysta zawsze startuje zapauzowana; Uruchom to "
            "jedyne wł./wył. Gdzie silnik patrzy i jak czują się "
            "kliknięcia - w Zaawansowane; co jest elementem - w "
            "Przetwarzanie.",
        "note.colors": "Dwie listy u góry wybierają, jakie kolory "
            "Snappy AI preferuje lub odrzuca. Każda pokazuje swoje "
            "kolory jako pola po prawej, najwyżej piętnaście, a "
            "kliknięcie pola znów usuwa ten kolor; pusta lista "
            "pokazuje przekreślone pole i liczy się jako wyłączona. "
            "«Dodaj do preferowanych» i «Dodaj do odrzuconych» "
            "wkładają kolor stojący w mieszalniku do właściwej "
            "listy. Bieżąca wartość RGB pokazuje trzy pola - każde "
            "szerokości pięciu pól koloru, więc wiersz obejmuje te "
            "same piętnaście pól co wszystko poniżej - świecące tym "
            "mocniej, im więcej czerwieni, zieleni i błękitu ma "
            "kolor w mieszalniku; wiersz podąża za mieszalnikiem i "
            "nie przyjmuje wpisywania. Mieszalnik poniżej miesza "
            "kolor jak program malarski; wszystko obok niego siedzi "
            "po prawej stronie okna, z tym samym odstępem od "
            "krawędzi co ustawienia u góry, i każdy wiersz obejmuje "
            "tę samą szerokość piętnastu pól: wysoka witryna z "
            "narysowanym w środku #kodem, potem piętnaście gotowych "
            "tonów, dwa przyciski dodawania i wiersz ekranu - "
            "«Pobierz kolor z ekranu» bierze pojedynczy kolor pod "
            "kursorem, «Zasugeruj kolory z ekranu» wypełnia "
            "piętnaście własnych pól kolorami znalezionymi wokół "
            "kursora, a kliknięcie jednego wczytuje go do "
            "mieszalnika. Witryna jest wysoka celowo: dzięki temu "
            "pola propozycji kończą się równo z suwakiem koloru po "
            "lewej.",
        "note.experimental": "Wybory silników, każdy ze sprawdzonym "
            "domyślnym. Zmieniaj tylko przy porównywaniu silników, "
            "na nietypowym sprzęcie lub na prośbę wsparcia - silnik "
            "przechwytywania obowiązuje po restarcie.",
        "note.handler": "Co jest klikalnym elementem: jak blada może "
            "być krawędź, jak wyrazista musi być i jak duży lub mały "
            "może być element. Nic nie znaleziono? Poluzuj. Złe "
            "znalezione? Zaostrz albo użyj swojego koloru na "
            "zakładce Kolory.",
        "note.keybindings": "Każdy skrót - a pod spodem, co robią "
            "dwa tryby, jak nagrać własne klawisze i ruchy myszy i "
            "czym pojedynczy klawisz różni się od kombinacji.",
        "note.macros": "Makro zamienia jedno naciśnięcie klawisza w "
            "całą kombinację podczas pracy. Obok makr Twoje "
            "nagrania: do pięciu nazwanych zapisów wszystkiego, co "
            "zrobiłeś - każdy klawisz, kliknięcie myszy i ruch "
            "kursora - odtwarzanych dokładnie tak, jak nagrano. "
            "Kliknij nagranie, aby je wybrać; każdy wiersz ma własny "
            "przełącznik «Powtarzaj do zatrzymania», a «Zmień "
            "nazwę», «Eksportuj», «Importuj» i «Usuń» znajdują się "
            "na dole ramki.",
        "note.macros_keys": "Skróty nagrywania/odtwarzania są na "
            "zakładce Skróty klawiszowe (domyślnie: Ctrl+Alt+R "
            "nagrywanie, Ctrl+Alt+S stop i zapis, Ctrl+Alt+M "
            "odtwarzanie, Ctrl+1..5 odtwarzanie z listy).",
        "online.cancelled": "Uwierzytelnienie Discord zostało "
            "przerwane (lub nieudane). Spróbuj ponownie.",
        "rec.export_fail": "Eksport nieudany: %r",
        "rec.exported": "Wyeksportowano do %s",
        "rec.import_fail": "Import nieudany: %r",
        "rec.imported": "Zaimportowano %d nagrań%s.",
        "rec.imported_none": " (żadne nie było poprawne)",
        "rec.no_sel": "Nic nie wybrano do eksportu.",
        "rec.notfile": "Import nieudany: to nie plik nagrania.",
        "shared.back": "Witaj ponownie - naciśnij Uruchom, gdy "
            "gotowy.",
        "shared.body": "To konto Discord uruchamia Snappy AI na "
            "innym komputerze właśnie teraz.\nAsysta pauzuje tu, "
            "dopóki nie zostanie jedna sesja.\n\nJedna subskrypcja, "
            "jedna maszyna naraz - to trzyma\ncenę nisko i rozwój w "
            "ruchu.",
        "shared.close": "Zamknij",
        "shared.recheck": "Sprawdź ponownie",
        "shared.still": "Nadal używane gdzie indziej - pozostaje "
            "pauza.",
        "shared.title": "Konto używane gdzie indziej",
        "shared.unreachable": "Serwer nieosiągalny - sprawdzimy "
            "ponownie.",
        "st.all_files": "Wszystkie pliki",
        "st.color_added": "Dodano rgb(%d, %d, %d) do %s - Zastosuj "
            "zapisuje.",
        "st.color_already": "rgb(%d, %d, %d) już jest w %s.",
        "st.color_full": "%s ma już 15 kolorów - najpierw kliknij "
            "jedno z pól, aby usunąć kolor.",
        "st.color_removed": "Usunięto rgb(%d, %d, %d) z %s - "
            "Zastosuj zapisuje.",
        "st.delete_confirm": "Usunąć nagranie %r?\nTego nie da się "
            "cofnąć.",
        "st.deleted": "Nagranie usunięte.",
        "st.engine_dead": "Wątek silnika niedostępny - skróty nie "
            "odpowiadają.",
        "st.ent_paused": "Subskrypcja %s - asysta pauzuje. Odnów na "
            "Stripe, potem uruchom ponownie.",
        "st.ent_unreachable": "Sprawdzenie subskrypcji: serwer "
            "nieosiągalny (sesja działa dalej).",
        "st.export_fail": "Eksport nieudany: %r",
        "st.export_rec_title": "Eksportuj nagranie",
        "st.export_title": "Eksport ustawień",
        "st.exported": "Ustawienia wyeksportowane do %s",
        "st.file_rec": "Nagranie Snappy AI",
        "st.file_settings": "Ustawienia Snappy AI",
        "st.follow": "  |  śledzenie %d s temu",
        "st.import_fail": "Import nieudany: %r",
        "st.import_notfile": "Import nieudany: to nie plik ustawień.",
        "st.import_rec_title": "Import nagrań",
        "st.import_title": "Import ustawień",
        "st.imported": "Zaimportowano %d ustawień%s.",
        "st.imported_ignored": ", pominięto: %s",
        "st.ini_over": "Zastosowano, ale config.ini nadpisuje: %s",
        "st.lib_empty": "Lista jest pusta - nie ma czego "
            "eksportować.",
        "st.line": "Wspomoż. %d  |  przepuszcz. %d%s  |  motyw: %s",
        "st.loop_desc": "Styl odtwarzania TEGO nagrania: wył. = gra "
            "raz; wł. = powtarza, dopóki nie naciśniesz ponownie "
            "skrótu odtwarzania. Każde nagranie ma własny "
            "przełącznik, zapisany razem z nagraniem.",
        "st.name_empty": "Nazwa nie może być pusta.",
        "st.pick_err": "Pobranie nieudane: %r",
        "st.pick_fail": "Pobranie nieudane - spróbuj ponownie.",
        "st.pick_ok": "Pobrano rgb(%d, %d, %d) w (%d, %d).",
        "st.pick_wait": "Najedź kursor na kolor - pobranie za 3 s...",
        "st.preset_desc": "Gotowa barwa: %s - kliknij, by wczytać do "
            "miksera.",
        "st.rec_count": "%d z 5 nagrań",
        "st.rec_now": "%r teraz: %s.",
        "st.rec_once": "gra raz",
        "st.rec_playing": "Odtwarzanie %r...",
        "st.rec_playing_loop": "Odtwarzanie %r do zatrzymania",
        "st.rec_recording": "NAGRYWANIE - %s zatrzymuje i zapisuje",
        "st.rec_repeats": "powtarzaj do zatrzymania",
        "st.registered": "Zarejestrowano na: %s    Status: %s",
        "st.rename_prompt": "Nowa nazwa nagrania #%d:",
        "st.renamed": "Zmieniono nazwę nagrania.",
        "st.reset_confirm": "Przywrócić wszystkie ustawienia do "
            "domyślnych?\nKonta zostają; to dotyczy tylko ustawień.",
        "st.rgb_bad": "Najpierw podaj poprawne wartości R/G/B.",
        "st.running": "Działa..",
        "st.saved": "Zapisano i zastosowano.",
        "st.defaults_restored": "Przywrócono ustawienia domyślne.",
        "st.saved_bad": "Zapisano, ale niepoprawne (zostaje stare): "
            "%s",
        "st.select_rec": "Najpierw wybierz nagranie.",
        "st.shared_paused": "KONTO UŻYWANE GDZIE INDZIEJ - asysta "
            "pauzuje; jedna subskrypcja = jedna maszyna.",
        "st.standby": "Gotowość..",
        "st.sug_fail": "Propozycja nieudana: %r",
        "st.sug_loaded": "Propozycja rgb(%d, %d, %d) jest w "
            "mieszalniku - dodaj ją do listy przyciskami powyżej.",
        "st.sug_loaded_desc": "Proponowany kolor interfejsu rgb(%d, "
            "%d, %d) - %d%% obszaru. Kliknij, by wczytać do miksera.",
        "st.sug_none": "Brak propozycji kolorów z tego obszaru.",
        "st.sug_ok": "%d propozycji - kliknij jedną, aby wczytać ją "
            "do mieszalnika.",
        "st.sug_wait": "Wskaż aplikację, w której pracujesz - próbka "
            "za 3 s...",
        "tab.advanced": "Zaawansowane",
        "tab.assist": "Asysta",
        "tab.colors": "Kolory",
        "tab.experimental": "Eksperymentalne",
        "tab.handler": "Przetwarzanie",
        "tab.help": "Pomoc",
        "tab.hotkeys": "Skróty klawiszowe",
        "tab.macros": "Makra",
        "theme.dark": "Ciemny",
        "theme.light": "Jasny",
        "val.accent_matcher.hsv": "Klasyczny - starszy silnik",
        "val.accent_matcher.oklab": "Percepcyjny - jak kolory "
            "wyglądają (zalecany)",
        "val.capture_backend.auto": "Automatycznie - najszybszy z "
            "bezpiecznym zapasem",
        "val.capture_backend.dxcam": "Desktop Duplication - "
            "najszybszy na większości PC",
        "val.capture_backend.mss": "Kompatybilny - działa zawsze "
            "(Pulpit zdalny, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "eksperymentalny",
        "val.follow_learn.accent": "Tylko elementy w moim kolorze",
        "val.follow_learn.any": "Każde udane przyciągnięcie",
        "val.mouse2_action.1": "Wyczyść bieżące zadanie śledzenia",
        "val.mouse2_action.2": "Podążaj za ostatnio złapanym kolorem",
        "val.mouse2_action.3": "Pobierz kolor pod kursorem i podążaj "
            "za nim",
        "val.mouse2_action.4": "Nic nie rób",
        "val.mouse2_hold_action.1": "Wyczyść bieżące zadanie "
            "śledzenia",
        "val.mouse2_hold_action.2": "Podążaj za ostatnio złapanym "
            "kolorem",
        "val.mouse2_hold_action.3": "Pobierz kolor pod kursorem i "
            "podążaj za nim",
        "val.mouse2_hold_action.4": "Nic nie rób",
        "word.off": "Wył.",
        "word.on": "Wł.",
    },
    "ru": {
        "btn.apply": "Применить",
        "btn.export": "Экспорт настроек",
        "btn.import": "Импорт настроек",
        "btn.language": "Язык: %s",
        "btn.launch": "Запуск",
        "btn.logout": "Выйти",
        "btn.pause": "Пауза",
        "btn.restore": "Сбросить по умолчанию",
        "col.accent": "Акцент",
        "col.add_pref": "Добавить в предпочитаемые",
        "col.add_ref": "Добавить в запрещённые",
        "col.chip_desc": "rgb(%d, %d, %d) в %s - кликните по "
            "квадратику, чтобы убрать этот цвет.",
        "col.chip_off": "В %s нет цветов - перечёркнутый квадрат "
            "означает «выкл». Выберите цвет ниже и нажмите "
            "соответствующую кнопку добавления.",
        "col.exclude": "Исключение",
        "col.pick": "Взять цвет с экрана",
        "col.rgb.desc": "Три квадратика показывают цвет, который "
            "сейчас в миксере: первый светится тем ярче, чем больше "
            "в нём красного, второй - зелёного, третий - синего; "
            "ярче значит больше. Строка следует за миксером, "
            "готовыми тонами и экранными кнопками; вводить в неё "
            "нельзя.",
        "col.rgb.name": "Текущее значение RGB",
        "col.suggest": "Предложить цвета с экрана",
        "desc.accent_boost": "Насколько ваш цвет поднимает элемент "
            "(0-3). Поднимите до 1,5-2, если всё же выигрывает не "
            "тот элемент.",
        "desc.accent_coherent": "Ваш цвет должен образовывать "
            "связное пятно, чтобы засчитываться - рассыпанные "
            "вкрапления дизеринга или компрессии никогда не "
            "квалифицируют элемент, не усиливают его и не вносят в "
            "никогда-некликабельный список.",
        "desc.accent_color": "Цвет, который Snappy AI должен "
            "предпочитать, показанный квадратами цвета справа. "
            "Выберите цвет ниже и нажмите «Добавить в "
            "предпочитаемые», чтобы добавить его - не больше "
            "пятнадцати квадратов; щелчок по квадрату снова убирает "
            "этот цвет. Элементы с одним из них выигрывают ничьи. "
            "Пустой список показывает перечёркнутый квадрат и "
            "выключает настройку.",
        "desc.accent_matcher": "Как сравниваются цвета. Перцептивный "
            "ранжирует по тому, как цвета действительно выглядят, и "
            "рекомендован; классический - старый движок для "
            "сравнения.",
        "desc.accent_only": "Помогаются только элементы, содержащие "
            "ваш цвет; клики в другом месте проходят в Windows "
            "нетронутыми.",
        "desc.accent_soft": "0-100: насколько светлые, тёмные или "
            "выцветшие версии вашего цвета всё же считаются. 0 = "
            "только точные оттенки.",
        "desc.accent_tolerance": "Насколько близким должен быть "
            "цвет, чтобы считаться вашим (4-90). Меньше = строже.",
        "desc.accent_variants": "Более светлые и тёмные копии вашего "
            "цвета тоже засчитываются, чтобы состояния наведения, "
            "нажатия и приглушения действовали без расширения "
            "допуска оттенка. Только яркость - неверный оттенок "
            "никогда не проскочит.",
        "desc.adaptive_threshold": "Тёмные темы и выцветшие "
            "документы сами понижают свой порог обнаружения, поэтому "
            "бледные элементы тоже находятся. Рекомендовано вкл.",
        "desc.auto_click": "Включено: программа сама кликает каждые 0,1 с по лучшему элементу "
            "наблюдаемой области, приоритет — контраст. При заданном акцентном "
            "цвете годятся только окрашенные элементы; без цвета кликаются "
            "только очень чётко прорисованные. Никогда дважды в одном месте и "
            "не в собственных окнах.",
        "desc.auto_click_interval": "Как часто экран проверяется на "
            "ваш цвет (0,5-60). Медленное число - безопасное: 2-5 "
            "подходит для диалога, за которым вы следите.",
        "desc.auto_click_max_clicks": "Сколько раз может кликнуть "
            "само после запуска (1-200). На лимите останавливается и "
            "сообщает, чтобы неверная настройка не разбежалась.",
        "desc.auto_click_min_contrast": "По той же шкале, что "
            "»Минимальная чёткость края«. Начните со значения по "
            "умолчанию и повышайте, если кликает не то: "
            "засчитываться будут только сильные, чёткие элементы.",
        "desc.auto_click_radius": "Автоклик ищет вокруг центра "
            "экрана (40-600 px). Шире для занятого окна; уже, чтобы "
            "видел только один контрол по центру.",
        "desc.auto_click_repeat_px": "После автоклика цель в "
            "стольких пикселях оставляется в покое (0-400). Без "
            "этого стоящая на экране кнопка кликалась бы снова и "
            "снова.",
        "desc.auto_click_settle_ms": "Курсор отдыхает так на цели "
            "(0-2000 мс) перед кликом, чтобы программа сначала "
            "увидела подсветку. 120 подходит большинству окон.",
        "desc.block_bound_keys": "Выкл (по умолчанию): сочетание без "
            "Ctrl/Alt/Shift - например 1 или V - работает в каждой "
            "программе И печатает как обычно, то есть в середине "
            "фразы тоже вызовет действие. Вкл: действие срабатывает "
            "везде, но клавиша больше не печатает.",
        "desc.capture_backend": "Как фотографируется экран. "
            "Автоматически использует совместимый способ, который видит почти все окна; "
            "Совместимый работает всегда, включая удалённый рабочий "
            "стол и виртуальные машины. Действует после перезапуска.",
        "desc.color_adapt": "Каждый элемент перед сравнением "
            "балансируется по белому относительно собственного фона, "
            "чтобы ночной свет и оттенки темы перестали выталкивать "
            "ваш цвет из допуска. Отключайте только для сравнения с "
            "неадаптированным сравнителем.",
        "desc.contrast_threshold": "Ниже находит более бледные "
            "элементы (и больше шума); выше требует более чётких "
            "краёв.",
        "desc.default": "Наведите курсор на название настройки, "
            "чтобы увидеть, что она делает.",
        "desc.exclude_color": "Элементы с этими цветами никогда не "
            "сопровождаются: щелчки по ним уходят прямо в Windows в "
            "обоих режимах. Показаны квадратами цвета справа - "
            "выберите цвет ниже и нажмите «Добавить в запрещённые», "
            "чтобы добавить один (не больше пятнадцати); щелчок по "
            "квадрату убирает его. Пустой список показывает "
            "перечёркнутый квадрат и выключает настройку.",
        "desc.follow_boost": "Насколько запомненный элемент "
            "выигрывает ничьи: 100% может вдвое поднять его оценку, "
            "пока память свежая, 25% - лёгкий толчок.",
        "desc.follow_enabled": "После удачного притяжения похожие "
            "элементы или элементы на том же месте выигрывают "
            "некоторое время - удобно для ползунков и повторных "
            "кликов по одной кнопке.",
        "desc.follow_learn": "Только элементы моего цвета: промах "
            "куда-то ещё не может перенацелить память. Каждое "
            "удачное притяжение: старое, доверчивое поведение.",
        "desc.follow_seconds": "Секунды, в течение которых "
            "запомненный элемент предпочитается после последнего "
            "удачного притяжения (1-120).",
        "desc.glide_ms": "0 (по умолчанию) прыгает мгновенно - "
            "быстрее всего. 40-120 скользит, чтобы вы видели; своё "
            "движение мыши отменяет скольжение.",
        "desc.hold_follow": "Пока вы держите левую кнопку сразу "
            "после притяжения - или нажимаете снова на запомненном "
            "элементе - курсор остаётся на цвете этого элемента; это "
            "успокаивает перетаскивание, например ползунков. Нажатия "
            "в другом месте не трогаются.",
        "desc.key_launch": "Формат: ctrl+l, f5, space, ctrl+alt+1 "
            "... Модификаторы: ctrl, alt, shift, win. Действует "
            "после «Применить».",
        "desc.key_mode1": "Через запятую, напр. '1, f1, ctrl+f1, v'. "
            "Что делает классический режим, объясняет вкладка "
            "«Горячие клавиши».",
        "desc.key_mode2": "Через запятую, напр. '2, f2, ctrl+f2, b'. "
            "Что делает режим ведения, объясняет вкладка «Горячие "
            "клавиши».",
        "desc.key_pause": "Мышь и клавиатура снова полностью ваши, "
            "до запуска.",
        "desc.key_play": "Воспроизводит запись, выбранную в списке "
            "Макросов, а если ничего не выбрано - новейшую. На "
            "повторяющейся записи останавливает её.",
        "desc.key_play_n": "Воспроизводит запись #%d из "
            "пронумерованного списка на вкладке Макросы, по её "
            "позиции. Если список короче, ничего не происходит.",
        "desc.key_record": "Записывает всё, что вы делаете - каждую "
            "клавишу, каждый щелчок мыши и каждое движение курсора, "
            "- и ваш ввод всё ещё доходит до ваших программ, пока "
            "сочетание стоп не сохранит его в список Макросов. "
            "Взводится только в рабочем состоянии.",
        "desc.key_record_stop": "Останавливает запись, сохраняет "
            "последовательность в список Макросов и останавливает "
            "идущее воспроизведение.",
        "desc.luminance_norm": "Края оцениваются относительно "
            "яркости окружения, поэтому тёмные темы работают как "
            "светлые. Рекомендовано вкл.",
        "desc.macro_action": "Сочетание, нажимаемое за вас при "
            "каждом нажатии триггера (одно нажатие = одно "
            "сочетание): 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' ... "
            "Пусто = макрос выкл.",
        "desc.macro_key": "Клавиша, которая ОЗНАЧАЕТ макрос вместо "
            "печати: 'b', 'f7', 'ctrl+b' ... В рабочем состоянии "
            "одно нажатие отправляет сочетание рядом ровно один раз, "
            "а сама клавиша не доходит до программ. На паузе "
            "печатает как обычно. Пусто = макрос выкл.",
        "desc.max_area": "Большие пятна игнорируются - обычно целые "
            "окна или обои, а не кликабельные элементы.",
        "desc.max_dim": "Элементы шире или выше этого игнорируются; "
            "элементы у края экрана, как ползунки, получают двойной "
            "запас.",
        "desc.merge_distance": "Кусочки ближе этого (рваный контур, "
            "иконка рядом с подписью) становятся одним элементом. "
            "Два полноценных элемента никогда не склеиваются.",
        "desc.min_area": "Меньшие пятна игнорируются как соринки, "
            "если не приклеены к более крупному элементу.",
        "desc.min_contrast": "Элемент должен быть не менее чётким, "
            "чтобы вообще быть кликабельным. Значения ниже 28 "
            "считаются за 28: встроенный порог качества не даёт шуму "
            "стать кликабельным.",
        "desc.motion_3d": "Отслеживает движущиеся элементы позицией "
            "И размером вместо прямой подгонки: одиночные плохие "
            "сканы игнорируются вместо ослепления слежения, повороты "
            "проходятся, а внезапный скачок размера перезапускает "
            "трек (сканер взял другой элемент). Те же пороги "
            "скорости, тот же лимит 80 px - меняются только мозги. "
            "Работает самостоятельно.",
        "desc.motion_lead_ms": "Миллисекунды движения, на которые "
            "опережать движущийся элемент (0-300): 40-80 для "
            "медленной прокрутки, 100-150 для быстрых полос. "
            "Ограничено 80 px, выключено при медленном или меняющем "
            "направление движении.",
        "desc.motion_predict": "Для элементов, которые двигаются во "
            "время клика (прокручиваемые списки, полосы видео), "
            "целится чуть вперёд, чтобы клик попал в элемент. "
            "Неподвижные элементы не меняются.",
        "desc.mouse2_action": "Что короткий правый клик делает "
            "ДОПОЛНИТЕЛЬНО - сам правый клик всегда сохраняет свою "
            "обычную функцию Windows. По умолчанию: ничего.",
        "desc.mouse2_hold_action": "Те же возможности, срабатывают, "
            "если УДЕРЖАТЬ правую кнопку около полсекунды вместо "
            "клика. Нажатие - это либо клик, либо удержание, никогда "
            "оба. По умолчанию: ничего.",
        "desc.on_target_dist": "Если ваш клик попадает в это число "
            "пикселей от центра элемента, ничего не движется - вы "
            "попали.",
        "desc.radius": "Дальность поиска в пикселях (40-400). "
            "Больше, если нужный элемент совсем рядом вне "
            "досягаемости; меньше, если выигрывает не тот сосед.",
        "desc.rapid_click_snap": "Выкл (по умолчанию): пока клик "
            "обрабатывается, остальные уходят в Windows. Вкл: "
            "обслуживается каждый левый клик.",
        "desc.snap_offset_x": "Сдвигает точку клика вбок от центра "
            "элемента (-200 до 200, отрицательные влево). Для "
            "контрола с мёртвой серединой - разделённая кнопка, "
            "ползунок - наведите клик на живое место один раз вместо "
            "борьбы при каждом снапе.",
        "desc.snap_offset_y": "Сдвигает точку клика вертикально от "
            "центра элемента (-200 до 200, отрицательные вверх). Как "
            "боковой сдвиг: приземляйтесь на живую часть контрола.",
        "desc.stall_pause_seconds": "Если скан когда-либо зависнет, "
            "помощь приостанавливается на это время, и любой "
            "удерживаемый клик возвращается вам.",
        "desc.watcher_seconds": "В классическом режиме второе "
            "притяжение близ того же места за это время становится "
            "двойным кликом по элементу.",
        "ent.cancel_line": "активна до %s - НЕ продлится",
        "ent.canceled_line": "подписка завершена%s",
        "ent.expired_line": "истекла %s - продлите на Stripe",
        "ent.past_due_line": "платёж не прошёл - исправьте карту в "
            "письме-квитанции Stripe; доступ вернётся, когда счёт "
            "оплатится",
        "ent.plan": " (%s)",
        "ent.refunded_line": "возврат / оспаривание - активация "
            "отозвана",
        "ent.st.active": "активна",
        "ent.st.canceled": "завершена",
        "ent.st.canceling": "активна, но отключается",
        "ent.st.grant": "грант поддержки",
        "ent.st.past_due": "ПЛАТЁЖ НЕ ПРОШЁЛ",
        "ent.st.refunded": "возврат / оспаривание",
        "ent.st.trial": "проба",
        "ent.st.unsubscribed": "нет подписки",
        "ent.until": " до %s",
        "err.auth_unreachable": "Сервер аутентификации Snappy AI "
            "недоступен:\n%s\n\nSnappy AI работает только с живым "
            "ответом от него.\nПовторить?",
        "err.start_fail": "Snappy AI не смог запуститься.\nЗапустите "
            "с --console, чтобы увидеть детали.",
        "gate.btn.monthly": "Подписка на месяц за 9,99€",
        "gate.btn.trial": "Пробная покупка за 1,99€",
        "gate.head.canceled": "Эта подписка отменена - заведите "
            "новую на Stripe, чтобы продолжить.",
        "gate.head.canceling": "Ваша подписка настроена на "
            "отключение - она активна до %s, затем этот вход снова "
            "заблокируется, если не продлить.",
        "gate.head.email_mismatch": "Платёж сделан с другого e-mail, "
            "не с вашей учётной записи Discord. Подписки работают "
            "только на e-mail Discord, показанный ниже - оплатите с "
            "него или свяжитесь с поддержкой.",
        "gate.head.expired": "Подписка этого входа истекла - "
            "продлите её на Stripe, чтобы продолжить.",
        "gate.head.none": "Вы вошли, но у этого входа нет активной "
            "подписки. Оплатите ЭТИМ e-mail Discord - покупка на "
            "другой адрес не может его активировать.",
        "gate.head.past_due": "Последний платёж подписки не прошёл - "
            "исправьте его на Stripe, чтобы снова разблокировать "
            "этот вход.",
        "gate.head.refunded": "Эта покупка возвращена или оспорена, "
            "поэтому активация отозвана. Новая подписка на этом "
            "e-mail Discord снова активирует её.",
        "gate.head.shared": "Эта учётная запись СЕЙЧАС работает на "
            "ДРУГОМ компьютере. Snappy AI остаётся выключен, пока та "
            "же учётная запись Discord запущена в двух местах - "
            "закройте другую сессию и проверьте снова. Общие "
            "подписки поднимают цены; пожалуйста, не надо.",
        "gate.msg.active": "Подписка активна - Snappy AI "
            "запускается...",
        "gate.msg.checking": "Проверяем у сервера...",
        "gate.msg.no_link": "Эта платёжная ссылка не настроена в "
            "этой сборке.",
        "gate.msg.open_fail": "Не удалось открыть браузер. Откройте "
            "эту ссылку вручную:\n%s",
        "gate.msg.open_ok": "Stripe открыт в браузере - оплатите там. Это окно само заметит платёж и запустит движок.",
        "gate.msg.session_gone": "Сессия исчезла - войдите снова.",
        "gate.msg.still_none": "У этого входа всё ещё нет активной "
            "подписки.",
        "gate.msg.still_shared": "Всё ещё используется на другом "
            "компьютере - закройте ту сессию и проверьте снова.",
        "gate.msg.unreachable": "Сервер аутентификации недоступен: "
            "%s",
        "gate.note": "Движок стартует, как только подписка активна - "
            "это окно само проверяет каждые 30 секунд. Закрытие "
            "возвращает ко входу.",
        "gate.prices": "Проба 2 дня: 1,99€ (разово)  -  подписка: "
            "9,99€ / мес.\nАктивация приходит до ~10 минут после "
            "оплаты; продления автоматически снова активируют этот "
            "же вход.",
        "gate.title": "%s - Подписка%s",
        "hdr.build": "сборка %s",
        "help.1.b": "Snappy AI смотрит на экран вокруг курсора, "
            "находит рядом плотные похожие на элементы вещи - "
            "кнопки, значки, ссылки - и выбирает лучшую: чёткие "
            "края, разумный размер и близость к курсору выигрывают. "
            "Ваш цвет, список «нельзя кликать» и память о последнем "
            "клике могут склонить выбор. Затем курсор целится в "
            "середину элемента, а не в угол его рамки.",
        "help.1.t": "Что происходит при клике",
        "help.10.b": "1. Запущено ли? Пауза значит, что ничего не "
            "перехватывается - «Клавиша: начать помощь» (по "
            "умолчанию Ctrl+L) это единственный вкл/выкл.  2. "
            "Удержите Shift на один клик, чтобы убедиться, что "
            "проблемой была помощь.  3. Выигрывает не тот элемент: "
            "уменьшите «Как далеко от курсора искать», затем задайте "
            "«Мой цвет» или поднимите «Силу цветового преимущества». "
            " 4. Ничего не находится: снизьте «Насколько бледным "
            "может быть край» и «Минимальную чёткость края», "
            "поднимите «Максимальную ширину или высоту» или "
            "«Склеивать близкие кусочки».  5. Что-то никогда не "
            "должно обслуживаться: положите его цвет в «Цвет(а), по "
            "которым нельзя кликать».  6. Всё ещё не так: сообщите в "
            "поддержку, куда вы кликнули и чего ждали, и приложите "
            "файл журнала, который Snappy AI пишет в свою папку "
            "данных.",
        "help.10.t": "Если что-то не так, проверяйте в этом порядке",
        "help.2.b": "Режим ведения (по умолчанию) не съедает клик: "
            "он доходит до программы, а после отпускания курсор едет "
            "на ближайший чистый элемент. Классический режим "
            "сильнее: промах рядом с элементом ловится, курсор "
            "притягивается, и Snappy AI кликает за вас. «Как далеко "
            "от курсора искать» задаёт круг поиска - больше, если "
            "нужный элемент совсем рядом вне досягаемости, меньше, "
            "если выигрывает не тот сосед. Удержание Shift обходит "
            "один клик в обоих режимах.",
        "help.2.t": "Сначала: режим и дальность поиска",
        "help.3.b": "На вкладке Обработка «Насколько бледным может "
            "быть край» и «Минимальная чёткость края» решают, какие "
            "края вообще считаются: ниже - найдёт бледнее, выше - "
            "отбросит шум. «Минимальный размер элемента», "
            "«Максимальная площадь элемента» и «Максимальная ширина "
            "или высота» отсеивают соринки и целые окна. «Склеивать "
            "близкие кусочки» соединяет рваный контур или значок "
            "рядом с подписью в один элемент. На вкладке Помощь "
            "«Автоподстройка для тусклых экранов» и «Оценивать края "
            "по относительной яркости» делают тёмные темы похожими "
            "на светлые - оставьте обе включёнными.",
        "help.3.t": "Ничего не найдено - или слишком много",
        "help.4.b": "На вкладке Цвета «Мой цвет (цвета)» - "
            "предпочитаемый цвет, а «Цвет(а), по которым нельзя "
            "кликать» абсолютны: такие элементы никогда не "
            "обслуживаются. «Помогать только моему цвету» "
            "ограничивает помощь подходящими элементами. На вкладке "
            "Обработка «Строгость совпадения цвета» говорит, "
            "насколько близким должен быть оттенок, «Принимать "
            "близкие оттенки» позволяет светлым или выцветшим "
            "считаться частично, а «Сила цветового преимущества» - "
            "насколько ваш цвет поднимает элемент; поднимите её, "
            "если всё же выигрывает не тот.",
        "help.4.t": "Работа с цветами",
        "help.5.b": "«Помнить последний кликнутый элемент» "
            "продолжает предпочитать элемент, на котором оказался "
            "ваш последний удачный клик, в течение «Как долго "
            "помнить» секунд - это делает ползунки и кнопки диалогов "
            "удобными. «Сила памяти» говорит, насколько сильно он "
            "выигрывает, а «Чему может учиться память» защищает её: "
            "при «Только элементы моего цвета» промах не может "
            "перенацелить память. «Удерживаемая кнопка держит курсор "
            "на элементе» успокаивает перетаскивание, а действия "
            "правой кнопки на вкладке Экспериментально могут "
            "следовать за памятью мышью или очищать её.",
        "help.5.t": "Повторные клики по одной кнопке",
        "help.6.b": "«Опережать движущиеся элементы» измеряет, как "
            "быстро движется выбранный элемент, и целится на "
            "«Насколько целиться вперёд» миллисекунд вперёд, чтобы "
            "клик попал в прокручиваемый список или полосу видео, а "
            "не позади. Опережение ограничено 80 пикселями и само "
            "выключается для неподвижных или поворачивающих "
            "элементов.",
        "help.6.t": "Клики по движущемуся",
        "help.7.b": "«Анимировать движение курсора» = 0 прыгает "
            "сразу; 40-120 скользит, чтобы вы видели, а своё "
            "движение мыши отменяет скольжение. «Окно двойного "
            "клика» в классическом режиме превращает второе "
            "притяжение близ того же места в двойной клик. «Помогать "
            "каждому клику быстрой серии» обслуживает каждый клик "
            "серии, а не только первый. «Пауза после сбоя» - "
            "предохранитель, возвращающий удерживаемый клик, если "
            "скан завис.",
        "help.7.t": "Как ощущаются клики",
        "help.8.b": "Вкладка «Горячие клавиши» объясняет два режима "
            "и процесс записи. Коротко: сочетания с Ctrl, Alt, Shift "
            "или Win зарезервированы системно; голые одиночные "
            "клавиши срабатывают везде и всё ещё печатают. Макрос "
            "превращает одно блокированное нажатие в целое "
            "сочетание. Записи ловят ваш настоящий ввод - каждую "
            "клавишу, щелчок мыши и движение курсора - и "
            "воспроизводят его с вкладки Макросы, у каждой свой "
            "переключатель один раз или повторять до остановки.",
        "help.8.t": "Клавиши, макросы и записи",
        "help.9.b": "Кнопка Язык рядом с «Экспорт настроек» - а "
            "также в окне входа и окне подписки - переключает весь "
            "интерфейс сразу, без перезапуска, и запоминает выбор. "
            "Языки, которые ещё переводятся, не предлагаются, "
            "поэтому любой выбранный полон.",
        "help.9.t": "Язык",
        "help.sub": "Каждая настройка под тем именем, которое вы "
            "видите на её вкладке, в том порядке, в котором "
            "понадобится. Наведите курсор на имя, чтобы увидеть "
            "короткое описание; эта страница - длинная форма.",
        "help.tail": "Настройки действуют после нажатия «Применить». "
            "Файл config.ini рядом с программой переопределяет "
            "config.json. Эта страница объясняет, а не настраивает.",
        "help.title": "Настройка Snappy AI простыми словами",
        "kb.keys.b": "Сочетание с Ctrl, Alt, Shift или Win "
            "зарезервировано системно: его видит только Snappy AI. "
            "Голая одиночная клавиша (как 1 или 2) работает в каждой "
            "программе И печатает как обычно - цена в том, что "
            "нажатие её в середине фразы тоже вызовет действие. "
            "Классическое поведение даёт переключатель "
            "«Одноклавишные сочетания поглощают клавишу» на вкладке "
            "Помощь. Макросы идут дальше: в рабочем состоянии "
            "клавиша-триггер проглатывается, а сочетание рядом "
            "отправляется ровно один раз.",
        "kb.keys.t": "Одиночные клавиши против комбинаций",
        "kb.mode.b": "Режим ведения (по умолчанию, клавиша 2): ваш "
            "клик всегда доходит до программы нетронутым; после "
            "отпускания кнопки курсор едет на ближайший чистый "
            "элемент, так что следующий клик стартует оттуда. Ничего "
            "никогда не проглатывается - самый безопасный режим.  "
            "Классический режим (клавиша 1): если вы кликнули рядом "
            "с элементом, этот промах ловится, курсор притягивается "
            "к элементу и Snappy AI кликает за вас; если рядом "
            "ничего нет, клик возвращается нетронутым.  В обоих "
            "режимах удержание Shift при клике обходит помощь для "
            "этого одного клика.",
        "kb.mode.t": "Что делают два режима",
        "kb.rec.b": "В рабочем состоянии нажмите сочетание начала "
            "записи (по умолчанию Ctrl+Alt+R): каждая нажатая "
            "клавиша, каждый щелчок мыши и каждое движение курсора "
            "записывается И всё ещё доходит до ваших программ, так "
            "что вы работаете как обычно во время записи. Нажмите "
            "сочетание стоп (Ctrl+Alt+S), чтобы сохранить запись в "
            "список на вкладке Макросы - туда помещается пять "
            "записей. Щёлкните запись, чтобы выбрать её, "
            "использовать «Переименовать» или «Экспорт» и настроить "
            "её собственный переключатель «Повторять до остановки». "
            "Сочетание воспроизведения (Ctrl+Alt+M) играет выбранную "
            "там запись; Ctrl+1..Ctrl+5 играют по позиции в списке. "
            "На паузе ничего не записывается и ничего не вводится - "
            "ваш ввод полностью ваш.",
        "kb.rec.t": "Как записать и воспроизвести свои клавиши и "
            "действия мыши",
        "lang.close": "Закрыть",
        "lang.coverage": "Переведено %d%%",
        "lang.current": "Текущий: %s",
        "lang.progress": "Ещё переводится, появится когда будет "
            "готово: %s",
        "lang.prompt": "Смена действует сразу - окно остаётся "
            "открытым, можно попробовать несколько.",
        "lang.title": "Язык",
        "lbl.accent_boost": "Сила цветового преимущества",
        "lbl.accent_coherent": "Игнорировать рассыпанные вкрапления",
        "lbl.accent_color": "Мой цвет (цвета)",
        "lbl.accent_matcher": "Движок сравнения цветов",
        "lbl.accent_only": "Помогать только моему цвету",
        "lbl.accent_soft": "Принимать близкие оттенки",
        "lbl.accent_tolerance": "Строгость совпадения цвета",
        "lbl.accent_variants": "Светлые и тёмные состояния моего "
            "цвета",
        "lbl.adaptive_threshold": "Автоподстройка для тусклых "
            "экранов",
        "lbl.auto_click": "Кликать элементы само",
        "lbl.auto_click_interval": "Секунды между автокликами",
        "lbl.auto_click_max_clicks": "Лимит автокликов за сеанс",
        "lbl.auto_click_min_contrast": "Насколько чёткой должна быть "
            "цель",
        "lbl.auto_click_radius": "Искать от центра экрана",
        "lbl.auto_click_repeat_px": "Не кликать в одно место "
            "повторно",
        "lbl.auto_click_settle_ms": "Пауза перед автокликом",
        "lbl.block_bound_keys": "Одноклавишные сочетания поглощают "
            "клавишу",
        "lbl.capture_backend": "Движок снимка экрана",
        "lbl.color_adapt": "Подстраиваться под свет экрана",
        "lbl.contrast_threshold": "Насколько бледным может быть край",
        "lbl.exclude_color": "Цвет(а), по которым нельзя кликать",
        "lbl.follow_boost": "Сила памяти",
        "lbl.follow_enabled": "Помнить последний кликнутый элемент",
        "lbl.follow_learn": "Чему может учиться память",
        "lbl.follow_seconds": "Как долго помнить",
        "lbl.glide_ms": "Анимировать движение курсора",
        "lbl.hold_follow": "Удерживаемая кнопка держит курсор на "
            "элементе",
        "lbl.key_launch": "Клавиша: начать помощь",
        "lbl.key_mode1": "Клавиша: классический режим (до 4 клавиш)",
        "lbl.key_mode2": "Клавиша: режим ведения (до 4 клавиш)",
        "lbl.key_pause": "Клавиша: пауза",
        "lbl.key_play": "Клавиша: воспроизвести выбранную запись",
        "lbl.key_play_n": "Клавиша: воспроизвести запись #%d",
        "lbl.key_record": "Клавиша: начать запись",
        "lbl.key_record_stop": "Клавиша: остановить и сохранить "
            "запись",
        "lbl.luminance_norm": "Оценивать края по относительной "
            "яркости",
        "lbl.macro_action": "Макрос %d: вместо этого шлёт",
        "lbl.macro_key": "Макрос %d: нажмите эту клавишу",
        "lbl.max_area": "Максимальная площадь элемента",
        "lbl.max_dim": "Максимальная ширина или высота элемента",
        "lbl.merge_distance": "Склеивать близкие кусочки",
        "lbl.min_area": "Минимальный размер элемента",
        "lbl.min_contrast": "Минимальная чёткость края",
        "lbl.motion_3d": "Умное слежение за движением",
        "lbl.motion_lead_ms": "Насколько целиться вперёд",
        "lbl.motion_predict": "Опережать движущиеся элементы",
        "lbl.watch_center_only": "Следить только за центром экрана",
        "desc.watch_center_only": "Помощник наблюдает только за фиксированным квадратом в центре "
            "экрана (размер = дистанция поиска, по умолчанию 150×150 px), "
            "независимо от положения курсора. Клики вне этого квадрата остаются "
            "без изменений.",
        "lbl.center_follow": "Экран следует за целью",
        "desc.center_follow": "Когда «Следить только за центром экрана» включено: после захвата "
            "элемента помощник двигает экран, чтобы удерживать его в центре, "
            "особенно на прокручиваемых плоскостях. Двигайте экран сами, чтобы "
            "отпустить следование.",
        "lbl.input_backend": "Метод ввода",
        "desc.input_backend": "Инъекция Windows (по умолчанию) работает везде. Interception "
            "отправляет через драйвер, и игры распознают её как настоящую мышь; "
            "требует установленного драйвера Interception и interception.dll "
            "рядом с программой; иначе автоматически используется инъекция "
            "Windows.",
        "val.input_backend.win32": "Инъекция Windows",
        "val.input_backend.interception": "Interception (драйвер)",
        "lbl.mouse2_action": "Дополнительное действие правой кнопки",
        "lbl.mouse2_hold_action": "Действие удержания правой кнопки",
        "lbl.on_target_dist": "Расстояние «уже попали»",
        "lbl.radius": "Как далеко от курсора искать",
        "lbl.rapid_click_snap": "Помогать каждому клику быстрой "
            "серии",
        "lbl.snap_offset_x": "Точка клика: влево / вправо",
        "lbl.snap_offset_y": "Точка клика: вверх / вниз",
        "lbl.stall_pause_seconds": "Пауза после сбоя",
        "lbl.watcher_seconds": "Окно двойного клика",
        "login.failed": "Вход %s не завершён - попробуйте снова.",
        "login.no_provider": "В эту копию не встроен провайдер "
            "входа.",
        "login.not_configured": "Файл подписки в этой сборке ещё не "
            "настроен.",
        "login.note": "Вход открывает браузер и сам возвращается в "
            "это окно.",
        "login.provider": "Войти через %s",
        "login.signedin": "Вы вошли как %s.",
        "login.sub": "Войдите через Discord - подписка привязана к "
            "этой учётной записи, и платежи должны использовать её "
            "e-mail. Пароля здесь нет.",
        "login.title": "%s - Вход",
        "login.unreachable": "Сервер аутентификации недоступен: %s",
        "login.waiting": "Ждём браузер - завершите вход %s...",
        "mac.delete": "Удалить",
        "mac.empty": "Записей пока нет - запустите, нажмите "
            "сочетание записи и работайте как обычно: каждая "
            "клавиша, клик и движение курсора записываются.",
        "mac.export": "Экспорт",
        "mac.import": "Импорт",
        "mac.keys_head": "Клавишные макросы",
        "mac.loop": "Повторять до остановки",
        "mac.recordings": "Записи",
        "mac.rename": "Переименовать",
        "mac.row": "Макрос %d",
        "mac.sends": "отправляет",
        "mac.steps": "%d шагов",
        "note.advanced": "Настройки расстояний и времени, меняющие "
            "ощущение кликов, а не то, что находится. Большинству "
            "людей трогать их не нужно; значения по умолчанию "
            "проверены.",
        "note.assist": "Каждый переключатель, меняющий поведение в "
            "рабочем состоянии. Режимы меняются вашими клавишами "
            "режимов - вкладка «Горячие клавиши» объясняет, что "
            "делает каждый. Помощь всегда стартует на паузе; Запуск "
            "- единственный вкл/выкл. Куда смотрит движок и как "
            "ощущаются клики - в «Дополнительно»; что считается "
            "элементом - в «Обработка».",
        "note.colors": "Два списка наверху решают, какие цвета "
            "Snappy AI предпочитает или отвергает. Каждый показывает "
            "свои цвета квадратами справа, не больше пятнадцати, и "
            "щелчок по квадрату снова убирает этот цвет; пустой "
            "список показывает перечёркнутый квадрат и считается "
            "выключенным. «Добавить в предпочитаемые» и «Добавить в "
            "запрещённые» кладут цвет, стоящий в палитре, в нужный "
            "список. Текущее значение RGB показывает три квадрата - "
            "каждый шириной в пять цветовых квадратов, так что "
            "строка занимает те же пятнадцать квадратов, что и всё "
            "ниже, - которые светятся тем ярче, чем больше красного, "
            "зелёного и синего в цвете палитры; строка следует за "
            "палитрой и не принимает ввод. Палитра ниже смешивает "
            "цвет как графический редактор; всё рядом с ней сидит у "
            "правого края окна с тем же отступом, что и настройки "
            "выше, и каждый ряд занимает одну и ту же ширину в "
            "пятнадцать квадратов: высокая витрина с нарисованным "
            "внутри #кодом, затем пятнадцать готовых тонов, две "
            "кнопки добавления и экранный ряд - «Взять цвет с "
            "экрана» берёт один цвет под курсором, «Предложить цвета "
            "с экрана» заполняет пятнадцать своих квадратов цветами, "
            "найденными вокруг курсора, и щелчок по одному загружает "
            "его в палитру. Витрина высокая не случайно: так "
            "квадраты подсказок заканчиваются ровно на уровне "
            "цветового ползунка слева.",
        "note.experimental": "Выбор движков, у каждого проверенное "
            "значение по умолчанию. Меняйте только при сравнении "
            "движков, на необычном оборудовании или по просьбе "
            "поддержки - движок снимка действует после перезапуска.",
        "note.handler": "Что считается кликабельным элементом: как "
            "бледным может быть край, насколько чётким он должен "
            "быть и каким большим или маленьким может быть элемент. "
            "Ничего не найдено? Ослабьте. Нашлось не то? Ужесточите "
            "или используйте свой цвет на вкладке Цвета.",
        "note.keybindings": "Каждое сочетание - а ниже, что делают "
            "два режима, как записать свои клавиши и действия мыши и "
            "чем одиночная клавиша отличается от комбинации.",
        "note.macros": "Макрос превращает одно нажатие клавиши в "
            "целое сочетание в рабочем состоянии. Рядом с макросами "
            "ваши записи: до пяти именованных снимков всего, что вы "
            "сделали - каждая клавиша, щелчок мыши и движение "
            "курсора, - воспроизводимых точно как записано. Щёлкните "
            "запись, чтобы выбрать её; у каждой строки свой "
            "переключатель «Повторять до остановки», а "
            "«Переименовать», «Экспорт», «Импорт» и «Удалить» "
            "находятся внизу рамки.",
        "note.macros_keys": "Клавиши записи/воспроизведения - на "
            "вкладке «Горячие клавиши» (по умолчанию: Ctrl+Alt+R "
            "запись, Ctrl+Alt+S стоп и сохранить, Ctrl+Alt+M "
            "воспроизвести, Ctrl+1..5 воспроизвести по списку).",
        "online.cancelled": "Аутентификация Discord отменена (или не "
            "удалась). Попробуйте снова.",
        "rec.export_fail": "Экспорт не удался: %r",
        "rec.exported": "Экспортировано в %s",
        "rec.import_fail": "Импорт не удался: %r",
        "rec.imported": "Импортировано записей: %d%s.",
        "rec.imported_none": " (ни одна не подошла)",
        "rec.no_sel": "Ничего не выбрано для экспорта.",
        "rec.notfile": "Импорт не удался: это не файл записи.",
        "shared.back": "С возвращением - нажмите Запуск, когда "
            "будете готовы.",
        "shared.body": "Эта учётная запись Discord сейчас запускает "
            "Snappy AI на другом компьютере.\nПомощь здесь "
            "приостановлена, пока не останется одна сессия.\n\nОдна "
            "подписка - одна машина одновременно: это держит\nцену "
            "низкой, а разработку идущей.",
        "shared.close": "Закрыть",
        "shared.recheck": "Проверить сейчас",
        "shared.still": "Всё ещё используется в другом месте - "
            "остаёмся на паузе.",
        "shared.title": "Учётная запись используется в другом месте",
        "shared.unreachable": "Сервер недоступен - проверим снова.",
        "st.all_files": "Все файлы",
        "st.color_added": "rgb(%d, %d, %d) добавлен в %s - "
            "«Применить» сохранит.",
        "st.color_already": "rgb(%d, %d, %d) уже есть в %s.",
        "st.color_full": "В %s уже 15 цветов - сначала кликните по "
            "одному из квадратиков, чтобы убрать цвет.",
        "st.color_removed": "rgb(%d, %d, %d) убран из %s - "
            "«Применить» сохранит.",
        "st.delete_confirm": "Удалить запись %r?\nЭто нельзя "
            "отменить.",
        "st.deleted": "Запись удалена.",
        "st.engine_dead": "Поток движка недоступен - сочетания не "
            "отвечают.",
        "st.ent_paused": "Подписка %s - помощь на паузе. Продлите на "
            "Stripe, затем перезапустите.",
        "st.ent_unreachable": "Проверка подписки: сервер недоступен "
            "(сессия продолжает работать).",
        "st.export_fail": "Экспорт не удался: %r",
        "st.export_rec_title": "Экспорт записи",
        "st.export_title": "Экспорт настроек",
        "st.exported": "Настройки экспортированы в %s",
        "st.file_rec": "Запись Snappy AI",
        "st.file_settings": "Настройки Snappy AI",
        "st.follow": "  |  слежение %d с назад",
        "st.import_fail": "Импорт не удался: %r",
        "st.import_notfile": "Импорт не удался: это не файл "
            "настроек.",
        "st.import_rec_title": "Импорт записей",
        "st.import_title": "Импорт настроек",
        "st.imported": "Импортировано настроек: %d%s.",
        "st.imported_ignored": ", пропущено: %s",
        "st.ini_over": "Применено, но config.ini переопределяет: %s",
        "st.lib_empty": "Список пуст - экспортировать нечего.",
        "st.line": "Помог %d  |  пропустил %d%s  |  тема: %s",
        "st.loop_desc": "Стиль воспроизведения ЭТОЙ записи: выкл = "
            "играет один раз; вкл = повторяет, пока вы снова не "
            "нажмёте сочетание воспроизведения. У каждой записи свой "
            "переключатель, сохраняется вместе с самой записью.",
        "st.name_empty": "Имя не должно быть пустым.",
        "st.pick_err": "Взятие не удалось: %r",
        "st.pick_fail": "Взятие не удалось - попробуйте снова.",
        "st.pick_ok": "Взят rgb(%d, %d, %d) в (%d, %d).",
        "st.pick_wait": "Наведите курсор на цвет - взятие через 3 "
            "с...",
        "st.preset_desc": "Готовый цвет: %s - кликните, чтобы "
            "загрузить в миксер.",
        "st.rec_count": "%d из 5 записей",
        "st.rec_now": "%r теперь: %s.",
        "st.rec_once": "играет один раз",
        "st.rec_playing": "Воспроизведение %r...",
        "st.rec_playing_loop": "Воспроизведение %r до остановки",
        "st.rec_recording": "ЗАПИСЬ - %s остановит и сохранит",
        "st.rec_repeats": "повторять до остановки",
        "st.registered": "Зарегистрировано на: %s    Статус: %s",
        "st.rename_prompt": "Новое имя записи #%d:",
        "st.renamed": "Запись переименована.",
        "st.reset_confirm": "Сбросить все настройки по "
            "умолчанию?\nУчётные записи сохраняются; это касается "
            "только настроек.",
        "st.rgb_bad": "Сначала введите корректные значения R/G/B.",
        "st.running": "Работает..",
        "st.saved": "Сохранено и применено.",
        "st.defaults_restored": "Настройки по умолчанию восстановлены.",
        "st.saved_bad": "Сохранено, но недействительно (осталось "
            "старое): %s",
        "st.select_rec": "Сначала выберите запись.",
        "st.shared_paused": "УЧЁТНАЯ ЗАПИСЬ ИСПОЛЬЗУЕТСЯ В ДРУГОМ "
            "МЕСТЕ - помощь на паузе; одна подписка = одна машина.",
        "st.standby": "Ожидание..",
        "st.sug_fail": "Предложение не удалось: %r",
        "st.sug_loaded": "Подсказка rgb(%d, %d, %d) стоит в палитре "
            "- добавьте её в список кнопками выше.",
        "st.sug_loaded_desc": "Предложенный цвет интерфейса rgb(%d, "
            "%d, %d) - %d%% области. Кликните, чтобы загрузить в "
            "миксер.",
        "st.sug_none": "Нет предложений цвета из этой области.",
        "st.sug_ok": "%d подсказок - щёлкните одну, чтобы загрузить "
            "её в палитру.",
        "st.sug_wait": "Укажите на приложение, в котором работаете - "
            "проба через 3 с...",
        "tab.advanced": "Дополнительно",
        "tab.assist": "Помощь",
        "tab.colors": "Цвета",
        "tab.experimental": "Экспериментально",
        "tab.handler": "Обработка",
        "tab.help": "Справка",
        "tab.hotkeys": "Горячие клавиши",
        "tab.macros": "Макросы",
        "theme.dark": "Тёмная",
        "theme.light": "Светлая",
        "val.accent_matcher.hsv": "Классический - старый движок",
        "val.accent_matcher.oklab": "Перцептивный - как цвета "
            "выглядят (рекомендуется)",
        "val.capture_backend.auto": "Автоматически - самый быстрый с "
            "надёжным запасом",
        "val.capture_backend.dxcam": "Desktop Duplication - самый "
            "быстрый на большинстве ПК",
        "val.capture_backend.mss": "Совместимый - работает всегда "
            "(удалённый стол, ВМ)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "экспериментально",
        "val.follow_learn.accent": "Только элементы моего цвета",
        "val.follow_learn.any": "Каждое удачное притяжение",
        "val.mouse2_action.1": "Снять текущую задачу слежения",
        "val.mouse2_action.2": "Следовать за последним цветом",
        "val.mouse2_action.3": "Взять цвет под курсором и следовать "
            "за ним",
        "val.mouse2_action.4": "Ничего не делать",
        "val.mouse2_hold_action.1": "Снять текущую задачу слежения",
        "val.mouse2_hold_action.2": "Следовать за последним цветом",
        "val.mouse2_hold_action.3": "Взять цвет под курсором и "
            "следовать за ним",
        "val.mouse2_hold_action.4": "Ничего не делать",
        "word.off": "Выкл",
        "word.on": "Вкл",
    },
    "zh": {
        "btn.apply": "应用",
        "btn.export": "导出设置",
        "btn.import": "导入设置",
        "btn.language": "语言：%s",
        "btn.launch": "启动",
        "btn.logout": "退出登录",
        "btn.pause": "暂停",
        "btn.restore": "恢复默认",
        "col.accent": "强调色",
        "col.add_pref": "添加到首选颜色",
        "col.add_ref": "添加到拒绝颜色",
        "col.chip_desc": "rgb(%d, %d, %d)，属于 %s - 点击色块即可移除此颜色。",
        "col.chip_off": "%s 还没有颜色——带红叉的方块表示关闭。在下方选一个颜色，再按对应的添加按钮。",
        "col.exclude": "排除",
        "col.pick": "从屏幕取色",
        "col.rgb.desc": "三个色块显示取色器中当前的颜色：第一个的亮度代表红色的多少，第二个代表绿色，第三个代表蓝色——越亮表示越多。这一行跟随取色器、预设色块和屏幕按钮；不能输入。",
        "col.rgb.name": "当前 RGB 值",
        "col.suggest": "从屏幕建议颜色",
        "desc.accent_boost": "您的颜色给目标加多少分（0-3）。若仍选错目标，提高到 1.5-2。",
        "desc.accent_coherent": "您的颜色必须连成一片才算数——零散的抖动或压缩噪点永远不能使元素合格、加成或进入永不点击列表。",
        "desc.accent_color": "Snappy AI "
            "应偏好的颜色，在右侧以颜色方块显示。在下方选一个颜色，按“添加到首选颜色”即可加入——最多 15 "
            "个方块；点击方块可再次移除该颜色。包含其中之一的元素在平局时优先。空列表显示带红叉的方块，表示停用该设置。",
        "desc.accent_matcher": "如何比较颜色。感知式按颜色实际的观感排序，推荐使用；经典式为旧引擎，供对比。",
        "desc.accent_only": "只有包含您颜色的目标才可被辅助；其他地方的点击原样交给 Windows。",
        "desc.accent_soft": "0-100：更亮、更暗或发灰的版本按多少程度计入。0 = 只认精确色调。",
        "desc.accent_tolerance": "颜色需要多接近才算您的（4-90）。越低越严格。",
        "desc.accent_variants": "您的颜色的更亮和更暗版本也算数，这样悬停、按下和变暗状态都有效，而无需放宽色相容差。只有明度——错的色相永远混不进来。",
        "desc.adaptive_threshold": "暗色主题和发灰的文档会自动降低自己的检测门槛，因此较淡的目标也能找到。建议开启。",
        "desc.auto_click": "开启后，程序每0.1秒自动点击被观察区域内的最佳项目，以对比度优先。设置了强调色时，只有带该色的项目符合条件；未设置颜色时，仅点击绘制非常清晰的项目。同一处不重复点击，绝不点击自己的窗口。",
        "desc.auto_click_interval": "屏幕多久检查一次您的颜色（0.5-60）。慢速数字更安全：2-5 "
            "适合您正在注视的对话框。",
        "desc.auto_click_max_clicks": "启动后最多自动点击多少次（1-200）。到达上限即停止并提示，错误的设置不会失控。",
        "desc.auto_click_min_contrast": "与“最低边缘清晰度”相同的刻度。从默认值开始，如果点错就调高：只有清晰、明确的元素才算数。",
        "desc.auto_click_radius": "自动点击在屏幕中央周围搜索（40-600 "
            "像素）。窗口内容多就调大；调小则只看中央那一个控件。",
        "desc.auto_click_repeat_px": "自动点击后，此像素范围内的目标不再打扰（0-400）。否则留在屏幕上的按钮会被反复点击。",
        "desc.auto_click_settle_ms": "点击前光标在目标上停留这么久（0-2000 "
            "毫秒），让程序先看到高亮。120 适合大多数窗口。",
        "desc.block_bound_keys": "关（默认）：不带 Ctrl/Alt/Shift 的快捷键（如 1 或 "
            "V）在所有程序中生效，并且照常输入，因此句子中间按下也会触发其动作。开：动作仍然随处触发，但该键不再输入。",
        "desc.capture_backend": "如何拍摄屏幕。自动使用兼容方式，可看到几乎所有窗口；兼容式始终可用，包括远程桌面与虚拟机。重启后生效。",
        "desc.color_adapt": "每个元素在匹配前都按自身背景做白平衡，这样夜灯和主题偏色就不会把您的颜色推出容差。仅在与未自适应匹配器对比时关闭。",
        "desc.contrast_threshold": "更低会找到更淡的目标（也更多噪声）；更高则需要更清晰的边缘。",
        "desc.default": "将鼠标悬停在设置名称上可查看它的作用。",
        "desc.exclude_color": "包含这些颜色的元素绝不会获得辅助：在两种模式下，点击它们都直接交给 "
            "Windows。在右侧以颜色方块显示——在下方选一个颜色，按“添加到拒绝颜色”即可加入一个（最多 15 "
            "个）；点击方块即可移除。空列表显示带红叉的方块，表示停用该设置。",
        "desc.follow_boost": "记住的目标在平局中赢的力度：100% 在新鲜时可使其得分翻倍，25% "
            "只是轻推。",
        "desc.follow_enabled": "成功吸附后，相似或同位置的目标在一段时间内优先——适合滚动条和反复点击同一控件。",
        "desc.follow_learn": "仅我的颜色：误点别处不会带偏记忆。每次成功吸附：旧的、信任的行为。",
        "desc.follow_seconds": "上次成功吸附后，记住的目标保持优先的秒数（1-120）。",
        "desc.glide_ms": "0（默认）立即跳移——最快。40-120 滑动以便您观看；自己移动鼠标会取消滑动。",
        "desc.hold_follow": "在吸附后继续按住左键——或在记住的目标上再次按下——光标会保持在该目标的颜色上；这能稳定拖动，例如滚动条滑块。在其他地方按下不受影响。",
        "desc.key_launch": "格式：ctrl+l、f5、space、ctrl+alt+1 "
            "…修饰键：ctrl、alt、shift、win。应用后生效。",
        "desc.key_mode1": "逗号分隔，如 '1, f1, ctrl+f1, "
            "v'。经典模式做什么，见“快捷键”页。",
        "desc.key_mode2": "逗号分隔，如 '2, f2, ctrl+f2, "
            "b'。引导模式做什么，见“快捷键”页。",
        "desc.key_pause": "鼠标与键盘重新完全归您，直到启动。",
        "desc.key_play": "播放宏列表中选中的录制；未选中时播放最新的一条。对循环中的录制按下则停止它。",
        "desc.key_play_n": "播放宏页编号列表中第 %d 条录制，按列表位置。列表不够长时什么都不发生。",
        "desc.key_record": "记录您做的一切——每个按键、每次鼠标点击和每次光标移动——同时您的输入仍送达您的程序，直到停止快捷键把它存入宏列表。仅在启动状态布防。",
        "desc.key_record_stop": "停止记录，把序列存入宏列表，并停止正在进行的播放。",
        "desc.luminance_norm": "边缘按周围亮度的相对值评分，因此暗色主题与亮色主题表现一致。建议开启。",
        "desc.macro_action": "每次按下触发键时替您按下的组合（按一次 = "
            "一次组合）：'ctrl+c'、'ctrl+shift+s'、'space'、'f5' …留空 = 关闭宏。",
        "desc.macro_key": "代表宏而非输入的键：'b'、'f7'、'ctrl+b' "
            "…启动时按一次正好发送旁边的组合一次，该键本身不会送达程序。暂停时正常输入。留空 = 关闭宏。",
        "desc.max_area": "更大的斑块被忽略——通常是整窗口或壁纸，而非可点击目标。",
        "desc.max_dim": "比这更宽或更高的目标被忽略；屏幕边缘的目标（如滚动条）获得双倍额度。",
        "desc.merge_distance": "比这更近的碎片（断裂的轮廓、图标加标签）合成一个目标。两个完整目标永不被粘合。",
        "desc.min_area": "更小的斑块作为噪点忽略，除非被粘到更大的目标上。",
        "desc.min_contrast": "目标至少要这么清晰才可被点击。 低于 28 的值按 28 "
            "处理：内置质量下限防止噪声变得可点击。",
        "desc.motion_3d": "用位置加尺寸跟踪移动元素，而不是直线拟合：单个坏扫描被忽略而不是致盲跟随器，转弯会被跟住，尺寸突变则重启跟踪（说明扫描器选中了别的元素）。速度门限和 "
            "80 像素上限不变——只换更聪明的逻辑。可独立运行。",
        "desc.motion_lead_ms": "对移动目标提前的毫秒数（0-300）：慢速滚动用 "
            "40-80，快速进度条用 100-150。上限 80 像素，慢速或转向时自动关闭。",
        "desc.motion_predict": "对点击时会移动的目标（滚动列表、视频进度条），稍微提前瞄准，让点击落在目标上。静止目标不受影响。",
        "desc.mouse2_action": "短按右键额外做的事——右键本身始终保留其正常 Windows "
            "功能。默认：无。",
        "desc.mouse2_hold_action": "同样的选项，在按住右键约半秒而非点击时触发。一次按下要么是点击要么是长按，不会两者。默认：无。",
        "desc.on_target_dist": "若您的点击落在目标中心这么多像素内，则不移动——您已点中。",
        "desc.radius": "以像素计的搜索距离（40-400）。想要的目标稍够不着时调大；选错邻居时调小。",
        "desc.rapid_click_snap": "关（默认）：点击处理中时其余点击交给 "
            "Windows。开：每个左键点击都被辅助。",
        "desc.snap_offset_x": "将点击点从元素中央横向偏移（-200 到 "
            "200，负数向左）。对于中央无用的控件——分体按钮、滑杆——一次性把点击调到有效位置，不用每次都较劲。",
        "desc.snap_offset_y": "将点击点从元素中央纵向偏移（-200 到 "
            "200，负数向上）。与横向偏移同理：落在控件的有效部位。",
        "desc.stall_pause_seconds": "若扫描卡住，辅助暂停这么久，任何按住的点击都归还给您。",
        "desc.watcher_seconds": "经典模式中，在此时间内于同一位置附近再次吸附会变成对该目标的双击。",
        "ent.cancel_line": "有效至 %s——不会续费",
        "ent.canceled_line": "订阅已结束%s",
        "ent.expired_line": "于 %s 过期——请在 Stripe 续费",
        "ent.past_due_line": "付款失败——请在 Stripe 收据邮件中修复卡片；账单付清后访问恢复",
        "ent.plan": "（%s）",
        "ent.refunded_line": "已退款 / 已拒付——授权已撤销",
        "ent.st.active": "有效",
        "ent.st.canceled": "已结束",
        "ent.st.canceling": "有效但将取消",
        "ent.st.grant": "支持赠予",
        "ent.st.past_due": "付款失败",
        "ent.st.refunded": "已退款 / 已拒付",
        "ent.st.trial": "试用",
        "ent.st.unsubscribed": "无订阅",
        "ent.until": " 至 %s",
        "err.auth_unreachable": "Snappy AI 认证服务器无法连接：\n%s\n\nSnappy "
            "AI 只在得到它的实时应答时运行。\n重试？",
        "err.start_fail": "Snappy AI 无法启动。\n请用 --console 运行以查看详情。",
        "gate.btn.monthly": "月度订阅 9.99€",
        "gate.btn.trial": "试用购买 1.99€",
        "gate.head.canceled": "此订阅已取消——请在 Stripe 新建一个以继续。",
        "gate.head.canceling": "您的订阅将取消——在 %s "
            "之前仍然有效，之后除非续费，此登录将重新锁定。",
        "gate.head.email_mismatch": "付款使用的邮箱与您的 Discord "
            "帐户不同。订阅只对下方显示的 Discord 邮箱有效——请用它重新订阅，或联系支持。",
        "gate.head.expired": "此登录的订阅已过期——请在 Stripe 续费以继续。",
        "gate.head.none": "您已登录，但此登录没有有效订阅。请用此 Discord "
            "邮箱付款——其他地址的购买无法激活它。",
        "gate.head.past_due": "上次订阅付款失败——请在 Stripe 修复，以重新启用此登录。",
        "gate.head.refunded": "此购买已退款或被拒付，授权已被撤销。在此 Discord "
            "邮箱上新建订阅即可重新激活。",
        "gate.head.shared": "此帐户此刻正在另一台电脑上运行 Snappy AI。同一 Discord "
            "帐户在两地运行期间本软件保持关闭——请关闭另一个会话后重新检查。共享订阅会抬高价格；请勿如此。",
        "gate.msg.active": "订阅有效——正在启动 Snappy AI…",
        "gate.msg.checking": "正在向服务器检查…",
        "gate.msg.no_link": "此版本未配置该付款链接。",
        "gate.msg.open_fail": "无法打开浏览器。请手动打开此链接：\n%s",
        "gate.msg.open_ok": "Stripe 已在浏览器中打开 - 在那里付款。此窗口会自己发现付款并启动引擎。",
        "gate.msg.session_gone": "会话已失效——请重新登录。",
        "gate.msg.still_none": "此登录仍无有效订阅。",
        "gate.msg.still_shared": "仍在另一台电脑上使用——请关闭该会话后重新检查。",
        "gate.msg.unreachable": "无法连接认证服务器：%s",
        "gate.note": "订阅生效后引擎即启动——本窗口每 30 秒自动复查。关闭则返回登录。",
        "gate.prices": "2 天试用：1.99€（一次性）  -  订阅：9.99€ / 月。\n付款后最多约 "
            "10 分钟生效；续费会自动重新激活同一登录。",
        "gate.title": "%s - 订阅%s",
        "hdr.build": "版本 %s",
        "help.1.b": "Snappy AI "
            "观察光标周围的屏幕，找到附近结实的、像目标的东西——按钮、图标、链接——并选出最佳者：边缘清晰、尺寸合适、离光标近者胜出。您的颜色、永不点击列表和上次点击的记忆可以影响选择。然后光标瞄准目标的中心，而非其方框的角。",
        "help.1.t": "点击时发生了什么",
        "help.10.b": "1. 启动了吗？暂停意味着什么都不拦截——“快捷键：开始辅助”（默认 "
            "Ctrl+L）是唯一的开关。  2. 按住 Shift 点一次，确认问题是否出在辅助。  3. "
            "选错目标：调小“距光标多远的搜索范围”，然后设置“我的颜色”或提高“颜色优先强度”。  4. "
            "找不到：调低“边缘可以多淡”和“最低边缘清晰度”，调高“最大宽度或高度”或“粘合相近的碎片”。  5. "
            "某物永不应被辅助：把它的颜色放进它的颜色放进“永不点击的颜色”。  6. "
            "仍不对：向支持说明您点了什么、期望什么，并附上 Snappy AI 写入其数据文件夹的日志文件。",
        "help.10.t": "出问题时按此顺序检查",
        "help.2.b": "引导模式（默认）不吃点击：您的点击送达程序，松开后光标移到最近的清晰目标。经典模式更强：在目标附近的误点会被接住，光标吸附并由 "
            "Snappy AI "
            "替您点击。“距光标多远的搜索范围”决定搜索圆——想要的目标稍够不着时调大，选错邻居时调小。按住 Shift "
            "可在两种模式中绕过一次点击。",
        "help.2.t": "先从这里开始：模式与搜索范围",
        "help.3.b": "在“处理”页，“边缘可以多淡”和“最低边缘清晰度”决定哪些边缘算数：调低找到更淡的，调高忽略噪声。“最小目标尺寸”“最大目标面积”“最大宽度或高度”筛掉噪点与整窗口。“粘合相近的碎片”把断裂轮廓或图标加标签合成一个目标。在“辅助”页，“自动适应昏暗屏幕”和“按相对亮度评判边缘”让暗色主题表现得像亮色——请保持开启。",
        "help.3.t": "什么都找不到——或找到太多",
        "help.4.b": "在“颜色”页，“我的颜色”是偏爱的颜色，“永不点击的颜色”是绝对的：含该颜色的目标永不被辅助。“只辅助我的颜色”把辅助限制在匹配的目标上。在“处理”页，“颜色匹配严格度”规定色调需要多接近，“接受相近色调”让更亮或发灰的版本部分计入，“颜色优先强度”规定您的颜色给目标加多少分——选错目标时提高它。",
        "help.4.t": "使用颜色",
        "help.5.b": "“记住上次点击的目标”在“记住多久”秒内继续偏爱您上次成功点击落到的目标——这让滚动条和对话框按钮变得顺手。“记忆强度”规定它赢的力度，“记忆可以学习什么”保护它：选“仅我的颜色”时误点不会带偏记忆。“按住按键时跟随目标”稳定拖动；“实验”页的右键动作可以用鼠标跟随或清除记忆。",
        "help.5.t": "反复点击同一控件",
        "help.6.b": "“提前瞄准移动的目标”测量所选目标的移动速度，并按“提前瞄准多少”毫秒提前瞄准，使点击落在滚动列表或视频进度条上而不是其后方。提前量上限 "
            "80 像素，对静止或转向的目标自动关闭。",
        "help.6.t": "点击移动的东西",
        "help.7.b": "“动画移动光标” = 0 立即跳移；40-120 "
            "滑动以便观看，自己移动鼠标会取消滑动。“双击判定窗口”在经典模式中把同一位置附近的第二次吸附变成双击。“快速连点时每次都辅助”辅助连点中的每一次而非仅第一次。“卡顿后的暂停”是安全阀：扫描卡住时把按住的点击归还给您。",
        "help.7.t": "点击的手感",
        "help.8.b": "“快捷键”页解释两种模式与录制流程。简言之：带 Ctrl、Alt、Shift 或 Win "
            "的快捷键在系统层面保留；裸单键随处触发且照常输入。宏把一次被屏蔽的按键变成一整个组合。录制捕获您真实的输入——每个按键、鼠标点击和光标移动——并从宏页回放，每条带有自己的播放一次或循环到停止开关。",
        "help.8.t": "按键、宏与录制",
        "help.9.b": "“导出设置”旁的“语言”按钮——登录窗与订阅窗中也有——立即切换整个界面，无需重启，并记住您的选择。仍在翻译中的语言不会提供，因此能选到的都是完整的。",
        "help.9.t": "语言",
        "help.sub": "每个设置都用您在其页签上看到的名称，按您需要的顺序排列。悬停名称可看一行说明；本页是长版。",
        "help.tail": "设置在按下“应用”后生效。程序旁的 config.ini 会覆盖 "
            "config.json。本页只解释，不设置。",
        "help.title": "用大白话调校 Snappy AI",
        "kb.keys.b": "含 Ctrl、Alt、Shift 或 Win 的快捷键在系统层面被保留：只有 Snappy "
            "AI 看得到。裸单键（如 1 或 "
            "2）在所有程序中生效并且照常输入——代价是句子中间按下它也会触发其动作。想要经典行为，请在“辅助”页打开“单键快捷键吞掉该键”。宏更进一步：启动时触发键被吞掉，旁边的组合正好发送一次。",
        "kb.keys.t": "单键与组合键",
        "kb.mode.b": "引导模式（默认，快捷键 "
            "2）：您的点击总是原样送达程序；松开按键后光标移到最近的清晰目标上，下一次点击从那里开始。任何点击都不被吞掉——最安全的模式。 "
            " 经典模式（快捷键 1）：若您在目标附近点击，这次误点会被接住，光标吸附到目标上并由 Snappy AI "
            "替您点击；若附近没有目标，您的点击原样归还。  两种模式中，点击时按住 Shift 可让该次点击绕过辅助。",
        "kb.mode.t": "两种模式做什么",
        "kb.rec.b": "启动时按下开始录制快捷键（默认 "
            "Ctrl+Alt+R）：您按下的每个键、点击的每个鼠标按键和每次光标移动都被记录，并且仍然送达您的程序，因此录制时您可正常工作。按停止快捷键（Ctrl+Alt+S）把它保存到宏页的列表——那里可容纳五条录制。点击一条录制以选中它，进行“重命名”或“导出”，并设置它自己的“循环直到停止”开关。播放快捷键（Ctrl+Alt+M）播放那里选中的录制；Ctrl+1 "
            "到 Ctrl+5 按列表位置播放。暂停时不记录也不注入——您的输入完全归您。",
        "kb.rec.t": "如何录制并回放自己的按键和鼠标输入",
        "lang.close": "关闭",
        "lang.coverage": "已翻译 %d%%",
        "lang.current": "当前：%s",
        "lang.progress": "仍在翻译中，完成后提供：%s",
        "lang.prompt": "更改立即生效——窗口保持打开，可试用多种语言。",
        "lang.title": "语言",
        "lbl.accent_boost": "颜色优先强度",
        "lbl.accent_coherent": "忽略零散的色点",
        "lbl.accent_color": "我的颜色",
        "lbl.accent_matcher": "颜色匹配引擎",
        "lbl.accent_only": "只辅助我的颜色",
        "lbl.accent_soft": "接受相近色调",
        "lbl.accent_tolerance": "颜色匹配严格度",
        "lbl.accent_variants": "识别我颜色的亮/暗状态",
        "lbl.adaptive_threshold": "自动适应昏暗屏幕",
        "lbl.auto_click": "自行点击项目",
        "lbl.auto_click_interval": "自动点击的间隔秒数",
        "lbl.auto_click_max_clicks": "每次会话的自动点击上限",
        "lbl.auto_click_min_contrast": "自动点击目标需多清晰",
        "lbl.auto_click_radius": "从屏幕中央向外查找",
        "lbl.auto_click_repeat_px": "不重复点击同一处",
        "lbl.auto_click_settle_ms": "自动点击前的停顿",
        "lbl.block_bound_keys": "单键快捷键吞掉该键",
        "lbl.capture_backend": "屏幕截取引擎",
        "lbl.color_adapt": "适应屏幕光线",
        "lbl.contrast_threshold": "边缘可以多淡",
        "lbl.exclude_color": "永不点击的颜色",
        "lbl.follow_boost": "记忆强度",
        "lbl.follow_enabled": "记住上次点击的目标",
        "lbl.follow_learn": "记忆可以学习什么",
        "lbl.follow_seconds": "记住多久",
        "lbl.glide_ms": "动画移动光标",
        "lbl.hold_follow": "按住按键时跟随目标",
        "lbl.key_launch": "快捷键：开始辅助",
        "lbl.key_mode1": "快捷键：经典模式（最多4键）",
        "lbl.key_mode2": "快捷键：引导模式（最多4键）",
        "lbl.key_pause": "快捷键：暂停",
        "lbl.key_play": "快捷键：播放所选录制",
        "lbl.key_play_n": "快捷键：播放录制 #%d",
        "lbl.key_record": "快捷键：开始录制",
        "lbl.key_record_stop": "快捷键：停止并保存录制",
        "lbl.luminance_norm": "按相对亮度评判边缘",
        "lbl.macro_action": "宏 %d：改发组合",
        "lbl.macro_key": "宏 %d：按此键",
        "lbl.max_area": "最大目标面积",
        "lbl.max_dim": "最大宽度或高度",
        "lbl.merge_distance": "粘合相近的碎片",
        "lbl.min_area": "最小目标尺寸",
        "lbl.min_contrast": "最低边缘清晰度",
        "lbl.motion_3d": "移动目标智能跟随",
        "lbl.motion_lead_ms": "提前瞄准多少",
        "lbl.motion_predict": "提前瞄准移动的目标",
        "lbl.watch_center_only": "仅注视屏幕中心",
        "desc.watch_center_only": "辅助功能只扫描屏幕正中心的固定方框（大小=搜索距离，默认150×150像素），与光标位置无关。该方框之外的点击保持原样。",
        "lbl.center_follow": "屏幕跟随目标",
        "desc.center_follow": "开启“仅注视屏幕中心”时：吸附到某个元素后，辅助功能会移动屏幕使其保持在中心——尤其适用于滚动画板。自己移动屏幕即可解除跟随。",
        "lbl.input_backend": "输入方式",
        "desc.input_backend": "Windows注入（默认）到处可用。Interception通过驱动发送，游戏将其识别为真实鼠标；需要已安装Interception驱动并在程序旁放置interception.dll；否则自动改用Windows注入。",
        "val.input_backend.win32": "Windows注入",
        "val.input_backend.interception": "Interception（驱动）",
        "lbl.mouse2_action": "右键附加动作",
        "lbl.mouse2_hold_action": "右键长按附加动作",
        "lbl.on_target_dist": "“已点中”的距离",
        "lbl.radius": "距光标多远的搜索范围",
        "lbl.rapid_click_snap": "快速连点时每次都辅助",
        "lbl.snap_offset_x": "点击点：左右偏移",
        "lbl.snap_offset_y": "点击点：上下偏移",
        "lbl.stall_pause_seconds": "卡顿后的暂停",
        "lbl.watcher_seconds": "双击判定窗口",
        "login.failed": "%s 登录未完成——请重试。",
        "login.no_provider": "此副本未内置登录提供商。",
        "login.not_configured": "此版本尚未配置订阅文件。",
        "login.note": "登录会打开浏览器，并自行回到本窗口。",
        "login.provider": "使用 %s 登录",
        "login.signedin": "已登录为 %s。",
        "login.sub": "使用 Discord 登录——您的订阅绑定到此帐户，付款必须使用其邮箱。这里不需要密码。",
        "login.title": "%s - 登录",
        "login.unreachable": "无法连接认证服务器：%s",
        "login.waiting": "等待浏览器——请完成 %s 登录…",
        "mac.delete": "删除",
        "mac.empty": "还没有录制——启动后按下您的录制快捷键并正常工作：每个按键、点击和光标移动都会被捕获。",
        "mac.export": "导出",
        "mac.import": "导入",
        "mac.keys_head": "按键宏",
        "mac.loop": "循环直到停止",
        "mac.recordings": "录制",
        "mac.rename": "重命名",
        "mac.row": "宏 %d",
        "mac.sends": "发送",
        "mac.steps": "%d 步",
        "note.advanced": "距离与时间设置，改变点击的手感而非找到什么。多数人无需碰这些；默认值是经过测试的。",
        "note.assist": "每个改变启动后行为的开关。两种模式用您的模式键切换——“快捷键”页解释每种模式做什么。辅助总是以暂停启动；启动是唯一的开关。引擎看哪里、点击手感如何，在“高级”；什么算目标，在“处理”。",
        "note.colors": "顶部的两个列表决定 Snappy AI "
            "偏好或拒绝哪些颜色。每个列表都在右侧以方块显示自己的颜色，最多 15 "
            "个，点击方块即可再次移除该颜色；空列表显示一个带红叉的方块，表示关闭。“添加到首选颜色”和“添加到拒绝颜色”会把调色器中当前的颜色放入对应的列表。当前 "
            "RGB 值显示三个方块——每个都有五个颜色方块那么宽，因此这一行正好横跨与下方所有内容相同的 15 "
            "个方块——分别按调色器中颜色所含红、绿、蓝的多少而发亮；该行跟随调色器，不能输入。下方的调色器像绘图软件一样混合颜色；它旁边的一切都靠窗口右侧，与上方设置保持相同的边距，且每一行都横跨同样的 "
            "15 方块宽度：内部画有 #色值的高展示条、然后是 15 "
            "个预设色、两个添加按钮和屏幕行——“从屏幕取色”取光标下的单个颜色，“从屏幕建议颜色”用光标周围找到的颜色填满自己的 "
            "15 个方块，点击其中一个即载入调色器。展示条加高是有意为之：这让建议色方块的下缘恰好与左侧的颜色滑条齐平。",
        "note.experimental": "引擎选择，每项都有经过测试的默认值。仅在对比引擎、特殊硬件或支持人员要求时更改——截取引擎重启后生效。",
        "note.handler": "什么算可点击目标：边缘可以多淡、必须多清晰、目标可以多大或多小。找不到？放宽这些。找错？收紧它们，或在“颜色”页使用您的颜色。",
        "note.keybindings": "所有快捷键——以及下方：两种模式做什么、如何录制自己的按键和鼠标输入、单键与组合键的区别。",
        "note.macros": "宏在启动时把一次按键变成一整个组合。宏旁边是您的录制：最多五条命名捕获，记录您做的一切——每个按键、鼠标点击和光标移动——并按录制原样回放。点击一条录制以选中它；每行带有自己的“循环直到停止”开关，“重命名”、“导出”、“导入”和“删除”位于框的底部。",
        "note.macros_keys": "录制/播放快捷键在“快捷键”页（默认：Ctrl+Alt+R "
            "录制，Ctrl+Alt+S 停止并保存，Ctrl+Alt+M 播放，Ctrl+1..5 按列表播放）。",
        "online.cancelled": "Discord 认证已取消（或失败）。请重试。",
        "rec.export_fail": "导出失败：%r",
        "rec.exported": "已导出到 %s",
        "rec.import_fail": "导入失败：%r",
        "rec.imported": "已导入 %d 条录制%s。",
        "rec.imported_none": "（没有有效的）",
        "rec.no_sel": "未选择要导出的内容。",
        "rec.notfile": "导入失败：不是录制文件。",
        "shared.back": "欢迎回来——准备好后按“启动”。",
        "shared.body": "此 Discord 帐户正在另一台电脑上运行 Snappy "
            "AI。\n在只剩一个会话之前，此处辅助暂停。\n\n一份订阅、同时一台机器——这才能\n保持低价并让开发持续。",
        "shared.close": "关闭",
        "shared.recheck": "立即重新检查",
        "shared.still": "仍在别处使用——保持暂停。",
        "shared.title": "帐户在别处使用",
        "shared.unreachable": "无法连接服务器——将重新检查。",
        "st.all_files": "所有文件",
        "st.color_added": "rgb(%d, %d, %d) 已加入 %s - 按“应用”保存。",
        "st.color_already": "rgb(%d, %d, %d) 已在 %s 中。",
        "st.color_full": "%s 已有 15 种颜色 - 请先点击其中一个色块移除一种颜色。",
        "st.color_removed": "rgb(%d, %d, %d) 已从 %s 移除 - 按“应用”保存。",
        "st.delete_confirm": "删除录制 %r？\n此操作无法撤销。",
        "st.deleted": "录制已删除。",
        "st.engine_dead": "引擎线程不可用——快捷键无响应。",
        "st.ent_paused": "订阅 %s——辅助暂停。请在 Stripe 续费后重启。",
        "st.ent_unreachable": "订阅复查：无法连接服务器（会话继续运行）。",
        "st.export_fail": "导出失败：%r",
        "st.export_rec_title": "导出录制",
        "st.export_title": "导出设置",
        "st.exported": "设置已导出到 %s",
        "st.file_rec": "Snappy AI 录制",
        "st.file_settings": "Snappy AI 设置",
        "st.follow": "  |  跟随 %d 秒前",
        "st.import_fail": "导入失败：%r",
        "st.import_notfile": "导入失败：不是设置文件。",
        "st.import_rec_title": "导入录制",
        "st.import_title": "导入设置",
        "st.imported": "已导入 %d 项设置%s。",
        "st.imported_ignored": "，已忽略：%s",
        "st.ini_over": "已应用，但 config.ini 覆盖了：%s",
        "st.lib_empty": "列表为空——没有可导出的内容。",
        "st.line": "已辅助 %d  |  已放行 %d%s  |  主题：%s",
        "st.loop_desc": "此录制的播放方式：关 = 播放一次；开 = "
            "重复直到您再次按下播放快捷键。每条录制有自己的开关，随录制本身保存。",
        "st.name_empty": "名称不能为空。",
        "st.pick_err": "取色失败：%r",
        "st.pick_fail": "取色失败——请重试。",
        "st.pick_ok": "在 (%d, %d) 取到 rgb(%d, %d, %d)。",
        "st.pick_wait": "把光标移到颜色上——3 秒后取色…",
        "st.preset_desc": "预设色：%s——点击载入取色器。",
        "st.rec_count": "%d / 5 条录制",
        "st.rec_now": "%r 现在：%s。",
        "st.rec_once": "播放一次",
        "st.rec_playing": "正在播放 %r…",
        "st.rec_playing_loop": "正在播放 %r 直到停止",
        "st.rec_recording": "录制中——按 %s 停止并保存",
        "st.rec_repeats": "循环直到停止",
        "st.registered": "注册于：%s    状态：%s",
        "st.rename_prompt": "录制 #%d 的新名称：",
        "st.renamed": "录制已重命名。",
        "st.reset_confirm": "将所有设置重置为默认？\n帐户保留；只影响设置。",
        "st.rgb_bad": "请先输入有效的 R/G/B 值。",
        "st.running": "运行中..",
        "st.saved": "已保存并应用。",
        "st.defaults_restored": "已恢复默认设置。",
        "st.saved_bad": "已保存，但无效（保留旧值）：%s",
        "st.select_rec": "请先选择一条录制。",
        "st.shared_paused": "帐户在别处使用——辅助暂停；一份订阅 = 一台机器。",
        "st.standby": "待机..",
        "st.sug_fail": "建议失败：%r",
        "st.sug_loaded": "建议色 rgb(%d, %d, %d) "
            "已载入调色器——用上方的按钮把它加入某个列表。",
        "st.sug_loaded_desc": "建议的界面颜色 rgb(%d, %d, %d)——占采样区域 "
            "%d%%。点击载入取色器。",
        "st.sug_none": "该区域没有颜色建议。",
        "st.sug_ok": "%d 个建议——点击一个即可载入到调色器。",
        "st.sug_wait": "指向您正在使用的应用——3 秒后采样…",
        "tab.advanced": "高级",
        "tab.assist": "辅助",
        "tab.colors": "颜色",
        "tab.experimental": "实验",
        "tab.handler": "处理",
        "tab.help": "帮助",
        "tab.hotkeys": "快捷键",
        "tab.macros": "宏",
        "theme.dark": "深色",
        "theme.light": "浅色",
        "val.accent_matcher.hsv": "经典 - 旧引擎",
        "val.accent_matcher.oklab": "感知式 - 按颜色实际观感（推荐）",
        "val.capture_backend.auto": "自动 - 最快且带安全回退",
        "val.capture_backend.dxcam": "Desktop Duplication - 多数电脑最快",
        "val.capture_backend.mss": "兼容 - 始终可用（远程桌面、虚拟机）",
        "val.capture_backend.wgc": "Windows Graphics Capture - 实验性",
        "val.follow_learn.accent": "仅我的颜色中的元素",
        "val.follow_learn.any": "每次成功吸附",
        "val.mouse2_action.1": "清除当前跟随任务",
        "val.mouse2_action.2": "跟随上次吸附的颜色",
        "val.mouse2_action.3": "取光标下的颜色并跟随",
        "val.mouse2_action.4": "什么都不做",
        "val.mouse2_hold_action.1": "清除当前跟随任务",
        "val.mouse2_hold_action.2": "跟随上次吸附的颜色",
        "val.mouse2_hold_action.3": "取光标下的颜色并跟随",
        "val.mouse2_hold_action.4": "什么都不做",
        "word.off": "关",
        "word.on": "开",
    },
    "ja": {
        "btn.apply": "適用",
        "btn.export": "設定を書き出す",
        "btn.import": "設定を読み込む",
        "btn.language": "言語: %s",
        "btn.launch": "起動",
        "btn.logout": "ログアウト",
        "btn.pause": "一時停止",
        "btn.restore": "既定値に戻す",
        "col.accent": "アクセント",
        "col.add_pref": "優先する色に追加",
        "col.add_ref": "拒否する色に追加",
        "col.chip_desc": "rgb(%d, %d, %d)（%s の色）- "
            "箱をクリックするとこの色が削除されます。",
        "col.chip_off": "%s に色はありません - "
            "バツ印の枠はオフの意味です。下で色を選んで、対応する追加ボタンを押してください。",
        "col.exclude": "除外",
        "col.pick": "画面から色を取得",
        "col.rgb.desc": "3つの箱は、今ピッカーにある色を示します: "
            "1つ目はその赤の量に応じて輝き、2つ目は緑、3つ目は青 - "
            "明るいほど多いことを意味します。この行はピッカーと既製色と画面ボタンに従います。入力はできません。",
        "col.rgb.name": "現在のRGB値",
        "col.suggest": "画面から色を提案",
        "desc.accent_boost": "自分の色が対象をどれだけ押し上げるか（0-3）。 誤った対象が勝つなら "
            "1.5-2 へ。",
        "desc.accent_coherent": "あなたの色はつながった塊を作って初めて有効です——散らばったディザや圧縮ノイズでは要素は認定も強化もクリック禁止リスト入りもしません。",
        "desc.accent_color": "Snappy AI "
            "に優先させたい色。右側に色の箱として表示されます。下で色を選び、「優先する色に追加」を押すと追加されます - "
            "最大15箱。箱をクリックするとその色を再度取り除けます。これらを含むアイテムは同点時に勝みます。空のリストはバツ印の箱を表示し、設定を無効にします。",
        "desc.accent_matcher": "色の比較方法。知覚式は色の見え方で順位付けし推奨。クラシックは比較用の旧エンジン。",
        "desc.accent_only": "自分の色を含む対象だけがアシスト対象。それ以外のクリックはそのまま "
            "Windows へ。",
        "desc.accent_soft": "0-100: 明るい/暗い/色あせた版をどの程度カウントするか。0 = "
            "正確な色調のみ。",
        "desc.accent_tolerance": "色がどれほど近ければ自分の色とみなすか（4-90）。低いほど厳格。",
        "desc.accent_variants": "あなたの色の明るい・暗い複製も一致とみなし、ホバー・押下・減光状態が色相許容を広げずに有効になります。明度だけ——違う色相が紛れ込むことは決してありません。",
        "desc.adaptive_threshold": "ダークテーマや色あせた文書は自分の検出基準を自動で下げるため、淡い対象も見つかります。オン推奨。",
        "desc.auto_click": "オンにすると、監視領域内の最良アイテムへ0.1秒ごとに自動クリックします。判定はまずコントラスト優先。アクセントカラー設定時はその色を持つアイテムのみが対象。色なしでは非常にくっきり描かれたアイテムだけがクリックされます。同じ場所を二度はクリックせず、自ウィンドウも絶対にクリックしません。",
        "desc.auto_click_interval": "あなたの色のために画面を調べる間隔（0.5-60）。遅い数値が安全です：見守るダイアログには "
            "2-5 が向きます。",
        "desc.auto_click_max_clicks": "起動後に自動でクリックできる回数（1-200）。上限に達したら止まって知らせるので、誤設定が暴走しません。",
        "desc.auto_click_min_contrast": "「縁の最低鮮明さ」と同じ尺度です。既定から始め、誤クリックしたら上げます：強く鮮明に描かれた要素だけが対象になります。",
        "desc.auto_click_radius": "自動クリックは画面中央の周りを探します（40-600 "
            "ピクセル）。忙しい窓には広く；中央の一つの部品だけ見せるには狭く。",
        "desc.auto_click_repeat_px": "自動クリック後、このピクセル以内の対象は放っておきます（0-400）。これがないと画面に残るボタンが何度もクリックされます。",
        "desc.auto_click_settle_ms": "クリック前にカーソルが対象の上でこう休み（0-2000 "
            "ミリ秒）、プログラムが先に強調表示を見ます。120 はほとんどの窓に向きます。",
        "desc.block_bound_keys": "オフ（既定）: Ctrl/Alt/Shift "
            "のないショートカット（1 や V "
            "など）はすべてのアプリで効き、かつ通常どおり入力されます。つまり文中で押すと動作も発動します。オン: "
            "動作は引き続きどこでも発動しますが、キーは入力されません。",
        "desc.capture_backend": "画面の撮影方法。自動は互換方式を使用し、ほぼすべてのウィンドウを捉えます。互換はリモートデスクトップや仮想マシンでも常に動作。再起動後に有効。",
        "desc.color_adapt": "各要素は照合前に自身の背景でホワイトバランスを取るので、夜間モードやテーマの色かぶりであなたの色が許容範囲から外れなくなります。未適応の照合との比較のためだけに切ってください。",
        "desc.contrast_threshold": "低くすると淡い対象まで発見（ノイズも増）、高くするとよりくっきりした縁を要求。",
        "desc.default": "設定名にカーソルを合わせると説明が表示されます。",
        "desc.exclude_color": "これらの色を含むアイテムは決して支援されません: クリックは両モードで直接 "
            "Windows に渡ります。右側に色の箱として表示 - "
            "下で色を選び、「拒否する色に追加」を押すと1つ追加されます(最大15)。箱をクリックすると取り除かれます。空のリストはバツ印の箱を表示し、設定を無効にします。",
        "desc.follow_boost": "記憶した対象が同点で勝つ強さ: 100% "
            "は新鮮な間に対象の得点を2倍にし得る、25% は軽い後押し。",
        "desc.follow_enabled": "成功したスナップの後、似た見た目や同じ場所の対象がしばらく優先されます。スクロールバーや同じボタンへの繰り返しクリックに便利。",
        "desc.follow_learn": "自分の色のみ: 誤クリックが記憶を連れ去れない。すべての成功スナップ: "
            "旧来の信頼型。",
        "desc.follow_seconds": "最後の成功スナップ後、記憶した対象が優先され続ける秒数（1-120）。",
        "desc.glide_ms": "0（既定）は即時ジャンプで最速。40-120 "
            "は滑るように動き見やすい。自分でマウスを動かすと中止。",
        "desc.hold_follow": "スナップ直後に左ボタンを押し続ける——または記憶した対象上で再び押す——と、カーソルはその対象の色の上に留まります。スクロールバーのつまみなどのドラッグが安定します。それ以外の場所での押しは影響しません。",
        "desc.key_launch": "形式: ctrl+l, f5, space, ctrl+alt+1 …修飾鍵: "
            "ctrl, alt, shift, win。適用後に有効。",
        "desc.key_mode1": "カンマ区切り、例 '1, f1, ctrl+f1, "
            "v'。クラシックモードの説明はショートカットのタブ。",
        "desc.key_mode2": "カンマ区切り、例 '2, f2, ctrl+f2, "
            "b'。ガイドモードの説明はショートカットのタブ。",
        "desc.key_pause": "起動するまで、マウスもキーボードも完全にあなた自身。",
        "desc.key_play": "マクロ一覧で選択中の記録を再生。未選択なら最新。繰り返しの記録で押すと停止。",
        "desc.key_play_n": "マクロタブの番号付き一覧から #%d "
            "番の記録を位置どおり再生。一覧が短ければ何もしない。",
        "desc.key_record": "あなたが行うすべて - "
            "すべてのキー、すべてのマウスクリック、すべてのカーソル移動 - "
            "を記録します。入力はそのままアプリに届き続け、停止ショートカットがマクロリストに保存するまで続きます。起動中のみ待機。",
        "desc.key_record_stop": "記録を停止し、マクロ一覧へ保存、実行中の再生も停止。",
        "desc.luminance_norm": "縁を周囲の明るさに対する相対で評価するため、ダークテーマもライトテーマと同じように働きます。オン推奨。",
        "desc.macro_action": "トリガー1押しごとに代わりに押される組合せ（1押し = 1組合せ）: "
            "'ctrl+c', 'ctrl+shift+s', 'space', 'f5' …空欄 = マクロ無効。",
        "desc.macro_key": "入力の代わりにマクロを意味するキー: 'b', 'f7', 'ctrl+b' "
            "…起動中は1押しで隣りの組合せをちょうど1回送り、キー自体はアプリへ届かない。停止中は通常入力。空欄 = "
            "マクロ無効。",
        "desc.max_area": "これより大きいしみは無視——通常は窓全体や壁紙であり、クリック対象ではない。",
        "desc.max_dim": "これより幅広い/高い対象は無視。スクロールバーなど画面端の対象は2倍まで許可。",
        "desc.merge_distance": "これより近い破片（途切れた輪郭、ラベル隣のアイコン）を1つの対象に結合。2つの完全な対象は結合しない。",
        "desc.min_area": "これより小さいしみはノイズとして無視。大きな対象に結合される場合は除く。",
        "desc.min_contrast": "対象がクリック可能になるために必要な最低限の鮮明さ。 28 未満の値は 28 "
            "として扱われます：内蔵の品質下限がノイズのクリックを防ぎます。",
        "desc.motion_3d": "移動体を直線近似ではなく位置と大きさで追跡します：単発の不良走査は追跡を盲目化せず無視され、曲がりも追い、大きさの急変では追跡を再開します（走査が別要素を掴んだ合図）。速度ゲートと "
            "80 ピクセル上限は同じ——賢くなるのは頭だけです。単独で動作します。",
        "desc.motion_lead_ms": "動く対象を先回りするミリ秒（0-300）: 遅いスクロールは "
            "40-80、速いシークバーは 100-150。上限 80 px、遅い/方向転換中は無効。",
        "desc.motion_predict": "クリック中に動く対象（スクロール一覧、動画バー）では少し先を狙い、クリックが対象に乗るようにします。静止した対象は変わりません。",
        "desc.mouse2_action": "短い右クリックが追加でやること——右クリック自体は常に通常の "
            "Windows 機能。既定: なし。",
        "desc.mouse2_hold_action": "同じ選択肢を、クリックではなく右ボタンを約0.5秒長押ししたときに発動。1回の押しはクリックか長押しのどちらか。既定: "
            "なし。",
        "desc.on_target_dist": "クリックが対象の中心からこのピクセル以内なら何も動かない——命中しています。",
        "desc.radius": "ピクセル単位の探索距離（40-400）。欲しい対象がもう少し遠いなら大きく、隣の対象が勝つなら小さく。",
        "desc.rapid_click_snap": "オフ（既定）: クリック処理中は他が Windows へ。オン: "
            "左クリックはすべてアシスト。",
        "desc.snap_offset_x": "クリック位置を要素中央から横にずらします（-200〜200、マイナスは左）。中央が死んでいる部品——分割ボタン、スライダー——では毎回格闘せず一度だけ有効位置に合わせます。",
        "desc.snap_offset_y": "クリック位置を要素中央から縦にずらします（-200〜200、マイナスは上）。横のずれと同じ考え：部品の生きている部分に落とします。",
        "desc.stall_pause_seconds": "スキャンが詰まったら、この時間アシストを停止し、押されていたクリックはあなたへ返す。",
        "desc.watcher_seconds": "クラシックモードで、同じ場所近くへの2回目のスナップがこの時間内なら対象へのダブルクリックになる。",
        "ent.cancel_line": "%s まで有効 - 更新されません",
        "ent.canceled_line": "サブスクリプション終了%s",
        "ent.expired_line": "%s に期限切れ——Stripe で更新を",
        "ent.past_due_line": "支払失敗——Stripe "
            "の受領メールでカードを修正。請求が払われるとアクセス復帰",
        "ent.plan": "（%s）",
        "ent.refunded_line": "返金 / チャージバック——有効化は取消",
        "ent.st.active": "有効",
        "ent.st.canceled": "終了",
        "ent.st.canceling": "有効だが取消予定",
        "ent.st.grant": "サポート付与",
        "ent.st.past_due": "支払失敗",
        "ent.st.refunded": "返金 / チャージバック",
        "ent.st.trial": "トライアル",
        "ent.st.unsubscribed": "サブスクリプションなし",
        "ent.until": " %s まで",
        "err.auth_unreachable": "Snappy AI "
            "の認証サーバーに接続できません:\n%s\n\nSnappy AI "
            "はそこからの応答があって初めて動作します。\n再試行しますか？",
        "err.start_fail": "Snappy AI を起動できませんでした。\n詳細は --console "
            "で実行してください。",
        "gate.btn.monthly": "月額サブスクリプション 9.99€",
        "gate.btn.trial": "トライアル購入 1.99€",
        "gate.head.canceled": "このサブスクリプションは取消済み——続行には Stripe で新規作成を。",
        "gate.head.canceling": "サブスクリプションはキャンセル予定——%s "
            "まで有効、以降は更新しない限りこのログインは再びロック。",
        "gate.head.email_mismatch": "支払いが Discord "
            "アカウントと違うメールで行われました。サブスクリプションは下記の Discord "
            "メールでのみ有効——それで再購読か、サポートへ。",
        "gate.head.expired": "このログインのサブスクリプションは期限切れ——続行には Stripe "
            "で更新を。",
        "gate.head.none": "サインイン済みですが、このログインに有効なサブスクリプションがありません。この "
            "Discord メールで支払って——別アドレスの購入は有効化できません。",
        "gate.head.past_due": "直近の支払が失敗——Stripe で修正するとこのログインが再度有効に。",
        "gate.head.refunded": "この購入は返金またはチャージバックされ、有効化は取り消されました。この "
            "Discord メールで新しいサブスクリプションを。",
        "gate.head.shared": "このアカウントは今、別のコンピュータで Snappy AI を実行中。同じ "
            "Discord "
            "アカウントが2箇所で動く間、本ソフトはオフ——他のセッションを閉じて再確認を。共有は価格を上げます。ご遠慮を。",
        "gate.msg.active": "サブスクリプション有効——Snappy AI を起動…",
        "gate.msg.checking": "サーバーに確認中…",
        "gate.msg.no_link": "この支払いリンクはこのビルドで未設定です。",
        "gate.msg.open_fail": "ブラウザを開けませんでした。手で開いてください:\n%s",
        "gate.msg.open_ok": "Stripeあなたのブラウザで開いています - そちらで支払いください。このウィンドウは支払いを自動的に気づき、エンジンを始動します。",
        "gate.msg.session_gone": "セッションが消えました——再サインインを。",
        "gate.msg.still_none": "このログインにはまだ有効なサブスクリプションがありません。",
        "gate.msg.still_shared": "依然ほかのコンピュータで使用中——そのセッションを閉じて再確認を。",
        "gate.msg.unreachable": "認証サーバーに接続できません: %s",
        "gate.note": "サブスクリプションが有効になるとエンジンが開始——この窓は30秒ごとに自動再確認。閉じるとサインインへ。",
        "gate.prices": "2日間トライアル: 1.99€（1回）  -  サブスクリプション: 9.99€ / "
            "月。\n有効化は支払後およそ10分以内。更新は同じログインを自動で再有効化。",
        "gate.title": "%s - サブスクリプション%s",
        "hdr.build": "ビルド %s",
        "help.1.b": "Snappy AI "
            "はカーソル周辺の画面を見て、近くのしっかりした対象らしいもの——ボタン、アイコン、リンク——を見つけ、最良のものを選びます: "
            "くっきりした縁、適切な大きさ、カーソル近さが勝ち。自分の色、クリック禁止一覧、前回のクリックの記憶が選択を傾け得ます。カーソルは枠の角でなく対象の中心を狙います。",
        "help.1.t": "クリック時に起きていること",
        "help.10.b": "1. 起動していますか？一時停止中は何も遮られません——「ショートカット: "
            "アシスト開始」（既定 Ctrl+L）が唯一のオン/オフ。  2. Shift "
            "を押しながら1クリックし、アシストが原因か確認。  3. 違う対象が勝つ: "
            "「カーソルから探す範囲」を下げ、次に「自分の色」を設定するか「色の優先強度」を上げる。  4. "
            "何も見つからない: "
            "「どれほど淡い縁まで認めるか」「縁の最低鮮明さ」を下げ、「最大の幅または高さ」や「近い破片を結合する」を上げる。 "
            " 5. 絶対にアシストさせたくないもの: その色を色を「クリック禁止の色」へ。  6. それでも駄目なら: "
            "何をクリックし何を期待したかをサポートに報告し、Snappy AI "
            "がデータフォルダーに書くログファイルを添えてください。",
        "help.10.t": "おかしいときはこの順で確認",
        "help.2.b": "ガイドモード（既定）はクリックを食べません: "
            "クリックはアプリへ届き、離すとカーソルが最寄りの明確な対象へ。クラシックモードは強力: "
            "対象近くの誤クリックを捕え、スナップして Snappy AI "
            "が代わりにクリック。「カーソルから探す範囲」が探索円を決定——届かないなら大きく、隣が勝つなら小さく。Shift "
            "長押しは1クリックだけ回避。",
        "help.2.t": "まず: モードと探索範囲",
        "help.3.b": "処理タブの「どれほど淡い縁まで認めるか」と「縁の最低鮮明さ」がどの縁を数えるかを決めます: "
            "低くすれば淡いものまで、高くすればノイズを無視。「最小の対象サイズ」「最大の対象面積」「最大の幅または高さ」がノイズと窓全体を除外。「近い破片を結合する」は途切れた輪郭やラベル隣のアイコンを1つに。アシストタブの「暗い画面に自動調整」と「縁を相対的な明るさで評価」はダークテーマをライト同様に——両方オンを推奨。",
        "help.3.t": "何も見つからない／見つかりすぎる",
        "help.4.b": "色タブの「自分の色」が優先色、「クリック禁止の色」は絶対: "
            "その色の対象は決してアシストされません。「自分の色のみアシスト」は合う対象に限定。処理タブの「色一致の厳しさ」は色調の近さの基準、「近い色調も受け入れる」は明るい/色あせた版を部分的にカウント、「色の優先強度」は自分の色が対象をどれだけ押すか——間違いが続けば上げて。",
        "help.4.t": "色の使い方",
        "help.5.b": "「最後にクリックした対象を記憶」は、最後の成功クリックが着地した対象を「記憶しておく時間」の秒数だけ優先し続け——スクロールバーやダイアログのボタンが快適に。「記憶の強さ」は勝ち方の強さ、「記憶が学べるもの」は保護: "
            "「自分の色のみ」なら誤クリックが記憶を連れ去れません。「ボタン長押し中は対象を追う」はドラッグを安定させ、実験タブの右ボタン動作はマウスで記憶を追従/解除できます。",
        "help.5.t": "同じ操作部への繰り返しクリック",
        "help.6.b": "「動く対象を先回りする」は選択した対象の移動速度を測り、「どれだけ先を狙うか」ミリ秒だけ先を狙うので、クリックがスクロール一覧や動画バーの後ろでなく上に着地。先回りは上限 "
            "80 ピクセル、静止や方向転換中の対象では自動で無効。",
        "help.6.t": "動くものをクリックする",
        "help.7.b": "「カーソル移動をアニメーション」= 0 は即時ジャンプ、40-120 "
            "は滑らかに動き自分でマウスを動かすと中止。「ダブルクリックの判定窓」はクラシックモードで同所近くの2回目スナップをダブルクリックに。「連打のたびにアシストする」は連打の最初だけではなく毎回アシスト。「詰まり後の一時停止」はスキャン詰まり時に押されたクリックを返す安全弁。",
        "help.7.t": "クリックの感触",
        "help.8.b": "「ショートカット」タブが2つのモードと記録の流れを説明します。要約: "
            "Ctrl、Alt、Shift、Winを含むショートカットはシステム全体で予約され、単独キーはどこでも発火し、かつ通常どおり入力されます。マクロは1回のブロックされたキー押しを1つの組合せ全体に変えます。記録はあなたの実際の入力 "
            "- すべてのキー、マウスクリック、カーソル移動 - "
            "を捉え、マクロタブから再生します。各記録は独自の1回再生または停止まで繰り返すスイッチを持ちます。",
        "help.8.t": "キー、マクロ、記録",
        "help.9.b": "「設定を書き出す」隣の「言語」ボタン——サインイン窓と購読窓にもあり——が再起動なしでインターフェース全体を即座に切替え、選択を記憶。翻訳中の言語は提示されないため、選べるものは常に完全です。",
        "help.9.t": "言語",
        "help.sub": "各タブに表示されている名前のまま、欲しい順に並べた全設定。名前にカーソルを合わせると1行説明、このページは長めの説明。",
        "help.tail": "設定は「適用」で有効に。プログラムと同じ場所の config.ini は "
            "config.json を上書き。このページは説明するだけで、設定は変更しません。",
        "help.title": "やさしい言葉で Snappy AI を調整",
        "kb.keys.b": "Ctrl/Alt/Shift/Win "
            "を含むショートカットはシステム全体で予約され、Snappy AI だけが認識。修飾鍵なしの単独キー（1 や 2 "
            "など）はすべてのアプリで効き、かつ通常どおり入力されます——ただし文中で押すと動作も発動するのが代償。古典的な挙動がよければアシストタブの「単独キーのショートカットはキーを吸収する」をオンに。マクロはさらに進み、起動中はトリガーキーを吸収し隣りの組合せをちょうど1回送ります。",
        "kb.keys.t": "単独キーと組合せキー",
        "kb.mode.b": "ガイドモード（既定、ショートカット 2）: "
            "クリックは常にそのままアプリへ。ボタンを離すとカーソルが最寄りの明確な対象へ移動し、次のクリックはそこから。何も吸われない、最も安全なモード。 "
            " クラシックモード（ショートカット 1）: "
            "対象の近くをクリックすると、その誤クリックを捕まえ、カーソルが対象にスナップし Snappy AI "
            "が代わりにクリック。近くに対象がなければクリックはそのまま返る。  どちらのモードでも、Shift "
            "を押しながらのクリックはその1回だけアシストを回避。",
        "kb.mode.t": "2つのモードの役割",
        "kb.rec.b": "起動中に記録開始ショートカット(既定は Ctrl+Alt+R)を押すと: "
            "押したすべてのキー、クリックしたすべてのマウスボタン、すべてのカーソル移動が記録され、かつそのままアプリにも届くので、記録中も通常どおり作業できます。停止ショートカット(Ctrl+Alt+S)でマクロタブのリストに保存されます "
            "- "
            "5件の記録が入ります。記録をクリックして選択し、「名前変更」や「書出し」を行い、独自の「停止まで繰り返す」スイッチを設定してください。再生ショートカット(Ctrl+Alt+M)はそこで選択した記録を再生し、Ctrl+1〜Ctrl+5はリストの位置で再生します。一時停止中は記録も注入もされません "
            "- 入力は完全にあなたのものです。",
        "kb.rec.t": "自分のキーとマウス入力を記録・再生する方法",
        "lang.close": "閉じる",
        "lang.coverage": "翻訳率 %d%%",
        "lang.current": "現在: %s",
        "lang.progress": "翻訳中のため未完成。完成次第表示: %s",
        "lang.prompt": "変更はすぐに反映されます。窓は開いたままなので複数試せます。",
        "lang.title": "言語",
        "lbl.accent_boost": "色の優先強度",
        "lbl.accent_coherent": "散らばった色点を無視",
        "lbl.accent_color": "自分の色",
        "lbl.accent_matcher": "色比較エンジン",
        "lbl.accent_only": "自分の色のみアシスト",
        "lbl.accent_soft": "近い色調も受け入れる",
        "lbl.accent_tolerance": "色一致の厳しさ",
        "lbl.accent_variants": "自分の色の明暗状態を認識",
        "lbl.adaptive_threshold": "暗い画面に自動調整",
        "lbl.auto_click": "自分でアイテムをクリック",
        "lbl.auto_click_interval": "自動クリックの間隔秒数",
        "lbl.auto_click_max_clicks": "セッションごとの自動クリック上限",
        "lbl.auto_click_min_contrast": "自動クリックのターゲットの鮮明さ",
        "lbl.auto_click_radius": "中央からの検索範囲",
        "lbl.auto_click_repeat_px": "同じ場所を再クリックしない",
        "lbl.auto_click_settle_ms": "自動クリック前の待ち時間",
        "lbl.block_bound_keys": "単独キーのショートカットはキーを吸収する",
        "lbl.capture_backend": "画面取得エンジン",
        "lbl.color_adapt": "画面の明るさに適応",
        "lbl.contrast_threshold": "どれほど淡い縁まで認めるか",
        "lbl.exclude_color": "クリック禁止の色",
        "lbl.follow_boost": "記憶の強さ",
        "lbl.follow_enabled": "最後にクリックした対象を記憶",
        "lbl.follow_learn": "記憶が学べるもの",
        "lbl.follow_seconds": "記憶しておく時間",
        "lbl.glide_ms": "カーソル移動をアニメーション",
        "lbl.hold_follow": "ボタン長押し中は対象を追う",
        "lbl.key_launch": "ショートカット: アシスト開始",
        "lbl.key_mode1": "ショートカット: クラシックモード（最大4キー）",
        "lbl.key_mode2": "ショートカット: ガイドモード（最大4キー）",
        "lbl.key_pause": "ショートカット: 一時停止",
        "lbl.key_play": "ショートカット: 選択中の記録を再生",
        "lbl.key_play_n": "ショートカット: 記録 #%d を再生",
        "lbl.key_record": "ショートカット: 記録開始",
        "lbl.key_record_stop": "ショートカット: 記録を停止して保存",
        "lbl.luminance_norm": "縁を相対的な明るさで評価",
        "lbl.macro_action": "マクロ %d: 代わりに送る",
        "lbl.macro_key": "マクロ %d: このキーを押す",
        "lbl.max_area": "最大の対象面積",
        "lbl.max_dim": "最大の幅または高さ",
        "lbl.merge_distance": "近い破片を結合する",
        "lbl.min_area": "最小の対象サイズ",
        "lbl.min_contrast": "縁の最低鮮明さ",
        "lbl.motion_3d": "移動体への賢い追従",
        "lbl.motion_lead_ms": "どれだけ先を狙うか",
        "lbl.motion_predict": "動く対象を先回りする",
        "lbl.watch_center_only": "画面中央のみを監視",
        "desc.watch_center_only": "アシストは画面正中の固定四角（サイズ＝検索距離、既定150×150px）だけを対象にします。カーソルの位置は関係ありません。その四角の外でのクリックは変更されません。",
        "lbl.center_follow": "画面がターゲットを追う",
        "desc.center_follow": "「画面中央のみを監視」ON時：アイテムを捕らえた後、アシストはそれを中央に保つよう画面を動かします（スクロール平面で特に有効）。自分で画面を動かすと追従が解除されます。",
        "lbl.input_backend": "入力方法",
        "desc.input_backend": "Windowsインジェクション（既定）はどこでも動作します。Interceptionはドライバ経由で送信し、ゲームは実マウスとして認識します。Interceptionドライバのインストールとプログラム横のinterception.dllが必要。無い場合は自動的にWindowsインジェクションへ戻ります。",
        "val.input_backend.win32": "Windowsインジェクション",
        "val.input_backend.interception": "Interception（ドライバ）",
        "lbl.mouse2_action": "右クリックの追加動作",
        "lbl.mouse2_hold_action": "右長押しの追加動作",
        "lbl.on_target_dist": "「既に命中」の距離",
        "lbl.radius": "カーソルから探す範囲",
        "lbl.rapid_click_snap": "連打のたびにアシストする",
        "lbl.snap_offset_x": "クリック位置：左右にずらす",
        "lbl.snap_offset_y": "クリック位置：上下にずらす",
        "lbl.stall_pause_seconds": "詰まり後の一時停止",
        "lbl.watcher_seconds": "ダブルクリックの判定窓",
        "login.failed": "%s のサインインが完了しません——再試行してください。",
        "login.no_provider": "このコピーにはサインイン提供者が組み込まれていません。",
        "login.not_configured": "このビルドでは購読ファイルが未設定です。",
        "login.note": "サインインはブラウザを開き、この窓へ自動的に戻ります。",
        "login.provider": "%s でサインイン",
        "login.signedin": "%s としてサインインしました。",
        "login.sub": "Discord "
            "でサインイン——サブスクリプションはこのアカウントに紐づき、支払いはそのメールアドレスを使用。パスワードは不要。",
        "login.title": "%s - サインイン",
        "login.unreachable": "認証サーバーに接続できません: %s",
        "login.waiting": "ブラウザを待機中——%s のサインインを完了してください…",
        "mac.delete": "削除",
        "mac.empty": "まだ記録がありません - 起動して記録ショートカットを押し、通常どおり作業してください: "
            "すべてのキー、クリック、カーソル移動が記録されます。",
        "mac.export": "書出し",
        "mac.import": "読込み",
        "mac.keys_head": "キーマクロ",
        "mac.loop": "停止まで繰り返す",
        "mac.recordings": "記録",
        "mac.rename": "名前変更",
        "mac.row": "マクロ %d",
        "mac.sends": "送信",
        "mac.steps": "%d ステップ",
        "note.advanced": "距離と時間の設定。見つかるものではなくクリックの感触を変えます。ほとんどの人は変更不要。既定値は検証済み。",
        "note.assist": "起動中の挙動を変えるスイッチがすべて。モードはモードキーで切替——各モードの説明はショートカットのタブ。アシストは常に一時停止で開始、起動が唯一のオン/オフ。探索範囲とクリックの感触は詳細、対象の判定は処理。",
        "note.colors": "上部の2つのリストは、Snappy AI "
            "が好む色と拒む色を決めます。それぞれ右側に色を箱で表示し(最大15個)、箱をクリックするとその色を再度取り除けます。空のリストはバツ印の箱を表示し、オフとして扱われます。「優先する色に追加」と「拒否する色に追加」は、ピッカーに立っている色を該当のリストに入れます。現在のRGB値は3つの箱で、それぞれ色箱5つ分の幅があり、下のすべてと同じ15箱ぶんをまたぎます "
            "- "
            "ピッカーの色が赤・緑・青をどれだけ含むかに応じて光ります。この行はピッカーに従い、入力はできません。下のピッカーはペイントソフトのように色を混ぜます。その横のものはすべてウィンドウ右側にあり、上の設定と同じ間隔で端に揃い、どの行も同じ15箱ぶんの幅をまたぎます: "
            "#値を内側に描いた背の高いショーケース、15の既製色、2つの追加ボタン、そして画面行 - "
            "「画面から色を取得」はカーソル下の1色を取り、「画面から色を提案」はカーソル周辺で見つけた色で自分の15の箱を埋め、その1つをクリックするとピッカーに読み込まれます。ショーケースが高いのには理由があります: "
            "提案の箱の下端が左側の色スライダーとちょうど揃うためです。",
        "note.experimental": "エンジン選択。それぞれ検証済みの既定値あり。エンジンの比較、特殊なハードウェア、サポートの依頼時だけ変更を——取得エンジンは再起動後に有効。",
        "note.handler": "クリック可能な対象の判定: "
            "縁の淡さ、必要な鮮明さ、対象の大きさ。見つからなければ緩め、間違えれば締めるか、色タブで自分の色を。",
        "note.keybindings": "すべてのショートカット——さらに下に、2つのモードの役割、自分のキーとマウス入力の記録方法、単独キーと組合せの違い。",
        "note.macros": "マクロは起動中、1回のキー押しを組合せ全体に変えます。マクロの隣は記録: "
            "あなたが行ったすべて - すべてのキー、マウスクリック、カーソル移動 - "
            "の名前付きキャプチャが最大5件、記録どおりに再生されます。記録をクリックすると選択されます。各行は独自の「停止まで繰り返す」スイッチを持ち、「名前変更」・「書出し」・「読込み」・「削除」はボックスの下端にあります。",
        "note.macros_keys": "記録/再生のショートカットはショートカットのタブ（既定: Ctrl+Alt+R "
            "記録、Ctrl+Alt+S 停止して保存、Ctrl+Alt+M 再生、Ctrl+1..5 は一覧順）。",
        "online.cancelled": "Discord 認証はキャンセル（または失敗）しました。再試行してください。",
        "rec.export_fail": "書出し失敗: %r",
        "rec.exported": "書出しました: %s",
        "rec.import_fail": "読込み失敗: %r",
        "rec.imported": "%d 件の記録を読込み%s。",
        "rec.imported_none": "（有効なものなし）",
        "rec.no_sel": "書出すものが選択されていません。",
        "rec.notfile": "読込み失敗: 記録ファイルではありません。",
        "shared.back": "お帰りなさい——準備ができたら起動を。",
        "shared.body": "この Discord アカウントは今別のコンピュータで Snappy AI "
            "を実行中。\nセッションが1つになるまで、ここではアシストを停止。\n\n1サブスクリプション=同時1台——これが\n価格を下げ開発を続けさせます。",
        "shared.close": "閉じる",
        "shared.recheck": "今すぐ再確認",
        "shared.still": "依然他所で使用中——停止を継続。",
        "shared.title": "アカウントが他所で使用中",
        "shared.unreachable": "サーバーに接続できません——再確認します。",
        "st.all_files": "すべてのファイル",
        "st.color_added": "rgb(%d, %d, %d) を %s に追加 - 「適用」で保存。",
        "st.color_already": "rgb(%d, %d, %d) は既に %s にあります。",
        "st.color_full": "%s には既に15色あります - まず箱の1つをクリックして色を削除してください。",
        "st.color_removed": "rgb(%d, %d, %d) を %s から削除 - 「適用」で保存。",
        "st.delete_confirm": "記録 %r を削除しますか？\n元に戻せません。",
        "st.deleted": "記録を削除しました。",
        "st.engine_dead": "エンジンスレッドが利用不可——ショートカットは応答しません。",
        "st.ent_paused": "サブスクリプション %s——アシスト停止。Stripe で更新後、再起動を。",
        "st.ent_unreachable": "購読確認: サーバー接続不可（セッションは継続）。",
        "st.export_fail": "書出し失敗: %r",
        "st.export_rec_title": "記録の書出し",
        "st.export_title": "設定の書出し",
        "st.exported": "設定を書き出しました: %s",
        "st.file_rec": "Snappy AI 記録",
        "st.file_settings": "Snappy AI 設定",
        "st.follow": "  |  追従 %d 秒前",
        "st.import_fail": "読込み失敗: %r",
        "st.import_notfile": "読込み失敗: 設定ファイルではありません。",
        "st.import_rec_title": "記録の読込み",
        "st.import_title": "設定の読込み",
        "st.imported": "%d 件の設定を読込み%s。",
        "st.imported_ignored": "、無視: %s",
        "st.ini_over": "適用しましたが config.ini が上書き: %s",
        "st.lib_empty": "一覧が空——書出すものがありません。",
        "st.line": "アシスト %d  |  通過 %d%s  |  テーマ: %s",
        "st.loop_desc": "この記録の再生方式: オフ = 1回再生; オン = "
            "再生ショートカットを再び押すまで繰り返す。各記録は独自のスイッチを持ち、記録自体と一緒に保存されます。",
        "st.name_empty": "名前は空にできません。",
        "st.pick_err": "取得失敗: %r",
        "st.pick_fail": "取得失敗——再試行してください。",
        "st.pick_ok": "(%d, %d) で rgb(%d, %d, %d) を取得。",
        "st.pick_wait": "カーソルを色へ——3秒で取得…",
        "st.preset_desc": "既製色: %s——クリックでピッカーへ。",
        "st.rec_count": "%d / 5 件の記録",
        "st.rec_now": "%r は現在: %s。",
        "st.rec_once": "1回再生",
        "st.rec_playing": "%r を再生中…",
        "st.rec_playing_loop": "%r を停止まで再生中",
        "st.rec_recording": "記録中——%s で停止して保存",
        "st.rec_repeats": "停止まで繰り返す",
        "st.registered": "登録先: %s    状態: %s",
        "st.rename_prompt": "記録 #%d の新しい名前:",
        "st.renamed": "記録の名前を変更しました。",
        "st.reset_confirm": "すべての設定を既定値に戻しますか？\nアカウントは維持、影響は設定のみ。",
        "st.rgb_bad": "先に正しい R/G/B 値を入力してください。",
        "st.running": "動作中..",
        "st.saved": "保存して適用しました。",
        "st.defaults_restored": "既定値に戻しました。",
        "st.saved_bad": "保存しましたが無効（旧値を維持）: %s",
        "st.select_rec": "先に記録を選択してください。",
        "st.shared_paused": "アカウントが他所で使用中——アシスト停止。1サブスク=1台。",
        "st.standby": "待機..",
        "st.sug_fail": "候補取得に失敗: %r",
        "st.sug_loaded": "候補 rgb(%d, %d, %d) がピッカーに入りました - "
            "上のボタンでリストに追加できます。",
        "st.sug_loaded_desc": "提案されたUI色 rgb(%d, %d, %d)——領域の "
            "%d%%。クリックでピッカーへ。",
        "st.sug_none": "この領域から色の候補はありません。",
        "st.sug_ok": "%d 件の候補 - 1つクリックするとピッカーに読み込みます。",
        "st.sug_wait": "作業中のアプリを指して——3秒で采样…",
        "tab.advanced": "詳細",
        "tab.assist": "アシスト",
        "tab.colors": "色",
        "tab.experimental": "実験的",
        "tab.handler": "処理",
        "tab.help": "ヘルプ",
        "tab.hotkeys": "ショートカット",
        "tab.macros": "マクロ",
        "theme.dark": "ダーク",
        "theme.light": "ライト",
        "val.accent_matcher.hsv": "クラシック - 旧エンジン",
        "val.accent_matcher.oklab": "知覚的 - 色の見え方どおり（推奨）",
        "val.capture_backend.auto": "自動 - 安全なフォールバック付きで最速",
        "val.capture_backend.dxcam": "Desktop Duplication - 大半のPCで最速",
        "val.capture_backend.mss": "互換 - 常に動作（リモートデスクトップ、VM）",
        "val.capture_backend.wgc": "Windows Graphics Capture - 実験的",
        "val.follow_learn.accent": "自分の色の項目のみ",
        "val.follow_learn.any": "成功したスナップすべて",
        "val.mouse2_action.1": "現在の追従タスクを解除",
        "val.mouse2_action.2": "最後にスナップした色を追う",
        "val.mouse2_action.3": "カーソル下の色を取得して追う",
        "val.mouse2_action.4": "何もしない",
        "val.mouse2_hold_action.1": "現在の追従タスクを解除",
        "val.mouse2_hold_action.2": "最後にスナップした色を追う",
        "val.mouse2_hold_action.3": "カーソル下の色を取得して追う",
        "val.mouse2_hold_action.4": "何もしない",
        "word.off": "オフ",
        "word.on": "オン",
    },
    "ko": {
        "btn.apply": "적용",
        "btn.export": "설정 내보내기",
        "btn.import": "설정 가져오기",
        "btn.language": "언어: %s",
        "btn.launch": "시작",
        "btn.logout": "로그아웃",
        "btn.pause": "일시정지",
        "btn.restore": "기본값 복원",
        "col.accent": "강조",
        "col.add_pref": "선호 색에 추가",
        "col.add_ref": "거부 색에 추가",
        "col.chip_desc": "rgb(%d, %d, %d) (%s에 속함) - 상자를 클릭하면 이 색이 "
            "제거됩니다.",
        "col.chip_off": "%s에 색이 없습니다 - X 표시 상자는 꺼짐을 뜻합니다. 아래에서 색을 "
            "고르고 해당하는 추가 버튼을 누르세요.",
        "col.exclude": "제외",
        "col.pick": "화면에서 색 찍기",
        "col.rgb.desc": "세 상자는 지금 픽커에 있는 색을 보여줍니다: 첫 번째는 빨강이 많을수록, 두 "
            "번째는 초록이, 세 번째는 파랑이 많을수록 빛납니다 - 더 밝을수록 더 많다는 뜻입니다. 이 행은 "
            "픽커와 미리 만든 색, 화면 버튼을 따르며 입력할 수 없습니다.",
        "col.rgb.name": "현재 RGB 값",
        "col.suggest": "화면에서 색 제안",
        "desc.accent_boost": "내 색이 항목을 얼마나 밀어올리는지(0-3). 잘못된 항목이 이기면 "
            "1.5-2로 올리기.",
        "desc.accent_coherent": "내 색상은 연결된 덩어리를 이뤄야 유효합니다 - 흩어진 "
            "디더·압축 잡점은 항목을 인정하거나 강화하거나 클릭 금지 목록에 올리지 않습니다.",
        "desc.accent_color": "Snappy AI가 선호해야 할 색으로, 오른쪽에 색 상자로 "
            "표시됩니다. 아래에서 색을 고르고 '선호 색에 추가'를 눌러 추가하세요 - 최대 15상자. 상자를 "
            "클릭하면 그 색이 다시 제거됩니다. 이들 중 하나를 포함한 항목은 동점일 때 이깁니다. 빈 목록은 "
            "X 표시 상자를 보여주며 설정을 끕니다.",
        "desc.accent_matcher": "색 비교 방법. 지각형은 색이 실제로 보이는 방식대로 순위를 "
            "매기며 권장. 클래식은 비교용 구형 엔진.",
        "desc.accent_only": "내 색상을 포함한 항목만 어시스트 가능. 그 외 클릭은 그대로 "
            "Windows로.",
        "desc.accent_soft": "0-100: 밝거나 어둡거나 바랜 버전이 얼마나인정되는지. 0 = "
            "정확한 색조만.",
        "desc.accent_tolerance": "색이 얼마나 가까워야 내 색으로 칠지(4-90). 낮을수록 "
            "엄격.",
        "desc.accent_variants": "내 색상의 더 밝고 어두운 복사본도 일치로 쳐서, "
            "호버·누름·흐림 상태가 색상 허용 범위 확장 없이 인정됩니다. 명도만 - 잘못된 색상은 절대 "
            "끼어들지 않습니다.",
        "desc.adaptive_threshold": "어두운 테마와 바랜 문서는 자체 감지 기준을 자동 낮춰 "
            "흐린 항목도 찾습니다. 켬 권장.",
        "desc.auto_click": "켜면 프로그램이 관찰 영역의 가장 좋은 항목을 0.1초마다 스스로 클릭하며 대비를 우선합니다. 강조 색이 설정되면 그 "
            "색을 가진 항목만 대상이고, 색이 없으면 매우 선명하게 그려진 항목만 클릭됩니다. 같은 곳을 두 번 클릭하지 않으며 "
            "자체 창은 절대 클릭하지 않습니다.",
        "desc.auto_click_interval": "내 색상을 위해 화면을 확인하는 간격(0.5-60). "
            "느린 숫자가 안전합니다: 지켜보는 대화창에는 2-5가 적당합니다.",
        "desc.auto_click_max_clicks": "시작 후 자동으로 클릭할 수 있는 횟수(1-200). "
            "한도에 닿으면 멈추고 알리므로 잘못된 설정이 폭주하지 않습니다.",
        "desc.auto_click_min_contrast": "»최소 가장자리 선명도«와 같은 척도입니다. "
            "기본값에서 시작해 잘못 클릭하면 올리세요: 강하고 선명한 항목만 해당됩니다.",
        "desc.auto_click_radius": "자동 클릭은 화면 중앙 주변을 찾습니다(40-600 px). "
            "복잡한 창에는 넓게, 중앙의 한 컨트롤만 보려면 좁게.",
        "desc.auto_click_repeat_px": "자동 클릭 후 이 픽셀 안의 대상은 "
            "내버려둡니다(0-400). 없으면 화면에 남은 단추가 계속 클릭됩니다.",
        "desc.auto_click_settle_ms": "클릭 전에 커서가 대상에서 이렇게 쉽니다(0-2000 "
            "ms). 프로그램이 강조 표시를 먼저 봅니다. 120은 대부분의 창에 적당합니다.",
        "desc.block_bound_keys": "끔(기본): Ctrl/Alt/Shift 없는 단축키(예: 1, "
            "V)는 모든 프로그램에서 작동하고 입력도 그대로 됩니다. 즉 문장 중간에 눌러도 동작이 발동합니다. "
            "켬: 동작은 어디서나 발동하지만 키는 입력되지 않습니다.",
        "desc.capture_backend": "화면을 찍는 방법. 자동은 호환 방식을 사용하며 거의 모든 창을 봅니다. "
            "호환은 원격 데스크톱과 가상 머신을 포함 항상 작동. 재시작 후 반영.",
        "desc.color_adapt": "각 항목은 비교 전에 자신의 배경에 맞춰 화이트밸런스를 조정하므로 야간 "
            "조명과 테마 색상이 내 색상을 허용 범위 밖으로 밀어내지 않습니다. 적응되지 않은 비교기와 비교할 "
            "때만 끄세요.",
        "desc.contrast_threshold": "낮추면 더 흐린 항목을 찾음(노이즈도 증가). 높이면 더 "
            "또렷한 가장자리 요구.",
        "desc.default": "설정 이름 위에 마우스를 올리면 역할을 볼 수 있습니다.",
        "desc.exclude_color": "이 색들을 포함한 항목은 결코 도움되지 않습니다: 두 모드 모두에서 "
            "클릭이 곧장 Windows로 갑니다. 오른쪽에 색 상자로 표시 - 아래에서 색을 고르고 '거부 색에 "
            "추가'를 눌러 하나 추가하세요(최대 15). 상자를 클릭하면 제거됩니다. 빈 목록은 X 표시 상자를 "
            "보여주며 설정을 끕니다.",
        "desc.follow_boost": "기억된 항목이 동률에서 이기는 강도: 100%는 신선할 때 점수를 두 "
            "배로, 25%는 가벼운 밀기.",
        "desc.follow_enabled": "성공한 스냅 뒤, 비슷해 보이거나 같은 자리의 항목이 잠시 "
            "우선합니다 - 스크롤막대와 같은 버튼 반복 클릭에 유용.",
        "desc.follow_learn": "내 색상의 항목만: 헛클릭이 기억을 빼앗지 못함. 모든 성공 스냅: "
            "옛 신뢰 방식.",
        "desc.follow_seconds": "마지막 성공 스냅 후 기억된 항목이 우선되는 초(1-120).",
        "desc.glide_ms": "0(기본)은 즉시 점프 - 가장 빠름. 40-120은 미끄러져 보임. 직접 "
            "마우스를 움직이면 중단.",
        "desc.hold_follow": "스냅 직후 왼쪽 버튼을 계속 누르거나 - 기억된 항목에서 다시 누르면 "
            "- 커서가 해당 항목의 색에 머뭅니다. 스크롤막대 손잡이 같은 끌기를 안정화합니다. 다른 곳에서의 "
            "누름은 영향 없음.",
        "desc.key_launch": "형식: ctrl+l, f5, space, ctrl+alt+1 ... "
            "보조키: ctrl, alt, shift, win. 적용 후 반영.",
        "desc.key_mode1": "쉼표 구분, 예 '1, f1, ctrl+f1, v'. 클래식 모드 설명은 "
            "단축키 탭.",
        "desc.key_mode2": "쉼표 구분, 예 '2, f2, ctrl+f2, b'. 가이드 모드 설명은 "
            "단축키 탭.",
        "desc.key_pause": "시작할 때까지 마우스와 키보드가 완전히 당신의 것.",
        "desc.key_play": "매크로 목록에서 선택한 녹화를 재생, 선택 없으면 최신 것. 반복 중인 "
            "녹화에서 누르면 중지.",
        "desc.key_play_n": "매크로 탭 번호 목록의 #%d번 녹화를 위치대로 재생. 목록이 더 짧으면 "
            "아무 일도 없음.",
        "desc.key_record": "당신이 하는 모든 것 - 모든 키, 모든 마우스 클릭, 모든 커서 이동 "
            "- 을 기록하며, 입력은 그대로 프로그램에 도달하고, 중지 단축키가 매크로 목록에 저장할 때까지 "
            "계속됩니다. 시작 상태에서만 대기.",
        "desc.key_record_stop": "기록을 중지하고 매크로 목록에 저장, 진행 중인 재생도 중지.",
        "desc.luminance_norm": "가장자리를 주변 밝기 대비로 평가해 어두운 테마도 밝은 테마처럼 "
            "동작. 켬 권장.",
        "desc.macro_action": "트리거 한 번당 대신 눌러 주는 조합(한 번 = 한 조합): "
            "'ctrl+c', 'ctrl+shift+s', 'space', 'f5' ... 비움 = 매크로 끔.",
        "desc.macro_key": "입력 대신 매크로를 의미하는 키: 'b', 'f7', 'ctrl+b' "
            "... 시작 중 한 번 누르면 옆 조합을 정확히 한 번 보내고 키 자체는 프로그램에 도달하지 않음. "
            "일시정지 중엔 정상 입력. 비움 = 매크로 끔.",
        "desc.max_area": "이보다 큰 얼룩은 무시 - 보통 창 전체나 배경이며 클릭할 항목이 아님.",
        "desc.max_dim": "이보다 넓거나 높은 항목은 무시. 스크롤막대처럼 화면 끝에 붙은 항목은 두 배 "
            "허용.",
        "desc.merge_distance": "이보다 가까운 조각(끊긴 윤곽, 라벨 옆 아이콘)을 한 항목으로 "
            "결합. 완성된 두 항목은 결코 결합하지 않음.",
        "desc.min_area": "이보다 작은 얼룩은 티끌로 무시. 큰 항목에 붙는 경우는 제외.",
        "desc.min_contrast": "항목이 클릭 가능하려면 최소 이 정도는 선명해야 합니다. 28 미만 "
            "값은 28로 처리됩니다: 내장 품질 하한이 노이즈 클릭을 막습니다.",
        "desc.motion_3d": "움직이는 항목을 직선 맞춤 대신 위치와 크기로 추적합니다: 단일 불량 "
            "스캔은 추적기를 실명시키지 않고 무시되고, 회전도 따라가며, 크기 급변 시 추적을 다시 "
            "시작합니다(스캐너가 다른 항목을 잡았다는 뜻). 같은 속도 게이트와 80 px 상한 - 바뀌는 것은 "
            "두뇌뿐입니다. 독립적으로 동작합니다.",
        "desc.motion_lead_ms": "움직이는 항목을 미리 겨눌 밀리초(0-300): 느린 스크롤 "
            "40-80, 빠른 탐색 바 100-150. 상한 80px, 느리거나 방향 전환 시 자동 끔.",
        "desc.motion_predict": "클릭 중에 움직이는 항목(스크롤 목록, 영상 바)은 약간 미리 "
            "겨냥해 클릭이 항목 위에 닿게 합니다. 정지한 항목은 변함없음.",
        "desc.mouse2_action": "짧은 우클릭이 추가로 하는 일 - 우클릭 자체는 항상 정상 "
            "Windows 기능. 기본: 없음.",
        "desc.mouse2_hold_action": "같은 선택지를, 클릭 대신 오른쪽 버튼을 약 0.5초 길게 "
            "누를 때 발동. 한 번 누름은 클릭이거나 길게 누름, 둘 다 아님. 기본: 없음.",
        "desc.on_target_dist": "클릭이 항목 중심으로부터 이 픽셀 안이면 아무것도 움직이지 않음 "
            "- 이미 맞습니다.",
        "desc.radius": "픽셀 단위 탐색 거리(40-400). 원하는 항목이 조금 멀면 크게, 옆 항목이 "
            "이기면 작게.",
        "desc.rapid_click_snap": "끔(기본): 클릭 처리 중 나머지는 Windows로. 켬: "
            "모든 왼쪽 클릭 어시스트.",
        "desc.snap_offset_x": "클릭 지점을 항목 중앙에서 옆으로 옮깁니다(-200~200, 음수는 "
            "왼쪽). 가운데가 죽은 컨트롤 - 분할 단추, 슬라이더 - 은 매번 씨름하지 말고 한 번에 살아 "
            "있는 곳으로 맞춥니다.",
        "desc.snap_offset_y": "클릭 지점을 항목 중앙에서 위아래로 옮깁니다(-200~200, "
            "음수는 위). 옆 이동과 같은 생각: 컨트롤의 살아 있는 부분에 내립니다.",
        "desc.stall_pause_seconds": "스캔이 멈추면 이 시간 동안 어시스트가 쉬고, 누르고 "
            "있던 클릭은 사용자에게 반환.",
        "desc.watcher_seconds": "클래식 모드에서 같은 자리 근처 두 번째 스냅이 이 시간 이내면 "
            "더블클릭이 됩니다.",
        "ent.cancel_line": "%s까지 활성 - 갱신되지 않음",
        "ent.canceled_line": "구독 종료%s",
        "ent.expired_line": "%s에 만료 - Stripe에서 갱신",
        "ent.past_due_line": "결제 실패 - Stripe 영수증 메일에서 카드 수정. 청구가 "
            "결제되면 접근 복귀",
        "ent.plan": " (%s)",
        "ent.refunded_line": "환불 / 차지백 - 활성화 취소됨",
        "ent.st.active": "활성",
        "ent.st.canceled": "종료",
        "ent.st.canceling": "활성이나 취소 예정",
        "ent.st.grant": "지원 부여",
        "ent.st.past_due": "결제 실패",
        "ent.st.refunded": "환불 / 차지백",
        "ent.st.trial": "체험",
        "ent.st.unsubscribed": "구독 없음",
        "ent.until": " %s까지",
        "err.auth_unreachable": "Snappy AI 인증 서버에 연결할 수 "
            "없습니다:\n%s\n\nSnappy AI는 해당 서버의 응답이 있어야만 작동합니다.\n다시 시도?",
        "err.start_fail": "Snappy AI를 시작할 수 없습니다.\n자세한 내용은 "
            "--console로 실행하세요.",
        "gate.btn.monthly": "월 구독 9.99€",
        "gate.btn.trial": "체험 구매 1.99€",
        "gate.head.canceled": "이 구독은 취소됨 - 계속하려면 Stripe에서 새로 시작.",
        "gate.head.canceling": "구독이 취소 예정 - %s까지 유효, 이후 갱신하지 않으면 이 "
            "로그인이 다시 잠깁니다.",
        "gate.head.email_mismatch": "결제가 Discord 계정과 다른 메일로 이루어졌습니다. "
            "구독은 아래 표시된 Discord 메일에서만 작동 - 해당 메일로 재구독하거나 지원에 연락하세요.",
        "gate.head.expired": "이 로그인의 구독이 만료 - 계속하려면 Stripe에서 갱신.",
        "gate.head.none": "로그인했으나 이 로그인에 유효한 구독이 없습니다. 이 Discord 메일로 "
            "결제하세요 - 다른 주소의 구매는 활성화할 수 없습니다.",
        "gate.head.past_due": "마지막 구독 결제 실패 - Stripe에서 수정하면 이 로그인이 "
            "다시 활성화.",
        "gate.head.refunded": "이 구매는 환불 또는 차지백되어 활성화가 취소되었습니다. 이 "
            "Discord 메일로 새 구독을 하면 다시 활성화.",
        "gate.head.shared": "이 계정은 지금 다른 컴퓨터에서 Snappy AI를 실행 중입니다. "
            "같은 Discord 계정이 두 곳에서 돌는 동안 본 소프트웨어는 꺼짐 - 다른 세션을 닫고 "
            "재확인하세요. 구독 공유는 가격을 올립니다.",
        "gate.msg.active": "구독 활성 - Snappy AI 시작...",
        "gate.msg.checking": "서버에 확인 중...",
        "gate.msg.no_link": "이 결제 링크는 이 빌드에서 설정되지 않았습니다.",
        "gate.msg.open_fail": "브라우저를 열 수 없습니다. 이 링크를 수동으로 여세요:\n%s",
        "gate.msg.open_ok": "Stripe가 브라우저에서 열렸습니다 - 그상에서 지불하세요. 이 창은 자동으로 지불을 기보고 엔진을 시작합니다.",
        "gate.msg.session_gone": "세션이 사라졌습니다 - 다시 로그인하세요.",
        "gate.msg.still_none": "이 로그인에 아직 유효한 구독이 없습니다.",
        "gate.msg.still_shared": "여전히 다른 컴퓨터에서 사용 중 - 그 세션을 닫고 재확인.",
        "gate.msg.unreachable": "인증 서버에 연결할 수 없음: %s",
        "gate.note": "구독이 활성화되면 엔진이 시작 - 이 창은 30초마다 자동 재확인. 닫으면 "
            "로그인으로.",
        "gate.prices": "2일 체험: 1.99€ (1회)  -  구독: 9.99€ / 월.\n활성화는 "
            "결제 후 최대 약 10분 소요. 갱신은 같은 로그인을 자동으로 다시 활성화.",
        "gate.title": "%s - 구독%s",
        "hdr.build": "빌드 %s",
        "help.1.b": "Snappy AI는 커서 주변 화면을 보고 근처의 단단한 항목 모양 - 버튼, "
            "아이콘, 링크 - 을 찾아 가장 좋은 것을 고릅니다: 또렷한 가장자리, 적당한 크기, 커서와의 "
            "가까움이 이깁니다. 내 색상, 클릭 금지 목록, 마지막 클릭 기억이 선택을 기울일 수 있습니다. "
            "커서는 틀의 모서리가 아닌 항목 한가운데를 겨냥.",
        "help.1.t": "클릭 시 일어나는 일",
        "help.10.b": "1. 시작했나요? 일시정지는 아무것도 가로채지 않음 - ‘단축키: 어시스트 "
            "시작’(기본 Ctrl+L)이 유일한 켬/끔.  2. Shift를 누른 채 한 번 클릭해 어시스트가 "
            "원인인지 확인.  3. 잘못된 항목이 이김: ‘커서로부터 탐색 거리’를 줄이고, ‘내 색상’ 지정 "
            "또는 ‘색상 우위 강도’ 상향.  4. 아무것도 못 찾음: ‘얼마나 흐린 가장자리까지 허용’과 "
            "‘최소 가장자리 선명도’ 하향, ‘최대 너비 또는 높이’ 또는 ‘가까운 조각 붙이기’ 상향.  5. "
            "결코 어시스트되면 안 되는 것: 그 색을 ‘클릭 금지 색상’에.  6. 여전히 문제: 무엇을 "
            "클릭했고 무엇을 기대했는지 지원에 알리고, Snappy AI가 데이터 폴더에 기록하는 로그 파일을 "
            "함께 보내세요.",
        "help.10.t": "문제 시 이 순서로 확인",
        "help.2.b": "가이드 모드(기본)는 클릭을 먹지 않습니다: 클릭은 프로그램에 도달하고, 놓으면 "
            "커서가 가장 가까운 깨끗한 항목으로. 클래식 모드는 더 강력: 항목 근처 헛클릭을 잡아 커서가 붙고 "
            "Snappy AI가 대신 클릭. ‘커서로부터 탐색 거리’가 탐색 원을 정함 - 원하는 항목이 "
            "чуть  밖에 없으면 크게, 옆 항목이 이기면 작게. Shift 누름은 두 모드에서 한 클릭을 "
            "우회.",
        "help.2.t": "먼저: 모드와 탐색 거리",
        "help.3.b": "처리 탭의 ‘얼마나 흐린 가장자리까지 허용’과 ‘최소 가장자리 선명도’가 어떤 "
            "가장자리를 셀지 결정: 낮추면 흐린 것을 찾고, 높이면 노이즈를 무시. ‘최소 항목 크기’, ‘최대 "
            "항목 면적’, ‘최대 너비 또는 높이’가 티끌과 창 전체를 걸름. ‘가까운 조각 붙이기’는 끊긴 "
            "윤곽이나 라벨 옆 아이콘을 한 항목으로. 어시스트 탭의 ‘어두운 화면에 자동 맞춤’과 ‘가장자리를 "
            "상대 밝기로 평가’는 어두운 테마를 밝게처럼 - 둘 다 켜 두기.",
        "help.3.t": "아무것도 못 찾거나 너무 많이 찾을 때",
        "help.4.b": "색상 탭의 ‘내 색상’은 선호 색, ‘클릭 금지 색상’은 절대적: 그 색의 항목은 "
            "결코 어시스트되지 않음. ‘내 색상만 어시스트’는 맞는 항목으로 제한. 처리 탭의 ‘색상 일치 "
            "엄격도’는 색조가 얼마나 가까워야 하는지, ‘비슷한 색조 받아들이기’는 밝거나 바랜 버전을 부분 "
            "인정, ‘색상 우위 강도’는 내 색이 항목을 얼마나 미는지 - 잘못 이기면 올리기.",
        "help.4.t": "색상 사용하기",
        "help.5.b": "‘마지막 클릭한 대상 기억’은 마지막 성공 클릭이 닿은 항목을 ‘기억 유지 시간’ 초 "
            "동안 계속 선호 - 스크롤막대와 대화상자 버튼을 편하게. ‘기억 강도’는 이기는 정도, ‘기억이 "
            "배울 수 있는 것’은 보호: ‘내 색상의 항목만’이면 헛클릭이 기억을 빼앗지 못함. ‘버튼을 누른 "
            "채 대상을 따라가기’는 끌기를 안정화, 실험 탭의 우클릭 동작은 마우스로 기억을 따르거나 해제.",
        "help.5.t": "같은 조작부 반복 클릭",
        "help.6.b": "‘움직이는 대상 미리 겨냥’은 선택한 항목의 이동 속도를 재고 ‘얼마나 미리 겨눌지’ "
            "밀리초만큼 미리 겨눠, 클릭이 스크롤 목록이나 영상 바 뒤가 아닌 위에 닿게 함. 미리 겨눔은 "
            "80픽셀 상한, 정지하거나 방향을 트는 항목에선 자동 끔.",
        "help.6.t": "움직이는 것 클릭",
        "help.7.b": "‘커서 이동 애니메이션’ = 0 즉시 점프, 40-120 미끄러지며 보임, 직접 "
            "마우스를 움직이면 중단. ‘더블클릭 판정 창’은 클래식 모드에서 같은 자리 근처 두 번째 스냅을 "
            "더블클릭으로. ‘빠른 연타의 모든 클릭 어시스트’는 연타의 첫 번째만이 아닌 매 클릭을 어시스트. "
            "‘멈춤 후 일시정지’는 스캔이 멈췄을 때 누른 클릭을 돌려주는 안전판.",
        "help.7.t": "클릭 느낌",
        "help.8.b": "단축키 탭이 두 모드와 녹화 절차를 설명합니다. 요약: Ctrl, Alt, "
            "Shift, Win이 포함된 단축키는 시스템 전역으로 예약되고, 맨 단일 키는 어디서나 발동하면서 "
            "입력도 됩니다. 매크로는 차단된 한 번의 키 누름을 조합 하나로 바꿉니다. 녹화는 당신의 실제 입력 "
            "- 모든 키, 마우스 클릭, 커서 이동 - 을 잡아 매크로 탭에서 재생하며, 각각 자체 한 번 재생 "
            "또는 멈출 때까지 반복 스위치를 가집니다.",
        "help.8.t": "키, 매크로, 녹화",
        "help.9.b": "‘설정 내보내기’ 옆의 언어 버튼 - 로그인 창과 구독 창에도 있음 - 이 재시작 "
            "없이 전체 인터페이스를 즉시 바꾸고 선택을 기억. 번역 중인 언어는 제공되지 않으므로 선택 가능한 "
            "것은 모두 완전합니다.",
        "help.9.t": "언어",
        "help.sub": "모든 설정을 해당 탭에서 보는 이름 그대로, 필요한 순서대로. 이름 위에 마우스를 "
            "올리면 한 줄 설명, 이 페이지는 긴 설명.",
        "help.tail": "설정은 ‘적용’을 누르면 반영. 프로그램 옆 config.ini는 "
            "config.json을 덮어씀. 이 페이지는 설명만 하고 설정은 바꾸지 않음.",
        "help.title": "쉬운 말로 Snappy AI 조정",
        "kb.keys.b": "Ctrl, Alt, Shift, Win을 포함한 단축키는 시스템 전역에서 예약되어 "
            "Snappy AI만 봅니다. 맨 단일 키(1, 2 등)는 모든 프로그램에서 작동하고 입력도 그대로 "
            "- 대신 문장 중간에 눌러도 동작이 발동. 클래식한 동작을 원하면 어시스트 탭의 ‘단일 키 단축키는 "
            "키를 흡수’를 켬. 매크로는 한 걸음 더: 시작 중 트리거 키는 흡수되고 옆 조합이 정확히 한 번 "
            "발송.",
        "kb.keys.t": "단일 키와 조합 키",
        "kb.mode.b": "가이드 모드(기본, 단축키 2): 클릭은 항상 그대로 프로그램에 도달. 버튼을 "
            "놓으면 커서가 가장 가까운 깨끗한 항목으로 이동해 다음 클릭이 거기서 시작. 아무것도 삼키지 않는 "
            "가장 안전한 모드.  클래식 모드(단축키 1): 항목 근처를 클릭하면 그 헛클릭을 잡아 커서가 "
            "항목에 붙고 Snappy AI가 대신 클릭. 근처에 없으면 클릭은 그대로 반환.  두 모드 모두 "
            "Shift를 누른 채 클릭하면 그 한 번만 어시스트를 우회.",
        "kb.mode.t": "두 모드의 역할",
        "kb.rec.b": "시작 상태에서 녹화 시작 단축키(기본 Ctrl+Alt+R)를 누르면: 누른 모든 키, "
            "클릭한 모든 마우스 버튼, 모든 커서 이동이 기록되고 그대로 프로그램에도 도달하므로 녹화 중에도 "
            "평소대로 작업할 수 있습니다. 중지 단축키(Ctrl+Alt+S)를 누르면 매크로 탭의 목록에 "
            "저장됩니다 - 녹화 5개가 들어갑니다. 녹화를 클릭해 선택하고 '이름 변경'이나 '내보내기'를 "
            "사용하고 자체 '멈출 때까지 반복' 스위치를 설정하세요. 재생 단축키(Ctrl+Alt+M)는 거기서 "
            "선택한 녹화를 재생하고, Ctrl+1~Ctrl+5는 목록 위치대로 재생합니다. 일시정지 중엔 "
            "아무것도 기록되거나 주입되지 않습니다 - 입력은 완전히 당신의 것입니다.",
        "kb.rec.t": "내 키와 마우스 입력 녹화 및 재생 방법",
        "lang.close": "닫기",
        "lang.coverage": "%d%% 번역됨",
        "lang.current": "현재: %s",
        "lang.progress": "번역 진행 중이며 완성 시 제공됩니다: %s",
        "lang.prompt": "변경 사항은 즉시 적용되며 창은 열려 있어 여러 언어를 시도할 수 있습니다.",
        "lang.title": "언어",
        "lbl.accent_boost": "색상 우위 강도",
        "lbl.accent_coherent": "흩어진 색점 무시",
        "lbl.accent_color": "내 색상",
        "lbl.accent_matcher": "색상 비교 엔진",
        "lbl.accent_only": "내 색상만 어시스트",
        "lbl.accent_soft": "비슷한 색조 받아들이기",
        "lbl.accent_tolerance": "색상 일치 엄격도",
        "lbl.accent_variants": "내 색상의 밝고 어두운 상태 인식",
        "lbl.adaptive_threshold": "어두운 화면에 자동 맞춤",
        "lbl.auto_click": "스스로 항목을 클릭",
        "lbl.auto_click_interval": "자동 클릭 간격(초)",
        "lbl.auto_click_max_clicks": "세션당 자동 클릭 한도",
        "lbl.auto_click_min_contrast": "자동 클릭 대상의 선명도",
        "lbl.auto_click_radius": "화면 중앙에서 찾는 거리",
        "lbl.auto_click_repeat_px": "같은 곳을 다시 클릭하지 않음",
        "lbl.auto_click_settle_ms": "자동 클릭 전 대기 시간",
        "lbl.block_bound_keys": "단일 키 단축키는 키를 흡수",
        "lbl.capture_backend": "화면 캡처 엔진",
        "lbl.color_adapt": "화면 밝기에 적응",
        "lbl.contrast_threshold": "얼마나 흐린 가장자리까지 허용",
        "lbl.exclude_color": "클릭 금지 색상",
        "lbl.follow_boost": "기억 강도",
        "lbl.follow_enabled": "마지막 클릭한 대상 기억",
        "lbl.follow_learn": "기억이 배울 수 있는 것",
        "lbl.follow_seconds": "기억 유지 시간",
        "lbl.glide_ms": "커서 이동 애니메이션",
        "lbl.hold_follow": "버튼을 누른 채 대상을 따라가기",
        "lbl.key_launch": "단축키: 어시스트 시작",
        "lbl.key_mode1": "단축키: 클래식 모드 (최대 4키)",
        "lbl.key_mode2": "단축키: 가이드 모드 (최대 4키)",
        "lbl.key_pause": "단축키: 일시정지",
        "lbl.key_play": "단축키: 선택한 녹화 재생",
        "lbl.key_play_n": "단축키: 녹화 #%d 재생",
        "lbl.key_record": "단축키: 녹화 시작",
        "lbl.key_record_stop": "단축키: 녹화 중지 및 저장",
        "lbl.luminance_norm": "가장자리를 상대 밝기로 평가",
        "lbl.macro_action": "매크로 %d: 대신 보내는 조합",
        "lbl.macro_key": "매크로 %d: 이 키를 누름",
        "lbl.max_area": "최대 항목 면적",
        "lbl.max_dim": "최대 너비 또는 높이",
        "lbl.merge_distance": "가까운 조각 붙이기",
        "lbl.min_area": "최소 항목 크기",
        "lbl.min_contrast": "최소 가장자리 선명도",
        "lbl.motion_3d": "움직이는 항목 스마트 추적",
        "lbl.motion_lead_ms": "얼마나 미리 겨눌지",
        "lbl.motion_predict": "움직이는 대상 미리 겨냥",
        "lbl.watch_center_only": "화면 중앙만 주시",
        "desc.watch_center_only": "도움 기능은 화면 정중앙의 고정 사각형(크기=검색 거리, 기본 150×150px)만 스캔합니다. 커서 위치와 "
            "무관합니다. 그 사각형 밖의 클릭은 그대로 통과합니다.",
        "lbl.center_follow": "화면이 대상을 따라감",
        "desc.center_follow": "“화면 중앙만 주시” 켜짐 시: 항목을 붙잡으면 도움 기능이 이를 중앙에 유지하도록 화면을 움직입니다(스크롤 평면에 "
            "특히 유용). 직접 화면을 움직이면 추적이 해제됩니다.",
        "lbl.input_backend": "입력 방식",
        "desc.input_backend": "Windows 인젝션(기본)은 어디서나 작동합니다. Interception은 드라이버를 통해 전송하며 게임이 실제 "
            "마우스로 인식합니다. Interception 드라이버 설치와 프로그램 옆 interception.dll이 필요합니다. "
            "없으면 자동으로 Windows 인젝션을 사용합니다.",
        "val.input_backend.win32": "Windows 인젝션",
        "val.input_backend.interception": "Interception (드라이버)",
        "lbl.mouse2_action": "우클릭 추가 동작",
        "lbl.mouse2_hold_action": "우클릭 길게 누름 동작",
        "lbl.on_target_dist": "‘이미 맞춤’ 거리",
        "lbl.radius": "커서로부터 탐색 거리",
        "lbl.rapid_click_snap": "빠른 연타의 모든 클릭 어시스트",
        "lbl.snap_offset_x": "클릭 지점: 좌 / 우 이동",
        "lbl.snap_offset_y": "클릭 지점: 상 / 하 이동",
        "lbl.stall_pause_seconds": "멈춤 후 일시정지",
        "lbl.watcher_seconds": "더블클릭 판정 창",
        "login.failed": "%s 로그인이 완료되지 않았습니다 - 다시 시도하세요.",
        "login.no_provider": "이 사본에는 로그인 제공자가 내장되어 있지 않습니다.",
        "login.not_configured": "이 빌드에서는 구독 파일이 아직 설정되지 않았습니다.",
        "login.note": "로그인은 브라우저를 열고 스스로 이 창으로 돌아옵니다.",
        "login.provider": "%s(으)로 로그인",
        "login.signedin": "%s(으)로 로그인했습니다.",
        "login.sub": "Discord로 로그인 - 구독은 이 계정에묶이며 결제는 해당 메일 주소를 사용해야 "
            "합니다. 비밀번호는 없습니다.",
        "login.title": "%s - 로그인",
        "login.unreachable": "인증 서버에 연결할 수 없음: %s",
        "login.waiting": "브라우저 대기 중 - %s 로그인을 완료하세요...",
        "mac.delete": "삭제",
        "mac.empty": "아직 녹화 없음 - 시작하고 녹화 단축키를 누른 뒤 평소대로 작업하세요: 모든 키, "
            "클릭, 커서 이동이 기록됩니다.",
        "mac.export": "내보내기",
        "mac.import": "가져오기",
        "mac.keys_head": "키 매크로",
        "mac.loop": "멈출 때까지 반복",
        "mac.recordings": "녹화",
        "mac.rename": "이름 변경",
        "mac.row": "매크로 %d",
        "mac.sends": "보냄",
        "mac.steps": "%d단계",
        "note.advanced": "거리와 시간 설정. 무엇을 찾는지보다 클릭 느낌을 바꿉니다. 대부분 만질 일 "
            "없음. 기본값이 검증된 값.",
        "note.assist": "시작 중 동작을 바꾸는 모든 스위치. 두 모드는 모드 키로 전환 - 각 모드의 "
            "설명은 단축키 탭. 어시스트는 항상 일시정지로 시작, 시작이 유일한 켬/끔. 엔진이 보는 곳과 클릭 "
            "느낌은 고급, 항목 판정은 처리.",
        "note.colors": "위 두 목록은 Snappy AI가 선호하거나 거부할 색을 정합니다. 각 목록은 "
            "자기 색을 오른쪽 상자로 보여 주며(최대 15개), 상자를 클릭하면 그 색이 다시 제거됩니다. 빈 "
            "목록은 X 표시 상자를 보여주며 꺼진 상태로 칩니다. '선호 색에 추가'와 '거부 색에 추가'는 "
            "피커에 서 있는 색을 해당 목록에 넣습니다. 현재 RGB 값은 피커의 색이 빨강·초록·파랑을 얼마나 "
            "품었는지에 따라 빛나는 세 상자를 보여 줍니다 - 각 상자는 색 상자 다섯 칸 너비라, 이 줄은 "
            "아래 모든 것과 같은 15칸을 꽉 채웁니다. 이 줄은 피커를 따르며 입력할 수 없습니다. 아래 "
            "피커는 페인트 프로그램처럼 색을 섞습니다. 그 옆의 모든 것은 창 오른쪽에 있으며 위 설정들과 같은 "
            "간격으로 가장자리에 붙고, 모든 줄이 같은 15칸 너비를 채웁니다: #값을 안에 그린 키 큰 "
            "쇼케이스, 그다음 준비된 15색, 두 추가 버튼, 화면 줄 - '화면에서 색 찍기'는 커서 아래 한 "
            "색을 가져오고, '화면에서 색 제안'은 커서 주변에서 찾은 색으로 자기 15상자를 채우며, 그중 "
            "하나를 클릭하면 피커에 불러옵니다. 쇼케이스가 키가 큰 데는 이유가 있습니다: 제안 상자의 아래 "
            "끝이 왼쪽 색 슬라이더와 정확히 맞춰집니다.",
        "note.experimental": "엔진 선택, 각각 검증된 기본값 있음. 엔진 비교, 특이 하드웨어, "
            "지원 요청 시에만 변경 - 캡처 엔진은 재시작 후 반영.",
        "note.handler": "클릭 가능한 항목의 판정: 가장자리의 흐림, 필요한 선명도, 항목의 크기. 못 "
            "찾으면 느슨하게, 잘못 찾으면 조이거나 색상 탭에서 내 색을.",
        "note.keybindings": "모든 단축키 - 그리고 아래에 두 모드의 역할, 내 키와 마우스 입력 "
            "녹화법, 단일 키와 조합의 차이.",
        "note.macros": "매크로는 시작 중 한 번의 키 누름을 조합 전체로 바꿉니다. 매크로 옆에는 "
            "녹화가 있습니다: 당신이 한 모든 것 - 모든 키, 마우스 클릭, 커서 이동 - 의 이름 있는 "
            "캡처가 최대 5개까지, 녹화된 그대로 재생됩니다. 녹화를 클릭해 선택하세요; 각 행은 자체 '멈출 "
            "때까지 반복' 스위치를 가지며, '이름 변경', '내보내기', '가져오기', '삭제'는 상자 "
            "아래쪽에 있습니다.",
        "note.macros_keys": "녹화/재생 단축키는 단축키 탭(기본: Ctrl+Alt+R 녹화, "
            "Ctrl+Alt+S 중지 및 저장, Ctrl+Alt+M 재생, Ctrl+1..5 목록 순 재생).",
        "online.cancelled": "Discord 인증이 취소(또는 실패)되었습니다. 다시 시도하세요.",
        "rec.export_fail": "내보내기 실패: %r",
        "rec.exported": "%s(으)로 내보냈습니다.",
        "rec.import_fail": "가져오기 실패: %r",
        "rec.imported": "녹화 %d개 가져옴%s.",
        "rec.imported_none": " (유효한 것 없음)",
        "rec.no_sel": "내보낼 항목이 선택되지 않았습니다.",
        "rec.notfile": "가져오기 실패: 녹화 파일이 아닙니다.",
        "shared.back": "다시 오신 것을 환영합니다 - 준비되면 시작을 누르세요.",
        "shared.body": "이 Discord 계정이 지금 다른 컴퓨터에서 Snappy AI를 실행 "
            "중.\n세션이 하나가 될 때까지 여기서는 어시스트 일시정지.\n\n구독 하나, 동시에 한 대 - "
            "이것이\n가격을 낮추고 개발을 지속하게 합니다.",
        "shared.close": "닫기",
        "shared.recheck": "지금 재확인",
        "shared.still": "여전히 다른 곳에서 사용 중 - 일시정지 유지.",
        "shared.title": "계정이 다른 곳에서 사용 중",
        "shared.unreachable": "서버에 연결할 수 없음 - 다시 확인합니다.",
        "st.all_files": "모든 파일",
        "st.color_added": "rgb(%d, %d, %d)을(를) %s에 추가 - «적용»이 저장.",
        "st.color_already": "rgb(%d, %d, %d)은(는) 이미 %s에 있습니다.",
        "st.color_full": "%s에는 이미 색이 15개 있습니다 - 먼저 상자 하나를 클릭해 색을 "
            "제거하세요.",
        "st.color_removed": "rgb(%d, %d, %d)을(를) %s에서 제거 - «적용»이 저장.",
        "st.delete_confirm": "녹화 %r을(를) 삭제할까요?\n되돌릴 수 없습니다.",
        "st.deleted": "녹화를 삭제했습니다.",
        "st.engine_dead": "엔진 스레드 사용 불가 - 단축키가 응답하지 않습니다.",
        "st.ent_paused": "구독 %s - 어시스트 일시정지. Stripe에서 갱신 후 재시작.",
        "st.ent_unreachable": "구독 재확인: 서버 연결 불가(세션은 계속 작동).",
        "st.export_fail": "내보내기 실패: %r",
        "st.export_rec_title": "녹화 내보내기",
        "st.export_title": "설정 내보내기",
        "st.exported": "설정을 %s(으)로 내보냈습니다.",
        "st.file_rec": "Snappy AI 녹화",
        "st.file_settings": "Snappy AI 설정",
        "st.follow": "  |  팔로우 %d초 전",
        "st.import_fail": "가져오기 실패: %r",
        "st.import_notfile": "가져오기 실패: 설정 파일이 아닙니다.",
        "st.import_rec_title": "녹화 가져오기",
        "st.import_title": "설정 가져오기",
        "st.imported": "설정 %d개 가져옴%s.",
        "st.imported_ignored": ", 무시: %s",
        "st.ini_over": "적용됨, 다만 config.ini가 덮어씀: %s",
        "st.lib_empty": "목록이 비어 있음 - 내보낼 것 없음.",
        "st.line": "어시스트 %d  |  통과 %d%s  |  테마: %s",
        "st.loop_desc": "이 녹화의 재생 방식: 끔 = 한 번 재생; 켬 = 재생 단축키를 다시 누를 "
            "때까지 반복. 각 녹화는 자체 스위치를 가지며 녹화 자체와 함께 저장됩니다.",
        "st.name_empty": "이름은 비워 둘 수 없습니다.",
        "st.pick_err": "찍기 실패: %r",
        "st.pick_fail": "찍기 실패 - 다시 시도하세요.",
        "st.pick_ok": "(%d, %d)에서 rgb(%d, %d, %d) 취득.",
        "st.pick_wait": "커서를 색 위로 - 3초 후 찍기...",
        "st.preset_desc": "미리 만든 색: %s - 클릭하여 픽커에.",
        "st.rec_count": "녹화 %d / 5개",
        "st.rec_now": "%r 현재: %s.",
        "st.rec_once": "한 번 재생",
        "st.rec_playing": "%r 재생 중...",
        "st.rec_playing_loop": "%r 멈출 때까지 재생 중",
        "st.rec_recording": "녹화 중 - %s(이)가 중지하고 저장",
        "st.rec_repeats": "멈출 때까지 반복",
        "st.registered": "등록: %s    상태: %s",
        "st.rename_prompt": "녹화 #%d의 새 이름:",
        "st.renamed": "녹화 이름을 변경했습니다.",
        "st.reset_confirm": "모든 설정을 기본값으로 초기화할까요?\n계정은 유지, 설정만 영향.",
        "st.rgb_bad": "먼저 유효한 R/G/B 값을 입력하세요.",
        "st.running": "작동 중..",
        "st.saved": "저장하고 적용했습니다.",
        "st.defaults_restored": "기본값으로 되돌렸습니다.",
        "st.saved_bad": "저장했으나 유효하지 않음(이전 값 유지): %s",
        "st.select_rec": "먼저 녹화를 선택하세요.",
        "st.shared_paused": "계정이 다른 곳에서 사용 중 - 어시스트 일시정지. 구독 하나 = 한 "
            "대.",
        "st.standby": "대기..",
        "st.sug_fail": "제안 실패: %r",
        "st.sug_loaded": "후보 rgb(%d, %d, %d)가 피커에 있습니다 - 위 버튼으로 목록에 "
            "추가하세요.",
        "st.sug_loaded_desc": "제안된 UI 색상 rgb(%d, %d, %d) - 영역 의 "
            "%d%%. 클릭하여 픽커에 불러오기.",
        "st.sug_none": "이 영역에서 색상 제안이 없습니다.",
        "st.sug_ok": "후보 %d개 - 하나를 클릭하면 피커에 불러옵니다.",
        "st.sug_wait": "작업 중인 앱을 가리키세요 - 3초 후 샘플링...",
        "tab.advanced": "고급",
        "tab.assist": "어시스트",
        "tab.colors": "색상",
        "tab.experimental": "실험",
        "tab.handler": "처리",
        "tab.help": "도움말",
        "tab.hotkeys": "단축키",
        "tab.macros": "매크로",
        "theme.dark": "다크",
        "theme.light": "라이트",
        "val.accent_matcher.hsv": "클래식 - 구형 엔진",
        "val.accent_matcher.oklab": "지각형 - 색이 보이는 대로 (권장)",
        "val.capture_backend.auto": "자동 - 안전한 폴백과 함께 가장 빠름",
        "val.capture_backend.dxcam": "Desktop Duplication - 대부분의 "
            "PC에서 가장 빠름",
        "val.capture_backend.mss": "호환 - 항상 작동 (원격 데스크톱, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - 실험적",
        "val.follow_learn.accent": "내 색상의 항목만",
        "val.follow_learn.any": "모든 성공 스냅",
        "val.mouse2_action.1": "현재 팔로우 작업 지우기",
        "val.mouse2_action.2": "마지막으로 스냅한 색상 따르기",
        "val.mouse2_action.3": "커서 아래 색을 가져와서 따르기",
        "val.mouse2_action.4": "아무 것도 안 함",
        "val.mouse2_hold_action.1": "현재 팔로우 작업 지우기",
        "val.mouse2_hold_action.2": "마지막으로 스냅한 색상 따르기",
        "val.mouse2_hold_action.3": "커서 아래 색을 가져와서 따르기",
        "val.mouse2_hold_action.4": "아무 것도 안 함",
        "word.off": "끔",
        "word.on": "켬",
    },
    "it": {
        "btn.apply": "Applica",
        "btn.export": "Esporta configurazione",
        "btn.import": "Importa configurazione",
        "btn.language": "Lingua: %s",
        "btn.launch": "Avvia",
        "btn.logout": "Esci",
        "btn.pause": "Pausa",
        "btn.restore": "Ripristina predefiniti",
        "col.accent": "Accento",
        "col.add_pref": "Aggiungi ai colori preferiti",
        "col.add_ref": "Aggiungi ai colori rifiutati",
        "col.chip_desc": "rgb(%d, %d, %d) in %s - clicca la casella "
            "per rimuovere questo colore.",
        "col.chip_off": "%s non contiene colori - la casella barrata "
            "significa spento. Scegli un colore qui sotto e premi il "
            "pulsante di aggiunta corrispondente.",
        "col.exclude": "Esclusione",
        "col.pick": "Prendi colore dallo schermo",
        "col.rgb.desc": "Tre caselle mostrano il colore che c'è ora "
            "nel miscelatore: la prima brilla in base al rosso che "
            "contiene, la seconda al verde, la terza al blu - più "
            "luminoso significa di più. La riga segue il "
            "miscelatore, i toni pronti e i pulsanti dallo schermo; "
            "non si può scrivere.",
        "col.rgb.name": "Valore RGB attuale",
        "col.suggest": "Colori suggeriti da schermo",
        "desc.accent_boost": "Quanto il tuo colore solleva il "
            "punteggio di un elemento (0-3). Alza verso 1,5-2 se "
            "vince ancora l'elemento sbagliato.",
        "desc.accent_coherent": "Il suo colore deve formare una "
            "macchia connessa per contare - puntini sparsi di "
            "retinatura o compressione non qualificano mai un "
            "elemento, non lo potenziano né lo mettono nella lista "
            "mai cliccabile.",
        "desc.accent_color": "Il colore che Snappy AI deve "
            "preferire, mostrato come caselle di colore a destra. "
            "Scegli un colore qui sotto e premi «Aggiungi ai colori "
            "preferiti» per aggiungerlo - quindici caselle al "
            "massimo; un clic su una casella rimuove di nuovo quel "
            "colore. Gli elementi che ne contengono uno vincono i "
            "pareggi. Una lista vuota mostra una casella barrata e "
            "disattiva l'impostazione.",
        "desc.accent_matcher": "Come si confrontano i colori. "
            "Percettivo ordina secondo come i colori appaiono "
            "davvero ed è consigliato; Classico è il motore vecchio, "
            "tenuto per confronto.",
        "desc.accent_only": "Solo gli elementi che contengono il tuo "
            "colore possono essere assistiti; i clic altrove passano "
            "intatti a Windows.",
        "desc.accent_soft": "0-100: quanto contano le versioni più "
            "chiare, scure o slavate del tuo colore. 0 = solo "
            "tonalità esatte.",
        "desc.accent_tolerance": "Quanto deve essere vicino un "
            "colore per contare come tuo (4-90). Più basso = più "
            "severo.",
        "desc.accent_variants": "Anche copie più chiare e più scure "
            "del suo colore valgono, perché gli stati di passaggio, "
            "pressione e attenuazione contino senza allargare la "
            "tolleranza di tinta. Solo luminosità - una tinta "
            "sbagliata non passa mai.",
        "desc.adaptive_threshold": "Temi scuri e documenti slavati "
            "abbassano da soli la propria soglia di rilevamento, "
            "così si trovano anche elementi tenui. Consigliato "
            "attivo.",
        "desc.auto_click": "Attivo, il programma clicca da solo ogni 0,1 secondi sul miglior "
            "elemento dell'area osservata, privilegiando il contrasto. Con un "
            "colore d'accento impostato contano solo gli elementi colorati; "
            "senza colore si cliccano solo elementi molto nitidi. Mai due volte "
            "nello stesso punto né sulle proprie finestre.",
        "desc.auto_click_interval": "Ogni quanto lo schermo viene "
            "controllato per il suo colore (0,5-60). Un numero lento "
            "è quello sicuro: 2-5 va bene per una finestra di "
            "dialogo che osserva.",
        "desc.auto_click_max_clicks": "Quante volte può premere da "
            "solo dopo l'avvio (1-200). Al limite si ferma e lo "
            "dice, così un'impostazione sbagliata non può scappare.",
        "desc.auto_click_min_contrast": "Sulla stessa scala di "
            "»Nitidezza minima del bordo«. Parta dal valore base e "
            "lo alzi se preme la cosa sbagliata: varranno solo "
            "elementi forti e ben disegnati.",
        "desc.auto_click_radius": "Il clic automatico cerca attorno "
            "al centro dello schermo (40-600 px). Più ampio per una "
            "finestra piena; più stretto perché veda solo l'unico "
            "controllo al centro.",
        "desc.auto_click_repeat_px": "Dopo un clic automatico, un "
            "bersaglio entro questi pixel viene lasciato in pace "
            "(0-400). Senza questo, un pulsante rimasto sullo "
            "schermo verrebbe premuto all'infinito.",
        "desc.auto_click_settle_ms": "Il cursore riposa così sul "
            "bersaglio (0-2000 ms) prima del clic, perché il "
            "programma veda prima l'evidenziazione. 120 va bene per "
            "quasi tutte le finestre.",
        "desc.block_bound_keys": "No (predefinito): una scorciatoia "
            "senza Ctrl/Alt/Shift - come 1 o V - agisce in ogni "
            "programma E continua a scrivere normalmente, quindi "
            "premerla a metà frase ne scatena anche l'azione. Sì: "
            "l'azione scatta comunque ovunque, ma il tasto non "
            "scrive più.",
        "desc.capture_backend": "Come si fotografa lo schermo. "
            "Automatico usa il metodo compatibile, che vede quasi tutte le finestre; "
            "Compatibile funziona sempre, incluso Desktop remoto e "
            "macchine virtuali. Vale dopo il riavvio.",
        "desc.color_adapt": "Ogni elemento viene bilanciato sul "
            "bianco col proprio sfondo prima del confronto, così la "
            "luce notturna e le tinte del tema smettono di spingere "
            "il suo colore fuori tolleranza. Lo spenga solo per "
            "confrontare col comparatore non adattato.",
        "desc.contrast_threshold": "Più basso trova elementi più "
            "tenui (e più rumore); più alto esige bordi più nitidi.",
        "desc.default": "Passa il mouse sul nome di un'impostazione "
            "per vederne l'effetto.",
        "desc.exclude_color": "Gli elementi con questi colori non "
            "vengono mai assistiti: i clic su di essi vanno dritti a "
            "Windows, in entrambe le modalità. Mostrati come caselle "
            "di colore a destra - scegli un colore qui sotto e premi "
            "«Aggiungi ai colori rifiutati» per aggiungerne uno "
            "(quindici al massimo); un clic su una casella lo "
            "rimuove. Una lista vuota mostra una casella barrata e "
            "disattiva l'impostazione.",
        "desc.follow_boost": "Con quanta forza l'elemento ricordato "
            "vince i pareggi: 100% può raddoppiarne il punteggio "
            "finché è fresco, 25% è una spinta leggera.",
        "desc.follow_enabled": "Dopo un aggancio riuscito, elementi "
            "dall'aspetto simile o nello stesso posto vincono per un "
            "po' - comodo per barre di scorrimento e clic ripetuti "
            "su un controllo.",
        "desc.follow_learn": "Solo elementi del mio colore: un clic "
            "mancato non può reindirizzare il ricordo. Ogni aggancio "
            "riuscito: il vecchio comportamento fiducioso.",
        "desc.follow_seconds": "Secondi per cui l'elemento ricordato "
            "resta preferito dopo l'ultimo aggancio riuscito "
            "(1-120).",
        "desc.glide_ms": "0 (predefinito) salta all'istante - il più "
            "rapido. 40-120 scivola perché tu possa seguire; muovere "
            "il mouse da soli annulla lo scivolamento.",
        "desc.hold_follow": "Finché tieni premuto il pulsante "
            "sinistro subito dopo un aggancio - o premi di nuovo "
            "sull'elemento ricordato - il cursore resta sul colore "
            "di quell'elemento; stabilizza trascinamenti come le "
            "manopole delle barre di scorrimento. Le pressioni "
            "altrove non vengono mai toccate.",
        "desc.key_launch": "Formato: ctrl+l, f5, space, ctrl+alt+1 "
            "... Modificatori: ctrl, alt, shift, win. Vale dopo "
            "Applica.",
        "desc.key_mode1": "Separate da virgole, es. '1, f1, ctrl+f1, "
            "v'. Cosa fa il modo classico lo spiega la scheda "
            "Scorciatoie.",
        "desc.key_mode2": "Separate da virgole, es. '2, f2, ctrl+f2, "
            "b'. Cosa fa il modo guida lo spiega la scheda "
            "Scorciatoie.",
        "desc.key_pause": "Mouse e tastiera tornano del tutto tuoi, "
            "finché non avvii.",
        "desc.key_play": "Riproduce la registrazione scelta "
            "nell'elenco Macro, o la più recente se nulla è scelto. "
            "Su una registrazione che ripete, la ferma.",
        "desc.key_play_n": "Riproduce la registrazione #%d "
            "dell'elenco numerato nella scheda Macro, per posizione. "
            "Se l'elenco è più corto, non succede nulla.",
        "desc.key_record": "Cattura tutto ciò che fai - ogni tasto, "
            "ogni clic del mouse e ogni movimento del cursore - "
            "mentre il tuo input raggiunge comunque i tuoi "
            "programmi, finché la scorciatoia di stop non lo salva "
            "nell'elenco Macro. Armata solo durante il "
            "funzionamento.",
        "desc.key_record_stop": "Ferma la cattura, salva la sequenza "
            "nell'elenco Macro e interrompe una riproduzione in "
            "corso.",
        "desc.luminance_norm": "I bordi sono valutati rispetto alla "
            "luminosità circostante, così i temi scuri si comportano "
            "come quelli chiari. Consigliato attivo.",
        "desc.macro_action": "La combinazione premuta per te a ogni "
            "pressione del trigger (una pressione = una "
            "combinazione): 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' "
            "... Vuoto = macro spenta.",
        "desc.macro_key": "Il tasto che SIGNIFICA la macro invece di "
            "scrivere: 'b', 'f7', 'ctrl+b' ... In funzionamento una "
            "pressione invia la combinazione accanto esattamente una "
            "volta e il tasto non raggiunge i tuoi programmi. In "
            "pausa scrive normale. Vuoto = macro spenta.",
        "desc.max_area": "Le macchie più grandi sono ignorate - di "
            "solito finestre intere o sfondo, non elementi "
            "cliccabili.",
        "desc.max_dim": "Gli elementi più larghi o alti di così sono "
            "ignorati; quelli che toccano un bordo dello schermo, "
            "come le barre di scorrimento, ricevono il doppio.",
        "desc.merge_distance": "I pezzi più vicini di così (contorno "
            "spezzato, icona accanto alla sua etichetta) diventano "
            "un elemento. Due elementi completi non vengono mai "
            "incollati.",
        "desc.min_area": "Le macchie più piccole sono ignorate come "
            "schizzi, a meno che si incollino a un elemento più "
            "grande.",
        "desc.min_contrast": "Un elemento deve essere almeno così "
            "nitido per essere cliccabile. I valori sotto 28 valgono "
            "28: una soglia di qualità integrata impedisce al rumore "
            "di diventare cliccabile.",
        "desc.motion_3d": "Segue gli elementi mobili con posizione E "
            "dimensione invece di un fit rettilineo: le singole "
            "analisi sbagliate vengono ignorate invece di accecare "
            "l'inseguitore, le curve vengono seguite, e un salto "
            "improvviso di dimensione riavvia la traccia (lo scanner "
            "ha preso un altro elemento). Stesse soglie di velocità, "
            "stesso tetto di 80 px - cambia solo il cervello. "
            "Funziona da solo.",
        "desc.motion_lead_ms": "Millisecondi di percorso con cui "
            "anticipare un elemento mobile (0-300): 40-80 per "
            "scorrimento lento, 100-150 per barre rapide. Tetto di "
            "80 px, disattivato con movimento lento o che svolta.",
        "desc.motion_predict": "Per elementi che si muovono mentre "
            "clicchi (elenchi che scorrono, barre video), mira un "
            "po' avanti così il clic cade sull'elemento. Gli "
            "elementi fermi non cambiano.",
        "desc.mouse2_action": "Cosa fa IN PIÙ un clic destro breve - "
            "il clic destro in sé conserva sempre la sua normale "
            "funzione Windows. Predefinito: nulla.",
        "desc.mouse2_hold_action": "Le stesse scelte, scattano "
            "quando TIENI premuto il destro circa mezzo secondo "
            "invece di cliccare. Una pressione è clic oppure tenuta, "
            "mai entrambe. Predefinito: nulla.",
        "desc.on_target_dist": "Se il tuo clic cade entro questi "
            "pixel dal centro dell'elemento, nulla si muove - hai "
            "colpito.",
        "desc.radius": "Distanza di ricerca in pixel (40-400). "
            "Alzala se l'elemento che vuoi è appena fuori portata; "
            "abbassala se vince il vicino sbagliato.",
        "desc.rapid_click_snap": "No (predefinito): mentre un clic è "
            "in lavorazione gli altri vanno a Windows. Sì: ogni clic "
            "sinistro è assistito.",
        "desc.snap_offset_x": "Sposta il punto di clic lateralmente "
            "dal centro dell'elemento (-200 a 200, negativo a "
            "sinistra). Per un controllo il cui centro è morto - "
            "pulsante diviso, barra di scorrimento - regoli il clic "
            "sul punto vivo una volta invece di lottare a ogni snap.",
        "desc.snap_offset_y": "Sposta il punto di clic verticalmente "
            "dal centro dell'elemento (-200 a 200, negativo verso "
            "l'alto). Come lo spostamento laterale: atterri sulla "
            "parte viva del controllo.",
        "desc.stall_pause_seconds": "Se una scansione si inceppa, "
            "l'assistenza pausa per questo tempo e ogni clic tenuto "
            "ti viene restituito.",
        "desc.watcher_seconds": "Nel modo classico, un secondo "
            "aggancio vicino allo stesso posto entro questo tempo "
            "diventa un doppio clic sull'elemento.",
        "ent.cancel_line": "attivo fino al %s - NON si rinnoverà",
        "ent.canceled_line": "abbonamento terminato%s",
        "ent.expired_line": "scaduto il %s - rinnova su Stripe",
        "ent.past_due_line": "pagamento fallito - sistema la carta "
            "nell'e-mail di ricevuta Stripe; l'accesso torna quando "
            "la fattura è pagata",
        "ent.plan": " (%s)",
        "ent.refunded_line": "rimborsato / stornato - attivazione "
            "revocata",
        "ent.st.active": "attivo",
        "ent.st.canceled": "terminato",
        "ent.st.canceling": "attivo ma in annullamento",
        "ent.st.grant": "concessione di supporto",
        "ent.st.past_due": "PAGAMENTO FALLITO",
        "ent.st.refunded": "rimborsato / stornato",
        "ent.st.trial": "prova",
        "ent.st.unsubscribed": "nessun abbonamento",
        "ent.until": " fino al %s",
        "err.auth_unreachable": "Il server di autenticazione di "
            "Snappy AI non è raggiungibile:\n%s\n\nSnappy AI "
            "funziona solo con una risposta viva da esso.\nRiprova?",
        "err.start_fail": "Snappy AI non è riuscito ad "
            "avviarsi.\nEsegui con --console per i dettagli.",
        "gate.btn.monthly": "Abbonamento mensile a 9,99€",
        "gate.btn.trial": "Acquisto di prova a 1,99€",
        "gate.head.canceled": "Questo abbonamento è stato annullato "
            "- avviane uno nuovo su Stripe per continuare.",
        "gate.head.canceling": "Il tuo abbonamento è impostato per "
            "l'annullamento - resta attivo fino al %s, poi questo "
            "accesso si blocca di nuovo salvo rinnovo.",
        "gate.head.email_mismatch": "Il pagamento è stato fatto con "
            "un'e-mail diversa da quella del tuo account Discord. "
            "Gli abbonamenti funzionano solo sull'e-mail Discord "
            "mostrata sotto - riabbonati con essa, o contatta il "
            "supporto.",
        "gate.head.expired": "L'abbonamento di questo accesso è "
            "scaduto - rinnovalo su Stripe per continuare.",
        "gate.head.none": "Sei entrato, ma questo accesso non ha un "
            "abbonamento attivo. Paga con QUESTA e-mail Discord - un "
            "acquisto su un altro indirizzo non può attivarlo.",
        "gate.head.past_due": "L'ultimo pagamento dell'abbonamento è "
            "fallito - sistemalo su Stripe per riabilitare questo "
            "accesso.",
        "gate.head.refunded": "Questo acquisto è stato rimborsato o "
            "stornato, quindi l'attivazione è stata revocata. Un "
            "nuovo abbonamento su questa e-mail Discord la riattiva.",
        "gate.head.shared": "Questo account è in uso ADESSO su un "
            "ALTRO computer. Snappy AI resta spento finché lo stesso "
            "account Discord gira in due posti - chiudi l'altra "
            "sessione e ricontrolla. Condividere gli abbonamenti "
            "alza i prezzi; per favore non farlo.",
        "gate.msg.active": "Abbonamento attivo - avvio di Snappy "
            "AI...",
        "gate.msg.checking": "Controllo col server...",
        "gate.msg.no_link": "Quel collegamento di pagamento non è "
            "configurato in questa build.",
        "gate.msg.open_fail": "Impossibile aprire un browser. Apri "
            "questo collegamento a mano:\n%s",
        "gate.msg.open_ok": "Stripe è aperto nel browser - paga lì. Questa finestra rileva il pagamento da sola e avvia il motore.",
        "gate.msg.session_gone": "Sessione persa - accedi di nuovo.",
        "gate.msg.still_none": "Ancora nessun abbonamento attivo per "
            "questo accesso.",
        "gate.msg.still_shared": "Ancora in uso su un altro computer "
            "- chiudi quella sessione e ricontrolla.",
        "gate.msg.unreachable": "Server di autenticazione "
            "irraggiungibile: %s",
        "gate.note": "Il motore parte appena l'abbonamento è attivo "
            "- questa finestra si ricontrolla da sola ogni 30 "
            "secondi. Chiuderla torna all'accesso.",
        "gate.prices": "Prova di 2 giorni: 1,99€ (una volta)  -  "
            "abbonamento: 9,99€ / mese.\nL'attivazione arriva fino a "
            "~10 minuti dopo il pagamento; i rinnovi riattivano "
            "automaticamente questo stesso accesso.",
        "gate.title": "%s - Abbonamento%s",
        "hdr.build": "build %s",
        "help.1.b": "Snappy AI guarda lo schermo intorno al cursore, "
            "trova le cose solide a forma di elemento lì vicino - "
            "pulsanti, icone, collegamenti - e sceglie la migliore: "
            "vincono bordi nitidi, dimensione sensata e vicinanza al "
            "cursore. Il tuo colore, l'elenco dei mai-cliccabili e "
            "il ricordo dell'ultimo clic possono inclinare la "
            "scelta. Il cursore mira poi al centro dell'elemento, "
            "non all'angolo del suo riquadro.",
        "help.1.t": "Cosa succede quando clicchi",
        "help.10.b": "1. È avviato? In pausa nulla è intercettato - "
            "«Scorciatoia: avvia assistenza» (Ctrl+L predefinita) è "
            "l'unico acceso/spento.  2. Tieni Shift per un clic per "
            "confermare che il problema era l'assistenza.  3. Vince "
            "l'elemento sbagliato: abbassa «Distanza di ricerca dal "
            "cursore», poi imposta «Il mio colore» o alza «Forza del "
            "vantaggio di colore».  4. Non si trova nulla: abbassa "
            "«Quanto tenue può essere un bordo» e «Nitidezza minima "
            "del bordo», alza «Larghezza o altezza massima» o "
            "«Incolla i pezzi vicini».  5. Una cosa non deve mai "
            "essere assistita: metti il suo colore in in «Colore(i) "
            "mai cliccabili».  6. Ancora sbagliato: riferisci al "
            "supporto cosa hai cliccato e cosa ti aspettavi, "
            "allegando il file di log che Snappy AI scrive nella sua "
            "cartella dati.",
        "help.10.t": "Se qualcosa non va, controlla in quest'ordine",
        "help.2.b": "Il modo guida (predefinito) non mangia alcun "
            "clic: il tuo clic raggiunge il programma e, al "
            "rilascio, il cursore va sull'elemento libero più "
            "vicino. Il modo classico è più forte: un clic mancato "
            "vicino a un elemento è catturato, il cursore si "
            "aggancia e Snappy AI clicca per te. «Distanza di "
            "ricerca dal cursore» fissa il cerchio di ricerca - "
            "alzala se l'elemento che vuoi è appena fuori portata, "
            "abbassala se vince il vicino sbagliato. Tenere Shift "
            "evita un clic in entrambi i modi.",
        "help.2.t": "Si parte da qui: modo e distanza di ricerca",
        "help.3.b": "Nella scheda Elaborazione, «Quanto tenue può "
            "essere un bordo» e «Nitidezza minima del bordo» "
            "decidono quali bordi contano: più bassi trovano più "
            "tenue, più alti ignorano il rumore. «Dimensione minima "
            "dell'elemento», «Area massima dell'elemento» e "
            "«Larghezza o altezza massima» scartano schizzi e "
            "finestre intere. «Incolla i pezzi vicini» unisce un "
            "contorno spezzato, o un'icona accanto alla sua "
            "etichetta, in un elemento. Nella scheda Assistenza, "
            "«Regolazione automatica per schermi tenui» e «Giudica i "
            "bordi per luminosità relativa» fanno sì che i temi "
            "scuri si comportino come i chiari - lasciali attivi.",
        "help.3.t": "Non si trova nulla - o se ne trova troppo",
        "help.4.b": "Nella scheda Colori, «Il mio colore» è il "
            "colore preferito e «Colore(i) mai cliccabili» è "
            "assoluto: quegli elementi non sono mai assistiti. "
            "«Assisti solo il mio colore» limita l'assistenza agli "
            "elementi corrispondenti. In Elaborazione, «Rigore della "
            "corrispondenza colore» dice quanto vicina debba essere "
            "una tinta, «Accetta tonalità simili» fa contare in "
            "parte le versioni più chiare o slavate, e «Forza del "
            "vantaggio di colore» dice quanto il tuo colore solleva "
            "un elemento - alzala se vince ancora quello sbagliato.",
        "help.4.t": "Lavorare coi colori",
        "help.5.b": "«Ricorda l'ultimo elemento cliccato» continua a "
            "preferire l'elemento su cui è caduto il tuo ultimo clic "
            "riuscito, per «Per quanto ricordare» secondi - è ciò "
            "che rende piacevoli barre di scorrimento e pulsanti di "
            "dialogo. «Forza del ricordo» dice con quanta forza "
            "vince, e «Cosa può imparare il ricordo» lo protegge: "
            "con «Solo elementi del mio colore» un clic mancato non "
            "può reindirizzarlo. «Segui l'elemento col pulsante "
            "tenuto» stabilizza i trascinamenti, e le azioni del "
            "pulsante destro in Sperimentale possono seguire o "
            "sgomberare il ricordo col mouse.",
        "help.5.t": "Clic ripetuti su un controllo",
        "help.6.b": "«Anticipa gli elementi in movimento» misura "
            "quanto veloce viaggia l'elemento scelto e mira avanti "
            "di «Quanto anticipare il tiro» millisecondi, così il "
            "clic cade su un elenco che scorre o una barra video "
            "invece che dietro. L'anticipo ha tetto di 80 pixel e si "
            "spegne da solo con elementi fermi o che svoltano.",
        "help.6.t": "Cliccare cose che si muovono",
        "help.7.b": "«Anima il movimento del cursore» = 0 salta "
            "all'istante; 40-120 scivola perché tu possa seguire, e "
            "muovere il mouse da soli annulla lo scivolamento. "
            "«Finestra del doppio clic» in modo classico trasforma "
            "un secondo aggancio vicino allo stesso posto in un "
            "doppio clic. «Assisti ogni clic di una raffica» assiste "
            "ogni clic di una serie invece del solo primo. «Pausa "
            "dopo un intoppo» è la valvola che restituisce un clic "
            "tenuto se una scansione si inceppa.",
        "help.7.t": "Come si sentono i clic",
        "help.8.b": "La scheda Scorciatoie spiega i due modi e il "
            "flusso di registrazione. In breve: le scorciatoie con "
            "Ctrl, Alt, Shift o Win sono riservate a livello di "
            "sistema; i tasti singoli funzionano ovunque e "
            "continuano a digitare. Una macro trasforma una "
            "pressione bloccata in una combinazione intera. Le "
            "registrazioni catturano il tuo input reale - ogni "
            "tasto, clic del mouse e movimento del cursore - e lo "
            "riproducono dalla scheda Macro, ognuna con il proprio "
            "interruttore una volta o ripeti fino allo stop.",
        "help.8.t": "Tasti, macro e registrazioni",
        "help.9.b": "Il pulsante Lingua accanto a «Esporta "
            "configurazione» - anche nelle finestre di accesso e di "
            "abbonamento - cambia tutta l'interfaccia subito, senza "
            "riavviare, e ricorda la tua scelta. Le lingue ancora in "
            "traduzione non sono offerte, quindi ciò che puoi "
            "scegliere è completo.",
        "help.9.t": "Lingua",
        "help.sub": "Ogni impostazione col nome che vedi nella sua "
            "scheda, nell'ordine in cui ti servirà. Passa il mouse "
            "su un nome per la descrizione di una riga; questa "
            "pagina è la forma lunga.",
        "help.tail": "Le impostazioni valgono quando premi Applica. "
            "Un config.ini accanto al programma sostituisce "
            "config.json. Questa pagina spiega; non configura.",
        "help.title": "Regolare Snappy AI con parole semplici",
        "kb.keys.b": "Una scorciatoia con Ctrl, Alt, Shift o Win è "
            "riservata a livello di sistema: la vede solo Snappy AI. "
            "Un tasto nudo (come 1 o 2) agisce in ogni programma E "
            "continua a scrivere - il prezzo è che premerlo a metà "
            "frase ne scatena anche l'azione. Per il comportamento "
            "classico attiva «Le scorciatoie a un tasto ingoiano il "
            "tasto» nella scheda Assistenza. Le macro vanno oltre: "
            "in funzionamento il tasto trigger è ingoiato e la "
            "combinazione accanto è inviata esattamente una volta.",
        "kb.keys.t": "Tasti singoli contro combinazioni",
        "kb.mode.b": "Modo guida (predefinito, scorciatoia 2): il "
            "tuo clic arriva sempre intatto al programma; al "
            "rilascio il cursore va sull'elemento libero più vicino, "
            "così il clic successivo parte da lì. Nulla viene mai "
            "ingoiato - il modo più sicuro.  Modo classico "
            "(scorciatoia 1): se clicchi vicino a un elemento, quel "
            "clic mancato viene catturato, il cursore si aggancia "
            "all'elemento e Snappy AI clicca per te; se non c'è "
            "nulla vicino, il clic ti viene reso intatto.  In "
            "entrambi i modi, tenere Shift mentre clicchi evita "
            "l'assistenza per quel clic.",
        "kb.mode.t": "Cosa fanno i due modi",
        "kb.rec.b": "Durante il funzionamento, premi la scorciatoia "
            "di avvio registrazione (Ctrl+Alt+R per impostazione "
            "predefinita): ogni tasto premuto, ogni pulsante del "
            "mouse cliccato e ogni movimento del cursore viene "
            "catturato E raggiunge comunque i tuoi programmi, così "
            "puoi lavorare normalmente durante la registrazione. "
            "Premi la scorciatoia di stop (Ctrl+Alt+S) per salvarla "
            "nell'elenco nella scheda Macro - cinque registrazioni "
            "ci stanno. Fai clic su una registrazione per "
            "sceglierla, usare «Rinomina» o «Esporta» e impostare il "
            "suo interruttore «Ripeti fino allo stop». La "
            "scorciatoia di riproduzione (Ctrl+Alt+M) riproduce la "
            "registrazione scelta lì; Ctrl+1 a Ctrl+5 riproducono "
            "per posizione nell'elenco. In pausa, nulla viene "
            "registrato e nulla viene iniettato - il tuo input è "
            "completamente tuo.",
        "kb.rec.t": "Come registrare e riprodurre i tuoi tasti e "
            "movimenti del mouse",
        "lang.close": "Chiudi",
        "lang.coverage": "%d%% tradotto",
        "lang.current": "Attuale: %s",
        "lang.progress": "Ancora in traduzione, offerto appena "
            "completo: %s",
        "lang.prompt": "La modifica è immediata; la finestra resta "
            "aperta per provarne altre.",
        "lang.title": "Lingua",
        "lbl.accent_boost": "Forza del vantaggio di colore",
        "lbl.accent_coherent": "Ignora i puntini di colore sparsi",
        "lbl.accent_color": "Il mio colore (colori)",
        "lbl.accent_matcher": "Motore di corrispondenza colore",
        "lbl.accent_only": "Assisti solo il mio colore",
        "lbl.accent_soft": "Accetta tonalità simili",
        "lbl.accent_tolerance": "Rigore della corrispondenza colore",
        "lbl.accent_variants": "Stati chiari e scuri del mio colore",
        "lbl.adaptive_threshold": "Regolazione automatica per "
            "schermi tesi",
        "lbl.auto_click": "Clicca gli elementi da sé",
        "lbl.auto_click_interval": "Secondi tra i clic automatici",
        "lbl.auto_click_max_clicks": "Limite di clic automatici per "
            "sessione",
        "lbl.auto_click_min_contrast": "Quanto nitido deve essere un "
            "bersaglio automatico",
        "lbl.auto_click_radius": "Cerca attorno al centro",
        "lbl.auto_click_repeat_px": "Non ricliccare lo stesso punto",
        "lbl.auto_click_settle_ms": "Pausa prima del clic automatico",
        "lbl.block_bound_keys": "Le scorciatoie a un tasto ingoiano "
            "il tasto",
        "lbl.capture_backend": "Motore di cattura schermo",
        "lbl.color_adapt": "Adattati alla luce dello schermo",
        "lbl.contrast_threshold": "Quanto tenue può essere un bordo",
        "lbl.exclude_color": "Colore(i) mai cliccabili",
        "lbl.follow_boost": "Forza del ricordo",
        "lbl.follow_enabled": "Ricorda l'ultimo elemento cliccato",
        "lbl.follow_learn": "Cosa può imparare il ricordo",
        "lbl.follow_seconds": "Per quanto ricordare",
        "lbl.glide_ms": "Anima il movimento del cursore",
        "lbl.hold_follow": "Segui l'elemento col pulsante tenuto",
        "lbl.key_launch": "Scorciatoia: avvia assistenza",
        "lbl.key_mode1": "Scorciatoia: modo classico (fino a 4 "
            "tasti)",
        "lbl.key_mode2": "Scorciatoia: modo guida (fino a 4 tasti)",
        "lbl.key_pause": "Scorciatoia: pausa",
        "lbl.key_play": "Scorciatoia: riproduci la registrazione "
            "scelta",
        "lbl.key_play_n": "Scorciatoia: riproduci registrazione #%d",
        "lbl.key_record": "Scorciatoia: inizia registrazione",
        "lbl.key_record_stop": "Scorciatoia: ferma e salva la "
            "registrazione",
        "lbl.luminance_norm": "Giudica i bordi per luminosità "
            "relativa",
        "lbl.macro_action": "Macro %d: invia invece",
        "lbl.macro_key": "Macro %d: premi questo tasto",
        "lbl.max_area": "Area massima dell'elemento",
        "lbl.max_dim": "Larghezza o altezza massima dell'elemento",
        "lbl.merge_distance": "Incolla i pezzi vicini",
        "lbl.min_area": "Dimensione minima dell'elemento",
        "lbl.min_contrast": "Nitidezza minima del bordo",
        "lbl.motion_3d": "Inseguimento più intelligente in movimento",
        "lbl.motion_lead_ms": "Quanto anticipare il tiro",
        "lbl.motion_predict": "Anticipa gli elementi in movimento",
        "lbl.watch_center_only": "Osserva solo il centro dello schermo",
        "desc.watch_center_only": "L'assistenza osserva solo un quadrato fisso al centro dello "
            "schermo (dimensione = distanza di ricerca, 150×150 px "
            "predefinita), indipendentemente dalla posizione del cursore. I "
            "clic fuori da quel quadrato non vengono modificati.",
        "lbl.center_follow": "Lo schermo segue l'oggetto",
        "desc.center_follow": "Con «Osserva solo il centro dello schermo» attivo: dopo l'aggancio "
            "di un elemento, l'assistenza muove lo schermo per tenerlo al "
            "centro, soprattutto su piani scorrevoli. Muovi tu lo schermo per "
            "rilasciare l'inseguimento.",
        "lbl.input_backend": "Metodo di immissione",
        "desc.input_backend": "L'iniezione Windows (predefinito) funziona ovunque. Interception "
            "invia tramite driver e i giochi la riconoscono come mouse reale; "
            "richiede il driver Interception installato e interception.dll "
            "accanto al programma; altrimenti usa automaticamente l'iniezione "
            "Windows.",
        "val.input_backend.win32": "Iniezione Windows",
        "val.input_backend.interception": "Interception (driver)",
        "lbl.mouse2_action": "Azione extra del clic destro",
        "lbl.mouse2_hold_action": "Azione del tenere premuto il "
            "destro",
        "lbl.on_target_dist": "Distanza «già sul bersaglio»",
        "lbl.radius": "Distanza di ricerca dal cursore",
        "lbl.rapid_click_snap": "Assisti ogni clic di una raffica",
        "lbl.snap_offset_x": "Punto di clic: sposta a sinistra / "
            "destra",
        "lbl.snap_offset_y": "Punto di clic: sposta in alto / basso",
        "lbl.stall_pause_seconds": "Pausa dopo un intoppo",
        "lbl.watcher_seconds": "Finestra del doppio clic",
        "login.failed": "L'accesso con %s non è completato - "
            "riprova.",
        "login.no_provider": "In questa copia non è integrato alcun "
            "fornitore di accesso.",
        "login.not_configured": "Il file abbonamento non è ancora "
            "configurato in questa build.",
        "login.note": "L'accesso apre il browser e torna da solo a "
            "questa finestra.",
        "login.provider": "Accedi con %s",
        "login.signedin": "Accesso effettuato come %s.",
        "login.sub": "Accedi con Discord - l'abbonamento è legato a "
            "questo account, e i pagamenti devono usarne l'e-mail. "
            "Nessuna password qui.",
        "login.title": "%s - Accedi",
        "login.unreachable": "Server di autenticazione "
            "irraggiungibile: %s",
        "login.waiting": "In attesa del browser - completa l'accesso "
            "%s...",
        "mac.delete": "Elimina",
        "mac.empty": "Ancora nessuna registrazione - avvia, premi la "
            "scorciatoia di registrazione e lavora normalmente: ogni "
            "tasto, clic e movimento del cursore viene catturato.",
        "mac.export": "Esporta",
        "mac.import": "Importa",
        "mac.keys_head": "Macro di tasti",
        "mac.loop": "Ripeti fino allo stop",
        "mac.recordings": "Registrazioni",
        "mac.rename": "Rinomina",
        "mac.row": "Macro %d",
        "mac.sends": "invia",
        "mac.steps": "%d passi",
        "note.advanced": "Impostazioni di distanza e tempo che "
            "cambiano come si sentono i clic, non cosa viene "
            "trovato. Quasi nessuno deve toccarle; i predefiniti "
            "sono quelli testati.",
        "note.assist": "Ogni interruttore che cambia il "
            "comportamento durante il funzionamento. I due modi si "
            "cambiano con i tuoi tasti modo - la scheda Scorciatoie "
            "spiega cosa fa ciascuno. L'assistenza parte sempre in "
            "pausa; Avvia è l'unico acceso/spento. Dove guarda il "
            "motore e come si sentono i clic vive in Avanzate; cosa "
            "conta come elemento in Elaborazione.",
        "note.colors": "Le due liste in alto scelgono quali colori "
            "Snappy AI preferisce o rifiuta. Ognuna mostra i suoi "
            "colori come caselle a destra, quindici al massimo, e un "
            "clic su una casella rimuove di nuovo quel colore; una "
            "lista vuota mostra una casella barrata e conta come "
            "spenta. «Aggiungi ai colori preferiti» e «Aggiungi ai "
            "colori rifiutati» mettono il colore che sta nel "
            "miscelatore nella lista corrispondente. Valore RGB "
            "attuale mostra tre caselle - ognuna larga come cinque "
            "caselle di colore, così la riga copre le stesse "
            "quindici caselle di tutto ciò che sta sotto - che "
            "brillano con quanto rosso, verde e blu ha il colore nel "
            "miscelatore; la riga segue il miscelatore e non si può "
            "digitare. Il miscelatore sotto mescola un colore come "
            "un programma di pittura; tutto ciò che gli sta accanto "
            "siede sul lato destro della finestra, con lo stesso "
            "stacco dal bordo delle impostazioni sopra, e ogni riga "
            "copre la stessa larghezza di quindici caselle: l'alta "
            "vetrina con il suo #valore disegnato dentro, poi i "
            "quindici toni pronti, i due pulsanti di aggiunta e la "
            "riga schermo - «Prendi colore dallo schermo» prende "
            "l'unico colore sotto il cursore, «Colori suggeriti da "
            "schermo» riempie quindici caselle proprie con i colori "
            "trovati intorno al cursore, e un clic su una di esse lo "
            "carica nel miscelatore. La vetrina è alta di proposito: "
            "così le caselle suggerite finiscono esattamente a "
            "livello del cursore del colore a sinistra.",
        "note.experimental": "Scelte di motore, ognuna con un "
            "predefinito testato. Cambiale solo per confrontare "
            "motori, su hardware insolito o se lo chiede il supporto "
            "- il motore di cattura vale dopo il riavvio.",
        "note.handler": "Cosa conta come elemento cliccabile: quanto "
            "tenue può essere un bordo, quanto nitido deve essere e "
            "quanto grande o piccolo può essere un elemento. Non "
            "trovi nulla? Allenta questi valori. Trovi quello che "
            "non serve? Stringili, o usa il tuo colore nella scheda "
            "Colori.",
        "note.keybindings": "Ogni scorciatoia - e sotto, cosa fanno "
            "i due modi, come registrare i tuoi tasti e movimenti "
            "del mouse e in cosa un tasto solo differisce da una "
            "combinazione.",
        "note.macros": "Una macro trasforma una pressione di tasto "
            "in una combinazione intera durante il funzionamento. "
            "Accanto alle macro, le tue registrazioni: fino a cinque "
            "catture con nome di tutto ciò che hai fatto - ogni "
            "tasto, clic del mouse e movimento del cursore - "
            "riprodotte esattamente come registrate. Fai clic su una "
            "registrazione per sceglierla; ogni riga ha il proprio "
            "interruttore «Ripeti fino allo stop», e «Rinomina», "
            "«Esporta», «Importa» ed «Elimina» stanno in fondo alla "
            "casella.",
        "note.macros_keys": "Le scorciatoie registra/riproduci sono "
            "nella scheda Scorciatoie (predefinite: Ctrl+Alt+R "
            "registra, Ctrl+Alt+S ferma e salva, Ctrl+Alt+M "
            "riproduce, Ctrl+1..5 riproducono per posizione).",
        "online.cancelled": "L'autenticazione Discord è stata "
            "annullata (o fallita). Riprova.",
        "rec.export_fail": "Esportazione fallita: %r",
        "rec.exported": "Esportato in %s",
        "rec.import_fail": "Importazione fallita: %r",
        "rec.imported": "%d registrazione/i importata/e%s.",
        "rec.imported_none": " (nessuna era valida)",
        "rec.no_sel": "Nulla di scelto da esportare.",
        "rec.notfile": "Importazione fallita: non è un file di "
            "registrazione.",
        "shared.back": "Bentornato - premi Avvia quando sei pronto.",
        "shared.body": "Questo account Discord esegue Snappy AI su "
            "un altro computer proprio ora.\nL'assistenza è in pausa "
            "qui finché resta una sola sessione.\n\nUn abbonamento, "
            "una macchina alla volta - è ciò che tiene\nbasso il "
            "prezzo e vivo lo sviluppo.",
        "shared.close": "Chiudi",
        "shared.recheck": "Ricontrolla ora",
        "shared.still": "Ancora in uso altrove - resto in pausa.",
        "shared.title": "Account in uso altrove",
        "shared.unreachable": "Server irraggiungibile - "
            "ricontrolleremo.",
        "st.all_files": "Tutti i file",
        "st.color_added": "rgb(%d, %d, %d) aggiunto a %s - Applica "
            "salva.",
        "st.color_already": "rgb(%d, %d, %d) è già in %s.",
        "st.color_full": "%s contiene già 15 colori - clicca prima "
            "una delle sue caselle per rimuovere un colore.",
        "st.color_removed": "Rimosso rgb(%d, %d, %d) da %s - Applica "
            "salva.",
        "st.delete_confirm": "Eliminare la registrazione %r?\nNon si "
            "può annullare.",
        "st.deleted": "Registrazione eliminata.",
        "st.engine_dead": "Thread del motore non disponibile - le "
            "scorciatoie non rispondono.",
        "st.ent_paused": "Abbonamento %s - assistenza in pausa. "
            "Rinnova su Stripe, poi riavvia.",
        "st.ent_unreachable": "Ricontrollo abbonamento: server "
            "irraggiungibile (la sessione continua).",
        "st.export_fail": "Esportazione fallita: %r",
        "st.export_rec_title": "Esporta registrazione",
        "st.export_title": "Esporta impostazioni",
        "st.exported": "Impostazioni esportate in %s",
        "st.file_rec": "Registrazione Snappy AI",
        "st.file_settings": "Impostazioni Snappy AI",
        "st.follow": "  |  seguito %d s fa",
        "st.import_fail": "Importazione fallita: %r",
        "st.import_notfile": "Importazione fallita: non è un file di "
            "impostazioni.",
        "st.import_rec_title": "Importa registrazione/i",
        "st.import_title": "Importa impostazioni",
        "st.imported": "%d impostazione/i importata/e%s.",
        "st.imported_ignored": ", ignorate: %s",
        "st.ini_over": "Applicato, ma config.ini sostituisce: %s",
        "st.lib_empty": "L'elenco è vuoto - nulla da esportare.",
        "st.line": "Assistiti %d  |  lasciati %d%s  |  tema: %s",
        "st.loop_desc": "Stile di riproduzione di QUESTA "
            "registrazione: off = suona una volta; on = ripete "
            "finché non ripremi la scorciatoia di riproduzione. Ogni "
            "registrazione ha il proprio interruttore, salvato con "
            "la registrazione stessa.",
        "st.name_empty": "Il nome non può essere vuoto.",
        "st.pick_err": "Cattura fallita: %r",
        "st.pick_fail": "Cattura fallita - riprova.",
        "st.pick_ok": "Prelevato rgb(%d, %d, %d) in (%d, %d).",
        "st.pick_wait": "Porta il cursore sul colore - cattura fra 3 "
            "s...",
        "st.preset_desc": "Tinta pronta: %s - clicca per caricarla "
            "nel miscelatore.",
        "st.rec_count": "%d di 5 registrazioni",
        "st.rec_now": "%r ora: %s.",
        "st.rec_once": "suona una volta",
        "st.rec_playing": "Riproduzione di %r...",
        "st.rec_playing_loop": "Riproduzione di %r fino allo stop",
        "st.rec_recording": "REGISTRAZIONE - %s ferma e salva",
        "st.rec_repeats": "ripete fino allo stop",
        "st.registered": "Registrato a: %s    Stato: %s",
        "st.rename_prompt": "Nuovo nome per la registrazione #%d:",
        "st.renamed": "Registrazione rinominata.",
        "st.reset_confirm": "Riportare tutte le impostazioni ai "
            "predefiniti?\nGli account si conservano; riguarda solo "
            "le impostazioni.",
        "st.rgb_bad": "Inserisci prima valori R/G/B validi.",
        "st.running": "Attivo..",
        "st.saved": "Salvato e applicato.",
        "st.defaults_restored": "Impostazioni predefinite ripristinate.",
        "st.saved_bad": "Salvato, ma non valido (resta il vecchio): "
            "%s",
        "st.select_rec": "Prima scegli una registrazione.",
        "st.shared_paused": "ACCOUNT IN USO ALTROVE - assistenza in "
            "pausa; un abbonamento = una macchina.",
        "st.standby": "Attesa..",
        "st.sug_fail": "Suggerimento fallito: %r",
        "st.sug_loaded": "Il suggerimento rgb(%d, %d, %d) è nel "
            "miscelatore - aggiungilo a una lista con i pulsanti qui "
            "sopra.",
        "st.sug_loaded_desc": "Colore d'interfaccia suggerito "
            "rgb(%d, %d, %d) - %d%% della regione campionata. Clicca "
            "per caricarlo nel miscelatore.",
        "st.sug_none": "Nessun suggerimento di colore da questa "
            "regione.",
        "st.sug_ok": "%d suggerimenti - cliccane uno per caricarlo "
            "nel miscelatore.",
        "st.sug_wait": "Punta all'app in cui lavori - campionamento "
            "fra 3 s...",
        "tab.advanced": "Avanzate",
        "tab.assist": "Assistenza",
        "tab.colors": "Colori",
        "tab.experimental": "Sperimentale",
        "tab.handler": "Elaborazione",
        "tab.help": "Aiuto",
        "tab.hotkeys": "Scorciatoie",
        "tab.macros": "Macro",
        "theme.dark": "Scuro",
        "theme.light": "Chiaro",
        "val.accent_matcher.hsv": "Classico - il motore vecchio",
        "val.accent_matcher.oklab": "Percettivo - come appaiono i "
            "colori (consigliato)",
        "val.capture_backend.auto": "Automatico - il più veloce con "
            "riserva sicura",
        "val.capture_backend.dxcam": "Desktop Duplication - il più "
            "veloce sulla maggior parte dei PC",
        "val.capture_backend.mss": "Compatibile - funziona sempre "
            "(Desktop remoto, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "sperimentale",
        "val.follow_learn.accent": "Solo elementi del mio colore",
        "val.follow_learn.any": "Ogni aggancio riuscito",
        "val.mouse2_action.1": "Cancella il compito di seguito "
            "attuale",
        "val.mouse2_action.2": "Segui l'ultimo colore agganciato",
        "val.mouse2_action.3": "Prendi il colore sotto il cursore, "
            "poi seguilo",
        "val.mouse2_action.4": "Non fare nulla",
        "val.mouse2_hold_action.1": "Cancella il compito di seguito "
            "attuale",
        "val.mouse2_hold_action.2": "Segui l'ultimo colore "
            "agganciato",
        "val.mouse2_hold_action.3": "Prendi il colore sotto il "
            "cursore, poi seguilo",
        "val.mouse2_hold_action.4": "Non fare nulla",
        "word.off": "No",
        "word.on": "Sì",
    },
    "pt": {
        "btn.apply": "Aplicar",
        "btn.export": "Exportar configuração",
        "btn.import": "Importar configuração",
        "btn.language": "Idioma: %s",
        "btn.launch": "Iniciar",
        "btn.logout": "Sair",
        "btn.pause": "Pausa",
        "btn.restore": "Repor predefinições",
        "col.accent": "Realce",
        "col.add_pref": "Adicionar às preferidas",
        "col.add_ref": "Adicionar às recusadas",
        "col.chip_desc": "rgb(%d, %d, %d) em %s - clique na caixa "
            "para remover esta cor.",
        "col.chip_off": "%s não tem cores - a caixa riscada "
            "significa desligado. Escolha uma cor abaixo e prima o "
            "botão de adicionar correspondente.",
        "col.exclude": "Exclusão",
        "col.pick": "Captar a cor do ecrã",
        "col.rgb.desc": "Três caixas mostram a cor que está no "
            "misturador agora: a primeira brilha conforme o vermelho "
            "que contém, a segunda o verde, a terceira o azul - mais "
            "brilho quer dizer mais. A linha segue o misturador, os "
            "tons prontos e os botões do ecrã; não dá para escrever "
            "nela.",
        "col.rgb.name": "Valor RGB atual",
        "col.suggest": "Sugerir cores do ecrã",
        "desc.accent_boost": "Quanto a sua cor eleva a pontuação de "
            "um elemento (0-3). Suba para 1,5-2 se ainda ganhar o "
            "elemento errado.",
        "desc.accent_coherent": "A sua cor tem de formar uma mancha "
            "ligada para contar - pintas dispersas de pontilhado ou "
            "compressão nunca qualificam um elemento, nem o "
            "potenciam, nem o põem na lista jamais clicável.",
        "desc.accent_color": "A cor que o Snappy AI deve preferir, "
            "mostrada como caixas de cor à direita. Escolha uma cor "
            "abaixo e prima «Adicionar às preferidas» para a "
            "acrescentar - quinze caixas no máximo; clicar numa "
            "caixa remove essa cor de novo. Itens que contêm uma "
            "delas ganham empates. Uma lista vazia mostra uma caixa "
            "riscada e desativa a definição.",
        "desc.accent_matcher": "Como as cores são comparadas. "
            "Percetivo ordena pelo aspeto real das cores e é o "
            "recomendado; Clássico é o motor antigo, guardado para "
            "comparação.",
        "desc.accent_only": "Só os elementos com a sua cor podem ser "
            "assistidos; cliques noutro sítio passam intactos ao "
            "Windows.",
        "desc.accent_soft": "0-100: quanto contam as versões mais "
            "claras, escuras ou desbotadas da sua cor. 0 = só tons "
            "exatos.",
        "desc.accent_tolerance": "Quão perto deve estar uma cor para "
            "contar como sua (4-90). Mais baixo = mais rigoroso.",
        "desc.accent_variants": "Cópias mais claras e mais escuras "
            "da sua cor também valem, para que os estados de "
            "passagem, pressão e atenuação contem sem alargar a "
            "tolerância de tom. Só luminosidade - um tom errado "
            "nunca passa.",
        "desc.adaptive_threshold": "Temas escuros e documentos "
            "desbotados baixam sozinhos a sua fasquia de deteção, "
            "por isso elementos ténues também são encontrados. "
            "Recomendado ligado.",
        "desc.auto_click": "Ligado, o programa clica sozinho a cada 0,1 segundos no melhor "
            "item da área observada, dando prioridade ao contraste. Com cor de "
            "acento definida, só contam os itens com essa cor; sem cor, só são "
            "clicados itens muito nítidos. Nunca duas vezes no mesmo sítio nem "
            "nas suas próprias janelas.",
        "desc.auto_click_interval": "Com que frequência o ecrã é "
            "verificado para a sua cor (0,5-60). Um número lento é o "
            "seguro: 2-5 serve para um diálogo que esteja a "
            "observar.",
        "desc.auto_click_max_clicks": "Quantas vezes pode clicar "
            "sozinho após iniciar (1-200). No limite para e avisa, "
            "para que uma má definição não se descontrole.",
        "desc.auto_click_min_contrast": "Na mesma escala que "
            "»Nitidez mínima da borda«. Comece pelo valor base e "
            "suba se clicar mal: só valerão elementos fortes e bem "
            "desenhados.",
        "desc.auto_click_radius": "O clique automático procura à "
            "volta do centro do ecrã (40-600 px). Mais largo para "
            "uma janela cheia; mais estreito para ver só o único "
            "controlo do meio.",
        "desc.auto_click_repeat_px": "Após um clique automático, um "
            "alvo dentro destes píxeis é deixado em paz (0-400). Sem "
            "isto, um botão que fique no ecrã seria clicado sem "
            "parar.",
        "desc.auto_click_settle_ms": "O cursor descansa assim no "
            "alvo (0-2000 ms) antes do clique, para o programa ver o "
            "destaque primeiro. 120 serve para quase todas as "
            "janelas.",
        "desc.block_bound_keys": "Não (predefinição): um atalho sem "
            "Ctrl/Alt/Shift - como 1 ou V - age em cada programa E "
            "continua a escrever normalmente, por isso premi-lo a "
            "meio de uma frase também dispara a ação. Sim: a ação "
            "continua a disparar em todo o lado, mas a tecla já não "
            "escreve.",
        "desc.capture_backend": "Como o ecrã é fotografado. "
            "Automático usa o método compatível, que vê quase todas as janelas; "
            "Compatível funciona sempre, incluindo Ambiente de "
            "trabalho remoto e máquinas virtuais. Vale após "
            "reiniciar.",
        "desc.color_adapt": "Cada elemento é equilibrado a branco "
            "com o seu próprio fundo antes de comparar, para que a "
            "luz noturna e os tons do tema deixem de empurrar a sua "
            "cor para fora da tolerância. Desligue só para comparar "
            "com o comparador não adaptado.",
        "desc.contrast_threshold": "Mais baixo encontra elementos "
            "mais ténues (e mais ruído); mais alto exige bordas mais "
            "nítidas.",
        "desc.default": "Passe o cursor sobre o nome de uma "
            "definição para ver o que faz.",
        "desc.exclude_color": "Itens com estas cores nunca são "
            "assistidos: cliques neles vão diretamente ao Windows, "
            "em ambos os modos. Mostrados como caixas de cor à "
            "direita - escolha uma cor abaixo e prima «Adicionar às "
            "recusadas» para acrescentar uma (quinze no máximo); "
            "clicar numa caixa remove-a. Uma lista vazia mostra uma "
            "caixa riscada e desativa a definição.",
        "desc.follow_boost": "Com quanta força o elemento lembrado "
            "ganha empates: 100% pode dobrar-lhe a pontuação "
            "enquanto está fresco, 25% é um empurrão leve.",
        "desc.follow_enabled": "Após um encaixe bem sucedido, "
            "elementos parecidos ou no mesmo sítio ganham durante um "
            "bocado - útil para barras de deslocamento e cliques "
            "repetidos num controlo.",
        "desc.follow_learn": "Só elementos da minha cor: um clique "
            "falhado não pode reorientar a memória. Cada encaixe bem "
            "sucedido: o comportamento antigo e confiante.",
        "desc.follow_seconds": "Segundos durante os quais o elemento "
            "lembrado continua preferido após o último encaixe bem "
            "sucedido (1-120).",
        "desc.glide_ms": "0 (predefinição) salta de imediato - o "
            "mais rápido. 40-120 desliza para que possa acompanhar; "
            "mexer o rato você mesmo cancela o deslize.",
        "desc.hold_follow": "Enquanto mantém o botão esquerdo "
            "premido logo após um encaixe - ou prime de novo sobre o "
            "elemento lembrado - o cursor fica na cor desse "
            "elemento; isto estabiliza arrastamentos como as pegas "
            "das barras de deslocamento. Pressões noutro sítio nunca "
            "são tocadas.",
        "desc.key_launch": "Formato: ctrl+l, f5, space, ctrl+alt+1 "
            "... Modificadores: ctrl, alt, shift, win. Vale após "
            "Aplicar.",
        "desc.key_mode1": "Separadas por vírgulas, ex. '1, f1, "
            "ctrl+f1, v'. O que o modo clássico faz é explicado no "
            "separador Atalhos.",
        "desc.key_mode2": "Separadas por vírgulas, ex. '2, f2, "
            "ctrl+f2, b'. O que o modo guia faz é explicado no "
            "separador Atalhos.",
        "desc.key_pause": "O rato e o teclado voltam a ser "
            "inteiramente seus, até iniciar.",
        "desc.key_play": "Reproduz a gravação escolhida na lista de "
            "Macros, ou a mais recente se nenhuma estiver escolhida. "
            "Sobre uma gravação a repetir, pára-a.",
        "desc.key_play_n": "Reproduz a gravação #%d da lista "
            "numerada no separador Macros, pela sua posição. Se a "
            "lista for mais curta, nada acontece.",
        "desc.key_record": "Captura tudo o que faz - cada tecla, "
            "cada clique do rato e cada movimento do cursor - "
            "enquanto o seu input continua a chegar aos seus "
            "programas, até o atalho de parar o guardar na lista de "
            "Macros. Só armada enquanto iniciado.",
        "desc.key_record_stop": "Pára a captura, guarda a sequência "
            "na lista de Macros e interrompe uma reprodução em "
            "curso.",
        "desc.luminance_norm": "As bordas são pontuadas contra o "
            "brilho do que as rodeia, por isso temas escuros "
            "portam-se como claros. Recomendado ligado.",
        "desc.macro_action": "A combinação premida por si a cada "
            "pressão do gatilho (uma pressão = uma combinação): "
            "'ctrl+c', 'ctrl+shift+s', 'space', 'f5' ... Vazio = "
            "macro desligada.",
        "desc.macro_key": "A tecla que SIGNIFICA a macro em vez de "
            "escrever: 'b', 'f7', 'ctrl+b' ... Iniciado, uma pressão "
            "envia a combinação ao lado exatamente uma vez e a tecla "
            "não chega aos seus programas. Em pausa escreve normal. "
            "Vazio = macro desligada.",
        "desc.max_area": "Manchas maiores são ignoradas - costumam "
            "ser janelas inteiras ou fundo, não elementos clicáveis.",
        "desc.max_dim": "Elementos mais largos ou altos do que isto "
            "são ignorados; os que tocam uma borda do ecrã, como "
            "barras de deslocamento, recebem o dobro.",
        "desc.merge_distance": "Pedaços mais próximos do que isto "
            "(um contorno partido, um ícone junto à sua legenda) "
            "tornam-se um elemento. Dois elementos completos nunca "
            "são colados.",
        "desc.min_area": "Manchas menores são ignoradas como "
            "borratos, salvo se se colarem a um elemento maior.",
        "desc.min_contrast": "Um elemento tem de ser pelo menos "
            "assim nítido para poder ser clicado. Valores abaixo de "
            "28 valem 28: um piso de qualidade interno impede que o "
            "ruído seja clicável.",
        "desc.motion_3d": "Segue os elementos móveis com posição E "
            "tamanho em vez de um ajuste reto: as análises más "
            "isoladas são ignoradas em vez de cegar o seguidor, as "
            "curvas são seguidas, e um salto brusco de tamanho "
            "reinicia a pista (o scanner apanhou outro elemento). "
            "Mesmos limites de velocidade, mesmo teto de 80 px - só "
            "o cérebro muda. Funciona sozinho.",
        "desc.motion_lead_ms": "Milissegundos de percurso com que "
            "antecipar um elemento móvel (0-300): 40-80 para rolar "
            "lento, 100-150 para barras rápidas. Teto de 80 px, "
            "desligado com movimento lento ou que vira.",
        "desc.motion_predict": "Para elementos que se mexem enquanto "
            "clica (listas a rolar, barras de vídeo), aponta um "
            "pouco à frente para o clique cair no elemento. Os "
            "parados não mudam.",
        "desc.mouse2_action": "O que um clique direito curto faz A "
            "MAIS - o clique direito em si conserva sempre a sua "
            "função normal do Windows. Predefinição: nada.",
        "desc.mouse2_hold_action": "As mesmas escolhas, disparadas "
            "ao MANTER o botão direito cerca de meio segundo em vez "
            "de clicar. Uma pressão é clique ou pressão mantida, "
            "nunca ambos. Predefinição: nada.",
        "desc.on_target_dist": "Se o seu clique cai dentro destes "
            "pixéis do centro do elemento, nada se mexe - já "
            "acertou.",
        "desc.radius": "Distância de busca em pixéis (40-400). "
            "Aumente se o elemento que quer fica mesmo fora de "
            "alcance; diminua se ganha o vizinho errado.",
        "desc.rapid_click_snap": "Não (predefinição): enquanto um "
            "clique é processado os outros vão ao Windows. Sim: cada "
            "clique esquerdo é assistido.",
        "desc.snap_offset_x": "Desloca o ponto de clique "
            "lateralmente a partir do centro do elemento (-200 a "
            "200, negativo para a esquerda). Para um controlo cujo "
            "meio está morto - botão dividido, barra deslizante - "
            "gire o clique para o ponto vivo uma vez em vez de lutar "
            "a cada snap.",
        "desc.snap_offset_y": "Desloca o ponto de clique "
            "verticalmente a partir do centro do elemento (-200 a "
            "200, negativo para cima). Como o deslocamento lateral: "
            "aterre na parte viva do controlo.",
        "desc.stall_pause_seconds": "Se uma varredura encravar, a "
            "assistência pausa este tempo e qualquer clique mantido "
            "é devolvido a si.",
        "desc.watcher_seconds": "No modo clássico, um segundo "
            "encaixe perto do mesmo sítio dentro deste tempo "
            "torna-se um duplo clique no elemento.",
        "ent.cancel_line": "ativa até %s - NÃO se renovará",
        "ent.canceled_line": "subscrição terminada%s",
        "ent.expired_line": "caducou em %s - renove no Stripe",
        "ent.past_due_line": "pagamento falhou - corrija o cartão no "
            "e-mail de recibo do Stripe; o acesso volta quando a "
            "fatura for paga",
        "ent.plan": " (%s)",
        "ent.refunded_line": "reembolsada / estornada - ativação "
            "revogada",
        "ent.st.active": "ativa",
        "ent.st.canceled": "terminada",
        "ent.st.canceling": "ativa mas a cancelar",
        "ent.st.grant": "concessão de suporte",
        "ent.st.past_due": "PAGAMENTO FALHOU",
        "ent.st.refunded": "reembolsada / estornada",
        "ent.st.trial": "teste",
        "ent.st.unsubscribed": "sem subscrição",
        "ent.until": " até %s",
        "err.auth_unreachable": "O servidor de autenticação do "
            "Snappy AI está inacessível:\n%s\n\nO Snappy AI só "
            "funciona com uma resposta viva dele.\nTentar de novo?",
        "err.start_fail": "O Snappy AI não conseguiu "
            "arrancar.\nExecute com --console para ver os detalhes.",
        "gate.btn.monthly": "Subscrição mensal por 9,99€",
        "gate.btn.trial": "Compra de teste por 1,99€",
        "gate.head.canceled": "Esta subscrição foi cancelada - "
            "comece uma nova no Stripe para continuar.",
        "gate.head.canceling": "A sua subscrição está marcada para "
            "cancelamento - fica ativa até %s, depois esta entrada "
            "bloqueia de novo salvo renovação.",
        "gate.head.email_mismatch": "O pagamento foi feito com um "
            "e-mail diferente do da sua conta Discord. As "
            "subscrições só funcionam no e-mail Discord mostrado em "
            "baixo - subscreva de novo com ele, ou contacte o "
            "suporte.",
        "gate.head.expired": "A subscrição desta entrada caducou - "
            "renove-a no Stripe para continuar.",
        "gate.head.none": "Entrou, mas esta entrada não tem "
            "subscrição ativa. Pague com ESTE e-mail Discord - uma "
            "compra noutro endereço não pode ativá-la.",
        "gate.head.past_due": "O último pagamento da subscrição "
            "falhou - corrija-o no Stripe para reabilitar esta "
            "entrada.",
        "gate.head.refunded": "Esta compra foi reembolsada ou "
            "estornada, por isso a ativação foi revogada. Uma "
            "subscrição nova neste e-mail Discord reativa-a.",
        "gate.head.shared": "Esta conta está A SER usada NOUTRO "
            "computador agora. O Snappy AI continua desligado "
            "enquanto a mesma conta Discord corre em dois sítios - "
            "feche a outra sessão e verifique de novo. Partilhar "
            "subscrições encarece o preço; por favor, não o faça.",
        "gate.msg.active": "Subscrição ativa - a arrancar o Snappy "
            "AI...",
        "gate.msg.checking": "A verificar com o servidor...",
        "gate.msg.no_link": "Essa ligação de pagamento não está "
            "configurada nesta compilação.",
        "gate.msg.open_fail": "Não foi possível abrir um navegador. "
            "Abra esta ligação à mão:\n%s",
        "gate.msg.open_ok": "O Stripe está aberto no seu navegador - pague lá. Esta janela percebe o pagamento sozinha e inicia o mecanismo.",
        "gate.msg.session_gone": "A sessão perdeu-se - entre de "
            "novo.",
        "gate.msg.still_none": "Ainda sem subscrição ativa para esta "
            "entrada.",
        "gate.msg.still_shared": "Ainda em uso noutro computador - "
            "feche essa sessão e verifique de novo.",
        "gate.msg.unreachable": "Servidor de autenticação "
            "inacessível: %s",
        "gate.note": "O motor arranca assim que a subscrição está "
            "ativa - esta janela verifica-se sozinha a cada 30 "
            "segundos. Fechá-la volta à entrada.",
        "gate.prices": "Teste de 2 dias: 1,99€ (uma vez)  -  "
            "subscrição: 9,99€ / mês.\nA ativação chega até ~10 "
            "minutos após o pagamento; as renovações reativam "
            "automaticamente esta mesma entrada.",
        "gate.title": "%s - Subscrição%s",
        "hdr.build": "compilação %s",
        "help.1.b": "O Snappy AI olha o ecrã à volta do seu cursor, "
            "encontra as coisas sólidas com forma de elemento ali "
            "perto - botões, ícones, ligações - e escolhe a melhor: "
            "ganham bordas nítidas, tamanho razoável e proximidade "
            "ao cursor. A sua cor, a lista de jamais clicáveis e a "
            "memória do seu último clique podem inclinar a escolha. "
            "O cursor aponta depois ao centro do elemento, não ao "
            "canto da sua caixa.",
        "help.1.t": "O que acontece quando clica",
        "help.10.b": "1. Está iniciado? Em pausa nada é intercetado "
            "- «Atalho: iniciar assistência» (Ctrl+L por omissão) é "
            "o único ligar/desligar.  2. Mantenha Shift num clique "
            "para confirmar que o problema era a assistência.  3. "
            "Ganha o elemento errado: diminua «Distância de busca "
            "desde o cursor», depois defina «A minha cor» ou suba "
            "«Força da vantagem de cor».  4. Nada é encontrado: "
            "baixe «Quão ténue pode ser uma borda» e «Nitidez mínima "
            "da borda», suba «Largura ou altura máxima» ou «Colar "
            "pedaços próximos».  5. Algo nunca deve ser assistido: "
            "ponha a sua cor em a sua cor em «Cor(es) jamais "
            "clicáveis».  6. Ainda errado: diga ao suporte o que "
            "clicou e o que esperava, e anexe o ficheiro de registo "
            "que o Snappy AI grava na sua pasta de dados.",
        "help.10.t": "Se algo corre mal, verifique por esta ordem",
        "help.2.b": "O modo guia (predefinição) não come nenhum "
            "clique: o seu clique chega ao programa e, ao largar, o "
            "cursor vai ao elemento desimpedido mais próximo. O modo "
            "clássico é mais forte: um clique falhado perto de um "
            "elemento é capturado, o cursor encaixa e o Snappy AI "
            "clica por si. «Distância de busca desde o cursor» fixa "
            "o círculo de busca - aumente se o elemento que quer "
            "fica mesmo fora de alcance, diminua se ganha o vizinho "
            "errado. Manter Shift evita um clique em ambos os modos.",
        "help.2.t": "Comece aqui: modo e distância de busca",
        "help.3.b": "No separador Tratamento, «Quão ténue pode ser "
            "uma borda» e «Nitidez mínima da borda» decidem que "
            "bordas contam: mais baixo encontra mais ténue, mais "
            "alto ignora ruído. «Tamanho mínimo do elemento», «Área "
            "máxima do elemento» e «Largura ou altura máxima» deitam "
            "fora borratos e janelas inteiras. «Colar pedaços "
            "próximos» junta um contorno partido, ou um ícone junto "
            "à sua legenda, num elemento. No separador Assistência, "
            "«Ajuste automático para ecrãs baços» e «Julgar bordas "
            "por brilho relativo» fazem os temas escuros portarem-se "
            "como os claros - deixe-os ligados.",
        "help.3.t": "Nada é encontrado - ou é encontrado demais",
        "help.4.b": "No separador Cores, «A minha cor» é a cor "
            "preferida e «Cor(es) jamais clicáveis» é absoluto: "
            "esses elementos nunca são assistidos. «Assistir só a "
            "minha cor» restringe a assistência a elementos "
            "correspondentes. Em Tratamento, «Rigor da "
            "correspondência de cor» diz quão perto deve estar um "
            "tom, «Aceitar tons parecidos» deixa contar em parte "
            "versões mais claras ou desbotadas, e «Força da vantagem "
            "de cor» diz quanto a sua cor eleva um elemento - suba-a "
            "se ainda ganhar o errado.",
        "help.4.t": "Trabalhar com cores",
        "help.5.b": "«Lembrar o último elemento clicado» continua a "
            "preferir o elemento onde caiu o seu último clique bem "
            "sucedido, durante «Durante quanto tempo lembrar» "
            "segundos - é o que torna agradáveis barras de "
            "deslocamento e botões de diálogo. «Força da memória» "
            "diz com quanta força ganha, e «O que a memória pode "
            "aprender» protege-a: com «Só elementos da minha cor», "
            "um clique falhado não a pode reorientar. «Seguir o "
            "elemento com o botão mantido» estabiliza arrastamentos, "
            "e as ações do botão direito em Experimental podem "
            "seguir ou limpar a memória com o rato.",
        "help.5.t": "Cliques repetidos num controlo",
        "help.6.b": "«Antecipar elementos em movimento» mede a "
            "velocidade do elemento escolhido e aponta à frente "
            "«Quanta antecipação no tiro» milissegundos, para o "
            "clique cair numa lista a rolar ou numa barra de vídeo "
            "em vez de atrás. A antecipação tem teto de 80 pixéis e "
            "desliga-se sozinha com elementos parados ou a virar.",
        "help.6.t": "Clicar coisas que se mexem",
        "help.7.b": "«Animar o movimento do cursor» = 0 salta de "
            "imediato; 40-120 desliza para que possa ver, e mexer o "
            "rato você mesmo cancela o deslize. «Janela de duplo "
            "clique» transforma no modo clássico um segundo encaixe "
            "perto do mesmo sítio num duplo clique. «Assistir cada "
            "clique de uma rajada» assiste cada clique de uma série "
            "em vez de só o primeiro. «Pausa após um encravamento» é "
            "a válvula que devolve um clique mantido se uma "
            "varredura encravar.",
        "help.7.t": "Como se sentem os cliques",
        "help.8.b": "O separador Atalhos explica os dois modos e o "
            "fluxo de gravação. Em resumo: atalhos com Ctrl, Alt, "
            "Shift ou Win são reservados em todo o sistema; teclas "
            "sozinhas disparam em todo o lado e continuam a "
            "escrever. Uma macro transforma um toque bloqueado numa "
            "combinação inteira. As gravações capturam o seu input "
            "real - cada tecla, clique do rato e movimento do cursor "
            "- e reproduzem-no a partir do separador Macros, cada "
            "uma com o seu próprio interruptor uma vez ou repetir "
            "até parar.",
        "help.8.t": "Teclas, macros e gravações",
        "help.9.b": "O botão Idioma ao pé de «Exportar configuração» "
            "- também nas janelas de entrada e de subscrição - muda "
            "toda a interface de imediato, sem reiniciar, e lembra a "
            "sua escolha. Idiomas ainda em tradução não são "
            "oferecidos, portanto qualquer um que possa escolher "
            "está completo.",
        "help.9.t": "Idioma",
        "help.sub": "Cada definição com o nome que vê no seu "
            "separador, pela ordem em que dela precisará. Passe o "
            "cursor sobre um nome para a descrição de uma linha; "
            "esta página é a forma longa.",
        "help.tail": "As definições valem ao premir Aplicar. Um "
            "config.ini ao pé do programa substitui o config.json. "
            "Esta página explica; não configura.",
        "help.title": "Afinar o Snappy AI com palavras simples",
        "kb.keys.b": "Um atalho com Ctrl, Alt, Shift ou Win fica "
            "reservado em todo o sistema: só o Snappy AI o vê. Uma "
            "tecla nua (como 1 ou 2) age em cada programa E continua "
            "a escrever - o preço é que premi-la a meio de uma frase "
            "também dispara a ação. Para o comportamento clássico, "
            "ligue «Atalhos de uma tecla engolem a tecla» no "
            "separador Assistência. As macros vão mais longe: "
            "iniciado, a tecla gatilho é engolida e a combinação ao "
            "lado é enviada exatamente uma vez.",
        "kb.keys.t": "Teclas sozinhas contra combinações",
        "kb.mode.b": "Modo guia (predefinição, atalho 2): o seu "
            "clique chega sempre intacto ao programa; ao largar o "
            "botão, o cursor vai ao elemento desimpedido mais "
            "próximo, assim o próximo clique parte daí. Nada é "
            "jamais engolido - o modo mais seguro.  Modo clássico "
            "(atalho 1): se clicar perto de um elemento, esse clique "
            "falhado é capturado, o cursor encaixa no elemento e o "
            "Snappy AI clica por si; se não houver nada perto, o "
            "clique é devolvido intacto.  Em ambos os modos, manter "
            "Shift ao clicar evita a assistência para esse clique.",
        "kb.mode.t": "O que fazem os dois modos",
        "kb.rec.b": "Enquanto iniciado, prima o seu atalho de início "
            "de gravação (Ctrl+Alt+R por omissão): cada tecla "
            "premida, cada botão do rato clicado e cada movimento do "
            "cursor é capturado E continua a chegar aos seus "
            "programas, pelo que pode trabalhar normalmente enquanto "
            "grava. Prima o atalho de parar (Ctrl+Alt+S) para a "
            "guardar na lista do separador Macros - cabem lá cinco "
            "gravações. Clique numa gravação para a escolher, usar "
            "«Renomear» ou «Exportar» e definir o seu próprio "
            "interruptor «Repetir até parar». O atalho de reprodução "
            "(Ctrl+Alt+M) reproduz a gravação escolhida aí; Ctrl+1 a "
            "Ctrl+5 reproduzem por posição na lista. Em pausa, nada "
            "é gravado e nada é injetado - o seu input é "
            "inteiramente seu.",
        "kb.rec.t": "Como gravar e reproduzir as suas teclas e "
            "movimentos do rato",
        "lang.close": "Fechar",
        "lang.coverage": "%d%% traduzido",
        "lang.current": "Atual: %s",
        "lang.progress": "Ainda em tradução, oferecido assim que "
            "completo: %s",
        "lang.prompt": "A mudança é imediata; a janela fica aberta "
            "para experimentar várias.",
        "lang.title": "Idioma",
        "lbl.accent_boost": "Força da vantagem de cor",
        "lbl.accent_coherent": "Ignorar pintas de cor dispersas",
        "lbl.accent_color": "A minha cor (cores)",
        "lbl.accent_matcher": "Motor de correspondência de cor",
        "lbl.accent_only": "Assistir só a minha cor",
        "lbl.accent_soft": "Aceitar tons parecidos",
        "lbl.accent_tolerance": "Rigor da correspondência de cor",
        "lbl.accent_variants": "Estados claros e escuros da minha "
            "cor",
        "lbl.adaptive_threshold": "Ajuste automático para ecrãs "
            "baços",
        "lbl.auto_click": "Clica nos itens sozinho",
        "lbl.auto_click_interval": "Segundos entre cliques "
            "automáticos",
        "lbl.auto_click_max_clicks": "Limite de cliques automáticos "
            "por sessão",
        "lbl.auto_click_min_contrast": "O quão nítido deve ser um "
            "alvo automático",
        "lbl.auto_click_radius": "Procurar a partir do centro",
        "lbl.auto_click_repeat_px": "Não clicar no mesmo lugar outra "
            "vez",
        "lbl.auto_click_settle_ms": "Pausa antes do clique "
            "automático",
        "lbl.block_bound_keys": "Atalhos de uma tecla engolem a "
            "tecla",
        "lbl.capture_backend": "Motor de captura de ecrã",
        "lbl.color_adapt": "Adaptar à luz do ecrã",
        "lbl.contrast_threshold": "Quão ténue pode ser uma borda",
        "lbl.exclude_color": "Cor(es) jamais clicáveis",
        "lbl.follow_boost": "Força da memória",
        "lbl.follow_enabled": "Lembrar o último elemento clicado",
        "lbl.follow_learn": "O que a memória pode aprender",
        "lbl.follow_seconds": "Durante quanto tempo lembrar",
        "lbl.glide_ms": "Animar o movimento do cursor",
        "lbl.hold_follow": "Seguir o elemento com o botão mantido",
        "lbl.key_launch": "Atalho: iniciar assistência",
        "lbl.key_mode1": "Atalho: modo clássico (até 4 teclas)",
        "lbl.key_mode2": "Atalho: modo guia (até 4 teclas)",
        "lbl.key_pause": "Atalho: pausa",
        "lbl.key_play": "Atalho: reproduzir a gravação escolhida",
        "lbl.key_play_n": "Atalho: reproduzir gravação #%d",
        "lbl.key_record": "Atalho: iniciar gravação",
        "lbl.key_record_stop": "Atalho: parar e guardar gravação",
        "lbl.luminance_norm": "Julgar bordas por brilho relativo",
        "lbl.macro_action": "Macro %d: envia em vez disso",
        "lbl.macro_key": "Macro %d: prima esta tecla",
        "lbl.max_area": "Área máxima do elemento",
        "lbl.max_dim": "Largura ou altura máxima do elemento",
        "lbl.merge_distance": "Colar pedaços próximos",
        "lbl.min_area": "Tamanho mínimo do elemento",
        "lbl.min_contrast": "Nitidez mínima da borda",
        "lbl.motion_3d": "Seguimento mais inteligente em movimento",
        "lbl.motion_lead_ms": "Quanta antecipação no tiro",
        "lbl.motion_predict": "Antecipar elementos em movimento",
        "lbl.watch_center_only": "Observar apenas o centro do ecrã",
        "desc.watch_center_only": "A assistência observa apenas um quadrado fixo no centro do ecrã "
            "(tamanho = distância de pesquisa, 150×150 px por omissão), "
            "independentemente da posição do cursor. Os cliques fora desse "
            "quadrado não são alterados.",
        "lbl.center_follow": "O ecrã segue o alvo",
        "desc.center_follow": "Com «Observar apenas o centro do ecrã» ativo: após capturar um "
            "item, a assistência move o ecrã para o manter no centro, "
            "especialmente em planos com deslocamento. Mova você o ecrã para "
            "libertar o seguimento.",
        "lbl.input_backend": "Método de entrada",
        "desc.input_backend": "A injeção do Windows (predefinido) funciona em todo lado. A "
            "Interception envia através do controlador e os jogos reconhecem-na "
            "como rato real; requer o controlador Interception instalado e "
            "interception.dll junto ao programa; caso contrário usa "
            "automaticamente a injeção do Windows.",
        "val.input_backend.win32": "Injeção do Windows",
        "val.input_backend.interception": "Interception (controlador)",
        "lbl.mouse2_action": "Ação extra do clique direito",
        "lbl.mouse2_hold_action": "Ação de manter o direito premido",
        "lbl.on_target_dist": "Distância de «já acertei»",
        "lbl.radius": "Distância de busca desde o cursor",
        "lbl.rapid_click_snap": "Assistir cada clique de uma rajada",
        "lbl.snap_offset_x": "Ponto de clique: deslocar à esquerda / "
            "direita",
        "lbl.snap_offset_y": "Ponto de clique: deslocar para cima / "
            "baixo",
        "lbl.stall_pause_seconds": "Pausa após um encravamento",
        "lbl.watcher_seconds": "Janela de duplo clique",
        "login.failed": "A entrada com %s não foi concluída - tente "
            "de novo.",
        "login.no_provider": "Esta cópia não traz fornecedor de "
            "entrada.",
        "login.not_configured": "O ficheiro de subscrição ainda não "
            "está configurado nesta compilação.",
        "login.note": "A entrada abre o seu navegador e volta "
            "sozinha a esta janela.",
        "login.provider": "Entrar com %s",
        "login.signedin": "Sessão iniciada como %s.",
        "login.sub": "Entre com Discord - a sua subscrição fica "
            "ligada a esta conta, e os pagamentos devem usar o "
            "e-mail dela. Aqui não há palavra-passe.",
        "login.title": "%s - Entrar",
        "login.unreachable": "Servidor de autenticação inacessível: "
            "%s",
        "login.waiting": "À espera do navegador - termine a entrada "
            "%s...",
        "mac.delete": "Apagar",
        "mac.empty": "Ainda sem gravações - inicie, prima o seu "
            "atalho de gravar e trabalhe normalmente: cada tecla, "
            "clique e movimento do cursor é capturado.",
        "mac.export": "Exportar",
        "mac.import": "Importar",
        "mac.keys_head": "Macros de teclas",
        "mac.loop": "Repetir até parar",
        "mac.recordings": "Gravações",
        "mac.rename": "Renomear",
        "mac.row": "Macro %d",
        "mac.sends": "envia",
        "mac.steps": "%d passos",
        "note.advanced": "Definições de distância e tempo que mudam "
            "como se sentem os cliques, não o que é encontrado. A "
            "maioria das pessoas nunca precisa de lhes tocar; as "
            "predefinições são as testadas.",
        "note.assist": "Cada interruptor que muda o comportamento "
            "enquanto iniciado. Os dois modos mudam com as suas "
            "teclas de modo - o separador Atalhos explica o que cada "
            "um faz. A assistência arranca sempre em pausa; Iniciar "
            "é o único ligar/desligar. Onde o motor olha e como se "
            "sentem os cliques vive em Avançado; o que conta como "
            "elemento, em Tratamento.",
        "note.colors": "As duas listas no topo escolhem que cores o "
            "Snappy AI prefere ou recusa. Cada uma mostra as suas "
            "cores como caixas à direita, quinze no máximo, e clicar "
            "numa caixa remove essa cor de novo; uma lista vazia "
            "mostra uma caixa riscada e conta como desligada. "
            "«Adicionar às preferidas» e «Adicionar às recusadas» "
            "põem a cor que está no misturador na lista "
            "correspondente. Valor RGB atual mostra três caixas - "
            "cada uma com a largura de cinco caixas de cor, pelo que "
            "a fila cobre as mesmas quinze caixas que tudo abaixo - "
            "que brilham com quanto vermelho, verde e azul a cor no "
            "misturador tem; a linha segue o misturador e não aceita "
            "digitação. O misturador abaixo mistura uma cor como um "
            "programa de pintura; tudo ao lado dele fica no lado "
            "direito da janela, com o mesmo espaçamento até à borda "
            "que as definições acima, e cada fila cobre a mesma "
            "largura de quinze caixas: a montra alta com o seu "
            "#valor desenhado dentro, depois os quinze tons prontos, "
            "os dois botões de adicionar e a linha de ecrã - «Captar "
            "a cor do ecrã» tira a única cor sob o cursor, «Sugerir "
            "cores do ecrã» enche quinze caixas próprias com cores "
            "que encontra à volta do cursor, e clicar numa delas "
            "carrega-a no misturador. A montra é alta de propósito: "
            "assim as caixas sugeridas terminam exatamente ao nível "
            "do cursor de cor à esquerda.",
        "note.experimental": "Escolhas de motor, cada uma com uma "
            "predefinição testada. Mude-as só para comparar motores, "
            "em hardware invulgar, ou se o suporte o pedir - o motor "
            "de captura vale após reiniciar.",
        "note.handler": "O que conta como elemento clicável: quão "
            "ténue pode ser uma borda, quão nítida deve ser e que "
            "tamanho pode ter um elemento. Não encontra nada? "
            "Alargue estes valores. Encontra o que não deve? "
            "Aperte-os, ou use a sua cor no separador Cores.",
        "note.keybindings": "Cada atalho - e por baixo, o que fazem "
            "os dois modos, como gravar as suas teclas e movimentos "
            "do rato e em que uma tecla sozinha difere de uma "
            "combinação.",
        "note.macros": "Uma macro transforma um toque de tecla numa "
            "combinação inteira enquanto iniciado. Ao lado das "
            "macros, as suas gravações: até cinco capturas com nome "
            "de tudo o que fez - cada tecla, clique do rato e "
            "movimento do cursor - reproduzidas exatamente como "
            "gravadas. Clique numa gravação para a escolher; cada "
            "linha tem o seu próprio interruptor «Repetir até "
            "parar», e «Renomear», «Exportar», «Importar» e «Apagar» "
            "ficam no fundo da caixa.",
        "note.macros_keys": "Os atalhos de gravar/reproduzir estão "
            "no separador Atalhos (predefinições: Ctrl+Alt+R gravar, "
            "Ctrl+Alt+S parar e guardar, Ctrl+Alt+M reproduzir, "
            "Ctrl+1..5 reproduzir por posição).",
        "online.cancelled": "A autenticação Discord foi cancelada "
            "(ou falhou). Tente de novo.",
        "rec.export_fail": "Exportação falhou: %r",
        "rec.exported": "Exportado para %s",
        "rec.import_fail": "Importação falhou: %r",
        "rec.imported": "%d gravação(ões) importada(s)%s.",
        "rec.imported_none": " (nenhuma era válida)",
        "rec.no_sel": "Nada escolhido para exportar.",
        "rec.notfile": "Importação falhou: não é um ficheiro de "
            "gravação.",
        "shared.back": "Bem-vindo de volta - prima Iniciar quando "
            "estiver pronto.",
        "shared.body": "Esta conta Discord executa o Snappy AI "
            "noutro computador agora mesmo.\nA assistência fica em "
            "pausa aqui até restar uma só sessão.\n\nUma subscrição, "
            "uma máquina de cada vez - é o que mantém\no preço baixo "
            "e o desenvolvimento a andar.",
        "shared.close": "Fechar",
        "shared.recheck": "Verificar agora",
        "shared.still": "Ainda em uso noutro sítio - ficamos em "
            "pausa.",
        "shared.title": "Conta em uso noutro sítio",
        "shared.unreachable": "Servidor inacessível - voltaremos a "
            "verificar.",
        "st.all_files": "Todos os ficheiros",
        "st.color_added": "rgb(%d, %d, %d) acrescentado a %s - "
            "Aplicar guarda.",
        "st.color_already": "rgb(%d, %d, %d) já está em %s.",
        "st.color_full": "%s já tem 15 cores - clique primeiro numa "
            "das caixas para remover uma cor.",
        "st.color_removed": "Removido rgb(%d, %d, %d) de %s - "
            "Aplicar guarda.",
        "st.delete_confirm": "Apagar a gravação %r?\nIsto não pode "
            "ser desfeito.",
        "st.deleted": "Gravação apagada.",
        "st.engine_dead": "Thread do motor indisponível - os atalhos "
            "não respondem.",
        "st.ent_paused": "Subscrição %s - assistência em pausa. "
            "Renove no Stripe e reinicie.",
        "st.ent_unreachable": "Reverificação de subscrição: servidor "
            "inacessível (a sessão continua).",
        "st.export_fail": "Exportação falhou: %r",
        "st.export_rec_title": "Exportar gravação",
        "st.export_title": "Exportar definições",
        "st.exported": "Definições exportadas para %s",
        "st.file_rec": "Gravação do Snappy AI",
        "st.file_settings": "Definições do Snappy AI",
        "st.follow": "  |  seguimento há %d s",
        "st.import_fail": "Importação falhou: %r",
        "st.import_notfile": "Importação falhou: não é um ficheiro "
            "de definições.",
        "st.import_rec_title": "Importar gravação(ões)",
        "st.import_title": "Importar definições",
        "st.imported": "%d definição(ões) importada(s)%s.",
        "st.imported_ignored": ", ignoradas: %s",
        "st.ini_over": "Aplicado, mas o config.ini substitui: %s",
        "st.lib_empty": "A lista está vazia - nada a exportar.",
        "st.line": "Assistidos %d  |  deixados %d%s  |  tema: %s",
        "st.loop_desc": "Estilo de reprodução DESTA gravação: "
            "desligado = toca uma vez; ligado = repete até voltar a "
            "premir o atalho de reprodução. Cada gravação tem o seu "
            "próprio interruptor, guardado com a própria gravação.",
        "st.name_empty": "O nome não pode ficar vazio.",
        "st.pick_err": "Captação falhou: %r",
        "st.pick_fail": "Captação falhou - tente de novo.",
        "st.pick_ok": "Captado rgb(%d, %d, %d) em (%d, %d).",
        "st.pick_wait": "Leve o cursor à cor - captação em 3 s...",
        "st.preset_desc": "Tom pronto: %s - clique para o carregar "
            "no misturador.",
        "st.rec_count": "%d de 5 gravações",
        "st.rec_now": "%r agora: %s.",
        "st.rec_once": "toca uma vez",
        "st.rec_playing": "A reproduzir %r...",
        "st.rec_playing_loop": "A reproduzir %r até parar",
        "st.rec_recording": "A GRAVAR - %s pára e guarda",
        "st.rec_repeats": "repete até parar",
        "st.registered": "Registado em: %s    Estado: %s",
        "st.rename_prompt": "Nome novo para a gravação #%d:",
        "st.renamed": "Gravação renomeada.",
        "st.reset_confirm": "Repor todas as definições nas "
            "predefinições?\nAs contas conservam-se; isto só toca "
            "nas definições.",
        "st.rgb_bad": "Introduza primeiro valores R/G/B válidos.",
        "st.running": "Ativo..",
        "st.saved": "Guardado e aplicado.",
        "st.defaults_restored": "Predefinições restauradas.",
        "st.saved_bad": "Guardado, mas inválido (mantém-se o "
            "antigo): %s",
        "st.select_rec": "Escolha primeiro uma gravação.",
        "st.shared_paused": "CONTA EM USO NOUTRO SÍTIO - assistência "
            "em pausa; uma subscrição = uma máquina.",
        "st.standby": "Em espera..",
        "st.sug_fail": "Sugestão falhou: %r",
        "st.sug_loaded": "A sugestão rgb(%d, %d, %d) está no "
            "misturador - acrescente-a a uma lista com os botões "
            "acima.",
        "st.sug_loaded_desc": "Cor de interface sugerida rgb(%d, %d, "
            "%d) - %d%% da região amostrada. Clique para a carregar "
            "no misturador.",
        "st.sug_none": "Sem sugestões de cor desta região.",
        "st.sug_ok": "%d sugestões - clique numa para a carregar no "
            "misturador.",
        "st.sug_wait": "Aponte para a app em que trabalha - "
            "amostragem em 3 s...",
        "tab.advanced": "Avançado",
        "tab.assist": "Assistência",
        "tab.colors": "Cores",
        "tab.experimental": "Experimental",
        "tab.handler": "Tratamento",
        "tab.help": "Ajuda",
        "tab.hotkeys": "Atalhos",
        "tab.macros": "Macros",
        "theme.dark": "Escuro",
        "theme.light": "Claro",
        "val.accent_matcher.hsv": "Clássico - o motor antigo",
        "val.accent_matcher.oklab": "Percetivo - como as cores "
            "parecem (recomendado)",
        "val.capture_backend.auto": "Automático - o mais rápido com "
            "reserva segura",
        "val.capture_backend.dxcam": "Desktop Duplication - o mais "
            "rápido na maioria dos PC",
        "val.capture_backend.mss": "Compatível - funciona sempre "
            "(Ambiente remoto, MV)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "experimental",
        "val.follow_learn.accent": "Só elementos da minha cor",
        "val.follow_learn.any": "Cada encaixe bem sucedido",
        "val.mouse2_action.1": "Limpar a tarefa de seguimento atual",
        "val.mouse2_action.2": "Seguir a última cor captada",
        "val.mouse2_action.3": "Captar a cor sob o cursor e segui-la",
        "val.mouse2_action.4": "Não fazer nada",
        "val.mouse2_hold_action.1": "Limpar a tarefa de seguimento "
            "atual",
        "val.mouse2_hold_action.2": "Seguir a última cor captada",
        "val.mouse2_hold_action.3": "Captar a cor sob o cursor e "
            "segui-la",
        "val.mouse2_hold_action.4": "Não fazer nada",
        "word.off": "Não",
        "word.on": "Sim",
    },
    "nl": {
        "btn.apply": "Toepassen",
        "btn.export": "Configuratie exporteren",
        "btn.import": "Configuratie importeren",
        "btn.language": "Taal: %s",
        "btn.launch": "Starten",
        "btn.logout": "Afmelden",
        "btn.pause": "Pauze",
        "btn.restore": "Standaardwaarden herstellen",
        "col.accent": "Accent",
        "col.add_pref": "Als voorkeur toevoegen",
        "col.add_ref": "Als geweigerde toevoegen",
        "col.chip_desc": "rgb(%d, %d, %d) in %s - klik op het vakje "
            "om deze kleur te verwijderen.",
        "col.chip_off": "%s bevat geen kleuren - het doorgekruiste "
            "vak betekent uit. Kies hieronder een kleur en druk op "
            "de bijpassende toevoegknop.",
        "col.exclude": "Uitsluiten",
        "col.pick": "Kleur van scherm oppakken",
        "col.rgb.desc": "Drie vakjes tonen de kleur die nu in de "
            "menger staat: het eerste licht op naarmate hij meer "
            "rood bevat, het tweede groen, het derde blauw - feller "
            "betekent meer. De rij volgt de menger, de vaste tinten "
            "en de schermknoppen; typen kan niet.",
        "col.rgb.name": "Huidige RGB-waarde",
        "col.suggest": "Schermkleuren voorstellen",
        "desc.accent_boost": "Hoezeer uw kleur de score van een "
            "element optilt (0-3). Verhoog richting 1,5-2 als nog "
            "steeds het verkeerde element wint.",
        "desc.accent_coherent": "Uw kleur moet een verbonden vlek "
            "vormen om te tellen - verspreide dither- of "
            "compressiespikkels kwalificeren nooit een element, "
            "boosten het niet en zetten het niet op de "
            "nooit-klikbaar-lijst.",
        "desc.accent_color": "De kleur die Snappy AI moet verkiezen, "
            "getoond als kleurvakjes rechts. Kies hieronder een "
            "kleur en druk op «Als voorkeur toevoegen» om hem toe te "
            "voegen - vijftien vakjes hoogstens; een klik op een "
            "vakje haalt die kleur er weer uit. Items met een ervan "
            "winnen gelijke standen. Een lege lijst toont een "
            "doorgekruist vak en zet de instelling uit.",
        "desc.accent_matcher": "Hoe kleuren vergeleken worden. "
            "Perceptueel rangschikt op hoe kleuren er echt uitzien "
            "en is aanbevolen; Klassiek is de oude motor, bewaard "
            "voor vergelijking.",
        "desc.accent_only": "Alleen elementen met uw kleur kunnen "
            "geassisteerd worden; klikken elders gaan onaangetast "
            "naar Windows.",
        "desc.accent_soft": "0-100: in welke mate lichtere, donkere "
            "of verschoten versies van uw kleur toch meetellen. 0 = "
            "alleen exacte tinten.",
        "desc.accent_tolerance": "Hoe dicht een kleur bij de uwe "
            "moet liggen om mee te tellen (4-90). Lager = strenger.",
        "desc.accent_variants": "Lichtere en donkerdere kopieën van "
            "uw kleur tellen ook, zodat zweef-, druk- en gedempte "
            "toestanden gelden zonder de kleurtolerantie te "
            "verbreden. Alleen helderheid - een verkeerde kleurtint "
            "komt er nooit door.",
        "desc.adaptive_threshold": "Donkere thema's en verschoten "
            "documenten verlagen zelf hun detectielat, zodat ook "
            "vage elementen gevonden worden. Aanbevolen aan.",
        "desc.auto_click": "Aangezet klikt het programma elke 0,1 seconde zelf op het beste "
            "item in het bewaakte gebied, eerst op contrast gesorteerd. Met een "
            "accentkleur komen alleen items met die kleur in aanmerking; zonder "
            "kleur worden alleen zeer scherp getekende items geklikt. Nooit "
            "twee keer op dezelfde plek, nooit eigen vensters.",
        "desc.auto_click_interval": "Hoe vaak het scherm op uw kleur "
            "wordt gecontroleerd (0,5-60). Een langzaam getal is "
            "veilig: 2-5 past bij een dialoog waar u naar kijkt.",
        "desc.auto_click_max_clicks": "Hoe vaak het na het starten "
            "zelf mag klikken (1-200). Bij de limiet stopt het en "
            "meldt het, zodat een foute instelling niet op hol "
            "slaat.",
        "desc.auto_click_min_contrast": "Op dezelfde schaal als "
            "»Minimale randscherpte«. Begin bij de standaard en "
            "verhoog als er mis wordt geklikt: alleen sterke, scherp "
            "getekende elementen tellen dan.",
        "desc.auto_click_radius": "Automatisch klikken zoekt rond "
            "het midden van het scherm (40-600 px). Breder voor een "
            "vol venster; smaller zodat het alleen dat ene element "
            "in het midden ziet.",
        "desc.auto_click_repeat_px": "Na een automatische klik wordt "
            "een doel binnen zoveel pixels met rust gelaten (0-400). "
            "Zonder dit zou een knop die blijft staan steeds opnieuw "
            "worden geklikt.",
        "desc.auto_click_settle_ms": "De cursor rust zo op het doel "
            "(0-2000 ms) voor de klik, zodat het programma eerst de "
            "markering ziet. 120 past bij de meeste vensters.",
        "desc.block_bound_keys": "Uit (standaard): een sneltoets "
            "zonder Ctrl/Alt/Shift - zoals 1 of V - werkt in elk "
            "programma EN typt gewoon door, dus hem midden in een "
            "zin drukken triggert ook de actie. Aan: de actie vuurt "
            "nog steeds overal, maar de toets typt niet meer.",
        "desc.capture_backend": "Hoe het scherm gefotografeerd "
            "wordt. Automatisch gebruikt de compatibele methode, die bijna alle vensters ziet; "
            "Compatibel werkt altijd, ook bij Remote Desktop en "
            "virtuele machines. Geldt na herstart.",
        "desc.color_adapt": "Elk element wordt vóór het vergelijken "
            "witgebalanceerd op de eigen achtergrond, zodat "
            "nachtlampje en themakleuren uw kleur niet meer uit de "
            "tolerantie duwen. Alleen uitschakelen om met de "
            "onaangepaste vergelijker te vergelijken.",
        "desc.contrast_threshold": "Lager vindt vagere elementen (en "
            "meer ruis); hoger eist scherpere randen.",
        "desc.default": "Beweeg over de naam van een instelling om "
            "te zien wat deze doet.",
        "desc.exclude_color": "Items met deze kleuren worden nooit "
            "geholpen: klikken erop gaan rechtstreeks naar Windows, "
            "in beide modi. Getoond als kleurvakjes rechts - kies "
            "hieronder een kleur en druk op «Als geweigerde "
            "toevoegen» om er een toe te voegen (vijftien "
            "hoogstens); een klik op een vakje haalt hem eruit. Een "
            "lege lijst toont een doorgekruist vak en zet de "
            "instelling uit.",
        "desc.follow_boost": "Hoe sterk het onthouden element "
            "gelijke spelen wint: 100% kan de score vers "
            "verdubbelen, 25% is een licht duwtje.",
        "desc.follow_enabled": "Na een geslaagde vang winnen "
            "gelijkende elementen of elementen op dezelfde plek een "
            "tijdje - handig voor schuifbalken en herhaalde klikken "
            "op één knop.",
        "desc.follow_learn": "Alleen elementen in mijn kleur: een "
            "mis klik kan het geheugen niet van koers laten "
            "veranderen. Elke geslaagde vang: het oude, goedgelovige "
            "gedrag.",
        "desc.follow_seconds": "Seconden dat het onthouden element "
            "voorkomt blijft na uw laatste geslaagde vang (1-120).",
        "desc.glide_ms": "0 (standaard) springt meteen - snelst. "
            "40-120 glijdt zodat u kunt kijken; zelf de muis bewegen "
            "breekt het glijden af.",
        "desc.hold_follow": "Zolang u de linkerknop ingedrukt houdt "
            "vlak na een vang - of opnieuw drukt op het onthouden "
            "element - blijft de cursor op de kleur van dat element; "
            "dit stabiliseert slepen zoals schuifbalkknoppen. "
            "Drukken ergens anders wordt nooit aangeraakt.",
        "desc.key_launch": "Formaat: ctrl+l, f5, space, ctrl+alt+1 "
            "... Wijzigingstoetsen: ctrl, alt, shift, win. Geldt na "
            "Toepassen.",
        "desc.key_mode1": "Komma-gescheiden, bijv. '1, f1, ctrl+f1, "
            "v'. Wat de klassieke modus doet legt het tabblad "
            "Sneltoetsen uit.",
        "desc.key_mode2": "Komma-gescheiden, bijv. '2, f2, ctrl+f2, "
            "b'. Wat de gidsmodus doet legt het tabblad Sneltoetsen "
            "uit.",
        "desc.key_pause": "Muis en toetsenbord zijn weer helemaal "
            "van u, tot u start.",
        "desc.key_play": "Speelt de in de Macro-lijst gekozen "
            "opname, of de nieuwste als niets gekozen is. Op een "
            "herhalende opname stopt hij die.",
        "desc.key_play_n": "Speelt opname #%d van de genummerde "
            "lijst op het tabblad Macro's, op positie. Is de lijst "
            "korter, dan gebeurt er niets.",
        "desc.key_record": "Legt alles vast wat u doet - elke toets, "
            "elke muisklik en elke cursorbeweging - terwijl uw "
            "invoer uw programma's nog steeds bereikt, tot de "
            "stop-sneltoets het in de Macro-lijst bewaart. Alleen "
            "scherp terwijl gestart.",
        "desc.key_record_stop": "Stopt het vastleggen, bewaart de "
            "reeks in de Macro-lijst en stopt een lopende weergave.",
        "desc.luminance_norm": "Randen worden gescoord tegen de "
            "helderheid van hun omgeving, zodat donkere thema's zich "
            "gedragen als lichte. Aanbevolen aan.",
        "desc.macro_action": "De combinatie die voor u wordt "
            "ingedrukt bij elke triggerdruk (één druk = één "
            "combinatie): 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' "
            "... Leeg = macro uit.",
        "desc.macro_key": "De toets die de macro BETEKENT in plaats "
            "van typen: 'b', 'f7', 'ctrl+b' ... Gestart stuurt één "
            "druk de combinatie ernaast precies één keer en bereikt "
            "de toets uw programma's niet. Gepauzeerd typt hij "
            "gewoon. Leeg = macro uit.",
        "desc.max_area": "Grotere vlekken worden genegeerd - meestal "
            "hele vensters of achtergrond, geen klikbare elementen.",
        "desc.max_dim": "Elementen breder of hoger dan dit worden "
            "genegeerd; elementen tegen een schermrand, zoals "
            "schuifbalken, krijgen het dubbele.",
        "desc.merge_distance": "Stukken dichter bij elkaar dan dit "
            "(gebroken omtrek, icoon naast zijn label) worden één "
            "element. Twee volledige elementen worden nooit geplakt.",
        "desc.min_area": "Kleinere vlekken worden genegeerd als "
            "spetters, tenzij ze aan een groter element plakken.",
        "desc.min_contrast": "Een element moet minstens zo scherp "
            "zijn om überhaupt klikbaar te zijn. Waarden onder 28 "
            "gelden als 28: een ingebouwde kwaliteitsdrempel houdt "
            "ruis niet-klikbaar.",
        "desc.motion_3d": "Volgt bewegende elementen met positie EN "
            "grootte in plaats van een rechte fit: losse foute scans "
            "worden genegeerd in plaats van de volger te verblinden, "
            "bochten worden gevolgd, en een plotselinge "
            "groottesprong start het spoor opnieuw (de scanner pakte "
            "een ander element). Zelfde snelheidsdrempels, zelfde "
            "plafond van 80 px - alleen slimmere logica. Werkt "
            "zelfstandig.",
        "desc.motion_lead_ms": "Milliseconden beweging waarmee een "
            "bewegend element wordt voorlopen (0-300): 40-80 voor "
            "traag scrollen, 100-150 voor snelle balken. Plafond van "
            "80 px, uit bij traag of draaiend bewegen.",
        "desc.motion_predict": "Voor elementen die bewegen tijdens "
            "het klikken (scrollende lijsten, videobalken) mik iets "
            "vooruit zodat de klik op het element landt. Stille "
            "elementen blijven gelijk.",
        "desc.mouse2_action": "Wat een korte rechterklik EXTRA doet "
            "- de rechterklik zelf houdt altijd zijn normale "
            "Windows-functie. Standaard: niets.",
        "desc.mouse2_hold_action": "Dezelfde keuzes, vuurend wanneer "
            "u de rechterknop ongeveer een halve seconde INHOUDT in "
            "plaats van klikken. Een druk is klik of inhouden, nooit "
            "beide. Standaard: niets.",
        "desc.on_target_dist": "Valt uw klik binnen dit aantal "
            "pixels van het middelpunt van het element, dan beweegt "
            "er niets - u raakte.",
        "desc.radius": "Zoekafstand in pixels (40-400). Verhoog als "
            "het gewenste element net buiten bereik zit; verlaag als "
            "de verkeerde buur wint.",
        "desc.rapid_click_snap": "Uit (standaard): terwijl een klik "
            "loopt gaan de andere naar Windows. Aan: elke linkerklik "
            "wordt geassisteerd.",
        "desc.snap_offset_x": "Verschuift het klikpunt zijwaarts "
            "vanuit het midden van het element (-200 tot 200, "
            "negatief naar links). Voor een bediening met een dood "
            "midden - gesplitste knop, schuifbalk - draai de klik "
            "eenmaal naar de levende plek in plaats van bij elke "
            "snap te vechten.",
        "desc.snap_offset_y": "Verschuift het klikpunt verticaal "
            "vanuit het midden van het element (-200 tot 200, "
            "negatief omhoog). Net als de zijwaartse verschuiving: "
            "land op het levende deel.",
        "desc.stall_pause_seconds": "Als een scan ooit hapert, "
            "pauzeert de assistentie zo lang en krijgt u elke "
            "ingehouden klik terug.",
        "desc.watcher_seconds": "In klassieke modus wordt een tweede "
            "vang dicht bij dezelfde plek binnen deze tijd een "
            "dubbelklik op het element.",
        "ent.cancel_line": "actief tot %s - wordt NIET verlengd",
        "ent.canceled_line": "abonnement beëindigd%s",
        "ent.expired_line": "verlopen op %s - verleng op Stripe",
        "ent.past_due_line": "betaling mislukt - maak de kaart in "
            "orde in de Stripe-kwitantie-e-mail; toegang keert terug "
            "zodra de factuur betaald is",
        "ent.plan": " (%s)",
        "ent.refunded_line": "terugbetaald / teruggevorderd - "
            "activatie ingetrokken",
        "ent.st.active": "actief",
        "ent.st.canceled": "beëindigd",
        "ent.st.canceling": "actief maar wordt opgezegd",
        "ent.st.grant": "supporttoelage",
        "ent.st.past_due": "BETALING MISLUKT",
        "ent.st.refunded": "terugbetaald / teruggevorderd",
        "ent.st.trial": "proef",
        "ent.st.unsubscribed": "geen abonnement",
        "ent.until": " tot %s",
        "err.auth_unreachable": "De Snappy AI-authserver is "
            "onbereikbaar:\n%s\n\nSnappy AI werkt alleen met een "
            "levend antwoord ervan.\nOpnieuw proberen?",
        "err.start_fail": "Snappy AI kon niet starten.\nStart met "
            "--console voor details.",
        "gate.btn.monthly": "Maandabonnement voor 9,99€",
        "gate.btn.trial": "Proefkoop voor 1,99€",
        "gate.head.canceled": "Dit abonnement is opgezegd - begin "
            "een nieuw op Stripe om door te gaan.",
        "gate.head.canceling": "Uw abonnement staat op opzeggen - "
            "het blijft actief tot %s, daarna vergrendelt deze "
            "aanmelding opnieuw tenzij u verlengt.",
        "gate.head.email_mismatch": "De betaling gebeurde met een "
            "ander e-mailadres dan dat van uw Discord-account. "
            "Abonnementen werken alleen op het hieronder getoonde "
            "Discord-e-mailadres - abonneer daarmee opnieuw, of neem "
            "contact op met support.",
        "gate.head.expired": "Het abonnement van deze aanmelding is "
            "verlopen - verleng het op Stripe om door te gaan.",
        "gate.head.none": "U bent aangemeld, maar deze aanmelding "
            "heeft geen actief abonnement. Betaal met DIT "
            "Discord-e-mailadres - een koop op een ander adres kan "
            "het niet activeren.",
        "gate.head.past_due": "De laatste abonnementsbetaling is "
            "mislukt - maak haar in orde op Stripe om deze "
            "aanmelding weer in te schakelen.",
        "gate.head.refunded": "Deze aankoop is terugbetaald of "
            "teruggevorderd, daarom is de activatie ingetrokken. Een "
            "nieuw abonnement op dit Discord-e-mailadres activeert "
            "opnieuw.",
        "gate.head.shared": "Dit account draait NU op een ANDERE "
            "computer. Snappy AI blijft uit zolang hetzelfde "
            "Discord-account op twee plekken draait - sluit de "
            "andere sessie en controleer opnieuw. Abonnementen delen "
            "jaagt de prijs op; doe het alstublieft niet.",
        "gate.msg.active": "Abonnement actief - Snappy AI start...",
        "gate.msg.checking": "Controleren bij de server...",
        "gate.msg.no_link": "Die betaallink is in deze build niet "
            "geconfigureerd.",
        "gate.msg.open_fail": "Kon geen browser openen. Open deze "
            "link met de hand:\n%s",
        "gate.msg.open_ok": "Stripe is geopend in uw browser - betaal daar. Dit venster merkt de betaling zelf op en start de engine.",
        "gate.msg.session_gone": "Sessie weg - meld opnieuw aan.",
        "gate.msg.still_none": "Nog steeds geen actief abonnement "
            "voor deze aanmelding.",
        "gate.msg.still_shared": "Nog steeds in gebruik op een "
            "andere computer - sluit die sessie en controleer "
            "opnieuw.",
        "gate.msg.unreachable": "Authenticatieserver onbereikbaar: "
            "%s",
        "gate.note": "De motor start zodra het abonnement actief is "
            "- dit venster controleert zichzelf elke 30 seconden. "
            "Sluiten gaat terug naar aanmelden.",
        "gate.prices": "2 dagen proberen: 1,99€ (eenmalig)  -  "
            "abonnement: 9,99€ / maand.\nActivatie komt tot ~10 "
            "minuten na betaling; verlengingen activeren dezelfde "
            "aanmelding automatisch opnieuw.",
        "gate.title": "%s - Abonnement%s",
        "hdr.build": "build %s",
        "help.1.b": "Snappy AI kijkt naar het scherm rond uw cursor, "
            "vindt de stevige, elementvormige dingen dichtbij - "
            "knoppen, iconen, koppelingen - en kiest de beste: "
            "scherpe randen, een fatsoenlijke grootte en nabijheid "
            "bij de cursor winnen. Uw kleur, de nooit-klikbaar-lijst "
            "en het geheugen van uw laatste klik kunnen de keuze "
            "laten overhellen. De cursor mikt daarna op het midden "
            "van het element, niet op de hoek van zijn kader.",
        "help.1.t": "Wat er gebeurt als u klikt",
        "help.10.b": "1. Draait het? Gepauzeerd betekent dat niets "
            "wordt onderschept - «Sneltoets: assistentie starten» "
            "(standaard Ctrl+L) is de enige aan/uit.  2. Houd Shift "
            "vast bij één klik om te bevestigen dat de assistentie "
            "het probleem was.  3. Verkeerde element wint: verlaag "
            "«Zoekafstand vanaf de cursor», stel dan «Mijn kleur» in "
            "of verhoog «Kracht van het kleurvoordeel».  4. Niets "
            "wordt gevonden: verlaag «Hoe vaag een rand mag zijn» en "
            "«Minimale randscherpte», verhoog «Grootste breedte of "
            "hoogte» of «Nabije stukken aan elkaar plakken».  5. "
            "Iets mag nooit geassisteerd worden: zet zijn kleur in "
            "«Kleur(en) die nooit klikbaar zijn».  6. Nog steeds "
            "fout: vertel de ondersteuning wat u klikte en wat u "
            "verwachtte, en voeg het logbestand toe dat Snappy AI in "
            "zijn gegevensmap schrijft.",
        "help.10.t": "Als er iets misgaat, controleer in deze "
            "volgorde",
        "help.2.b": "De gidsmodus (standaard) eet geen enkele klik: "
            "uw klik bereikt het programma en na het lossen gaat de "
            "cursor naar het dichtstbijzijnde vrije element. De "
            "klassieke modus is sterker: een mis klik dicht bij een "
            "element wordt gevangen, de cursor vangt en Snappy AI "
            "klikt voor u. «Zoekafstand vanaf de cursor» bepaalt de "
            "zoekcirkel - verhoog als het gewenste element net "
            "buiten bereik zit, verlaag als de verkeerde buur wint. "
            "Shift ingehouden omzeilt één klik in beide modi.",
        "help.2.t": "Begin hier: modus en zoekafstand",
        "help.3.b": "Op het tabblad Verwerking beslissen «Hoe vaag "
            "een rand mag zijn» en «Minimale randscherpte» welke "
            "randen tellen: lager vindt vager, hoger negeert ruis. "
            "«Kleinste elementgrootte», «Grootste elementoppervlak» "
            "en «Grootste breedte of hoogte» gooien spetters en hele "
            "vensters weg. «Nabije stukken aan elkaar plakken» voegt "
            "een gebroken omtrek, of een icoon naast zijn label, "
            "samen tot één element. Op het tabblad Assistentie "
            "zorgen «Automatisch aanpassen aan matte schermen» en "
            "«Randen beoordelen op relatieve helderheid» ervoor dat "
            "donkere thema's zich gedragen als lichte - laat beide "
            "aan.",
        "help.3.t": "Niets wordt gevonden - of te veel",
        "help.4.b": "Op het tabblad Kleuren is «Mijn kleur» de "
            "voorkeurskleur en «Kleur(en) die nooit klikbaar zijn» "
            "absoluut: zulke elementen worden nooit geassisteerd. "
            "«Alleen mijn kleur assisteren» beperkt assistentie tot "
            "passende elementen. Bij Verwerking zegt «Strengheid van "
            "de kleurmatch» hoe dicht een tint moet liggen, laat "
            "«Vergelijkbare tinten accepteren» lichtere of "
            "verschoten versies deels meetellen, en zegt «Kracht van "
            "het kleurvoordeel» hoeveel uw kleur een element optilt "
            "- verhoog wanneer nog steeds de verkeerde wint.",
        "help.4.t": "Werken met kleuren",
        "help.5.b": "«Laatst aangeklikte element onthouden» blijft "
            "het element verkiezen waarop uw laatste geslaagde klik "
            "landde, gedurende «Hoe lang onthouden» seconden - dat "
            "maakt schuifbalken en dialoogknoppen prettig. «Kracht "
            "van het geheugen» zegt hoe sterk het wint, en «Wat het "
            "geheugen mag leren» beschermt het: met «Alleen "
            "elementen in mijn kleur» kan een mis klik het niet van "
            "koers laten veranderen. «Element volgen terwijl de knop "
            "ingehouden wordt» stabiliseert slepen, en de "
            "rechterknopacties op Experimenteel kunnen het geheugen "
            "met de muis volgen of wissen.",
        "help.5.t": "Herhaalde klikken op één bedieningselement",
        "help.6.b": "«Bewegende elementen voorlopen» meet hoe snel "
            "het gekozen element reist en mikt «Hoe ver vooruit "
            "mikken» milliseconden vooruit, zodat de klik op een "
            "scrollende lijst of videobalk landt in plaats van "
            "erachter. Het voorlopen heeft een plafond van 80 pixels "
            "en schakelt zichzelf uit bij stilstaande of draaiende "
            "elementen.",
        "help.6.t": "Klikken op bewegende dingen",
        "help.7.b": "«Cursorbeweging animeren» = 0 springt meteen; "
            "40-120 glijdt zodat u kunt kijken, en zelf de muis "
            "bewegen breekt het glijden af. «Dubbelklik-venster» "
            "maakt in klassieke modus van een tweede vang dicht bij "
            "dezelfde plek een dubbelklik. «Elke klik in een snelle "
            "reeks assisteren» assisteert elke klik van een reeks in "
            "plaats van alleen de eerste. «Pauze na een hapering» is "
            "het veiligheidsventiel dat een ingehouden klik "
            "teruggeeft als een scan hapert.",
        "help.7.t": "Hoe klikken voelen",
        "help.8.b": "Het tabblad Sneltoetsen legt de twee modi en "
            "het opnameverloop uit. Kort: sneltoetsen met Ctrl, Alt, "
            "Shift of Win zijn systeemwijd gereserveerd; losse "
            "toetsen vuren overal en typen nog steeds. Een macro "
            "maakt van één geblokkeerde toetsdruk een hele "
            "combinatie. Opnamen leggen uw echte invoer vast - elke "
            "toets, muisklik en cursorbeweging - en spelen die af "
            "vanaf het tabblad Macro's, elk met een eigen schakelaar "
            "voor eenmaal of herhalen tot stoppen.",
        "help.8.t": "Toetsen, macro's en opnamen",
        "help.9.b": "De knop Taal naast «Configuratie exporteren» - "
            "ook in de aanmeld- en abonnementvensters - schakelt de "
            "hele interface meteen om, zonder herstart, en onthoudt "
            "uw keuze. Talen die nog vertaald worden worden niet "
            "aangeboden, dus wat u kunt kiezen is volledig.",
        "help.9.t": "Taal",
        "help.sub": "Elke instelling met de naam die u op zijn "
            "tabblad ziet, in de volgorde waarin u ze nodig hebt. "
            "Beweeg over een naam voor de beschrijving van één "
            "regel; deze pagina is de lange vorm.",
        "help.tail": "Instellingen gelden zodra u op Toepassen "
            "drukt. Een config.ini naast het programma overschrijft "
            "config.json. Deze pagina legt uit; zij stelt niets in.",
        "help.title": "Snappy AI afstellen in gewone woorden",
        "kb.keys.b": "Een sneltoets met Ctrl, Alt, Shift of Win is "
            "systeembreed gereserveerd: alleen Snappy AI ziet hem. "
            "Een kale losse toets (zoals 1 of 2) werkt in elk "
            "programma EN typt gewoon door - de prijs is dat hem "
            "midden in een zin drukken ook de actie vuurt. Voor "
            "klassiek gedrag zet u «Sneltoetsen van één toets "
            "slikken de toets in» aan op het tabblad Assistentie. "
            "Macro's gaan verder: gestart wordt de triggertoets "
            "ingelijfd en de combinatie ernaast precies één keer "
            "verstuurd.",
        "kb.keys.t": "Losse toetsen tegenover combinaties",
        "kb.mode.b": "Gidsmodus (standaard, sneltoets 2): uw klik "
            "komt altijd onaangeroerd aan bij het programma; na het "
            "lossen gaat de cursor naar het dichtstbijzijnde vrije "
            "element, zodat uw volgende klik daar begint. Niets "
            "wordt ooit ingelijfd - de veiligste modus.  Klassieke "
            "modus (sneltoets 1): klikt u dicht bij een element, dan "
            "wordt die mis klik gevangen, de cursor vangt op het "
            "element en Snappy AI klikt voor u; is er niets "
            "dichtbij, dan krijgt u uw klik onaangetast terug.  In "
            "beide modi omzeilt Shift ingehouden tijdens het klikken "
            "de assistentie voor die ene klik.",
        "kb.mode.t": "Wat de twee modi doen",
        "kb.rec.b": "Druk terwijl gestart op uw opname-sneltoets "
            "(standaard Ctrl+Alt+R): elke toets die u indrukt, elke "
            "muisknop die u klikt en elke cursorbeweging wordt "
            "vastgelegd EN bereikt nog steeds uw programma's, dus u "
            "werkt gewoon door tijdens het opnemen. Druk op de "
            "stop-sneltoets (Ctrl+Alt+S) om de reeks in de lijst op "
            "het tabblad Macro's te bewaren - vijf opnamen passen "
            "erin. Klik op een opname om haar te kiezen, «Hernoemen» "
            "of «Exporteren» te gebruiken en haar eigen «Herhalen "
            "tot stoppen»-schakelaar te zetten. De afspeel-sneltoets "
            "(Ctrl+Alt+M) speelt de daar gekozen opname; Ctrl+1 tot "
            "Ctrl+5 spelen op positie in de lijst. Gepauzeerd wordt "
            "niets opgenomen en niets ingevoegd - uw invoer is "
            "helemaal van u.",
        "kb.rec.t": "Eigen toetsen en muisbewegingen opnemen en "
            "afspelen",
        "lang.close": "Sluiten",
        "lang.coverage": "%d%% vertaald",
        "lang.current": "Huidig: %s",
        "lang.progress": "Nog in vertaling, aangeboden zodra "
            "voltoooid: %s",
        "lang.prompt": "De wissel werkt meteen; het venster blijft "
            "open om er meerdere te proberen.",
        "lang.title": "Taal",
        "lbl.accent_boost": "Kracht van het kleurvoordeel",
        "lbl.accent_coherent": "Verspreide kleurspikkels negeren",
        "lbl.accent_color": "Mijn kleur(en)",
        "lbl.accent_matcher": "Motor voor kleurvergelijking",
        "lbl.accent_only": "Alleen mijn kleur assisteren",
        "lbl.accent_soft": "Vergelijkbare tinten accepteren",
        "lbl.accent_tolerance": "Strengheid van de kleurmatch",
        "lbl.accent_variants": "Lichte en donkere toestanden van "
            "mijn kleur",
        "lbl.adaptive_threshold": "Automatisch aanpassen aan matte "
            "schermen",
        "lbl.auto_click": "Klikt items zelf aan",
        "lbl.auto_click_interval": "Seconden tussen automatische "
            "klikken",
        "lbl.auto_click_max_clicks": "Limiet automatische klikken "
            "per sessie",
        "lbl.auto_click_min_contrast": "Hoe scherp een automatisch "
            "doel moet zijn",
        "lbl.auto_click_radius": "Zoeken vanaf het midden",
        "lbl.auto_click_repeat_px": "Niet op dezelfde plek opnieuw "
            "klikken",
        "lbl.auto_click_settle_ms": "Pauze voor een automatische "
            "klik",
        "lbl.block_bound_keys": "Sneltoetsen van één toets slikken "
            "de toets in",
        "lbl.capture_backend": "Schermafbeeldingsmotor",
        "lbl.color_adapt": "Aanpassen aan het schermlicht",
        "lbl.contrast_threshold": "Hoe vaag een rand mag zijn",
        "lbl.exclude_color": "Kleur(en) die nooit klikbaar zijn",
        "lbl.follow_boost": "Kracht van het geheugen",
        "lbl.follow_enabled": "Laatst aangeklikte element onthouden",
        "lbl.follow_learn": "Wat het geheugen mag leren",
        "lbl.follow_seconds": "Hoe lang onthouden",
        "lbl.glide_ms": "Cursorbeweging animeren",
        "lbl.hold_follow": "Element volgen terwijl de knop "
            "ingehouden wordt",
        "lbl.key_launch": "Sneltoets: assistentie starten",
        "lbl.key_mode1": "Sneltoets: klassieke modus (max 4 toetsen)",
        "lbl.key_mode2": "Sneltoets: gidsmodus (max 4 toetsen)",
        "lbl.key_pause": "Sneltoets: pauze",
        "lbl.key_play": "Sneltoets: gekozen opname afspelen",
        "lbl.key_play_n": "Sneltoets: opname #%d afspelen",
        "lbl.key_record": "Sneltoets: opname starten",
        "lbl.key_record_stop": "Sneltoets: opname stoppen en bewaren",
        "lbl.luminance_norm": "Randen beoordelen op relatieve "
            "helderheid",
        "lbl.macro_action": "Macro %d: stuurt in plaats daarvan",
        "lbl.macro_key": "Macro %d: druk deze toets",
        "lbl.max_area": "Grootste elementoppervlak",
        "lbl.max_dim": "Grootste breedte of hoogte",
        "lbl.merge_distance": "Nabije stukken aan elkaar plakken",
        "lbl.min_area": "Kleinste elementgrootte",
        "lbl.min_contrast": "Minimale randscherpte",
        "lbl.motion_3d": "Slimmer volgen bij beweging",
        "lbl.motion_lead_ms": "Hoe ver vooruit mikken",
        "lbl.motion_predict": "Bewegende elementen voorlopen",
        "lbl.watch_center_only": "Alleen het schermcentrum bewaken",
        "desc.watch_center_only": "De assistentie bekijkt alleen een vast vierkant in het midden van "
            "het scherm (grootte = zoekafstand, standaard 150×150 px), ongeacht "
            "waar de cursor staat. Klik buiten dat vierkant blijven "
            "onveranderd.",
        "lbl.center_follow": "Scherm volgt het doel",
        "desc.center_follow": "Met «Alleen het schermcentrum bewaken» aan: na het vergrendelen op "
            "een item beweegt de assistentie het scherm om het in het midden te "
            "houden, vooral bij scrollvlakken. Beweeg zelf het scherm om het "
            "volgen los te laten.",
        "lbl.input_backend": "Invoermethode",
        "desc.input_backend": "Windows-injectie (standaard) werkt overal. Interception verzendt "
            "via het stuurprogramma en spellen herkennen het als een echte "
            "muis; vereist het geïnstalleerde Interception-stuurprogramma en "
            "interception.dll naast het programma; anders wordt automatisch "
            "Windows-injectie gebruikt.",
        "val.input_backend.win32": "Windows-injectie",
        "val.input_backend.interception": "Interception (stuurprogramma)",
        "lbl.mouse2_action": "Extra actie van de rechterknop",
        "lbl.mouse2_hold_action": "Actie bij ingehouden rechterknop",
        "lbl.on_target_dist": "Afstand voor «al geraakt»",
        "lbl.radius": "Zoekafstand vanaf de cursor",
        "lbl.rapid_click_snap": "Elke klik in een snelle reeks "
            "assisteren",
        "lbl.snap_offset_x": "Klikpunt: naar links / rechts "
            "verschuiven",
        "lbl.snap_offset_y": "Klikpunt: omhoog / omlaag verschuiven",
        "lbl.stall_pause_seconds": "Pauze na een hapering",
        "lbl.watcher_seconds": "Dubbelklik-venster",
        "login.failed": "%s-aanmelding niet voltooid - probeer "
            "opnieuw.",
        "login.no_provider": "In deze kopie is geen "
            "aanmeldleverancier ingebouwd.",
        "login.not_configured": "Het abonnementsbestand is in deze "
            "build nog niet geconfigureerd.",
        "login.note": "Het aanmelden opent uw browser en komt "
            "vanzelf naar dit venster terug.",
        "login.provider": "Aanmelden met %s",
        "login.signedin": "Aangemeld als %s.",
        "login.sub": "Meld aan met Discord - uw abonnement is "
            "gekoppeld aan dit account, en betalingen moeten het "
            "e-mailadres ervan gebruiken. Hier is geen wachtwoord.",
        "login.title": "%s - Aanmelden",
        "login.unreachable": "Authenticatieserver onbereikbaar: %s",
        "login.waiting": "Wachten op de browser - rond de "
            "%s-aanmelding af...",
        "mac.delete": "Verwijderen",
        "mac.empty": "Nog geen opnamen - start, druk op uw "
            "opname-sneltoets en werk gewoon door: elke toets, klik "
            "en cursorbeweging wordt vastgelegd.",
        "mac.export": "Exporteren",
        "mac.import": "Importeren",
        "mac.keys_head": "Toetsmacro's",
        "mac.loop": "Herhalen tot stoppen",
        "mac.recordings": "Opnamen",
        "mac.rename": "Hernoemen",
        "mac.row": "Macro %d",
        "mac.sends": "stuurt",
        "mac.steps": "%d stappen",
        "note.advanced": "Afstand- en tijdinstellingen die "
            "veranderen hoe klikken voelen, niet wat gevonden wordt. "
            "De meeste mensen hoeven deze nooit aan te raken; de "
            "standaardwaarden zijn de geteste.",
        "note.assist": "Elke schakelaar die het gedrag tijdens het "
            "draaien verandert. De twee modi wisselt u met uw "
            "modustoetsen - het tabblad Sneltoetsen legt uit wat "
            "elke modus doet. Assistentie start altijd gepauzeerd; "
            "Starten is de enige aan/uit. Waar de motor kijkt en hoe "
            "klikken voelen staat bij Geavanceerd; wat als element "
            "telt bij Verwerking.",
        "note.colors": "De twee lijsten bovenaan kiezen welke "
            "kleuren Snappy AI verkiest of weigert. Elke toont zijn "
            "kleuren als vakjes rechts, vijftien hoogstens, en een "
            "klik op een vakje haalt die kleur er weer uit; een lege "
            "lijst toont een doorgekruist vak en telt als uit. «Als "
            "voorkeur toevoegen» en «Als geweigerde toevoegen» "
            "zetten de kleur die in de menger staat in de "
            "bijpassende lijst. Huidige RGB-waarde toont drie vakjes "
            "- elk zo breed als vijf kleurvakjes, zodat de rij "
            "dezelfde vijftien vakjes overspant als alles eronder - "
            "die glimmen met hoeveel rood, groen en blauw de kleur "
            "in de menger heeft; de rij volgt de menger en kan niet "
            "getypt worden. De menger eronder mengt een kleur als "
            "een tekenprogramma; alles ernaast zit aan de "
            "rechterkant van het venster, met dezelfde afstand tot "
            "de rand als de instellingen boven, en elke rij "
            "overspant dezelfde vijftien vakjes breedte: de hoge "
            "etalage met zijn #waarde erin getekend, dan de vijftien "
            "kant-en-klare tinten, de twee toevoegknoppen en de "
            "schermrij - «Kleur van scherm oppakken» pakt de ene "
            "kleur onder de cursor, «Schermkleuren voorstellen» vult "
            "vijftien eigen vakjes met kleuren die hij rond de "
            "cursor vindt, en een klik op een ervan laadt die in de "
            "menger. De etalage is met opzet hoog: zo eindigen de "
            "voorgestelde vakjes precies gelijk met de kleurschuif "
            "links.",
        "note.experimental": "Motorkeuzes, elk met een geteste "
            "standaard. Wijzig ze alleen om motoren te vergelijken, "
            "op ongewone hardware, of als ondersteuning erom vraagt "
            "- de capturermotor geldt na herstart.",
        "note.handler": "Wat als klikbaar element telt: hoe vaag een "
            "rand mag zijn, hoe scherp hij moet zijn, en hoe groot "
            "of klein een element mag zijn. Niets gevonden? Ruim "
            "deze waarden op. Verkeerde gevonden? Verscherpen, of "
            "gebruik uw kleur op het tabblad Kleuren.",
        "note.keybindings": "Elke sneltoets - en eronder wat de twee "
            "modi doen, hoe u eigen toetsen en muisbewegingen "
            "opneemt, en waarin een losse toets verschilt van een "
            "combinatie.",
        "note.macros": "Een macro maakt van één toetsdruk een hele "
            "combinatie terwijl gestart. Naast de macro's uw "
            "opnamen: tot vijf benoemde vastleggingen van alles wat "
            "u deed - elke toets, muisklik en cursorbeweging - die "
            "precies afspelen zoals opgenomen. Klik op een opname om "
            "haar te kiezen; elke regel draagt haar eigen «Herhalen "
            "tot stoppen»-schakelaar, en «Hernoemen», «Exporteren», "
            "«Importeren» en «Verwijderen» staan onder in het vak.",
        "note.macros_keys": "Opname-/afspeelsneltoetsen staan op het "
            "tabblad Sneltoetsen (standaard: Ctrl+Alt+R opnemen, "
            "Ctrl+Alt+S stoppen en bewaren, Ctrl+Alt+M afspelen, "
            "Ctrl+1..5 afspelen op positie).",
        "online.cancelled": "De Discord-authenticatie is geannuleerd "
            "(of mislukt). Probeer opnieuw.",
        "rec.export_fail": "Export mislukt: %r",
        "rec.exported": "Geëxporteerd naar %s",
        "rec.import_fail": "Import mislukt: %r",
        "rec.imported": "%d opname(n) geïmporteerd%s.",
        "rec.imported_none": " (geen was geldig)",
        "rec.no_sel": "Niets gekozen om te exporteren.",
        "rec.notfile": "Import mislukt: geen opnamebestand.",
        "shared.back": "Welkom terug - druk op Starten zodra u klaar "
            "bent.",
        "shared.body": "Dit Discord-account draait Snappy AI nu op "
            "een andere computer.\nAssistentie pauzeert hier tot er "
            "nog één sessie over is.\n\nEén abonnement, één machine "
            "tegelijk - dat houdt\nde prijs laag en de ontwikkeling "
            "gaande.",
        "shared.close": "Sluiten",
        "shared.recheck": "Nu opnieuw controleren",
        "shared.still": "Nog steeds elders in gebruik - we blijven "
            "gepauzeerd.",
        "shared.title": "Account elders in gebruik",
        "shared.unreachable": "Server onbereikbaar - we controleren "
            "opnieuw.",
        "st.all_files": "Alle bestanden",
        "st.color_added": "rgb(%d, %d, %d) toegevoegd aan %s - "
            "Toepassen bewaart.",
        "st.color_already": "rgb(%d, %d, %d) staat al in %s.",
        "st.color_full": "%s bevat al 15 kleuren - klik eerst op een "
            "van de vakjes om een kleur te verwijderen.",
        "st.color_removed": "rgb(%d, %d, %d) verwijderd uit %s - "
            "Toepassen bewaart.",
        "st.delete_confirm": "Opname %r verwijderen?\nDit kan niet "
            "worden teruggedraaid.",
        "st.deleted": "Opname verwijderd.",
        "st.engine_dead": "Motor-thread niet beschikbaar - "
            "sneltoetsen reageren niet.",
        "st.ent_paused": "Abonnement %s - assistentie gepauzeerd. "
            "Verleng op Stripe en start opnieuw.",
        "st.ent_unreachable": "Abonnementscontrole: server "
            "onbereikbaar (sessie blijft lopen).",
        "st.export_fail": "Export mislukt: %r",
        "st.export_rec_title": "Opname exporteren",
        "st.export_title": "Instellingen exporteren",
        "st.exported": "Instellingen geëxporteerd naar %s",
        "st.file_rec": "Snappy AI-opname",
        "st.file_settings": "Snappy AI-instellingen",
        "st.follow": "  |  volgen %d s geleden",
        "st.import_fail": "Import mislukt: %r",
        "st.import_notfile": "Import mislukt: geen "
            "instellingenbestand.",
        "st.import_rec_title": "Opname(n) importeren",
        "st.import_title": "Instellingen importeren",
        "st.imported": "%d instelling(en) geïmporteerd%s.",
        "st.imported_ignored": ", genegeerd: %s",
        "st.ini_over": "Toegepast, maar config.ini overschrijft: %s",
        "st.lib_empty": "De lijst is leeg - niets om te exporteren.",
        "st.line": "Geassisteerd %d  |  door gelaten %d%s  |  thema: "
            "%s",
        "st.loop_desc": "Afspeelstijl van DEZE opname: uit = eenmaal "
            "afspelen; aan = herhalen tot u de afspeel-sneltoets "
            "opnieuw drukt. Elke opname heeft haar eigen schakelaar, "
            "bewaard met de opname zelf.",
        "st.name_empty": "De naam mag niet leeg zijn.",
        "st.pick_err": "Opnemen mislukt: %r",
        "st.pick_fail": "Opnemen mislukt - probeer opnieuw.",
        "st.pick_ok": "rgb(%d, %d, %d) genomen op (%d, %d).",
        "st.pick_wait": "Zet de cursor op de kleur - opnemen over 3 "
            "s...",
        "st.preset_desc": "Kant-en-klare tint: %s - klik om in de "
            "menger te laden.",
        "st.rec_count": "%d van 5 opnamen",
        "st.rec_now": "%r nu: %s.",
        "st.rec_once": "speelt eenmaal",
        "st.rec_playing": "%r spelen...",
        "st.rec_playing_loop": "%r spelen tot stoppen",
        "st.rec_recording": "OPNEME - %s stopt en bewaart",
        "st.rec_repeats": "herhaalt tot stoppen",
        "st.registered": "Geregistreerd op: %s    Status: %s",
        "st.rename_prompt": "Nieuwe naam voor opname #%d:",
        "st.renamed": "Opname hernoemd.",
        "st.reset_confirm": "Alle instellingen terugzetten op "
            "standaard?\nAccounts blijven bewaard; dit raakt alleen "
            "instellingen.",
        "st.rgb_bad": "Voer eerst geldige R/G/B-waarden in.",
        "st.running": "Actief..",
        "st.saved": "Bewaard en toegepast.",
        "st.defaults_restored": "Standaardinstellingen hersteld.",
        "st.saved_bad": "Bewaard, maar ongeldig (oude blijft): %s",
        "st.select_rec": "Kies eerst een opname.",
        "st.shared_paused": "ACCOUNT ELDERS IN GEBRUIK - assistentie "
            "gepauzeerd; één abonnement = één machine.",
        "st.standby": "Stand-by..",
        "st.sug_fail": "Voorstel mislukt: %r",
        "st.sug_loaded": "Suggestie rgb(%d, %d, %d) staat in de "
            "menger - voeg hem met de knoppen hierboven aan een "
            "lijst toe.",
        "st.sug_loaded_desc": "Voorgestelde interfacekleur rgb(%d, "
            "%d, %d) - %d%% van het bemonsterde gebied. Klik om in "
            "de menger te laden.",
        "st.sug_none": "Geen kleurvoorstellen uit dit gebied.",
        "st.sug_ok": "%d suggesties - klik er een om die in de "
            "menger te laden.",
        "st.sug_wait": "Wijs naar de app waarin u werkt - "
            "bemonsteren over 3 s...",
        "tab.advanced": "Geavanceerd",
        "tab.assist": "Assistentie",
        "tab.colors": "Kleuren",
        "tab.experimental": "Experimenteel",
        "tab.handler": "Verwerking",
        "tab.help": "Help",
        "tab.hotkeys": "Sneltoetsen",
        "tab.macros": "Macro's",
        "theme.dark": "Donker",
        "theme.light": "Licht",
        "val.accent_matcher.hsv": "Klassiek - de oude motor",
        "val.accent_matcher.oklab": "Perceptueel - hoe kleuren "
            "eruitzien (aanbevolen)",
        "val.capture_backend.auto": "Automatisch - snelste met "
            "veilige terugval",
        "val.capture_backend.dxcam": "Desktop Duplication - snelste "
            "op de meeste pc's",
        "val.capture_backend.mss": "Compatibel - werkt altijd "
            "(Remote Desktop, VM's)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "experimenteel",
        "val.follow_learn.accent": "Alleen elementen in mijn kleur",
        "val.follow_learn.any": "Elke geslaagde vang",
        "val.mouse2_action.1": "Huidige volgtaak wissen",
        "val.mouse2_action.2": "De laatst geknapte kleur volgen",
        "val.mouse2_action.3": "Kleur onder de cursor nemen en dan "
            "volgen",
        "val.mouse2_action.4": "Niets doen",
        "val.mouse2_hold_action.1": "Huidige volgtaak wissen",
        "val.mouse2_hold_action.2": "De laatst geknapte kleur volgen",
        "val.mouse2_hold_action.3": "Kleur onder de cursor nemen en "
            "dan volgen",
        "val.mouse2_hold_action.4": "Niets doen",
        "word.off": "Uit",
        "word.on": "Aan",
    },
    "tr": {
        "btn.apply": "Uygula",
        "btn.export": "Yapılandırmayı dışa aktar",
        "btn.import": "Yapılandırmayı içe aktar",
        "btn.language": "Dil: %s",
        "btn.launch": "Başlat",
        "btn.logout": "Çıkış yap",
        "btn.pause": "Duraklat",
        "btn.restore": "Varsayılanları geri yükle",
        "col.accent": "Vurgu",
        "col.add_pref": "Tercih edilen renklere ekle",
        "col.add_ref": "Reddedilen renklere ekle",
        "col.chip_desc": "rgb(%d, %d, %d), %s içinde - bu rengi "
            "kaldırmak için kutuya tıklayın.",
        "col.chip_off": "%s hiç renk tutmuyor - üstü çizili kutu "
            "kapalı demek. Aşağıdan bir renk seçin ve ilgili ekleme "
            "düğmesine basın.",
        "col.exclude": "Hariç",
        "col.pick": "Ekrandan renk al",
        "col.rgb.desc": "Üç kutu, şu an karıştırıcıda duran rengi "
            "gösterir: ilki içerdiği kırmızı kadar, ikincisi yeşil, "
            "üçüncüsü mavi kadar parlar - daha parlak, daha çok "
            "demektir. Satır karıştırıcıyı, hazır tonları ve ekran "
            "düğmelerini izler; yazılamaz.",
        "col.rgb.name": "Geçerli RGB değeri",
        "col.suggest": "Ekrandan renkler öner",
        "desc.accent_boost": "Renginizin bir öğenin puanını ne kadar "
            "yükselttiği (0-3). Yanlış öğe kazanmaya devam ederse "
            "1,5-2'ye çıkarın.",
        "desc.accent_coherent": "Renginizin sayılması için "
            "bağlantılı bir leke oluşturması gerekir - dağınık "
            "titreme ya da sıkıştırma benekleri öğeyi niteleyemez, "
            "güçlendiremez ya da asla-tıklanamaz listeye koyamaz.",
        "desc.accent_color": "Snappy AI'ın tercih etmesi gereken "
            "renk, sağda renk kutuları olarak gösterilir. Aşağıdan "
            "bir renk seçin ve eklemek için «Tercih edilen renklere "
            "ekle»ye basın - en fazla on beş kutu; bir kutuya "
            "tıklamak o rengi yeniden kaldırır. Bunlardan birini "
            "içeren öğeler beraberliği kazanır. Boş liste üstü "
            "çizili bir kutu gösterir ve ayarı kapatır.",
        "desc.accent_matcher": "Renklerin nasıl karşılaştırıldığı. "
            "Algısal, renklerin gerçekte nasıl göründüğüne göre "
            "sıralar ve önerilir; Klasik, karşılaştırma için tutulan "
            "eski motordur.",
        "desc.accent_only": "Yalnızca renginizi içeren öğelere "
            "yardım edilebilir; başka yerdeki tıklamalar "
            "dokunulmadan Windows'a geçer.",
        "desc.accent_soft": "0-100: renginizin daha açık, koyu veya "
            "soluk sürümlerinin ne ölçüde sayılacağı. 0 = yalnız "
            "kesin tonlar.",
        "desc.accent_tolerance": "Bir rengin sizinki sayılması için "
            "ne kadar yakın olması gerektiği (4-90). Daha düşük = "
            "daha katı.",
        "desc.accent_variants": "Renginizin daha açık ve koyu "
            "kopyaları da sayılır, üzerine gelme, basma ve soluk "
            "haller renk toleransı genişlemeden geçerli olur. "
            "Yalnızca parlaklık - yanlış renk tonu asla geçemez.",
        "desc.adaptive_threshold": "Koyu temalar ve soluk belgeler "
            "kendi algılama çıtalarını kendileri indirir, böylece "
            "soluk öğeler de bulunur. Açık önerilir.",
        "desc.auto_click": "Açıkken program, gözlenen bölgedeki en iyi öğeye her 0,1 saniyede "
            "kendiliğinden tıklar; öncelik kontrasttır. Vurgu rengi ayarlıysa "
            "yalnız renkli öğeler adaydır; renk yoksa sadece çok keskin "
            "çizilmiş öğelere tıklanır. Aynı yere iki kez ve kendi "
            "pencerelerine asla.",
        "desc.auto_click_interval": "Ekran renginiz için ne sıklıkla "
            "denetlenir (0,5-60). Yavaş sayı güvenlidir: 2-5, "
            "izlediğiniz bir pencereye uyar.",
        "desc.auto_click_max_clicks": "Başlatmadan sonra kendi "
            "başına kaç kez tıklayabilir (1-200). Sınıra ulaşınca "
            "durur ve söyler, yanlış ayar kaçamaz.",
        "desc.auto_click_min_contrast": "»En düşük kenar netliği« "
            "ile aynı ölçekte. Varsayılanla başlayın, yanlış "
            "tıklıyorsa yükseltin: yalnızca güçlü, net öğeler "
            "sayılır.",
        "desc.auto_click_radius": "Otomatik tıklama ekranın ortası "
            "çevresinde arar (40-600 px). Kalabalık pencereye geniş; "
            "yalnızca ortadaki tek denetimi görsün diye dar.",
        "desc.auto_click_repeat_px": "Otomatik tıklamadan sonra bu "
            "kadar piksel içindeki hedef rahat bırakılır (0-400). "
            "Olmasa ekranda duran düğme tekrar tekrar tıklanırdı.",
        "desc.auto_click_settle_ms": "İmleç tıklamadan önce hedefte "
            "böyle dinlenir (0-2000 ms), program vurguyu önce "
            "görsün. 120 çoğu pencereye uyar.",
        "desc.block_bound_keys": "Kapalı (varsayılan): "
            "Ctrl/Alt/Shift olmayan bir kısayol - 1 veya V gibi - "
            "her programda çalışır VE normal yazmaya devam eder, "
            "yani cümle ortasında basmak eylemini de tetikler. Açık: "
            "eylem yine her yerde tetiklenir, ama tuş artık yazmaz.",
        "desc.capture_backend": "Ekranın nasıl fotoğraflandığı. "
            "Otomatik, neredeyse tüm pencereleri gören uyumlu yöntemi kullanır; Uyumlu, Uzak "
            "Masaüstü ve sanal makineler dahil her zaman çalışır. "
            "Yeniden başlatmadan sonra geçerli.",
        "desc.color_adapt": "Her öğe karşılaştırmadan önce kendi "
            "arka planına göre beyaz dengelenir, gece ışığı ve tema "
            "renkleri renginizi tolerans dışına itemez. Yalnızca "
            "uyarlanmamış karşılaştırıcıyla kıyas için kapatın.",
        "desc.contrast_threshold": "Daha düşük, daha soluk öğeleri "
            "bulur (ve daha çok gürültü); daha yüksek daha net "
            "kenarlar ister.",
        "desc.default": "Bir ayarın ne yaptığını görmek için imleci "
            "adının üzerine getirin.",
        "desc.exclude_color": "Bu renkleri içeren öğelere asla "
            "yardım edilmez: üzerlerindeki tıklamalar her iki modda "
            "da doğrudan Windows'a gider. Sağda renk kutuları olarak "
            "gösterilir - aşağıdan bir renk seçin ve bir tane "
            "eklemek için «Reddedilen renklere ekle»ye basın (en "
            "fazla on beş); bir kutuya tıklamak onu kaldırır. Boş "
            "liste üstü çizili bir kutu gösterir ve ayarı kapatır.",
        "desc.follow_boost": "Hatırlanan öğenin beraberelikleri ne "
            "güçlü kazandığı: 100% tazeyken puanını katlayabilir, "
            "25% hafif bir itkidir.",
        "desc.follow_enabled": "Başarılı bir yapışmadan sonra benzer "
            "görünen veya aynı yerdeki öğeler bir süre kazanır - "
            "kaydırma çubukları ve bir denetimde yinelenen "
            "tıklamalar için kullanışlı.",
        "desc.follow_learn": "Yalnızca benim rengimdeki öğeler: ıska "
            "bir tıklama hatırayı başka yöne çeviremez. Her başarılı "
            "yapışma: eski, güvenen davranış.",
        "desc.follow_seconds": "Son başarılı yapışmadan sonra "
            "hatırlanan öğenin tercih edilir kaldığı saniye (1-120).",
        "desc.glide_ms": "0 (varsayılan) anında atlar - en hızlısı. "
            "40-120 izleyebilmeniz için kayar; fareyi kendiniz "
            "oynatmak kaymayı iptal eder.",
        "desc.hold_follow": "Bir yapışmanın hemen ardından sol "
            "düğmeyi basılı tuttuğunuzda - veya hatırlanan öğenin "
            "üzerine yeniden bastığınızda - imleç o öğenin renginde "
            "kalır; bu, kaydırma çubuğu tutamaçları gibi "
            "sürüklemeleri sabitleştirir. Başka yerdeki basışlara "
            "hiç dokunulmaz.",
        "desc.key_launch": "Biçim: ctrl+l, f5, space, ctrl+alt+1 ... "
            "Değiştiriciler: ctrl, alt, shift, win. Uygula'dan sonra "
            "geçerli.",
        "desc.key_mode1": "Virgülle ayrılmış, örn '1, f1, ctrl+f1, "
            "v'. Klasik modun ne yaptığını Kısayollar sekmesi "
            "açıklar.",
        "desc.key_mode2": "Virgülle ayrılmış, örn '2, f2, ctrl+f2, "
            "b'. Kılavuz modun ne yaptığını Kısayollar sekmesi "
            "açıklar.",
        "desc.key_pause": "Başlatana dek fare ve klavye yeniden "
            "tamamen sizin.",
        "desc.key_play": "Makrolar listesinde seçili kaydı oynatır; "
            "seçim yoksa en yenisini. Tekrarlayan bir kayıtta onu "
            "durdurur.",
        "desc.key_play_n": "Makrolar sekmesindeki numaralı listeden "
            "#%d kaydını konumuna göre oynatır. Liste daha kısaysa "
            "hiçbir şey olmaz.",
        "desc.key_record": "Yaptığınız her şeyi - her tuşu, her fare "
            "tıklamasını ve her imleç hareketini - yakalar; "
            "girişiniz durdur kısayolu onu Makrolar listesine "
            "kaydedene dek programlarınıza ulaşmaya devam eder. "
            "Yalnız çalışırken kurulu.",
        "desc.key_record_stop": "Yakalamayı durdurur, diziyi "
            "Makrolar listesine kaydeder ve süren bir oynatmayı "
            "durdurur.",
        "desc.luminance_norm": "Kenarlar çevrelerinin parlaklığına "
            "göre puanlanır, böylece koyu temalar açıklar gibi "
            "davranır. Açık önerilir.",
        "desc.macro_action": "Her tetik basışında sizin için basılan "
            "kombinasyon (bir basış = bir kombinasyon): 'ctrl+c', "
            "'ctrl+shift+s', 'space', 'f5' ... Boş = makro kapalı.",
        "desc.macro_key": "Yazmak yerine makroyu ANLAMINA gelen tuş: "
            "'b', 'f7', 'ctrl+b' ... Çalışırken bir basış yandaki "
            "kombinasyonu tam bir kez gönderir ve tuşun kendisi "
            "programlarınıza ulaşmaz. Duraklatıldığında normal "
            "yazar. Boş = makro kapalı.",
        "desc.max_area": "Daha büyük lekeler yoksayılır - genellikle "
            "tüm pencereler veya duvar kâğıdı, tıklanabilir öğeler "
            "değil.",
        "desc.max_dim": "Bundan daha geniş veya yüksek öğeler "
            "yoksayılır; kaydırma çubukları gibi ekran kenarına "
            "değenler iki katını alır.",
        "desc.merge_distance": "Bundan daha yakın parçalar (kırık "
            "bir kontur, etiketinin yanındaki simge) tek öğe olur. "
            "İki eksiksiz öğe asla yapıştırılmaz.",
        "desc.min_area": "Daha küçük lekeler, daha büyük bir öğeye "
            "yapışmadıkça zerre olarak yoksayılır.",
        "desc.min_contrast": "Bir öğenin hiç tıklanabilir olması "
            "için en az bu kadar net olması gerekir. 28 altındaki "
            "değerler 28 sayılır: yerleşik kalite eşiği gürültünün "
            "tıklanabilir olmasını engeller.",
        "desc.motion_3d": "Hareketli öğeleri doğru çizgi uydurma "
            "yerine konum VE boy ile izler: tekil kötü taramalar "
            "izleyiciyi kör etmek yerine yoksayılır, virajlar "
            "izlenir, ani boy sıçraması izi yeniden başlatır "
            "(tarayıcı başka öğe yakaladı). Aynı hız eşikleri, aynı "
            "80 px sınırı - yalnız akıl değişir. Tek başına çalışır.",
        "desc.motion_lead_ms": "Hareketli bir öğeyi önden nişanlamak "
            "için milisaniye (0-300): yavaş kaydırma için 40-80, "
            "hızlı çubuklar için 100-150. Üst sınır 80 px, yavaş "
            "veya dönen harekette kapalı.",
        "desc.motion_predict": "Tıklarken hareket eden öğeler için "
            "(kayan listeler, video çubukları) tıkın öğenin üzerine "
            "düşmesi için biraz önden nişan alır. Duran öğeler "
            "değişmez.",
        "desc.mouse2_action": "Kısa bir sağ tıkın EKSTRA yaptığı - "
            "sağ tıkın kendisi her zaman normal Windows işlevini "
            "korur. Varsayılan: hiçbir şey.",
        "desc.mouse2_hold_action": "Aynı seçenekler, tıklamak yerine "
            "sağ düğmeyi yaklaşık yarım saniye BASILI tuttuğunuzda "
            "tetiklenir. Bir basış ya tıklamadır ya basılı tutma, "
            "asla ikisi birden. Varsayılan: hiçbir şey.",
        "desc.on_target_dist": "Tıklamanız öğenin merkezinden bu "
            "piksel içinde düşerse hiçbir şey kımıldamaz - isabet "
            "ettiniz.",
        "desc.radius": "Piksel cinsinden arama uzaklığı (40-400). "
            "İstediğiniz öğe hemen erişimin dışındaysa yükseltin; "
            "yanlış komşu kazanıyorsa düşürün.",
        "desc.rapid_click_snap": "Kapalı (varsayılan): bir tıklama "
            "işlenirken diğerleri Windows'a gider. Açık: her sol "
            "tıklamaya yardım edilir.",
        "desc.snap_offset_x": "Tıklama noktasını öğenin ortasından "
            "yana kaydırır (-200 ile 200, negatif sola). Ortası ölü "
            "denetim için - bölünmüş düğme, kaydırma çubuğu - her "
            "snapte boğuşmak yerine tıklamayı bir kez canlı noktaya "
            "ayarlayın.",
        "desc.snap_offset_y": "Tıklama noktasını öğenin ortasından "
            "dikey kaydırır (-200 ile 200, negatif yukarı). Yanal "
            "kaydırma gibi: denetimin canlı kısmına inin.",
        "desc.stall_pause_seconds": "Bir tarama bir gün takılırsa, "
            "yardım bu süre duraksar ve basılı tutulan her tıklama "
            "size iade edilir.",
        "desc.watcher_seconds": "Klasik modda, aynı yere yakın "
            "ikinci bir yapışma bu süre içinde olursa öğeye çift "
            "tıklama olur.",
        "ent.cancel_line": "%s tarihine dek etkin - YENİLENMEYECEK",
        "ent.canceled_line": "abonelik sona erdi%s",
        "ent.expired_line": "%s tarihinde doldu - Stripe'ta "
            "yenileyin",
        "ent.past_due_line": "ödeme başarısız - kartı Stripe makbuz "
            "e-postasında düzeltin; fatura ödenince erişim geri "
            "gelir",
        "ent.plan": " (%s)",
        "ent.refunded_line": "iade edildi / ters ibraz - "
            "etkinleştirme geri alındı",
        "ent.st.active": "etkin",
        "ent.st.canceled": "sona erdi",
        "ent.st.canceling": "etkin ama iptal ediliyor",
        "ent.st.grant": "destek bağışı",
        "ent.st.past_due": "ÖDEME BAŞARISIZ",
        "ent.st.refunded": "iade edildi / ters ibraz",
        "ent.st.trial": "deneme",
        "ent.st.unsubscribed": "abonelik yok",
        "ent.until": " %s tarihine dek",
        "err.auth_unreachable": "Snappy AI kimlik doğrulama "
            "sunucusuna ulaşılamıyor:\n%s\n\nSnappy AI yalnızca "
            "ondan canlı bir yanıtla çalışır.\nYeniden dene?",
        "err.start_fail": "Snappy AI başlatılamadı.\nAyrıntılar için "
            "--console ile çalıştırın.",
        "gate.btn.monthly": "9,99€ karşılığı aylık abonelik",
        "gate.btn.trial": "1,99€ karşılığı deneme satın alımı",
        "gate.head.canceled": "Bu abonelik iptal edildi - devam "
            "etmek için Stripe'ta yenisini başlatın.",
        "gate.head.canceling": "Aboneliğiniz iptale ayarlı - %s "
            "tarihine dek etkin, sonra yenilemezseniz bu giriş "
            "yeniden kilitlenir.",
        "gate.head.email_mismatch": "Ödeme, Discord hesabınızdan "
            "farklı bir e-posta ile yapıldı. Abonelikler yalnız "
            "aşağıda gösterilen Discord e-postasında çalışır - "
            "onunla yeniden abone olun veya destekle iletişime "
            "geçin.",
        "gate.head.expired": "Bu girişin aboneliğinin süresi doldu - "
            "devam etmek için Stripe'ta yenileyin.",
        "gate.head.none": "Giriş yaptınız, ama bu girişin etkin bir "
            "aboneliği yok. BU Discord e-postası ile ödeyin - başka "
            "bir adresteki satın alım onu etkinleştiremez.",
        "gate.head.past_due": "Son abonelik ödemesi başarısız - bu "
            "girişi yeniden etkinleştirmek için Stripe'ta düzeltin.",
        "gate.head.refunded": "Bu satın alım iade edildi veya ters "
            "ibraz edildi, bu yüzden etkinleştirme geri alındı. Bu "
            "Discord e-postasında yeni bir abonelik yeniden "
            "etkinleştirir.",
        "gate.head.shared": "Bu hesap ŞU AN BAŞKA bir bilgisayarda "
            "kullanılıyor. Aynı Discord hesabı iki yerde çalıştığı "
            "sürece Snappy AI kapalı kalır - diğer oturumu kapatıp "
            "yeniden denetleyin. Abonelikleri paylaşmak fiyatları "
            "yükseltir; lütfen yapmayın.",
        "gate.msg.active": "Abonelik etkin - Snappy AI "
            "başlatılıyor...",
        "gate.msg.checking": "Sunucuya denetleniyor...",
        "gate.msg.no_link": "Bu ödeme bağlantısı bu derlemede "
            "yapılandırılmamış.",
        "gate.msg.open_fail": "Tarayıcı açılamadı. Bu bağlantıyı "
            "elle açın:\n%s",
        "gate.msg.open_ok": "Stripe tarayıcınızda açık - orada ödeyin. Bu pencere ödemeyi kendiliğinden fark eder ve motoru başlatır.",
        "gate.msg.session_gone": "Oturum kayboldu - yeniden giriş "
            "yapın.",
        "gate.msg.still_none": "Bu giriş için hâlâ etkin abonelik "
            "yok.",
        "gate.msg.still_shared": "Hâlâ başka bir bilgisayarda "
            "kullanımda - o oturumu kapatıp yeniden denetleyin.",
        "gate.msg.unreachable": "Kimlik doğrulama sunucusuna "
            "ulaşılamıyor: %s",
        "gate.note": "Abonelik etkin olur olmaz motor başlar - bu "
            "pencere 30 saniyede bir kendini denetler. Kapatmak "
            "girişe döndürür.",
        "gate.prices": "2 günlük deneme: 1,99€ (tek sefer)  -  "
            "abonelik: 9,99€ / ay.\nEtkinleştirme ödemeden sonra en "
            "çok ~10 dakikada gelir; yenilemeler aynı girişi "
            "otomatik olarak yeniden etkinleştirir.",
        "gate.title": "%s - Abonelik%s",
        "hdr.build": "derleme %s",
        "help.1.b": "Snappy AI imlecinizin çevresindeki ekrana "
            "bakar, yakındaki sağlam, öğe biçimli şeyleri bulur - "
            "düğmeler, simgeler, bağlantılar - ve en iyisini seçer: "
            "net kenarlar, makul boyut ve imlece yakınlık kazanır. "
            "Renginiz, asla-tıklanmaz listesi ve son tıklamanızın "
            "hatırası seçimi eğebilir. İmleç sonra öğenin ortasına "
            "nişan alır, kutusunun köşesine değil.",
        "help.1.t": "Tıkladığınızda ne olur",
        "help.10.b": "1. Başlatıldı mı? Duraklatılmışken hiçbir şey "
            "yakalanmaz - «Kısayol: yardımı başlat» (varsayılan "
            "Ctrl+L) tek açma/kapamadır.  2. Sorunun yardım olduğunu "
            "doğrulamak için bir tıklamada Shift'i basılı tutun.  3. "
            "Yanlış öğe kazanıyor: «İmleçten arama uzaklığı»nı "
            "düşürün, sonra «Benim rengim»i ayarlayın veya «Renk "
            "avantajının gücü»nü yükseltin.  4. Hiçbir şey "
            "bulunmuyor: «Bir kenar ne kadar soluk olabilir» ve «En "
            "düşük kenar netliği»ni düşürün, «En büyük genişlik veya "
            "yükseklik» ya da «Yakın parçaları yapıştır»ı yükseltin. "
            " 5. Bir şeye asla yardım edilmemeli: rengini tıklanamaz "
            "renk(ler)»e koyun.  6. Hâlâ yanlış: neye tıkladığınızı "
            "ve ne beklediğinizi desteğe bildirin ve Snappy AI'nin "
            "veri klasörüne yazdığı günlük dosyasını ekleyin.",
        "help.10.t": "Bir şey ters giderse bu sırayla denetleyin",
        "help.2.b": "Kılavuz mod (varsayılan) hiçbir tıklamayı "
            "yemez: tıklamanız programa ulaşır ve bırakınca imleç en "
            "yakın temiz öğeye gider. Klasik mod daha güçlüdür: bir "
            "öğenin yakınındaki ıskalanmış tıklama yakalanır, imleç "
            "yapışır ve Snappy AI sizin için tıklar. «İmleçten arama "
            "uzaklığı» arama çemberini belirler - istediğiniz öğe "
            "hemen erişimin dışındaysa yükseltin, yanlış komşu "
            "kazanıyorsa düşürün. Shift'i basılı tutmak her iki "
            "modda bir tıklamayı atlar.",
        "help.2.t": "Buradan başlayın: mod ve arama uzaklığı",
        "help.3.b": "İşleme sekmesinde «Bir kenar ne kadar soluk "
            "olabilir» ve «En düşük kenar netliği» hangi kenarların "
            "sayılacağını belirler: daha düşük daha solukları bulur, "
            "daha yüksek gürültüyü yok sayar. «En küçük öğe boyutu», "
            "«En büyük öğe alanı» ve «En büyük genişlik veya "
            "yükseklik» zerreleri ve tüm pencereleri eler. «Yakın "
            "parçaları yapıştır» kırık bir konturu veya etiketinin "
            "yanındaki bir simgeyi tek öğede birleştirir. Yardım "
            "sekmesinde «Soluk ekranlara otomatik uyum» ve "
            "«Kenarları göreli parlaklıkla değerlendir» koyu "
            "temaların açıklar gibi davranmasını sağlar - ikisini de "
            "açık bırakın.",
        "help.3.t": "Hiçbir şey bulunmuyor - veya çok fazla",
        "help.4.b": "Renkler sekmesinde «Benim rengim» tercih edilen "
            "renktir ve «Asla tıklanamaz renk(ler)» mutlaktır: o "
            "renkteki öğelere asla yardım edilmez. «Yalnızca benim "
            "rengime yardım et» yardımı eşleşen öğelerle sınırlar. "
            "İşleme'de «Renk eşleşmesinin katılığı» bir tonun ne "
            "kadar yakın olması gerektiğini söyler, «Benzer tonları "
            "kabul et» daha açık veya soluk sürümlerin kısmen "
            "sayılmasını sağlar ve «Renk avantajının gücü» "
            "renginizin bir öğeyi ne kadar yükselttiğini söyler - "
            "yanlış kazanmaya devam ederse yükseltin.",
        "help.4.t": "Renklerle çalışma",
        "help.5.b": "«Son tıklanan öğeyi hatırla», son başarılı "
            "tıklamanızın düştüğü öğeyi «Ne kadar süre hatırlanacak» "
            "saniye boyunca tercih etmeye devam eder - kaydırma "
            "çubuklarını ve iletişim kutusu düğmelerini keyifli "
            "yapan budur. «Hatıranın gücü» ne güçlü kazandığını "
            "söyler ve «Hatıra neyi öğrenebilir» onu korur: "
            "«Yalnızca benim rengimdeki öğeler» ile ıskalanmış bir "
            "tıklama onu başka yöne çeviremez. «Düğme basılıyken "
            "öğeyi takip et» sürüklemeleri sabitleştirir ve Deneysel "
            "sekmesindeki sağ düğme eylemleri hatırayı fareyle takip "
            "edebilir veya temizleyebilir.",
        "help.5.t": "Bir denetimde yinelenen tıklamalar",
        "help.6.b": "«Hareketli öğeleri önden nişanla», seçilen "
            "öğenin ne hızlı ilerlediğini ölçer ve «Ne kadar önden "
            "nişan alınacak» milisaniye kadar önden nişan alır, "
            "böylece tıklama kayan bir listenin veya video çubuğunun "
            "üzerine düşer, arkasına değil. Önden nişan 80 pikselle "
            "sınırlıdır ve duran veya dönen öğelerde kendini "
            "kapatır.",
        "help.6.t": "Hareket eden şeylere tıklamak",
        "help.7.b": "«İmleç hareketini canlandır» = 0 anında atlar; "
            "40-120 izleyebilmeniz için kayar ve fareyi kendiniz "
            "oynatmak kaymayı iptal eder. «Çift tıklama penceresi» "
            "klasik modda aynı yere yakın ikinci bir yapışmayı çift "
            "tıklamaya çevirir. «Hızlı serideki her tıklamaya yardım "
            "et» bir serinin yalnız ilki yerine her tıklamasına "
            "yardım eder. «Takılmadan sonra duraksama», bir tarama "
            "takılırsa basılı tıklamayı iade eden emniyet supabıdır.",
        "help.7.t": "Tıklamalar nasıl hissedilir",
        "help.8.b": "Kısayollar sekmesi iki modu ve kayıt akışını "
            "açıklar. Kısaca: Ctrl, Alt, Shift veya Win içeren "
            "kısayollar sistem genelinde ayrılmıştır; tek başına "
            "tuşlar her yerde çalışır ve yazmaya devam eder. Bir "
            "makro, engellenen tek tuş basışını tüm bir kombinasyona "
            "çevirir. Kayıtlar gerçek girişinizi - her tuşu, fare "
            "tıklamasını ve imleç hareketini - yakalar ve Makrolar "
            "sekmesinden oynatır; her birinin kendi bir kez veya "
            "durdurana kadar tekrarla anahtarı vardır.",
        "help.8.t": "Tuşlar, makrolar ve kayıtlar",
        "help.9.b": "«Yapılandırmayı dışa aktar» yanındaki Dil "
            "düğmesi - giriş ve abonelik pencerelerinde de - tüm "
            "arayüzü yeniden başlatmadan anında değiştirir ve "
            "seçiminizi hatırlar. Hâlâ çevrilen diller sunulmaz, bu "
            "yüzden seçebildiğiniz her şey eksiksizdir.",
        "help.9.t": "Dil",
        "help.sub": "Her ayar, kendi sekmesinde gördüğünüz adla, "
            "ihtiyacınız olacak sırayla. Tek satırlık açıklama için "
            "bir adın üzerine gelin; bu sayfa uzun biçimdir.",
        "help.tail": "Ayarlar Uygula'ya bastığınızda geçerli olur. "
            "Programın yanındaki bir config.ini, config.json'ı "
            "geçersiz kılar. Bu sayfa açıklar; yapılandırmaz.",
        "help.title": "Snappy AI'ı sade sözlerle ayarlama",
        "kb.keys.b": "Ctrl, Alt, Shift veya Win içeren bir kısayol "
            "sistem genelinde ayrılmıştır: onu yalnız Snappy AI "
            "görür. Çıplak tek tuş (1 veya 2 gibi) her programda "
            "çalışır VE normal yazmaya devam eder - bedeli, cümle "
            "ortasında basmanın eylemini de tetiklemesidir. Klasik "
            "davranış için Yardım sekmesinde «Tek tuşlu kısayollar "
            "tuşu yutar»ı açın. Makrolar daha ileri gider: "
            "çalışırken tetik tuşu yutulur ve yandaki kombinasyon "
            "tam bir kez gönderilir.",
        "kb.keys.t": "Tek tuşlar ve kombinasyonlar",
        "kb.mode.b": "Kılavuz mod (varsayılan, kısayol 2): "
            "tıklamanız her zaman programa dokunulmamış ulaşır; "
            "düğmeyi bırakınca imleç en yakın temiz öğeye gider, "
            "böylece sonraki tıklamanız oradan başlar. Hiçbir şey "
            "asla yutulmaz - en güvenli mod.  Klasik mod (kısayol "
            "1): bir öğenin yakınına tıklarsanız, o ıskalanan "
            "tıklama yakalanır, imleç öğeye yapışır ve Snappy AI "
            "sizin için tıklar; yakında hiçbir şey yoksa tıklamanız "
            "dokunulmamış iade edilir.  Her iki modda da tıklarken "
            "Shift'i basılı tutmak, o tek tıklama için yardımı "
            "atlar.",
        "kb.mode.t": "İki mod ne yapar",
        "kb.rec.b": "Çalışırken kayıt başlatma kısayoluna basın "
            "(varsayılan Ctrl+Alt+R): bastığınız her tuş, "
            "tıkladığınız her fare düğmesi ve her imleç hareketi "
            "yakalanır VE programlarınıza ulaşmaya devam eder, "
            "böylece kayıt sırasında normal çalışabilirsiniz. Durdur "
            "kısayoluna (Ctrl+Alt+S) basınca Makrolar sekmesindeki "
            "listeye kaydedilir - oraya beş kayıt sığar. Seçmek için "
            "bir kayda tıklayın, «Yeniden adlandır» veya «Dışa "
            "aktar» yapın ve kendi «Durdurana kadar tekrarla» "
            "anahtarını ayarlayın. Oynatma kısayolu (Ctrl+Alt+M) "
            "orada seçilen kaydı oynatır; Ctrl+1 ile Ctrl+5 "
            "listedeki konumuna göre oynatır. Duraklatıldığında "
            "hiçbir şey kaydedilmez ve hiçbir şey enjekte edilmez - "
            "girişiniz tamamen sizindir.",
        "kb.rec.t": "Kendi tuş ve fare hareketlerinizi kaydetme ve "
            "oynatma",
        "lang.close": "Kapat",
        "lang.coverage": "%%%d çevrildi",
        "lang.current": "Geçerli: %s",
        "lang.progress": "Hâlâ çevriliyor, tamamlanınca sunulacak: "
            "%s",
        "lang.prompt": "Değişiklik anında uygulanır; pencere açık "
            "kalır, birkaçını deneyebilirsiniz.",
        "lang.title": "Dil",
        "lbl.accent_boost": "Renk avantajının gücü",
        "lbl.accent_coherent": "Dağınık renk beneklerini yoksay",
        "lbl.accent_color": "Benim rengim(renklerim)",
        "lbl.accent_matcher": "Renk eşleştirme motoru",
        "lbl.accent_only": "Yalnızca benim rengime yardım et",
        "lbl.accent_soft": "Benzer tonları kabul et",
        "lbl.accent_tolerance": "Renk eşleşmesinin katılığı",
        "lbl.accent_variants": "Rengimin açık ve koyu halleri",
        "lbl.adaptive_threshold": "Soluk ekranlara otomatik uyum",
        "lbl.auto_click": "Öğelere kendi tıklar",
        "lbl.auto_click_interval": "Otomatik tıklamalar arası saniye",
        "lbl.auto_click_max_clicks": "Oturum başına otomatik tıklama "
            "sınırı",
        "lbl.auto_click_min_contrast": "Otomatik hedef ne kadar net "
            "olmalı",
        "lbl.auto_click_radius": "Ortadan arama yarıçapı",
        "lbl.auto_click_repeat_px": "Aynı yeri tekrar tıklama",
        "lbl.auto_click_settle_ms": "Otomatik tıklamadan önce "
            "bekleme",
        "lbl.block_bound_keys": "Tek tuşlu kısayollar tuşu yutar",
        "lbl.capture_backend": "Ekran yakalama motoru",
        "lbl.color_adapt": "Ekran ışığına uyum sağla",
        "lbl.contrast_threshold": "Bir kenar ne kadar soluk olabilir",
        "lbl.exclude_color": "Asla tıklanamaz renk(ler)",
        "lbl.follow_boost": "Hatıranın gücü",
        "lbl.follow_enabled": "Son tıklanan öğeyi hatırla",
        "lbl.follow_learn": "Hatıra neyi öğrenebilir",
        "lbl.follow_seconds": "Ne kadar süre hatırlanacak",
        "lbl.glide_ms": "İmleç hareketini canlandır",
        "lbl.hold_follow": "Düğme basılıyken öğeyi takip et",
        "lbl.key_launch": "Kısayol: yardımı başlat",
        "lbl.key_mode1": "Kısayol: klasik mod (en çok 4 tuş)",
        "lbl.key_mode2": "Kısayol: kılavuz mod (en çok 4 tuş)",
        "lbl.key_pause": "Kısayol: duraklat",
        "lbl.key_play": "Kısayol: seçili kaydı oynat",
        "lbl.key_play_n": "Kısayol: #%d kaydını oynat",
        "lbl.key_record": "Kısayol: kayda başla",
        "lbl.key_record_stop": "Kısayol: kaydı durdur ve kaydet",
        "lbl.luminance_norm": "Kenarları göreli parlaklıkla "
            "değerlendir",
        "lbl.macro_action": "Makro %d: bunun yerine gönderir",
        "lbl.macro_key": "Makro %d: bu tuşa bas",
        "lbl.max_area": "En büyük öğe alanı",
        "lbl.max_dim": "En büyük genişlik veya yükseklik",
        "lbl.merge_distance": "Yakın parçaları yapıştır",
        "lbl.min_area": "En küçük öğe boyutu",
        "lbl.min_contrast": "En düşük kenar netliği",
        "lbl.motion_3d": "Hareketlide daha akıllı takip",
        "lbl.motion_lead_ms": "Ne kadar önden nişan alınacak",
        "lbl.motion_predict": "Hareketli öğeleri önden nişanla",
        "lbl.watch_center_only": "Yalnızca ekran merkezini izle",
        "desc.watch_center_only": "Destek, yalnızca ekranın ortasındaki sabit bir kareyi tarar (boyut "
            "= arama mesafesi, varsayılan 150×150 px); imlecin nerede olduğu "
            "fark etmez. Bu karenin dışındaki tıklamalar değiştirilmez.",
        "lbl.center_follow": "Ekran hedefi takip eder",
        "desc.center_follow": "“Yalnızca ekran merkezini izle” açıkken: bir öğeye kilitlenince "
            "destek, özellikle kayan düzlemlerde, onu merkezde tutmak için "
            "ekranı hareket ettirir. Takibi bırakmak için ekranı siz hareket "
            "ettirin.",
        "lbl.input_backend": "Giriş yöntemi",
        "desc.input_backend": "Windows enjeksiyonu (varsayılan) her yerde çalışır. Interception "
            "sürücü üzerinden gönderir ve oyunlar bunu gerçek fare olarak "
            "tanır; kurulu Interception sürücüsü ve programın yanında "
            "interception.dll gerektirir; aksi halde otomatik olarak Windows "
            "enjeksiyonu kullanılır.",
        "val.input_backend.win32": "Windows enjeksiyonu",
        "val.input_backend.interception": "Interception (sürücü)",
        "lbl.mouse2_action": "Sağ tıkın ek eylemi",
        "lbl.mouse2_hold_action": "Sağı basılı tutmanın eylemi",
        "lbl.on_target_dist": "«Zaten üzerinde» uzaklığı",
        "lbl.radius": "İmleçten arama uzaklığı",
        "lbl.rapid_click_snap": "Hızlı serideki her tıklamaya yardım "
            "et",
        "lbl.snap_offset_x": "Tıklama noktası: sola / sağa kaydır",
        "lbl.snap_offset_y": "Tıklama noktası: yukarı / aşağı kaydır",
        "lbl.stall_pause_seconds": "Takılmadan sonra duraksama",
        "lbl.watcher_seconds": "Çift tıklama penceresi",
        "login.failed": "%s girişi tamamlanmadı - yeniden deneyin.",
        "login.no_provider": "Bu kopyaya yerleşik bir giriş "
            "sağlayıcı yok.",
        "login.not_configured": "Abonelik dosyası bu derlemede henüz "
            "yapılandırılmamış.",
        "login.note": "Giriş tarayıcınızı açar ve kendiliğinden bu "
            "pencereye döner.",
        "login.provider": "%s ile giriş yap",
        "login.signedin": "%s olarak giriş yapıldı.",
        "login.sub": "Discord ile giriş yapın - aboneliğiniz bu "
            "hesaba bağlıdır ve ödemeler onun e-posta adresini "
            "kullanmalıdır. Burada parola yoktur.",
        "login.title": "%s - Giriş",
        "login.unreachable": "Kimlik doğrulama sunucusuna "
            "ulaşılamıyor: %s",
        "login.waiting": "Tarayıcı bekleniyor - %s girişini "
            "tamamlayın...",
        "mac.delete": "Sil",
        "mac.empty": "Henüz kayıt yok - başlatın, kayıt kısayoluna "
            "basın ve normal çalışın: her tuş, tıklama ve imleç "
            "hareketi yakalanır.",
        "mac.export": "Dışa aktar",
        "mac.import": "İçe aktar",
        "mac.keys_head": "Tuş makroları",
        "mac.loop": "Durdurana kadar tekrarla",
        "mac.recordings": "Kayıtlar",
        "mac.rename": "Yeniden adlandır",
        "mac.row": "Makro %d",
        "mac.sends": "gönderir",
        "mac.steps": "%d adım",
        "note.advanced": "Bulunanı değil, tıklamaların nasıl "
            "hissedildiğini değiştiren uzaklık ve zaman ayarları. "
            "Çoğu kişinin bunlara dokunması gerekmez; varsayılanlar "
            "test edilmiş olanlardır.",
        "note.assist": "Çalışırken davranışı değiştiren her anahtar. "
            "İki mod, mod tuşlarınızla değişir - her modun ne "
            "yaptığını Kısayollar sekmesi açıklar. Yardım her zaman "
            "duraklatılmış başlar; Başlat tek açma/kapama. Motorun "
            "nereye baktığı ve tıklamaların nasıl hissettirdiği "
            "Gelişmiş'te; öğe sayılan şey İşleme'de.",
        "note.colors": "Üstteki iki liste, Snappy AI'ın hangi "
            "renkleri tercih edip reddedeceğini seçer. Her biri "
            "renklerini sağda kutular olarak gösterir, en fazla on "
            "beş, ve bir kutuya tıklamak o rengi yeniden kaldırır; "
            "boş liste üstü çizili bir kutu gösterir ve kapalı "
            "sayılır. «Tercih edilen renklere ekle» ve «Reddedilen "
            "renklere ekle», karıştırıcıda duran rengi ilgili "
            "listeye koyar. Geçerli RGB değeri, karıştırıcıdaki "
            "rengin ne kadar kırmızı, yeşil ve mavi tuttuğuna göre "
            "parlayan üç kutu gösterir - her biri beş renk kutusu "
            "genişliğindedir, böylece satır aşağıdaki her şeyle aynı "
            "on beş kutuyu kaplar; satır karıştırıcıyı izler ve "
            "yazılamaz. Alttaki karıştırıcı bir çizim programı gibi "
            "renk karıştırır; yanındaki her şey pencerenin sağ "
            "tarafında, üstteki ayarlarla kenara aynı boşlukta durur "
            "ve her satır aynı on beş kutu genişliğini kaplar: "
            "içinde #değeri çizili uzun vitrin, sonra on beş hazır "
            "ton, iki ekleme düğmesi ve ekran satırı - «Ekrandan "
            "renk al» imlecin altındaki tek rengi alır, «Ekrandan "
            "renkler öner» imlecin çevresinde bulduğu renklerle "
            "kendi on beş kutusunu doldurur ve birine tıklamak onu "
            "karıştırıcıya yükler. Vitrinin uzun olması bilinçli: "
            "böylece öneri kutuları soldaki renk kaydırıcısıyla tam "
            "aynı hizada biter.",
        "note.experimental": "Motor seçimleri, her birinin test "
            "edilmiş bir varsayılanı var. Yalnızca motorları "
            "karşılaştırırken, alışılmadık donanımda veya destek "
            "istediğinde değiştirin - yakalama motoru yeniden "
            "başlatmadan sonra geçerli.",
        "note.handler": "Tıklanabilir öğe sayılan şey: bir kenar ne "
            "kadar soluk olabilir, ne kadar net olmalıdır ve bir öğe "
            "ne kadar büyük veya küçük olabilir. Hiçbir şey "
            "bulunmuyor mu? Bunları gevşetin. Yanlış şey mi "
            "bulunuyor? Sıkılaştırın veya Renkler sekmesinde "
            "renginizi kullanın.",
        "note.keybindings": "Her kısayol - ve altında, iki modun ne "
            "yaptığı, kendi tuş ve fare hareketlerinizi nasıl "
            "kaydedeceğiniz ve tek tuşun kombinasyondan nasıl farklı "
            "olduğu.",
        "note.macros": "Bir makro, çalışırken tek tuş basışını tüm "
            "bir kombinasyona çevirir. Makroların yanında "
            "kayıtlarınız: yaptığınız her şeyin - her tuş, fare "
            "tıklaması ve imleç hareketi - adlı yakalamaları, en "
            "fazla beş tane, kaydedildiği gibi oynatılır. Seçmek "
            "için bir kayda tıklayın; her satır kendi «Durdurana "
            "kadar tekrarla» anahtarını taşır ve «Yeniden adlandır», "
            "«Dışa aktar», «İçe aktar» ile «Sil» kutunun altında yan "
            "yana durur.",
        "note.macros_keys": "Kayıt/oynatma kısayolları Kısayollar "
            "sekmesinde (varsayılanlar: Ctrl+Alt+R kaydet, "
            "Ctrl+Alt+S durdur ve kaydet, Ctrl+Alt+M oynat, "
            "Ctrl+1..5 konuma göre oynat).",
        "online.cancelled": "Discord kimlik doğrulaması iptal edildi "
            "(veya başarısız oldu). Lütfen yeniden deneyin.",
        "rec.export_fail": "Dışa aktarma başarısız: %r",
        "rec.exported": "Şuraya dışa aktarıldı: %s",
        "rec.import_fail": "İçe aktarma başarısız: %r",
        "rec.imported": "%d kayıt içe aktarıldı%s.",
        "rec.imported_none": " (hiçbiri geçerli değildi)",
        "rec.no_sel": "Dışa aktarmak için hiçbir şey seçilmedi.",
        "rec.notfile": "İçe aktarma başarısız: bu bir kayıt dosyası "
            "değil.",
        "shared.back": "Tekrar hoş geldiniz - hazır olunca Başlat'a "
            "basın.",
        "shared.body": "Bu Discord hesabı şu anda Snappy AI'ı başka "
            "bir bilgisayarda çalıştırıyor.\nYalnız bir oturum "
            "kalana dek yardım burada duraklatıldı.\n\nTek abonelik, "
            "tek makine - fiyatı düşük\ntutan ve geliştirmeyi "
            "sürdüren budur.",
        "shared.close": "Kapat",
        "shared.recheck": "Şimdi yeniden denetle",
        "shared.still": "Hâlâ başka yerde kullanımda - duraklamada "
            "kalıyoruz.",
        "shared.title": "Hesap başka yerde kullanımda",
        "shared.unreachable": "Sunucuya ulaşılamıyor - yeniden "
            "denetlenecek.",
        "st.all_files": "Tüm dosyalar",
        "st.color_added": "rgb(%d, %d, %d) %s alanına eklendi - "
            "Uygula kaydeder.",
        "st.color_already": "rgb(%d, %d, %d) zaten %s içinde.",
        "st.color_full": "%s zaten 15 renk içeriyor - önce bir rengi "
            "kaldırmak için kutularından birine tıklayın.",
        "st.color_removed": "rgb(%d, %d, %d) %s alanından kaldırıldı "
            "- Uygula kaydeder.",
        "st.delete_confirm": "%r kaydı silinsin mi?\nBu geri "
            "alınamaz.",
        "st.deleted": "Kayıt silindi.",
        "st.engine_dead": "Motor iş parçacığı kullanılamıyor - "
            "kısayollar yanıt vermiyor.",
        "st.ent_paused": "Abonelik %s - yardım duraklatıldı. "
            "Stripe'ta yenileyin, sonra yeniden başlatın.",
        "st.ent_unreachable": "Abonelik denetimi: sunucuya "
            "ulaşılamıyor (oturum sürüyor).",
        "st.export_fail": "Dışa aktarma başarısız: %r",
        "st.export_rec_title": "Kaydı dışa aktar",
        "st.export_title": "Ayarları dışa aktar",
        "st.exported": "Ayarlar şuraya dışa aktarıldı: %s",
        "st.file_rec": "Snappy AI kaydı",
        "st.file_settings": "Snappy AI ayarları",
        "st.follow": "  |  izleme %d sn önce",
        "st.import_fail": "İçe aktarma başarısız: %r",
        "st.import_notfile": "İçe aktarma başarısız: bu bir ayar "
            "dosyası değil.",
        "st.import_rec_title": "Kayıt(lar)ı içe aktar",
        "st.import_title": "Ayarları içe aktar",
        "st.imported": "%d ayar içe aktarıldı%s.",
        "st.imported_ignored": ", yok sayıldı: %s",
        "st.ini_over": "Uygulandı, ama config.ini geçersiz kılıyor: "
            "%s",
        "st.lib_empty": "Liste boş - dışa aktarılacak bir şey yok.",
        "st.line": "Yardım edilen %d  |  geçirilen %d%s  |  tema: %s",
        "st.loop_desc": "BU kaydın oynatma biçimi: kapalı = bir kez "
            "oynat; açık = oynatma kısayoluna yeniden basana dek "
            "tekrarla. Her kaydın kendi anahtarı vardır, kaydın "
            "kendisiyle birlikte saklanır.",
        "st.name_empty": "Ad boş olamaz.",
        "st.pick_err": "Alma başarısız: %r",
        "st.pick_fail": "Alma başarısız - yeniden deneyin.",
        "st.pick_ok": "rgb(%d, %d, %d) (%d, %d) konumundan alındı.",
        "st.pick_wait": "İmleci rengin üzerine getirin - 3 sn içinde "
            "alınıyor...",
        "st.preset_desc": "Hazır ton: %s - karıştırıcıya yüklemek "
            "için tıklayın.",
        "st.rec_count": "%d / 5 kayıt",
        "st.rec_now": "%r şimdi: %s.",
        "st.rec_once": "bir kez oynat",
        "st.rec_playing": "%r oynatılıyor...",
        "st.rec_playing_loop": "%r durdurana kadar oynatılıyor",
        "st.rec_recording": "KAYIT - %s durdurur ve kaydeder",
        "st.rec_repeats": "durdurana kadar tekrarla",
        "st.registered": "Kayıtlı: %s    Durum: %s",
        "st.rename_prompt": "#%d kaydının yeni adı:",
        "st.renamed": "Kayıt yeniden adlandırıldı.",
        "st.reset_confirm": "Tüm ayarlar varsayılana sıfırlansın "
            "mı?\nHesaplar korunur; bu yalnız ayarları etkiler.",
        "st.rgb_bad": "Önce geçerli R/G/B değerleri girin.",
        "st.running": "Çalışıyor..",
        "st.saved": "Kaydedildi ve uygulandı.",
        "st.defaults_restored": "Varsayılanlar geri yüklendi.",
        "st.saved_bad": "Kaydedildi, ama geçersiz (eskisi korundu): "
            "%s",
        "st.select_rec": "Önce bir kayıt seçin.",
        "st.shared_paused": "HESAP BAŞKA YERDE KULLANIMDA - yardım "
            "duraklatıldı; bir abonelik = bir makine.",
        "st.standby": "Beklemede..",
        "st.sug_fail": "Öneri başarısız: %r",
        "st.sug_loaded": "Öneri rgb(%d, %d, %d) karıştırıcıda - "
            "yukarıdaki düğmelerle bir listeye ekleyin.",
        "st.sug_loaded_desc": "Önerilen arayüz rengi rgb(%d, %d, %d) "
            "- örneklenen bölgenin %%%d'si. Karıştırıcıya yüklemek "
            "için tıklayın.",
        "st.sug_none": "Bu bölgeden renk önerisi yok.",
        "st.sug_ok": "%d öneri - birine tıklayınca karıştırıcıya "
            "yüklenir.",
        "st.sug_wait": "Çalıştığınız uygulamayı gösterin - 3 sn "
            "içinde örnekleniyor...",
        "tab.advanced": "Gelişmiş",
        "tab.assist": "Yardım",
        "tab.colors": "Renkler",
        "tab.experimental": "Deneysel",
        "tab.handler": "İşleme",
        "tab.help": "Yardım",
        "tab.hotkeys": "Kısayollar",
        "tab.macros": "Makrolar",
        "theme.dark": "Koyu",
        "theme.light": "Açık",
        "val.accent_matcher.hsv": "Klasik - eski motor",
        "val.accent_matcher.oklab": "Algısal - renkler nasıl "
            "görünüyorsa (önerilen)",
        "val.capture_backend.auto": "Otomatik - güvenli yedekli en "
            "hızlısı",
        "val.capture_backend.dxcam": "Desktop Duplication - çoğu "
            "PC'de en hızlısı",
        "val.capture_backend.mss": "Uyumlu - her zaman çalışır (Uzak "
            "Masaüstü, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "deneysel",
        "val.follow_learn.accent": "Yalnızca benim rengimdeki öğeler",
        "val.follow_learn.any": "Her başarılı yapışma",
        "val.mouse2_action.1": "Geçerli takip görevini temizle",
        "val.mouse2_action.2": "Son yakalanan rengi takip et",
        "val.mouse2_action.3": "İmlecin altındaki rengi al ve onu "
            "takip et",
        "val.mouse2_action.4": "Hiçbir şey yapma",
        "val.mouse2_hold_action.1": "Geçerli takip görevini temizle",
        "val.mouse2_hold_action.2": "Son yakalanan rengi takip et",
        "val.mouse2_hold_action.3": "İmlecin altındaki rengi al ve "
            "onu takip et",
        "val.mouse2_hold_action.4": "Hiçbir şey yapma",
        "word.off": "Kapalı",
        "word.on": "Açık",
    },
    "uk": {
        "btn.apply": "Застосувати",
        "btn.export": "Експорт налаштувань",
        "btn.import": "Імпорт налаштувань",
        "btn.language": "Мова: %s",
        "btn.launch": "Запуск",
        "btn.logout": "Вийти",
        "btn.pause": "Пауза",
        "btn.restore": "Повернути типові",
        "col.accent": "Акцент",
        "col.add_pref": "Додати до бажаних кольорів",
        "col.add_ref": "Додати до відхилених",
        "col.chip_desc": "rgb(%d, %d, %d) у %s - клікніть по "
            "квадратику, щоб прибрати цей колір.",
        "col.chip_off": "У %s немає кольорів - перекреслений квадрат "
            "означає «вимкнено». Оберіть колір нижче і натисніть "
            "відповідну кнопку додавання.",
        "col.exclude": "Виключення",
        "col.pick": "Взяти колір з екрана",
        "col.rgb.desc": "Три квадратики показують колір, який зараз "
            "у змішувачі: перший світиться тим яскравіше, чим більше "
            "в ньому червоного, другий - зеленого, третій - синього; "
            "яскравіше означає більше. Рядок слідує за змішувачем, "
            "готовими тонами та екранними кнопками; вводити в нього "
            "не можна.",
        "col.rgb.name": "Поточне значення RGB",
        "col.suggest": "Порадити кольори з екрана",
        "desc.accent_boost": "Наскільки ваш колір підіймає оцінку "
            "елемента (0-3). Підніміть до 1,5-2, якщо все ще виграє "
            "не той елемент.",
        "desc.accent_coherent": "Ваш колір має утворювати зв'язну "
            "пляму, щоб зараховуватись - розсипані вкраплення "
            "дизерингу чи компресії ніколи не кваліфікують елемент, "
            "не підсилюють його й не вносять до "
            "ніколи-неклікабельного списку.",
        "desc.accent_color": "Колір, який Snappy AI має вподобавати, "
            "показаний квадратами кольору праворуч. Оберіть колір "
            "нижче і натисніть «Додати до бажаних кольорів», щоб "
            "додати його - щонайбільше п'ятнадцять квадратів; клац "
            "по квадрату знову прибирає цей колір. Елементи з одним "
            "із них виграють нічиї. Порожній список показує "
            "перекреслений квадрат і вимикає налаштування.",
        "desc.accent_matcher": "Як порівнюються кольори. "
            "Перцептивний ранжує за тим, як кольори справді "
            "виглядають, і є рекомендованим; класичний - старий "
            "рушій для порівняння.",
        "desc.accent_only": "Лише елементи з вашим кольором можуть "
            "бути асистовані; кліки в інших місцях проходять до "
            "Windows недоторканими.",
        "desc.accent_soft": "0-100: наскільки світліші, темніші чи "
            "вицвілі версії вашого кольору все ж враховуються. 0 = "
            "лише точні відтінки.",
        "desc.accent_tolerance": "Наскільки близьким має бути колір, "
            "щоб вважатися вашим (4-90). Менше = суворіше.",
        "desc.accent_variants": "Світліші й темніші копії вашого "
            "кольору теж зараховуються, щоб стани наведення, "
            "натискання й приглушення діяли без розширення допуску "
            "відтінку. Лише яскравість - невірний відтінок ніколи не "
            "проскочить.",
        "desc.adaptive_threshold": "Темні теми та вицвілі документи "
            "самі знижують свій поріг виявлення, тому бліді елементи "
            "теж знаходяться. Рекомендовано увімкнено.",
        "desc.auto_click": "Увімкнено: програма сама клацає кожні 0,1 с по найкращому елементі "
            "спостережуваної ділянки, пріоритет — контраст. Якщо заданий "
            "акцентний колір, придатні лише забарвлені елементи; без кольору "
            "клацаються тільки дуже чітко намальовані. Ніколи двічі в одному "
            "місці й не у власних вікнах.",
        "desc.auto_click_interval": "Як часто екран перевіряється на "
            "ваш колір (0,5-60). Повільне число - безпечне: 2-5 "
            "пасує до діалогу, за яким ви стежите.",
        "desc.auto_click_max_clicks": "Скільки разів може клікнути "
            "само після запуску (1-200). На ліміті зупиняється і "
            "повідомляє, щоб хибне налаштування не розбіглось.",
        "desc.auto_click_min_contrast": "За тією ж шкалою, що "
            "»Мінімальна чіткість краю«. Почніть зі значення за "
            "замовчуванням і підвищуйте, якщо клікає не те: "
            "зараховуватимуться лише сильні, чіткі елементи.",
        "desc.auto_click_radius": "Автоклік шукає навколо центру "
            "екрана (40-600 px). Ширше для зайнятого вікна; вужче, "
            "щоб бачив лише один контрол по центру.",
        "desc.auto_click_repeat_px": "Після автокліку ціль у "
            "стількох пікселях лишається у спокої (0-400). Без цього "
            "кнопка, що стоїть на екрані, клікалась би знову й "
            "знову.",
        "desc.auto_click_settle_ms": "Курсор відпочиває так на цілі "
            "(0-2000 мс) перед кліком, щоб програма спершу побачила "
            "підсвітку. 120 пасує більшості вікон.",
        "desc.block_bound_keys": "Вимк (типово): комбінація без "
            "Ctrl/Alt/Shift - як-от 1 чи V - діє в кожній програмі І "
            "далі друкує як зазвичай, тож натискання посеред речення "
            "також запускає її дію. Увім: дія все одно спрацьовує "
            "усюди, але клавіша більше не друкує.",
        "desc.capture_backend": "Як фотографується екран. "
            "Автоматично використовує сумісний спосіб, який бачить майже всі вікна; Сумісний працює "
            "завжди, зокрема у віддаленому робочому столі та "
            "віртуальних машинах. Діє після перезапуску.",
        "desc.color_adapt": "Кожен елемент перед порівнянням "
            "балансується по білому відносно власного фону, щоб "
            "нічне світло й відтінки теми перестали виштовхувати ваш "
            "колір з допуску. Вимикайте лише для порівняння з "
            "неадаптованим порівнювачем.",
        "desc.contrast_threshold": "Нижче знаходить блідіші елементи "
            "(і більше шуму); вище вимагає чіткіших країв.",
        "desc.default": "Наведіть курсор на назву налаштування, щоб "
            "побачити, що воно робить.",
        "desc.exclude_color": "Елементи з цими кольорами ніколи не "
            "супроводжуються: клац по них іде прямо до Windows в "
            "обох режимах. Показані квадратами кольору праворуч - "
            "оберіть колір нижче і натисніть «Додати до відхилених», "
            "щоб додати один (щонайбільше п'ятнадцять); клац по "
            "квадрату прибирає його. Порожній список показує "
            "перекреслений квадрат і вимикає налаштування.",
        "desc.follow_boost": "Наскільки сильно запом'ятований "
            "елемент виграє нічиї: 100% може подвоїти його оцінку, "
            "поки пам'ять свіжа, 25% - легкий поштовх.",
        "desc.follow_enabled": "Після вдалого причеплення схожі "
            "елементи чи елементи на тому самому місці виграють "
            "деякий час - зручно для смуг прокрутки та повторних "
            "кліків по одному елементу керування.",
        "desc.follow_learn": "Лише елементи мого кольору: схиблений "
            "клік не може перенацілити пам'ять. Кожне вдале "
            "причеплення: стара, довірлива поведінка.",
        "desc.follow_seconds": "Секунди, протягом яких "
            "запом'ятований елемент лишається пріоритетним після "
            "останнього вдалого причеплення (1-120).",
        "desc.glide_ms": "0 (типово) стрибає миттєво - найшвидше. "
            "40-120 ковзає, щоб ви бачили; власний рух миші скасовує "
            "ковзання.",
        "desc.hold_follow": "Поки ви тримаєте ліву кнопку одразу "
            "після причеплення - чи тиснете знову на запом'ятованому "
            "елементі - курсор лишається на кольорі цього елемента; "
            "це стабілізує перетягування, як-от повзунки смуг "
            "прокрутки. Натискання в інших місцях не чіпаються.",
        "desc.key_launch": "Формат: ctrl+l, f5, space, ctrl+alt+1 "
            "... Модифікатори: ctrl, alt, shift, win. Діє після "
            "«Застосувати».",
        "desc.key_mode1": "Через кому, напр. '1, f1, ctrl+f1, v'. Що "
            "робить класичний режим, пояснює вкладка «Комбінації "
            "клавіш».",
        "desc.key_mode2": "Через кому, напр. '2, f2, ctrl+f2, b'. Що "
            "робить режим ведення, пояснює вкладка «Комбінації "
            "клавіш».",
        "desc.key_pause": "Миша й клавіатура знову повністю ваші, до "
            "запуску.",
        "desc.key_play": "Відтворює запис, вибраний у списку "
            "макросів, або найновіший, якщо нічого не вибрано. На "
            "записі, що повторюється, зупиняє його.",
        "desc.key_play_n": "Відтворює запис #%d з нумерованого "
            "списку на вкладці Макроси, за позицією. Якщо список "
            "коротший, нічого не стається.",
        "desc.key_record": "Захоплює все, що ви робите - кожну "
            "клавішу, кожен клік миші та кожен рух курсора, - поки "
            "ваш ввід далі сягає ваших програм, аж поки "
            "стоп-комбінація не збереже його до списку Макросів. "
            "Заряджено лише під час роботи.",
        "desc.key_record_stop": "Зупиняє захоплення, зберігає "
            "послідовність до списку макросів і зупиняє відтворення, "
            "що триває.",
        "desc.luminance_norm": "Краї оцінюються відносно яскравості "
            "оточення, тому темні теми поводяться як світлі. "
            "Рекомендовано увімкнено.",
        "desc.macro_action": "Комбінація, яку натискають за вас при "
            "кожному натисканні тригера (одне натискання = одна "
            "комбінація): 'ctrl+c', 'ctrl+shift+s', 'space', 'f5' "
            "... Порожньо = макрос вимкнено.",
        "desc.macro_key": "Клавіша, яка ОЗНАЧАЄ макрос замість "
            "друку: 'b', 'f7', 'ctrl+b' ... Під час роботи одне "
            "натискання надсилає комбінацію поруч рівно один раз, і "
            "клавіша не сягає ваших програм. У паузі друкує як "
            "зазвичай. Порожньо = макрос вимкнено.",
        "desc.max_area": "Більші плями ігноруються - зазвичай цілі "
            "вікна чи тло, а не клікабельні елементи.",
        "desc.max_dim": "Елементи ширші чи вищі за це ігноруються; "
            "ті, що торкаються краю екрана, як смуги прокрутки, "
            "отримують подвійне.",
        "desc.merge_distance": "Шматки, ближчі за це (урваний "
            "контур, ікона поруч із підписом), стають одним "
            "елементом. Два повноцінні елементи ніколи не "
            "склеюються.",
        "desc.min_area": "Менші плями ігноруються як цяточки, якщо "
            "не приклеєні до більшого елемента.",
        "desc.min_contrast": "Елемент має бути принаймні таким "
            "чітким, щоб узагалі бути клікабельним. Значення нижче "
            "28 вважаються за 28: вбудований поріг якості не дає "
            "шуму стати клікабельним.",
        "desc.motion_3d": "Відстежує рухомі елементи позицією І "
            "розміром замість прямої підгонки: поодинокі погані "
            "скани ігноруються замість осліплення стеження, повороти "
            "проходяться, а раптовий стрибок розміру перезапускає "
            "трек (сканер узяв інший елемент). Ті ж пороги "
            "швидкості, той же ліміт 80 px - змінюються лише мізки. "
            "Працює самостійно.",
        "desc.motion_lead_ms": "Мілісекунди руху, на які випереджати "
            "рухомий елемент (0-300): 40-80 для повільного гортання, "
            "100-150 для швидких смуг. Межа 80 px, вимкнено для "
            "повільного або руху зі зміною напрямку.",
        "desc.motion_predict": "Для елементів, що рухаються під час "
            "кліку (списки, що гортаються, відеосмуги), цілить трохи "
            "вперед, аби клік упав на елемент. Нерухомі елементи не "
            "змінюються.",
        "desc.mouse2_action": "Що короткий правий клік робить "
            "ДОДАТКОВО - сам правий клік завжди зберігає свою "
            "звичайну функцію Windows. Типово: нічого.",
        "desc.mouse2_hold_action": "Ті самі варіанти, спрацьовують, "
            "коли ви УТРИМУЄТЕ праву кнопку близько пів секунди "
            "замість кліку. Одне натискання - це клік або "
            "утримування, ніколи обидва. Типово: нічого.",
        "desc.on_target_dist": "Якщо ваш клік падає в межах цих "
            "пікселів від центру елемента, нічого не рухається - ви "
            "влучили.",
        "desc.radius": "Дальність пошуку в пікселях (40-400). "
            "Збільште, якщо потрібний елемент зовсім поруч поза "
            "досяжністю; зменште, якщо виграє не той сусід.",
        "desc.rapid_click_snap": "Вимк (типово): поки клік "
            "обробляється, інші йдуть до Windows. Увім: кожен лівий "
            "клік асистується.",
        "desc.snap_offset_x": "Зсуває точку кліку вбік від центру "
            "елемента (-200 до 200, від'ємні вліво). Для контрола з "
            "мертвою серединою - розділена кнопка, повзунок - "
            "наведіть клік на живе місце один раз замість боротьби "
            "при кожному снапі.",
        "desc.snap_offset_y": "Зсуває точку кліку вертикально від "
            "центру елемента (-200 до 200, від'ємні вгору). Як "
            "бічний зсув: приземляйтесь на живу частину контрола.",
        "desc.stall_pause_seconds": "Якщо сканування колись "
            "застрягне, асистування паузує на цей час, і будь-який "
            "утримуваний клік повертається вам.",
        "desc.watcher_seconds": "У класичному режимі друге "
            "причеплення поблизу того самого місця в межах цього "
            "часу стає подвійним кліком по елементу.",
        "ent.cancel_line": "активна до %s - НЕ поновиться",
        "ent.canceled_line": "підписку завершено%s",
        "ent.expired_line": "минула %s - оновіть на Stripe",
        "ent.past_due_line": "платіж не пройшов - виправте картку в "
            "листі-квитанції Stripe; доступ повернеться, коли "
            "рахунок буде сплачено",
        "ent.plan": " (%s)",
        "ent.refunded_line": "повернена / оскаржена - активацію "
            "відкликано",
        "ent.st.active": "активна",
        "ent.st.canceled": "завершена",
        "ent.st.canceling": "активна, але скасовується",
        "ent.st.grant": "підтримна надання",
        "ent.st.past_due": "ПЛАТІЖ НЕ ПРОЙШОВ",
        "ent.st.refunded": "повернена / оскаржена",
        "ent.st.trial": "проба",
        "ent.st.unsubscribed": "немає підписки",
        "ent.until": " до %s",
        "err.auth_unreachable": "Сервер автентифікації Snappy AI "
            "недоступний:\n%s\n\nSnappy AI працює лише з живою "
            "відповіддю від нього.\nПовторити?",
        "err.start_fail": "Snappy AI не зміг запуститися.\nЗапустіть "
            "з --console, щоб побачити деталі.",
        "gate.btn.monthly": "Місячна підписка за 9,99€",
        "gate.btn.trial": "Пробна покупка за 1,99€",
        "gate.head.canceled": "Цю підписку скасовано - створіть нову "
            "на Stripe, щоб продовжити.",
        "gate.head.canceling": "Вашу підписку налаштовано на "
            "скасування - вона активна до %s, потім цей вхід знову "
            "заблокується, якщо не оновите.",
        "gate.head.email_mismatch": "Платіж зроблено з іншого "
            "e-mail, ніж ваш обліковий запис Discord. Підписки "
            "працюють лише на показаному нижче e-mail Discord - "
            "підпишіться з нього ще раз або зверніться до підтримки.",
        "gate.head.expired": "Підписка цього входу минула - оновіть "
            "її на Stripe, щоб продовжити.",
        "gate.head.none": "Ви увійшли, але цей вхід не має активної "
            "підписки. Сплатіть ЦИМ e-mail Discord - покупка з іншої "
            "адреси не може його активувати.",
        "gate.head.past_due": "Останній платіж підписки не пройшов - "
            "виправте його на Stripe, щоб знову увімкнути цей вхід.",
        "gate.head.refunded": "Цю покупку повернено або оскаржено, "
            "тож активацію відкликано. Нова підписка на цьому e-mail "
            "Discord знову активує її.",
        "gate.head.shared": "Цей обліковий запис ЗАРАЗ працює на "
            "ІНШОМУ комп'ютері. Snappy AI лишається вимкненим, поки "
            "той самий обліковий запис Discord працює у двох місцях "
            "- закрийте іншу сесію та перевірте знову. Спільні "
            "підписки піднімають ціни; будь ласка, не робіть цього.",
        "gate.msg.active": "Підписка активна - Snappy AI "
            "запускається...",
        "gate.msg.checking": "Перевіряємо у сервера...",
        "gate.msg.no_link": "Це платіжне посилання не налаштовано в "
            "цій збірці.",
        "gate.msg.open_fail": "Не вдалося відкрити браузер. "
            "Відкрийте це посилання вручну:\n%s",
        "gate.msg.open_ok": "Stripe відкритий у вашому браузері - оплатіть там. Це вікно само помітить оплату та запустить рухавик.",
        "gate.msg.session_gone": "Сесія зникла - увійдіть знову.",
        "gate.msg.still_none": "Для цього входу все ще немає "
            "активної підписки.",
        "gate.msg.still_shared": "Все ще використовується на іншому "
            "комп'ютері - закрийте ту сесію та перевірте знову.",
        "gate.msg.unreachable": "Сервер автентифікації недоступний: "
            "%s",
        "gate.note": "Рушій стартує, щойно підписка активна - це "
            "вікно само перевіряється кожні 30 секунд. Закриття "
            "повертає до входу.",
        "gate.prices": "Проба на 2 дні: 1,99€ (разово)  -  підписка: "
            "9,99€ / міс.\nАктивація надходить до ~10 хвилин після "
            "оплати; оновлення автоматично повторно активують цей "
            "самий вхід.",
        "gate.title": "%s - Підписка%s",
        "hdr.build": "збірка %s",
        "help.1.b": "Snappy AI дивиться на екран довкола вашого "
            "курсора, знаходить міцні речі формою схожі на елементи "
            "- кнопки, іконки, посилання - і обирає найкращу: "
            "виграють чіткі краї, пристойний розмір і близькість до "
            "курсора. Ваш колір, список «ніколи не клікати» та "
            "пам'ять останнього кліку можуть схилити вибір. Далі "
            "курсор цілить у середину елемента, а не в кут його "
            "рамки.",
        "help.1.t": "Що стається, коли ви клікаєте",
        "help.10.b": "1. Чи запущено? Пауза означає, що нічого не "
            "перехоплюється - «Клавіша: почати асистування» (типово "
            "Ctrl+L) є єдиним увімк/вимк.  2. Утримайте Shift на "
            "одному кліку, щоб переконатися, що проблемою було "
            "асистування.  3. Виграє не той елемент: зменшіть "
            "«Дальність пошуку від курсора», потім задайте «Мій "
            "колір» або підніміть «Силу кольорової переваги».  4. "
            "Нічого не знаходиться: знизьте «Наскільки блідим може "
            "бути край» і «Мінімальна чіткість краю», підніміть "
            "«Найбільша ширина або висота» або «Склеювати близькі "
            "шматки».  5. Щось ніколи не має асистуватися: покладіть "
            "його колір у його колір у «Колір(и), по яких ніколи не "
            "клікати».  6. Все ще не так: повідомте службі "
            "підтримки, куди ви клікали і чого очікували, і додайте "
            "файл журналу, який Snappy AI пише у свою теку даних.",
        "help.10.t": "Якщо щось не так, перевіряйте в цьому порядку",
        "help.2.b": "Режим ведення (типовий) не з'їдає жодного "
            "кліку: ваш клік сягає програми, а після відпускання "
            "курсор їде на найближчий чистий елемент. Класичний "
            "режим сильніший: схиблений клік поруч з елементом "
            "ловиться, курсор причеплюється, і Snappy AI клікає за "
            "вас. «Дальність пошуку від курсора» задає коло пошуку - "
            "збільште, якщо потрібний елемент зовсім поруч поза "
            "досяжністю, зменште, якщо виграє не той сусід. "
            "Утримання Shift оминає один клік в обох режимах.",
        "help.2.t": "Почніть звідси: режим і дальність пошуку",
        "help.3.b": "На вкладці Обробка «Наскільки блідим може бути "
            "край» і «Мінімальна чіткість краю» вирішують, які краї "
            "рахуються: нижче знаходить блідіше, вище ігнорує шум. "
            "«Найменший розмір елемента», «Найбільша площа елемента» "
            "та «Найбільша ширина або висота» відсіюють цяточки й "
            "цілі вікна. «Склеювати близькі шматки» єднає урваний "
            "контур чи ікону поруч із підписом в один елемент. На "
            "вкладці Допомога «Автопідлаштування для тьмяних "
            "екранів» і «Оцінювати краї за відносною яскравістю» "
            "роблять темні теми схожими на світлі - лиште обидва "
            "увімкненими.",
        "help.3.t": "Нічого не знаходиться - або знаходиться "
            "забагато",
        "help.4.b": "На вкладці Кольори «Мій колір» - бажаний колір, "
            "а «Колір(и), по яких ніколи не клікати» - абсолютний: "
            "такі елементи ніколи не асистуються. «Асистувати лише "
            "мій колір» обмежує асистування відповідними елементами. "
            "В Обробці «Строгість збігу кольору» каже, наскільки "
            "близьким має бути відтінок, «Приймати близькі відтінки» "
            "дає світлішим чи вицвілим версіям рахуватися частково, "
            "а «Сила кольорової переваги» каже, наскільки ваш колір "
            "підіймає елемент - підніміть, якщо все ще виграє не "
            "той.",
        "help.4.t": "Робота з кольорами",
        "help.5.b": "«Пам'ятати останній клікнутий елемент» далі "
            "переважає елемент, на якому опинився ваш останній "
            "вдалий клік, протягом «Скільки часу пам'ятати» секунд - "
            "це робить зручними смуги прокрутки та кнопки діалогів. "
            "«Сила пам'яті» каже, наскільки сильно вона виграє, а "
            "«Чого може вчитися пам'ять» захищає її: з «Лише "
            "елементи мого кольору» схиблений клік не може її "
            "перенацілити. «Слідувати за елементом з утримуваною "
            "кнопкою» стабілізує перетягування, а дії правої кнопки "
            "на вкладці Експериментально можуть слідувати за "
            "пам'яттю або очищати її мишею.",
        "help.5.t": "Повторні кліки по одному елементу керування",
        "help.6.b": "«Випереджати рухомі елементи» міряє, як швидко "
            "рухається вибраний елемент, і цілить на «Наскільки "
            "цілити вперед» мілісекунд уперед, аби клік упав на "
            "список, що гортається, чи відеосмугу, а не позаду. "
            "Випередження має межу 80 пікселів і вимикається саме "
            "для нерухомих або тих, що звертають.",
        "help.6.t": "Кліки по рухомих речах",
        "help.7.b": "«Анімувати рух курсора» = 0 стрибає миттєво; "
            "40-120 ковзає, щоб ви бачили, а власний рух миші "
            "скасовує ковзання. «Вікно подвійного кліку» у "
            "класичному режимі перетворює друге причеплення поблизу "
            "того самого місця на подвійний клік. «Асистувати кожен "
            "клік швидкої серії» асистує кожен клік серії, а не лише "
            "перший. «Пауза після зупинки» - запобіжний клапан, що "
            "повертає утримуваний клік, якщо сканування застрягне.",
        "help.7.t": "Як відчуваються кліки",
        "help.8.b": "Вкладка «Гарячі клавіші» пояснює два режими та "
            "процес запису. Коротко: комбінації з Ctrl, Alt, Shift "
            "або Win зарезервовані системно; окремі клавіші "
            "спрацьовують всюди і далі друкують. Макрос перетворює "
            "одне блоковане натискання на цілу комбінацію. Записи "
            "захоплюють ваш справжній ввід - кожну клавішу, клік "
            "миші та рух курсора - і відтворюють його з вкладки "
            "Макроси; у кожного власний перемикач один раз або "
            "повторювати до зупинки.",
        "help.8.t": "Клавіші, макроси та записи",
        "help.9.b": "Кнопка Мова поруч з «Експорт налаштувань» - а "
            "також у вікнах входу та підписки - миттєво перемикає "
            "весь інтерфейс без перезапуску і пам'ятає ваш вибір. "
            "Мови, що ще перекладаються, не пропонуються, тож усе, "
            "що можна обрати, є повним.",
        "help.9.t": "Мова",
        "help.sub": "Кожне налаштування під назвою, яку ви бачите на "
            "його вкладці, у порядку, в якому знадобиться. Наведіть "
            "на назву для однорядкового опису; ця сторінка - довга "
            "форма.",
        "help.tail": "Налаштування діють після натискання "
            "«Застосувати». config.ini поруч із програмою перекриває "
            "config.json. Ця сторінка пояснює, а не налаштовує.",
        "help.title": "Налагодження Snappy AI простими словами",
        "kb.keys.b": "Комбінація з Ctrl, Alt, Shift або Win "
            "зарезервована на рівні системи: її бачить лише Snappy "
            "AI. Гола одинарна клавіша (як 1 чи 2) діє в кожній "
            "програмі І далі друкує - ціна в тому, що натискання її "
            "посеред речення також запускає дію. Для класичної "
            "поведінки увімкніть «Одноклавішні комбінації поглинають "
            "клавішу» на вкладці Допомога. Макроси йдуть далі: під "
            "час роботи клавіша-тригер поглинається, а комбінація "
            "поруч надсилається рівно один раз.",
        "kb.keys.t": "Одинарні клавіші проти комбінацій",
        "kb.mode.b": "Режим ведення (типовий, комбінація 2): ваш "
            "клік завжди сягає програми недоторканим; після "
            "відпускання кнопки курсор їде на найближчий чистий "
            "елемент, тож наступний клік стартує звідти. Нічого "
            "ніколи не поглинається - найбезпечніший режим.  "
            "Класичний режим (комбінація 1): якщо ви клікнули поруч "
            "з елементом, той схиблений клік ловиться, курсор "
            "причеплюється до елемента, і Snappy AI клікає за вас; "
            "якщо поруч нічого немає, ваш клік повертається "
            "недоторканим.  В обох режимах утримання Shift під час "
            "кліку оминає асистування для цього одного кліку.",
        "kb.mode.t": "Що роблять два режими",
        "kb.rec.b": "Під час роботи натисніть комбінацію початку "
            "запису (типово Ctrl+Alt+R): кожна натиснута клавіша, "
            "кожен клік миші та кожен рух курсора захоплюються І "
            "далі сягають ваших програм, тож ви працюєте як зазвичай "
            "під час запису. Натисніть стоп-комбінацію (Ctrl+Alt+S), "
            "щоб зберегти запис до списку на вкладці Макроси - туди "
            "вміщується п'ять записів. Клацніть запис, щоб вибрати "
            "його, скористатися «Перейменувати» чи «Експорт» і "
            "встановити власний перемикач «Повторювати до зупинки». "
            "Комбінація відтворення (Ctrl+Alt+M) грає вибраний там "
            "запис; Ctrl+1..Ctrl+5 грають за позицією у списку. На "
            "паузі нічого не записується і нічого не вводиться - ваш "
            "ввід повністю ваш.",
        "kb.rec.t": "Як записати й відтворити власні клавіші та дії "
            "миші",
        "lang.close": "Закрити",
        "lang.coverage": "Перекладено %d%%",
        "lang.current": "Поточна: %s",
        "lang.progress": "Ще перекладається, з'явиться коли буде "
            "готове: %s",
        "lang.prompt": "Зміна діє одразу - вікно лишається "
            "відкритим, можна спробувати кілька.",
        "lang.title": "Мова",
        "lbl.accent_boost": "Сила кольорової переваги",
        "lbl.accent_coherent": "Ігнорувати розсипані вкраплення",
        "lbl.accent_color": "Мій колір (кольори)",
        "lbl.accent_matcher": "Рушій порівняння кольорів",
        "lbl.accent_only": "Асистувати лише мій колір",
        "lbl.accent_soft": "Приймати близькі відтінки",
        "lbl.accent_tolerance": "Строгість збігу кольору",
        "lbl.accent_variants": "Світлі й темні стани мого кольору",
        "lbl.adaptive_threshold": "Автопідлаштування для тьмяних "
            "екранів",
        "lbl.auto_click": "Клацати елементи самостійно",
        "lbl.auto_click_interval": "Секунди між автокліками",
        "lbl.auto_click_max_clicks": "Ліміт автокліків за сеанс",
        "lbl.auto_click_min_contrast": "Наскільки чіткою має бути "
            "ціль",
        "lbl.auto_click_radius": "Шукати від центру екрана",
        "lbl.auto_click_repeat_px": "Не клікати в одне місце "
            "повторно",
        "lbl.auto_click_settle_ms": "Пауза перед автокліком",
        "lbl.block_bound_keys": "Одноклавішні комбінації поглинають "
            "клавішу",
        "lbl.capture_backend": "Рушій знімання екрана",
        "lbl.color_adapt": "Підлаштовуватись під світло екрана",
        "lbl.contrast_threshold": "Наскільки блідим може бути край",
        "lbl.exclude_color": "Колір(и), по яких ніколи не клікати",
        "lbl.follow_boost": "Сила пам'яті",
        "lbl.follow_enabled": "Пам'ятати останній клікнутий елемент",
        "lbl.follow_learn": "Чого може вчитися пам'ять",
        "lbl.follow_seconds": "Скільки часу пам'ятати",
        "lbl.glide_ms": "Анімувати рух курсора",
        "lbl.hold_follow": "Слідувати за елементом з утримуваною "
            "кнопкою",
        "lbl.key_launch": "Клавіша: почати асистування",
        "lbl.key_mode1": "Клавіша: класичний режим (до 4 клавіш)",
        "lbl.key_mode2": "Клавіша: режим ведення (до 4 клавіш)",
        "lbl.key_pause": "Клавіша: пауза",
        "lbl.key_play": "Клавіша: відтворити вибраний запис",
        "lbl.key_play_n": "Клавіша: відтворити запис #%d",
        "lbl.key_record": "Клавіша: почати запис",
        "lbl.key_record_stop": "Клавіша: зупинити й зберегти запис",
        "lbl.luminance_norm": "Оцінювати краї за відносною "
            "яскравістю",
        "lbl.macro_action": "Макрос %d: натомість надсилає",
        "lbl.macro_key": "Макрос %d: натисніть цю клавішу",
        "lbl.max_area": "Найбільша площа елемента",
        "lbl.max_dim": "Найбільша ширина або висота елемента",
        "lbl.merge_distance": "Склеювати близькі шматки",
        "lbl.min_area": "Найменший розмір елемента",
        "lbl.min_contrast": "Мінімальна чіткість краю",
        "lbl.motion_3d": "Розумніше стеження за рухомим",
        "lbl.motion_lead_ms": "Наскільки цілити вперед",
        "lbl.motion_predict": "Випереджати рухомі елементи",
        "lbl.watch_center_only": "Слідкувати лише за центром екрана",
        "desc.watch_center_only": "Помічник спостерігає лише за фіксованим квадратом у центрі екрана "
            "(розмір = дистанція пошуку, типово 150×150 px), незалежно від "
            "положення курсора. Кліки поза цим квадратом залишаються без змін.",
        "lbl.center_follow": "Екран слідкує за ціллю",
        "desc.center_follow": "Коли «Слідкувати лише за центром екрана» увімкнено: після "
            "захоплення елемента помічник рухає екран, щоб утримувати його в "
            "центрі, особливо на прокручуваних площинах. Рухайте екран "
            "самостійно, щоб відпустити стеження.",
        "lbl.input_backend": "Метод введення",
        "desc.input_backend": "Ін'єкція Windows (типово) працює скрізь. Interception надсилає "
            "через драйвер, і ігри розпізнають її як справжню мишу; потребує "
            "встановленого драйвера Interception і interception.dll поруч із "
            "програмою; інакше автоматично використовується ін'єкція Windows.",
        "val.input_backend.win32": "Ін'єкція Windows",
        "val.input_backend.interception": "Interception (драйвер)",
        "lbl.mouse2_action": "Додаткова дія правого кліку",
        "lbl.mouse2_hold_action": "Дія утримування правої кнопки",
        "lbl.on_target_dist": "Відстань «уже влучив»",
        "lbl.radius": "Дальність пошуку від курсора",
        "lbl.rapid_click_snap": "Асистувати кожен клік швидкої серії",
        "lbl.snap_offset_x": "Точка кліку: вліво / вправо",
        "lbl.snap_offset_y": "Точка кліку: вгору / вниз",
        "lbl.stall_pause_seconds": "Пауза після зупинки",
        "lbl.watcher_seconds": "Вікно подвійного кліку",
        "login.failed": "Вхід через %s не завершено - спробуйте "
            "знову.",
        "login.no_provider": "У цю копію не вбудовано надавача "
            "входу.",
        "login.not_configured": "Файл підписки ще не налаштовано в "
            "цій збірці.",
        "login.note": "Вхід відкриває ваш браузер і сам повертається "
            "до цього вікна.",
        "login.provider": "Увійти через %s",
        "login.signedin": "Ви увійшли як %s.",
        "login.sub": "Увійдіть через Discord - ваша підписка "
            "прив'язана до цього облікового запису, і платежі мають "
            "використовувати його e-mail. Пароля тут немає.",
        "login.title": "%s - Вхід",
        "login.unreachable": "Сервер автентифікації недоступний: %s",
        "login.waiting": "Чекаємо на браузер - завершіть вхід %s...",
        "mac.delete": "Видалити",
        "mac.empty": "Записів ще немає - запустіть, натисніть "
            "комбінацію запису й працюйте як зазвичай: кожна "
            "клавіша, клік і рух курсора захоплюються.",
        "mac.export": "Експорт",
        "mac.import": "Імпорт",
        "mac.keys_head": "Клавішні макроси",
        "mac.loop": "Повторювати до зупинки",
        "mac.recordings": "Записи",
        "mac.rename": "Перейменувати",
        "mac.row": "Макрос %d",
        "mac.sends": "надсилає",
        "mac.steps": "%d кроків",
        "note.advanced": "Налаштування відстані та часу, що змінюють "
            "відчуття кліків, а не те, що знаходиться. Більшості "
            "людей не потрібно їх чіпати; типові значення - "
            "перевірені.",
        "note.assist": "Кожен перемикач, що змінює поведінку під час "
            "роботи. Два режими перемикаються вашими клавішами "
            "режимів - вкладка «Комбінації клавіш» пояснює, що "
            "робить кожен. Асистування завжди стартує на паузі; "
            "Запуск - єдиний увімк/вимк. Де дивиться рушій і як "
            "відчуваються кліки - у «Додатково»; що вважається "
            "елементом - у «Обробка».",
        "note.colors": "Два списки вгорі вирішують, які кольори "
            "Snappy AI вподобає чи відкидає. Кожен показує свої "
            "кольори квадратами праворуч, щонайбільше п'ятнадцять, і "
            "клац по квадрату знову прибирає цей колір; порожній "
            "список показує перекреслений квадрат і вважається "
            "вимкненим. «Додати до бажаних кольорів» і «Додати до "
            "відхилених» кладуть колір, що стоїть у палітрі, у "
            "потрібний список. Поточне значення RGB показує три "
            "квадрати - кожен завширшки як п'ять кольорових "
            "квадратів, тож рядок займає ті самі п'ятнадцять "
            "квадратів, що й усе нижче, - які світяться тим "
            "яскравіше, чим більше червоного, зеленого та синього в "
            "кольорі палітри; рядок слідує за палітрою і не приймає "
            "введення. Палітра нижче змішує колір як графічний "
            "редактор; усе поруч із нею сидить у правому боці вікна "
            "з тим же відступом до краю, що й налаштування вище, і "
            "кожен рядок займає ту саму ширину в п'ятнадцять "
            "квадратів: висока вітрина з намальованим усередині "
            "#кодом, потім п'ятнадцять готових тонів, дві кнопки "
            "додавання та екранний ряд - «Взяти колір з екрана» бере "
            "один колір під курсором, «Порадити кольори з екрана» "
            "заповнює п'ятнадцять своїх квадратів кольорами, "
            "знайденими довкола курсора, і клац по одному завантажує "
            "його в палітру. Вітрина висока навмисне: так квадрати "
            "підказок закінчуються рівно на рівні кольорового "
            "повзунка ліворуч.",
        "note.experimental": "Вибір рушіїв, кожен з перевіреним "
            "типовим значенням. Змінюйте лише для порівняння рушіїв, "
            "на незвичному обладнанні або на прохання підтримки - "
            "рушій знімання діє після перезапуску.",
        "note.handler": "Що вважається клікабельним елементом: "
            "наскільки блідим може бути край, наскільки чітким має "
            "бути, і якого розміру може бути елемент. Нічого не "
            "знайдено? Послабте ці значення. Знайдено не те? "
            "Посильте їх, або скористайтеся своїм кольором на "
            "вкладці Кольори.",
        "note.keybindings": "Кожна комбінація - а нижче, що роблять "
            "два режими, як записати власні клавіші та дії миші і "
            "чим одинарна клавіша відрізняється від комбінації.",
        "note.macros": "Макрос перетворює одне натискання клавіші на "
            "цілу комбінацію під час роботи. Поруч із макросами ваші "
            "записи: до п'яти іменованих знімків усього, що ви "
            "зробили - кожна клавіша, клік миші та рух курсора, - "
            "які відтворюються точно як записано. Клацніть запис, "
            "щоб вибрати його; у кожному рядку власний перемикач "
            "«Повторювати до зупинки», а «Перейменувати», «Експорт», "
            "«Імпорт» і «Видалити» сидять унизу рамки.",
        "note.macros_keys": "Комбінації запису/відтворення - на "
            "вкладці «Комбінації клавіш» (типово: Ctrl+Alt+R запис, "
            "Ctrl+Alt+S зупинити й зберегти, Ctrl+Alt+M відтворити, "
            "Ctrl+1..5 відтворити за позицією).",
        "online.cancelled": "Автентифікацію Discord скасовано (або "
            "не вдалася). Спробуйте знову.",
        "rec.export_fail": "Експорт не вдався: %r",
        "rec.exported": "Експортовано до %s",
        "rec.import_fail": "Імпорт не вдався: %r",
        "rec.imported": "Імпортовано %d запис(ів)%s.",
        "rec.imported_none": " (жоден не був дійсним)",
        "rec.no_sel": "Нічого не вибрано для експорту.",
        "rec.notfile": "Імпорт не вдався: це не файл запису.",
        "shared.back": "З поверненням - натисніть Запуск, коли "
            "будете готові.",
        "shared.body": "Цей обліковий запис Discord запускає Snappy "
            "AI на іншому комп'ютері просто зараз.\nАсистування тут "
            "паузує, доки не лишиться одна сесія.\n\nОдна підписка, "
            "одна машина одночасно - саме це тримає\nціну низькою, а "
            "розробку живою.",
        "shared.close": "Закрити",
        "shared.recheck": "Перевірити зараз",
        "shared.still": "Все ще використовується інде - лишаємось на "
            "паузі.",
        "shared.title": "Обліковий запис використовується інде",
        "shared.unreachable": "Сервер недоступний - перевіримо "
            "знову.",
        "st.all_files": "Усі файли",
        "st.color_added": "rgb(%d, %d, %d) додано до %s - "
            "«Застосувати» збереже.",
        "st.color_already": "rgb(%d, %d, %d) уже є в %s.",
        "st.color_full": "У %s вже 15 кольорів - спершу клікніть по "
            "одному з квадратиків, щоб прибрати колір.",
        "st.color_removed": "rgb(%d, %d, %d) прибрано з %s - "
            "«Застосувати» збереже.",
        "st.delete_confirm": "Видалити запис %r?\nЦе неможливо "
            "скасувати.",
        "st.deleted": "Запис видалено.",
        "st.engine_dead": "Потік рушія недоступний - комбінації не "
            "відповідають.",
        "st.ent_paused": "Підписка %s - асистування на паузі. "
            "Оновіть на Stripe, потім перезапустіть.",
        "st.ent_unreachable": "Перевірка підписки: сервер "
            "недоступний (сесія триває).",
        "st.export_fail": "Експорт не вдався: %r",
        "st.export_rec_title": "Експорт запису",
        "st.export_title": "Експорт налаштувань",
        "st.exported": "Налаштування експортовано до %s",
        "st.file_rec": "Запис Snappy AI",
        "st.file_settings": "Налаштування Snappy AI",
        "st.follow": "  |  стеження %d с тому",
        "st.import_fail": "Імпорт не вдався: %r",
        "st.import_notfile": "Імпорт не вдався: це не файл "
            "налаштувань.",
        "st.import_rec_title": "Імпорт запису(ів)",
        "st.import_title": "Імпорт налаштувань",
        "st.imported": "Імпортовано %d налаштувань%s.",
        "st.imported_ignored": ", проігноровано: %s",
        "st.ini_over": "Застосовано, але config.ini перекриває: %s",
        "st.lib_empty": "Список порожній - немає чого експортувати.",
        "st.line": "Поміг %d  |  пропустив %d%s  |  тема: %s",
        "st.loop_desc": "Стиль відтворення ЦЬОГО запису: вимк = грає "
            "один раз; увімк = повторює, доки ви знову не натиснете "
            "комбінацію відтворення. У кожного запису власний "
            "перемикач, зберігається разом із самим записом.",
        "st.name_empty": "Назва не може бути порожньою.",
        "st.pick_err": "Зняття не вдалося: %r",
        "st.pick_fail": "Зняття не вдалося - спробуйте знову.",
        "st.pick_ok": "Узято rgb(%d, %d, %d) у (%d, %d).",
        "st.pick_wait": "Підведіть курсор до кольору - зняття за 3 "
            "с...",
        "st.preset_desc": "Готовий тон: %s - клікніть, щоб "
            "завантажити у змішувач.",
        "st.rec_count": "%d із 5 записів",
        "st.rec_now": "%r тепер: %s.",
        "st.rec_once": "грає один раз",
        "st.rec_playing": "Відтворення %r...",
        "st.rec_playing_loop": "Відтворення %r до зупинки",
        "st.rec_recording": "ЗАПИС - %s зупиняє та зберігає",
        "st.rec_repeats": "повторювати до зупинки",
        "st.registered": "Зареєстровано на: %s    Статус: %s",
        "st.rename_prompt": "Нова назва запису #%d:",
        "st.renamed": "Запис перейменовано.",
        "st.reset_confirm": "Повернути всі налаштування до "
            "типових?\nОблікові записи зберігаються; це стосується "
            "лише налаштувань.",
        "st.rgb_bad": "Спершу введіть коректні значення R/G/B.",
        "st.running": "Працює..",
        "st.saved": "Збережено і застосовано.",
        "st.defaults_restored": "Налаштування за замовчуванням відновлено.",
        "st.saved_bad": "Збережено, але недійсне (лишається старе): "
            "%s",
        "st.select_rec": "Спершу виберіть запис.",
        "st.shared_paused": "ОБЛІКОВИЙ ЗАПИС ВИКОРИСТОВУЄТЬСЯ ІНДЕ - "
            "асистування на паузі; одна підписка = одна машина.",
        "st.standby": "Очікування..",
        "st.sug_fail": "Пропозиція не вдалася: %r",
        "st.sug_loaded": "Підказка rgb(%d, %d, %d) стоїть у палітрі "
            "- додайте її до списку кнопками вище.",
        "st.sug_loaded_desc": "Запропонований колір інтерфейсу "
            "rgb(%d, %d, %d) - %d%% вибраної області. Клікніть, щоб "
            "завантажити у змішувач.",
        "st.sug_none": "Немає пропозицій кольору з цієї області.",
        "st.sug_ok": "%d підказок - клацніть одну, щоб завантажити "
            "її в палітру.",
        "st.sug_wait": "Наведіть на застосунок, у якому працюєте - "
            "вибірка за 3 с...",
        "tab.advanced": "Додатково",
        "tab.assist": "Допомога",
        "tab.colors": "Кольори",
        "tab.experimental": "Експериментально",
        "tab.handler": "Обробка",
        "tab.help": "Довідка",
        "tab.hotkeys": "Комбінації клавіш",
        "tab.macros": "Макроси",
        "theme.dark": "Темна",
        "theme.light": "Світла",
        "val.accent_matcher.hsv": "Класичний - старий рушій",
        "val.accent_matcher.oklab": "Перцептивний - як кольори "
            "виглядають (рекомендовано)",
        "val.capture_backend.auto": "Автоматично - найшвидший із "
            "надійним запасом",
        "val.capture_backend.dxcam": "Desktop Duplication - "
            "найшвидший на більшості ПК",
        "val.capture_backend.mss": "Сумісний - працює завжди "
            "(віддалений стіл, ВМ)",
        "val.capture_backend.wgc": "Windows Graphics Capture - "
            "експериментально",
        "val.follow_learn.accent": "Лише елементи мого кольору",
        "val.follow_learn.any": "Кожне вдале причеплення",
        "val.mouse2_action.1": "Прибрати поточне завдання стеження",
        "val.mouse2_action.2": "Слідувати за останнім кольором",
        "val.mouse2_action.3": "Взяти колір під курсором і слідувати "
            "за ним",
        "val.mouse2_action.4": "Нічого не робити",
        "val.mouse2_hold_action.1": "Прибрати поточне завдання "
            "стеження",
        "val.mouse2_hold_action.2": "Слідувати за останнім кольором",
        "val.mouse2_hold_action.3": "Взяти колір під курсором і "
            "слідувати за ним",
        "val.mouse2_hold_action.4": "Нічого не робити",
        "word.off": "Вимк",
        "word.on": "Увім",
    },
    "sw": {
        "btn.apply": "Tumia",
        "btn.export": "Toa mipangilio",
        "btn.import": "Ingiza mipangilio",
        "btn.language": "Lugha: %s",
        "btn.launch": "Anza",
        "btn.logout": "Toka",
        "btn.pause": "Simamisha",
        "btn.restore": "Rejesha chaguo-msingi",
        "col.accent": "Rangi kuu",
        "col.add_pref": "Ongeza zinazopendelewa",
        "col.add_ref": "Ongeza zinazokataliwa",
        "col.chip_desc": "rgb(%d, %d, %d) katika %s - bofya "
            "kisanduku kuondoa rangi hii.",
        "col.chip_off": "%s haina rangi - kisanduku kilichopigwa "
            "msalaba kinamaanisha kimezimwa. Chagua rangi hapa chini "
            "kisha bonyeza kitufe cha kuongeza kinacholingana.",
        "col.exclude": "Kutoa",
        "col.pick": "Chukua rangi kutoka skrini",
        "col.rgb.desc": "Visanduku vitatu huonyesha rangi iliyopo "
            "kwenye kichanganyiko sasa: cha kwanza huong'aa "
            "kulingana na nyekundu iliyo nacho, cha pili kijani, cha "
            "tatu bluu - angavu zaidi humaanisha zaidi. Safu hufuata "
            "kichanganyiko, toni tayari na vitufe vya skrini; "
            "haiwezi kuandikwa.",
        "col.rgb.name": "Thamani ya RGB ya sasa",
        "col.suggest": "Pendekeza rangi za skrini",
        "desc.accent_boost": "Rangi yako huinua alama ya kipengee "
            "kwa kiasi gani (0-3). Panda kuelekea 1,5-2 iwapo "
            "kipengee kisicho sahihi bado kinashinda.",
        "desc.accent_coherent": "Rangi yako lazima iunde doa "
            "lililounganika ili ihesabiwe - vidoti vilivyotawanyika "
            "vya dither au mgandamizo haviwezi kustahikisha "
            "kipengee, kukikuza, wala kukiweka kwenye orodha "
            "isiyoweza kubofywa kamwe.",
        "desc.accent_color": "Rangi ambayo Snappy AI inapaswa "
            "kupendelea, ikionyeshwa kama visanduku vya rangi upande "
            "wa kulia. Chagua rangi hapa chini na bonyeza «Ongeza "
            "zinazopendelewa» kuiongeza - visanduku kumi na vitano "
            "vipeo; kubofya kisanduku huondoa rangi hiyo tena. "
            "Vipengele vyenye moja yazo hushinda sare. Orodha tupu "
            "huonyesha kisanduku kilichopigwa msalaba na huzima "
            "mpangilio.",
        "desc.accent_matcher": "Jinsi rangi zinavyolinganishwa. Ya "
            "kuona huorodhesha kwa jinsi rangi zinavyoonekana kweli "
            "na ndiyo inayopendekezwa; ya Kale ni injini ya zamani, "
            "imehifadhiwa kwa ulinganisho.",
        "desc.accent_only": "Vipengele vyenye rangi yako pekee "
            "vinaweza kusaidiwa; mabofyo mahali pengine hupita bila "
            "kuguswa kwa Windows.",
        "desc.accent_soft": "0-100: kiasi ambacho toleo zilizo "
            "pepesi, nyeusi au zilipopauka za rangi yako bado "
            "huhesabika. 0 = vivuli sahihi pekee.",
        "desc.accent_tolerance": "Rangi lazima iwe karibu kiasi gani "
            "kuhesabika kama yako (4-90). Chini = kali zaidi.",
        "desc.accent_variants": "Nakala angavu na nyeusi zaidi za "
            "rangi yako pia zinahesabiwa, ili hali za kuelea, "
            "kubonyezwa na kufifia zihesabiwe bila kupanua uvumilivu "
            "wa rangi. Mwangaza tu - rangi isiyo sahihi haiwezi "
            "kupita.",
        "desc.adaptive_threshold": "Mandhari meusi na hati "
            "zilizopauka hushusha wenyewe kizingiti chao cha "
            "ugunduzi, hivyo vipengele dhaifu hupatikana pia. "
            "Inapendekezwa kuwasha.",
        "desc.auto_click": "Ikiwa washwa, programu yenyewe inabofya kila sekunde 0.1 kitu bora "
            "katika eneo linalozingatiwa, ikipanga kwanza kwa contrast. Ikiwa "
            "rangi ya kipaumbele imewekwa, vitu vilivyo na rangi hiyo ndivyo "
            "vinavyostahili; bila rangi, vitu vilivyo chorwa kwa ukali ndivyo "
            "vinabofywa. Kamwe mara mbili mahali pamoja wala dirisha lake "
            "lenyewe.",
        "desc.auto_click_interval": "Skrini inatazamwa mara ngapi "
            "kwa rangi yako (0,5-60). Nambari ya polepole ndiyo "
            "salama: 2-5 inafaa dirisha unalolitazama.",
        "desc.auto_click_max_clicks": "Mara ngapi inaweza kubofya "
            "yenyewe baada ya kuanzisha (1-200). Ikifika kikomo "
            "inasimama na kusema, ili mpangilio mbaya usikimbie.",
        "desc.auto_click_min_contrast": "Kwa kipimo kile kile cha "
            "»Uwazi wa chini wa kingo«. Anza na chaguo-msingi na "
            "pandisha ikibofya vibaya: ni vipengee vikali "
            "vilivyochorwa wazi vitahesabiwa.",
        "desc.auto_click_radius": "Mibofyo ya mojawa hutafuta "
            "kuzunguka katikati ya skrini (40-600 px). Pana kwa "
            "dirisha lenye shughuli; nyembamba ili ione kidhibiti "
            "kimoja cha katikati tu.",
        "desc.auto_click_repeat_px": "Baada ya bofyo la mojawa, "
            "lengo ndani ya pikseli hizi linaachwa (0-400). Bila "
            "hivyo kitufe kilichobaki skrini kingebofywa tena na "
            "tena.",
        "desc.auto_click_settle_ms": "Kishale kinapumzika hivyo "
            "kwenye lengo (0-2000 ms) kabla ya bofyo, ili programu "
            "ione mwangaza kwanza. 120 inafaa madirisha mengi.",
        "desc.block_bound_keys": "Zima (chaguo-msingi): kifupo "
            "kisicho na Ctrl/Alt/Shift - kama 1 au V - hufanya kazi "
            "katika kila programu NA huchapa kawaida, hivyo "
            "kukibonyeza katikati ya sentensi pia huwasha kitendo "
            "chake. Washa: kitendo bado huwasha kila mahali, lakini "
            "kifungo hakichapi tena.",
        "desc.capture_backend": "Jinsi skrini inavyopigwa picha. "
            "Otomatiki hutumia njia endelevu inayoona karibu dirisha zote; "
            "Inayooana hufanya kazi daima, ikiwemo Eneo la Kazi la "
            "Mbali na mashine pepe. Hutumika baada ya kuanzisha "
            "upya.",
        "desc.color_adapt": "Kila kipengee kinasawazishwa kwa weupe "
            "dhidi ya mandharinyuma yake kabla ya kulinganisha, ili "
            "mwanga wa usiku na rangi za mandhari zisiautoe rangi "
            "yako nje ya uvumilivu. Izime tu kwa kulinganisha na "
            "kilinganishi kisichorekebishwa.",
        "desc.contrast_threshold": "Chini hupata vipengele dhaifu "
            "zaidi (na kelele zaidi); juu huhitaji kingo zilizo wazi "
            "zaidi.",
        "desc.default": "Elekeza kishale juu ya jina la mpangilio "
            "kuona unachofanya.",
        "desc.exclude_color": "Vipengele vyenye rangi hizi havipati "
            "msaada kamwe: kubofya juu yao huenda moja kwa moja kwa "
            "Windows, katika hali zote mbili. Vinaonyeshwa kama "
            "visanduku vya rangi upande wa kulia - chagua rangi hapa "
            "chini na bonyeza «Ongeza zinazokataliwa» kuongeza moja "
            "(kumi na vitano vipeo); kubofya kisanduku huiondoa. "
            "Orodha tupu huonyesha kisanduku kilichopigwa msalaba na "
            "huzima mpangilio.",
        "desc.follow_boost": "Kipengee kilichokumbukwa hushinda sare "
            "kwa nguvu gani: 100% inaweza kudubulta alama yake ikiwa "
            "mbichi, 25% ni kusukuma kidogo.",
        "desc.follow_enabled": "Baada ya kunasa kwa mafanikio, "
            "vipengele vinavyofanana au mahali pale pale hushinda "
            "kwa muda - vizuri kwa miamba ya kubiringiza na mabofyo "
            "yanayorudiwa kwenye kidhibiti kimoja.",
        "desc.follow_learn": "Vipengele vya rangi yangu pekee: bofi "
            "la kukosa haliwezi kubadilisha kumbukumbu. Kila kunasa "
            "kwa mafanikio: tabia ya zamani ya kuamini.",
        "desc.follow_seconds": "Sekunde ambazo kipengee "
            "kilichokumbukwa hubaki kipendelewa baada ya kunasa "
            "kwako kwa mafanikio (1-120).",
        "desc.glide_ms": "0 (chaguo-msingi) huruka papo hapo - "
            "haraka zaidi. 40-120 huteleza ili uweze kuangalia; "
            "kusogeza kipanya mwenyewe huhairisha kuteleza.",
        "desc.hold_follow": "Unaposhikilia kifungo cha kushoto mara "
            "baada ya kunasa - au kubonyeza tena kwenye kipengee "
            "kilichokumbukwa - kishale hubaki kwenye rangi ya "
            "kipengee hicho; huu hutuliza kuburura kama vidokezi vya "
            "mwamba wa kubiringiza. Mabonyezo mahali pengine "
            "hayagusiwi.",
        "desc.key_launch": "Muundo: ctrl+l, f5, space, ctrl+alt+1 "
            "... Vibadilishaji: ctrl, alt, shift, win. Hutumika "
            "baada ya Tumia.",
        "desc.key_mode1": "Zikitenganishwa kwa koma, mf. '1, f1, "
            "ctrl+f1, v'. Hali ya kawaida inafanya nini huelezwa na "
            "kichupo cha Vifupo.",
        "desc.key_mode2": "Zikitenganishwa kwa koma, mf. '2, f2, "
            "ctrl+f2, b'. Hali ya kuongoza inafanya nini huelezwa na "
            "kichupo cha Vifupo.",
        "desc.key_pause": "Kipanya na kibodi vyarudia kuwa vyako "
            "kabisa, mpaka uanze.",
        "desc.key_play": "Hucheza rekodi iliyochaguliwa kwenye "
            "orodha ya Makro, au mpya zaidi kama hakuna "
            "iliyochaguliwa. Kwenye rekodi inayorudia, huisimamisha.",
        "desc.key_play_n": "Hucheza rekodi #%d ya orodha yenye namba "
            "katika kichupo cha Makro, kwa nafasi yake. Orodha ikiwa "
            "fupi, hakuna kitu kitakachotokea.",
        "desc.key_record": "Hukamata kila kitu unachofanya - kila "
            "kifungo, kila bofyo la kipanya na kila mwendo wa "
            "kishale - huku ingizo lako bado likifikia programu "
            "zako, hadi kifupo cha kusimamisha kilihifadhi kwenye "
            "orodha ya Makro. Hupandwa tu wakati imeanzishwa.",
        "desc.key_record_stop": "Husimamisha ukamataji, huhifadhi "
            "mfululizo kwenye orodha ya Makro na husimamisha "
            "uchezaji unaosogea.",
        "desc.luminance_norm": "Kingo hupimwa dhidi ya mwangaza wa "
            "mazingira yake, hivyo mandhari meusi hutenda kama "
            "meyepesi. Inapendekezwa kuwasha.",
        "desc.macro_action": "Mchanganyiko unaobonyezwa kwako kwa "
            "kila shinikizo la kiwasha (shinikizo moja = "
            "mchanganyiko moja): 'ctrl+c', 'ctrl+shift+s', 'space', "
            "'f5' ... Tupu = makro imezimwa.",
        "desc.macro_key": "Kifungo kinachomaanisha makro badala ya "
            "kuchapa: 'b', 'f7', 'ctrl+b' ... Imeanzishwa, shinikizo "
            "moja hutuma mchanganyiko ulio kando mara moja hasa na "
            "kifungo hakifiki programu zako. Imepumzika, huchapa "
            "kawaida. Tupu = makro imezimwa.",
        "desc.max_area": "Madoa makubwa hupuuzwa - mara nyingi ni "
            "madirisha mazima au mandharinyuma, si vipengele "
            "vinavyobofywa.",
        "desc.max_dim": "Vipengele vipana au virefu kuliko hivi "
            "hupuuzwa; vile vinavyogusa ukingo wa skrini, kama "
            "miamba ya kubiringiza, hupewa mara mbili.",
        "desc.merge_distance": "Vipande vilivyo karibu kuliko hivi "
            "(mzingo uliovunjika, ikoni kando ya lebo yake) huwa "
            "kipengee kimoja. Vipengee viwili kamwe havibandikwi.",
        "desc.min_area": "Madoa madogo hupuuzwa kama tone, isipokuwa "
            "yabandikwe kwenye kipengee kikubwa.",
        "desc.min_contrast": "Kipengee lazima kiwe angalau hivi wazi "
            "kiweze kubofywa kabisa. Thamani chini ya 28 huhesabiwa "
            "kama 28: kiwango cha ubora kilichojengewa ndani "
            "kinazuia kelele zisibofyeke.",
        "desc.motion_3d": "Hufuatilia vipengee vinavyosogea kwa "
            "nafasi NA ukubwa badala ya mstari ulionyooka: skani "
            "mbaya moja hupuuzwa badala ya kupofusha kifuatiliaji, "
            "kona hufuatwa, na mruko wa ghafla wa ukubwa huanzisha "
            "upya wimbo (kichunguzi kimechukua kipengee kingine). "
            "Vizingiti vile vile vya kasi, kikomo kile kile cha px "
            "80 - akili tu zinabadilika. Hufanya kazi yenyewe.",
        "desc.motion_lead_ms": "Milisekunde za msogeo za kutangulia "
            "kipengee kinachosogea (0-300): 40-80 kwa kubiringiza "
            "taratibu, 100-150 kwa pau za haraka. Kikomo cha px 80, "
            "huzimika kwa msogeo taratibu au unaogeuka.",
        "desc.motion_predict": "Kwa vipengele vinavyosogea "
            "unapobofya (orodha zinazobiringika, pau za video), "
            "hulenga kidogo mbele ili bofi liweke juu ya kipengee. "
            "Vipengele vivyotu havibadiliki.",
        "desc.mouse2_action": "Bofi fupi la kulia linachofanya ZAIDI "
            "- bofi la kulia lenyewe huhifadhi daima kazi yake ya "
            "kawaida ya Windows. Chaguo-msingi: hakuna.",
        "desc.mouse2_hold_action": "Chaguo zile zile, huwashwa "
            "unapOSHIKILIA kifungo cha kulia kwa takriban nusu "
            "sekunde badala ya kubofya. Shinikizo moja ni bofi au "
            "kushikilia, kamwe si vyote. Chaguo-msingi: hakuna.",
        "desc.on_target_dist": "Bofyo lako likianguka ndani ya "
            "pikseli hizi kutoka katikati ya kipengee, hakuna "
            "kinachosogea - umepata.",
        "desc.radius": "Umbali wa kutafuta kwa pikseli (40-400). "
            "Pandisha ikiwa kipengee unachotaka kiko nje kabisa ya "
            "ufikivu; punguza ikiwa jirani mbaya anashinda.",
        "desc.rapid_click_snap": "Zima (chaguo-msingi): bofi "
            "linachakatwa mengine huenda kwa Windows. Washa: kila "
            "bofi la kushoto husaidiwa.",
        "desc.snap_offset_x": "Husogeza mahali pa kubofya kando "
            "kutoka katikati ya kipengee (-200 hadi 200, hasi "
            "inaenda kushoto). Kwa kidhibiti chenye katikati "
            "iliyokufa - kitufe kilichogawanyika, slaidi - elekeza "
            "bofyo mahali penye uhai mara moja badala ya kupambana "
            "kila snap.",
        "desc.snap_offset_y": "Husogeza mahali pa kubofya wima "
            "kutoka katikati ya kipengee (-200 hadi 200, hasi "
            "inaenda juu). Kama usogezaji wa kando: tua kwenye "
            "sehemu hai ya kidhibiti.",
        "desc.stall_pause_seconds": "Uchanganuzi ukisita, usaidizi "
            "hupumzika kwa muda huu na bofi lolote lililoshikiliwa "
            "hukurejeshewa.",
        "desc.watcher_seconds": "Katika hali ya kawaida, kunasa kwa "
            "pili karibu na mahali pale pale ndani ya muda huu huwa "
            "bofi mara mbili juu ya kipengee.",
        "ent.cancel_line": "hai hadi %s - HAITAFUPISHWA",
        "ent.canceled_line": "usajili umeisha%s",
        "ent.expired_line": "imeisha %s - fupisha kwenye Stripe",
        "ent.past_due_line": "malipo yameshindikana - rekebisha kadi "
            "kwenye barua pepe ya risiti ya Stripe; ufikiaji hurudi "
            "ankara inapolipwa",
        "ent.plan": " (%s)",
        "ent.refunded_line": "imerejeshewa / kubishwaliwa - uwashaji "
            "umefutwa",
        "ent.st.active": "hai",
        "ent.st.canceled": "imekwisha",
        "ent.st.canceling": "hai lakini inafutwa",
        "ent.st.grant": "ruzuku ya usaidizi",
        "ent.st.past_due": "MALIPO YMESHINDIKANA",
        "ent.st.refunded": "imerejeshewa / kubishwaliwa",
        "ent.st.trial": "majaribio",
        "ent.st.unsubscribed": "hakuna usajili",
        "ent.until": " hadi %s",
        "err.auth_unreachable": "Seva ya uthibitisho ya Snappy AI "
            "haufikiki:\n%s\n\nSnappy AI hufanya kazi tu kwa jibu "
            "hai kutoka kwake.\nJaribu tena?",
        "err.start_fail": "Snappy AI imeshindwa kuanza.\nEndesha na "
            "--console kuona maelezo.",
        "gate.btn.monthly": "Usajili wa kila mwezi kwa 9,99€",
        "gate.btn.trial": "Ununuzi wa majaribio kwa 1,99€",
        "gate.head.canceled": "Usajili huu umefutwa - anzisha mpya "
            "kwenye Stripe kuendelea.",
        "gate.head.canceling": "Usajili wako umewekwa kufutwa - "
            "unabaki hai hadi %s, kisha kuingia huku hufungwa tena "
            "isipokuwa ufupishe.",
        "gate.head.email_mismatch": "Malipo lilifanywa kwa barua "
            "pepe tofauti na ile ya akaunti yako ya Discord. Usajili "
            "hufanya kazi kwenye barua pepe ya Discord inayoonyeshwa "
            "chini - jiandikishe tena nayo, au wasiliana na "
            "usaidizi.",
        "gate.head.expired": "Usajili wa kuingia huku umeisha - "
            "ufupishe kwenye Stripe kuendelea.",
        "gate.head.none": "Umeingia, lakini kuingia huku hakuna "
            "usajili hai. Lipa kwa barua pepe HII ya Discord - "
            "ununuzi kwenye anwani nyingine hauwezi kuiwasha.",
        "gate.head.past_due": "Malipo la mwisho la usajili "
            "limeshindikana - lilirekebishe kwenye Stripe kuwasha "
            "upya kuingia huku.",
        "gate.head.refunded": "Ununuzi huu ulirejeshewa au "
            "kubishwaliwa, hivyo uwashaji ulifutwa. Usajili mpya "
            "kwenye barua pepe hii ya Discord huwasha upya.",
        "gate.head.shared": "Akaunti hii inatumika SASA kwenye "
            "kompyuta NINGINE. Snappy AI hubaki kimezimwa wakati "
            "akaunti ile ile ya Discord inafanya kazi mahali pabili "
            "- funga kipindi kingine kisha kagua tena. Kushiriki "
            "usajili huinua bei; tafadhali usifanye.",
        "gate.msg.active": "Usajili hai - Snappy AI inaanza...",
        "gate.msg.checking": "Inakagua kwa seva...",
        "gate.msg.no_link": "Kiungo hicho cha malipo hakijasanidiwa "
            "kwenye jengo hili.",
        "gate.msg.open_fail": "Imeshindwa kufungua kivinjari. Fungua "
            "kiungo hiki kwa mkono:\n%s",
        "gate.msg.open_ok": "Stripe imefunguliwa katika kivinjari chako - lipa hapo. Dirisha hili lugha linajua malipo yenyewe na kuanza injini.",
        "gate.msg.session_gone": "Kipindi kimepotea - ingia tena.",
        "gate.msg.still_none": "Bado hakuna usajili hai kwa kuingia "
            "huku.",
        "gate.msg.still_shared": "Bado inatumika kwenye kompyuta "
            "nyingine - funga kipindi hicho kisha kagua tena.",
        "gate.msg.unreachable": "Seva ya uthibitisho haufikiki: %s",
        "gate.note": "Injini huanza usajili unapokuwa hai - dirisha "
            "hili hujikagua kila sekunde 30. Kufunga hukurudisha "
            "kwenye kuingia.",
        "gate.prices": "Majario ya siku 2: 1,99€ (mara moja)  -  "
            "usajili: 9,99€ / mwezi.\nUwashaji hufika hadi dakika "
            "~10 baada ya malipo; ufupishaji huwasha upya kuingia "
            "huku huko kivyake.",
        "gate.title": "%s - Usajili%s",
        "hdr.build": "jengo %s",
        "help.1.b": "Snappy AI huangalia skrini inayozunguka kishale "
            "chako, hupata vitu imara vyenye umbo la kipengee "
            "vilivyo karibu - vitufe, ikoni, viungo - na kuchagua "
            "bora zaidi: kingo wazi, ukubwa unaofaa na ukaribu na "
            "kishale hushinda. Rangi yako, orodha ya kamwe-usibofye "
            "na kumbukumbu ya bofyo lako la mwisho vinaweza "
            "kuinamisha uchaguzi. Kisha kishale hulenga katikati ya "
            "kipengee, si pembe ya sanduku lake.",
        "help.1.t": "Nini hutokea unapobofya",
        "help.10.b": "1. Je imeanzishwa? Kupumzika kunamaanisha "
            "hakuna kinachokamatwa - «Kifupo: anza usaidizi» "
            "(chaguo-msingi Ctrl+L) ndiyo washa/zima pekee.  2. "
            "Shikilia Shift kwa bofyo moja kuthibitisha kuwa tatizo "
            "lilikuwa usaidizi.  3. Kipengee kibaya kinashinda: "
            "punguza «Umbali wa kutafuta kutoka kishale», kisha weka "
            "«Rangi yangu» au pandisha «Nguvu ya faida ya rangi».  "
            "4. Hakuna kinachopatikana: punguza «Kingo inaweza kuwa "
            "dhaifu kiasi gani» na «Uwazi wa chini wa kingo», "
            "pandisha «Upana au urefu mkubwa» au «Bandika vipande "
            "vya karibu».  5. Kitu kisipaswe kusaidiwa kamwe: weka "
            "rangi yake katika «Rangi zisizoweza kubofywa kamwe».  "
            "6. Bado si sawa: eleza kwa huduma ya wateja ulichobofya "
            "na ulichotarajia, na ambatisha faili ya kumbukumbu "
            "inayohandikwa na Snappy AI katika folda yake ya data.",
        "help.10.t": "Kitu kikiwa si sawa, hakiki kwa mpangilio huu",
        "help.2.b": "Hali ya kuongoza (chaguo-msingi) hali bofyo "
            "lolote: bofyo lako hufika programu na, ukilifungua, "
            "kishale huenda kwenye kipengee safi cha karibu zaidi. "
            "Hali ya kawaida ni yenye nguvu zaidi: bofyo la kukosa "
            "karibu na kipengee hukamatwa, kishale hunasa na Snappy "
            "AI hubofya kwa ajili yako. «Umbali wa kutafuta kutoka "
            "kishale» huweka duara la kutafuta - pandisha ikiwa "
            "kipengee unachotaka kiko nje kidogo ya ufikivu, punguza "
            "ikiwa jirani mbaya anashinda. Kushikilia Shift huepuka "
            "bofyo moja katika hali zote mbili.",
        "help.2.t": "Anza hapa: hali na umbali wa kutafuta",
        "help.3.b": "Kwenye kichupo cha Uchakataji, «Kingo inaweza "
            "kuwa dhaifu kiasi gani» na «Uwazi wa chini wa kingo» "
            "huamua kingo zipi zinahesabika: chini hupata dhaifu "
            "zaidi, juu hupuuzia kelele. «Ukubwa mdogo wa kipengee», "
            "«Eneo kubwa la kipengee» na «Upana au urefu mkubwa» "
            "hutuosa tone na madirisha mazima. «Bandika vipande vya "
            "karibu» huunganisha mzingo uliovunjika, au ikoni kando "
            "ya lebo yake, kuwa kipengee kimoja. Kwenye kichupo cha "
            "Usaidizi, «Marekebisho otomatiki kwa skrini dhaifu» na "
            "«Kadiria kingo kwa mwangaza wa ulinganifu» hufanya "
            "mandhari meusi yatende kama meyepesi - vyaache vyote "
            "vikiwaka.",
        "help.3.t": "Hakuna kinachopatikana - au kinapatikana kingi",
        "help.4.b": "Kwenye kichupo cha Rangi, «Rangi yangu» ndiyo "
            "rangi inayopendelewa na «Rangi zisizoweza kubofywa "
            "kamwe» ni kamili: vipengee hivyo havisaidiwi kamwe. "
            "«Saidia rangi yangu pekee» huhadhibiti usaidizi kwa "
            "vipengele vinavyolingana. Katika Uchakataji, «Ukali wa "
            "ulinganifu wa rangi» hueleza kivuli kinapaswa kuwa "
            "karibu kiasi gani, «Kubali vivuli vinavyofanana» "
            "huruhusu matoleo yaliyo pepesi au kupauka kuhesabika "
            "kiasi, na «Nguvu ya faida ya rangi» hueleza rangi yako "
            "huinua kipengee kwa kiasi gani - ipandishe ikiwa "
            "kisicho sahihi bado kinashinda.",
        "help.4.t": "Kufanya kazi na rangi",
        "help.5.b": "«Kumbuka kipengee cha mwisho kilichobofywa» "
            "huendelea kupendelea kipengee ambapo bofyo lako la "
            "mwisho la mafanikio lilianguka, kwa sekunde za «Kumbuka "
            "kwa muda gani» - hii ndiyo inayofanya miamba ya "
            "kubiringiza na vitufe vya mazungumzo kuwa nafuu. «Nguvu "
            "ya kumbukumbu» hueleza inashinda kwa nguvu kiasi gani, "
            "na «Kumbukumbu inaweza kujifunza nini» huilinda: kwa "
            "«Vipengele vya rangi yangu pekee», bofyo la kukosa "
            "haliwezi kuibadilisha. «Fuata kipengee huku kifungo "
            "kikishikiliwa» hutuliza kuburura, na vitendo vya "
            "kifungo cha kulia vya Majaribio vinaweza kufuata au "
            "kufuta kumbukumbu kwa kipanya.",
        "help.5.t": "Mabofyo yanayorudiwa kwenye kidhibiti kimoja",
        "help.6.b": "«Tangulia vipengele vinavyosogea» hupima kasi "
            "ya kipengee kilichochaguliwa na kulenga mbele kwa "
            "milisekunde za «Kutangulia kwa umbali gani», ili bofyo "
            "lianguke kwenye orodha inayobiringika au pau ya video "
            "badala ya nyuma yake. Utangulizi una kikomo cha pikseli "
            "80 na hujizima wenyewe kwa vipengee vilivyotu au "
            "vinavyogeuka.",
        "help.6.t": "Kubofya vitu vinavyosogea",
        "help.7.b": "«Huishaji wa msogeo wa kishale» = 0 huruka papo "
            "hapo; 40-120 huteleza ili uweze kuangalia, na kusogeza "
            "kipanya mwenyewe huhairisha kuteleza. «Dirisha la bofi "
            "mara mbili» katika hali ya kawaida hugeuza kunasa kwa "
            "pili karibu na mahali pale pale kuwa bofi mara mbili. "
            "«Saidia kila bofi la mfululizo wa haraka» husaidia kila "
            "bofi la mfululizo badala ya la kwanza pekee. «Pumziko "
            "baada ya kusita» ni valivu ya usalama inayorejesha "
            "bofyo lililoshikiliwa uchanganuzi ukisita.",
        "help.7.t": "Mabofyo yanahisikaje",
        "help.8.b": "Kichupo cha Vifupo kinaeleza hali mbili na "
            "mtiririko wa kurekodi. Kwa kifupi: vifupo vyenye Ctrl, "
            "Alt, Shift au Win huhifadhiwa kwa mfumo mzima; vitufe "
            "pekee hufanya kazi kila mahali na bado huchapa. Makro "
            "hugeuza shinikizo moja la kifungo lililozuiwa kuwa "
            "mchanganyiko mzima. Rekodi hukamata ingizo lako halisi "
            "- kila kifungo, bofyo la kipanya na mwendo wa kishale - "
            "na kucheza kutoka kichupo cha Makro, kila moja ikiwa na "
            "swichi yake mwenyewe ya mara moja au kurudia hadi "
            "kusimamisha.",
        "help.8.t": "Vitufe, makro na rekodi",
        "help.9.b": "Kitufe cha Lugha kando ya «Toa mipangilio» - "
            "pia katika madirisha ya kuingia na ya usajili - "
            "hubadilisha kiolesura chote mara moja, bila kuanzisha "
            "upya, na kukumbuka chaguo lako. Lugha zinazoendelea "
            "kutafsiriwa hazitolewi, hivyo yoyote unayoweza kuchagua "
            "imekamilika.",
        "help.9.t": "Lugha",
        "help.sub": "Kila mpangilio kwa jina unaloliona kwenye "
            "kichupo chake, kwa mpangilio utakavyohitaji. Elekeza "
            "kishale juu ya jina kupata maelezo ya mstari mmoja; "
            "ukurasa huu ni umbo refu.",
        "help.tail": "Mipangilio hutumika unapobonyeza Tumia. "
            "config.ini kando ya programu huweka mbali config.json. "
            "Ukurasa huu hueleza; hausanidi.",
        "help.title": "Kurekebisha Snappy AI kwa maneno rahisi",
        "kb.keys.b": "Kifupo chenye Ctrl, Alt, Shift au Win "
            "kimehifadhiwa kwa mfumo mzima: Snappy AI pekee ndiyo "
            "huiona. Kifungo kimoja tupu (kama 1 au 2) hufanya kazi "
            "kwenye kila programu NA bado huchapa - gharama ni "
            "kwamba kukibonyeza katikati ya sentensi pia huwasha "
            "kitendo chake. Kwa tabia ya kawaida, washa «Vifupo vya "
            "kifungo kimoja humeza kifungo» kwenye kichupo cha "
            "Usaidizi. Makro huenda mbali zaidi: imeanzishwa, "
            "kifungo kiwasha humezwa na mchanganyiko ulio kando "
            "hutumwa mara moja hasa.",
        "kb.keys.t": "Vitufe vinavyojitegemea dhidi ya michanganyiko",
        "kb.mode.b": "Hali ya kuongoza (chaguo-msingi, kifupo 2): "
            "bofyo lako hufika programu bila kuguswa; ukilifungua "
            "kifungo, kishale huenda kwenye kipengee safi cha karibu "
            "zaidi, hivyo bofyo lako lijalo huanza hapo. Hakuna "
            "kinachomezwa kamwe - hali salimu zaidi.  Hali ya "
            "kawaida (kifupo 1): ukibofya karibu na kipengee, bofyo "
            "hilo la kukosa hukamatwa, kishale hunasa kwenye "
            "kipengee na Snappy AI hubofya kwa ajili yako; hakuna "
            "kitu karibu, bofyo lako hurejeshwa bila kuguswa.  "
            "Katika hali zote mbili, kushikilia Shift unapobofya "
            "huepuka usaidizi kwa bofyo hilo moja.",
        "kb.mode.t": "Hali mbili zinafanya nini",
        "kb.rec.b": "Wakati imeanzishwa, bonyeza kifupo chako cha "
            "kuanza kurekodi (Ctrl+Alt+R kwa chaguo-msingi): kila "
            "kifungo unachobonyeza, kila kitufe cha kipanya "
            "unachobofya na kila mwendo wa kishale huchukuliwa NA "
            "bado hufika programu zako, hivyo unaweza kufanya kazi "
            "kawaida wakati wa kurekodi. Bonyeza kifupo cha "
            "kusimamisha (Ctrl+Alt+S) kuihifadhi kwenye orodha ya "
            "kichupo cha Makro - rekodi tano zinatosha hapo. Bofya "
            "rekodi ili kuichagua, «Badilisha jina» au «Toa», na "
            "kuweka swichi yake mwenyewe ya «Rudia hadi "
            "kusimamisha». Kifupo cha kucheza (Ctrl+Alt+M) hucheza "
            "rekodi iliyochaguliwa hapo; Ctrl+1 hadi Ctrl+5 hucheza "
            "kwa nafasi katika orodha. Ikiwa imesitishwa, hakuna "
            "kinachorekodiwa wala kuingizwa - ingizo lako ni lako "
            "kabisa.",
        "kb.rec.t": "Jinsi ya kurekodi na kucheza vitufe na shughuli "
            "zako za kipanya",
        "lang.close": "Funga",
        "lang.coverage": "Imetafsiriwa %d%%",
        "lang.current": "Ya sasa: %s",
        "lang.progress": "Bado inatafsiriwa, itatolewa ikikamilika: "
            "%s",
        "lang.prompt": "Badiliko hufanya kazi mara moja; dirisha "
            "hubaki wazi kujaribu kadhaa.",
        "lang.title": "Lugha",
        "lbl.accent_boost": "Nguvu ya faida ya rangi",
        "lbl.accent_coherent": "Puuza vidoti vya rangi "
            "vilivyotawanyika",
        "lbl.accent_color": "Rangi yangu",
        "lbl.accent_matcher": "Injini ya ulinganishaji wa rangi",
        "lbl.accent_only": "Saidia rangi yangu pekee",
        "lbl.accent_soft": "Kubali vivuli vinavyofanana",
        "lbl.accent_tolerance": "Ukali wa ulinganifu wa rangi",
        "lbl.accent_variants": "Hali angavu na nyeusi za rangi yangu",
        "lbl.adaptive_threshold": "Marekebisho otomatiki kwa skrini "
            "dhaifu",
        "lbl.auto_click": "Bofya vitu vyenyewe",
        "lbl.auto_click_interval": "Sekunde kati ya mibofyo ya "
            "mojawa",
        "lbl.auto_click_max_clicks": "Kipimo cha mibofyo ya mojawa "
            "kwa kikao",
        "lbl.auto_click_min_contrast": "Usha wa lengo la lengo la "
            "mojawa",
        "lbl.auto_click_radius": "Tafuta kutoka katika kati ya "
            "skrini",
        "lbl.auto_click_repeat_px": "Usibofye mahali pale tena",
        "lbl.auto_click_settle_ms": "Pauza kabla ya mibofyo ya "
            "mojawa",
        "lbl.block_bound_keys": "Vifupo vya kifungo kimoja humeza "
            "kifungo",
        "lbl.capture_backend": "Injini ya kunasa skrini",
        "lbl.color_adapt": "Endana na mwanga wa skrini",
        "lbl.contrast_threshold": "Kingo inaweza kuwa dhaifu kiasi "
            "gani",
        "lbl.exclude_color": "Rangi zisizoweza kubofywa kamwe",
        "lbl.follow_boost": "Nguvu ya kumbukumbu",
        "lbl.follow_enabled": "Kumbuka kipengee cha mwisho "
            "kilichobofywa",
        "lbl.follow_learn": "Kumbukumbu inaweza kujifunza nini",
        "lbl.follow_seconds": "Kumbuka kwa muda gani",
        "lbl.glide_ms": "Huishaji wa msogeo wa kishale",
        "lbl.hold_follow": "Fuata kipengee huku kifungo "
            "kikishikiliwa",
        "lbl.key_launch": "Kifupo: anza usaidizi",
        "lbl.key_mode1": "Kifupo: hali ya kawaida (hadi vitufe 4)",
        "lbl.key_mode2": "Kifupo: hali ya kuongoza (hadi vitufe 4)",
        "lbl.key_pause": "Kifupo: pumzika",
        "lbl.key_play": "Kifupo: cheza rekodi iliyochaguliwa",
        "lbl.key_play_n": "Kifupo: cheza rekodi #%d",
        "lbl.key_record": "Kifupo: anza kurekodi",
        "lbl.key_record_stop": "Kifupo: simamisha na huhifadhi "
            "rekodi",
        "lbl.luminance_norm": "Kadiria kingo kwa mwangaza wa "
            "ulinganifu",
        "lbl.macro_action": "Makro %d: inatuma badala yake",
        "lbl.macro_key": "Makro %d: bonyeza kifungo hiki",
        "lbl.max_area": "Eneo kubwa la kipengee",
        "lbl.max_dim": "Upana au urefu mkubwa wa kipengee",
        "lbl.merge_distance": "Bandika vipande vya karibu",
        "lbl.min_area": "Ukubwa mdogo wa kipengee",
        "lbl.min_contrast": "Uwazi wa chini wa kingo",
        "lbl.motion_3d": "Ufuatiliaji bora wa vitu vinavyosogea",
        "lbl.motion_lead_ms": "Kutangulia kwa umbali gani",
        "lbl.motion_predict": "Tangulia vipengele vinavyosogea",
        "lbl.watch_center_only": "Fuatilia katikati ya skrini pekee",
        "desc.watch_center_only": "Usaidizi huangalia mraba uliotulia katikati ya skrini (ukubwa = "
            "umbali wa utafutaji, chaguo-msingi 150×150 px) bila kujali "
            "kiashiria kiko. Bofyo nje ya mraba huo hubaki vilevile.",
        "lbl.center_follow": "Skrini ifuate lengo",
        "desc.center_follow": "«Fuatilia katikati ya skrini pekee» ikiwa washa: baada ya kitu "
            "kushikwa, usaidizi husogeua skrini ili kikaa katikati hasa kwa "
            "ndege zinazosogea. Sofisha skrini wewe mwenyewe kuachilia "
            "ufuataji.",
        "lbl.input_backend": "Njia ya ingizo",
        "desc.input_backend": "Uingizaji wa Windows (chaguo-msingi) hufanya kila mahali. "
            "Interception hutuma kupitia kiendeshi na michezo huitambua kama "
            "panya halisi; inahitaji kiendeshi cha Interception kilichowekwa na "
            "interception.dll karibu na programu; vinginevyo hutumia uingizaji "
            "wa Windows kiotomatiki.",
        "val.input_backend.win32": "Uingizaji wa Windows",
        "val.input_backend.interception": "Interception (kiendeshi)",
        "lbl.mouse2_action": "Kitendo cha ziada cha bofi la kulia",
        "lbl.mouse2_hold_action": "Kitendo cha kushikilia kulia",
        "lbl.on_target_dist": "Umbali wa «tayari nimepata»",
        "lbl.radius": "Umbali wa kutafuta kutoka kishale",
        "lbl.rapid_click_snap": "Saidia kila bofi la mfululizo wa "
            "haraka",
        "lbl.snap_offset_x": "Mahali pa kubofya: kushoto / kulia",
        "lbl.snap_offset_y": "Mahali pa kubofya: juu / chini",
        "lbl.stall_pause_seconds": "Pumziko baada ya kusita",
        "lbl.watcher_seconds": "Dirisha la bofi mara mbili",
        "login.failed": "Kuingia kwa %s hakukukamilika - jaribu "
            "tena.",
        "login.no_provider": "Nakili hii haina mtoaji wa kuingia "
            "uliojengwa ndani.",
        "login.not_configured": "Faili la usajili halijasanidiwa "
            "kwenye jengo hili bado.",
        "login.note": "Kuingia hufungua kivinjari chako na kurudi "
            "kwenye dirisha hili kivyake.",
        "login.provider": "Ingia kwa %s",
        "login.signedin": "Umeingia kama %s.",
        "login.sub": "Ingia kwa Discord - usajili wako umeunganishwa "
            "kwenye akaunti hii, na malipo lazima matumie barua pepe "
            "yake. Hapana nenosiri hapa.",
        "login.title": "%s - Ingia",
        "login.unreachable": "Seva ya uthibitisho haufikiki: %s",
        "login.waiting": "Inasubiri kivinjari - maliza kuingia kwa "
            "%s...",
        "mac.delete": "Futa",
        "mac.empty": "Hakuna rekodi bado - anzisha, bonyeza kifupo "
            "chako cha kurekodi na fanya kazi kawaida: kila kifungo, "
            "bofyo na mwendo wa kishale huchukuliwa.",
        "mac.export": "Toa",
        "mac.import": "Ingiza",
        "mac.keys_head": "Mikro za vitufe",
        "mac.loop": "Rudia hadi kusimamisha",
        "mac.recordings": "Rekodi",
        "mac.rename": "Badilisha jina",
        "mac.row": "Makro %d",
        "mac.sends": "inatuma",
        "mac.steps": "hatua %d",
        "note.advanced": "Mipangilio ya umbali na muda "
            "inayobadilisha jinsi mabofyo yanavyohisika, si "
            "kinachopatikana. Watu wengi hawahitaji kuivuta; "
            "chaguo-msingi ndizo zilizojaribiwa.",
        "note.assist": "Kila swichi inayobadilisha tabia wakati "
            "imeanzishwa. Hali mbili hubadilishwa kwa vitufe vyako "
            "vya hali - kichupo cha Vifupo hueleza kila hali "
            "inachofanya. Usaidizi huanza daima ukiwa umepumzika; "
            "Anza ndiyo washa/zima pekee. Injini inaangalia wapi na "
            "mabofyo yanahisikaje viko Kina kina; kinachohesabika "
            "kipengee kiko Uchakataji.",
        "note.colors": "Orodha mbili za juu huchagua rangi zipi "
            "Snappy AI hupendelea au kukataa. Kila moja huonyesha "
            "rangi zake kama visanduku upande wa kulia, kumi na "
            "vitano vipeo, na kubofya kisanduku huondoa rangi hiyo "
            "tena; orodha tupu huonyesha kisanduku kilichopigwa "
            "msalaba na huhesabika kimezimwa. «Ongeza "
            "zinazopendelewa» na «Ongeza zinazokataliwa» huweka "
            "rangi iliyopo kwenye kichanganyaji kwenye orodha "
            "inayolingana. Thamani ya RGB ya sasa huonyesha "
            "visanduku vitatu - kila kimoja ni kipana kama visanduku "
            "vitano vya rangi, hivyo mstari huu unatanda visanduku "
            "vile vile kumi na vitano kama kila kitu chini yake - "
            "vinavyong'aa kwa kiasi cha nyekundu, kijani na buluu "
            "kilichopo kwenye rangi ya kichanganyaji; mstari huu "
            "hufuata kichanganyaji na hauwezi kuchapishwa. "
            "Kichanganyaji kilicho chini huchanganya rangi kama "
            "programu ya uchoraji; kila kitu kilicho kando yake "
            "kikaa upande wa kulia wa dirisha, kwa nafasi ile ile "
            "hadi ukingo kama mipangilio ya juu, na kila mstari "
            "unatanda upana ule ule wa visanduku kumi na vitano: "
            "kioo kirefu chenye #thamani yake kuchorwa ndani, kisha "
            "toni kumi na tano tayari, vitufe viwili vya kuongeza na "
            "mstari wa skrini - «Chukua rangi kutoka skrini» "
            "huchukua rangi moja chini ya kishale, «Pendekeza rangi "
            "za skrini» hujaza visanduku vyake kumi na vitano kwa "
            "rangi anazozipata kuzunguka kishale, na kubofya kimoja "
            "hukupakia kwenye kichanganyaji. Kioo ni kirefu "
            "makusudi: hivyo visanduku vya mapendekezo huishia sawa "
            "kabisa na kitelezi cha rangi upande wa kushoto.",
        "note.experimental": "Chaguo za injini, kila moja ikiwa na "
            "chaguo-msingi lililojaribiwa. Zibadilishe tu "
            "unapolinganisha injini, kwenye vifaa visivyo vya "
            "kawaida, au usaidizi unapoomba - injini ya kunasa "
            "hutumika baada ya kuanzisha upya.",
        "note.handler": "Kinachohesabika kipengee kinachobofywa: "
            "kingo inaweza kuwa dhaifu kiasi gani, lazima iwe wazi "
            "kiasi gani, na kipengee kinaweza kuwa kikubwa au kidogo "
            "kiasi gani. Hakuna kinachopatikana? Legeza thamani "
            "hizi. Kimepatikana kisicho sahihi? Zikaze, au tumia "
            "rangi yako kwenye kichupo cha Rangi.",
        "note.keybindings": "Kila kifupo - na chini yake, hali mbili "
            "zinafanya nini, jinsi ya kurekodi vitufe na shughuli "
            "zako za kipanya, na kifungo kimoja kinatofautiana vipi "
            "na mchanganyiko.",
        "note.macros": "Makro hugeuza shinikizo moja la kifungo kuwa "
            "mchanganyiko mzima wakati imeanzishwa. Kando ya makro, "
            "rekodi zako: hadi tano zenye majina za kila kitu "
            "ulichofanya - kila kifungo, bofyo la kipanya na mwendo "
            "wa kishale - zinazochezwa kama zilivyorekodiwa. Bofya "
            "rekodi ili kuichagua; kila mstari una swichi yake "
            "mwenyewe ya «Rudia hadi kusimamisha», na «Badilisha "
            "jina», «Toa», «Ingiza» na «Futa» ziko chini ya sanduku.",
        "note.macros_keys": "Vifupo vya kurekodi/kucheza viko kwenye "
            "kichupo cha Vifupo (chaguo-msingi: Ctrl+Alt+R rekodi, "
            "Ctrl+Alt+S simamisha na huhifadhi, Ctrl+Alt+M cheza, "
            "Ctrl+1..5 cheza kwa nafasi).",
        "online.cancelled": "Uthibitisho wa Discord umeghairiwa (au "
            "umeshindikana). Tafadhali jaribu tena.",
        "rec.export_fail": "Kutoa kumeshindikana: %r",
        "rec.exported": "Imetolewa kwenda %s",
        "rec.import_fail": "Kuingiza kumeshindikana: %r",
        "rec.imported": "Rekodi %d zimeingizwa%s.",
        "rec.imported_none": " (hakuna iliyokuwa sahihi)",
        "rec.no_sel": "Hakuna kilichochaguliwa cha kutoa.",
        "rec.notfile": "Kuingiza kumeshindikana: si faili la rekodi.",
        "shared.back": "Karibu tena - bonyeza Anza ukiwa tayari.",
        "shared.body": "Akaunti hii ya Discord inaendesha Snappy AI "
            "kwenye kompyuta nyingine sasa hivi.\nUsaidizi "
            "umesimamishwa hapa hadi kipindi kimoja "
            "kibaki.\n\nUsajili mmoja, mashine moja kwa wakati - "
            "ndiyo inayoshikilia\nbei chini na maendeleo ikiendelea.",
        "shared.close": "Funga",
        "shared.recheck": "Kagua sasa",
        "shared.still": "Bado inatumika mahali pengine - tunabaki "
            "tumepumzika.",
        "shared.title": "Akaunti inatumika mahali pengine",
        "shared.unreachable": "Seva haufikiki - tutakagua tena.",
        "st.all_files": "Faili zote",
        "st.color_added": "rgb(%d, %d, %d) imeongezwa kwenye %s - "
            "Tumia huhifadhi.",
        "st.color_already": "rgb(%d, %d, %d) tayari iko katika %s.",
        "st.color_full": "%s tayari ina rangi 15 - bofya kwanza "
            "kimoja cha visanduku vyake kuondoa rangi.",
        "st.color_removed": "rgb(%d, %d, %d) imeondolewa kutoka %s - "
            "Tumia huhifadhi.",
        "st.delete_confirm": "Ufute rekodi %r?\nHii haiwezi "
            "kutenduliwa.",
        "st.deleted": "Rekodi imefutwa.",
        "st.engine_dead": "Uzi wa injini haupatikani - vifupo "
            "havijibu.",
        "st.ent_paused": "Usajili %s - usaidizi umepumzika. Fupisha "
            "kwenye Stripe, kisha anzisha upya.",
        "st.ent_unreachable": "Ukaguzi wa usajili: seva haufikiki "
            "(kipindi kinaendelea).",
        "st.export_fail": "Kutoa kumeshindikana: %r",
        "st.export_rec_title": "Toa rekodi",
        "st.export_title": "Toa mipangilio",
        "st.exported": "Mipangilio imetolewa kwenda %s",
        "st.file_rec": "Rekodi ya Snappy AI",
        "st.file_settings": "Mipangilio ya Snappy AI",
        "st.follow": "  |  kufuata sekunde %d zilizopita",
        "st.import_fail": "Kuingiza kumeshindikana: %r",
        "st.import_notfile": "Kuingiza kumeshindikana: si faili la "
            "mipangilio.",
        "st.import_rec_title": "Ingiza rekodi",
        "st.import_title": "Ingiza mipangilio",
        "st.imported": "Mipangilio %d imeingizwa%s.",
        "st.imported_ignored": ", imepuuzwa: %s",
        "st.ini_over": "Imetumika, lakini config.ini inaweka mbali: "
            "%s",
        "st.lib_empty": "Orodha iko tupu - hakuna cha kutoa.",
        "st.line": "Imesaidia %d  |  imepita %d%s  |  mandhari: %s",
        "st.loop_desc": "Mtindo wa uchezaji wa rekodi HII: zima = "
            "inacheza mara moja; washa = inarudia hadi ubonyeze tena "
            "kifupo cha kucheza. Kila rekodi ina swichi yake "
            "mwenyewe, huhifadhiwa pamoja na rekodi yenyewe.",
        "st.name_empty": "Jina haliwezi kuwa tupu.",
        "st.pick_err": "Kuchukua kumeshindikana: %r",
        "st.pick_fail": "Kuchukua kumeshindikana - jaribu tena.",
        "st.pick_ok": "Imechukuliwa rgb(%d, %d, %d) kwa (%d, %d).",
        "st.pick_wait": "Peleka kishale kwenye rangi - inachukuliwa "
            "baada ya sekunde 3...",
        "st.preset_desc": "Toni tayari: %s - bofya kuipakia kwenye "
            "kichanganyiko.",
        "st.rec_count": "Rekodi %d kati ya 5",
        "st.rec_now": "%r sasa: %s.",
        "st.rec_once": "inacheza mara moja",
        "st.rec_playing": "Inacheza %r...",
        "st.rec_playing_loop": "Inacheza %r hadi kusimamisha",
        "st.rec_recording": "INAREKODI - %s husimamisha na kuhifadhi",
        "st.rec_repeats": "rudia hadi kusimamisha",
        "st.registered": "Imesajiliwa kwa: %s    Hali: %s",
        "st.rename_prompt": "Jina jipya la rekodi #%d:",
        "st.renamed": "Rekodi imebadilishwa jina.",
        "st.reset_confirm": "Urudishe mipangilio yote kwa "
            "chaguo-msingi?\nAkaunti huhifadhiwa; hii hugusa "
            "mipangilio tu.",
        "st.rgb_bad": "Weka kwanza thamani sahihi za R/G/B.",
        "st.running": "Inafanya kazi..",
        "st.saved": "Imehifadhiwa na kutumika.",
        "st.defaults_restored": "Chaguo-msingi zimerejeshwa.",
        "st.saved_bad": "Imehifadhiwa, lakini si sahili (ya zamani "
            "inabaki): %s",
        "st.select_rec": "Chagua rekodi kwanza.",
        "st.shared_paused": "AKAUNTI INATUMIKA MAHALI PENGINE - "
            "usaidizi umepumzika; usajili mmoja = mashine moja.",
        "st.standby": "Imesimama..",
        "st.sug_fail": "Pendekezo limeshindikana: %r",
        "st.sug_loaded": "Pendekezo rgb(%d, %d, %d) lipo kwenye "
            "kichanganyaji - liliongeze kwenye orodha kwa vitufe vya "
            "juu.",
        "st.sug_loaded_desc": "Rangi ya kiolesura iliyopendekezwa "
            "rgb(%d, %d, %d) - %d%% ya eneo lililochukuliwa. Bofya "
            "kuipakia kwenye kichanganyiko.",
        "st.sug_none": "Hakuna mapendekezo ya rangi kutoka eneo "
            "hili.",
        "st.sug_ok": "Mapendekezo %d - bofya moja ili kulipakia "
            "kwenye kichanganyaji.",
        "st.sug_wait": "Elekeza kwenye programu unayofanya kazi - "
            "inachukuliwa baada ya sekunde 3...",
        "tab.advanced": "Kina kina",
        "tab.assist": "Usaidizi",
        "tab.colors": "Rangi",
        "tab.experimental": "Majaribio",
        "tab.handler": "Uchakataji",
        "tab.help": "Msaada",
        "tab.hotkeys": "Vifupo",
        "tab.macros": "Makro",
        "theme.dark": "Giza",
        "theme.light": "Mwanga",
        "val.accent_matcher.hsv": "Ya kale - injini ya zamani",
        "val.accent_matcher.oklab": "Ya kuona - jinsi rangi "
            "zinavyoonekana (inapendekezwa)",
        "val.capture_backend.auto": "Otomatiki - ya haraka zaidi "
            "yenye chepuo salama",
        "val.capture_backend.dxcam": "Desktop Duplication - ya "
            "haraka zaidi kwa PC nyingi",
        "val.capture_backend.mss": "Inayooana - hufanya kazi daima "
            "(Remote Desktop, VM)",
        "val.capture_backend.wgc": "Windows Graphics Capture - ya "
            "majaribio",
        "val.follow_learn.accent": "Vipengele vya rangi yangu pekee",
        "val.follow_learn.any": "Kila kunasa kwa mafanikio",
        "val.mouse2_action.1": "Futa kazi ya kufuata ya sasa",
        "val.mouse2_action.2": "Fuata rangi ya mwisho iliyonaswa",
        "val.mouse2_action.3": "Chukua rangi chini ya kishale kisha "
            "uifuate",
        "val.mouse2_action.4": "Usifanye chochote",
        "val.mouse2_hold_action.1": "Futa kazi ya kufuata ya sasa",
        "val.mouse2_hold_action.2": "Fuata rangi ya mwisho "
            "iliyonaswa",
        "val.mouse2_hold_action.3": "Chukua rangi chini ya kishale "
            "kisha uifuate",
        "val.mouse2_hold_action.4": "Usifanye chochote",
        "word.off": "Zima",
        "word.on": "Washa",
    },

}

_current = FALLBACK
_ALL_KEYS = []          # registered by the GUI; drives coverage %


def codes():
    """Every selectable language code, chooser order."""
    return [code for code, _native, _eng in LANGUAGES]


def native_name(code):
    for c, native, _eng in LANGUAGES:
        if c == code:
            return native
    return code


def english_name(code):
    for c, _native, eng in LANGUAGES:
        if c == code:
            return eng
    return code


def publish(code, mapping):
    """Merge strings into a catalog. The GUI publishes its English
    prose (notes, Help, explanations, dialogs) this way, so the English
    source of truth stays readable in gui.py next to the widgets it
    describes, while every other locale overrides by key."""
    STRINGS.setdefault(code, {}).update(mapping)


def register_keys(keys):
    """The GUI's complete key list, so coverage() can be honest."""
    global _ALL_KEYS
    _ALL_KEYS = list(keys)


def coverage(code):
    """0..1: share of the registered keys this locale actually has.
    English is the source of truth: whatever it does not carry, the GUI
    falls back to (META labels, descriptions), so it is always full.
    v8.67: before register_keys() runs there is no key universe to
    measure - report 0.0 (NOT complete) instead of the old misleading
    1.0, which made every locale look fully translated and offered the
    entire language list to anything asking during early startup."""
    if code == FALLBACK:
        return 1.0
    if not _ALL_KEYS:
        return 0.0
    cat = STRINGS.get(code, {})
    hit = sum(1 for k in _ALL_KEYS if k in cat)
    return hit / float(len(_ALL_KEYS))


def is_complete(code):
    """True when the locale carries EVERY registered string.

    v8.40 rule from the owner: a language is offered only when it is
    100% done, so nobody can switch into a half-translated interface.
    English is the source and therefore always complete."""
    return code == FALLBACK or coverage(code) >= 1.0


def offered_codes():
    """Selectable languages, chooser order."""
    return [c for c in codes() if is_complete(c)]


def in_progress():
    """(code, coverage) of locales still being translated."""
    return [(c, coverage(c)) for c in codes() if not is_complete(c)]


def diagnose():
    """Why is a locale not offered? -> [(code, coverage, [missing keys])].

    v8.49. The 100% rule is a hair trigger, and before this the failure was
    invisible: `is_complete()` withholds a language from the chooser, so a
    SINGLE English string that no locale carries - typically one left behind
    in gui.py's PROSE dict when a widget was redesigned - quietly removes all
    fifteen translations from the product. Nothing crashes, the chooser just
    shows English, and the reason is a key nobody displays.

    Called from run_gui() right after register_keys(), and logged, so the
    drift surfaces on the first run of a new build instead of as a support
    thread about "the language button only has English"."""
    out = []
    for code in codes():
        if code == FALLBACK:
            continue
        cov = coverage(code)
        if cov >= 1.0:
            continue
        cat = STRINGS.get(code, {})
        missing = sorted(k for k in _ALL_KEYS if k not in cat)
        out.append((code, cov, missing))
    return out


def english_only_keys():
    """Registered keys the English catalog carries that NO other locale has.

    The signature of a stale PROSE entry: English gained a string when a
    widget was rewritten, the translations were never asked for it, and every
    locale is now incomplete because of a key nothing may ever render."""
    others = set()
    for code, cat in STRINGS.items():
        if code != FALLBACK:
            others |= set(cat)
    return sorted(k for k in _ALL_KEYS
                  if k in STRINGS.get(FALLBACK, {}) and k not in others)


def current():
    return _current


def set_language(code):
    """Switch the live language. Incomplete or unknown codes fall back
    to English instead of showing a mixed interface."""
    global _current
    _current = code if code in offered_codes() else FALLBACK
    return _current


def L(key, *args):
    """Translated string; catalog -> English -> the key itself."""
    text = STRINGS.get(_current, {}).get(key)
    if text is None:
        text = STRINGS[FALLBACK].get(key)
    if text is None:
        return key
    if args:
        try:
            return text % args
        except (TypeError, ValueError):
            return text
    return text
