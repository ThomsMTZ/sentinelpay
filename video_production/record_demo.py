import os
import sys
import time
import glob
import math
import random
import subprocess
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Big Tech presentation overlay & water-ripple cursor script
BIG_TECH_OVERLAY_SCRIPT = """
(() => {
    if (document.getElementById('big-tech-cursor')) return;

    // 1. macOS High-DPI Cursor Arrow
    const cursor = document.createElement('div');
    cursor.id = 'big-tech-cursor';
    cursor.innerHTML = `
        <svg width="28" height="34" viewBox="0 0 28 34" fill="none" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(0 4px 8px rgba(0,0,0,0.38));">
            <path d="M3 2L24.5 17L14 18.5L19 30.5L14.5 32.5L9.5 20.5L3 26V2Z" fill="#0C121D" stroke="#FFFFFF" stroke-width="2.2" stroke-linejoin="round"/>
        </svg>
    `;
    cursor.style.position = 'fixed';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '9999999';
    cursor.style.left = '960px';
    cursor.style.top = '540px';
    cursor.style.transformOrigin = '3px 2px';
    cursor.style.transform = 'scale(1)';
    cursor.style.transition = 'transform 0.1s cubic-bezier(0.2, 0.9, 0.3, 1)';
    document.body.appendChild(cursor);

    // 2. Ripple Container
    const rippleContainer = document.createElement('div');
    rippleContainer.id = 'big-tech-ripples';
    rippleContainer.style.position = 'fixed';
    rippleContainer.style.pointerEvents = 'none';
    rippleContainer.style.zIndex = '9999998';
    rippleContainer.style.inset = '0';
    document.body.appendChild(rippleContainer);

    // 3. Big Tech Product Feature Pill (Apple / Microsoft / Anthropic Keynote Style)
    const pill = document.createElement('div');
    pill.id = 'big-tech-feature-pill';
    pill.style.position = 'fixed';
    pill.style.bottom = '36px';
    pill.style.left = '50%';
    pill.style.transform = 'translateX(-50%) translateY(120px)';
    pill.style.opacity = '0';
    pill.style.pointerEvents = 'none';
    pill.style.zIndex = '9999990';
    pill.style.background = 'rgba(12, 18, 29, 0.88)';
    pill.style.backdropFilter = 'blur(20px)';
    pill.style.webkitBackdropFilter = 'blur(20px)';
    pill.style.border = '1px solid rgba(255, 255, 255, 0.18)';
    pill.style.borderRadius = '9999px';
    pill.style.padding = '12px 28px';
    pill.style.boxShadow = '0 20px 50px rgba(0, 48, 135, 0.3), 0 6px 20px rgba(0, 0, 0, 0.45)';
    pill.style.display = 'flex';
    pill.style.alignItems = 'center';
    pill.style.gap = '14px';
    pill.style.color = '#FFFFFF';
    pill.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    pill.style.fontSize = '14px';
    pill.style.fontWeight = '500';
    pill.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.45s ease';
    pill.innerHTML = `
        <span id="pill-icon" style="font-size:20px; line-height:1;">✨</span>
        <span id="pill-title" style="font-weight:700; color:#0070BA; letter-spacing:-0.2px;">SentinelPay</span>
        <span style="color:rgba(255,255,255,0.3); font-weight:300;">•</span>
        <span id="pill-desc" style="color:#F1F5F9; font-weight:500;">Autonomous Treasury Copilot</span>
    `;
    document.body.appendChild(pill);

    // Water Ripple Shockwave on Click (Goutte d'eau)
    window.addEventListener('mousedown', (e) => {
        cursor.style.transform = 'scale(0.85)';

        // Inner drop ripple
        const innerDrop = document.createElement('div');
        innerDrop.style.position = 'fixed';
        innerDrop.style.left = e.clientX + 'px';
        innerDrop.style.top = e.clientY + 'px';
        innerDrop.style.width = '8px';
        innerDrop.style.height = '8px';
        innerDrop.style.borderRadius = '50%';
        innerDrop.style.transform = 'translate(-50%, -50%) scale(1)';
        innerDrop.style.backgroundColor = 'rgba(0, 112, 186, 0.7)';
        innerDrop.style.boxShadow = '0 0 16px rgba(0, 112, 186, 0.9)';
        innerDrop.style.transition = 'transform 0.4s ease-out, opacity 0.4s ease-out';
        rippleContainer.appendChild(innerDrop);

        // Outer water ring shockwave
        const outerRing = document.createElement('div');
        outerRing.style.position = 'fixed';
        outerRing.style.left = e.clientX + 'px';
        outerRing.style.top = e.clientY + 'px';
        outerRing.style.width = '14px';
        outerRing.style.height = '14px';
        outerRing.style.borderRadius = '50%';
        outerRing.style.transform = 'translate(-50%, -50%) scale(1)';
        outerRing.style.border = '2.5px solid rgba(0, 112, 186, 0.9)';
        outerRing.style.backgroundColor = 'rgba(0, 112, 186, 0.15)';
        outerRing.style.boxShadow = '0 0 24px rgba(0, 112, 186, 0.7)';
        outerRing.style.transition = 'transform 0.7s cubic-bezier(0.1, 0.8, 0.25, 1), opacity 0.7s ease-out';
        rippleContainer.appendChild(outerRing);

        requestAnimationFrame(() => {
            innerDrop.style.transform = 'translate(-50%, -50%) scale(4)';
            innerDrop.style.opacity = '0';

            outerRing.style.transform = 'translate(-50%, -50%) scale(9.5)';
            outerRing.style.opacity = '0';
            outerRing.style.borderWidth = '1px';
        });

        setTimeout(() => {
            innerDrop.remove();
            outerRing.remove();
        }, 750);
    });

    window.addEventListener('mouseup', () => {
        cursor.style.transform = 'scale(1)';
    });

    window.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });

    window.showFeaturePill = (icon, title, desc, duration = 6500) => {
        const p = document.getElementById('big-tech-feature-pill');
        if (!p) return;
        document.getElementById('pill-icon').textContent = icon;
        document.getElementById('pill-title').textContent = title;
        document.getElementById('pill-desc').textContent = desc;
        p.style.transform = 'translateX(-50%) translateY(0)';
        p.style.opacity = '1';
        if (window._pillTimeout) clearTimeout(window._pillTimeout);
        if (duration > 0) {
            window._pillTimeout = setTimeout(() => {
                p.style.transform = 'translateX(-50%) translateY(120px)';
                p.style.opacity = '0';
            }, duration);
        }
    };
})();
"""


def human_move(page, target_x, target_y, steps=22, base_delay=0.016):
    """
    Curved human-like mouse movement with natural ease-out deceleration.
    Uses quadratic bezier curve with subtle perpendicular deflection.
    """
    current = getattr(page, "_last_mouse_pos", (960, 540))
    start_x, start_y = current

    dx = target_x - start_x
    dy = target_y - start_y
    dist = math.hypot(dx, dy)

    if dist < 5:
        page.mouse.move(target_x, target_y)
        page._last_mouse_pos = (target_x, target_y)
        return

    curvature = min(40, dist * 0.15) * (1 if random.random() > 0.5 else -1)
    ctrl_x = (start_x + target_x) / 2 - (dy / dist) * curvature
    ctrl_y = (start_y + target_y) / 2 + (dx / dist) * curvature

    for i in range(1, steps + 1):
        t = i / steps
        ease = t * t * (3.0 - 2.0 * t)
        inv = 1.0 - ease
        cx = inv * inv * start_x + 2 * inv * ease * ctrl_x + ease * ease * target_x
        cy = inv * inv * start_y + 2 * inv * ease * ctrl_y + ease * ease * target_y

        page.mouse.move(cx, cy)
        sleep_time = base_delay * (1.0 + (ease * 0.8))
        time.sleep(sleep_time)

    page.mouse.move(target_x, target_y)
    page._last_mouse_pos = (target_x, target_y)


def click_locator_with_ripple(page, locator, delay_after=0.6):
    """Moves smoothly to the locator and clicks with water ripple shockwave."""
    box = locator.bounding_box()
    if box:
        target_x = box["x"] + box["width"] / 2
        target_y = box["y"] + box["height"] / 2
        human_move(page, target_x, target_y)
        time.sleep(0.2)
        page.mouse.down()
        time.sleep(0.12)
        page.mouse.up()
        time.sleep(delay_after)
    else:
        locator.click()
        time.sleep(delay_after)


def record_session():
    os.makedirs("video_production/raw_video", exist_ok=True)
    # Clear old webm files
    for old_file in glob.glob("video_production/raw_video/*.webm"):
        try:
            os.remove(old_file)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--start-maximized",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--hide-scrollbars"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1.0,
            record_video_dir="video_production/raw_video",
            record_video_size={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        # Step 0: Reset demo state for fresh clean start
        try:
            page.request.post("http://127.0.0.1:8000/api/v1/demo/reset")
        except Exception:
            pass

        print("Navigating to SentinelPay Web Interface...")
        page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        page.evaluate(BIG_TECH_OVERLAY_SCRIPT)
        time.sleep(1.2)

        start_time = time.time()
        print("Recording started at t=0s with Big Tech presentation styling...")

        # -------------------------------------------------------------
        # SCENE 1: The Hook & Overview (0s to ~33s)
        # -------------------------------------------------------------
        print("Scene 1: Hook & Overview...")
        page.evaluate("window.showFeaturePill('🔷', 'SentinelPay AI', 'Autonomous PayPal Treasury & Agentic Commerce', 8000)")

        # Hover brand title
        human_move(page, 220, 32)
        time.sleep(3.0)

        # Hover connection status pill
        human_move(page, 950, 32)
        time.sleep(3.0)

        # Move to potential savings banner ($2,682/yr)
        human_move(page, 450, 185)
        time.sleep(4.0)

        # Move to monthly spend KPI ($301.50)
        human_move(page, 750, 185)
        time.sleep(3.5)

        # Move to Financial Health Score (38/100 Warning)
        human_move(page, 1050, 185)
        time.sleep(4.0)

        # Scroll down smoothly to showcase the 6 subscriptions
        page.mouse.wheel(0, 160)
        time.sleep(2.0)
        human_move(page, 400, 380)
        time.sleep(3.0)
        human_move(page, 400, 480)
        time.sleep(3.0)

        # Scroll back up to top banner for scene 2
        page.mouse.wheel(0, -200)
        time.sleep(1.5)

        # Synchronize with audio
        elapsed = time.time() - start_time
        if elapsed < 33.0:
            time.sleep(33.0 - elapsed)

        # -------------------------------------------------------------
        # SCENE 2: Live Webhook Trap & Instant Refund (33s to ~70.5s)
        # -------------------------------------------------------------
        print("Scene 2: Webhook Firewall & Instant Refund...")
        page.evaluate("window.showFeaturePill('⚡', 'Live Webhook Firewall', 'PayPal Captures Refund API v2 Instant Clawback', 8500)")

        # Highlight purple Webhook Interceptor banner
        human_move(page, 620, 105)
        time.sleep(3.5)

        # Click button "Simuler Arnaque Essai (1 $ -> 49 $)" with water ripple
        trap_button = page.locator("button:has-text('Simuler Arnaque Essai')")
        if trap_button.count() > 0:
            click_locator_with_ripple(page, trap_button.first, delay_after=1.8)

        # Highlight the instant refund receipt ($49.00 refunded)
        time.sleep(2.5)
        human_move(page, 660, 185)
        time.sleep(3.5)

        # Click on JSON Inspector button to reveal PayPal raw response
        inspector_btn = page.locator("button:has-text('Inspecter Payload PayPal')")
        if inspector_btn.count() > 0:
            click_locator_with_ripple(page, inspector_btn.first, delay_after=2.2)
            time.sleep(4.0)
            # Close inspector
            close_btn = page.locator("button:has-text('Fermer')")
            if close_btn.count() > 0:
                click_locator_with_ripple(page, close_btn.first, delay_after=1.2)

        # Synchronize with audio
        elapsed = time.time() - start_time
        if elapsed < 70.5:
            time.sleep(70.5 - elapsed)

        # -------------------------------------------------------------
        # SCENE 3: SaaS Arbitrage & B2B Negotiation (70.5s to ~124s)
        # -------------------------------------------------------------
        print("Scene 3: SaaS Arbitrage & B2B Negotiation...")
        page.evaluate("window.showFeaturePill('🔄', '1-Click SaaS Arbitrage', 'Atomic Switch & PayPal /revise Plan Downgrade', 9000)")

        # Scroll to subscriptions list
        page.mouse.wheel(0, 240)
        time.sleep(2.0)

        # 1. Expand CloudGPU Studio Pro ($89.00/mo)
        cloudgpu_row = page.locator("div:has-text('CloudGPU Studio Pro')").first
        click_locator_with_ripple(page, cloudgpu_row, delay_after=1.8)

        # Highlight 1-Click Arbitrage box
        human_move(page, 450, 480)
        time.sleep(3.0)

        # Click "Remplacer par RunPod Serverless GPU"
        switch_btn = page.locator("button:has-text('Remplacer par RunPod')")
        if switch_btn.count() > 0:
            click_locator_with_ripple(page, switch_btn.first, delay_after=2.5)

        # 2. Expand DesignFlow Enterprise ($120.00/mo)
        designflow_row = page.locator("div:has-text('DesignFlow Enterprise')").first
        click_locator_with_ripple(page, designflow_row, delay_after=1.8)

        # Click "Négocier remise B2B (-40%)"
        negotiate_btn = page.locator("button:has-text('Négocier remise B2B')")
        if negotiate_btn.count() > 0:
            click_locator_with_ripple(page, negotiate_btn.first, delay_after=3.0)

        # Inside Negotiation Modal: show ultimatum letter and counter offer
        time.sleep(2.5)
        human_move(page, 960, 420)
        time.sleep(3.0)
        human_move(page, 960, 620)
        time.sleep(3.0)

        # Click "Appliquer -40% sur PayPal (/revise)"
        apply_neg_btn = page.locator("button:has-text('Appliquer -40% sur PayPal')")
        if apply_neg_btn.count() > 0:
            click_locator_with_ripple(page, apply_neg_btn.first, delay_after=2.5)

        # Close negotiation modal
        close_neg = page.locator("div[role='dialog'] button, .fixed button:has-text('Fermer')")
        if close_neg.count() > 0:
            click_locator_with_ripple(page, close_neg.first, delay_after=1.5)
        else:
            page.keyboard.press("Escape")
            time.sleep(1.0)

        # Scroll to top of list and trigger Autonomous Sweep
        page.mouse.wheel(0, -320)
        time.sleep(1.5)
        sweep_btn = page.locator("button:has-text('Optimiser les'), button:has-text('Optimiser les 2 abonnements')")
        if sweep_btn.count() > 0:
            click_locator_with_ripple(page, sweep_btn.first, delay_after=3.0)

        # Highlight animated Health Score flipping to 98/100
        human_move(page, 1050, 220)
        time.sleep(4.0)

        # Synchronize with audio
        elapsed = time.time() - start_time
        if elapsed < 124.0:
            time.sleep(124.0 - elapsed)

        # -------------------------------------------------------------
        # SCENE 4: Budget Guardrails, Orders v2 & CFO Boardpack (124s to ~172.5s)
        # -------------------------------------------------------------
        print("Scene 4: Zero-Trust Guardrails & CFO Boardpack...")
        page.evaluate("window.showFeaturePill('🛡️', 'Budget Guardrails', 'PayPal Orders v2 & Model Context Protocol (MCP)', 9000)")

        # Focus right column
        human_move(page, 1500, 320)
        time.sleep(2.0)

        # Click Auto-approved purchase ($19.50)
        quick_buy_19 = page.locator("button:has-text('19,50 $')").first
        if quick_buy_19.count() > 0:
            click_locator_with_ripple(page, quick_buy_19, delay_after=2.5)

        # Click 1-Click approval purchase ($65.00)
        quick_buy_65 = page.locator("button:has-text('65,00 $')").first
        if quick_buy_65.count() > 0:
            click_locator_with_ripple(page, quick_buy_65, delay_after=2.5)

        # Approve the 1-click pending order
        approve_order_btn = page.locator("button:has-text('Approuver le paiement PayPal')").first
        if approve_order_btn.count() > 0:
            click_locator_with_ripple(page, approve_order_btn, delay_after=2.5)

        # Scroll back up to header
        page.mouse.wheel(0, -420)
        time.sleep(1.5)

        # Click "Rapport CFO" in header
        cfo_btn = page.locator("button:has-text('Rapport CFO')").first
        if cfo_btn.count() > 0:
            click_locator_with_ripple(page, cfo_btn.first, delay_after=3.0)

        page.evaluate("window.showFeaturePill('📜', 'CFO Boardpack', 'Certified SHA-256 Cryptographic Audit Ledger', 8000)")

        # In CFO Boardpack modal: showcase metrics, table, and SHA-256 proof
        human_move(page, 960, 320)
        time.sleep(3.5)
        human_move(page, 960, 520)
        time.sleep(3.5)
        human_move(page, 960, 720)
        time.sleep(4.0)

        # Synchronize with audio (172.5s)
        elapsed = time.time() - start_time
        if elapsed < 172.5:
            time.sleep(172.5 - elapsed)

        print(f"Big Tech choreography completed in {time.time() - start_time:.2f}s!")

        # Finalize video recording
        page.close()
        context.close()
        browser.close()


def merge_video_and_audio():
    video_files = glob.glob("video_production/raw_video/*.webm")
    if not video_files:
        raise FileNotFoundError("No recorded video found in video_production/raw_video!")

    raw_video = max(video_files, key=os.path.getctime)
    master_audio = "video_production/audio/master_voiceover.mp3"
    output_mp4 = "sentinelpay_demo.mp4"

    print(f"\nMerging {raw_video} with {master_audio} into {output_mp4} with high-definition MP4...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video,
        "-i", master_audio,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]

    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"\nSUCCESS! Master Big Tech demo video produced: {output_mp4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    record_session()
    merge_video_and_audio()
