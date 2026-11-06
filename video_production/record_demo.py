import os
import sys
import time
import glob
import math
import random
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# =============================================================================
# Big Tech & Apple-Grade Presentation Injections (Cursor, Zoom, Chapters)
# =============================================================================
APPLE_PRESENTATION_SCRIPT = """
(() => {
  if (document.getElementById('apple-motion-cursor')) return;

  // 1. Inject Styles for Apple Cursor, Ripple Physics & Chapter Cards
  const style = document.createElement('style');
  style.id = 'apple-motion-styles';
  style.textContent = `
    #apple-motion-cursor {
      position: fixed;
      top: 0;
      left: 0;
      width: 26px;
      height: 32px;
      pointer-events: none;
      z-index: 2147483647;
      transform-origin: 3px 2px;
      transform: translate3d(-100px, -100px, 0) scale(1);
      transition: transform 0.09s cubic-bezier(0.2, 0.9, 0.3, 1);
      will-change: transform;
    }
    #apple-motion-cursor.clicking {
      transform: translate3d(var(--cursor-x), var(--cursor-y), 0) scale(0.86) !important;
    }
    .apple-click-ripple {
      position: fixed;
      pointer-events: none;
      z-index: 2147483646;
      border-radius: 50%;
      transform: translate(-50%, -50%) scale(0.6);
      opacity: 1;
      will-change: transform, opacity;
    }
    .apple-ripple-core {
      width: 10px;
      height: 10px;
      background: radial-gradient(circle, #009CDE 0%, rgba(0, 112, 186, 0.4) 100%);
      box-shadow: 0 0 14px rgba(0, 156, 222, 0.9);
      transition: transform 0.38s ease-out, opacity 0.38s ease-out;
    }
    .apple-ripple-wave {
      width: 22px;
      height: 22px;
      border: 2px solid rgba(0, 112, 186, 0.9);
      background: rgba(0, 156, 222, 0.15);
      box-shadow: 0 0 22px rgba(0, 112, 186, 0.5);
      transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.65s ease-out, border-width 0.65s ease;
    }

    /* Chapter Card (Dynamic Island Keynote Architecture) */
    #apple-chapter-container {
      position: fixed;
      top: 24px;
      left: 50%;
      transform: translateX(-50%) translateY(-40px) scale(0.95);
      opacity: 0;
      filter: blur(8px);
      z-index: 2147483640;
      pointer-events: none;
      transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1),
                  opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1),
                  filter 0.5s ease;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
    }
    #apple-chapter-container.active {
      transform: translateX(-50%) translateY(0) scale(1);
      opacity: 1;
      filter: blur(0px);
    }
    .chapter-card-pill {
      position: relative;
      background: rgba(12, 18, 29, 0.90);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-top: 1px solid rgba(255, 255, 255, 0.35);
      border-radius: 9999px;
      padding: 10px 24px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55), 0 0 24px rgba(0, 112, 186, 0.32);
      display: flex;
      align-items: center;
      gap: 14px;
      overflow: hidden;
    }
    .chapter-badge {
      background: linear-gradient(135deg, rgba(0, 112, 186, 0.45), rgba(0, 156, 222, 0.25));
      border: 1px solid rgba(0, 156, 222, 0.55);
      color: #38BDF8;
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      letter-spacing: 0.04em;
      font-variant-numeric: tabular-nums;
    }
    .chapter-kicker {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: rgba(255, 255, 255, 0.45);
      line-height: 1;
    }
    .chapter-title {
      font-size: 14px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #FFFFFF;
      line-height: 1.2;
    }
    .chapter-progress-line {
      position: absolute;
      bottom: 0;
      left: 0;
      height: 2.5px;
      background: linear-gradient(90deg, #0070BA, #009CDE, #38BDF8);
      width: 0%;
      border-radius: 9999px;
      transition: width linear;
    }
  `;
  document.head.appendChild(style);

  // 2. Vector SVG Pointer (Apple macOS Aerodynamic Design)
  const cursor = document.createElement('div');
  cursor.id = 'apple-motion-cursor';
  cursor.innerHTML = `
    <svg width="26" height="32" viewBox="0 0 26 32" fill="none" xmlns="http://www.w3.org/2000/svg"
         style="filter: drop-shadow(0 2px 5px rgba(0,0,0,0.32)) drop-shadow(0 6px 14px rgba(0,0,0,0.18));">
      <path d="M2.5 1.8L22.2 16.5L12.8 17.8L17.2 28.5L13.1 30.2L8.7 19.5L2.5 24.6V1.8Z"
            fill="#0C121D" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round"/>
    </svg>
  `;
  document.body.appendChild(cursor);

  // Track Mouse Movement
  let currentX = 960, currentY = 540;
  window.addEventListener('mousemove', (e) => {
    currentX = e.clientX;
    currentY = e.clientY;
    cursor.style.setProperty('--cursor-x', `${currentX}px`);
    cursor.style.setProperty('--cursor-y', `${currentY}px`);
    cursor.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
  }, { passive: true });

  // Spring Press Dynamics & Dual-Ring Shockwave
  window.addEventListener('mousedown', (e) => {
    cursor.classList.add('clicking');

    // Inner Core Pulse
    const core = document.createElement('div');
    core.className = 'apple-click-ripple apple-ripple-core';
    core.style.left = `${e.clientX}px`;
    core.style.top = `${e.clientY}px`;
    document.body.appendChild(core);

    // Outer Expansion Ring
    const wave = document.createElement('div');
    wave.className = 'apple-click-ripple apple-ripple-wave';
    wave.style.left = `${e.clientX}px`;
    wave.style.top = `${e.clientY}px`;
    document.body.appendChild(wave);

    requestAnimationFrame(() => {
      core.style.transform = 'translate(-50%, -50%) scale(3.2)';
      core.style.opacity = '0';
      wave.style.transform = 'translate(-50%, -50%) scale(4.8)';
      wave.style.opacity = '0';
      wave.style.borderWidth = '1px';
    });

    setTimeout(() => { core.remove(); wave.remove(); }, 700);
  });

  window.addEventListener('mouseup', () => {
    cursor.classList.remove('clicking');
  });

  // 3. Chapter Card Container Element
  const chapterContainer = document.createElement('div');
  chapterContainer.id = 'apple-chapter-container';
  chapterContainer.innerHTML = `
    <div class="chapter-card-pill">
      <span class="chapter-badge" id="chap-num">01</span>
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span class="chapter-kicker" id="chap-kicker">THREAT MITIGATION</span>
        <span class="chapter-title" id="chap-title">Real-Time Webhook Firewall</span>
      </div>
      <div class="chapter-progress-line" id="chap-progress"></div>
    </div>
  `;
  document.body.appendChild(chapterContainer);

  window.showChapter = (num, kicker, title, duration = 6500) => {
    document.getElementById('chap-num').textContent = num;
    document.getElementById('chap-kicker').textContent = kicker;
    document.getElementById('chap-title').textContent = title;

    const prog = document.getElementById('chap-progress');
    prog.style.transition = 'none';
    prog.style.width = '0%';

    chapterContainer.classList.add('active');

    requestAnimationFrame(() => {
      prog.style.transition = `width ${duration}ms linear`;
      prog.style.width = '100%';
    });

    if (window._chapTimeout) clearTimeout(window._chapTimeout);
    window._chapTimeout = setTimeout(() => {
      chapterContainer.classList.remove('active');
    }, duration);
  };

  // 4. Dynamic Camera Zoom & Spotlight System
  const stage = document.getElementById('root') || document.body;
  stage.style.transformOrigin = '0 0';
  stage.style.willChange = 'transform';
  stage.style.transition = 'transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';

  let scrim = document.getElementById('camera-spotlight-scrim');
  if (!scrim) {
    scrim = document.createElement('div');
    scrim.id = 'camera-spotlight-scrim';
    scrim.style.position = 'fixed';
    scrim.style.inset = '0';
    scrim.style.pointerEvents = 'none';
    scrim.style.zIndex = '999990';
    scrim.style.opacity = '0';
    scrim.style.transition = 'opacity 0.6s ease';
    document.body.appendChild(scrim);
  }

  window.cameraZoomTo = (target, scale = 1.25, duration = 800, spotlight = true) => {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) {
      console.warn('cameraZoomTo: Target not found', target);
      return;
    }

    const prevTransform = stage.style.transform;
    stage.style.transform = 'none';
    const rect = el.getBoundingClientRect();
    stage.style.transform = prevTransform;

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    const elCenterX = rect.left + rect.width / 2;
    const elCenterY = rect.top + rect.height / 2;

    const translateX = (vw / 2) - (elCenterX * scale);
    const translateY = (vh / 2) - (elCenterY * scale);

    stage.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
    stage.style.transform = `translate3d(${translateX.toFixed(2)}px, ${translateY.toFixed(2)}px, 0) scale(${scale})`;

    if (spotlight) {
      scrim.style.background = 'radial-gradient(circle at 50% 50%, rgba(12, 18, 29, 0.12) 40%, rgba(12, 18, 29, 0.65) 90%)';
      scrim.style.opacity = '1';
    }
  };

  window.cameraReset = (duration = 650) => {
    stage.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
    stage.style.transform = 'translate3d(0, 0, 0) scale(1)';
    scrim.style.opacity = '0';
  };
})();
"""


def human_move(page, target_x, target_y, steps=22, base_delay=0.016):
    """
    Curved human-like mouse movement with natural ease-out deceleration.
    Uses quadratic bezier curve with subtle perpendicular deflection.
    """
    current = getattr(page, "_last_mouse_pos", (960, 540))
    x0, y0 = current
    x2, y2 = target_x, target_y

    dx = x2 - x0
    dy = y2 - y0
    dist = math.hypot(dx, dy)

    if dist < 5:
        page.mouse.move(x2, y2)
        page._last_mouse_pos = (x2, y2)
        return

    # Perpendicular control point deflection for natural biological trajectory
    perp_scale = min(40, dist * 0.18) * (1 if random.random() > 0.5 else -1)
    norm = max(dist, 1)
    x1 = (x0 + x2) / 2 - (dy / norm) * perp_scale
    y1 = (y0 + y2) / 2 + (dx / norm) * perp_scale

    actual_steps = max(12, int(steps * (dist / 400)))
    actual_steps = min(actual_steps, 36)

    for i in range(1, actual_steps + 1):
        t = i / actual_steps
        # Smooth ease-out deceleration curve
        t_curved = math.sin(t * math.pi / 2)

        xt = (1 - t_curved) ** 2 * x0 + 2 * (1 - t_curved) * t_curved * x1 + t_curved ** 2 * x2
        yt = (1 - t_curved) ** 2 * y0 + 2 * (1 - t_curved) * t_curved * y1 + t_curved ** 2 * y2

        page.mouse.move(xt, yt)
        time.sleep(base_delay + (0.004 * (t ** 2)))

    page.mouse.move(x2, y2)
    page._last_mouse_pos = (x2, y2)


def click_locator_with_ripple(page, locator, delay_after=1.2):
    """
    Moves smoothly to element bounding box, triggers press with spring ripple, then releases.
    """
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

        print("Navigating to SentinelPay Web Interface (http://127.0.0.1:5173)...")
        page.goto("http://127.0.0.1:5173", wait_until="networkidle")
        page.evaluate(APPLE_PRESENTATION_SCRIPT)
        time.sleep(1.2)

        start_time = time.time()
        print("Recording started at t=0s with Apple-grade keynote motion engine...")

        # -------------------------------------------------------------
        # SCENE 1: The Hook & Overview (0s to ~33.3s)
        # -------------------------------------------------------------
        print("\n[SCENE 1] Hook & Overview (0s - 33.3s)...")
        page.evaluate("window.showChapter('01', 'AUTONOMOUS TREASURY', 'Autonomous PayPal Treasury Copilot', 7500)")

        # Hover brand title & PayPal badge
        human_move(page, 220, 32)
        time.sleep(3.0)

        # Hover connection status pill
        human_move(page, 950, 32)
        time.sleep(2.5)

        # Dynamic zoom on KPI financial synthesis banner
        print("  -> Dynamic zoom onto #kpi-banner (scale: 1.15)...")
        page.evaluate("window.cameraZoomTo('#kpi-banner', 1.15, 800, false)")
        time.sleep(1.0)

        # Hover potential annual savings ($2,682/yr)
        human_move(page, 450, 185)
        time.sleep(3.5)

        # Hover monthly commitments KPI
        human_move(page, 750, 185)
        time.sleep(3.0)

        # Hover Health Score bar (38/100)
        human_move(page, 1050, 185)
        time.sleep(3.5)

        # Reset camera before overview scroll
        page.evaluate("window.cameraReset(650)")
        time.sleep(0.8)

        # Smooth scroll down to showcase the 6 subscriptions
        page.mouse.wheel(0, 160)
        time.sleep(1.5)
        human_move(page, 400, 380)
        time.sleep(2.5)
        human_move(page, 400, 480)
        time.sleep(2.5)

        # Scroll back up to top banner for scene 2
        page.mouse.wheel(0, -200)
        time.sleep(1.5)

        # Synchronize with Scene 1 audio boundary (33.3s)
        elapsed = time.time() - start_time
        if elapsed < 33.3:
            time.sleep(33.3 - elapsed)

        # -------------------------------------------------------------
        # SCENE 2: Live Webhook Trap & Instant Refund (33.3s to ~71.0s)
        # -------------------------------------------------------------
        print("\n[SCENE 2] Live Webhook Firewall & Instant Refund (33.3s - 71.0s)...")
        page.evaluate("window.showChapter('02', 'REAL-TIME THREAT DEFENSE', 'Live Webhook Firewall & Instant Refund', 8000)")

        # Zoom into the Webhook Firewall section
        print("  -> Dynamic zoom onto #webhook-firewall (scale: 1.25)...")
        page.evaluate("window.cameraZoomTo('#webhook-firewall', 1.25, 750, true)")
        time.sleep(2.5)

        # Hover firewall title
        human_move(page, 580, 220)
        time.sleep(2.0)

        # Click button "Simulate Trial Trap $1 -> $49" with water-ripple pulse
        trap_button = page.locator("button:has-text('Simulate Trial Trap')")
        if trap_button.count() > 0:
            print("  -> Clicking 'Simulate Trial Trap'...")
            click_locator_with_ripple(page, trap_button.first, delay_after=1.8)
        else:
            print("  -> Fallback: locating trial trap button...")
            fallback = page.locator("button:has-text('Simuler piège fin')")
            if fallback.count() > 0:
                click_locator_with_ripple(page, fallback.first, delay_after=1.8)

        # Spotlight the instant refund receipt ($49.00 refunded)
        time.sleep(1.5)
        human_move(page, 660, 320)
        time.sleep(3.0)

        # Click on Developer X-Ray JSON Inspector button to reveal PayPal raw response
        inspector_btn = page.locator("button:has-text('Developer X-Ray')")
        if inspector_btn.count() == 0:
            inspector_btn = page.locator("button:has-text('Inspect')")
        if inspector_btn.count() > 0:
            print("  -> Clicking PayPal Developer X-Ray...")
            click_locator_with_ripple(page, inspector_btn.first, delay_after=1.8)
            time.sleep(3.5)
            # Close inspector
            close_btn = page.locator("button:has-text('Close')")
            if close_btn.count() > 0:
                click_locator_with_ripple(page, close_btn.first, delay_after=1.0)

        # Reset camera smoothly
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.0)

        # Synchronize with Scene 2 audio boundary (71.0s)
        elapsed = time.time() - start_time
        if elapsed < 71.0:
            time.sleep(71.0 - elapsed)

        # -------------------------------------------------------------
        # SCENE 3: SaaS Arbitrage & Gemini B2B Negotiation (71.0s to ~124.6s)
        # -------------------------------------------------------------
        print("\n[SCENE 3] 1-Click SaaS Arbitrage & B2B Negotiation (71.0s - 124.6s)...")
        page.evaluate("window.showChapter('03', 'SAAS ARBITRAGE & RETENTION', '1-Click Arbitrage & Gemini B2B Negotiation', 8000)")

        # Scroll down slightly to align Subscriptions Ledger
        page.mouse.wheel(0, 220)
        time.sleep(1.2)

        # Zoom into subscriptions ledger
        print("  -> Dynamic zoom onto #subscriptions-ledger (scale: 1.15)...")
        page.evaluate("window.cameraZoomTo('#subscriptions-ledger', 1.15, 750, false)")
        time.sleep(1.5)

        # Find and click on CloudGPU Pro row to expand telemetry
        gpu_row = page.locator("div:has-text('CloudGPU Pro')").first
        if gpu_row.count() > 0:
            print("  -> Expanding CloudGPU Pro telemetry...")
            click_locator_with_ripple(page, gpu_row, delay_after=1.8)

        # Hover over 1-Click SaaS Switch Arbitrage card
        time.sleep(1.5)
        switch_btn = page.locator("button:has-text('Switch to RunPod')")
        if switch_btn.count() > 0:
            print("  -> Triggering 1-Click SaaS Arbitrage (Switch to RunPod)...")
            click_locator_with_ripple(page, switch_btn.first, delay_after=2.0)

        # Find and click DesignFlow Enterprise row
        design_row = page.locator("div:has-text('DesignFlow Enterprise')").first
        if design_row.count() > 0:
            print("  -> Expanding DesignFlow Enterprise telemetry...")
            click_locator_with_ripple(page, design_row, delay_after=1.5)

        # Click "Negotiate B2B Discount (-40%)"
        neg_btn = page.locator("button:has-text('Negotiate B2B Discount')")
        if neg_btn.count() > 0:
            print("  -> Launching Gemini Autonomous Retention Negotiator...")
            click_locator_with_ripple(page, neg_btn.first, delay_after=2.5)

            # Camera zoom on the B2B modal
            page.evaluate("window.cameraZoomTo('#b2b-modal', 1.15, 600, true)")
            time.sleep(3.0)

            # Click "Apply 40% Discount on PayPal via /revise"
            apply_btn = page.locator("button:has-text('Apply 40% Discount')")
            if apply_btn.count() == 0:
                apply_btn = page.locator("button:has-text('Appliquer -40%')")
            if apply_btn.count() > 0:
                print("  -> Applying 40% discount on PayPal via /revise...")
                click_locator_with_ripple(page, apply_btn.first, delay_after=2.0)

            # Close negotiation modal if still open
            close_modal = page.locator("button:has-text('Close')")
            if close_modal.count() > 0:
                click_locator_with_ripple(page, close_modal.first, delay_after=1.0)

        # Reset camera
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.0)

        # Scroll up to trigger batch sweep button
        page.mouse.wheel(0, -220)
        time.sleep(1.5)

        # Click "Optimize Subscriptions" batch sweep button
        sweep_btn = page.locator("button:has-text('Optimize')")
        if sweep_btn.count() > 0:
            print("  -> Executing Autonomous Sweep...")
            click_locator_with_ripple(page, sweep_btn.first, delay_after=2.5)

        # Hover over transformed Health Score (98/100 A+)
        time.sleep(1.5)
        human_move(page, 1050, 185)
        time.sleep(3.0)

        # Synchronize with Scene 3 audio boundary (124.6s)
        elapsed = time.time() - start_time
        if elapsed < 124.6:
            time.sleep(124.6 - elapsed)

        # -------------------------------------------------------------
        # SCENE 4: Agentic Commerce & Certified CFO Boardpack (124.6s to ~173.0s)
        # -------------------------------------------------------------
        print("\n[SCENE 4] Agentic Commerce & CFO Boardpack (124.6s - 173.0s)...")
        page.evaluate("window.showChapter('04', 'AGENTIC COMMERCE', 'Zero-Trust Budget Guardrails & Orders v2', 8000)")

        # Zoom into Guardrails & Purchases Panel
        print("  -> Dynamic zoom onto #guardrails-panel (scale: 1.25)...")
        page.evaluate("window.cameraZoomTo('#guardrails-panel', 1.25, 750, true)")
        time.sleep(2.0)

        # Test Scenario 1: $19.50 (Auto-approved under $25 threshold)
        order_19 = page.locator("button:has-text('19,50')").or_(page.locator("button:has-text('19.50')"))
        if order_19.count() > 0:
            print("  -> Purchasing $19.50 GPU Credits (Zero-Click Auto-Approved)...")
            click_locator_with_ripple(page, order_19.first, delay_after=2.0)

        # Test Scenario 2: $65.00 (Exceeds $25 threshold -> Human Approval Queue)
        order_65 = page.locator("button:has-text('65,00')").or_(page.locator("button:has-text('65.00')"))
        if order_65.count() > 0:
            print("  -> Submitting $65.00 Purchase (Approval Required)...")
            click_locator_with_ripple(page, order_65.first, delay_after=2.0)

        # Approve the pending proposal in the 1-click queue
        approve_btn = page.locator("button:has-text('Approve PayPal Order')")
        if approve_btn.count() > 0:
            print("  -> 1-Click Human Approval for $65.00 Order capture...")
            click_locator_with_ripple(page, approve_btn.first, delay_after=2.2)

        # Reset camera before opening CFO Boardpack
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.2)

        # Display Chapter 5: CFO Governance
        page.evaluate("window.showChapter('05', 'AUDIT & GOVERNANCE', 'Certified CFO Boardpack with SHA-256 Proof', 7500)")

        # Scroll to top to access header button
        page.mouse.wheel(0, -300)
        time.sleep(1.0)

        # Click "CFO Boardpack" button in header
        cfo_btn = page.locator("button:has-text('CFO Boardpack')")
        if cfo_btn.count() > 0:
            print("  -> Opening Certified CFO Boardpack modal...")
            click_locator_with_ripple(page, cfo_btn.first, delay_after=2.2)

            # Dynamic camera zoom on the CFO Boardpack modal
            page.evaluate("window.cameraZoomTo('#cfo-modal', 1.15, 600, false)")
            time.sleep(3.0)

            # Hover KPI benchmark grid inside CFO Boardpack
            human_move(page, 700, 320)
            time.sleep(3.5)

            # Hover cryptographic SHA-256 chain verification badge
            human_move(page, 500, 520)
            time.sleep(3.0)

            # Close CFO Modal
            cfo_close = page.locator("button:has-text('Print')").locator("xpath=..").locator("button").last
            if cfo_close.count() > 0:
                click_locator_with_ripple(page, cfo_close, delay_after=1.2)

        # Reset camera
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.0)

        # Final showcase hover on top brand bar
        human_move(page, 960, 400)

        # Synchronize with master audio duration (~173.0s)
        elapsed = time.time() - start_time
        if elapsed < 173.0:
            time.sleep(173.0 - elapsed)

        print(f"\nChoreographed recording completed in {time.time() - start_time:.2f}s!")

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
    subs_file = "video_production/sentinelpay_subs.srt"
    output_mp4 = "sentinelpay_demo.mp4"

    # Forward slash path for FFmpeg subtitles filter
    subs_formatted = subs_file.replace("\\", "/")

    print(f"\nMerging {raw_video} with {master_audio} and burning subtitles ({subs_file}) into {output_mp4}...")

    # High-accessibility Apple-style subtitles: pure white bold text on semi-transparent dark obsidian pill
    subtitles_filter = (
        f"subtitles={subs_formatted}:force_style="
        "'Fontname=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,BackColour=&HB00C121D,"
        "BorderStyle=3,Outline=0,Shadow=0,MarginV=44,Alignment=2,Bold=1,Spacing=0.5'"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video,
        "-i", master_audio,
        "-vf", subtitles_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ]

    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"\nSUCCESS! Master Big Tech demo video produced with subtitles: {output_mp4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    record_session()
    merge_video_and_audio()
