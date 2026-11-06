import asyncio
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
            "Every year, companies and individuals waste over 135 billion dollars on zombie SaaS subscriptions, "
            "underutilized team seats, and silent recurring price hikes. "
            "Meanwhile, autonomous AI agents are ready to buy compute and software on our behalf—but no CFO will hand "
            "an unconstrained LLM raw access to a PayPal account. "
            "Welcome to SentinelPay: the autonomous PayPal Treasury and Agentic Commerce copilot, powered by Google Gemini "
            "and native PayPal Sandbox REST APIs."
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


async def main():
    os.makedirs("video_production/audio", exist_ok=True)
    durations = {}

    for scene in SCENES:
        output_file = f"video_production/audio/{scene['id']}.mp3"
        print(f"Generating audio for {scene['id']} with {VOICE}...")
        communicate = edge_tts.Communicate(scene["text"], VOICE, rate="+3%")
        await communicate.save(output_file)
        duration = get_audio_duration(output_file)
        durations[scene["id"]] = duration
        print(f"  -> Generated {output_file} (Duration: {duration:.2f}s)")

    # Concatenate all audio files into master_voiceover.mp3 with 1s pause between scenes
    concat_list_file = "video_production/audio/concat_list.txt"
    # Generate 1s silence file
    silence_file = "video_production/audio/silence1s.mp3"
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1.0", "-q:a", "9", silence_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(concat_list_file, "w", encoding="utf-8") as f:
        for i, scene in enumerate(SCENES):
            f.write(f"file '{scene['id']}.mp3'\n")
            if i < len(SCENES) - 1:
                f.write(f"file 'silence1s.mp3'\n")

    master_audio = "video_production/audio/master_voiceover.mp3"
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", concat_list_file,
        "-c", "copy", master_audio
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_duration = get_audio_duration(master_audio)
    print(f"\nMaster voiceover generated: {master_audio}")
    print(f"Total Duration: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")

    with open("video_production/audio/durations.json", "w", encoding="utf-8") as f:
        import json
        json.dump({"durations": durations, "total_duration": total_duration}, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
