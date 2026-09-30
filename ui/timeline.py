import tkinter as tk

class CustomTimeline(tk.Canvas):
    def __init__(self, master, on_frame_change=None, **kwargs):
        super().__init__(master, height=26, bg="#202020", highlightthickness=0, **kwargs)
        self.total_frames = 0
        self.current_frame = 0
        self.on_frame_change = on_frame_change
        self.is_dragging = False

        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", lambda e: self.draw())

    def set_state(self, total: int, current: int) -> None:
        self.total_frames = total
        self.current_frame = min(current, max(0, total - 1))
        self.draw()

    def draw(self) -> None:
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()

        if self.total_frames <= 0 or width <= 20:
            return

        pad_x = 14
        track_y = height // 2
        track_w = width - (pad_x * 2)

        self.create_line(pad_x, track_y, width - pad_x, track_y, fill="#444444", width=3)
        step = track_w / (self.total_frames - 1) if self.total_frames > 1 else 0

        for i in range(self.total_frames):
            cx = pad_x + (i * step)
            if i == self.current_frame:
                self.create_oval(cx - 6, track_y - 6, cx + 6, track_y + 6, fill="#4CAF50", outline="#FFFFFF", width=2)
            else:
                self.create_oval(cx - 3, track_y - 3, cx + 3, track_y + 3, fill="#888888", outline="")

    def _frame_from_x(self, x: int) -> int:
        if self.total_frames <= 1:
            return 0
        pad_x = 14
        track_w = self.winfo_width() - (pad_x * 2)
        rel_x = max(0, min(x - pad_x, track_w))
        ratio = rel_x / track_w
        return int(round(ratio * (self.total_frames - 1)))

    def _on_click(self, event) -> None:
        self.is_dragging = True
        idx = self._frame_from_x(event.x)
        if self.on_frame_change:
            self.on_frame_change(idx)

    def _on_drag(self, event) -> None:
        if self.is_dragging:
            idx = self._frame_from_x(event.x)
            if self.on_frame_change:
                self.on_frame_change(idx)

    def _on_release(self, event) -> None:
        self.is_dragging = False