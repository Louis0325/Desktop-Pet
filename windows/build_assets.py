from pathlib import Path
import subprocess

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
SVG_DIR = ROOT / "build" / "svg"
ASSET_DIR = ROOT / "assets"


def main():
    subprocess.run(["node", str(ROOT / "generate_frames.js")], check=True)
    ASSET_DIR.mkdir(exist_ok=True)
    for path in ASSET_DIR.glob("*.png"):
        path.unlink()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 512, "height": 512}, device_scale_factor=1)
        page.goto("about:blank")
        for svg_path in sorted(SVG_DIR.glob("*.svg")):
            page.set_content(
                "<style>html,body{margin:0;width:512px;height:512px}</style>"
                + svg_path.read_text(encoding="utf-8")
            )
            page.locator("svg").screenshot(
                path=str(ASSET_DIR / (svg_path.stem + ".png")),
                omit_background=True,
            )
        browser.close()

    frames = [Image.open(path).convert("RGBA") for path in sorted(ASSET_DIR.glob("*.png"))]
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    left = max(0, min(box[0] for box in boxes) - 12)
    top = max(0, min(box[1] for box in boxes) - 12)
    right = min(512, max(box[2] for box in boxes) + 12)
    bottom = min(512, max(box[3] for box in boxes) + 12)
    for path in ASSET_DIR.glob("*.png"):
        with Image.open(path) as image:
            image.crop((left, top, right, bottom)).save(path)
    print(f"Generated {len(frames)} transparent frames at {right-left}x{bottom-top}")


if __name__ == "__main__":
    main()
