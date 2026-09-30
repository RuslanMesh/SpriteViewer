import locale
from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ru": {
        "title": "Sprite Viewer",
        "hide_ui": "▲ Скрыть UI (H)",
        "show_ui": "▼ Показать UI (H)",
        "folder": "Папка",
        "sheet": "Спрайт-лист",
        "play": "Старт (P)",
        "pause": "Пауза (P)",
        "fps": "FPS:",
        "ontop": "Поверх",
        "frames_count": "к.",
        "mode_strip": "Линейный",
        "mode_grid": "Сетка (Матрица)",
        "width": "W:",
        "height": "H:",
        "step_x": "Шаг X:",
        "step_y": "Шаг Y:",
        "max_frames": "Кадров:",
        "apply": "Применить",
        "zoom": "Зум:",
        "reset_zoom": "1:1",
        "export_gif": "GIF",
        "export_success": "Анимация успешно экспортирована в GIF!",
        "export_no_frames": "Нет загруженных кадров для экспорта!",
        "dlg_folder": "Выберите папку с кадрами",
        "dlg_file": "Выберите файл спрайт-листа",
        "dlg_save_gif": "Сохранить GIF анимацию",
        "err_title": "Недостаточно места на полотне",
        "err_strip_overflow": (
            "Недостаточно места на полотне для кадра №{req_frame}!\n\n"
            "• Ширина холста: {curr_w} px\n"
            "• Поместилось кадров: {avail_count}\n"
            "• Для кадра №{req_frame} требуется ширина: {needed_w} px\n"
            "• Не хватает: {missing_w} px\n\n"
            "Расширьте холст вправо или переключитесь на режим 'Сетка'."
        ),
        "err_grid_overflow": (
            "Недостаточно места на полотне для кадра №{req_frame}!\n\n"
            "• Размер холста: {curr_w} × {curr_h} px\n"
            "• Вместимость сетки: {cols} кол. × {rows} ряд. = {avail_count} кадров\n\n"
            "Подсказка для размещения кадра №{req_frame}:\n"
            "{suggestion}"
        ),
        "hint_vertical": "• Кадр должен быть в {row}-м ряду (колонка {col}).\n• Не хватает места снизу: увеличьте высоту холста минимум на {missing_h} px (до {needed_h} px).",
        "hint_horizontal": "• Не хватает места справа: расширьте ширину на {missing_w} px (до {needed_w} px).",
        "hint_too_narrow": "• Холст ({sheet_w} px) уже ширины одного кадра ({frame_w} px)."
    },
    "en": {
        "title": "Sprite Viewer",
        "hide_ui": "▲ Hide UI (H)",
        "show_ui": "▼ Show UI (H)",
        "folder": "Folder",
        "sheet": "Sprite Sheet",
        "play": "Play (P)",
        "pause": "Pause (P)",
        "fps": "FPS:",
        "ontop": "On Top",
        "frames_count": "fr.",
        "mode_strip": "Strip (Linear)",
        "mode_grid": "Grid (Matrix)",
        "width": "W:",
        "height": "H:",
        "step_x": "Step X:",
        "step_y": "Step Y:",
        "max_frames": "Frames:",
        "apply": "Apply",
        "zoom": "Zoom:",
        "reset_zoom": "1:1",
        "export_gif": "GIF",
        "export_success": "Animation exported to GIF successfully!",
        "export_no_frames": "No frames loaded to export!",
        "dlg_folder": "Select folder with frames",
        "dlg_file": "Select sprite sheet file",
        "dlg_save_gif": "Save GIF Animation",
        "err_title": "Canvas boundary exceeded",
        "err_strip_overflow": (
            "Not enough space on canvas for frame #{req_frame}!\n\n"
            "• Canvas width: {curr_w} px\n"
            "• Frames fitted: {avail_count}\n"
            "• Required width for frame #{req_frame}: {needed_w} px\n"
            "• Missing: {missing_w} px\n\n"
            "Expand canvas rightward or switch to 'Grid' mode."
        ),
        "err_grid_overflow": (
            "Not enough space on canvas for frame #{req_frame}!\n\n"
            "• Canvas size: {curr_w} × {curr_h} px\n"
            "• Grid capacity: {cols} cols × {rows} rows = {avail_count} frames\n\n"
            "Hint to fit frame #{req_frame}:\n"
            "{suggestion}"
        ),
        "hint_vertical": "• Frame belongs to row {row}, col {col}.\n• Vertical space missing: extend canvas downward by {missing_h} px (to {needed_h} px).",
        "hint_horizontal": "• Horizontal space missing: extend width by {missing_w} px (to {needed_w} px).",
        "hint_too_narrow": "• Canvas width ({sheet_w} px) is narrower than single frame width ({frame_w} px)."
    },
    "es": {
        "title": "Sprite Viewer",
        "hide_ui": "▲ Ocultar UI (H)",
        "show_ui": "▼ Mostrar UI (H)",
        "folder": "Carpeta",
        "sheet": "Sprite Sheet",
        "play": "Play (P)",
        "pause": "Pausa (P)",
        "fps": "FPS:",
        "ontop": "Fijar",
        "frames_count": "fr.",
        "mode_strip": "Tira (Lineal)",
        "mode_grid": "Cuadrícula (Matriz)",
        "width": "W:",
        "height": "H:",
        "step_x": "Paso X:",
        "step_y": "Paso Y:",
        "max_frames": "Fotogramas:",
        "apply": "Aplicar",
        "zoom": "Zoom:",
        "reset_zoom": "1:1",
        "export_gif": "GIF",
        "export_success": "¡Animación exportada a GIF con éxito!",
        "export_no_frames": "¡No hay fotogramas para exportar!",
        "dlg_folder": "Seleccione carpeta de fotogramas",
        "dlg_file": "Seleccione archivo de hoja de sprites",
        "dlg_save_gif": "Guardar animación GIF",
        "err_title": "Espacio insuficiente en el lienzo",
        "err_strip_overflow": (
            "¡No hay suficiente espacio en el lienzo para el fotograma #{req_frame}!\n\n"
            "• Ancho del lienzo: {curr_w} px\n"
            "• Fotogramas que caben: {avail_count}\n"
            "• Ancho requerido: {needed_w} px\n"
            "• Faltan: {missing_w} px\n\n"
            "Amplíe el lienzo a la derecha o cambie al modo 'Cuadrícula'."
        ),
        "err_grid_overflow": (
            "¡No hay suficiente espacio en la cuadrícula para el fotograma #{req_frame}!\n\n"
            "• Tamaño del lienzo: {curr_w} × {curr_h} px\n"
            "• Capacidad: {cols} col. × {rows} filas = {avail_count} fotogramas\n\n"
            "Sugerencia para ubicar el fotograma #{req_frame}:\n"
            "{suggestion}"
        ),
        "hint_vertical": "• El fotograma pertenece a la fila {row}, col {col}.\n• Falta espacio vertical: amplíe el lienzo hacia abajo al menos {missing_h} px (hasta {needed_h} px).",
        "hint_horizontal": "• Falta espacio horizontal: amplíe el ancho en {missing_w} px (hasta {needed_w} px).",
        "hint_too_narrow": "• El lienzo ({sheet_w} px) es más estrecho que un solo fotograma ({frame_w} px)."
    }
}

def detect_system_language() -> str:
    try:
        lang, _ = locale.getdefaultlocale()
        if lang:
            code = lang.lower()
            if code.startswith("ru"):
                return "ru"
            if code.startswith("es"):
                return "es"
    except Exception:
        pass
    return "en"