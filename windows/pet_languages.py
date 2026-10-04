"""Menu translations selected from the Windows user's preferred UI languages."""
import ctypes

# size, small, medium, large, dock, quit
TRANSLATIONS = {
    'en': ('Size', 'Small', 'Medium', 'Large', 'Align to taskbar (drag down to reposition)', 'Quit'),
    'zh-Hant': ('大小', '小', '中', '大', '貼齊工作列（可往下拖）', '結束'),
    'zh-Hans': ('大小', '小', '中', '大', '贴齐任务栏（可向下拖动）', '退出'),
    'ja': ('サイズ', '小', '中', '大', 'タスクバーに合わせる（下へドラッグ可能）', '終了'),
    'ko': ('크기', '작게', '보통', '크게', '작업 표시줄에 맞추기 (아래로 드래그 가능)', '종료'),
    'fr': ('Taille', 'Petite', 'Moyenne', 'Grande', 'Aligner sur la barre des tâches (glisser vers le bas)', 'Quitter'),
    'de': ('Größe', 'Klein', 'Mittel', 'Groß', 'An Taskleiste ausrichten (nach unten ziehbar)', 'Beenden'),
    'es': ('Tamaño', 'Pequeño', 'Mediano', 'Grande', 'Alinear con la barra de tareas (arrastrar hacia abajo)', 'Salir'),
    'pt': ('Tamanho', 'Pequeno', 'Médio', 'Grande', 'Alinhar à barra de tarefas (arrastar para baixo)', 'Sair'),
    'it': ('Dimensione', 'Piccola', 'Media', 'Grande', 'Allinea alla barra delle applicazioni (trascina in basso)', 'Esci'),
    'nl': ('Grootte', 'Klein', 'Middel', 'Groot', 'Uitlijnen op taakbalk (omlaag slepen mogelijk)', 'Afsluiten'),
    'ru': ('Размер', 'Маленький', 'Средний', 'Большой', 'Выровнять по панели задач (можно перетащить вниз)', 'Выход'),
    'uk': ('Розмір', 'Малий', 'Середній', 'Великий', 'Вирівняти по панелі завдань (можна тягнути вниз)', 'Вийти'),
    'pl': ('Rozmiar', 'Mały', 'Średni', 'Duży', 'Wyrównaj do paska zadań (można przeciągnąć w dół)', 'Zakończ'),
    'cs': ('Velikost', 'Malá', 'Střední', 'Velká', 'Zarovnat k hlavnímu panelu (lze táhnout dolů)', 'Ukončit'),
    'sk': ('Veľkosť', 'Malá', 'Stredná', 'Veľká', 'Zarovnať k panelu úloh (možno potiahnuť nadol)', 'Ukončiť'),
    'hu': ('Méret', 'Kicsi', 'Közepes', 'Nagy', 'Igazítás a tálcához (lefelé húzható)', 'Kilépés'),
    'ro': ('Dimensiune', 'Mică', 'Medie', 'Mare', 'Aliniază la bara de activități (se poate trage în jos)', 'Ieșire'),
    'bg': ('Размер', 'Малък', 'Среден', 'Голям', 'Подравняване към лентата на задачите (плъзгане надолу)', 'Изход'),
    'el': ('Μέγεθος', 'Μικρό', 'Μεσαίο', 'Μεγάλο', 'Στοίχιση στη γραμμή εργασιών (σύρετε προς τα κάτω)', 'Έξοδος'),
    'tr': ('Boyut', 'Küçük', 'Orta', 'Büyük', 'Görev çubuğuna hizala (aşağı sürüklenebilir)', 'Çıkış'),
    'sv': ('Storlek', 'Liten', 'Mellan', 'Stor', 'Justera mot aktivitetsfältet (kan dras nedåt)', 'Avsluta'),
    'da': ('Størrelse', 'Lille', 'Mellem', 'Stor', 'Juster til proceslinjen (kan trækkes ned)', 'Afslut'),
    'nb': ('Størrelse', 'Liten', 'Middels', 'Stor', 'Juster til oppgavelinjen (kan dras ned)', 'Avslutt'),
    'fi': ('Koko', 'Pieni', 'Keskikokoinen', 'Suuri', 'Kohdista tehtäväpalkkiin (voi vetää alas)', 'Lopeta'),
    'id': ('Ukuran', 'Kecil', 'Sedang', 'Besar', 'Sejajarkan ke bilah tugas (bisa diseret ke bawah)', 'Keluar'),
    'ms': ('Saiz', 'Kecil', 'Sederhana', 'Besar', 'Jajarkan ke bar tugas (boleh diseret ke bawah)', 'Keluar'),
    'vi': ('Kích thước', 'Nhỏ', 'Vừa', 'Lớn', 'Căn theo thanh tác vụ (có thể kéo xuống)', 'Thoát'),
    'th': ('ขนาด', 'เล็ก', 'กลาง', 'ใหญ่', 'จัดชิดแถบงาน (ลากลงได้)', 'ออก'),
    'hi': ('आकार', 'छोटा', 'मध्यम', 'बड़ा', 'टास्कबार से संरेखित करें (नीचे खींच सकते हैं)', 'बंद करें'),
    'ar': ('الحجم', 'صغير', 'متوسط', 'كبير', 'محاذاة مع شريط المهام (يمكن السحب لأسفل)', 'خروج'),
    'he': ('גודל', 'קטן', 'בינוני', 'גדול', 'יישור לשורת המשימות (ניתן לגרור למטה)', 'יציאה'),
    'fa': ('اندازه', 'کوچک', 'متوسط', 'بزرگ', 'تراز با نوار وظیفه (قابل کشیدن به پایین)', 'خروج'),
    'ca': ('Mida', 'Petita', 'Mitjana', 'Gran', 'Alinea amb la barra de tasques (arrossega avall)', 'Surt'),
    'hr': ('Veličina', 'Mala', 'Srednja', 'Velika', 'Poravnaj s programskom trakom (povuci dolje)', 'Izlaz'),
    'sr': ('Величина', 'Мала', 'Средња', 'Велика', 'Поравнај са траком задатака (превуци надоле)', 'Излаз'),
    'sl': ('Velikost', 'Majhna', 'Srednja', 'Velika', 'Poravnaj z opravilno vrstico (povleci navzdol)', 'Izhod'),
    'et': ('Suurus', 'Väike', 'Keskmine', 'Suur', 'Joonda tegumiribaga (saab alla lohistada)', 'Välju'),
    'lv': ('Izmērs', 'Mazs', 'Vidējs', 'Liels', 'Līdzināt ar uzdevumjoslu (var vilkt lejup)', 'Iziet'),
    'lt': ('Dydis', 'Mažas', 'Vidutinis', 'Didelis', 'Lygiuoti su užduočių juosta (galima vilkti žemyn)', 'Išeiti'),
    'fil': ('Laki', 'Maliit', 'Katamtaman', 'Malaki', 'Ihanay sa taskbar (maaaring i-drag pababa)', 'Isara'),
}


def windows_ui_languages():
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    api = kernel.GetUserPreferredUILanguages
    api.argtypes = (ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
                    ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong))
    api.restype = ctypes.c_bool
    count, length = ctypes.c_ulong(), ctypes.c_ulong()
    if api(8, ctypes.byref(count), None, ctypes.byref(length)) and length.value:
        buffer = ctypes.create_unicode_buffer(length.value)
        if api(8, ctypes.byref(count), buffer, ctypes.byref(length)):
            return [tag for tag in buffer[:length.value].split('\0') if tag]
    # UI language, not keyboard layout or regional number/date formatting.
    kernel.GetUserDefaultUILanguage.restype = ctypes.c_ushort
    kernel.LCIDToLocaleName.argtypes = (ctypes.c_ulong, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_ulong)
    buffer = ctypes.create_unicode_buffer(85)
    if kernel.LCIDToLocaleName(kernel.GetUserDefaultUILanguage(), buffer, 85, 0):
        return [buffer.value]
    return ['en']


def menu_language(tags=None):
    for tag in windows_ui_languages() if tags is None else tags:
        parts = tag.lower().replace('_', '-').split('-')
        lang = parts[0]
        if lang == 'zh':
            key = 'zh-Hant' if any(p in ('hant', 'tw', 'hk', 'mo') for p in parts[1:]) else 'zh-Hans'
        else:
            key = {'no': 'nb', 'nn': 'nb', 'tl': 'fil', 'iw': 'he'}.get(lang, lang)
        if key in TRANSLATIONS:
            return key, TRANSLATIONS[key]
    return 'en', TRANSLATIONS['en']
