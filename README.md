# 🎬 SpriteViewer

A lightweight, portable live preview tool for 2D animators and game developers. Built specifically to streamline frame-by-frame animation workflows in software like **Paint Tool SAI**, **Photoshop**, and **Clip Studio Paint**.

---

## ✨ Features

- 🔄 **Live Hot-Reloading:** Automatically monitors your active folder or sprite sheet. Updates playback instantly upon saving (`Ctrl + S`).
- 🎞️ **Flexible Slicing Layouts:**
  - **Strip (Linear):** Horizontal frame sequence with custom frame width, step, and limit.
  - **Grid (Matrix):** 2D matrix sheets with automatic row/column calculation and space-overflow hints.
- 📌 **Always on Top & Compact Mode:** Keep the reference pinned over your workspace. Press `H` to collapse the UI and retain native sprite proportions.
- 🎯 **Interactive Timeline:** Individual frame step markers with instant scrub and navigation.
- 🔍 **Native 1:1 Zoom & Reset:** Nearest-neighbor scaling for pixel-art clarity with a single-click 1:1 canvas reset button.
- 💾 **GIF Export:** One-click export to animated GIF with transparent background preservation and frame-accurate timing.
- 🌐 **Multilingual:** Supports English, Russian, and Spanish with automatic system locale detection.
- 📦 **100% Portable:** Zero installation required. Keeps configuration strictly local next to the executable.

---

## 📥 Download Executable

Ready-to-use standalone Windows binaries require no Python installation:

👉 **[Download Latest SpriteViewer.exe](https://github.com/RuslanMesh/SpriteViewer/releases/latest)**

---

## ⌨️ Controls & Shortcuts

| Action | Shortcut / Input |
| :--- | :--- |
| **Play / Pause** | `P` (works regardless of system language layout) |
| **Collapse / Expand UI** | `H` |
| **Step Backward / Forward** | `Left Arrow` / `Right Arrow` |
| **Scrub Timeline** | `Left Click` or `Drag` on timeline |
| **Reset Scale (1:1)** | `[ 1:1 ]` button in the top bar |

---

## 🛠️ Running from Source

1. Clone the repository:
   ```bash
   git clone [https://github.com/RuslanMesh/SpriteViewer.git]
   cd SpriteViewer
   ```
   
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python main.py
    ```


## 🔨 Building Executable

To package into a single standalone `.exe`:

```bash
pip install pyinstaller
python -m PyInstaller --noconsole --onefile --name "SpriteViewer" main.py
```

The compiled binary will be placed in the dist/ directory.

## 📄 License
Distributed under the MIT License. See LICENSE for details.