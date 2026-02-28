#!/usr/bin/env python3
"""Generate terminal preview images for iTerm2 .itermcolors color schemes."""

import os
import sys
import plistlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
FONT_SIZE = 16
LINE_HEIGHT = 22
PADDING_X = 24
PADDING_Y = 20
TITLE_BAR_HEIGHT = 38
CHAR_WIDTH = 9.6  # approximate monospace character width at 16pt
COLS = 80
IMAGE_WIDTH = int(COLS * CHAR_WIDTH + PADDING_X * 2)

# Color key mappings from itermcolors to our internal names
COLOR_KEYS = {
    "Ansi 0 Color": "black",
    "Ansi 1 Color": "red",
    "Ansi 2 Color": "green",
    "Ansi 3 Color": "yellow",
    "Ansi 4 Color": "blue",
    "Ansi 5 Color": "magenta",
    "Ansi 6 Color": "cyan",
    "Ansi 7 Color": "white",
    "Ansi 8 Color": "bright_black",
    "Ansi 9 Color": "bright_red",
    "Ansi 10 Color": "bright_green",
    "Ansi 11 Color": "bright_yellow",
    "Ansi 12 Color": "bright_blue",
    "Ansi 13 Color": "bright_magenta",
    "Ansi 14 Color": "bright_cyan",
    "Ansi 15 Color": "bright_white",
    "Foreground Color": "fg",
    "Background Color": "bg",
    "Bold Color": "bold",
    "Cursor Color": "cursor",
    "Cursor Text Color": "cursor_text",
    "Selection Color": "selection",
}


def parse_color(color_dict):
    """Convert an iTerm color dict to an RGB tuple."""
    r = color_dict.get("Red Component", 0.0)
    g = color_dict.get("Green Component", 0.0)
    b = color_dict.get("Blue Component", 0.0)
    return (int(r * 255), int(g * 255), int(b * 255))


def load_scheme(path):
    """Load a .itermcolors file and return a dict of color names to RGB tuples."""
    with open(path, "rb") as f:
        data = plistlib.load(f)
    colors = {}
    for key, name in COLOR_KEYS.items():
        if key in data:
            colors[name] = parse_color(data[key])
    # Fallbacks
    if "fg" not in colors:
        colors["fg"] = (204, 204, 204)
    if "bg" not in colors:
        colors["bg"] = (0, 0, 0)
    if "bold" not in colors:
        colors["bold"] = colors["fg"]
    if "cursor" not in colors:
        colors["cursor"] = colors["fg"]
    if "selection" not in colors:
        colors["selection"] = (80, 80, 80)
    # Ensure all 16 ANSI colors exist with defaults
    defaults = [
        (0, 0, 0), (204, 0, 0), (0, 204, 0), (204, 204, 0),
        (0, 0, 204), (204, 0, 204), (0, 204, 204), (204, 204, 204),
        (85, 85, 85), (255, 85, 85), (85, 255, 85), (255, 255, 85),
        (85, 85, 255), (255, 85, 255), (85, 255, 255), (255, 255, 255),
    ]
    ansi_names = [
        "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
        "bright_black", "bright_red", "bright_green", "bright_yellow",
        "bright_blue", "bright_magenta", "bright_cyan", "bright_white",
    ]
    for name, default in zip(ansi_names, defaults):
        if name not in colors:
            colors[name] = default
    return colors


def darken(color, factor=0.6):
    return tuple(int(c * factor) for c in color)


def lighten(color, factor=0.3):
    return tuple(min(255, int(c + (255 - c) * factor)) for c in color)


def draw_title_bar(draw, width, scheme_name, bg_color):
    """Draw a macOS-style title bar."""
    # Title bar background (slightly different from terminal bg)
    r, g, b = bg_color
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    if brightness > 128:
        title_bg = darken(bg_color, 0.85)
        title_fg = darken(bg_color, 0.4)
    else:
        title_bg = lighten(bg_color, 0.12)
        title_fg = lighten(bg_color, 0.4)

    draw.rectangle([0, 0, width, TITLE_BAR_HEIGHT], fill=title_bg)
    # Separator line
    draw.line([0, TITLE_BAR_HEIGHT, width, TITLE_BAR_HEIGHT],
              fill=darken(title_bg, 0.7), width=1)

    # Traffic light buttons
    btn_y = TITLE_BAR_HEIGHT // 2
    btn_colors = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]
    for i, color in enumerate(btn_colors):
        x = 16 + i * 22
        draw.ellipse([x - 6, btn_y - 6, x + 6, btn_y + 6], fill=color)

    # Scheme name centered in title bar
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except (OSError, IOError):
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), scheme_name, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) / 2, (TITLE_BAR_HEIGHT - 14) / 2), scheme_name,
              fill=title_fg, font=font)


def generate_preview(scheme_path, output_path):
    """Generate a terminal preview image for a color scheme."""
    scheme_name = Path(scheme_path).stem
    colors = load_scheme(scheme_path)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", FONT_SIZE)
        bold_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", FONT_SIZE)
    except (OSError, IOError):
        font = ImageFont.load_default()
        bold_font = font

    # Build the sample content as a list of lines, each line is a list of (text, color, is_bold)
    lines = []

    # Line 1: prompt with directory
    lines.append([
        ("user", colors["green"], True),
        ("@", colors["fg"], False),
        ("host", colors["blue"], True),
        (" ", colors["fg"], False),
        ("~/projects/demo", colors["cyan"], False),
        (" $ ", colors["fg"], False),
        ("ls -la", colors["bright_white"], True),
    ])

    # Line 2-4: ls output
    lines.append([
        ("total 42", colors["fg"], False),
    ])
    lines.append([
        ("drwxr-xr-x  ", colors["fg"], False),
        ("5", colors["bright_white"], False),
        (" user staff ", colors["fg"], False),
        (" 160 Feb 28 ", colors["fg"], False),
        (".", colors["bold"], True),
    ])
    lines.append([
        ("-rw-r--r--  ", colors["fg"], False),
        ("1", colors["bright_white"], False),
        (" user staff ", colors["fg"], False),
        ("2048 Feb 28 ", colors["fg"], False),
        ("README.md", colors["fg"], False),
    ])
    lines.append([
        ("-rwxr-xr-x  ", colors["fg"], False),
        ("1", colors["bright_white"], False),
        (" user staff ", colors["fg"], False),
        ("8192 Feb 28 ", colors["fg"], False),
        ("build.sh", colors["green"], True),
    ])
    lines.append([
        ("drwxr-xr-x  ", colors["fg"], False),
        ("3", colors["bright_white"], False),
        (" user staff ", colors["fg"], False),
        ("  96 Feb 28 ", colors["fg"], False),
        ("src/", colors["blue"], True),
    ])

    # Blank line
    lines.append([])

    # Prompt + git status
    lines.append([
        ("user", colors["green"], True),
        ("@", colors["fg"], False),
        ("host", colors["blue"], True),
        (" ", colors["fg"], False),
        ("~/projects/demo", colors["cyan"], False),
        (" (", colors["fg"], False),
        ("main", colors["magenta"], True),
        (") $ ", colors["fg"], False),
        ("git status", colors["bright_white"], True),
    ])
    lines.append([
        ("On branch ", colors["fg"], False),
        ("main", colors["magenta"], True),
    ])
    lines.append([
        ("Changes not staged for commit:", colors["yellow"], False),
    ])
    lines.append([
        ("  modified:   ", colors["fg"], False),
        ("src/app.py", colors["red"], False),
    ])
    lines.append([
        ("  modified:   ", colors["fg"], False),
        ("src/utils.py", colors["red"], False),
    ])

    # Blank line
    lines.append([])

    # Color swatches - normal colors
    lines.append([
        ("  Normal:  ", colors["fg"], False),
    ] + [
        ("  %s  " % name, colors[name], False)
        for name in ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    ])

    # Color swatches - bright colors
    lines.append([
        ("  Bright:  ", colors["fg"], False),
    ] + [
        ("  %s  " % name.replace("bright_", ""), colors[name], True)
        for name in ["bright_black", "bright_red", "bright_green", "bright_yellow",
                      "bright_blue", "bright_magenta", "bright_cyan", "bright_white"]
    ])

    # Blank line
    lines.append([])

    # Color block row - normal
    color_block_line_normal = ("color_blocks_normal",
        ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"])
    color_block_line_bright = ("color_blocks_bright",
        ["bright_black", "bright_red", "bright_green", "bright_yellow",
         "bright_blue", "bright_magenta", "bright_cyan", "bright_white"])

    # Prompt line
    lines.append([
        ("user", colors["green"], True),
        ("@", colors["fg"], False),
        ("host", colors["blue"], True),
        (" ", colors["fg"], False),
        ("~/projects/demo", colors["cyan"], False),
        (" $ ", colors["fg"], False),
        ("echo \"Hello, World!\"", colors["bright_yellow"], False),
    ])
    lines.append([
        ("Hello, World!", colors["fg"], False),
    ])

    # Blank line
    lines.append([])

    # Cursor line
    lines.append([
        ("user", colors["green"], True),
        ("@", colors["fg"], False),
        ("host", colors["blue"], True),
        (" ", colors["fg"], False),
        ("~/projects/demo", colors["cyan"], False),
        (" $ ", colors["fg"], False),
    ])

    num_text_lines = len(lines)
    # +2 for color block rows
    total_content_lines = num_text_lines + 2
    image_height = TITLE_BAR_HEIGHT + PADDING_Y * 2 + total_content_lines * LINE_HEIGHT

    img = Image.new("RGB", (IMAGE_WIDTH, image_height), colors["bg"])
    draw = ImageDraw.Draw(img)

    # Draw title bar
    draw_title_bar(draw, IMAGE_WIDTH, scheme_name, colors["bg"])

    y = TITLE_BAR_HEIGHT + PADDING_Y
    color_blocks_inserted = False

    for i, line_parts in enumerate(lines):
        if not line_parts:
            y += LINE_HEIGHT
            continue

        x = PADDING_X
        for text, color, is_bold in line_parts:
            f = bold_font if is_bold else font
            draw.text((x, y), text, fill=color, font=f)
            bbox = draw.textbbox((0, 0), text, font=f)
            x += bbox[2] - bbox[0]
        y += LINE_HEIGHT

        # Insert color blocks after the "Bright:" line
        if i == 14 and not color_blocks_inserted:
            color_blocks_inserted = True
            y += 4
            block_w = (IMAGE_WIDTH - PADDING_X * 2) // 8
            block_h = LINE_HEIGHT - 2
            # Normal colors
            for j, name in enumerate(color_block_line_normal[1]):
                bx = PADDING_X + j * block_w
                draw.rectangle([bx, y, bx + block_w - 2, y + block_h], fill=colors[name])
            y += LINE_HEIGHT
            # Bright colors
            for j, name in enumerate(color_block_line_bright[1]):
                bx = PADDING_X + j * block_w
                draw.rectangle([bx, y, bx + block_w - 2, y + block_h], fill=colors[name])
            y += LINE_HEIGHT + 4

    # Draw cursor block on last line
    cursor_x = PADDING_X
    last_line = lines[-1]
    for text, color, is_bold in last_line:
        f = bold_font if is_bold else font
        bbox = draw.textbbox((0, 0), text, font=f)
        cursor_x += bbox[2] - bbox[0]
    draw.rectangle([cursor_x, y - LINE_HEIGHT + 3, cursor_x + 10, y - 3], fill=colors["cursor"])

    img.save(output_path, "PNG")


def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "/data/presets"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/data/previews"

    os.makedirs(output_dir, exist_ok=True)

    itermcolors_files = sorted(Path(input_dir).glob("*.itermcolors"))
    if not itermcolors_files:
        print(f"No .itermcolors files found in {input_dir}")
        sys.exit(1)

    print(f"Generating previews for {len(itermcolors_files)} color schemes...")

    for i, path in enumerate(itermcolors_files, 1):
        name = path.stem
        output_path = os.path.join(output_dir, f"{name}.png")
        try:
            generate_preview(str(path), output_path)
            print(f"  [{i}/{len(itermcolors_files)}] {name}")
        except Exception as e:
            print(f"  [{i}/{len(itermcolors_files)}] ERROR: {name}: {e}")

    print(f"\nDone! Previews saved to {output_dir}")


if __name__ == "__main__":
    main()
