from typing import List
from PIL import Image

def export_to_gif(frames: List[Image.Image], output_path: str, fps: int) -> None:
    if not frames:
        raise ValueError("No frames provided")

    frame_duration = max(10, int(round(1000 / fps)))
    gif_frames: List[Image.Image] = []

    for img in frames:
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            rgba = img.convert("RGBA")
            alpha = rgba.split()[3]
            p_img = rgba.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=255)
            mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
            p_img.paste(255, mask)
            p_img.info["transparency"] = 255
            gif_frames.append(p_img)
        else:
            gif_frames.append(img.convert("P", palette=Image.Palette.ADAPTIVE))

    gif_frames[0].save(
        output_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=frame_duration,
        loop=0,
        disposal=2
    )