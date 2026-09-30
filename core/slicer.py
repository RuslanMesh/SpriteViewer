import time
from typing import List, Optional, Tuple
from PIL import Image

def calculate_grid_capacity(sheet_w: int, sheet_h: int, frame_w: int, frame_h: int, step_x: int, step_y: int) -> Tuple[int, int, int]:
    cols = 1 + (sheet_w - frame_w) // step_x if sheet_w >= frame_w and step_x > 0 else 0
    rows = 1 + (sheet_h - frame_h) // step_y if sheet_h >= frame_h and step_y > 0 else 0
    return cols, rows, cols * rows

def open_image_safe(path: str, retries: int = 3, delay: float = 0.05) -> Optional[Image.Image]:
    """Открывает изображение с повторными попытками при блокировке файла редактором (Ctrl+S в SAI)."""
    for _ in range(retries):
        try:
            with Image.open(path) as img:
                return img.copy()
        except (PermissionError, OSError):
            time.sleep(delay)
    return None

def slice_strip(img: Image.Image, frame_w: int, step_x: int, max_frames: Optional[int] = None) -> List[Image.Image]:
    frames: List[Image.Image] = []
    sheet_w, sheet_h = img.size
    curr_x = 0
    while curr_x + frame_w <= sheet_w:
        if max_frames is not None and len(frames) >= max_frames:
            break
        frames.append(img.crop((curr_x, 0, curr_x + frame_w, sheet_h)))
        curr_x += step_x
    return frames

def slice_grid(img: Image.Image, frame_w: int, frame_h: int, step_x: int, step_y: int, max_frames: Optional[int] = None) -> List[Image.Image]:
    frames: List[Image.Image] = []
    sheet_w, sheet_h = img.size
    curr_y = 0
    while curr_y + frame_h <= sheet_h:
        curr_x = 0
        while curr_x + frame_w <= sheet_w:
            if max_frames is not None and len(frames) >= user_frames_limit(max_frames):
                break
            frames.append(img.crop((curr_x, curr_y, curr_x + frame_w, curr_y + frame_h)))
            curr_x += step_x
        if max_frames is not None and len(frames) >= user_frames_limit(max_frames):
            break
        curr_y += step_y
    return frames

def user_frames_limit(val: Optional[int]) -> int:
    return val if val is not None else 999999