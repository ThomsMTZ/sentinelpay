import asyncio
import json
import os
import re
import subprocess
import imageio_ffmpeg
import edge_tts

VOICE = "en-US-AvaNeural"
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

SCENES = [
    {
        "id": "scene1",
        "text": (
            "Welcome to SentinelPay: the autonomous PayPal Treasury and Agentic Commerce copilot, built for the PayPal AI Hackathon 2026. "
            "SentinelPay transforms how businesses manage recurring commitments, giving CFOs an intelligent command center over cash flow and autonomous transactions. "
            "Under the hood, SentinelPay connects Google Gemini 2.5 Flash to PayPal's native Subscriptions v1, Orders v2, and Captures v2 APIs, "
            "protected by deterministic policy guardrails and a cryptographic SHA-256 audit ledger."
        )
    },
    {
        "id": "scene2",
        "text": (
            "Let's start with our real-time defense: the Live Webhook Firewall. "
            "Watch what happens when a predatory merchant attempts an unauthorized one-dollar trial conversion into a "
            "recurring 49-dollar monthly charge. "
            "The moment the signed PayPal webhook hits our system, SentinelPay verifies the signature, suspends the "
            "billing agreement, and triggers an instant clawback refund via PayPal's Captures Refund API v2 in under 100 milliseconds. "
            "With our PayPal Developer X-Ray, judges and developers can inspect the raw JSON receipt, HATEOAS links, "
            "and verified idempotency keys."
        )
    },
    {
        "id": "scene3",
        "text": (
            "Next, SentinelPay continuously audits active subscriptions against real usage telemetry. "
            "Instead of just cutting tools, SentinelPay offers 1-Click SaaS Arbitrage. Here, it cancels overpriced CloudGPU Pro "
            "at 89 dollars a month and immediately provisions an equivalent RunPod serverless cluster for 19 dollars via "
            "PayPal Orders v2—saving 840 dollars a year. "
            "For active tools like DesignFlow Enterprise, our Gemini Copilot initiates an active B2B retention negotiation. "
            "It drafts a formal notice citing actual seat usage, secures a 40 percent enterprise discount, and applies it "
            "directly to the PayPal billing agreement via the Subscriptions Revise API. "
            "With our Autonomous Sweep, one click cleans up dormant zombies and flips our Financial Health Score from 38 to 98."
        )
    },
    {
        "id": "scene4",
        "text": (
            "For outbound Agentic Commerce, our deterministic Budget Guardrails protect autonomous spending. "
            "A 19 dollar 50 GPU credit top-up is auto-approved under our 25 dollar threshold and captured via PayPal Orders v2. "
            "A 65 dollar token pack requires human approval and is queued for a safe 1-click confirmation. "
            "SentinelPay also exposes a full Model Context Protocol server, enabling external AI agents in Claude or Cursor "
            "to command PayPal safely. "
            "Finally, the CFO can generate a certified, board-ready audit pack complete with before-and-after spend benchmarks "
            "and cryptographic SHA-256 ledger proof. "
            "SentinelPay turns PayPal into the trusted operating system for autonomous commerce. Thank you."
        )
    }
]


def get_audio_duration(file_path: str) -> float:
    cmd = [FFMPEG_EXE, "-i", file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 0.0


def format_ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


async def generate_scene_audio_with_cues(scene, voice_rate="+3%"):
    audio_path = f"video_production/audio/{scene['id']}.mp3"
    comm = edge_tts.Communicate(scene["text"], VOICE, rate=voice_rate)
    
    audio_data = bytearray()
    boundaries = []
    
    async for chunk in comm.stream():
        if chunk.get("type") == "audio":
            audio_data.extend(chunk["data"])
        elif chunk.get("type") == "SentenceBoundary":
            start_s = chunk["offset"] / 10_000_000
            dur_s = chunk["duration"] / 10_000_000
            boundaries.append({
                "start": start_s,
                "end": start_s + dur_s,
                "text": chunk["text"]
            })
            
    with open(audio_path, "wb") as f:
        f.write(audio_data)
        
    duration = get_audio_duration(audio_path)
    return audio_path, duration, boundaries


def split_long_cue(start, end, text, max_words=12):
    """
    If a sentence is long, split it into two balanced subtitle lines.
    """
    words = text.split()
    if len(words) <= max_words:
        return [(start, end, text)]
    
    # Try splitting at comma, semicolon, dash, or em-dash
    split_points = [m.start() for m in re.finditer(r"[,;—\-] ", text)]
    best_char_split = None
    mid_char = len(text) // 2
    if split_points:
        best_char_split = min(split_points, key=lambda p: abs(p - mid_char))
    
    if best_char_split and 15 < best_char_split < len(text) - 15:
        p1 = text[:best_char_split + 1].strip()
        p2 = text[best_char_split + 1:].strip()
    else:
        half = len(words) // 2
        p1 = " ".join(words[:half])
        p2 = " ".join(words[half:])
        
    ratio = len(p1.split()) / len(words)
    mid_time = start + (end - start) * ratio
    return [(start, mid_time, p1), (mid_time, end, p2)]


async def main():
    os.makedirs("video_production/audio", exist_ok=True)
    all_cues = []
    current_offset = 0.0
    scene_durations = {}
    
    # 0.8s clean silence file
    silence_file = "video_production/audio/silence08s.mp3"
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "0.8", "-q:a", "9", silence_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    concat_list = []
    for i, scene in enumerate(SCENES):
        print(f"Synthesizing {scene['id']} with exact sentence boundaries...")
        audio_path, duration, boundaries = await generate_scene_audio_with_cues(scene)
        scene_durations[scene['id']] = duration
        concat_list.append(f"file '{scene['id']}.mp3'")
        
        # Process cues with scene start offset
        for b in boundaries:
            sub_cues = split_long_cue(b["start"], b["end"], b["text"])
            for s_start, s_end, s_text in sub_cues:
                all_cues.append({
                    "start": current_offset + s_start,
                    "end": current_offset + s_end,
                    "text": s_text
                })
                
        current_offset += duration
        if i < len(SCENES) - 1:
            concat_list.append("file 'silence08s.mp3'")
            current_offset += 0.8  # Add pause offset between scenes
            
    # Write concat list
    concat_file = "video_production/audio/concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        f.write("\n".join(concat_list) + "\n")
        
    # Concatenate master audio
    master_audio = "video_production/audio/master_voiceover.mp3"
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", master_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    total_audio_duration = get_audio_duration(master_audio)
    print(f"\nMaster voiceover generated: {master_audio} ({total_audio_duration:.2f}s)")
    
    # Generate ASS Subtitles
    ass_header = """[Script Info]
Title: SentinelPay Synchronized Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,34,&H00FFFFFF,&H000000FF,&H00000000,&H180C121D,-1,0,0,0,100,100,0.5,0,3,8.0,0,2,60,60,55,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass_lines = [ass_header]
    for cue in all_cues:
        start_str = format_ass_time(cue["start"])
        end_str = format_ass_time(cue["end"])
        text = cue["text"]
        # Format currency & symbols nicely for readability
        text = text.replace("one-dollar", "$1")
        text = text.replace("49-dollar", "$49")
        text = text.replace("89 dollars a month", "$89/mo")
        text = text.replace("19 dollars", "$19")
        text = text.replace("840 dollars a year", "$840/year")
        text = text.replace("40 percent", "40%")
        text = text.replace("19 dollar 50", "$19.50")
        text = text.replace("25 dollar", "$25")
        text = text.replace("65 dollar", "$65")
        ass_lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}\n")
        
    ass_path = "video_production/sentinelpay_subs.ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.writelines(ass_lines)
    print(f"Generated frame-perfect ASS subtitles: {ass_path} ({len(all_cues)} cues)")
    
    with open("video_production/audio/durations.json", "w", encoding="utf-8") as f:
        json.dump({
            "durations": scene_durations,
            "total_duration": total_audio_duration,
            "cue_count": len(all_cues)
        }, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
