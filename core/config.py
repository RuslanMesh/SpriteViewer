import json
import sys
from pathlib import Path
from typing import Any, Dict

def get_app_dir() -> Path:
    """Возвращает абсолютный путь к папке приложения (.exe или main.py)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

CONFIG_PATH = get_app_dir() / "viewer_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "lang": "auto",
    "mode": "folder",
    "sheet_layout": "strip",
    "folder_path": "",
    "single_file_path": "",
    "frame_w": "300",
    "frame_h": "300",
    "step_x": "150",
    "step_y": "300",
    "max_frames": "4",
    "fps": 12,
    "always_on_top": False,
    "geometry": "780x620"
}

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(data)
            return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(cfg: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except OSError:
        pass