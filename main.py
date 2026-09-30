import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from typing import List, Optional
from PIL import Image, ImageTk

from core.config import load_config, save_config
from core.slicer import slice_strip, slice_grid, calculate_grid_capacity, open_image_safe
from core.exporter import export_to_gif
from locales.i18n import TRANSLATIONS, detect_system_language
from ui.timeline import CustomTimeline

def natural_keys(text: str):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

class SpriteViewerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_config()

        saved_lang = self.cfg.get("lang", "auto")
        self.lang = detect_system_language() if saved_lang == "auto" else saved_lang

        self.root.geometry(self.cfg.get("geometry", "780x620"))
        self.root.minsize(140, 140)

        self.mode = self.cfg.get("mode", "folder")
        self.sheet_layout = self.cfg.get("sheet_layout", "strip")

        self.folder_path = self.cfg.get("folder_path", "")
        self.single_file_path = self.cfg.get("single_file_path", "")
        self.file_mtime = 0

        self.file_list: List[str] = []
        self.cached_images: List[Image.Image] = []
        self.file_mtimes = {}
        self.current_frame = 0
        self.is_playing = False
        self.fps = max(1, min(60, self.cfg.get("fps", 12)))
        self.ui_visible = True

        self._build_ui()
        self._bind_keys()
        self._apply_initial_config()
        self._update_ui_text()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._playback_loop()
        self._watch_loop()

    def t(self, key: str) -> str:
        return TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)

    def _validate_digits_only(self, P: str) -> bool:
        return P == "" or P.isdigit()

    def _build_ui(self) -> None:
        vcmd = (self.root.register(self._validate_digits_only), "%P")

        self.mini_bar = tk.Frame(self.root, bg="#1a1a1a", height=22)
        self.mini_bar.pack(side=tk.TOP, fill=tk.X)

        self.btn_toggle_ui = tk.Button(
            self.mini_bar, text="", bg="#2b2b2b", fg="#cccccc",
            relief=tk.FLAT, font=("Arial", 8), command=self.toggle_ui,
            takefocus=False
        )
        self.btn_toggle_ui.pack(side=tk.LEFT, padx=4, pady=1)

        self.btn_lang = tk.Button(
            self.mini_bar, text=self.lang.upper(), bg="#2b2b2b", fg="#aaaaaa",
            relief=tk.FLAT, font=("Arial", 8, "bold"), width=3, command=self.switch_language,
            takefocus=False
        )
        self.btn_lang.pack(side=tk.LEFT, padx=2, pady=1)

        self.btn_reset_zoom = tk.Button(
            self.mini_bar, text="[ 1:1 ]", bg="#2b2b2b", fg="#4CAF50",
            relief=tk.FLAT, font=("Arial", 8, "bold"), command=self.reset_to_native_resolution,
            takefocus=False
        )
        self.btn_reset_zoom.pack(side=tk.RIGHT, padx=4, pady=1)

        self.lbl_zoom = tk.Label(self.mini_bar, text="100%", bg="#1a1a1a", fg="#888888", font=("Arial", 8))
        self.lbl_zoom.pack(side=tk.RIGHT, padx=2)

        self.collapsible_ui = ttk.Frame(self.root)
        self.collapsible_ui.pack(side=tk.TOP, fill=tk.X)

        top_frame = ttk.Frame(self.collapsible_ui, padding=4)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_folder = ttk.Button(top_frame, text="", width=7, command=self.select_folder, takefocus=False)
        self.btn_folder.pack(side=tk.LEFT, padx=1)

        self.btn_file = ttk.Button(top_frame, text="", width=12, command=self.select_file, takefocus=False)
        self.btn_file.pack(side=tk.LEFT, padx=1)

        self.btn_play = ttk.Button(top_frame, text="", width=9, command=self.toggle_play, takefocus=False)
        self.btn_play.pack(side=tk.LEFT, padx=1)

        self.lbl_fps_tag = ttk.Label(top_frame, text="")
        self.lbl_fps_tag.pack(side=tk.LEFT, padx=(4, 1))

        self.spin_fps = ttk.Spinbox(
            top_frame, from_=1, to=60, width=3, command=self.update_fps,
            validate="key", validatecommand=vcmd
        )
        self.spin_fps.set(self.fps)
        self.spin_fps.pack(side=tk.LEFT)
        self.spin_fps.bind("<Return>", lambda e: self._on_field_enter(self.update_fps))

        self.btn_export_gif = ttk.Button(top_frame, text="", width=6, command=self.on_export_gif, takefocus=False)
        self.btn_export_gif.pack(side=tk.LEFT, padx=(6, 2))

        self.always_on_top_var = tk.BooleanVar(value=bool(self.cfg.get("always_on_top", False)))
        self.chk_ontop = ttk.Checkbutton(
            top_frame, text="", variable=self.always_on_top_var, command=self.toggle_always_on_top,
            takefocus=False
        )
        self.chk_ontop.pack(side=tk.LEFT, padx=4)

        self.lbl_info = ttk.Label(top_frame, text="")
        self.lbl_info.pack(side=tk.RIGHT, padx=4)

        self.sheet_frame = ttk.Frame(self.collapsible_ui, padding=4)

        self.btn_sheet_type = ttk.Button(
            self.sheet_frame, text="", command=self.toggle_sheet_layout, takefocus=False
        )
        self.btn_sheet_type.pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_w_tag = ttk.Label(self.sheet_frame, text="")
        self.lbl_w_tag.pack(side=tk.LEFT, padx=(1, 1))
        self.entry_frame_w = ttk.Entry(self.sheet_frame, width=4, validate="key", validatecommand=vcmd)
        self.entry_frame_w.insert(0, str(self.cfg.get("frame_w", "300")))
        self.entry_frame_w.pack(side=tk.LEFT, padx=(0, 3))
        self.entry_frame_w.bind("<KeyRelease>", lambda e: self._sync_cfg())
        self.entry_frame_w.bind("<Return>", lambda e: self._on_field_enter(lambda: self.reload_data(force=True, user_action=True)))

        self.lbl_step_x_tag = ttk.Label(self.sheet_frame, text="")
        self.lbl_step_x_tag.pack(side=tk.LEFT, padx=(2, 1))
        self.entry_step_x = ttk.Entry(self.sheet_frame, width=4, validate="key", validatecommand=vcmd)
        self.entry_step_x.insert(0, str(self.cfg.get("step_x", "150")))
        self.entry_step_x.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_step_x.bind("<KeyRelease>", lambda e: self._sync_cfg())
        self.entry_step_x.bind("<Return>", lambda e: self._on_field_enter(lambda: self.reload_data(force=True, user_action=True)))

        self.grid_controls_container = ttk.Frame(self.sheet_frame)

        self.lbl_h_tag = ttk.Label(self.grid_controls_container, text="")
        self.lbl_h_tag.pack(side=tk.LEFT, padx=(2, 1))
        self.entry_frame_h = ttk.Entry(self.grid_controls_container, width=4, validate="key", validatecommand=vcmd)
        self.entry_frame_h.insert(0, str(self.cfg.get("frame_h", "300")))
        self.entry_frame_h.pack(side=tk.LEFT, padx=(0, 3))
        self.entry_frame_h.bind("<KeyRelease>", lambda e: self._sync_cfg())
        self.entry_frame_h.bind("<Return>", lambda e: self._on_field_enter(lambda: self.reload_data(force=True, user_action=True)))

        self.lbl_step_y_tag = ttk.Label(self.grid_controls_container, text="")
        self.lbl_step_y_tag.pack(side=tk.LEFT, padx=(2, 1))
        self.entry_step_y = ttk.Entry(self.grid_controls_container, width=4, validate="key", validatecommand=vcmd)
        self.entry_step_y.insert(0, str(self.cfg.get("step_y", "300")))
        self.entry_step_y.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_step_y.bind("<KeyRelease>", lambda e: self._sync_cfg())
        self.entry_step_y.bind("<Return>", lambda e: self._on_field_enter(lambda: self.reload_data(force=True, user_action=True)))

        self.lbl_frames_tag = ttk.Label(self.sheet_frame, text="")
        self.lbl_frames_tag.pack(side=tk.LEFT, padx=(2, 1))
        self.entry_max_frames = ttk.Entry(self.sheet_frame, width=3, validate="key", validatecommand=vcmd)
        self.entry_max_frames.insert(0, str(self.cfg.get("max_frames", "4")))
        self.entry_max_frames.pack(side=tk.LEFT, padx=(0, 4))
        self.entry_max_frames.bind("<KeyRelease>", lambda e: self._sync_cfg())
        self.entry_max_frames.bind("<Return>", lambda e: self._on_field_enter(lambda: self.reload_data(force=True, user_action=True)))

        self.btn_apply_cut = ttk.Button(
            self.sheet_frame, text="", width=9, 
            command=lambda: self.reload_data(force=True, user_action=True), 
            takefocus=False
        )
        self.btn_apply_cut.pack(side=tk.LEFT, padx=2)

        self.timeline = CustomTimeline(self.root, on_frame_change=self.on_timeline_click)
        self.timeline.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg="#262626", highlightthickness=0, takefocus=True)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.show_frame(self.current_frame))

    def _apply_initial_config(self) -> None:
        self.root.wm_attributes("-topmost", self.always_on_top_var.get())
        if self.mode == "sheet" and os.path.exists(self.single_file_path):
            self.sheet_frame.pack(side=tk.TOP, fill=tk.X)
            self._apply_sheet_layout_view()
            self.reload_data(force=True, user_action=False)
        elif self.mode == "folder" and os.path.exists(self.folder_path):
            self.sheet_frame.pack_forget()
            self.reload_data(force=True, user_action=False)

    def _on_field_enter(self, callback_fn) -> None:
        callback_fn()
        self.canvas.focus_set()

    def _bind_keys(self) -> None:
        def on_global_click(event):
            if not isinstance(event.widget, (ttk.Entry, tk.Entry, ttk.Spinbox, tk.Spinbox)):
                self.canvas.focus_set()

        self.root.bind_all("<Button-1>", on_global_click)

        def on_key_press(event):
            if event.keycode == 80:
                self.canvas.focus_set()
                self.toggle_play()
                return "break"
            if event.keycode == 72:
                self.canvas.focus_set()
                self.toggle_ui()
                return "break"
            if event.keysym == "Left":
                self.canvas.focus_set()
                self.prev_frame()
                return "break"
            if event.keysym == "Right":
                self.canvas.focus_set()
                self.next_frame()
                return "break"

        self.root.bind_all("<Key>", on_key_press)

    def toggle_sheet_layout(self) -> None:
        switching_to_strip = (self.sheet_layout == "grid")
        self.sheet_layout = "strip" if switching_to_strip else "grid"

        if switching_to_strip and self.single_file_path and os.path.exists(self.single_file_path):
            try:
                fw = int(self.entry_frame_w.get())
                sx = int(self.entry_step_x.get())
                img = open_image_safe(self.single_file_path)
                if img and img.width >= fw and sx > 0:
                    max_possible = 1 + (img.width - fw) // sx
                    raw_max = self.entry_max_frames.get().strip()
                    curr = int(raw_max) if raw_max.isdigit() else 0
                    if curr > max_possible or curr == 0:
                        self.entry_max_frames.delete(0, tk.END)
                        self.entry_max_frames.insert(0, str(max_possible))
            except Exception:
                pass

        self._apply_sheet_layout_view()
        self.reload_data(force=True, user_action=False)
        self._sync_cfg()

    def _apply_sheet_layout_view(self) -> None:
        if self.sheet_layout == "grid":
            self.btn_sheet_type.config(text=f"⊞ {self.t('mode_grid')}")
            self.grid_controls_container.pack(side=tk.LEFT, before=self.lbl_frames_tag)
        else:
            self.btn_sheet_type.config(text=f"━ {self.t('mode_strip')}")
            self.grid_controls_container.pack_forget()

    def reset_to_native_resolution(self) -> None:
        if not self.cached_images:
            return

        img = self.cached_images[self.current_frame]
        img_w, img_h = img.size

        self.root.update_idletasks()
        ui_height = self.mini_bar.winfo_height() + self.timeline.winfo_height()
        if self.ui_visible:
            ui_height += self.collapsible_ui.winfo_height()

        target_w = max(140, img_w)
        target_h = max(140, img_h + ui_height)

        cur_x = self.root.winfo_x()
        cur_y = self.root.winfo_y()
        self.root.geometry(f"{target_w}x{target_h}+{cur_x}+{cur_y}")

    def switch_language(self) -> None:
        cycle = {"ru": "en", "en": "es", "es": "ru"}
        self.lang = cycle.get(self.lang, "en")
        self.btn_lang.config(text=self.lang.upper())
        self._update_ui_text()
        self._sync_cfg()

    def _update_ui_text(self) -> None:
        self.root.title(self.t("title"))
        self.btn_toggle_ui.config(text=self.t("hide_ui") if self.ui_visible else self.t("show_ui"))
        self.btn_folder.config(text=self.t("folder"))
        self.btn_file.config(text=self.t("sheet"))
        self.btn_play.config(text=self.t("pause") if self.is_playing else self.t("play"))
        self.btn_export_gif.config(text=self.t("export_gif"))
        self.lbl_fps_tag.config(text=self.t("fps"))
        self.chk_ontop.config(text=self.t("ontop"))
        self.lbl_w_tag.config(text=self.t("width"))
        self.lbl_h_tag.config(text=self.t("height"))
        self.lbl_step_x_tag.config(text=self.t("step_x"))
        self.lbl_step_y_tag.config(text=self.t("step_y"))
        self.lbl_frames_tag.config(text=self.t("max_frames"))
        self.btn_apply_cut.config(text=self.t("apply"))
        self.lbl_info.config(text=f"{len(self.cached_images)} {self.t('frames_count')}")
        self._apply_sheet_layout_view()

    def toggle_ui(self) -> None:
        self.root.update_idletasks()
        cur_w = self.root.winfo_width()
        cur_h = self.root.winfo_height()
        cur_x = self.root.winfo_x()
        cur_y = self.root.winfo_y()

        if self.ui_visible:
            ui_h = self.collapsible_ui.winfo_height()
            self.collapsible_ui.pack_forget()
            self.ui_visible = False
            self.btn_toggle_ui.config(text=self.t("show_ui"))

            new_h = max(140, cur_h - ui_h)
            self.root.geometry(f"{cur_w}x{new_h}+{cur_x}+{cur_y}")
        else:
            self.collapsible_ui.pack(side=tk.TOP, fill=tk.X, before=self.canvas)
            self.ui_visible = True
            self.btn_toggle_ui.config(text=self.t("hide_ui"))

            self.root.update_idletasks()
            ui_h = self.collapsible_ui.winfo_height()
            new_h = cur_h + ui_h
            self.root.geometry(f"{cur_w}x{new_h}+{cur_x}+{cur_y}")

    def toggle_always_on_top(self) -> None:
        is_top = self.always_on_top_var.get()
        self.root.wm_attributes("-topmost", is_top)
        self._sync_cfg()

    def select_folder(self) -> None:
        path = filedialog.askdirectory(title=self.t("dlg_folder"))
        if path:
            self.mode = "folder"
            self.folder_path = path
            self.sheet_frame.pack_forget()
            self.reload_data(force=True, user_action=True)
            self._sync_cfg()

    def select_file(self) -> None:
        filetypes = [("Images", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")]
        path = filedialog.askopenfilename(title=self.t("dlg_file"), filetypes=filetypes)
        if path:
            self.mode = "sheet"
            self.single_file_path = path
            self.sheet_frame.pack(side=tk.TOP, fill=tk.X)
            self._apply_sheet_layout_view()
            self.reload_data(force=True, user_action=True)
            self._sync_cfg()

    def on_export_gif(self) -> None:
        if not self.cached_images:
            messagebox.showwarning(self.t("title"), self.t("export_no_frames"))
            return

        filepath = filedialog.asksaveasfilename(
            title=self.t("dlg_save_gif"),
            defaultextension=".gif",
            filetypes=[("GIF Image", "*.gif")]
        )
        if not filepath:
            return

        try:
            export_to_gif(self.cached_images, filepath, self.fps)
            messagebox.showinfo(self.t("title"), self.t("export_success"))
        except Exception as e:
            messagebox.showerror(self.t("title"), str(e))

    def _slice_current_sheet(self, show_warning: bool) -> List[Image.Image]:
        img = open_image_safe(self.single_file_path)
        if img is None:
            return []

        try:
            frame_w = int(self.entry_frame_w.get())
            step_x = int(self.entry_step_x.get())
            if frame_w <= 0 or step_x <= 0:
                return []
        except ValueError:
            return []

        raw_max = self.entry_max_frames.get().strip()
        user_max_frames = int(raw_max) if raw_max.isdigit() and int(raw_max) > 0 else None
        sheet_w, sheet_h = img.size

        if self.sheet_layout == "strip":
            avail_count = 1 + (sheet_w - frame_w) // step_x if sheet_w >= frame_w else 0
            if user_max_frames is not None and user_max_frames > avail_count and show_warning:
                needed_w = (user_max_frames - 1) * step_x + frame_w
                err_msg = self.t("err_strip_overflow").format(
                    req_frame=user_max_frames,
                    curr_w=sheet_w,
                    avail_count=avail_count,
                    needed_w=needed_w,
                    missing_w=needed_w - sheet_w
                )
                messagebox.showwarning(self.t("err_title"), err_msg)
            return slice_strip(img, frame_w, step_x, user_max_frames)
        else:
            try:
                frame_h = int(self.entry_frame_h.get()) if self.entry_frame_h.get().isdigit() else sheet_h
            except ValueError:
                frame_h = sheet_h

            try:
                step_y = int(self.entry_step_y.get()) if self.entry_step_y.get().isdigit() else frame_h
            except ValueError:
                step_y = frame_h

            cols, rows, total_capacity = calculate_grid_capacity(sheet_w, sheet_h, frame_w, frame_h, step_x, step_y)
            if user_max_frames is not None and user_max_frames > total_capacity and show_warning:
                if cols > 0:
                    needed_row = (user_max_frames - 1) // cols
                    needed_col = (user_max_frames - 1) % cols
                    needed_h = needed_row * step_y + frame_h
                    needed_w = needed_col * step_x + frame_w
                    if needed_row >= rows:
                        suggestion = self.t("hint_vertical").format(
                            row=needed_row + 1, col=needed_col + 1,
                            missing_h=needed_h - sheet_h, needed_h=needed_h
                        )
                    else:
                        suggestion = self.t("hint_horizontal").format(
                            missing_w=needed_w - sheet_w, needed_w=needed_w
                        )
                else:
                    suggestion = self.t("hint_too_narrow").format(sheet_w=sheet_w, frame_w=frame_w)

                err_msg = self.t("err_grid_overflow").format(
                    req_frame=user_max_frames, curr_w=sheet_w, curr_h=sheet_h,
                    cols=cols, rows=rows, avail_count=total_capacity, suggestion=suggestion
                )
                messagebox.showwarning(self.t("err_title"), err_msg)

            return slice_grid(img, frame_w, frame_h, step_x, step_y, user_max_frames)

    def reload_data(self, force: bool = False, user_action: bool = False) -> None:
        if self.mode == "folder":
            self._reload_folder(force)
        elif self.mode == "sheet":
            self._reload_sheet(force, show_warning=user_action)
        self._sync_cfg()

    def _reload_sheet(self, force: bool = False, show_warning: bool = False) -> None:
        if not self.single_file_path or not os.path.exists(self.single_file_path):
            return

        try:
            mtime = os.path.getmtime(self.single_file_path)
        except OSError:
            return

        if not force and mtime == self.file_mtime:
            return

        new_cached = self._slice_current_sheet(show_warning=show_warning)
        if not new_cached:
            return

        self.file_mtime = mtime
        self.cached_images = new_cached
        self._update_timeline_and_labels()

    def _reload_folder(self, force: bool = False) -> None:
        if not self.folder_path or not os.path.exists(self.folder_path):
            return

        supported_exts = (".png", ".jpg", ".jpeg", ".bmp")
        all_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(supported_exts)]
        all_files.sort(key=natural_keys)

        changed = force or (len(all_files) != len(self.file_list))
        current_mtimes = {}

        for f in all_files:
            full_p = os.path.join(self.folder_path, f)
            try:
                mtime = os.path.getmtime(full_p)
                current_mtimes[f] = mtime
                if self.file_mtimes.get(f) != mtime:
                    changed = True
            except OSError:
                return

        if not changed:
            return

        new_cached: List[Image.Image] = []
        for f in all_files:
            img = open_image_safe(os.path.join(self.folder_path, f))
            if img:
                new_cached.append(img)

        self.file_list = all_files
        self.cached_images = new_cached
        self.file_mtimes = current_mtimes
        self._update_timeline_and_labels()

    def _update_timeline_and_labels(self) -> None:
        count = len(self.cached_images)
        self.lbl_info.config(text=f"{count} {self.t('frames_count')}")
        if count > 0:
            if self.current_frame >= count:
                self.current_frame = 0
            self.timeline.set_state(count, self.current_frame)
            self.show_frame(self.current_frame)
        else:
            self.timeline.set_state(0, 0)
            self.canvas.delete("all")
            self.lbl_zoom.config(text="100%")

    def show_frame(self, index: int) -> None:
        if not self.cached_images:
            return

        self.current_frame = index % len(self.cached_images)
        self.timeline.set_state(len(self.cached_images), self.current_frame)

        img = self.cached_images[self.current_frame]
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()

        if c_width <= 2 or c_height <= 2:
            return

        img_w, img_h = img.size
        scale = min(c_width / img_w, c_height / img_h, 8.0)
        zoom_pct = int(scale * 100)
        self.lbl_zoom.config(text=f"{self.t('zoom')} {zoom_pct}% ({img_w}x{img_h})")

        new_w = max(1, int(img_w * scale))
        new_h = max(1, int(img_h * scale))

        resized = img.resize((new_w, new_h), Image.Resampling.NEAREST)
        self.tk_img = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        self.canvas.create_image(c_width // 2, c_height // 2, anchor=tk.CENTER, image=self.tk_img)

    def _playback_loop(self) -> None:
        if self.is_playing and self.cached_images:
            self.current_frame = (self.current_frame + 1) % len(self.cached_images)
            self.show_frame(self.current_frame)

        delay = max(10, int(1000 / self.fps))
        self.root.after(delay, self._playback_loop)

    def _watch_loop(self) -> None:
        self.reload_data(force=False, user_action=False)
        self.root.after(1000, self._watch_loop)

    def toggle_play(self) -> None:
        self.is_playing = not self.is_playing
        self.btn_play.config(text=self.t("pause") if self.is_playing else self.t("play"))

    def prev_frame(self) -> None:
        self.is_playing = False
        self.btn_play.config(text=self.t("play"))
        if self.cached_images:
            self.current_frame = (self.current_frame - 1) % len(self.cached_images)
            self.show_frame(self.current_frame)

    def next_frame(self) -> None:
        self.is_playing = False
        self.btn_play.config(text=self.t("play"))
        if self.cached_images:
            self.current_frame = (self.current_frame + 1) % len(self.cached_images)
            self.show_frame(self.current_frame)

    def on_timeline_click(self, frame_idx: int) -> None:
        if not self.cached_images:
            return
        self.canvas.focus_set()
        self.is_playing = False
        self.btn_play.config(text=self.t("play"))
        self.show_frame(frame_idx)

    def update_fps(self) -> None:
        try:
            val = int(self.spin_fps.get())
            self.fps = max(1, min(60, val))
            self._sync_cfg()
        except ValueError:
            pass

    def _sync_cfg(self) -> None:
        try:
            geom = self.root.geometry()
        except Exception:
            geom = "780x620"

        self.cfg.update({
            "lang": self.lang,
            "mode": self.mode,
            "sheet_layout": self.sheet_layout,
            "folder_path": self.folder_path,
            "single_file_path": self.single_file_path,
            "frame_w": self.entry_frame_w.get(),
            "frame_h": self.entry_frame_h.get(),
            "step_x": self.entry_step_x.get(),
            "step_y": self.entry_step_y.get(),
            "max_frames": self.entry_max_frames.get(),
            "fps": self.fps,
            "always_on_top": self.always_on_top_var.get(),
            "geometry": geom
        })
        save_config(self.cfg)

    def _on_close(self) -> None:
        self._sync_cfg()
        self.root.destroy()

if __name__ == "__main__":
    app_root = tk.Tk()
    viewer = SpriteViewerApp(app_root)
    app_root.mainloop()