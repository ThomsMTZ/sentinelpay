# Creative Director & Motion Design Specification: SentinelPay AI
**PayPal AI Hackathon 2026 — Product Video Architecture**
*Designed in the aesthetic tradition of Apple Keynotes, Stripe Sessions, and Linear*

---

### Executive Motion Philosophy
To win a Tier-1 hackathon, a demo video must not look like an amateur screen recording. It must feel like an **Apple Product Keynote**:
1. **Zero Input Friction**: Fluid, spring-damped pointer cursor with authentic macOS micro-geometry and tactile optical feedback.
2. **Executive Focus**: Smooth camera pans and dynamic lens zooming with zero-distortion hit testing, paired with an illuminated vignette spotlight.
3. **Keynote Chapter Architecture**: Top-tier frosted glass chapter cards that anchor the 5 major PayPal AI capabilities.
4. **Cinematic Accessibility**: Studio-grade burned subtitles using Apple SF Pro / Inter typography inside translucent obsidian pills.

Below are the complete, production-ready specifications, code injections, and FFmpeg pipeline commands.

---

## 1. Apple-Style Minimalist Pointer Cursor & Click Physics

### Visual Geometry & Aesthetic
- **Vector Silhouette**: Authentic macOS Sonoma/Sequoia aerodynamic pointer geometry with a 1.5px crisp white halo outline (`#FFFFFF`) enclosing a deep graphite core (`#0C121D`), ensuring 100% contrast over both light PayPal panels and dark code viewers.
- **Elevation Shadow**: Dual-frequency ambient + contact drop shadow (`rgba(0,0,0,0.28)` and `rgba(0,0,0,0.16)`).
- **Press Dynamics**: Damped scale compression (`scale(0.88)`) on pointer-down with instant response (0ms delay), springing back on release.
- **Tactile Shockwave (Optical Pulse)**: A concentric dual-ring ripple combining an inner cyan droplet (`#0070BA`) and an outer frosted wave expanding via Apple's `cubic-bezier(0.16, 1, 0.3, 1)` deceleration curve.

### Production Injection Code (CSS + SVG + JS)

```javascript
/**
 * Apple-Style Minimalist Pointer & Click Physics Engine
 * Zero dependencies — inject into Playwright page.evaluate()
 */
(() => {
  if (document.getElementById('apple-motion-cursor')) return;

  // 1. Inject Styles
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
      box-shadow: 0 0 12px rgba(0, 156, 222, 0.8);
      transition: transform 0.38s ease-out, opacity 0.38s ease-out;
    }
    .apple-ripple-wave {
      width: 22px;
      height: 22px;
      border: 2px solid rgba(0, 112, 186, 0.85);
      background: rgba(0, 156, 222, 0.12);
      box-shadow: 0 0 20px rgba(0, 112, 186, 0.45);
      transition: transform 0.65s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.65s ease-out, border-width 0.65s ease;
    }
  `;
  document.head.appendChild(style);

  // 2. Cursor Container & Precision Vector SVG
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

  // Track Mouse Movement with Sub-pixel Hardware Acceleration
  let currentX = 960, currentY = 540;
  window.addEventListener('mousemove', (e) => {
    currentX = e.clientX;
    currentY = e.clientY;
    cursor.style.setProperty('--cursor-x', `${currentX}px`);
    cursor.style.setProperty('--cursor-y', `${currentY}px`);
    cursor.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
  }, { passive: true });

  // Spring Press Dynamics & Concentric Shockwave
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
})();
```

---

## 2. Dynamic Section Zoom & Cinematic Spotlight Effect

### Technical Architecture
- **Zero Coordinate Drift**: Instead of scaling `document.body` (which corrupts fixed UI layers), the camera engine transforms the main application container (`#root`). Because the custom cursor and keynote overlays are anchored to the viewport outside `#root`, mouse tracking stays 1:1.
- **Playwright Hit Alignment**: When `#root` is scaled and translated, calling `element.getBoundingClientRect()` or Playwright's `locator.bounding_box()` accurately reflects the **real viewport screen coordinates**. Playwright clicks land directly on the intended buttons.
- **Cinematic Spotlight**: An animated fixed vignette scrim with an inverted soft mask highlights the target element, dims peripheral noise with 60% obsidian scrim, and adds a delicate PayPal-cyan edge glow.

### Production Injection Code

```javascript
/**
 * Apple Keynote Camera Zoom & Spotlight System
 * Zero dependencies — inject into browser runtime
 */
(() => {
  const stage = document.getElementById('root') || document.body;
  stage.style.transformOrigin = '0 0';
  stage.style.willChange = 'transform, filter';
  stage.style.transition = 'transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';

  // Spotlight Scrim Element
  let scrim = document.getElementById('camera-spotlight-scrim');
  if (!scrim) {
    scrim = document.createElement('div');
    scrim.id = 'camera-spotlight-scrim';
    scrim.style.position = 'fixed';
    scrim.style.inset = '0';
    scrim.style.pointerEvents = 'none';
    scrim.style.zIndex = '999990';
    scrim.style.opacity = '0';
    scrim.style.backdropFilter = 'blur(0px)';
    scrim.style.transition = 'opacity 0.6s ease, backdrop-filter 0.6s ease';
    document.body.appendChild(scrim);
  }

  /**
   * Smoothly pans and zooms to any target element
   * @param {string|HTMLElement} target - CSS selector or DOM element
   * @param {number} scale - Zoom factor (e.g. 1.25)
   * @param {number} duration - Transition duration in ms
   * @param {boolean} spotlight - Enable focused dark vignette
   */
  window.cameraZoomTo = (target, scale = 1.25, duration = 800, spotlight = true) => {
    const el = typeof target === 'string' ? document.querySelector(target) : target;
    if (!el) {
      console.warn('cameraZoomTo: Target not found', target);
      return;
    }

    // Reset transform temporarily to read true unscaled geometry
    const prevTransform = stage.style.transform;
    stage.style.transform = 'none';
    const rect = el.getBoundingClientRect();
    stage.style.transform = prevTransform;

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // Calculate center of element
    const elCenterX = rect.left + rect.width / 2;
    const elCenterY = rect.top + rect.height / 2;

    // Center target element at (vw/2, vh/2) under magnification 'scale'
    const translateX = (vw / 2) - (elCenterX * scale);
    const translateY = (vh / 2) - (elCenterY * scale);

    stage.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
    stage.style.transform = `translate3d(${translateX.toFixed(2)}px, ${translateY.toFixed(2)}px, 0) scale(${scale})`;

    if (spotlight) {
      scrim.style.background = 'radial-gradient(circle at 50% 50%, rgba(12, 18, 29, 0.15) 35%, rgba(12, 18, 29, 0.72) 90%)';
      scrim.style.backdropFilter = 'blur(2.5px)';
      scrim.style.opacity = '1';
    }
  };

  /**
   * Resets camera smoothly to natural full-page view
   */
  window.cameraReset = (duration = 650) => {
    stage.style.transition = `transform ${duration}ms cubic-bezier(0.16, 1, 0.3, 1)`;
    stage.style.transform = 'translate3d(0, 0, 0) scale(1)';
    scrim.style.opacity = '0';
    scrim.style.backdropFilter = 'blur(0px)';
  };
})();
```

---

## 3. Keynote Chapter Cards & Section Motion Graphics

### Apple Keynote Aesthetic
- **Floating Island Architecture**: Rendered at top-center (Dynamic Island style) with deep frosted glass (`rgba(13, 19, 33, 0.88)` with `backdrop-filter: blur(24px)`).
- **Executive Typography**: Kicker in Apple SF Pro / Inter uppercase (`tracking: 0.14em`), crisp chapter number with PayPal cyan badge, and animated micro-progress indicator.
- **Fluid Motion Curves**: Drops in with Apple's spring curve (`cubic-bezier(0.16, 1, 0.3, 1)`) and exits with a subtle upward float and optical blur fade.

### Production Injection Code

```javascript
/**
 * Apple Keynote Chapter Card Presentation Engine
 * Zero dependencies — inject into browser runtime
 */
(() => {
  if (document.getElementById('apple-chapter-container')) return;

  const style = document.createElement('style');
  style.id = 'apple-chapter-styles';
  style.textContent = `
    #apple-chapter-container {
      position: fixed;
      top: 28px;
      left: 50%;
      transform: translateX(-50%) translateY(-35px) scale(0.96);
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
      background: rgba(12, 18, 29, 0.88);
      backdrop-filter: blur(28px) saturate(190%);
      -webkit-backdrop-filter: blur(28px) saturate(190%);
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-top: 1px solid rgba(255, 255, 255, 0.32);
      border-radius: 9999px;
      padding: 10px 24px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.55), 0 0 24px rgba(0, 112, 186, 0.28);
      display: flex;
      align-items: center;
      gap: 14px;
      overflow: hidden;
    }
    .chapter-badge {
      background: linear-gradient(135deg, rgba(0, 112, 186, 0.35), rgba(0, 156, 222, 0.2));
      border: 1px solid rgba(0, 156, 222, 0.45);
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

  const container = document.createElement('div');
  container.id = 'apple-chapter-container';
  container.innerHTML = `
    <div class="chapter-card-pill">
      <span class="chapter-badge" id="chap-num">01</span>
      <div style="display:flex; flex-direction:column; gap:2px;">
        <span class="chapter-kicker" id="chap-kicker">THREAT MITIGATION</span>
        <span class="chapter-title" id="chap-title">Real-Time Webhook Firewall</span>
      </div>
      <div class="chapter-progress-line" id="chap-progress"></div>
    </div>
  `;
  document.body.appendChild(container);

  window.showChapter = (num, kicker, title, duration = 6500) => {
    document.getElementById('chap-num').textContent = num;
    document.getElementById('chap-kicker').textContent = kicker;
    document.getElementById('chap-title').textContent = title;

    const prog = document.getElementById('chap-progress');
    prog.style.transition = 'none';
    prog.style.width = '0%';

    container.classList.add('active');

    requestAnimationFrame(() => {
      prog.style.transition = `width ${duration}ms linear`;
      prog.style.width = '100%';
    });

    if (window._chapTimeout) clearTimeout(window._chapTimeout);
    window._chapTimeout = setTimeout(() => {
      container.classList.remove('active');
    }, duration);
  };
})();
```

### The 5 Hackathon Demo Chapters
In `record_demo.py`, trigger these at the exact narrative transitions:
```python
# Chapter 1: Hook & Webhook Trap
page.evaluate("window.showChapter('01', 'REAL-TIME THREAT DEFENSE', 'Real-Time Webhook Firewall', 8000)")

# Chapter 2: SaaS Optimization
page.evaluate("window.showChapter('02', 'AUTONOMOUS TREASURY', '1-Click SaaS Arbitrage Engine', 7500)")

# Chapter 3: Gemini Copilot Negotiation
page.evaluate("window.showChapter('03', 'GEMINI B2B COPILOT', 'Autonomous Retention Negotiator', 8000)")

# Chapter 4: Agentic Commerce Budgeting
page.evaluate("window.showChapter('04', 'AGENTIC COMMERCE', 'Zero-Trust Budget Guardrails & MCP Server', 8000)")

# Chapter 5: CFO Governance & Boardpack
page.evaluate("window.showChapter('05', 'AUDIT & GOVERNANCE', 'Certified CFO Boardpack with SHA-256 Proof', 7500)")
```

---

## 4. High-Accessibility Apple-Style Subtitles (SRT + ASS + FFmpeg)

### Subtitle Aesthetics & Readability Standards
- **Typography**: Inter Bold / SF Pro Display at 20pt (1080p canvas).
- **Background Pill**: High-contrast, semi-transparent obsidian pill (`#0C121D` with 68% opacity), eliminating contrast fatigue over white backgrounds.
- **Safe Zone Margin**: 44px vertical margin from the viewport floor, sitting gracefully below primary content and above playback scrubbers.
- **Alignment**: Center-anchored with 0.5px letter-spacing.

### Synchronized SRT Subtitle File (`sentinelpay_subs.srt`)
Based on the verified audio durations (Scene 1: 32.3s, Scene 2: 36.72s, Scene 3: 52.61s, Scene 4: 47.42s + 1.0s scene pauses):

```srt
1
00:00:00,000 --> 00:00:06,200
Every year, companies and individuals waste over $135 billion on zombie SaaS subscriptions,

2
00:00:06,200 --> 00:00:10,800
underutilized team seats, and silent recurring price hikes.

3
00:00:10,800 --> 00:00:17,500
Meanwhile, autonomous AI agents are ready to buy compute—but no CFO will hand an unconstrained LLM raw access to a PayPal account.

4
00:00:17,500 --> 00:00:23,800
Welcome to SentinelPay: the autonomous PayPal Treasury and Agentic Commerce copilot,

5
00:00:23,800 --> 00:00:32,300
powered by Google Gemini and native PayPal Sandbox REST APIs.

6
00:00:33,300 --> 00:00:38,500
Let's start with our real-time defense: the Live Webhook Firewall.

7
00:00:38,500 --> 00:00:46,000
Watch what happens when a predatory merchant attempts an unauthorized $1 trial conversion into a recurring $49 charge.

8
00:00:46,000 --> 00:00:53,200
The moment the signed PayPal webhook hits our system, SentinelPay verifies the signature and suspends the billing agreement.

9
00:00:53,200 --> 00:01:02,000
It triggers an instant clawback refund via PayPal's Captures Refund API v2 in under 100 milliseconds.

10
00:01:02,000 --> 00:01:10,020
With our PayPal Developer X-Ray, inspect the raw JSON receipt, HATEOAS links, and verified idempotency keys.

11
00:01:11,020 --> 00:01:17,200
Next, SentinelPay continuously audits active subscriptions against real usage telemetry.

12
00:01:17,200 --> 00:01:23,500
Instead of just cutting tools, SentinelPay offers 1-Click SaaS Arbitrage.

13
00:01:23,500 --> 00:01:31,800
It cancels overpriced CloudGPU Pro at $89/mo and provisions an equivalent RunPod serverless cluster for $19 via PayPal Orders v2—saving $840/year.

14
00:01:31,800 --> 00:01:39,000
For active tools like DesignFlow Enterprise, our Gemini Copilot initiates an active B2B retention negotiation.

15
00:01:39,000 --> 00:01:46,500
It drafts a formal notice citing actual usage, secures a 40% enterprise discount, and applies it directly via the Subscriptions Revise API.

16
00:01:46,500 --> 00:01:54,500
With our Autonomous Sweep, one click cleans up dormant zombies and flips our Financial Health Score from 38 to 98.

17
00:01:55,500 --> 00:02:02,800
For outbound Agentic Commerce, our deterministic Budget Guardrails protect autonomous spending.

18
00:02:02,800 --> 00:02:11,200
A $19.50 GPU credit top-up is auto-approved under our $25 threshold and captured via PayPal Orders v2.

19
00:02:11,200 --> 00:02:18,500
A $65 token pack requires human approval and is queued for a safe 1-click confirmation.

20
00:02:18,500 --> 00:02:26,000
SentinelPay also exposes a full Model Context Protocol server, enabling external AI agents in Claude or Cursor to command PayPal safely.

21
00:02:26,000 --> 00:02:34,000
Finally, the CFO can generate a certified, board-ready audit pack complete with before-and-after spend benchmarks and SHA-256 proof.

22
00:02:34,000 --> 00:02:42,500
SentinelPay turns PayPal into the trusted operating system for autonomous commerce.
```

### FFmpeg Burn-In Filter Commands

#### Option A: Direct Burning via FFmpeg `force_style` (Production Recommendation)
This executes immediately without converting files, using FFmpeg's built-in `libass` renderer:

```bash
ffmpeg -y -i raw_video.webm -i master_voiceover.mp3 \
  -vf "subtitles=sentinelpay_subs.srt:force_style='Fontname=Inter,FontSize=20,PrimaryColour=&H00FFFFFF,BackColour=&HB00C121D,BorderStyle=3,Outline=0,Shadow=0,MarginV=44,Alignment=2,Bold=1,Spacing=0.5'" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest sentinelpay_demo_subtitled.mp4
```

*Style breakdown:*
- `Fontname=Inter` (Clean geometric neo-grotesque font; falls back cleanly to Helvetica/Arial if not installed).
- `FontSize=20` (Optimal proportional sizing for 1920x1080 display).
- `PrimaryColour=&H00FFFFFF` (100% pure white lettering).
- `BackColour=&HB00C121D` (`&HAABBGGRR` hex format: `B0` = ~69% opacity dark obsidian box `#0C121D`).
- `BorderStyle=3` (Enables the **opaque pill background box** behind the text).
- `Outline=0, Shadow=0` (Eliminates harsh 90s-style black text drop shadows).
- `MarginV=44` (Precision bottom spacing).

---

## 5. Master Integration Checklist for `record_demo.py`

1. **Inject Combined Engine in Page Setup**:
   Add `BIG_TECH_OVERLAY_SCRIPT` containing Cursor, Camera Zoom, and Keynote Chapters right after `page.goto("http://127.0.0.1:5173")`.
2. **Execute Visual Zooms at Climax Moments**:
   - In Scene 2 (Clawback refund): `page.evaluate("window.cameraZoomTo('#refund-badge', 1.35, 700)")`
   - In Scene 3 (B2B Discount): `page.evaluate("window.cameraZoomTo('#negotiation-modal', 1.25, 800)")`
   - Reset before navigating: `page.evaluate("window.cameraReset(600)")`
3. **Execute One-Step Audio-Video-Subtitle Encoding**:
   The final FFmpeg pass burns the subtitles with zero generation overhead.

All code snippets above have been architected to run immediately in your existing Python/Playwright/FFmpeg pipeline without adding any external npm packages or Python dependencies.
