import re

def convert_srt_to_ass(srt_path, ass_path, style_type="box"):
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Split into subtitle blocks
    blocks = re.split(r'\n\s*\n', content)

    # Style definition
    if style_type == "box":
        # Dark obsidian translucent box (&H180C121D = ~90% opaque #0C121D dark obsidian) with pure white bold text
        style_line = "Style: Default,Arial,34,&H00FFFFFF,&H000000FF,&H00000000,&H180C121D,-1,0,0,0,100,100,0.5,0,3,8.0,0,2,60,60,55,1"
    else:
        # Bold pure white text with 3.8px black contour and 2.5px drop shadow
        style_line = "Style: Default,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0.5,0,1,3.8,2.5,2,60,60,55,1"

    ass_header = f"""[Script Info]
Title: SentinelPay Keynote Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{style_line}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogues = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 3:
            # line 0: index
            # line 1: timing
            # line 2+: text
            timing_match = re.search(r'(\d\d:\d\d:\d\d,\d\d\d)\s*-->\s*(\d\d:\d\d:\d\d,\d\d\d)', lines[1])
            if timing_match:
                start_srt, end_srt = timing_match.groups()
                
                def to_ass_time(t):
                    h, m, s_ms = t.split(":")
                    s, ms = s_ms.split(",")
                    return f"{int(h)}:{m}:{s}.{ms[:2]}"
                
                start_ass = to_ass_time(start_srt)
                end_ass = to_ass_time(end_srt)
                text = " ".join([l.strip() for l in lines[2:]])
                # Escape backslashes if any
                text = text.replace("\\", "\\\\")
                dialogues.append(f"Dialogue: 0,{start_ass},{end_ass},Default,,0,0,0,,{text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "\n".join(dialogues) + "\n")
    
    print(f"Generated {ass_path} with {len(dialogues)} dialogues (Style: {style_type})")

if __name__ == "__main__":
    convert_srt_to_ass("video_production/sentinelpay_subs.srt", "video_production/sentinelpay_subs.ass", style_type="box")
