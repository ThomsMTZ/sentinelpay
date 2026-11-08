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

  // 1. Remove early boot curtain if present now that slide overlay is mounting
  const curtain = document.getElementById('early-boot-curtain');
  if (curtain) curtain.remove();

  // 2. Inject Styles for Apple Cursor, Ripple Physics & Keynote Slide Transitions
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
      padding: 50px 80px !important;
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
      margin-bottom: 22px;
    }
    .slide-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #0070BA;
      box-shadow: 0 0 10px rgba(0, 112, 186, 0.6);
    }
    .slide-title {
      font-size: 54px;
      font-weight: 800;
      letter-spacing: -0.035em;
      color: #0C121D;
      margin: 0 0 16px 0;
      max-width: 1200px;
      line-height: 1.14;
    }
    .slide-divider {
      width: 84px;
      height: 4px;
      border-radius: 2px;
      background: linear-gradient(90deg, #003087, #0070BA, #009CDE);
      margin: 8px 0 22px 0;
    }
    .slide-subtitle {
      font-size: 22px;
      font-weight: 500;
      color: #4A5568;
      margin: 0;
      max-width: 950px;
      line-height: 1.5;
    }
  `;
  document.head.appendChild(style);

  // 3. Vector SVG Pointer (Apple macOS Aerodynamic Design)
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

  // 4. Full-Screen Keynote Slide Element (starts active with title immediately)
  const slideOverlay = document.createElement('div');
  slideOverlay.id = 'keynote-slide-overlay';
  slideOverlay.className = 'active';
  slideOverlay.innerHTML = `
    <div class="slide-badge">
      <span class="slide-dot"></span>
      <span id="slide-kicker-text">PAYPAL AI HACKATHON 2026 • OFFICIAL SUBMISSION</span>
    </div>
    <h1 class="slide-title" id="slide-title-text">SentinelPay: Autonomous Treasury & Agentic Commerce</h1>
    <div class="slide-divider"></div>
    <p class="slide-subtitle" id="slide-sub-text">Autonomous copilot eliminating zombie SaaS waste & policy-guarding AI spending with PayPal Sandbox APIs</p>
    <div id="slide-conclusion-extra" style="display: none;"></div>
  `;
  document.body.appendChild(slideOverlay);

  // 5. Visual Frame Synchronization Trigger: 24x24 Magenta square at (0, 0)
  // Removed precisely at start_time so FFmpeg can trim pre-demo setup with 100% mathematical accuracy!
  const syncMarker = document.createElement('div');
  syncMarker.id = 'recording-sync-trigger';
  syncMarker.style.position = 'fixed';
  syncMarker.style.top = '0px';
  syncMarker.style.left = '0px';
  syncMarker.style.width = '24px';
  syncMarker.style.height = '24px';
  syncMarker.style.background = '#FF00FF';
  syncMarker.style.zIndex = '2147483647';
  syncMarker.style.pointerEvents = 'none';
  document.body.appendChild(syncMarker);

  window.showSlide = (kicker, title, subtitle, duration = 3000, slideType = 'normal') => {
    // Hide cursor during slide presentation so it never wanders in the void!
    const c = document.getElementById('apple-motion-cursor');
    if (c) c.classList.remove('visible');

    document.getElementById('slide-kicker-text').textContent = kicker;
    document.getElementById('slide-title-text').textContent = title;
    document.getElementById('slide-sub-text').textContent = subtitle;

    const extra = document.getElementById('slide-conclusion-extra');
    if (slideType === 'final') {
      extra.style.display = 'flex';
      extra.innerHTML = `
        <div style="margin-top: 36px; display: flex; flex-direction: column; align-items: center; gap: 20px;">
          <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
            <span style="padding: 7px 18px; border-radius: 9999px; background: #F8FAFC; border: 1px solid #CBD5E1; font-size: 14px; font-weight: 600; color: #1E293B; display: inline-flex; align-items: center; gap: 6px;">
              <span style="color: #003087;">●</span> PayPal Sandbox REST APIs
            </span>
            <span style="padding: 7px 18px; border-radius: 9999px; background: #F8FAFC; border: 1px solid #CBD5E1; font-size: 14px; font-weight: 600; color: #1E293B; display: inline-flex; align-items: center; gap: 6px;">
              <span style="color: #0070BA;">●</span> Google Gemini 2.5 Flash
            </span>
            <span style="padding: 7px 18px; border-radius: 9999px; background: #F8FAFC; border: 1px solid #CBD5E1; font-size: 14px; font-weight: 600; color: #1E293B; display: inline-flex; align-items: center; gap: 6px;">
              <span style="color: #0E7C47;">●</span> Deterministic Policy Guardrails
            </span>
            <span style="padding: 7px 18px; border-radius: 9999px; background: #F8FAFC; border: 1px solid #CBD5E1; font-size: 14px; font-weight: 600; color: #1E293B; display: inline-flex; align-items: center; gap: 6px;">
              <span style="color: #D97706;">●</span> Cryptographic SHA-256 Ledger
            </span>
          </div>
          <div style="display: inline-flex; align-items: center; gap: 10px; padding: 12px 28px; border-radius: 14px; background: #003087; color: #FFFFFF; font-size: 16px; font-weight: 700; box-shadow: 0 4px 16px rgba(0, 48, 135, 0.28); margin-top: 6px;">
            <span>GitHub Repository:</span>
            <span style="color: #93C5FD; text-decoration: underline;">github.com/ThomsMTZ/sentinelpay</span>
          </div>
          <div style="font-size: 13px; font-weight: 600; color: #64748B; margin-top: 4px;">
            PayPal AI Hackathon 2026 Submission • Autonomous Treasury & Agentic Commerce Copilot
          </div>
        </div>
      `;
    } else if (slideType === 'architecture') {
      extra.style.display = 'flex';
      extra.innerHTML = `
        <div style="margin-top: 30px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; max-width: 1040px; text-align: left;">
          <div style="padding: 18px 22px; border-radius: 16px; background: #F8FAFC; border: 1.5px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
              <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 8px; background: rgba(0, 48, 135, 0.1); color: #003087; font-weight: 800; font-size: 13px;">PP</span>
              <span style="font-size: 16px; font-weight: 700; color: #0C121D;">PayPal Subscriptions v1</span>
            </div>
            <p style="font-size: 13px; color: #64748B; margin: 0; line-height: 1.45;">Automated recurring billing audit, webhook lifecycle events, and in-flight agreement revision via <code style="color: #003087; font-weight: 600;">/revise</code>.</p>
          </div>

          <div style="padding: 18px 22px; border-radius: 16px; background: #F8FAFC; border: 1.5px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
              <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 8px; background: rgba(0, 112, 186, 0.1); color: #0070BA; font-weight: 800; font-size: 13px;">v2</span>
              <span style="font-size: 16px; font-weight: 700; color: #0C121D;">Orders v2 & Captures Refund</span>
            </div>
            <p style="font-size: 13px; color: #64748B; margin: 0; line-height: 1.45;">Sub-100ms clawbacks via <code style="color: #0070BA; font-weight: 600;">/refund</code> and autonomous GPU/token credit procurement via Orders v2.</p>
          </div>

          <div style="padding: 18px 22px; border-radius: 16px; background: #F8FAFC; border: 1.5px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
              <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 8px; background: rgba(14, 124, 71, 0.1); color: #0E7C47; font-weight: 800; font-size: 13px;">AI</span>
              <span style="font-size: 16px; font-weight: 700; color: #0C121D;">Google Gemini 2.5 Flash</span>
            </div>
            <p style="font-size: 13px; color: #64748B; margin: 0; line-height: 1.45;">Autonomous seat telemetry reasoning, market pricing arbitrage, and multi-turn vendor retention negotiation.</p>
          </div>

          <div style="padding: 18px 22px; border-radius: 16px; background: #F8FAFC; border: 1.5px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
              <span style="display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 8px; background: rgba(217, 119, 6, 0.1); color: #D97706; font-weight: 800; font-size: 13px;">256</span>
              <span style="font-size: 16px; font-weight: 700; color: #0C121D;">Policy Guardrails & SHA-256 Ledger</span>
            </div>
            <p style="font-size: 13px; color: #64748B; margin: 0; line-height: 1.45;">Deterministic spend bounds, human-in-the-loop approval queues, and immutable cryptographic audit trails.</p>
          </div>
        </div>
      `;
    } else {
      extra.style.display = 'none';
      extra.innerHTML = '';
    }

    slideOverlay.classList.remove('exiting');
    slideOverlay.classList.add('active');

    if (window._slideExitTimeout) clearTimeout(window._slideExitTimeout);
    if (window._slideDoneTimeout) clearTimeout(window._slideDoneTimeout);

    if (slideType === 'final') {
      // Keep final thank-you slide active until the end
      return;
    }

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

  // 6. Dynamic Camera Zoom & Spotlight System (+25% Enlarged Radiant Spotlight)
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
      // 25% Enlarged radiant spotlight halo (700px radius): center is brilliant white luminescence, outer edges soft cinematic vignette
      scrim.style.background = 'radial-gradient(circle 700px at 50% 50%, rgba(255, 255, 255, 0.40) 0%, rgba(255, 255, 255, 0.20) 35%, rgba(255, 255, 255, 0) 62%, rgba(12, 18, 29, 0.18) 82%, rgba(12, 18, 29, 0.45) 100%)';
      scrim.style.opacity = '1';
    } else {
      scrim.style.opacity = '0';
    }
  };

  window.cameraReset = (duration = 650) => {
    stage.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
    stage.style.transform = 'translate3d(0, 0, 0) scale(1)';
    scrim.style.opacity = '0';
    setTimeout(() => {
      stage.style.transform = 'none';
    }, duration + 50);
  };
})();
"""


def human_move(page, target_x, target_y, steps=22, base_delay=0.016):
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
            locale="en-US",
            record_video_dir="video_production/raw_video",
            record_video_size={"width": 1920, "height": 1080}
        )

        # Early boot curtain: keeps #root invisible while React hydrates so dashboard never flashes!
        context.add_init_script("""
            (() => {
                const s = document.createElement('style');
                s.id = 'early-boot-curtain';
                s.textContent = `
                    #root { opacity: 0 !important; }
                    body { background: #FFFFFF !important; }
                `;
                document.documentElement.appendChild(s);
            })()
        """)

        page = context.new_page()

        # Step 0: Reset demo state for fresh clean start
        try:
            page.request.post("http://127.0.0.1:8000/api/v1/demo/reset")
        except Exception:
            pass

        print("Navigating to SentinelPay Web Interface (http://127.0.0.1:5173)...")
        page.goto("http://127.0.0.1:5173", wait_until="networkidle")

        # Wait until dashboard is fully hydrated behind the curtain
        page.wait_for_selector("#kpi-banner", state="visible", timeout=15000)

        # Inject presentation engine (mounts Keynote Slide Overlay and sync trigger box)
        page.evaluate(KEYNOTE_PRESENTATION_SCRIPT)
        time.sleep(0.6)

        # Drop the sync trigger marker and begin presentation at the EXACT SAME instant!
        start_time = time.time()
        print("Recording started at t=0s with Title Slide active & Apple Motion Engine...")

        # -------------------------------------------------------------
        # SCENE 1: The Snappy Hook, Quick Global Look & Tech Architecture (0s to 37.4s)
        # -------------------------------------------------------------
        print("\n[SCENE 1] Snappy Hook, Interface Overview & Architecture Slide (0s - 37.4s)...")
        print("  -> Displaying Slide 1: Welcome & Official Submission Slide (0.0s - 8.8s)...")
        page.evaluate("""
            (() => {
                const marker = document.getElementById('recording-sync-trigger');
                if (marker) marker.remove();
                window.showSlide(
                    'PAYPAL AI HACKATHON 2026 • OFFICIAL SUBMISSION',
                    'SentinelPay: Autonomous Treasury & Agentic Commerce',
                    'Autonomous copilot eliminating zombie SaaS waste & policy-guarding AI spending with PayPal Sandbox APIs',
                    8800,
                    'normal'
                );
            })()
        """)
        time.sleep(8.8)  # Slide dissolves smoothly right as narrator finishes the greeting

        # Step 1b: Quick Global Visual of the Interface (8.8s - 18.5s)
        print("  -> Quick Global Visual of the Interface (8.8s - 18.5s)...")
        brand_logo = page.locator("span:has-text('SentinelPay')").first
        move_to_locator(page, brand_logo, offset_x=0.5, offset_y=0.5, delay_after=1.2)

        # Dynamic gentle zoom on KPI financial synthesis banner
        print("  -> Dynamic gentle zoom onto #kpi-banner (scale: 1.12)...")
        page.evaluate("window.cameraZoomTo('#kpi-banner', 1.12, 700, false)")
        time.sleep(0.8)

        # Hover potential annual savings heading
        savings_h1 = page.locator("#kpi-banner h1").first
        move_to_locator(page, savings_h1, offset_x=0.4, offset_y=0.5, delay_after=1.8)

        # Reset camera before swift overview scroll
        page.evaluate("window.cameraReset(500)")
        time.sleep(0.5)

        # Smooth scroll down to give a quick glance of the full interface
        page.mouse.wheel(0, 220)
        time.sleep(1.2)
        # Scroll back up to align for the architecture slide
        page.mouse.wheel(0, -220)
        time.sleep(1.0)

        # Step 1c: Technical Architecture Slide (18.5s - 36.6s)
        print("  -> Displaying Slide 1b: Technical Architecture Slide (18.5s - 36.6s)...")
        page.evaluate("""
            window.showSlide(
                'SYSTEM ARCHITECTURE • BUILT FOR AGENTIC COMMERCE',
                'Powered by PayPal Sandbox APIs & Google Gemini',
                'Native Subscriptions v1, Orders v2, and Captures v2 orchestrated by Gemini 2.5 Flash with deterministic budget guardrails',
                17500,
                'architecture'
            )
        """)
        time.sleep(17.5)  # Technical slide dissolves into Scene 2

        # Synchronize with Scene 1 audio boundary (37.4s)
        elapsed = time.time() - start_time
        if elapsed < 37.4:
            time.sleep(37.4 - elapsed)

        # -------------------------------------------------------------
        # SCENE 2: Live Webhook Trap & Dynamic Camera Recalibration on JSON (37.4s to 74.9s)
        # -------------------------------------------------------------
        print("\n[SCENE 2] Live Webhook Firewall & Instant Refund (37.4s - 74.9s)...")
        print("  -> Displaying Slide 2: Webhook Firewall Title Slide (37.4s - 40.8s)...")
        page.evaluate("""
            window.showSlide(
                'PART 01 • REAL-TIME THREAT DEFENSE',
                'Real-Time PayPal Webhook Firewall',
                'Zero-trust interception of stealth price hikes & instant clawback refund via Captures API v2 in under 100ms',
                3400,
                'normal'
            )
        """)
        time.sleep(3.4)

        # Zoom into the Webhook Firewall section with 25% enlarged radiant spotlight!
        print("  -> Dynamic zoom onto #webhook-firewall (scale: 1.25 with 700px spotlight)...")
        page.evaluate("window.cameraZoomTo('#webhook-firewall', 1.25, 750, true)")
        time.sleep(1.5)

        # Hover firewall title
        firewall_title = page.locator("#webhook-firewall h2").first
        move_to_locator(page, firewall_title, offset_x=0.3, offset_y=0.5, delay_after=1.8)

        # Click button "Simulate MeetScribe Trial Trap ($1 -> $49)" with water-ripple pulse
        trap_button = (
            page.locator("button:has-text('MeetScribe')")
            .or_(page.locator("button:has-text('Trial Trap')"))
            .or_(page.locator("button:has-text('Simulate Trial Trap')"))
        )
        if trap_button.count() > 0:
            print("  -> Clicking 'Simulate Trial Trap'...")
            click_locator_with_ripple(page, trap_button.first, delay_after=1.8)

        # Spotlight the instant refund receipt ($49.00 refunded)
        try:
            page.wait_for_selector("text=Instant PayPal Refund Executed", timeout=5000)
        except Exception:
            pass
        refund_badge = page.get_by_text("Instant PayPal Refund Executed").first
        move_to_locator(page, refund_badge, offset_x=0.5, offset_y=0.5, delay_after=2.5)

        # Click on Developer X-Ray JSON Inspector button to reveal PayPal raw response
        inspector_btn = page.locator("button:has-text('Inspect PayPal JSON')")
        if inspector_btn.count() > 0:
            print("  -> Clicking PayPal Developer X-Ray...")
            click_locator_with_ripple(page, inspector_btn.first, delay_after=1.0)
            
            # Wait for JSON drawer to mount
            page.wait_for_selector("#paypal-json-drawer", state="visible", timeout=4000)

            # DYNAMIC CAMERA RECALIBRATION: smoothly pan and zoom directly to #paypal-json-drawer!
            print("  -> CAMERA RECALIBRATION: Centering zoom onto #paypal-json-drawer...")
            page.evaluate("window.cameraZoomTo('#paypal-json-drawer', 1.18, 650, true)")
            time.sleep(1.0)

            # Hover inside the raw JSON receipt and verified SHA-256 chain badge
            json_badge = page.locator("#paypal-json-drawer span:has-text('SHA-256')").first
            move_to_locator(page, json_badge, offset_x=0.5, offset_y=0.5, delay_after=1.5)

            json_pre = page.locator("#paypal-json-drawer pre").first
            move_to_locator(page, json_pre, offset_x=0.4, offset_y=0.3, delay_after=2.0)

            # Explicitly close the inspector drawer so it doesn't linger!
            hide_btn = page.locator("button:has-text('Hide PayPal JSON')")
            if hide_btn.count() > 0:
                print("  -> Closing PayPal Developer X-Ray drawer...")
                click_locator_with_ripple(page, hide_btn.first, delay_after=0.8)

            # Recalibrate camera back onto the firewall card
            page.evaluate("window.cameraZoomTo('#webhook-firewall', 1.15, 500, true)")
            time.sleep(0.8)

        # Reset camera smoothly
        page.evaluate("window.cameraReset(600)")
        time.sleep(1.0)

        # Synchronize with Scene 2 audio boundary (74.9s)
        elapsed = time.time() - start_time
        if elapsed < 74.9:
            time.sleep(74.9 - elapsed)

        # -------------------------------------------------------------
        # SCENE 3: SaaS Arbitrage & Gemini B2B Negotiation (74.9s to 128.3s)
        # -------------------------------------------------------------
        print("\n[SCENE 3] 1-Click SaaS Arbitrage & B2B Negotiation (74.9s - 128.3s)...")
        print("  -> Displaying Slide 3: SaaS Arbitrage & B2B Negotiation Slide (74.9s - 78.3s)...")
        page.evaluate("""
            window.showSlide(
                'PART 02 • TREASURY OPTIMIZATION',
                '1-Click SaaS Arbitrage & Gemini B2B Negotiation',
                'Autonomous subscription replacement via Orders v2 & -40% enterprise discount via /revise',
                3400,
                'normal'
            )
        """)
        time.sleep(3.4)

        # Scroll down slightly to align Subscriptions Ledger
        page.mouse.wheel(0, 220)
        time.sleep(1.2)

        # Zoom into subscriptions ledger with +25% enlarged radiant spotlight
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

        # Scroll and expand DesignFlow Enterprise row
        print("  -> Ensuring DesignFlow Enterprise row is expanded...")
        page.evaluate("window.cameraReset(400)")
        time.sleep(0.5)

        page.mouse.wheel(0, 260)
        time.sleep(0.8)

        design_row = page.locator("span:has-text('DesignFlow Enterprise')").first
        design_row.scroll_into_view_if_needed()
        time.sleep(0.4)
        click_locator_with_ripple(page, design_row, delay_after=1.5)

        # Locate and click Negotiate B2B Discount button
        neg_btn = page.locator("button:has-text('Negotiate B2B Discount')").first
        neg_btn.scroll_into_view_if_needed()
        time.sleep(0.4)
        print("  -> Launching Gemini Autonomous Retention Negotiator...")
        click_locator_with_ripple(page, neg_btn, delay_after=1.5)

        # Clear stage transform to 'none' so modal is 100% dead center in the viewport!
        page.evaluate("""
            (() => {
                const stage = document.getElementById('root') || document.body;
                stage.style.transform = 'none';
            })()
        """)

        # Wait for modal to render completely centered at 100% scale
        page.wait_for_selector("#b2b-modal pre", state="visible", timeout=12000)
        time.sleep(1.0)

        # Hover formal notice letter
        letter_box = page.locator("#b2b-modal pre").first
        move_to_locator(page, letter_box, offset_x=0.5, offset_y=0.4, delay_after=2.5)

        # Hover 40% discount savings
        counter_box = page.locator("#b2b-modal").get_by_text("Retention Counter-Offer Accepted").first
        move_to_locator(page, counter_box, offset_x=0.5, offset_y=0.5, delay_after=2.0)

        # Click 'Apply 40% Discount on PayPal via /revise'
        apply_btn = page.locator("button:has-text('Apply 40% Discount')").or_(
            page.locator("button:has-text('Appliquer -40%')")
        )
        if apply_btn.count() > 0:
            print("  -> Applying 40% discount on PayPal via /revise...")
            click_locator_with_ripple(page, apply_btn.first, delay_after=2.5)

        # Close B2B modal cleanly via close button
        print("  -> Closing B2B modal...")
        close_btn = page.locator("#b2b-close-btn")
        if close_btn.count() > 0 and close_btn.first.is_visible():
            click_locator_with_ripple(page, close_btn.first, delay_after=0.8)

        page.evaluate("""(
            () => {
                const btn = document.getElementById('b2b-close-btn') || document.getElementById('b2b-close-x-btn');
                if (btn) btn.click();
                else {
                    const modal = document.getElementById('b2b-modal');
                    if (modal) modal.click();
                }
            }
        )()""")
        time.sleep(0.8)

        # Reset camera
        page.evaluate("window.cameraReset(600)")
        time.sleep(0.8)

        # Scroll up to trigger batch sweep button
        page.mouse.wheel(0, -350)
        time.sleep(1.5)
        sweep_btn = page.locator("button:has-text('Optimize')")
        if sweep_btn.count() > 0:
            print("  -> Executing Autonomous Sweep...")
            click_locator_with_ripple(page, sweep_btn.first, delay_after=2.5)

        # Hover over transformed Health Score (98/100 A+)
        health_final = page.locator("#kpi-banner").get_by_text("Health Score:").first
        move_to_locator(page, health_final, offset_x=0.5, offset_y=0.5, delay_after=3.0)

        # Synchronize with Scene 3 audio boundary (128.3s)
        elapsed = time.time() - start_time
        if elapsed < 128.3:
            time.sleep(128.3 - elapsed)

        # -------------------------------------------------------------
        # SCENE 4: Agentic Commerce & Certified CFO Boardpack (128.3s to 175.7s)
        # -------------------------------------------------------------
        print("\n[SCENE 4] Agentic Commerce & CFO Boardpack (128.3s - 175.7s)...")
        print("  -> Displaying Slide 4: Budget Guardrails Title Slide (128.3s - 131.7s)...")
        page.evaluate("""
            window.showSlide(
                'PART 03 • AGENTIC COMMERCE & MCP',
                'Zero-Trust Budget Guardrails & Orders v2',
                'Policy-guarded autonomous procurement and standard Model Context Protocol for external AI agents',
                3400,
                'normal'
            )
        """)
        time.sleep(3.4)

        # Zoom into Guardrails & Purchases Panel with enlarged spotlight
        print("  -> Dynamic zoom onto #guardrails-panel (scale: 1.25)...")
        page.evaluate("window.cameraZoomTo('#guardrails-panel', 1.25, 750, true)")
        time.sleep(2.0)

        # Test Scenario 1: $19.50 (Auto-approved under $25 threshold)
        order_19 = page.locator("button:has-text('$19.50')").or_(page.locator("button:has-text('19.50')")).or_(page.locator("button:has-text('19,50')"))
        if order_19.count() > 0:
            print("  -> Purchasing $19.50 GPU Credits (Zero-Click Auto-Approved)...")
            click_locator_with_ripple(page, order_19.first, delay_after=2.0)

        # Test Scenario 2: $65.00 (Exceeds $25 threshold -> Human Approval Queue)
        order_65 = page.locator("button:has-text('$65.00')").or_(page.locator("button:has-text('65.00')")).or_(page.locator("button:has-text('65,00')"))
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
                3200,
                'normal'
            )
        """)
        time.sleep(3.2)

        page.mouse.wheel(0, -300)
        time.sleep(1.0)

        # Click "CFO Boardpack" button in header
        cfo_btn = page.locator("button:has-text('CFO Boardpack')")
        if cfo_btn.count() > 0:
            print("  -> Opening Certified CFO Boardpack modal...")
            click_locator_with_ripple(page, cfo_btn.first, delay_after=2.2)

            page.evaluate("""
                (() => {
                    const stage = document.getElementById('root') || document.body;
                    stage.style.transform = 'none';
                })()
            """)
            time.sleep(0.5)

            # Hover KPI benchmark grid inside CFO Boardpack
            bench_grid = page.locator("#cfo-modal").get_by_text("Baseline Spend").first
            move_to_locator(page, bench_grid, offset_x=0.5, offset_y=1.5, delay_after=2.5)

            # Hover cryptographic SHA-256 chain verification badge
            sha_badge = page.locator("#cfo-modal").get_by_text("Cryptographic SHA-256 Chain Verified").first
            move_to_locator(page, sha_badge, offset_x=0.5, offset_y=0.5, delay_after=2.5)

            # Close CFO Modal
            cfo_close = page.locator("#cfo-modal button:has-text('Print')").locator("xpath=..").locator("button").last
            if cfo_close.count() > 0:
                click_locator_with_ripple(page, cfo_close, delay_after=1.0)
            
            page.evaluate("""
                (() => {
                    const modal = document.getElementById('cfo-modal');
                    if (modal) modal.click();
                })()
            """)
            time.sleep(0.5)

        # Reset camera
        page.evaluate("window.cameraReset(400)")
        time.sleep(0.5)

        # Final Keynote Conclusion Slide: Thank You & Credits
        print("  -> Displaying Final Keynote Slide: Thank You & Architecture Credits...")
        page.evaluate("""
            window.showSlide(
                'CONCLUSION • SENTINELPAY AI',
                'Thank You',
                'Autonomous PayPal Treasury & Agentic Commerce Copilot • PayPal AI Hackathon 2026',
                8000,
                'final'
            )
        """)

        # Synchronize with master audio duration (~175.7s)
        elapsed = time.time() - start_time
        if elapsed < 175.7:
            time.sleep(175.7 - elapsed)

        print(f"\nChoreographed recording completed in {time.time() - start_time:.2f}s!")

        page.close()
        context.close()
        browser.close()


def find_demo_start_offset(raw_video: str) -> float:
    """
    Scans the top-left 24x24 pixels of raw_video.
    Before demo start, pixel (12, 12) is pure magenta (#FF00FF).
    The very first frame where it is no longer magenta is the EXACT frame 0 of the presentation.
    """
    print(f"\nScanning {raw_video} for precise frame 0 demo start offset...")
    seen_magenta = False
    for t_ms in range(1000, 8000, 40):
        t_sec = t_ms / 1000.0
        cmd = [
            FFMPEG_EXE, "-ss", f"{t_sec:.3f}", "-i", raw_video,
            "-vframes", "1", "-vf", "crop=24:24:0:0",
            "-f", "image2pipe", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if len(res.stdout) == 24 * 24 * 3:
            idx = (12 * 24 + 12) * 3
            r, g, b = res.stdout[idx], res.stdout[idx + 1], res.stdout[idx + 2]
            is_magenta = (r > 200 and g < 50 and b > 200)
            if is_magenta:
                seen_magenta = True
            elif seen_magenta and not is_magenta:
                print(f"-> Frame 0 Slide Trigger detected at {t_sec:.3f}s (RGB: {r},{g},{b})!")
                return t_sec
    print("Warning: Sync marker transition not found, default to 5.04s")
    return 5.04


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

    start_offset = find_demo_start_offset(raw_video)
    print(f"\nTrimming {start_offset:.3f}s of pre-demo setup so frame 0 starts IMMEDIATELY on the Title Slide at t=0s!")

    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{start_offset:.3f}",
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
    print(f"\nSUCCESS! Master Big Tech demo video produced with 0ms Title Slide start: {output_mp4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    record_session()
    merge_video_and_audio()
