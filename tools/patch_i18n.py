# -*- coding: utf-8 -*-
"""One-shot i18n patcher.

Adds the 8 keys every locale is missing (watch_center_only, center_follow,
input_backend labels/descriptions + backend option values), refreshes the
auto-click label/description to the new 0.1 s contrast-first behaviour in
every language, and inserts a "colour follow" mouse2 option so the right
button can start following the snapped item without an accent colour.

Run from the repo root:  python tools/patch_i18n.py
Idempotent: refuses to re-run once the keys exist."""
import io, re, sys

SRC = "app/i18n.py"
ANCHOR = '"lbl.mouse2_action"'

NEW_KEYS = {
 "de": [
  ("lbl.watch_center_only", "Nur die Bildschirmmitte beobachten"),
  ("desc.watch_center_only", "Die Hilfe beachtet nur ein festes Quadrat in der Mitte des Bildschirms (Größe = Suchdistanz, standardmäßig 150×150 px) – egal wo der Cursor steht. Klicks außerhalb dieses Quadrats bleiben unberührt."),
  ("lbl.center_follow", "Bildschirm folgt dem Ziel"),
  ("desc.center_follow", "Wenn „Nur die Bildschirmmitte beobachten“ an ist: Nach dem Einrasten auf ein Element bewegt die Hilfe den Bildschirm mit, damit das Ziel in der Mitte bleibt – besonders bei scrollenden Flächen. Bewege den Bildschirm selbst, um die Verfolgung loszulassen."),
  ("lbl.input_backend", "Eingabemethode"),
  ("desc.input_backend", "Windows-Einspeisung (Standard) funktioniert überall. Interception sendt über den Treiber und wird von Spielen als echte Maus erkannt – erfordert den installierten Interception-Treiber und interception.dll neben dem Programm; sonst automatisch Windows-Einspeisung."),
  ("val.input_backend.win32", "Windows-Einspeisung"),
  ("val.input_backend.interception", "Interception (Treiber)")],
 "es": [
  ("lbl.watch_center_only", "Vigilar solo el centro de la pantalla"),
  ("desc.watch_center_only", "La ayuda solo observa un cuadrado fijo en el centro de la pantalla (tamaño = distancia de búsqueda, 150×150 px por defecto), sin importar dónde esté el cursor. Los clics fuera de ese cuadrado no se modifican."),
  ("lbl.center_follow", "La pantalla sigue al objetivo"),
  ("desc.center_follow", "Con «Vigilar solo el centro de la pantalla» activado: tras enganchar un elemento, la ayuda mueve la pantalla para mantenerlo en el centro, especialmente en planos que se desplazan. Mueve tú la pantalla para soltar el seguimiento."),
  ("lbl.input_backend", "Método de entrada"),
  ("desc.input_backend", "Inyección de Windows (predeterminado) funciona en todas partes. Interception envía a través del controlador y los juegos lo reconocen como ratón real; requiere el controlador instalado y interception.dll junto al programa; si falta, usa la inyección de Windows automáticamente."),
  ("val.input_backend.win32", "Inyección de Windows"),
  ("val.input_backend.interception", "Interception (controlador)")],
 "fr": [
  ("lbl.watch_center_only", "Surveiller uniquement le centre de l'écran"),
  ("desc.watch_center_only", "L'assistance n'observe qu'un carré fixe au centre de l'écran (taille = distance de recherche, 150×150 px par défaut), où que soit le curseur. Les clics hors de ce carré restent inchangés."),
  ("lbl.center_follow", "L'écran suit la cible"),
  ("desc.center_follow", "Quand « Surveiller uniquement le centre de l'écran » est activé : après l'accrochage d'un élément, l'assistance déplace l'écran pour le garder au centre, surtout sur les plans défilants. Déplacez vous-même l'écran pour relâcher le suivi."),
  ("lbl.input_backend", "Méthode d'entrée"),
  ("desc.input_backend", "Injection Windows (par défaut) fonctionne partout. Interception envoie via le pilote et les jeux le reconnaissent comme une vraie souris ; nécessite le pilote Interception installé et interception.dll à côté du programme ; sinon l'injection Windows est utilisée automatiquement."),
  ("val.input_backend.win32", "Injection Windows"),
  ("val.input_backend.interception", "Interception (pilote)")],
 "it": [
  ("lbl.watch_center_only", "Osserva solo il centro dello schermo"),
  ("desc.watch_center_only", "L'assistenza osserva solo un quadrato fisso al centro dello schermo (dimensione = distanza di ricerca, 150×150 px predefinita), indipendentemente dalla posizione del cursore. I clic fuori da quel quadrato non vengono modificati."),
  ("lbl.center_follow", "Lo schermo segue l'oggetto"),
  ("desc.center_follow", "Con «Osserva solo il centro dello schermo» attivo: dopo l'aggancio di un elemento, l'assistenza muove lo schermo per tenerlo al centro, soprattutto su piani scorrevoli. Muovi tu lo schermo per rilasciare l'inseguimento."),
  ("lbl.input_backend", "Metodo di immissione"),
  ("desc.input_backend", "L'iniezione Windows (predefinito) funziona ovunque. Interception invia tramite driver e i giochi la riconoscono come mouse reale; richiede il driver Interception installato e interception.dll accanto al programma; altrimenti usa automaticamente l'iniezione Windows."),
  ("val.input_backend.win32", "Iniezione Windows"),
  ("val.input_backend.interception", "Interception (driver)")],
 "pt": [
  ("lbl.watch_center_only", "Observar apenas o centro do ecrã"),
  ("desc.watch_center_only", "A assistência observa apenas um quadrado fixo no centro do ecrã (tamanho = distância de pesquisa, 150×150 px por omissão), independentemente da posição do cursor. Os cliques fora desse quadrado não são alterados."),
  ("lbl.center_follow", "O ecrã segue o alvo"),
  ("desc.center_follow", "Com «Observar apenas o centro do ecrã» ativo: após capturar um item, a assistência move o ecrã para o manter no centro, especialmente em planos com deslocamento. Mova você o ecrã para libertar o seguimento."),
  ("lbl.input_backend", "Método de entrada"),
  ("desc.input_backend", "A injeção do Windows (predefinido) funciona em todo lado. A Interception envia através do controlador e os jogos reconhecem-na como rato real; requer o controlador Interception instalado e interception.dll junto ao programa; caso contrário usa automaticamente a injeção do Windows."),
  ("val.input_backend.win32", "Injeção do Windows"),
  ("val.input_backend.interception", "Interception (controlador)")],
 "nl": [
  ("lbl.watch_center_only", "Alleen het schermcentrum bewaken"),
  ("desc.watch_center_only", "De assistentie bekijkt alleen een vast vierkant in het midden van het scherm (grootte = zoekafstand, standaard 150×150 px), ongeacht waar de cursor staat. Klik buiten dat vierkant blijven onveranderd."),
  ("lbl.center_follow", "Scherm volgt het doel"),
  ("desc.center_follow", "Met «Alleen het schermcentrum bewaken» aan: na het vergrendelen op een item beweegt de assistentie het scherm om het in het midden te houden, vooral bij scrollvlakken. Beweeg zelf het scherm om het volgen los te laten."),
  ("lbl.input_backend", "Invoermethode"),
  ("desc.input_backend", "Windows-injectie (standaard) werkt overal. Interception verzendt via het stuurprogramma en spellen herkennen het als een echte muis; vereist het geïnstalleerde Interception-stuurprogramma en interception.dll naast het programma; anders wordt automatisch Windows-injectie gebruikt."),
  ("val.input_backend.win32", "Windows-injectie"),
  ("val.input_backend.interception", "Interception (stuurprogramma)")],
 "pl": [
  ("lbl.watch_center_only", "Obserwuj tylko środek ekranu"),
  ("desc.watch_center_only", "Asystent obserwuje wyłącznie stały kwadrat w środku ekranu (rozmiar = dystans wyszukiwania, domyślnie 150×150 px), niezależnie od położenia kursora. Kliknięcia poza tym kwadratem pozostają bez zmian."),
  ("lbl.center_follow", "Ekran podąża za celem"),
  ("desc.center_follow", "Przy włączonym «Obserwuj tylko środek ekranu»: po przyciągnięciu elementu asystent przesuwa ekran, aby utrzymać go w środku, zwłaszcza na przewijanych płaszczyznach. Przesuń ekran samodzielnie, aby zwolnić podążanie."),
  ("lbl.input_backend", "Metoda wprowadzania"),
  ("desc.input_backend", "Wstrzykiwanie Windows (domyślne) działa wszędzie. Interception wysyła przez sterownik i gry rozpoznają je jako prawdziwą mysz; wymaga zainstalowanego sterownika Interception i pliku interception.dll obok programu; w przeciwnym razie automatycznie używa wstrzykiwania Windows."),
  ("val.input_backend.win32", "Wstrzykiwanie Windows"),
  ("val.input_backend.interception", "Interception (sterownik)")],
 "ru": [
  ("lbl.watch_center_only", "Следить только за центром экрана"),
  ("desc.watch_center_only", "Помощник наблюдает только за фиксированным квадратом в центре экрана (размер = дистанция поиска, по умолчанию 150×150 px), независимо от положения курсора. Клики вне этого квадрата остаются без изменений."),
  ("lbl.center_follow", "Экран следует за целью"),
  ("desc.center_follow", "Когда «Следить только за центром экрана» включено: после захвата элемента помощник двигает экран, чтобы удерживать его в центре, особенно на прокручиваемых плоскостях. Двигайте экран сами, чтобы отпустить следование."),
  ("lbl.input_backend", "Метод ввода"),
  ("desc.input_backend", "Инъекция Windows (по умолчанию) работает везде. Interception отправляет через драйвер, и игры распознают её как настоящую мышь; требует установленного драйвера Interception и interception.dll рядом с программой; иначе автоматически используется инъекция Windows."),
  ("val.input_backend.win32", "Инъекция Windows"),
  ("val.input_backend.interception", "Interception (драйвер)")],
 "uk": [
  ("lbl.watch_center_only", "Слідкувати лише за центром екрана"),
  ("desc.watch_center_only", "Помічник спостерігає лише за фіксованим квадратом у центрі екрана (розмір = дистанція пошуку, типово 150×150 px), незалежно від положення курсора. Кліки поза цим квадратом залишаються без змін."),
  ("lbl.center_follow", "Екран слідкує за ціллю"),
  ("desc.center_follow", "Коли «Слідкувати лише за центром екрана» увімкнено: після захоплення елемента помічник рухає екран, щоб утримувати його в центрі, особливо на прокручуваних площинах. Рухайте екран самостійно, щоб відпустити стеження."),
  ("lbl.input_backend", "Метод введення"),
  ("desc.input_backend", "Ін'єкція Windows (типово) працює скрізь. Interception надсилає через драйвер, і ігри розпізнають її як справжню мишу; потребує встановленого драйвера Interception і interception.dll поруч із програмою; інакше автоматично використовується ін'єкція Windows."),
  ("val.input_backend.win32", "Ін'єкція Windows"),
  ("val.input_backend.interception", "Interception (драйвер)")],
 "tr": [
  ("lbl.watch_center_only", "Yalnızca ekran merkezini izle"),
  ("desc.watch_center_only", "Destek, yalnızca ekranın ortasındaki sabit bir kareyi tarar (boyut = arama mesafesi, varsayılan 150×150 px); imlecin nerede olduğu fark etmez. Bu karenin dışındaki tıklamalar değiştirilmez."),
  ("lbl.center_follow", "Ekran hedefi takip eder"),
  ("desc.center_follow", "“Yalnızca ekran merkezini izle” açıkken: bir öğeye kilitlenince destek, özellikle kayan düzlemlerde, onu merkezde tutmak için ekranı hareket ettirir. Takibi bırakmak için ekranı siz hareket ettirin."),
  ("lbl.input_backend", "Giriş yöntemi"),
  ("desc.input_backend", "Windows enjeksiyonu (varsayılan) her yerde çalışır. Interception sürücü üzerinden gönderir ve oyunlar bunu gerçek fare olarak tanır; kurulu Interception sürücüsü ve programın yanında interception.dll gerektirir; aksi halde otomatik olarak Windows enjeksiyonu kullanılır."),
  ("val.input_backend.win32", "Windows enjeksiyonu"),
  ("val.input_backend.interception", "Interception (sürücü)")],
 "sw": [
  ("lbl.watch_center_only", "Fuatilia katikati ya skrini pekee"),
  ("desc.watch_center_only", "Usaidizi huangalia mraba uliotulia katikati ya skrini (ukubwa = umbali wa utafutaji, chaguo-msingi 150×150 px) bila kujali kiashiria kiko. Bofyo nje ya mraba huo hubaki vilevile."),
  ("lbl.center_follow", "Skrini ifuate lengo"),
  ("desc.center_follow", "«Fuatilia katikati ya skrini pekee» ikiwa washa: baada ya kitu kushikwa, usaidizi husogeua skrini ili kikaa katikati hasa kwa ndege zinazosogea. Sofisha skrini wewe mwenyewe kuachilia ufuataji."),
  ("lbl.input_backend", "Njia ya ingizo"),
  ("desc.input_backend", "Uingizaji wa Windows (chaguo-msingi) hufanya kila mahali. Interception hutuma kupitia kiendeshi na michezo huitambua kama panya halisi; inahitaji kiendeshi cha Interception kilichowekwa na interception.dll karibu na programu; vinginevyo hutumia uingizaji wa Windows kiotomatiki."),
  ("val.input_backend.win32", "Uingizaji wa Windows"),
  ("val.input_backend.interception", "Interception (kiendeshi)")],
 "hu": [
  ("lbl.watch_center_only", "Csak a képernyő közepét figyelje"),
  ("desc.watch_center_only", "A segítség csak a képernyő közepén lévő rögzített négyzetet figyeli (méret = keresési távolság, alapértelmezés szerint 150×150 px), függetlenül a kurzor helyétől. A négyzeten kívüli kattintások érintetlenek maradnak."),
  ("lbl.center_follow", "A képernyő követi a célt"),
  ("desc.center_follow", "Ha a „Csak a képernyő közepét figyelje” be van kapcsolva: egy elem megragadása után a segítség mozgatja a képernyőt, hogy középen maradjon – különösen görgetett felületeknél. Mozgasd magad a képernyőt a követés elengedéséhez."),
  ("lbl.input_backend", "Beviteli mód"),
  ("desc.input_backend", "A Windows-befecskendezés (alapértelmezett) mindenhol működik. Az Interception illesztőprogramon keresztül küld, és a játékok valódi egérként ismerik fel; telepített Interception-illesztőprogramot és az interception.dll-t igényli a program mellett; hiányában automatikusan a Windows-befecskendezést használja."),
  ("val.input_backend.win32", "Windows-befecskendezés"),
  ("val.input_backend.interception", "Interception (illesztő)")],
 "zh": [
  ("lbl.watch_center_only", "仅注视屏幕中心"),
  ("desc.watch_center_only", "辅助功能只扫描屏幕正中心的固定方框（大小=搜索距离，默认150×150像素），与光标位置无关。该方框之外的点击保持原样。"),
  ("lbl.center_follow", "屏幕跟随目标"),
  ("desc.center_follow", "开启“仅注视屏幕中心”时：吸附到某个元素后，辅助功能会移动屏幕使其保持在中心——尤其适用于滚动画板。自己移动屏幕即可解除跟随。"),
  ("lbl.input_backend", "输入方式"),
  ("desc.input_backend", "Windows注入（默认）到处可用。Interception通过驱动发送，游戏将其识别为真实鼠标；需要已安装Interception驱动并在程序旁放置interception.dll；否则自动改用Windows注入。"),
  ("val.input_backend.win32", "Windows注入"),
  ("val.input_backend.interception", "Interception（驱动）")],
 "ja": [
  ("lbl.watch_center_only", "画面中央のみを監視"),
  ("desc.watch_center_only", "アシストは画面正中の固定四角（サイズ＝検索距離、既定150×150px）だけを対象にします。カーソルの位置は関係ありません。その四角の外でのクリックは変更されません。"),
  ("lbl.center_follow", "画面がターゲットを追う"),
  ("desc.center_follow", "「画面中央のみを監視」ON時：アイテムを捕らえた後、アシストはそれを中央に保つよう画面を動かします（スクロール平面で特に有効）。自分で画面を動かすと追従が解除されます。"),
  ("lbl.input_backend", "入力方法"),
  ("desc.input_backend", "Windowsインジェクション（既定）はどこでも動作します。Interceptionはドライバ経由で送信し、ゲームは実マウスとして認識します。Interceptionドライバのインストールとプログラム横のinterception.dllが必要。無い場合は自動的にWindowsインジェクションへ戻ります。"),
  ("val.input_backend.win32", "Windowsインジェクション"),
  ("val.input_backend.interception", "Interception（ドライバ）")],
 "ko": [
  ("lbl.watch_center_only", "화면 중앙만 주시"),
  ("desc.watch_center_only", "도움 기능은 화면 정중앙의 고정 사각형(크기=검색 거리, 기본 150×150px)만 스캔합니다. 커서 위치와 무관합니다. 그 사각형 밖의 클릭은 그대로 통과합니다."),
  ("lbl.center_follow", "화면이 대상을 따라감"),
  ("desc.center_follow", "“화면 중앙만 주시” 켜짐 시: 항목을 붙잡으면 도움 기능이 이를 중앙에 유지하도록 화면을 움직입니다(스크롤 평면에 특히 유용). 직접 화면을 움직이면 추적이 해제됩니다."),
  ("lbl.input_backend", "입력 방식"),
  ("desc.input_backend", "Windows 인젝션(기본)은 어디서나 작동합니다. Interception은 드라이버를 통해 전송하며 게임이 실제 마우스로 인식합니다. Interception 드라이버 설치와 프로그램 옆 interception.dll이 필요합니다. 없으면 자동으로 Windows 인젝션을 사용합니다."),
  ("val.input_backend.win32", "Windows 인젝션"),
  ("val.input_backend.interception", "Interception (드라이버)")],
}

# Refreshed auto-click wording (label, description) per locale - the old
# text still described the 2 s colour-only behaviour.
AUTOCLICK = {
 "de": ("Klickt selbst auf Elemente",
        "Eingeschaltet klickt das Programm alle 0,1 Sekunden von selbst auf das beste Element im beobachteten Bereich – zuerst nach Kontrast sortiert. Ist eine Akzentfarbe gesetzt, kommen nur Elemente mit dieser Farbe infrage; ohne Farbe werden nur sehr scharf gezeichnete Elemente geklickt. Dasselbe Feld nicht zweimal, eigenes Fenster nie."),
 "es": ("Clicar elementos él solo",
        "Activado, el programa hace clic por sí solo cada 0,1 segundos en el mejor elemento del área observada, priorizando el contraste. Con color de acento definido, solo cuentan los elementos con ese color; sin color, solo se clican los dibujados con gran nitidez. Nunca dos veces en el mismo sitio ni en ventanas propias."),
 "fr": ("Cliquer les éléments tout seul",
        "Activé, le programme clique seul toutes les 0,1 s sur le meilleur élément de la zone surveillée, en privilégiant le contraste. Avec une couleur d'accent définie, seuls les éléments porteurs comptent ; sans couleur, seuls les éléments très nets sont cliqués. Jamais deux fois au même endroit ni dans ses propres fenêtres."),
 "it": ("Clicca gli elementi da sé",
        "Attivo, il programma clicca da solo ogni 0,1 secondi sul miglior elemento dell'area osservata, privilegiando il contrasto. Con un colore d'accento impostato contano solo gli elementi colorati; senza colore si cliccano solo elementi molto nitidi. Mai due volte nello stesso punto né sulle proprie finestre."),
 "pt": ("Clica nos itens sozinho",
        "Ligado, o programa clica sozinho a cada 0,1 segundos no melhor item da área observada, dando prioridade ao contraste. Com cor de acento definida, só contam os itens com essa cor; sem cor, só são clicados itens muito nítidos. Nunca duas vezes no mesmo sítio nem nas suas próprias janelas."),
 "nl": ("Klikt items zelf aan",
        "Aangezet klikt het programma elke 0,1 seconde zelf op het beste item in het bewaakte gebied, eerst op contrast gesorteerd. Met een accentkleur komen alleen items met die kleur in aanmerking; zonder kleur worden alleen zeer scherp getekende items geklikt. Nooit twee keer op dezelfde plek, nooit eigen vensters."),
 "pl": ("Klikna elementy samoistnie",
        "Włączone: program sam klika co 0,1 sekundy w najlepszy element obserwowanego obszaru, przedkładając kontrast. Ustawiony kolor akcentu oznacza, że kwalifikują się tylko kolorowe elementy; bez koloru klikane są wyłącznie bardzo wyraziste. Nigdy dwa razy w tym samym miejscu ani we własnych oknach."),
 "ru": ("Кликать элементы само",
        "Включено: программа сама кликает каждые 0,1 с по лучшему элементу наблюдаемой области, приоритет — контраст. При заданном акцентном цвете годятся только окрашенные элементы; без цвета кликаются только очень чётко прорисованные. Никогда дважды в одном месте и не в собственных окнах."),
 "uk": ("Клацати елементи самостійно",
        "Увімкнено: програма сама клацає кожні 0,1 с по найкращому елементі спостережуваної ділянки, пріоритет — контраст. Якщо заданий акцентний колір, придатні лише забарвлені елементи; без кольору клацаються тільки дуже чітко намальовані. Ніколи двічі в одному місці й не у власних вікнах."),
 "tr": ("Öğelere kendi tıklar",
        "Açıkken program, gözlenen bölgedeki en iyi öğeye her 0,1 saniyede kendiliğinden tıklar; öncelik kontrasttır. Vurgu rengi ayarlıysa yalnız renkli öğeler adaydır; renk yoksa sadece çok keskin çizilmiş öğelere tıklanır. Aynı yere iki kez ve kendi pencerelerine asla."),
 "sw": ("Bofya vitu vyenyewe",
        "Ikiwa washwa, programu yenyewe inabofya kila sekunde 0.1 kitu bora katika eneo linalozingatiwa, ikipanga kwanza kwa contrast. Ikiwa rangi ya kipaumbele imewekwa, vitu vilivyo na rangi hiyo ndivyo vinavyostahili; bila rangi, vitu vilivyo chorwa kwa ukali ndivyo vinabofywa. Kamwe mara mbili mahali pamoja wala dirisha lake lenyewe."),
 "hu": ("Magától kattint az elemekre",
        "Bekapcsolva a program minden 0,1 másodpercben magától kattint a figyelt terület legjobb elemére, a kontraszt az elsőbbségi szempont. Ha alapszín be van állítva, csak a színes elemek jöhetnek szóba; szín nélkül csak a nagyon élesen rajzolt elemekre kattint. Ugyanoda sosem kétszer, és saját ablakaira soha."),
 "zh": ("自行点击项目",
        "开启后，程序每0.1秒自动点击被观察区域内的最佳项目，以对比度优先。设置了强调色时，只有带该色的项目符合条件；未设置颜色时，仅点击绘制非常清晰的项目。同一处不重复点击，绝不点击自己的窗口。"),
 "ja": ("自分でアイテムをクリック",
        "オンにすると、監視領域内の最良アイテムへ0.1秒ごとに自動クリックします。判定はまずコントラスト優先。アクセントカラー設定時はその色を持つアイテムのみが対象。色なしでは非常にくっきり描かれたアイテムだけがクリックされます。同じ場所を二度はクリックせず、自ウィンドウも絶対にクリックしません。"),
 "ko": ("스스로 항목을 클릭",
        "켜면 프로그램이 관찰 영역의 가장 좋은 항목을 0.1초마다 스스로 클릭하며 대비를 우선합니다. 강조 색이 설정되면 그 색을 가진 항목만 대상이고, 색이 없으면 매우 선명하게 그려진 항목만 클릭됩니다. 같은 곳을 두 번 클릭하지 않으며 자체 창은 절대 클릭하지 않습니다."),
}


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def render_kv(key, value, indent):
    """Source text for one dict entry, in the catalog's own style: the
    value is packed into quoted fragments that each END their physical
    line (so implicit concatenation works without backslashes), the
    final fragment closes with a comma. No parentheses - the catalog is
    a dict literal."""
    cont = indent + "    "
    budget = 66                      # chars of text per fragment
    words = value.split(" ")
    parts, cur = [], ""
    for w in words:
        cand = (cur + " " + w) if cur else w
        if len(cand) > budget and cur:
            parts.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        parts.append(cur)
    # Implicit concatenation glues fragments with NO separator, so every
    # non-final fragment must end with its trailing space.
    parts = [q + " " for q in parts[:-1]] + parts[-1:]
    lines = []
    for i, p in enumerate(parts):
        head = ('%s"%s": ' % (indent, key)) if i == 0 else cont
        sep = "," if i == len(parts) - 1 else ""
        lines.append('%s"%s"%s' % (head, esc(p), sep))
    return chr(10).join(lines)


def entry_span(lines, start, key, end=None):
    """First line of a `"key":` entry and how many source lines it
    occupies: an entry's LAST physical line is the one ending in a
    comma; every earlier line of the value is a bare quoted fragment."""
    pat = '"%s":' % key
    if end is None:
        end = len(lines)
    for j in range(start, end):
        if pat in lines[j]:
            n = 1
            while not lines[j + n - 1].rstrip().endswith(","):
                n += 1
                if j + n > end:
                    break
            return j, n
    return None, 0


def replace_entry(lines, start, key, value, end=None):
    j, n = entry_span(lines, start, key, end)
    if j is None:
        return False
    indent = lines[j][:len(lines[j]) - len(lines[j].lstrip())]
    lines[j:j + n] = render_kv(key, value, indent).split(chr(10))
    return True


def main():
    src = io.open(SRC, encoding="utf-8").read()
    if '"lbl.watch_center_only"' in src:
        print("already patched"); return 1
    lines = src.split(chr(10))

    blocks = []
    for i, ln in enumerate(lines):
        m = re.match(r'^\s{4}"(en|de|es|fr|it|pt|nl|pl|ru|uk|tr|sw|hu'
                     r'|zh|ja|ko)": \{$', ln)
        if m:
            blocks.append((m.group(1), i))
    names = [b[0] for b in blocks]
    print("locales:", names)

    edits = []
    for idx, (loc, start) in enumerate(blocks):
        if loc == "en":
            continue          # English catalog is the source; locales only
        end = blocks[idx + 1][1] if idx + 1 < len(blocks) else len(lines)
        anchor_line = None
        for j in range(start, end):
            if ANCHOR in lines[j]:
                anchor_line = j
                break
        if anchor_line is None:
            raise SystemExit("no mouse2 anchor in %s" % loc)
        indent = lines[anchor_line][:len(lines[anchor_line]) -
                                   len(lines[anchor_line].lstrip())]
        chunk = []
        for key, val in NEW_KEYS[loc]:
            chunk.append(render_kv(key, val, indent))
        if chunk:
            edits.append((anchor_line, chr(10).join(chunk)))

    # apply insertions bottom-up (line indices stay valid)
    for at, code in sorted(edits, key=lambda e: -e[0]):
        lines.insert(at, code)

    # auto-click wording refresh (label + description) per locale
    src = chr(10).join(lines)
    lines = src.split(chr(10))
    blocks = []
    for i, ln in enumerate(lines):
        m = re.match(r'^\s{4}"(en|de|es|fr|it|pt|nl|pl|ru|uk|tr|sw|hu'
                     r'|zh|ja|ko)": \{$', ln)
        if m:
            blocks.append((m.group(1), i))
    done_lbl = done_desc = 0
    for idx, (loc, start) in enumerate(blocks):
        if loc not in AUTOCLICK:
            continue
        end = blocks[idx + 1][1] if idx + 1 < len(blocks) else len(lines)
        # scope replacement to this locale block
        sub = lines[start:end]
        ok1 = replace_entry(sub, 0, "lbl.auto_click", AUTOCLICK[loc][0], len(sub))
        ok2 = replace_entry(sub, 0, "desc.auto_click", AUTOCLICK[loc][1], len(sub))
        done_lbl += ok1; done_desc += ok2
        lines[start:end] = sub
    src = chr(10).join(lines)

    io.open(SRC, "w", encoding="utf-8").write(src)
    print("inserted new keys into %d locales; refreshed auto_click "
          "labels=%d descriptions=%d" % (len(edits), done_lbl, done_desc))


if __name__ == "__main__":
    main()
