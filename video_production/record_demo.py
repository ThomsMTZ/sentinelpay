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
# Big Tech Keynote Engine: Full-Screen Slide Cards, Vector Cursor & Dynamic Zoom
# =============================================================================
KEYNOTE_PRESENTATION_SCRIPT = """
(() => {
  if (document.getElementById('apple-motion-cursor')) return;

  // 1. Inject Styles for Apple Cursor, Ripple Physics & Keynote Slide Transitions
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
      opacity: 0;
      transition: opacity 0.35s ease, transform 0.09s cubic-bezier(0.2, 0.9, 0.3, 1);
      will-change: transform, opacity;
    }
    #apple-motion-cursor.visible {
      opacity: 1 !important;
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

    /* Full-Screen Keynote Title Slide (Diapositive Fond Blanc Style Big Tech) */
    #keynote-slide-overlay {
      position: fixed !important;
      inset: 0 !important;
      z-index: 2147483640 !important;
      background: #FFFFFF !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: center !important;
      align-items: center !important;
      text-align: center !important;
      padding: 60px 80px !important;
      opacity: 0;
      pointer-events: none;
      transform: scale(0.98);
      filter: blur(8px);
      transition: opacity 0.50s cubic-bezier(0.16, 1, 0.3, 1),
                  transform 0.50s cubic-bezier(0.16, 1, 0.3, 1),
                  filter 0.50s ease;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif !important;
    }
    #keynote-slide-overlay.active {
      opacity: 1 !important;
      pointer-events: auto !important;
      transform: scale(1) !important;
      filter: blur(0px) !important;
    }
    #keynote-slide-overlay.exiting {
      opacity: 0 !important;
      pointer-events: none !important;
      transform: scale(1.04) !important;
      filter: blur(6px) !important;
    }
    .slide-badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 7px 22px;
      border-radius: 9999px;
      background: rgba(0, 112, 186, 0.08);
      border: 1px solid rgba(0, 112, 186, 0.28);
      color: #0070BA;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      margin-bottom: 26px;
    }
    .slide-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #0070BA;
      box-shadow: 0 0 10px rgba(0, 112, 186, 0.6);
    }
    .slide-title {
      font-size: 58px;
      font-weight: 800;
      letter-spacing: -0.035em;
      color: #0C121D;
      margin: 0 0 18px 0;
      max-width: 1180px;
      line-height: 1.12;
    }
    .slide-divider {
      width: 84px;
      height: 4px;
      border-radius: 2px;
      background: linear-gradient(90deg, #003087, #0070BA, #009CDE);
      margin: 8px 0 24px 0;
    }
    .slide-subtitle {
      font-size: 23px;
      font-weight: 500;
      color: #4A5568;
      margin: 0;
      max-width: 900px;
      line-height: 1.5;
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

  // 3. Full-Screen Keynote Slide Element (starts active for instant keynote opening)
  const slideOverlay = document.createElement('div');
  slideOverlay.id = 'keynote-slide-overlay';
  slideOverlay.className = 'active';
  slideOverlay.innerHTML = `
    <div class="slide-badge">
      <span class="slide-dot"></span>
      <span id="slide-kicker-text">KEYNOTE OVERVIEW • ARCHITECTURE</span>
    </div>
    <h1 class="slide-title" id="slide-title-text">Autonomous PayPal Treasury & Agentic Commerce</h1>
    <div class="slide-divider"></div>
    <p class="slide-subtitle" id="slide-sub-text">Eliminating zombie SaaS waste & policy-guarding autonomous AI spending with PayPal Sandbox APIs</p>
  `;
  document.body.appendChild(slideOverlay);

  window.showSlide = (kicker, title, subtitle, duration = 3000) => {
    // Hide cursor during slide presentation so it never wanders in the void!
    const c = document.getElementById('apple-motion-cursor');
    if (c) c.classList.remove('visible');

    document.getElementById('slide-kicker-text').textContent = kicker;
    document.getElementById('slide-title-text').textContent = title;
    document.getElementById('slide-sub-text').textContent = subtitle;

    slideOverlay.classList.remove('exiting');
    slideOverlay.classList.add('active');

    if (window._slideExitTimeout) clearTimeout(window._slideExitTimeout);
    if (window._slideDoneTimeout) clearTimeout(window._slideDoneTimeout);

    // Begin smooth dissolve into live video
    window._slideExitTimeout = setTimeout(() => {
      slideOverlay.classList.remove('active');
      slideOverlay.classList.add('exiting');
      // Fade cursor in cleanly as live interface emerges
      if (c) c.classList.add('visible');
    }, Math.max(duration - 550, 1000));

    window._slideDoneTimeout = setTimeout(() => {
      slideOverlay.classList.remove('exiting');
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

    # Perpendicular control point deflection for natural trajectory
    perp_scale = min(40, dist * 0.18) * (1 if random.random() > 0.5 else -1)
    norm = max(dist, 1)
    x1 = (x0 + x2) / 2 - (dy / norm) * perp_scale
    y1 = (y0 + y2) / 2 + (dx / norm) * perp_scale

    actual_steps = max(12, int(steps * (dist / 400)))
    actual_steps = min(actual_steps, 36)

    for i in range(1, actual_steps + 1):
        t = i / actual_steps
        t_curved = math.sin(t * math.pi / 2)

        xt = (1 - t_curved) ** 2 * x0 + 2 * (1 - t_curved) * t_curved * x1 + t_curved ** 2 * x2
        yt = (1 - t_curved) ** 2 * y0 + 2 * (1 - t_curved) * t_curved * y1 + t_curved ** 2 * y2

        page.mouse.move(xt, yt)
        time.sleep(base_delay + (0.004 * (t ** 2)))

    page.mouse.move(x2, y2)
    page._last_mouse_pos = (x2, y2)


def move_to_locator(page, locator, offset_x=0.5, offset_y=0.5, delay_after=1.0):
    """
    Moves smoothly to element real screen coordinates derived from bounding_box().
    """
    try:
        box = locator.bounding_box(timeout=3500)
        if box:
            target_x = box["x"] + box["width"] * offset_x
            target_y = box["y"] + box["height"] * offset_y
            human_move(page, target_x, target_y)
            time.sleep(delay_after)
            return
    except Exception as e:
        print(f"  [warn] move_to_locator notice: {e}")
    time.sleep(delay_after)


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

        # Wait until dashboard is fully hydrated and KPI banner is visible
        page.wait_for_selector("#kpi-banner", state="visible", timeout=15000)

        # Inject presentation engine (Slide 1 starts active immediately, cursor hidden)
        page.evaluate(KEYNOTE_PRESENTATION_SCRIPT)
        time.sleep(0.5)

        start_time = time.time()
        print("Recording started at t=0s with Keynote Slide Transitions & Apple Motion Engine...")

        # -------------------------------------------------------------
        # SCENE 1: The Hook & Overview (0s to ~33.3s)
        # -------------------------------------------------------------
        print("\n[SCENE 1] Hook & Overview (0s - 33.3s)...")
        print("  -> Displaying Slide 1: Introduction Title Slide (0.0s - 3.2s)...")
        # Trigger slide 1 dissolve after 3.2s (cursor stays hidden until slide dissolves)
        page.evaluate("""
            window.showSlide(
                'KEYNOTE OVERVIEW • ARCHITECTURE',
                'Autonomous PayPal Treasury & Agentic Commerce',
                'Eliminating zombie SaaS waste & policy-guarding autonomous AI spending with PayPal Sandbox APIs',
                3200
            )
        """)
        time.sleep(3.2)  # Wait for slide presentation and smooth dissolve

        # Slide dissolved -> cursor fades in cleanly onto SentinelPay brand
        brand_logo = page.locator("span:has-text('SentinelPay')").first
        move_to_locator(page, brand_logo, offset_x=0.5, offset_y=0.5, delay_after=2.0)

        # Dynamic zoom on KPI financial synthesis banner
        print("  -> Dynamic zoom onto #kpi-banner (scale: 1.15)...")
        page.evaluate("window.cameraZoomTo('#kpi-banner', 1.15, 800, false)")
        time.sleep(1.0)

        # Hover potential annual savings heading directly via locator bounding box
        savings_h1 = page.locator("#kpi-banner h1").first
        move_to_locator(page, savings_h1, offset_x=0.4, offset_y=0.5, delay_after=3.0)

        # Hover active monthly commitments card
        commit_card = page.locator("#kpi-banner").get_by_text("Active Monthly Commitments").first
        move_to_locator(page, commit_card, offset_x=0.5, offset_y=1.5, delay_after=3.0)

        # Hover Health Score bar
        health_label = page.locator("#kpi-banner").get_by_text("Health Score:").first
        move_to_locator(page, health_label, offset_x=0.5, offset_y=0.5, delay_after=3.0)

        # Reset camera before overview scroll
        page.evaluate("window.cameraReset(650)")
        time.sleep(0.8)

        # Smooth scroll down to showcase the subscriptions
        page.mouse.wheel(0, 180)
        time.sleep(1.5)

        # Hover first subscription row (CloudGPU)
        sub_row1 = page.locator("span:has-text('CloudGPU Studio Pro')").first
        move_to_locator(page, sub_row1, offset_x=0.5, offset_y=0.5, delay_after=2.5)

        # Hover second subscription row (DesignFlow)
        sub_row2 = page.locator("span:has-text('DesignFlow Enterprise')").first
        move_to_locator(page, sub_row2, offset_x=0.5, offset_y=0.5, delay_after=2.5)

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
        print("  -> Displaying Slide 2: Webhook Firewall Title Slide (33.3s - 36.8s)...")
        page.evaluate("""
            window.showSlide(
                'PART 01 • REAL-TIME THREAT DEFENSE',
                'Real-Time PayPal Webhook Firewall',
                'Zero-trust interception of stealth price hikes & instant clawback refund via Captures API v2 in under 100ms',
                3400
            )
        """)
        time.sleep(3.4)  # Slide presentation and dissolve

        # Zoom into the Webhook Firewall section
        print("  -> Dynamic zoom onto #webhook-firewall (scale: 1.25)...")
        page.evaluate("window.cameraZoomTo('#webhook-firewall', 1.25, 750, true)")
        time.sleep(1.5)

        # Hover firewall title
        firewall_title = page.locator("#webhook-firewall h2").first
        move_to_locator(page, firewall_title, offset_x=0.3, offset_y=0.5, delay_after=2.0)

        # Click button "Simulate Trial Trap $1 -> $49" with water-ripple pulse
        trap_button = page.locator("button:has-text('Simulate Trial Trap')")
        if trap_button.count() > 0:
            print("  -> Clicking 'Simulate Trial Trap'...")
            click_locator_with_ripple(page, trap_button.first, delay_after=1.8)

        # Spotlight the instant refund receipt ($49.00 refunded)
        refund_badge = page.get_by_text("Instant PayPal Refund Executed").first
        move_to_locator(page, refund_badge, offset_x=0.5, offset_y=0.5, delay_after=3.0)

        # Click on Developer X-Ray JSON Inspector button to reveal PayPal raw response
        inspector_btn = page.locator("button:has-text('Inspect PayPal JSON')")
        if inspector_btn.count() > 0:
            print("  -> Clicking PayPal Developer X-Ray...")
            click_locator_with_ripple(page, inspector_btn.first, delay_after=1.8)
            time.sleep(3.0)
            # Explicitly close the inspector drawer so it doesn't linger!
            hide_btn = page.locator("button:has-text('Hide PayPal JSON')")
            if hide_btn.count() > 0:
                print("  -> Closing PayPal Developer X-Ray drawer...")
                click_locator_with_ripple(page, hide_btn.first, delay_after=1.0)

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
        print("  -> Displaying Slide 3: SaaS Arbitrage & B2B Negotiation Slide (71.0s - 74.5s)...")
        page.evaluate("""
            window.showSlide(
                'PART 02 • TREASURY OPTIMIZATION',
                '1-Click SaaS Arbitrage & Gemini B2B Negotiation',
                'Autonomous subscription replacement via Orders v2 & -40% enterprise discount via /revise',
                3400
            )
        """)
        time.sleep(3.4)  # Slide presentation and dissolve

        # Scroll down slightly to align Subscriptions Ledger
        page.mouse.wheel(0, 220)
        time.sleep(1.2)

        # Zoom into subscriptions ledger
        print("  -> Dynamic zoom onto #subscriptions-ledger (scale: 1.15)...")
        page.evaluate("window.cameraZoomTo('#subscriptions-ledger', 1.15, 750, false)")
        time.sleep(1.5)

        # Find and click on CloudGPU Pro row to expand telemetry
        gpu_row = page.locator("span:has-text('CloudGPU Studio Pro')").first
        if gpu_row.count() == 0:
            gpu_row = page.locator("span:has-text('CloudGPU')").first
        if gpu_row.count() > 0:
            print("  -> Expanding CloudGPU Pro telemetry...")
            click_locator_with_ripple(page, gpu_row, delay_after=1.8)

        # Click 1-Click SaaS Switch Arbitrage card
        time.sleep(1.2)
        switch_btn = page.locator("button:has-text('Switch to RunPod')")
        if switch_btn.count() > 0:
            print("  -> Triggering 1-Click SaaS Arbitrage (Switch to RunPod)...")
            click_locator_with_ripple(page, switch_btn.first, delay_after=2.0)

        # Robust expansion of DesignFlow Enterprise row
        print("  -> Ensuring DesignFlow Enterprise row is expanded...")
        neg_btn = page.locator("button:has-text('Negotiate B2B Discount')")
        if neg_btn.count() == 0 or not neg_btn.first.is_visible():
            design_row = page.locator("span:has-text('DesignFlow Enterprise')").first
            if design_row.count() > 0:
                click_locator_with_ripple(page, design_row, delay_after=1.8)

        # Click "Negotiate B2B Discount (-40%)"
        neg_btn = page.locator("button:has-text('Negotiate B2B Discount')")
        if neg_btn.count() > 0 and neg_btn.first.is_visible():
            print("  -> Launching Gemini Autonomous Retention Negotiator...")
            click_locator_with_ripple(page, neg_btn.first, delay_after=2.5)

            # Camera zoom on the B2B modal
            page.evaluate("window.cameraZoomTo('#b2b-modal', 1.15, 600, true)")
            time.sleep(2.5)

            # Hover formal notice letter
            letter_box = page.locator("#b2b-modal pre").first
            move_to_locator(page, letter_box, offset_x=0.5, offset_y=0.4, delay_after=2.5)

            # Hover 40% discount savings
            counter_box = page.locator("#b2b-modal").get_by_text("Retention Counter-Offer Accepted").first
            move_to_locator(page, counter_box, offset_x=0.5, offset_y=0.5, delay_after=2.0)

            # Click "Apply 40% Discount on PayPal via /revise"
            apply_btn = page.locator("button:has-text('Apply 40% Discount')").or_(
                page.locator("button:has-text('Appliquer -40%')")
            )
            if apply_btn.count() > 0:
                print("  -> Applying 40% discount on PayPal via /revise...")
                click_locator_with_ripple(page, apply_btn.first, delay_after=2.5)

            # RESET CAMERA FIRST so modal coordinates and buttons are 100% natural and unscaled!
            print("  -> Resetting camera and closing B2B modal...")
            page.evaluate("window.cameraReset(400)")
            time.sleep(0.6)

            # Click close button with locator
            close_btn = page.locator("#b2b-close-btn")
            if close_btn.count() > 0 and close_btn.first.is_visible():
                click_locator_with_ripple(page, close_btn.first, delay_after=0.8)

            # Triple-check: if modal is still open, close it via state / backdrop click!
            page.evaluate("""
                (() => {
                    const btn = document.getElementById('b2b-close-btn') || document.getElementById('b2b-close-x-btn');
                    if (btn) btn.click();
                    else {
                        const modal = document.getElementById('b2b-modal');
                        if (modal) modal.click();
                    }
                })()
            """)
            time.sleep(0.8)

        # Reset camera
        page.evaluate("window.cameraReset(600)")
        time.sleep(0.8)

        # Scroll up to trigger batch sweep button
        page.mouse.wheel(0, -220)
        time.sleep(1.5)

        # Click "Optimize Subscriptions" batch sweep button
        sweep_btn = page.locator("button:has-text('Optimize')")
        if sweep_btn.count() > 0:
            print("  -> Executing Autonomous Sweep...")
            click_locator_with_ripple(page, sweep_btn.first, delay_after=2.5)

        # Hover over transformed Health Score (98/100 A+)
        health_final = page.locator("#kpi-banner").get_by_text("Health Score:").first
        move_to_locator(page, health_final, offset_x=0.5, offset_y=0.5, delay_after=3.0)

        # Synchronize with Scene 3 audio boundary (124.6s)
        elapsed = time.time() - start_time
        if elapsed < 124.6:
            time.sleep(124.6 - elapsed)

        # -------------------------------------------------------------
        # SCENE 4: Agentic Commerce & Certified CFO Boardpack (124.6s to ~173.0s)
        # -------------------------------------------------------------
        print("\n[SCENE 4] Agentic Commerce & CFO Boardpack (124.6s - 173.0s)...")
        print("  -> Displaying Slide 4: Budget Guardrails Title Slide (124.6s - 128.0s)...")
        page.evaluate("""
            window.showSlide(
                'PART 03 • AGENTIC COMMERCE & MCP',
                'Zero-Trust Budget Guardrails & Orders v2',
                'Policy-guarded autonomous procurement and standard Model Context Protocol for external AI agents',
                3400
            )
        """)
        time.sleep(3.4)  # Slide presentation and dissolve

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

        # Display Slide 5: Corporate Governance & CFO Boardpack
        print("  -> Displaying Slide 5: CFO Governance Slide...")
        page.evaluate("""
            window.showSlide(
                'PART 04 • CORPORATE GOVERNANCE',
                'Certified CFO Boardpack with SHA-256 Proof',
                'Cryptographically verified before-and-after spend benchmarks and board-ready financial certification',
                3200
            )
        """)
        time.sleep(3.2)  # Slide presentation and dissolve

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
            time.sleep(2.5)

            # Hover KPI benchmark grid inside CFO Boardpack
            bench_grid = page.locator("#cfo-modal").get_by_text("Baseline Spend").first
            move_to_locator(page, bench_grid, offset_x=0.5, offset_y=1.5, delay_after=3.0)

            # Hover cryptographic SHA-256 chain verification badge
            sha_badge = page.locator("#cfo-modal").get_by_text("Cryptographic SHA-256 Chain Verified").first
            move_to_locator(page, sha_badge, offset_x=0.5, offset_y=0.5, delay_after=3.0)

            # Reset camera before closing modal
            page.evaluate("window.cameraReset(500)")
            time.sleep(0.6)

            # Close CFO Modal
            cfo_close = page.locator("#cfo-modal button:has-text('Print')").locator("xpath=..").locator("button").last
            if cfo_close.count() > 0:
                click_locator_with_ripple(page, cfo_close, delay_after=1.0)
            
            # Double check CFO modal is closed
            page.evaluate("""
                (() => {
                    const modal = document.getElementById('cfo-modal');
                    if (modal) modal.click();
                })()
            """)
            time.sleep(0.5)

        # Reset camera
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.0)

        # Final showcase hover on top brand bar
        brand_final = page.locator("span:has-text('SentinelPay')").first
        move_to_locator(page, brand_final, offset_x=0.5, offset_y=0.5, delay_after=2.0)

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
    ass_file = "video_production/sentinelpay_subs.ass"
    output_mp4 = "sentinelpay_demo.mp4"

    # Forward slash path for FFmpeg subtitles filter
    ass_formatted = ass_file.replace("\\", "/")

    print(f"\nMerging {raw_video} with {master_audio} and burning high-contrast ASS subtitles into {output_mp4}...")

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", raw_video,
        "-i", master_audio,
        "-vf", f"subtitles={ass_formatted}",
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
    print(f"\nSUCCESS! Master Big Tech demo video produced with slide transitions & high-contrast subtitles: {output_mp4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    record_session()
    merge_video_and_audio()
