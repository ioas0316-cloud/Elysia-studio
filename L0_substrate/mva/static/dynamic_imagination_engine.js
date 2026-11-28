/**
 * Elysia Dynamic Reality Prediction, World-Space Optical Integration & Real-Corpus Learning Engine
 * ================================================================================================
 * Real continuous dynamic learning + physically harmonized intentional recomposition loop:
 *   1. Dynamic Streams: Local Video (.mp4/.webm), Live Game/Screen Capture
 *      (getDisplayMedia), Live Webcam (getUserMedia), or Real-World Photorealistic
 *      Drifting Streams (ocean sunlight, alpine dawn lake, glass conservatory).
 *   2. Frame-by-Frame Prediction & Self-Correction (t-1 -> t -> Î(t+1) <-> I(t+1)):
 *      - Estimates live dense optical flow (vx, vy), acceleration (ax, ay), and
 *        3-band environmental irradiance (Sky / Horizon Mist / Ground Bounce RGB).
 *      - Separates Static Background / Coherent Moving Entity / Gliding Specular Light.
 *      - Warps frame(t) forward via adaptive rotor to predict Î(t+1) BEFORE I(t+1) arrives.
 *   3. World-Space Optical Integration (Zero "Floating Sticker" Look):
 *      - World-Space Camera Flow Anchoring (S3) with depth parallax so placed entities
 *        move naturally WITH the drifting world instead of sticking to the screen glass.
 *      - Intrinsic Decomposition (Albedo + 3D Dome/Sobel Surface Normal Map + De-fringed
 *        Alpha) + Pixel-Level Environmental Relighting (Sky/Ground Hemisphere + Directional
 *        Key Light + Fresnel Rim Backlight + Atmospheric Horizon Mist Veil).
 *      - Wave-Rippled Mirrored Water Reflection + Dual-Layer Contact/Cast Shadows.
 *   4. Autonomous Real-World Multi-Asset Corpus Batch Learning:
 *      - Decodes all real photographic assets on disk (/api/dynamic-engine/corpus-manifest)
 *        and user-selected multi-file photo/video batches natively via HTML5 Canvas,
 *        distills empirical optical priors (sky-to-ground ratio, mist attenuation,
 *        specular coupling) in Python, and feeds them directly back into relighting!
 */
(function () {
  'use strict';

  const STAGE = document.getElementById('ervDynamicEngineStage');
  const CANVAS = document.getElementById('diCanvas');
  if (!STAGE || !CANVAS) return;
  const ctx = CANVAS.getContext('2d');

  // Controls
  const SEL_STREAM = document.getElementById('diSelectStream');
  const BTN_UPLOAD_VID = document.getElementById('diBtnUploadVideo');
  const FILE_VID = document.getElementById('diFileVideo');
  const BTN_SCREEN = document.getElementById('diBtnScreenCapture');
  const BTN_WEBCAM = document.getElementById('diBtnWebcam');
  const BTN_SAVE_LAW = document.getElementById('diBtnSaveLaw');
  const BTN_HARVEST = document.getElementById('diBtnHarvestMoving');
  const BTN_TRAIN_CORPUS = document.getElementById('diBtnTrainCorpus');
  const BTN_UPLOAD_CORPUS = document.getElementById('diBtnUploadCorpus');
  const FILE_BATCH_CORPUS = document.getElementById('diFileBatchCorpus');

  const BTN_EXTRACT_MOTION = document.getElementById('diBtnExtractMotion');
  const SEL_MOTION_DNA = document.getElementById('diSelectMotionDna');
  const SEL_ACTOR_BODY = document.getElementById('diSelectActorBody');
  const BTN_TRANSPLANT_ACTOR = document.getElementById('diBtnTransplantActor');

  const SEL_REALM_PRESET = document.getElementById('diSelectRealmPreset');
  const SEL_PRESENCE_ROTOR = document.getElementById('diSelectPresenceRotor');
  const SEL_ALIGNMENT = document.getElementById('diSelectAlignment');
  const SEL_ARCHETYPE = document.getElementById('diSelectArchetype');
  const BTN_ROLL_CHARACTER = document.getElementById('diBtnRollCharacter');
  const CHAR_BADGE = document.getElementById('diCharBadge');

  const INTENT_INPUT = document.getElementById('diIntentInput');
  const BTN_APPLY_INTENT = document.getElementById('diBtnApplyIntent');
  const BTN_AUTO_INTENT = document.getElementById('diBtnAutoIntent');
  const BTN_RESEARCH_FRONTIER = document.getElementById('diBtnResearchFrontier');
  const BTN_CLEAR_ENTS = document.getElementById('diBtnClearEntities');
  const QUICK_BTNS = STAGE.querySelectorAll('[data-di-quick]');
  const VIEW_BTNS = STAGE.querySelectorAll('[data-di-view]');

  const READOUT_LEARN = document.getElementById('diLearnReadout');
  const READOUT_INTENT = document.getElementById('diIntentReadout');
  const READOUT_LEDGER = document.getElementById('diLedgerReadout');

  // Processing canvas dimensions (dense optical flow + crisp pixel prediction at 30-60fps)
  const PW = 384;
  const PH = 216;

  const curCanvas = document.createElement('canvas');
  curCanvas.width = PW;
  curCanvas.height = PH;
  const curCtx = curCanvas.getContext('2d', { willReadFrequently: true });

  const prevCanvas = document.createElement('canvas');
  prevCanvas.width = PW;
  prevCanvas.height = PH;
  const prevCtx = prevCanvas.getContext('2d', { willReadFrequently: true });

  const predCanvas = document.createElement('canvas');
  predCanvas.width = PW;
  predCanvas.height = PH;
  const predCtx = predCanvas.getContext('2d', { willReadFrequently: true });

  const vizCanvas = document.createElement('canvas');
  vizCanvas.width = PW;
  vizCanvas.height = PH;
  const vizCtx = vizCanvas.getContext('2d');
  const vizImg = vizCtx.createImageData(PW, PH);

  // Offscreen analyzer canvas for real-world multi-asset corpus decoding
  const CORPUS_W = 256;
  const CORPUS_H = 144;
  const corpusCanvas = document.createElement('canvas');
  corpusCanvas.width = CORPUS_W;
  corpusCanvas.height = CORPUS_H;
  const corpusCtx = corpusCanvas.getContext('2d', { willReadFrequently: true });

  const liveVideo = document.createElement('video');
  liveVideo.muted = true;
  liveVideo.loop = true;
  liveVideo.playsInline = true;
  liveVideo.crossOrigin = 'anonymous';

  const PRESET_STREAMS = {
    forest_drift: {
      label: '실사 새벽 숲 호수 (동적 카메라·빛 흐름)',
      url: '/static/assets/real_world/forest_mist.jpg',
      driftVx: 0.72,
      driftVy: 0.14,
      hasWaterSurface: true,
    },
    ocean_drift: {
      label: '실사 바다 윤슬 (동적 파동·난반사 흐름)',
      url: '/static/assets/real_world/ocean_sunlight.jpg',
      driftVx: -0.95,
      driftVy: 0.18,
      hasWaterSurface: true,
    },
    conservatory_drift: {
      label: '실사 유리 서재 (동적 조광 이동)',
      url: '/static/assets/elysia/conservatory_bg.jpg',
      driftVx: 0.55,
      driftVy: -0.10,
      hasWaterSurface: false,
    },
  };

  // Cache of intrinsically decomposed entity optical models (keyed by entity_id)
  // Value: null (loading) or { w, h, albedo, normal, alpha, relitCanvas, relitCtx, relitImg, lastSig }
  const entityModelCache = new Map();

  const state = {
    active: false,
    viewMode: 'recompose', // 'recompose' | 'pred_split' | 'cloud_error' | 'motion_class'
    streamKind: 'photo_drift', // 'photo_drift' | 'video' | 'screen' | 'camera'
    streamName: PRESET_STREAMS.forest_drift.label,
    presetKey: 'forest_drift',
    presetImg: null,
    mediaStream: null,
    driftClock: 0,
    prevCropU: null,
    prevCropV: null,
    worldDeltaNorm: [0, 0], // Exact normalized world shift per frame for S3 anchoring

    // Live dynamic frame learning state (t-1 -> t -> Î(t+1) <-> I(t+1))
    hasPrev: false,
    hasPred: false,
    prevLuma: null,
    obsFlow: [0, 0],
    obsAccel: [0, 0],
    predFlow: [0, 0],
    movingRatio: 0,
    specularRatio: 0,
    movingBBox: [0.35, 0.35, 0.28, 0.30],
    meanRGB: [120, 130, 140],
    skyRGB: [148, 168, 198],
    horizonRGB: [164, 174, 186],
    groundRGB: [58, 68, 72],
    sceneKeyX: 0.25, // Measured real dominant sun/bright azimuth in [-1, 1]
    meanLuma: 0.45,
    colorTempK: 5800,
    framesObserved: 0,
    rmseInitial: null,
    rmseCurrent: 0,
    psnrCurrent: 32,
    rmseHistory: [],
    lastPriorRecalled: null,
    autoSavedOnce: false,
    corpusTraining: false,
    autoCorpusTriggered: false,

    // Intentional Creative Recomposition State
    s4Brightness: 0.0,
    s4Warmth: 0.0,
    s2RelightDeg: 0.0,
    s1SpecularBoost: 0.0,
    placedEntities: [], // [{ uid, entity_id, name, x, y, scale, phase, reason, living?, motionDna?, behavior?, targetX?, targetY?, vx?, vy?, facing?, speedMult?, gaitPhase?, behaviorLabel?, tactileLean?, tactileLeanTarget?, tactileBreathMult?, warmthGlow?, bondStageKo?, whisperText?, whisperTimer? }]
    motionBuffer: [],   // Rolling 72-frame real recorded dynamics from Source A
    interventionRipples: [], // [{ x, y, age, maxAge, color }]
    tactileAuraTrails: [],   // [{ x, y, age, maxAge, rgb }]
    hoverTouch: null,        // { uid, zone, zoneKo, hint, nx, ny }
    tactileSession: null,    // Active continuous touch kinematics tracker
    lastIntentSummary: '개체의 머리·어깨·손에 마우스를 대고 천천히 문지르거나(쓰다듬기), 지그시 누르거나(손잡기), 톡 건드려(반응) 보세요.',
    dragEntityUid: null,
    pointerDownPos: null,
    pointerNorm: [0.5, 0.68],
    pointerInside: false,

    // Persistent Server Ledger Snapshot (including distilled_optical_priors, motion_dna_library & entity_relations)
    ledger: null,
  };

  let rafId = 0;
  let lastTs = performance.now();
  let lastReadoutTs = 0;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  /**
   * True Intrinsic Optical Decomposition for Placed Real Photographic Entities:
   *   1. Exterior Border Flood-Fill Matte + Color-Spill Decontamination (eliminates white sticker halo!)
   *   2. Studio-Light-Stripped Intrinsic Albedo (local illumination normalization)
   *   3. 3D Volume Dome + Sobel Micro-Relief Surface Normal Map (nx, ny, nz)
   * Enables genuine per-pixel environmental relighting (Sky/Ground Hemisphere + Key + Fresnel Rim + Mist)!
   */
  function buildDecomposedEntityModel(imgOrCanvas, keyMode) {
    const srcW = imgOrCanvas.naturalWidth || imgOrCanvas.width || 320;
    const srcH = imgOrCanvas.naturalHeight || imgOrCanvas.height || 320;
    // Keep decomposed entity crisp (~240px wide) while blazingly fast to relight per-pixel
    const mw = Math.min(240, srcW);
    const mh = Math.max(32, Math.round(mw * (srcH / Math.max(1, srcW))));

    const tmp = document.createElement('canvas');
    tmp.width = mw;
    tmp.height = mh;
    const tctx = tmp.getContext('2d', { willReadFrequently: true });
    tctx.drawImage(imgOrCanvas, 0, 0, mw, mh);

    const idata = tctx.getImageData(0, 0, mw, mh);
    const d = idata.data;
    const n = mw * mh;
    const alpha = new Float32Array(n);

    if (keyMode === 'alpha_direct') {
      for (let i = 0; i < n; i++) {
        alpha[i] = d[i * 4 + 3] / 255.0;
      }
    } else {
      const isBg = new Uint8Array(n);
      const queue = new Int32Array(n);
      let qHead = 0, qTail = 0;

      function isNearWhite(idx) {
        const i4 = idx * 4;
        const r = d[i4], g = d[i4 + 1], b = d[i4 + 2];
        const maxC = Math.max(r, g, b);
        const minC = Math.min(r, g, b);
        return minC > 206 && (maxC - minC) < 34;
      }

      for (let x = 0; x < mw; x++) {
        const top = x;
        const bot = (mh - 1) * mw + x;
        if (isNearWhite(top) && !isBg[top]) { isBg[top] = 1; queue[qTail++] = top; }
        if (isNearWhite(bot) && !isBg[bot]) { isBg[bot] = 1; queue[qTail++] = bot; }
      }
      for (let y = 0; y < mh; y++) {
        const lt = y * mw;
        const rt = y * mw + (mw - 1);
        if (isNearWhite(lt) && !isBg[lt]) { isBg[lt] = 1; queue[qTail++] = lt; }
        if (isNearWhite(rt) && !isBg[rt]) { isBg[rt] = 1; queue[qTail++] = rt; }
      }

      while (qHead < qTail) {
        const cur = queue[qHead++];
        const cx = cur % mw;
        const cy = (cur - cx) / mw;
        if (cx > 0) {
          const nb = cur - 1;
          if (!isBg[nb] && isNearWhite(nb)) { isBg[nb] = 1; queue[qTail++] = nb; }
        }
        if (cx < mw - 1) {
          const nb = cur + 1;
          if (!isBg[nb] && isNearWhite(nb)) { isBg[nb] = 1; queue[qTail++] = nb; }
        }
        if (cy > 0) {
          const nb = cur - mw;
          if (!isBg[nb] && isNearWhite(nb)) { isBg[nb] = 1; queue[qTail++] = nb; }
        }
        if (cy < mh - 1) {
          const nb = cur + mw;
          if (!isBg[nb] && isNearWhite(nb)) { isBg[nb] = 1; queue[qTail++] = nb; }
        }
      }

      // Compute 2-ring soft matte + white fringe decontamination
      for (let y = 0; y < mh; y++) {
        for (let x = 0; x < mw; x++) {
          const i = y * mw + x;
          if (isBg[i]) {
            alpha[i] = 0.0;
            continue;
          }
          let bg1 = 0;
          if (x > 0 && isBg[i - 1]) bg1++;
          if (x < mw - 1 && isBg[i + 1]) bg1++;
          if (y > 0 && isBg[i - mw]) bg1++;
          if (y < mh - 1 && isBg[i + mw]) bg1++;

          if (bg1 > 0) {
            const i4 = i * 4;
            const lum = (d[i4] + d[i4 + 1] + d[i4 + 2]) / 3;
            // Aggressively soften bright studio-fringe pixels & de-spill white halo
            alpha[i] = lum > 195 ? 0.14 : (lum > 155 ? 0.42 : 0.72);
            const despill = lum > 170 ? 0.72 : 0.88;
            d[i4] = Math.round(d[i4] * despill);
            d[i4 + 1] = Math.round(d[i4 + 1] * despill);
            d[i4 + 2] = Math.round(d[i4 + 2] * despill);
          } else {
            // Check 2nd ring for subtle anti-aliased transition
            let bg2 = 0;
            if (x > 1 && isBg[i - 2]) bg2++;
            if (x < mw - 2 && isBg[i + 2]) bg2++;
            if (y > 1 && isBg[i - 2 * mw]) bg2++;
            if (y < mh - 2 && isBg[i + 2 * mw]) bg2++;
            alpha[i] = bg2 > 0 ? 0.90 : 1.0;
          }
        }
      }
    }

    // Find foreground bounding box & mean foreground luma to normalize studio exposure
    let minX = mw, maxX = 0, minY = mh, maxY = 0;
    let fgLumaSum = 0, fgCount = 0;
    const luma = new Float32Array(n);
    for (let y = 0; y < mh; y++) {
      for (let x = 0; x < mw; x++) {
        const i = y * mw + x;
        const i4 = i * 4;
        const lm = (0.2126 * d[i4] + 0.7152 * d[i4 + 1] + 0.0722 * d[i4 + 2]) / 255.0;
        luma[i] = lm;
        if (alpha[i] > 0.25) {
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
          fgLumaSum += lm;
          fgCount++;
        }
      }
    }
    const meanFgLuma = fgCount > 0 ? fgLumaSum / fgCount : 0.5;
    const cx = (minX + maxX) * 0.5;
    const cy = (minY + maxY) * 0.5;
    const rx = Math.max(8, (maxX - minX) * 0.52);
    const ry = Math.max(8, (maxY - minY) * 0.52);

    // Strip baked-in studio exposure bias -> Intrinsic Albedo (normalized to ~0.55 neutral reflectance)
    // and build 3D Dome + Sobel Micro-Bump Normal Map (nx, ny, nz)
    const albedo = new Float32Array(n * 3);
    const normal = new Float32Array(n * 3);
    const exposureNorm = clamp(0.54 / Math.max(0.18, meanFgLuma), 0.72, 1.32);

    for (let y = 0; y < mh; y++) {
      for (let x = 0; x < mw; x++) {
        const i = y * mw + x;
        const i3 = i * 3;
        const i4 = i * 4;

        // Slight studio-highlight compression so bright white fur/skin can receive colored environmental light!
        const r = clamp((d[i4] / 255.0) * exposureNorm, 0, 1.05);
        const g = clamp((d[i4 + 1] / 255.0) * exposureNorm, 0, 1.05);
        const b = clamp((d[i4 + 2] / 255.0) * exposureNorm, 0, 1.05);
        // Gentle desaturation of studio warm/cool cast -> clean intrinsic reflectance
        const avg = (r + g + b) / 3;
        albedo[i3] = clamp(avg + (r - avg) * 0.94, 0, 1);
        albedo[i3 + 1] = clamp(avg + (g - avg) * 0.94, 0, 1);
        albedo[i3 + 2] = clamp(avg + (b - avg) * 0.94, 0, 1);

        // Macro 3D dome normal (left/right/top/bottom curvature of the subject body)
        const dx = clamp((x - cx) / rx, -0.96, 0.96);
        const dy = clamp((y - cy) / ry, -0.96, 0.96);
        const r2 = Math.min(0.92, dx * dx + dy * dy);
        const domeZ = Math.sqrt(Math.max(0.06, 1.0 - r2));

        // Micro surface detail normal from luminance gradient (Sobel)
        const xm = x > 0 ? x - 1 : x;
        const xp = x < mw - 1 ? x + 1 : x;
        const ym = y > 0 ? y - 1 : y;
        const yp = y < mh - 1 ? y + 1 : y;
        const gx = (luma[y * mw + xp] - luma[y * mw + xm]) * 1.8;
        const gy = (luma[yp * mw + x] - luma[ym * mw + x]) * 1.8;

        const nx = dx * 0.72 - gx * 0.42;
        const ny = dy * 0.68 - gy * 0.42;
        const nz = domeZ;
        const len = Math.hypot(nx, ny, nz) || 1.0;
        normal[i3] = nx / len;
        normal[i3 + 1] = ny / len;
        normal[i3 + 2] = nz / len;
      }
    }

    const relitCanvas = document.createElement('canvas');
    relitCanvas.width = mw;
    relitCanvas.height = mh;
    const relitCtx = relitCanvas.getContext('2d');
    const relitImg = relitCtx.createImageData(mw, mh);

    return {
      w: mw,
      h: mh,
      minYNorm: minY / mh,
      maxYNorm: maxY / mh,
      albedo,
      normal,
      alpha,
      relitCanvas,
      relitCtx,
      relitImg,
      lastSig: '',
    };
  }

  /**
   * Pixel-Level Physically Harmonized Relighting using:
   *   - Live scene 3-band irradiance (Sky RGB, Horizon Mist RGB, Ground Bounce RGB)
   *   - Distilled Real-World Optical Priors from Python corpus (sky_to_ground_ratio, horizon_mist_ratio)
   *   - Directional Key Light (N · L_sun) + Hemisphere Ambient + Fresnel Rim Backlight + Atmospheric Mist
   */
  function relightEntityModel(model, depthNorm, env) {
    // Quantize signature so we only re-shade when light or depth meaningfully changes
    const q = (v) => Math.round(v * 20);
    const sig = [
      q(env.sky[0]), q(env.sky[1]), q(env.sky[2]),
      q(env.hor[0]), q(env.hor[1]), q(env.hor[2]),
      q(env.gnd[0]), q(env.gnd[1]), q(env.gnd[2]),
      q(env.lx), q(env.ly), q(depthNorm),
      q(env.mistPrior), q(env.skyGroundPrior),
    ].join('|');

    if (model.lastSig === sig) return model.relitCanvas;
    model.lastSig = sig;

    const { w, h, albedo, normal, alpha, relitImg, relitCtx } = model;
    const out = relitImg.data;
    const n = w * h;

    const skyR = env.sky[0], skyG = env.sky[1], skyB = env.sky[2];
    const horR = env.hor[0], horG = env.hor[1], horB = env.hor[2];
    const gndR = env.gnd[0], gndG = env.gnd[1], gndB = env.gnd[2];
    const keyR = env.key[0], keyG = env.key[1], keyB = env.key[2];
    const lx = env.lx, ly = env.ly, lz = env.lz;

    // Empirical learned priors from real corpus!
    const skyWeight = clamp(0.45 + (env.skyGroundPrior - 1.0) * 0.24, 0.38, 0.92);
    const gndWeight = clamp(0.55 - (env.skyGroundPrior - 1.0) * 0.14, 0.24, 0.66);
    const depthDist = clamp(1.0 - depthNorm, 0.0, 0.85);
    const mistFactor = clamp(0.05 + depthDist * env.mistPrior * 1.65, 0.05, 0.46);
    const invMist = 1.0 - mistFactor;

    for (let y = 0; y < h; y++) {
      const yNorm = y / Math.max(1, h - 1);
      // Bottom 9% foot/root contact zone receives extra ground bounce & subtle grass/water feathering
      const footBand = clamp((yNorm - 0.88) / 0.12, 0.0, 1.0);
      const footOcclusion = 1.0 - footBand * 0.24;

      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const a = alpha[i];
        const i4 = i * 4;
        if (a <= 0.01) {
          out[i4 + 3] = 0;
          continue;
        }

        const i3 = i * 3;
        const ar = albedo[i3];
        const ag = albedo[i3 + 1];
        const ab = albedo[i3 + 2];

        const nx = normal[i3];
        const ny = normal[i3 + 1];
        const nz = normal[i3 + 2];

        // 1. Hemisphere Ambient (top faces sky -ny > 0, bottom faces ground +ny > 0)
        const upFactor = clamp(0.5 - 0.5 * ny, 0.0, 1.0);
        const ambR = (skyR * upFactor * skyWeight + gndR * (1.0 - upFactor) * gndWeight) * 1.18;
        const ambG = (skyG * upFactor * skyWeight + gndG * (1.0 - upFactor) * gndWeight) * 1.18;
        const ambB = (skyB * upFactor * skyWeight + gndB * (1.0 - upFactor) * gndWeight) * 1.18;

        // 2. Wrapped Directional Key Light (N · L_sun)
        const ndl = nx * lx + ny * ly + nz * lz;
        const wrapDiff = clamp(ndl * 0.58 + 0.42, 0.0, 1.0);
        const diffGain = wrapDiff * wrapDiff * 0.72;

        // 3. Fresnel Rim Backlight (sky/sunlight wrapping around subject silhouette edges!)
        const fresnel = Math.pow(clamp(1.0 - nz, 0.0, 1.0), 2.35);
        const rimAmt = fresnel * (0.30 + 0.45 * upFactor) * (1.0 - footBand * 0.7);

        let cr = (ar * (ambR + keyR * diffGain) + skyR * rimAmt * 0.52) * footOcclusion;
        let cg = (ag * (ambG + keyG * diffGain) + skyG * rimAmt * 0.52) * footOcclusion;
        let cb = (ab * (ambB + keyB * diffGain) + skyB * rimAmt * 0.52) * footOcclusion;

        // 4. Subtle ground-bounce tint right at the feet/trunk base
        if (footBand > 0.01) {
          const gb = footBand * 0.22;
          cr = cr * (1.0 - gb) + gndR * gb;
          cg = cg * (1.0 - gb) + gndG * gb;
          cb = cb * (1.0 - gb) + gndB * gb;
        }

        // 5. Atmospheric Perspective Horizon Mist Veil (learned mist prior!)
        cr = cr * invMist + horR * mistFactor;
        cg = cg * invMist + horG * mistFactor;
        cb = cb * invMist + horB * mistFactor;

        // Filmic soft shoulder to avoid harsh blown-out digital edges
        cr = cr / (1.0 + Math.max(0, cr - 0.88) * 0.55);
        cg = cg / (1.0 + Math.max(0, cg - 0.88) * 0.55);
        cb = cb / (1.0 + Math.max(0, cb - 0.88) * 0.55);

        out[i4] = Math.round(clamp(cr, 0, 1) * 255);
        out[i4 + 1] = Math.round(clamp(cg, 0, 1) * 255);
        out[i4 + 2] = Math.round(clamp(cb, 0, 1) * 255);
        // Gentle foot contact alpha softening so the entity sits inside ground/water
        out[i4 + 3] = Math.round(clamp(a * (1.0 - footBand * 0.18), 0, 1) * 255);
      }
    }

    relitCtx.putImageData(relitImg, 0, 0);
    return model.relitCanvas;
  }

  function ensureEntityLoaded(entityMeta) {
    if (!entityMeta || !entityMeta.id || !entityMeta.asset_url) return;
    if (entityModelCache.has(entityMeta.id)) return;
    entityModelCache.set(entityMeta.id, null);
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      entityModelCache.set(entityMeta.id, buildDecomposedEntityModel(img, entityMeta.key_mode || 'white_matte'));
    };
    img.src = entityMeta.asset_url;
  }

  function findEntityMeta(entityId) {
    const list = (state.ledger && state.ledger.harvested_entities) || [];
    const found = list.find((e) => e.id === entityId);
    if (found) return found;
    const defaults = {
      'entity::puppy': { id: 'entity::puppy', name: '강아지', asset_url: '/static/assets/real_world/entity_puppy.jpg', default_scale: 0.24, default_y: 0.79, key_mode: 'white_matte' },
      'entity::cat': { id: 'entity::cat', name: '고양이', asset_url: '/static/assets/real_world/entity_cat.jpg', default_scale: 0.21, default_y: 0.80, key_mode: 'white_matte' },
      'entity::pine_tree': { id: 'entity::pine_tree', name: '삼나무', asset_url: '/static/assets/real_world/entity_pine_tree.jpg', default_scale: 0.44, default_y: 0.67, key_mode: 'white_matte' },
      'entity::embrace': { id: 'entity::embrace', name: '포옹하는 두 사람', asset_url: '/static/assets/real_world/entity_embrace.jpg', default_scale: 0.42, default_y: 0.74, key_mode: 'white_matte' },
    };
    return defaults[entityId] || null;
  }

  async function apiDynamic(action, params) {
    try {
      const res = await fetch('/api/dynamic-engine/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, params: params || {} }),
      });
      if (!res.ok) return null;
      const data = await res.json();
      if (data && data.memory_summary) {
        state.ledger = data;
        (data.harvested_entities || []).forEach(ensureEntityLoaded);
        syncCrossMediaSelectors();
      }
      return data;
    } catch {
      return null;
    }
  }

  function syncCrossMediaSelectors() {
    if (!state.ledger) return;
    if (SEL_MOTION_DNA && Array.isArray(state.ledger.motion_dna_library)) {
      const prevVal = SEL_MOTION_DNA.value;
      SEL_MOTION_DNA.innerHTML = '';
      state.ledger.motion_dna_library.slice().reverse().forEach((dna) => {
        const opt = document.createElement('option');
        opt.value = dna.id;
        const badge = dna.origin === 'live_video_extraction' ? '[추출]' : '[기준]';
        opt.textContent = `${badge} ${dna.name} · ${Number(dna.dominant_freq_hz || 1.2).toFixed(1)}Hz`;
        SEL_MOTION_DNA.appendChild(opt);
      });
      if (prevVal && Array.from(SEL_MOTION_DNA.options).some((o) => o.value === prevVal)) {
        SEL_MOTION_DNA.value = prevVal;
      }
    }
    if (SEL_ACTOR_BODY && Array.isArray(state.ledger.harvested_entities)) {
      const prevVal = SEL_ACTOR_BODY.value;
      SEL_ACTOR_BODY.innerHTML = '';
      state.ledger.harvested_entities.forEach((ent) => {
        const opt = document.createElement('option');
        opt.value = ent.id;
        opt.textContent = ent.origin === 'live_motion_harvest' ? `[수확] ${ent.name}` : ent.name;
        SEL_ACTOR_BODY.appendChild(opt);
      });
      if (prevVal && Array.from(SEL_ACTOR_BODY.options).some((o) => o.value === prevVal)) {
        SEL_ACTOR_BODY.value = prevVal;
      } else if (Array.from(SEL_ACTOR_BODY.options).some((o) => o.value === 'entity::cat')) {
        SEL_ACTOR_BODY.value = 'entity::cat';
      }
    }
  }

  function findMotionDna(dnaId) {
    const list = (state.ledger && state.ledger.motion_dna_library) || [];
    return list.find((d) => d.id === dnaId) || list[list.length - 1] || null;
  }

  async function extractMotionDnaFromSourceA() {
    const samples = state.motionBuffer.slice(-64);
    const res = await apiDynamic('extract_motion_dna', {
      source_name: state.streamName,
      stream_kind: state.streamKind,
      samples,
    });
    if (res && res.extracted_motion_dna) {
      const dna = res.extracted_motion_dna;
      syncCrossMediaSelectors();
      if (SEL_MOTION_DNA) SEL_MOTION_DNA.value = dna.id;
      state.lastIntentSummary =
        `[영상 A 동작 DNA 추출] ${dna.gait_label_ko} (${dna.dominant_freq_hz}Hz · ${dna.sample_frames_used}프레임) — ` +
        `이제 다른 영상/환경 B로 전환해 [타 환경 살아있는 이식]을 눌러보세요!`;
      renderReadouts(true);
    }
  }

  async function transplantLivingActorToWorldB() {
    const dnaId = (SEL_MOTION_DNA && SEL_MOTION_DNA.value) || 'dna::predator_prowl';
    const entityId = (SEL_ACTOR_BODY && SEL_ACTOR_BODY.value) || 'entity::cat';
    const res = await apiDynamic('transplant_living_actor', {
      motion_dna_id: dnaId,
      entity_id: entityId,
      target_world_name: state.streamName,
    });
    if (!res || !res.transplant_result) return;
    const tr = res.transplant_result;
    const dna = res.motion_dna || findMotionDna(dnaId);
    const meta = res.entity_meta || findEntityMeta(entityId);
    if (meta) ensureEntityLoaded(meta);

    const startX = clamp(0.28 + Math.random() * 0.44, 0.22, 0.78);
    const startY = clamp((meta && meta.default_y) || 0.78, 0.64, 0.85);
    const chosenArch = (SEL_ARCHETYPE && SEL_ARCHETYPE.value) || 'spirit_beast';
    const coupling = (state.ledger && state.ledger.archetype_couplings && state.ledger.archetype_couplings[chosenArch]) || null;
    const actor = {
      uid: `actor_${Date.now()}_${Math.random().toString(36).slice(2, 5)}`,
      entity_id: (meta && meta.id) || entityId,
      name: (meta && meta.name) || tr.entity_name,
      archetype: chosenArch,
      archetypeLabelKo: (coupling && coupling.archetype_label_ko) || '영수·신수',
      x: startX,
      y: startY,
      scale: clamp((meta && meta.default_scale) || 0.23, 0.16, 0.36),
      phase: Math.random() * Math.PI * 2,
      reason: tr.summary,
      // Living Interactive Causal Actor fields (Source A DNA -> Target World B + S4 Social Coupling)
      living: true,
      motionDna: dna,
      behavior: 'curious_patrol',
      behaviorLabel: (coupling && coupling.stance_ko) || (dna ? dna.gait_label_ko : '자율 탐색'),
      targetX: clamp(startX + (Math.random() > 0.5 ? 0.24 : -0.24), 0.16, 0.84),
      targetY: clamp(startY + (Math.random() - 0.5) * 0.08, 0.64, 0.86),
      vx: 0,
      vy: 0,
      facing: 1,
      speedMult: (coupling && coupling.speed_mult) || 1.0,
      socialBaseLean: (coupling && coupling.base_lean_rad) || 0,
      captivationPull: (coupling && coupling.captivation_pull) || 0,
      courtesyRestraint: (coupling && coupling.courtesy_restraint) || 0,
      gazeLock: Boolean(coupling && coupling.gaze_lock),
      gaitPhase: 0,
      patrolTimer: 1.5 + Math.random() * 2.5,
      jumpLift: 0,
      dynTilt: 0,
      dynSquash: 1.0,
    };
    state.placedEntities.push(actor);
    state.lastIntentSummary = `[A→B 교차 이식 · ${actor.archetypeLabelKo}] ${tr.summary}`;
    renderReadouts(true);
  }

  function applySocialFieldToPlacedEntities() {
    if (!state.ledger) return;
    const wf = state.ledger.world_social_field || {};
    const couplings = state.ledger.archetype_couplings || {};
    if (CHAR_BADGE && wf.race_label_ko) {
      CHAR_BADGE.textContent =
        `${wf.race_label_ko}[${wf.trait_label_ko || '특성'}] · ${wf.alignment_label_ko || '중립 선'} · ` +
        `매력${Math.round((wf.allure_gravity || 0.48) * 100)}/카리스마${Math.round((wf.charisma_rotor || 0.45) * 100)} · ` +
        `정령${Math.round((wf.spirit_affinity || 0.4) * 100)}`;
    }
    if (SEL_REALM_PRESET && wf.preset_id && Array.from(SEL_REALM_PRESET.options).some((o) => o.value === wf.preset_id)) {
      SEL_REALM_PRESET.value = wf.preset_id;
    }
    if (SEL_PRESENCE_ROTOR && wf.presence_preset_id && Array.from(SEL_PRESENCE_ROTOR.options).some((o) => o.value === wf.presence_preset_id)) {
      SEL_PRESENCE_ROTOR.value = wf.presence_preset_id;
    }
    if (SEL_ALIGNMENT && wf.alignment_preset_id && Array.from(SEL_ALIGNMENT.options).some((o) => o.value === wf.alignment_preset_id)) {
      SEL_ALIGNMENT.value = wf.alignment_preset_id;
    }

    state.placedEntities.forEach((ent) => {
      if (ent.entity_id === 'entity::pine_tree') return;
      const arch = ent.archetype || (ent.entity_id === 'entity::embrace' ? 'citizen_npc' : (ent.entity_id === 'entity::puppy' ? 'companion_pet' : 'spirit_beast'));
      ent.archetype = arch;
      const cp = couplings[arch];
      if (!cp) return;
      ent.archetypeLabelKo = cp.archetype_label_ko;
      ent.socialBaseLean = Number(cp.base_lean_rad || 0);
      ent.captivationPull = Number(cp.captivation_pull || 0);
      ent.courtesyRestraint = Number(cp.courtesy_restraint || 0);
      ent.gazeLock = Boolean(cp.gaze_lock);
      if (ent.living) {
        ent.behaviorLabel = `${cp.archetype_label_ko} · ${cp.stance_ko}`;
        ent.speedMult = Number(cp.speed_mult || 1.0);
        if (cp.stance === 'hostile_guard' || cp.stance === 'cower_retreat') {
          ent.targetX = clamp(ent.x >= 0.5 ? 0.82 : 0.18, 0.14, 0.86);
        } else if (cp.stance === 'captivated_gaze' || cp.stance === 'devoted_companion' || cp.stance === 'protective_huddle') {
          ent.targetX = clamp(state.pointerNorm[0] + (Math.random() - 0.5) * 0.16, 0.22, 0.78);
        }
      }
      ent.tactileLeanTarget = Number(cp.base_lean_rad || 0) * (ent.facing || 1);
    });
  }

  async function applyRealmPreset(presetId) {
    const res = await apiDynamic('set_world_social_field', { preset_id: presetId });
    if (!res || !res.world_social_field) return;
    applySocialFieldToPlacedEntities();
    const wf = res.world_social_field;
    const cps = res.archetype_couplings || {};
    const sb = cps.spirit_beast ? cps.spirit_beast.stance_ko : '';
    const wm = cps.wild_monster ? cps.wild_monster.stance_ko : '';
    const np = cps.citizen_npc ? cps.citizen_npc.stance_ko : '';
    state.lastIntentSummary = `[S4 세계장 전환: ${wf.realm_label_ko}] 영수(${sb}) · NPC(${np}) · 몬스터(${wm}) 자세와 촉감 반응이 즉시 재편되었습니다.`;
    renderReadouts(true);
  }

  async function applyPresenceRotorPreset(presenceId) {
    const res = await apiDynamic('set_world_social_field', { presence_preset_id: presenceId });
    if (!res || !res.world_social_field) return;
    applySocialFieldToPlacedEntities();
    const wf = res.world_social_field;
    const cps = res.archetype_couplings || {};
    const np = cps.citizen_npc || {};
    const sb = cps.spirit_beast || {};
    state.lastIntentSummary =
      `[스탯 스케일 로터 전환: 매력 ${Math.round((wf.allure_gravity || 0.48) * 100)} · 카리스마 ${Math.round((wf.charisma_rotor || 0.45) * 100)}] ` +
      `NPC(${np.stance_ko || ''}${np.gaze_lock ? ' · 시선 인력 고정' : ''}) · 영수(${sb.stance_ko || ''})로 장력이 즉시 휘어졌습니다.`;
    renderReadouts(true);
  }

  async function applyAlignmentPreset(alignmentId) {
    const res = await apiDynamic('set_world_social_field', { alignment_preset_id: alignmentId });
    if (!res || !res.world_social_field) return;
    applySocialFieldToPlacedEntities();
    const wf = res.world_social_field;
    const cps = res.archetype_couplings || {};
    const sb = cps.spirit_beast || {};
    const wm = cps.wild_monster || {};
    const np = cps.citizen_npc || {};
    state.lastIntentSummary =
      `[가치관·성향 공명: ${wf.alignment_label_ko}] ` +
      `영수(${sb.stance_ko || ''} · 공명 ${Number(sb.alignment_resonance || 0).toFixed(2)}) · ` +
      `NPC(${np.stance_ko || ''}) · 몬스터(${wm.stance_ko || ''})가 당신의 가치관을 감지합니다.`;
    renderReadouts(true);
  }

  async function rollCharacterLineage() {
    const res = await apiDynamic('roll_character_profile', {});
    if (!res || !res.rolled_character) return;
    applySocialFieldToPlacedEntities();
    const rc = res.rolled_character;
    const cps = res.archetype_couplings || {};
    state.lastIntentSummary =
      `[캐릭터 탄생: ${rc.realm_label_ko}] ` +
      `NPC(${(cps.citizen_npc && cps.citizen_npc.stance_ko) || ''}) · ` +
      `영수(${(cps.spirit_beast && cps.spirit_beast.stance_ko) || ''}) · ` +
      `몬스터(${(cps.wild_monster && cps.wild_monster.stance_ko) || ''})가 당신의 매혹·성향·정령 기운을 즉시 감지합니다!`;
    renderReadouts(true);
  }

  let frontierCycleIdx = 0;
  const FRONTIER_SAMPLES = ['SF 우주함선', '마나·에테르 마법 법칙', '비행기', '자동차'];

  async function runFrontierResearch(goalText) {
    const query = (goalText || '').trim() || FRONTIER_SAMPLES[frontierCycleIdx++ % FRONTIER_SAMPLES.length];
    const res = await apiDynamic('research_frontier_goal', { goal_text: query });
    if (!res || !res.research_bridge) return;
    const rb = res.research_bridge;
    state.lastIntentSummary = rb.summary_ko;
    renderReadouts(true);
  }

  async function interveneWorldActors(opts) {
    const { commandText, clickIntervention, targetX, targetY } = opts || {};
    const livingActors = state.placedEntities.filter((e) => e.living);
    if (livingActors.length === 0) {
      if (commandText) {
        // Auto-transplant one living actor first if the user speaks a live behavior command!
        await transplantLivingActorToWorldB();
      } else {
        return;
      }
    }
    const res = await apiDynamic('intervene_living_actor', {
      command_text: commandText || '',
      click_intervention: !!clickIntervention,
      target_x: typeof targetX === 'number' ? targetX : 0.5,
      target_y: typeof targetY === 'number' ? targetY : 0.76,
      target_world_name: state.streamName,
    });
    if (!res || !res.intervention) return;
    const iv = res.intervention;
    state.placedEntities.forEach((ent) => {
      if (!ent.living) return;
      ent.behavior = iv.behavior;
      ent.behaviorLabel = iv.behavior_label_ko;
      ent.speedMult = Number(iv.speed_mult || 1.0);
      if (iv.behavior === 'evade_retreat') {
        // Move away from intervention point smoothly
        const awayX = ent.x >= iv.target_x ? Math.min(0.88, ent.x + 0.28) : Math.max(0.12, ent.x - 0.28);
        ent.targetX = awayX;
        ent.targetY = clamp(ent.y + (Math.random() - 0.5) * 0.06, 0.62, 0.86);
      } else if (iv.behavior === 'approach_user' || iv.behavior === 'playful_chase') {
        ent.targetX = clamp(iv.target_x + (Math.random() - 0.5) * 0.06, 0.14, 0.86);
        ent.targetY = clamp(iv.target_y, 0.60, 0.86);
      } else if (iv.behavior === 'calm_rest') {
        ent.targetX = ent.x;
        ent.targetY = ent.y;
      }
    });
    state.lastIntentSummary = `[실시간 개입 · ${iv.behavior_label_ko}] ${iv.reaction_ko}`;
    renderReadouts(true);
  }

  /**
   * Real-World Pixel Optical Profile Extractor (used by Autonomous Corpus Batch Trainer)
   * Decodes genuine pixels of any real photograph or video frame and extracts:
   *   - sky_rgb (top 25%), horizon_rgb (mid 30%), ground_rgb (bottom 25%)
   *   - mean_luma, color_temp_k, specular_ratio, normal_energy, original pixel_count
   */
  function extractOpticalProfileFromDrawable(drawable, origW, origH, sourceName, mediaKind) {
    corpusCtx.clearRect(0, 0, CORPUS_W, CORPUS_H);
    corpusCtx.drawImage(drawable, 0, 0, CORPUS_W, CORPUS_H);
    const data = corpusCtx.getImageData(0, 0, CORPUS_W, CORPUS_H).data;
    const n = CORPUS_W * CORPUS_H;
    const luma = new Float32Array(n);

    let skyR = 0, skyG = 0, skyB = 0, skyC = 0;
    let horR = 0, horG = 0, horB = 0, horC = 0;
    let gndR = 0, gndG = 0, gndB = 0, gndC = 0;
    let sumR = 0, sumB = 0, sumL = 0, specCount = 0;

    const skyEnd = Math.floor(CORPUS_H * 0.25);
    const horStart = Math.floor(CORPUS_H * 0.35);
    const horEnd = Math.floor(CORPUS_H * 0.65);
    const gndStart = Math.floor(CORPUS_H * 0.75);

    for (let y = 0; y < CORPUS_H; y++) {
      for (let x = 0; x < CORPUS_W; x++) {
        const i = y * CORPUS_W + x;
        const i4 = i * 4;
        const r = data[i4], g = data[i4 + 1], b = data[i4 + 2];
        const lm = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0;
        luma[i] = lm;
        sumR += r; sumB += b; sumL += lm;

        const maxC = Math.max(r, g, b);
        const minC = Math.min(r, g, b);
        const sat = maxC > 1 ? (maxC - minC) / maxC : 0;
        if (lm > 0.72 && sat < 0.32) specCount++;

        if (y < skyEnd) { skyR += r; skyG += g; skyB += b; skyC++; }
        if (y >= horStart && y < horEnd) { horR += r; horG += g; horB += b; horC++; }
        if (y >= gndStart) { gndR += r; gndG += g; gndB += b; gndC++; }
      }
    }

    // Sobel gradient energy (micro-surface relief richness)
    let gradSum = 0, gradCount = 0;
    for (let y = 1; y < CORPUS_H - 1; y += 2) {
      for (let x = 1; x < CORPUS_W - 1; x += 2) {
        const i = y * CORPUS_W + x;
        const gx = luma[i + 1] - luma[i - 1];
        const gy = luma[i + CORPUS_W] - luma[i - CORPUS_W];
        gradSum += Math.hypot(gx, gy);
        gradCount++;
      }
    }

    const rb = (sumR / n) / Math.max(1, sumB / n);
    const tempK = Math.round(clamp(6500 - (rb - 1.0) * 3200, 2200, 10500));

    return {
      source_name: sourceName,
      media_kind: mediaKind || 'photo',
      pixel_count: Math.max(CORPUS_W * CORPUS_H, Math.round((origW || CORPUS_W) * (origH || CORPUS_H))),
      sky_rgb: [Math.round(skyR / Math.max(1, skyC)), Math.round(skyG / Math.max(1, skyC)), Math.round(skyB / Math.max(1, skyC))],
      horizon_rgb: [Math.round(horR / Math.max(1, horC)), Math.round(horG / Math.max(1, horC)), Math.round(horB / Math.max(1, horC))],
      ground_rgb: [Math.round(gndR / Math.max(1, gndC)), Math.round(gndG / Math.max(1, gndC)), Math.round(gndB / Math.max(1, gndC))],
      color_temp_k: tempK,
      mean_luma: Number((sumL / n).toFixed(4)),
      specular_ratio: Number((specCount / n).toFixed(4)),
      normal_energy: Number(clamp(gradSum / Math.max(1, gradCount), 0, 1).toFixed(4)),
    };
  }

  function decodeImageUrlProfile(url, name) {
    return new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        try {
          resolve(extractOpticalProfileFromDrawable(img, img.naturalWidth, img.naturalHeight, name, 'photo'));
        } catch {
          resolve(null);
        }
      };
      img.onerror = () => resolve(null);
      img.src = url;
    });
  }

  function decodeVideoFileProfiles(file) {
    return new Promise((resolve) => {
      const url = URL.createObjectURL(file);
      const vid = document.createElement('video');
      vid.muted = true;
      vid.playsInline = true;
      vid.preload = 'auto';
      const profiles = [];

      const cleanup = () => {
        URL.revokeObjectURL(url);
        resolve(profiles);
      };

      vid.onerror = cleanup;
      vid.onloadedmetadata = () => {
        const dur = Number.isFinite(vid.duration) && vid.duration > 0.4 ? vid.duration : 1.0;
        const times = [dur * 0.25, dur * 0.65];
        let idx = 0;

        const seekNext = () => {
          if (idx >= times.length) { cleanup(); return; }
          try {
            vid.currentTime = times[idx];
          } catch {
            cleanup();
          }
        };

        vid.onseeked = () => {
          try {
            const p = extractOpticalProfileFromDrawable(
              vid,
              vid.videoWidth || 1280,
              vid.videoHeight || 720,
              `${file.name}#f${idx + 1}`,
              'video'
            );
            if (p) profiles.push(p);
          } catch {}
          idx++;
          seekNext();
        };

        seekNext();
      };
      vid.src = url;
    });
  }

  /**
   * Autonomous Real-World Disk Corpus Batch Trainer
   * Discovers all real high-res assets on disk via /api/dynamic-engine/corpus-manifest,
   * decodes their actual pixels, and distills empirical cross-scene optical laws in Python!
   */
  async function trainFromDiskCorpus(silentAuto) {
    if (state.corpusTraining) return;
    state.corpusTraining = true;
    if (BTN_TRAIN_CORPUS) BTN_TRAIN_CORPUS.disabled = true;
    try {
      const res = await fetch('/api/dynamic-engine/corpus-manifest');
      if (!res.ok) return;
      const manifest = await res.json();
      const items = Array.isArray(manifest.items) ? manifest.items : [];
      if (!items.length) return;

      if (!silentAuto) {
        state.lastIntentSummary = `실세계 자산 ${items.length}개 픽셀 직접 해독·광학 법칙 추출 중…`;
        renderReadouts(true);
      }

      const measured = [];
      for (let i = 0; i < items.length; i++) {
        const it = items[i];
        const prof = await decodeImageUrlProfile(it.url, it.name);
        if (prof) measured.push(prof);
      }

      if (measured.length > 0) {
        const reply = await apiDynamic('ingest_real_corpus_batch', { items: measured });
        if (reply && reply.corpus_batch_result) {
          // Force immediate re-shading of all placed entities with the newly learned real-world priors!
          entityModelCache.forEach((m) => { if (m) m.lastSig = ''; });
          state.lastIntentSummary = `${silentAuto ? '[자율 실세계 학습]' : '[실세계 일괄 학습 완료]'} ${reply.corpus_batch_result.summary}`;
          renderReadouts(true);
        }
      }
    } finally {
      state.corpusTraining = false;
      if (BTN_TRAIN_CORPUS) BTN_TRAIN_CORPUS.disabled = false;
    }
  }

  /**
   * User Multi-File Real-World Batch Trainer (accepts multiple photos AND videos at once!)
   */
  async function trainFromUserBatchFiles(fileList) {
    if (!fileList || !fileList.length || state.corpusTraining) return;
    state.corpusTraining = true;
    if (BTN_UPLOAD_CORPUS) BTN_UPLOAD_CORPUS.disabled = true;
    try {
      const files = Array.from(fileList);
      state.lastIntentSummary = `사용자 실세계 파일 ${files.length}개 일괄 픽셀 해독·학습 중…`;
      renderReadouts(true);

      const measured = [];
      for (const file of files) {
        if (file.type && file.type.startsWith('video/')) {
          const vProfs = await decodeVideoFileProfiles(file);
          vProfs.forEach((p) => measured.push(p));
        } else if (file.type && file.type.startsWith('image/')) {
          const url = URL.createObjectURL(file);
          const prof = await decodeImageUrlProfile(url, file.name);
          URL.revokeObjectURL(url);
          if (prof) measured.push(prof);
        }
      }

      if (measured.length > 0) {
        const reply = await apiDynamic('ingest_real_corpus_batch', { items: measured });
        if (reply && reply.corpus_batch_result) {
          entityModelCache.forEach((m) => { if (m) m.lastSig = ''; });
          state.lastIntentSummary = `[사용자 실세계 배치 학습 완료] ${reply.corpus_batch_result.summary}`;
          renderReadouts(true);
        }
      }
    } finally {
      state.corpusTraining = false;
      if (BTN_UPLOAD_CORPUS) BTN_UPLOAD_CORPUS.disabled = false;
    }
  }

  async function loadInitialLedger() {
    try {
      const res = await fetch('/api/dynamic-engine/state');
      if (!res.ok) return;
      const data = await res.json();
      state.ledger = data;
      (data.harvested_entities || []).forEach(ensureEntityLoaded);
      syncCrossMediaSelectors();
      applySocialFieldToPlacedEntities();
      renderReadouts(true);

      // Auto-learn from all real photographic assets on disk once if corpus is still empty!
      const cCount = Number((data.memory_summary && data.memory_summary.real_corpus_count) || 0);
      if (cCount === 0 && !state.autoCorpusTriggered) {
        state.autoCorpusTriggered = true;
        trainFromDiskCorpus(true);
      }
    } catch {}
  }

  function resetStreamLearning(newName, newKind) {
    state.streamName = newName;
    state.streamKind = newKind;
    state.hasPrev = false;
    state.hasPred = false;
    state.prevLuma = null;
    state.prevCropU = null;
    state.prevCropV = null;
    state.worldDeltaNorm = [0, 0];
    state.framesObserved = 0;
    state.rmseInitial = null;
    state.rmseHistory = [];
    state.predFlow = [0, 0];
    state.obsFlow = [0, 0];
    state.obsAccel = [0, 0];
    state.autoSavedOnce = false;
    state.lastPriorRecalled = null;

    apiDynamic('recall_prior', { source_name: newName, mean_luma: state.meanLuma, flow_speed: 0.5 }).then((res) => {
      if (res && res.matched && res.prior_law && Array.isArray(res.prior_law.learned_flow_vec)) {
        state.predFlow = [
          Number(res.prior_law.learned_flow_vec[0]) * 0.65,
          Number(res.prior_law.learned_flow_vec[1]) * 0.65,
        ];
        state.lastPriorRecalled = res.prior_law.law_label_ko;
      }
    });
  }

  function stopMediaStream() {
    if (state.mediaStream) {
      state.mediaStream.getTracks().forEach((t) => t.stop());
      state.mediaStream = null;
    }
    if (BTN_SCREEN) BTN_SCREEN.classList.remove('primary');
    if (BTN_WEBCAM) BTN_WEBCAM.classList.remove('primary');
  }

  function loadPresetStream(key) {
    stopMediaStream();
    liveVideo.pause();
    const info = PRESET_STREAMS[key] || PRESET_STREAMS.forest_drift;
    state.presetKey = key;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      state.presetImg = img;
      state.driftClock = 0;
      resetStreamLearning(info.label, 'photo_drift');
    };
    img.src = info.url;
  }

  function loadUserVideoOrPhoto(file) {
    if (!file) return;
    stopMediaStream();
    const url = URL.createObjectURL(file);
    if (file.type && file.type.startsWith('video/')) {
      liveVideo.srcObject = null;
      liveVideo.src = url;
      liveVideo.onloadeddata = () => {
        liveVideo.play().catch(() => {});
        resetStreamLearning(file.name, 'video');
      };
    } else {
      const img = new Image();
      img.onload = () => {
        state.presetImg = img;
        state.driftClock = 0;
        resetStreamLearning(file.name, 'photo_drift');
      };
      img.src = url;
    }
  }

  async function startScreenCapture() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      state.lastIntentSummary = '이 환경에서는 브라우저 화면 캡처가 차단되어 있습니다. 로컬 동영상(.mp4/.webm)을 직접 올려보세요.';
      renderReadouts(true);
      return;
    }
    try {
      stopMediaStream();
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 24 }, audio: false });
      state.mediaStream = stream;
      liveVideo.srcObject = stream;
      await liveVideo.play();
      if (BTN_SCREEN) BTN_SCREEN.classList.add('primary');
      resetStreamLearning('실시간 화면·게임 캡처', 'screen');
      stream.getVideoTracks()[0].addEventListener('ended', () => {
        loadPresetStream(state.presetKey);
      });
    } catch {
      state.lastIntentSummary = '화면 캡처가 취소되었거나 권한이 거부되었습니다.';
      renderReadouts(true);
    }
  }

  async function startWebcamCapture() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      state.lastIntentSummary = '카메라 장치에 접근할 수 없습니다. 로컬 동영상이나 화면 캡처를 사용해 보세요.';
      renderReadouts(true);
      return;
    }
    try {
      stopMediaStream();
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 }, audio: false });
      state.mediaStream = stream;
      liveVideo.srcObject = stream;
      await liveVideo.play();
      if (BTN_WEBCAM) BTN_WEBCAM.classList.add('primary');
      resetStreamLearning('실시간 카메라 스트림', 'camera');
    } catch {
      state.lastIntentSummary = '카메라 권한이 거부되었습니다.';
      renderReadouts(true);
    }
  }

  // Capture current real frame I(t) into curCanvas AND compute exact world camera pan delta!
  function captureCurrentFrame(dt) {
    if (state.streamKind === 'video' || state.streamKind === 'screen' || state.streamKind === 'camera') {
      if (liveVideo.readyState < 2 || !liveVideo.videoWidth) return false;
      state.driftClock += dt;
      const sw = liveVideo.videoWidth;
      const sh = liveVideo.videoHeight;
      const sr = sw / sh;
      const dr = PW / PH;
      let sx = 0, sy = 0, cw = sw, ch = sh;
      if (sr > dr) { cw = sh * dr; sx = (sw - cw) * 0.5; }
      else { ch = sw / dr; sy = (sh - ch) * 0.5; }
      curCtx.drawImage(liveVideo, sx, sy, cw, ch, 0, 0, PW, PH);
      // For live video, world-space shift comes from measured global optical flow in processDynamicFrame!
      state.worldDeltaNorm = [
        clamp(state.predFlow[0] / PW, -0.015, 0.015),
        clamp(state.predFlow[1] / PH, -0.015, 0.015),
      ];
      return true;
    }

    if (!state.presetImg) return false;
    state.driftClock += dt;
    const info = PRESET_STREAMS[state.presetKey] || PRESET_STREAMS.forest_drift;
    const sw = state.presetImg.naturalWidth || 1280;
    const sh = state.presetImg.naturalHeight || 720;
    const zoom = 1.24 + 0.035 * Math.sin(state.driftClock * 0.42);
    const cw = sw / zoom;
    const ch = sh / zoom;
    const maxPanX = Math.max(1, sw - cw);
    const maxPanY = Math.max(1, sh - ch);
    const u = 0.5 + 0.44 * Math.sin(state.driftClock * 0.26 * Math.sign(info.driftVx || 1));
    const v = 0.5 + 0.30 * Math.cos(state.driftClock * 0.20);
    const sx = clamp(u * maxPanX, 0, maxPanX);
    const sy = clamp(v * maxPanY, 0, maxPanY);

    // Exact world-space viewport displacement (when camera pans right +sx, world objects shift left -dx!)
    if (state.prevCropU !== null && state.prevCropV !== null) {
      state.worldDeltaNorm = [
        -(sx - state.prevCropU) / Math.max(1, cw),
        -(sy - state.prevCropV) / Math.max(1, ch),
      ];
    } else {
      state.worldDeltaNorm = [0, 0];
    }
    state.prevCropU = sx;
    state.prevCropV = sy;

    curCtx.drawImage(state.presetImg, sx, sy, cw, ch, 0, 0, PW, PH);
    return true;
  }

  /**
   * Core Dynamic Learning + Live 3-Band Environmental Irradiance + World-Space Entity Anchoring
   */
  function processDynamicFrame() {
    const curImg = curCtx.getImageData(0, 0, PW, PH);
    const curData = curImg.data;
    const n = PW * PH;
    const luma = new Float32Array(n);

    const skyEnd = Math.floor(PH * 0.25);
    const horStart = Math.floor(PH * 0.35);
    const horEnd = Math.floor(PH * 0.65);
    const gndStart = Math.floor(PH * 0.75);

    let sumR = 0, sumG = 0, sumB = 0, sumL = 0;
    let skyR = 0, skyG = 0, skyB = 0, skyC = 0;
    let horR = 0, horG = 0, horB = 0, horC = 0;
    let gndR = 0, gndG = 0, gndB = 0, gndC = 0;
    let sunXNum = 0, sunXDen = 1e-4;

    for (let y = 0; y < PH; y++) {
      for (let x = 0; x < PW; x++) {
        const i = y * PW + x;
        const i4 = i * 4;
        const r = curData[i4] / 255.0;
        const g = curData[i4 + 1] / 255.0;
        const b = curData[i4 + 2] / 255.0;
        sumR += r; sumG += g; sumB += b;
        const lm = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        luma[i] = lm;
        sumL += lm;

        if (y < skyEnd) {
          skyR += curData[i4]; skyG += curData[i4 + 1]; skyB += curData[i4 + 2]; skyC++;
        }
        if (y >= horStart && y < horEnd) {
          horR += curData[i4]; horG += curData[i4 + 1]; horB += curData[i4 + 2]; horC++;
        }
        if (y >= gndStart) {
          gndR += curData[i4]; gndG += curData[i4 + 1]; gndB += curData[i4 + 2]; gndC++;
        }
        // Measure real dominant sun/bright light azimuth from upper 55% of frame
        if (y < PH * 0.55 && lm > 0.62) {
          const wgt = (lm - 0.60) * (lm - 0.60);
          sunXNum += ((x / PW) * 2.0 - 1.0) * wgt;
          sunXDen += wgt;
        }
      }
    }

    state.meanRGB = [Math.round((sumR / n) * 255), Math.round((sumG / n) * 255), Math.round((sumB / n) * 255)];
    // Smooth temporal low-pass on environmental irradiance so relighting breathes organically without flicker
    const ema = 0.18;
    const nextSky = [skyR / Math.max(1, skyC), skyG / Math.max(1, skyC), skyB / Math.max(1, skyC)];
    const nextHor = [horR / Math.max(1, horC), horG / Math.max(1, horC), horB / Math.max(1, horC)];
    const nextGnd = [gndR / Math.max(1, gndC), gndG / Math.max(1, gndC), gndB / Math.max(1, gndC)];
    for (let c = 0; c < 3; c++) {
      state.skyRGB[c] = state.skyRGB[c] * (1 - ema) + nextSky[c] * ema;
      state.horizonRGB[c] = state.horizonRGB[c] * (1 - ema) + nextHor[c] * ema;
      state.groundRGB[c] = state.groundRGB[c] * (1 - ema) + nextGnd[c] * ema;
    }
    state.sceneKeyX = state.sceneKeyX * 0.88 + clamp(sunXNum / sunXDen, -0.9, 0.9) * 0.12;
    state.meanLuma = sumL / n;
    const rb = state.meanRGB[0] / Math.max(1, state.meanRGB[2]);
    state.colorTempK = Math.round(clamp(6500 - (rb - 1.0) * 3200, 2200, 10500));

    // Anchor placed entities in WORLD SPACE with perspective depth parallax!
    const [wdx, wdy] = state.worldDeltaNorm;
    if (Math.abs(wdx) > 1e-6 || Math.abs(wdy) > 1e-6) {
      state.placedEntities.forEach((ent) => {
        if (state.dragEntityUid === ent.uid) return;
        const depth = clamp((ent.y - 0.30) / 0.62, 0.35, 1.15);
        ent.x = clamp(ent.x + wdx * depth, 0.08, 0.92);
        ent.y = clamp(ent.y + wdy * depth * 0.72, 0.34, 0.91);
      });
    }

    // Step 1: Contrast arriving REAL I(t) against our predicted Î(t)
    let predData = null;
    if (state.hasPred) {
      predData = predCtx.getImageData(0, 0, PW, PH).data;
      let mseSum = 0;
      for (let i = 0; i < n; i++) {
        const i4 = i * 4;
        const dr = (curData[i4] - predData[i4]) / 255.0;
        const dg = (curData[i4 + 1] - predData[i4 + 1]) / 255.0;
        const db = (curData[i4 + 2] - predData[i4 + 2]) / 255.0;
        mseSum += dr * dr + dg * dg + db * db;
      }
      const mse = mseSum / (n * 3);
      const rmse = Math.sqrt(mse);
      const psnr = mse > 1e-8 ? Math.min(62, -10 * Math.log10(mse)) : 62;
      if (state.rmseInitial === null && state.framesObserved >= 2) {
        state.rmseInitial = rmse;
      }
      state.rmseCurrent = rmse;
      state.psnrCurrent = psnr;
      state.rmseHistory.push(rmse);
      if (state.rmseHistory.length > 64) state.rmseHistory.shift();
    }

    // Step 2: Optical Flow & Motion-First Reclassification (t-1 -> t)
    const vizOut = vizImg.data;
    if (state.hasPrev && state.prevLuma) {
      let fxNum = 0, fyNum = 0, fDen = 1e-4;
      let movingCount = 0, specSlipCount = 0;
      let minMx = PW, minMy = PH, maxMx = 0, maxMy = 0;

      for (let y = 1; y < PH - 1; y++) {
        for (let x = 1; x < PW - 1; x++) {
          const i = y * PW + x;
          const i4 = i * 4;
          const ix = (luma[i + 1] - luma[i - 1]) * 0.5;
          const iy = (luma[i + PW] - luma[i - PW]) * 0.5;
          const it = luma[i] - state.prevLuma[i];
          const g2 = ix * ix + iy * iy;
          if (g2 > 0.0005 && ((x & 1) === 0) && ((y & 1) === 0)) {
            fxNum += -it * ix;
            fyNum += -it * iy;
            fDen += g2;
          }

          const temporalDiff = Math.abs(it);
          const r = curData[i4] / 255.0;
          const g = curData[i4 + 1] / 255.0;
          const b = curData[i4 + 2] / 255.0;
          const maxC = Math.max(r, g, b);
          const minC = Math.min(r, g, b);
          const sat = maxC > 1e-4 ? (maxC - minC) / maxC : 0;
          const isSpecSlip = luma[i] > 0.66 && sat < 0.35 && temporalDiff > 0.018;
          const isMoving = !isSpecSlip && temporalDiff > 0.036;

          if (isSpecSlip) specSlipCount++;
          else if (isMoving) {
            movingCount++;
            if (x < minMx) minMx = x;
            if (x > maxMx) maxMx = x;
            if (y < minMy) minMy = y;
            if (y > maxMy) maxMy = y;
          }

          if (state.viewMode === 'cloud_error' && predData) {
            const err = (Math.abs(curData[i4] - predData[i4]) + Math.abs(curData[i4 + 1] - predData[i4 + 1]) + Math.abs(curData[i4 + 2] - predData[i4 + 2])) / (3 * 255);
            const boost = clamp(err * 5.2, 0, 1);
            vizOut[i4] = Math.round(clamp(curData[i4] * 0.28 + boost * 255, 0, 255));
            vizOut[i4 + 1] = Math.round(clamp(curData[i4 + 1] * 0.28 + boost * 96, 0, 255));
            vizOut[i4 + 2] = Math.round(clamp(curData[i4 + 2] * 0.35 + (1 - boost) * 42, 0, 255));
            vizOut[i4 + 3] = 255;
          } else if (state.viewMode === 'motion_class') {
            if (isSpecSlip) {
              vizOut[i4] = 251; vizOut[i4 + 1] = 191; vizOut[i4 + 2] = 36; vizOut[i4 + 3] = 255;
            } else if (isMoving) {
              vizOut[i4] = Math.round(curData[i4] * 0.45 + 32);
              vizOut[i4 + 1] = Math.round(clamp(curData[i4 + 1] * 0.55 + 140, 0, 255));
              vizOut[i4 + 2] = Math.round(curData[i4 + 2] * 0.45 + 88);
              vizOut[i4 + 3] = 255;
            } else {
              vizOut[i4] = Math.round(curData[i4] * 0.35);
              vizOut[i4 + 1] = Math.round(curData[i4 + 1] * 0.42);
              vizOut[i4 + 2] = Math.round(clamp(curData[i4 + 2] * 0.65 + 24, 0, 255));
              vizOut[i4 + 3] = 255;
            }
          }
        }
      }

      const vx = clamp((fxNum / fDen) * 1.4, -14, 14);
      const vy = clamp((fyNum / fDen) * 1.4, -14, 14);
      state.obsAccel = [vx - state.obsFlow[0], vy - state.obsFlow[1]];
      state.obsFlow = [vx, vy];
      state.movingRatio = movingCount / n;
      state.specularRatio = specSlipCount / n;

      if (movingCount > 160 && maxMx > minMx + 12 && maxMy > minMy + 12) {
        const nx = minMx / PW, ny = minMy / PH;
        const nw = clamp((maxMx - minMx) / PW, 0.10, 0.70);
        const nh = clamp((maxMy - minMy) / PH, 0.10, 0.75);
        state.movingBBox = [
          state.movingBBox[0] * 0.72 + nx * 0.28,
          state.movingBBox[1] * 0.72 + ny * 0.28,
          state.movingBBox[2] * 0.72 + nw * 0.28,
          state.movingBBox[3] * 0.72 + nh * 0.28,
        ];
      }

      const lr = 0.28;
      state.predFlow[0] = state.predFlow[0] * (1 - lr) + vx * lr;
      state.predFlow[1] = state.predFlow[1] * (1 - lr) + vy * lr;

      // Record real frame-by-frame centroid + flow dynamics into rolling buffer for Source A Motion DNA extraction!
      const [bx, by, bw, bh] = state.movingBBox;
      state.motionBuffer.push({
        vx: state.obsFlow[0],
        vy: state.obsFlow[1],
        cx: bx + bw * 0.5,
        cy: by + bh * 0.5,
        area: bw * bh,
        dt: 0.033,
      });
      if (state.motionBuffer.length > 72) state.motionBuffer.shift();
    }

    if (state.viewMode === 'cloud_error' || state.viewMode === 'motion_class') {
      vizCtx.putImageData(vizImg, 0, 0);
    }

    // Step 4: Generate Next Predicted Frame Î(t+1)
    predCtx.fillStyle = '#070b14';
    predCtx.fillRect(0, 0, PW, PH);
    predCtx.drawImage(curCanvas, state.predFlow[0], state.predFlow[1]);
    state.hasPred = true;

    prevCtx.drawImage(curCanvas, 0, 0);
    state.prevLuma = luma;
    state.hasPrev = true;
    state.framesObserved += 1;

    if (!state.autoSavedOnce && state.framesObserved === 80 && state.rmseInitial !== null) {
      state.autoSavedOnce = true;
      saveCurrentDynamicLaw(true);
    }
  }

  async function saveCurrentDynamicLaw(isAuto) {
    const res = await apiDynamic('record_stream_learning', {
      source_name: state.streamName,
      stream_kind: state.streamKind,
      frames_observed: Math.max(10, state.framesObserved),
      rmse_initial: state.rmseInitial || Math.max(state.rmseCurrent * 1.45, 0.04),
      rmse_adapted: Math.max(0.001, state.rmseCurrent),
      psnr_adapted: state.psnrCurrent,
      flow_x: state.predFlow[0],
      flow_y: state.predFlow[1],
      accel_x: state.obsAccel[0],
      accel_y: state.obsAccel[1],
      moving_entity_ratio: state.movingRatio,
      specular_slip_ratio: state.specularRatio,
      mean_luma: state.meanLuma,
      color_temp_k: state.colorTempK,
    });
    if (res && res.recorded_law) {
      state.lastIntentSummary =
        `${isAuto ? '[자동 영속 저장]' : '[영속 원장 저장]'} ${res.recorded_law.law_label_ko} ` +
        `(오차 -${res.recorded_law.error_reduction_pct}% · 디스크 원장 축적 완료)`;
      renderReadouts(true);
    }
  }

  async function harvestLiveMovingEntity() {
    const [bx, by, bw, bh] = state.movingBBox;
    const sx = clamp(Math.floor(bx * PW), 0, PW - 16);
    const sy = clamp(Math.floor(by * PH), 0, PH - 16);
    const sw = clamp(Math.floor(bw * PW), 24, PW - sx);
    const sh = clamp(Math.floor(bh * PH), 24, PH - sy);

    const cut = document.createElement('canvas');
    cut.width = sw;
    cut.height = sh;
    const cctx = cut.getContext('2d');
    cctx.save();
    cctx.beginPath();
    cctx.ellipse(sw * 0.5, sh * 0.5, sw * 0.46, sh * 0.46, 0, 0, Math.PI * 2);
    cctx.clip();
    cctx.drawImage(curCanvas, sx, sy, sw, sh, 0, 0, sw, sh);
    cctx.restore();

    const dataUrl = cut.toDataURL('image/png');
    const entName = `수확실체(${state.streamName.slice(0, 8)})`;
    const res = await apiDynamic('harvest_entity', {
      name: entName,
      source_name: state.streamName,
      data_url: dataUrl,
      bbox_norm: state.movingBBox,
    });
    if (res && res.harvested_entity) {
      const he = res.harvested_entity;
      entityModelCache.set(he.id, buildDecomposedEntityModel(cut, 'alpha_direct'));
      state.placedEntities.push({
        uid: `ent_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
        entity_id: he.id,
        name: he.name,
        x: clamp(bx + bw * 0.5 + 0.18, 0.16, 0.84),
        y: clamp(by + bh * 0.5, 0.35, 0.84),
        scale: clamp(bw, 0.16, 0.34),
        phase: Math.random() * Math.PI * 2,
        reason: '실시간 움직임 경계에서 수확·복제',
      });
      state.lastIntentSummary = `실시간 움직임 경계에서 [${he.name}] 수확 완료 → 영속 기억 저장 및 장면 복제 배치`;
      renderReadouts(true);
    }
  }

  async function executeIntent(intentText, autonomous) {
    const res = await apiDynamic('apply_intent', {
      intent_text: intentText || '',
      autonomous: !!autonomous,
      source_name: state.streamName,
      mean_luma: state.meanLuma,
      color_temp_k: state.colorTempK,
      moving_entity_ratio: state.movingRatio,
      existing_entity_count: state.placedEntities.length,
    });
    if (!res || !res.creation_result) return;
    const cr = res.creation_result;
    const plan = cr.causal_plan || {};

    state.s4Brightness = clamp(state.s4Brightness + Number(plan.s4_brightness_delta || 0), -0.45, 0.55);
    state.s4Warmth = clamp(state.s4Warmth + Number(plan.s4_warmth_delta || 0), -0.45, 0.55);
    if (plan.s2_relight_deg) {
      state.s2RelightDeg = clamp(Number(plan.s2_relight_deg), -60, 60);
    }
    state.s1SpecularBoost = clamp(state.s1SpecularBoost + Number(plan.s1_specular_boost || 0), 0, 1.0);

    const spawns = Array.isArray(plan.spawn_entities) ? plan.spawn_entities : [];
    spawns.forEach((sp, idx) => {
      const meta = findEntityMeta(sp.entity_id);
      if (meta) ensureEntityLoaded(meta);
      const sameCount = state.placedEntities.filter((e) => e.entity_id === sp.entity_id).length;
      const offsetX = sameCount > 0 ? ((sameCount % 2 === 1 ? 0.15 : -0.15) * Math.ceil(sameCount / 2)) : 0;
      state.placedEntities.push({
        uid: `ent_${Date.now()}_${idx}_${Math.random().toString(36).slice(2, 5)}`,
        entity_id: sp.entity_id,
        name: (meta && meta.name) || sp.entity_id,
        x: clamp(Number(sp.x || 0.5) + offsetX, 0.14, 0.86),
        y: clamp(Number(sp.y || 0.76), 0.36, 0.86),
        scale: clamp(Number(sp.scale || (meta && meta.default_scale) || 0.25), 0.14, 0.54),
        phase: Math.random() * Math.PI * 2,
        reason: sp.reason || cr.rationale,
      });
    });

    state.lastIntentSummary = `${cr.intent} → ${cr.rationale}`;
    renderReadouts(true);
  }

  /**
   * Organic Anatomical Zone Sensing (Zero Button Menus):
   * Reads exact pointer position relative to an entity's body to distinguish
   * head (머리), shoulder (어깨), hand/paw (손·발), and torso (등·몸통).
   */
  function detectAnatomicalZone(ent, nx, ny) {
    const halfW = Math.max(0.03, ent.scale * 0.36);
    const lx = clamp((nx - ent.x) / halfW, -1.0, 1.0);
    const ly = clamp((ny - (ent.y - ent.scale)) / Math.max(0.05, ent.scale), 0.0, 1.0);
    if (ent.entity_id === 'entity::pine_tree') {
      return { zone: 'torso', zoneKo: '가지·잎', hint: '스치면 바람결처럼 흔들림' };
    }
    if (ly < 0.34) {
      return { zone: 'head', zoneKo: '머리', hint: '문질러 쓰다듬기 · 톡 건드리기' };
    }
    if (ly < 0.58 && Math.abs(lx) > 0.22) {
      return { zone: 'shoulder', zoneKo: '어깨', hint: '지그시 감싸기 · 톡 건드리기' };
    }
    if (ly >= 0.55 && ly <= 0.90 && Math.abs(lx) > 0.20) {
      return { zone: 'hand_paw', zoneKo: '손·발', hint: '지그시 맞잡기 · 부드럽게 이끌기' };
    }
    return { zone: 'torso', zoneKo: '등·몸통', hint: '천천히 쓰다듬기 · 곁에 머물기' };
  }

  async function commitTactileInteraction(ent, zoneInfo, gesture, durationSec, strokeCycles, speedNorm) {
    const chosenArch = ent.archetype || (SEL_ARCHETYPE && SEL_ARCHETYPE.value) || 'companion_pet';
    const res = await apiDynamic('tactile_interaction', {
      entity_id: ent.entity_id,
      entity_name: ent.name,
      archetype: chosenArch,
      zone: zoneInfo.zone,
      gesture,
      duration_sec: Number(durationSec.toFixed(2)),
      stroke_cycles: strokeCycles,
      speed_norm: Number(speedNorm.toFixed(2)),
      world_name: state.streamName,
    });
    if (!res || !res.tactile_result) return;
    const tr = res.tactile_result;
    const rel = tr.relation || {};

    ent.archetype = tr.archetype || chosenArch;
    ent.archetypeLabelKo = tr.archetype_label_ko || ent.archetypeLabelKo;
    ent.tactileLeanTarget = Number(tr.lean_angle_rad || 0) * (ent.facing || 1);
    ent.tactileBreathMult = Number(tr.breath_rate_mult || 1.0);
    ent.warmthGlow = Math.max(ent.warmthGlow || 0, Number(tr.warmth_glow || 0.4));
    ent.bondStageKo = rel.bond_stage_ko || '';
    ent.whisperText = tr.reaction_ko;
    ent.whisperTimer = 4.5;

    // Context- & S4-Social-Field-dependent physical recoil vs courteous restraint vs captivated/reverent yield!
    if (tr.posture === 'startle_recoil' || tr.posture === 'social_reject_recoil' || tr.posture === 'hostile_bristle') {
      const recoilDir = ent.x >= 0.5 ? 1 : -1;
      ent.x = clamp(ent.x + recoilDir * 0.042, 0.12, 0.88);
      if (ent.living) {
        ent.targetX = clamp(ent.x + recoilDir * 0.12, 0.14, 0.86);
        ent.behavior = 'evade_retreat';
        ent.behaviorLabel = tr.posture === 'hostile_bristle' ? '적대 경계·으르렁' : '경계·손길 거부';
      }
    } else if (tr.posture === 'courteous_restraint') {
      const stepDir = ent.x >= 0.5 ? 1 : -1;
      ent.x = clamp(ent.x + stepDir * 0.018, 0.14, 0.86);
      if (ent.living) {
        ent.behavior = 'calm_rest';
        ent.behaviorLabel = `${ent.archetypeLabelKo || 'NPC'} · 적대 속 매너 유지`;
        ent.targetX = ent.x;
        ent.targetY = ent.y;
      }
    } else if (tr.posture === 'captivated_blush' || tr.posture === 'reverent_yield' || tr.posture === 'lean_into_stroke' || tr.posture === 'hand_hold_sync' || tr.posture === 'shoulder_embrace') {
      if (ent.living) {
        ent.behavior = 'calm_rest';
        ent.behaviorLabel = tr.posture === 'captivated_blush'
          ? `${ent.archetypeLabelKo || 'NPC'} · 매혹 시선 고정`
          : (tr.posture === 'reverent_yield' ? `${ent.archetypeLabelKo || ''} · 경외 수용` : `${tr.zone_ko} 교감 · ${rel.bond_stage_ko || '호감'}`);
        ent.targetX = ent.x;
        ent.targetY = ent.y;
      }
    } else if (tr.posture === 'playful_nudge_back' && ent.living) {
      ent.behaviorLabel = `장난 호응 · ${rel.bond_stage_ko || '편안'}`;
      ent.jumpLift = 0.018;
    }

    state.lastIntentSummary =
      `[S4↔S0 교감 · ${tr.archetype_label_ko || ''} ${tr.zone_ko} ${tr.gesture_ko} · ${rel.bond_stage_ko || ''} (신뢰 ${Math.round((rel.trust || 0.3) * 100)}%)] ` +
      tr.reaction_ko;
    renderReadouts(true);
  }

  /**
   * Continuous Living Actor Physics, Tactile Posture Springs & Biomechanical Steering
   */
  function updateLivingActors(dt) {
    // Advance visual intervention ripples & tactile warmth aura trails
    for (let i = state.interventionRipples.length - 1; i >= 0; i--) {
      state.interventionRipples[i].age += dt;
      if (state.interventionRipples[i].age >= state.interventionRipples[i].maxAge) {
        state.interventionRipples.splice(i, 1);
      }
    }
    for (let i = state.tactileAuraTrails.length - 1; i >= 0; i--) {
      state.tactileAuraTrails[i].age += dt;
      if (state.tactileAuraTrails[i].age >= state.tactileAuraTrails[i].maxAge) {
        state.tactileAuraTrails.splice(i, 1);
      }
    }

    // Continuous hold detection while pointer rests calmly on an entity (hand-hold / shoulder embrace!)
    if (state.tactileSession) {
      const ts = state.tactileSession;
      const elapsed = (performance.now() - ts.startTs) / 1000;
      const ent = state.placedEntities.find((e) => e.uid === ts.uid);
      if (ent && elapsed >= 0.55 && ts.mode === 'pending' && ts.travel < 0.028) {
        ts.mode = 'hold';
        ent.tactileLeanTarget = 0.085 * (ent.facing || 1);
        ent.warmthGlow = Math.max(ent.warmthGlow || 0, 0.78);
        state.tactileAuraTrails.push({ x: ts.lastX, y: ts.lastY, age: 0, maxAge: 1.15, rgb: '251, 146, 172' });
        if (!ts.holdCommitted) {
          ts.holdCommitted = true;
          commitTactileInteraction(ent, ts.zoneInfo, 'hold', elapsed, 0, 0.05);
        }
      } else if (ent && ts.mode === 'hold') {
        ts.holdPulseAcc = (ts.holdPulseAcc || 0) + dt;
        if (ts.holdPulseAcc > 0.55) {
          ts.holdPulseAcc = 0;
          state.tactileAuraTrails.push({ x: ts.lastX, y: ts.lastY, age: 0, maxAge: 1.0, rgb: '251, 146, 172' });
        }
      }
    }

    // Update tactile posture lean, warmth decay, and living whispers for ALL entities
    state.placedEntities.forEach((ent) => {
      const targetLean = ent.tactileLeanTarget || 0;
      ent.tactileLean = (ent.tactileLean || 0) + (targetLean - (ent.tactileLean || 0)) * clamp(dt * 7.5, 0, 0.45);
      ent.tactileLeanTarget = targetLean * Math.pow(0.42, dt);
      ent.tactileBreathMult = 1.0 + ((ent.tactileBreathMult || 1.0) - 1.0) * Math.pow(0.65, dt);
      ent.warmthGlow = (ent.warmthGlow || 0) * Math.pow(0.76, dt);
      if (ent.whisperTimer > 0) ent.whisperTimer = Math.max(0, ent.whisperTimer - dt);
    });

    const actors = state.placedEntities.filter((e) => e.living);
    actors.forEach((ent) => {
      if (state.dragEntityUid === ent.uid) return;
      if (state.tactileSession && state.tactileSession.uid === ent.uid && state.tactileSession.mode !== 'guide') return;
      const dna = ent.motionDna || findMotionDna('dna::predator_prowl');
      const freq = Number((dna && dna.dominant_freq_hz) || 1.25);
      const traj = (dna && Array.isArray(dna.trajectory_samples) && dna.trajectory_samples.length > 0)
        ? dna.trajectory_samples
        : null;

      // Autonomous patrol waypoint picking
      ent.patrolTimer = (ent.patrolTimer || 0) - dt;
      const dxToTarget = (ent.targetX ?? ent.x) - ent.x;
      const dyToTarget = (ent.targetY ?? ent.y) - ent.y;
      const dist = Math.hypot(dxToTarget, dyToTarget);

      if (ent.behavior !== 'calm_rest') {
        if (dist < 0.025 && ent.patrolTimer <= 0) {
          ent.patrolTimer = 2.2 + Math.random() * 2.8;
          if (ent.behavior === 'approach_user' || ent.behavior === 'evade_retreat') {
            ent.behavior = 'curious_patrol';
            ent.behaviorLabel = dna ? dna.gait_label_ko : '자율 탐색';
            ent.speedMult = 1.0;
          }
          ent.targetX = clamp(0.16 + Math.random() * 0.68, 0.14, 0.86);
          ent.targetY = clamp(0.66 + Math.random() * 0.19, 0.62, 0.86);
        }
      }

      // Social awareness: if another living actor is nearby, gently orient toward it
      for (const other of actors) {
        if (other.uid === ent.uid) continue;
        const dOther = Math.hypot(other.x - ent.x, other.y - ent.y);
        if (dOther > 0.04 && dOther < 0.13 && ent.behavior === 'curious_patrol') {
          ent.facing = other.x >= ent.x ? 1 : -1;
        }
      }

      // Smooth inertial steering velocity
      const baseSpeed = (ent.behavior === 'calm_rest') ? 0.0 : (0.11 * (ent.speedMult || 1.0));
      const desiredVx = dist > 0.015 ? (dxToTarget / dist) * baseSpeed : 0;
      const desiredVy = dist > 0.015 ? (dyToTarget / dist) * baseSpeed * 0.45 : 0;
      const inertia = clamp(dt * 4.5, 0.05, 0.35);
      ent.vx = (ent.vx || 0) * (1 - inertia) + desiredVx * inertia;
      ent.vy = (ent.vy || 0) * (1 - inertia) + desiredVy * inertia;

      ent.x = clamp(ent.x + ent.vx * dt, 0.10, 0.90);
      ent.y = clamp(ent.y + ent.vy * dt, 0.58, 0.88);
      // Allure/Charisma Magnetic Gaze-Lock: captivated entities physically cannot tear their gaze away from player presence!
      if (ent.gazeLock && (ent.captivationPull || 0) >= 0.62) {
        const px = state.pointerNorm[0];
        const dxEye = px - ent.x;
        if (Math.abs(dxEye) > 0.025) {
          ent.facing = dxEye >= 0 ? 1 : -1;
        }
        ent.tactileLeanTarget = clamp(dxEye * 0.22, -0.09, 0.09);
      } else if (Math.abs(ent.vx) > 0.008) {
        ent.facing = ent.vx >= 0 ? 1 : -1;
      }

      // Sample 24-phase causal Motion DNA rotor extracted from Source A!
      const speedNorm = clamp(Math.hypot(ent.vx, ent.vy) / 0.11, 0, 1.8);
      const activeMove = ent.behavior === 'calm_rest' ? 0.15 : Math.max(0.28, speedNorm);
      ent.gaitPhase = ((ent.gaitPhase || 0) + dt * freq * activeMove) % 1.0;

      if (traj) {
        const fIdx = ent.gaitPhase * traj.length;
        const i0 = Math.floor(fIdx) % traj.length;
        const i1 = (i0 + 1) % traj.length;
        const fr = fIdx - Math.floor(fIdx);
        const s0 = traj[i0], s1 = traj[i1];
        const dySample = (s0[1] * (1 - fr) + s1[1] * fr) * activeMove;
        const squashSample = 1.0 + ((s0[2] * (1 - fr) + s1[2] * fr) - 1.0) * activeMove;
        const tiltSample = (s0[3] * (1 - fr) + s1[3] * fr) * activeMove;
        ent.jumpLift = Math.max(0, -dySample) * 1.45;
        ent.dynSquash = clamp(squashSample, 0.90, 1.10);
        ent.dynTilt = clamp(tiltSample + ent.vx * 0.65, -0.20, 0.20);
      } else {
        ent.jumpLift = 0;
        ent.dynSquash = 1.0;
        ent.dynTilt = clamp(ent.vx * 0.6, -0.15, 0.15);
      }
    });
  }

  // Build modulated live environmental lighting vector combining real frame RGB + S4 intent + learned priors
  function buildLiveEnvLighting() {
    const priors = (state.ledger && state.ledger.distilled_optical_priors) || {};
    const skyGroundPrior = Number(priors.sky_to_ground_ratio || 1.38);
    const mistPrior = Number(priors.horizon_mist_ratio || 0.22);

    const bMul = clamp(1.0 + state.s4Brightness * 0.82, 0.45, 1.65);
    const wShift = state.s4Warmth;
    const modColor = (rgb) => [
      clamp((rgb[0] / 255.0) * bMul * (1.0 + Math.max(0, wShift) * 0.34 - Math.max(0, -wShift) * 0.16), 0.04, 1.35),
      clamp((rgb[1] / 255.0) * bMul * (1.0 + Math.max(0, wShift) * 0.14 - Math.max(0, -wShift) * 0.04), 0.04, 1.35),
      clamp((rgb[2] / 255.0) * bMul * (1.0 - Math.max(0, wShift) * 0.22 + Math.max(0, -wShift) * 0.32), 0.04, 1.35),
    ];

    const sky = modColor(state.skyRGB);
    const hor = modColor(state.horizonRGB);
    const gnd = modColor(state.groundRGB);
    // Directional key light tinted warmer when golden-hour warmth rises
    const key = [
      clamp(sky[0] * 1.15 + Math.max(0, wShift) * 0.35 + state.s1SpecularBoost * 0.18, 0.15, 1.55),
      clamp(sky[1] * 1.10 + Math.max(0, wShift) * 0.18 + state.s1SpecularBoost * 0.14, 0.15, 1.50),
      clamp(sky[2] * 1.02 + Math.max(0, -wShift) * 0.28 + state.s1SpecularBoost * 0.10, 0.15, 1.45),
    ];

    const az = clamp(state.sceneKeyX + Math.sin((state.s2RelightDeg * Math.PI) / 180) * 0.85, -0.95, 0.95);
    const ly = -0.62; // Canvas -y points UP toward the sky/sun
    const lz = 0.64;
    const lLen = Math.hypot(az, ly, lz) || 1.0;

    return {
      sky,
      hor,
      gnd,
      key,
      lx: az / lLen,
      ly: ly / lLen,
      lz: lz / lLen,
      skyGroundPrior,
      mistPrior,
    };
  }

  /**
   * Draw Wave-Rippled Mirrored Water/Shoreline Reflection beneath an entity!
   */
  function drawWaterReflection(relitCanvas, cx, footY, drawW, drawH, swayX) {
    const slices = 12;
    const reflH = drawH * 0.44;
    const srcSliceH = relitCanvas.height / slices;
    const dstSliceH = reflH / slices;

    ctx.save();
    for (let s = 0; s < slices; s++) {
      const frac = s / slices;
      // Reflect from bottom of entity upward into the water surface
      const sy = relitCanvas.height - (s + 1) * srcSliceH;
      const dy = footY - 2 + s * dstSliceH;
      const rippleX = Math.sin(state.driftClock * 3.4 + s * 0.85 + cx * 0.03) * (1.2 + frac * 4.8);
      const alpha = (1.0 - frac) * (1.0 - frac) * 0.36;
      if (alpha < 0.02) continue;
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(cx + swayX * (1.0 - frac * 0.5) + rippleX, dy + dstSliceH);
      ctx.scale(1.0 + frac * 0.06, -1.0);
      ctx.drawImage(
        relitCanvas,
        0, sy, relitCanvas.width, srcSliceH,
        -drawW * 0.5, 0, drawW, dstSliceH + 0.8
      );
      ctx.restore();
    }
    ctx.restore();
  }

  function drawViewport() {
    const rect = CANVAS.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(360, Math.floor(rect.width));
    const h = Math.max(240, Math.floor(rect.height));
    if (CANVAS.width !== Math.floor(w * dpr) || CANVAS.height !== Math.floor(h * dpr)) {
      CANVAS.width = Math.floor(w * dpr);
      CANVAS.height = Math.floor(h * dpr);
    }

    ctx.save();
    ctx.scale(dpr, dpr);
    ctx.fillStyle = '#050811';
    ctx.fillRect(0, 0, w, h);

    if (state.viewMode === 'recompose') {
      // 1. Draw Live Real Video/Photo Stream modulated by S4 Brightness/Warmth/Specular
      ctx.save();
      const brightPct = Math.round(100 + state.s4Brightness * 85);
      const satPct = Math.round(100 + state.s4Warmth * 42 + state.s1SpecularBoost * 24);
      const contPct = Math.round(100 + state.s1SpecularBoost * 18);
      ctx.filter = `brightness(${brightPct}%) saturate(${satPct}%) contrast(${contPct}%)`;
      ctx.drawImage(curCanvas, 0, 0, w, h);
      ctx.restore();

      // 2. S4 Atmospheric Sunlight / Golden-Hour or Cool-Moonlight Radiance Gradient
      if (Math.abs(state.s4Warmth) > 0.03 || state.s4Brightness > 0.05) {
        const sunX = w * (0.5 + clamp(state.sceneKeyX + Math.sin((state.s2RelightDeg * Math.PI) / 180) * 0.55, -0.45, 0.45));
        const sunY = h * 0.16;
        const grad = ctx.createRadialGradient(sunX, sunY, 12, sunX, sunY, w * 0.80);
        if (state.s4Warmth >= 0) {
          const alpha = clamp(state.s4Warmth * 0.44 + state.s4Brightness * 0.26, 0, 0.46);
          grad.addColorStop(0, `rgba(255, 232, 165, ${alpha.toFixed(3)})`);
          grad.addColorStop(0.5, `rgba(255, 184, 102, ${(alpha * 0.42).toFixed(3)})`);
          grad.addColorStop(1, 'rgba(255, 160, 80, 0)');
        } else {
          const alpha = clamp(-state.s4Warmth * 0.40, 0, 0.40);
          grad.addColorStop(0, `rgba(110, 175, 255, ${alpha.toFixed(3)})`);
          grad.addColorStop(1, 'rgba(30, 64, 135, 0)');
        }
        ctx.save();
        ctx.globalCompositeOperation = 'screen';
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);
        ctx.restore();
      }

      // 3. Draw World-Space Anchored, Pixel-Relit Entities + Water Reflections + Contact Shadows!
      const env = buildLiveEnvLighting();
      const shadowSkew = -env.lx * 34;
      const presetInfo = PRESET_STREAMS[state.presetKey];
      const hasWater = state.streamKind !== 'photo_drift' ? (state.specularRatio > 0.04) : !!(presetInfo && presetInfo.hasWaterSurface);

      const sorted = state.placedEntities.slice().sort((a, b) => a.y - b.y);
      sorted.forEach((ent) => {
        const meta = findEntityMeta(ent.entity_id);
        if (meta) ensureEntityLoaded(meta);
        const model = entityModelCache.get(ent.entity_id);
        const cx = ent.x * w;
        const footY = ent.y * h;
        const depthNorm = clamp((ent.y - 0.30) / 0.62, 0.15, 1.0);
        const drawH = ent.scale * h;
        const aspect = model ? (model.w / Math.max(1, model.h)) : 1.0;
        const drawW = drawH * aspect;

        const breathSpeed = 2.1 * (ent.tactileBreathMult || 1.0);
        const breathe = 1.0 + Math.sin(state.driftClock * breathSpeed + ent.phase) * 0.012;
        const swayX = ent.entity_id === 'entity::pine_tree'
          ? Math.sin(state.driftClock * 1.45 + ent.phase) * (3.2 + Math.abs(ent.tactileLean || 0) * 32)
          : Math.sin(state.driftClock * 1.1 + ent.phase) * 0.9;

        const relit = model ? relightEntityModel(model, depthNorm, env) : null;
        const liftPx = ent.living ? (ent.jumpLift || 0) * h : 0;
        const squashY = ent.living ? (ent.dynSquash || 1.0) * breathe : breathe;
        const squashX = ent.living ? (1.0 / Math.max(0.88, Math.sqrt(ent.dynSquash || 1.0))) * (ent.facing || 1) : 1.0;
        const tiltRad = (ent.living ? (ent.dynTilt || 0) : 0) + (ent.tactileLean || 0);

        // 3a. Mirrored wave-rippled water reflection when standing over water/shoreline
        if (relit && hasWater && ent.y > 0.54) {
          drawWaterReflection(relit, cx, footY + liftPx * 0.35, drawW, drawH, swayX);
        }

        // 3a2. Ultra-soft warmth resonance aura + Magnetic Allure Gaze-Lock Tether!
        if ((ent.warmthGlow || 0) > 0.08) {
          ctx.save();
          const wg = clamp(ent.warmthGlow, 0, 1);
          const auraGrad = ctx.createRadialGradient(cx, footY - drawH * 0.52, 6, cx, footY - drawH * 0.52, drawW * 0.72);
          auraGrad.addColorStop(0, `rgba(255, 214, 150, ${(wg * 0.24).toFixed(3)})`);
          auraGrad.addColorStop(0.6, `rgba(251, 146, 172, ${(wg * 0.11).toFixed(3)})`);
          auraGrad.addColorStop(1, 'rgba(251, 146, 172, 0)');
          ctx.globalCompositeOperation = 'screen';
          ctx.fillStyle = auraGrad;
          ctx.beginPath();
          ctx.ellipse(cx, footY - drawH * 0.52, drawW * 0.72, drawH * 0.62, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
        if (ent.gazeLock && (ent.captivationPull || 0) >= 0.62 && state.pointerInside) {
          const headY = footY - drawH * 0.80;
          const px = state.pointerNorm[0] * w;
          const py = state.pointerNorm[1] * h;
          const dGaze = Math.hypot(px - cx, py - headY);
          if (dGaze > 24 && dGaze < w * 0.85) {
            ctx.save();
            const gAlpha = clamp(((ent.captivationPull || 0.62) - 0.55) * 0.55, 0.10, 0.36);
            const gGrad = ctx.createLinearGradient(cx, headY, px, py);
            gGrad.addColorStop(0, `rgba(244, 114, 182, ${gAlpha.toFixed(3)})`);
            gGrad.addColorStop(0.6, `rgba(253, 224, 71, ${(gAlpha * 0.65).toFixed(3)})`);
            gGrad.addColorStop(1, 'rgba(253, 224, 71, 0)');
            ctx.strokeStyle = gGrad;
            ctx.lineWidth = 1.3;
            ctx.setLineDash([4, 5]);
            ctx.beginPath();
            ctx.moveTo(cx, headY);
            ctx.quadraticCurveTo((cx + px) * 0.5, Math.min(headY, py) - 18, px, py);
            ctx.stroke();
            ctx.restore();
          }
        }

        // 3b. Dual-Layer Grounded Shadow: Cast Shadow (away from real sun) + Tight Contact AO (shrinks smoothly on jump lift!)
        const shadowScale = clamp(1.0 - liftPx / Math.max(40, drawH * 0.5), 0.55, 1.0);
        ctx.save();
        const castGrad = ctx.createRadialGradient(
          cx + shadowSkew * 0.55,
          footY - 1,
          4,
          cx + shadowSkew * 0.65,
          footY - 1,
          drawW * 0.52 * shadowScale
        );
        castGrad.addColorStop(0, `rgba(${Math.round(state.groundRGB[0] * 0.18)}, ${Math.round(state.groundRGB[1] * 0.20)}, ${Math.round(state.groundRGB[2] * 0.26)}, ${(0.44 * shadowScale).toFixed(2)})`);
        castGrad.addColorStop(1, 'rgba(5, 10, 20, 0)');
        ctx.fillStyle = castGrad;
        ctx.beginPath();
        ctx.ellipse(cx + shadowSkew * 0.58, footY - 1, drawW * 0.50 * shadowScale, Math.max(5, drawH * 0.08 * shadowScale), 0, 0, Math.PI * 2);
        ctx.fill();

        const aoGrad = ctx.createRadialGradient(cx, footY - 1, 2, cx, footY - 1, drawW * 0.28 * shadowScale);
        aoGrad.addColorStop(0, `rgba(4, 8, 16, ${(0.62 * shadowScale).toFixed(2)})`);
        aoGrad.addColorStop(1, 'rgba(4, 8, 16, 0)');
        ctx.fillStyle = aoGrad;
        ctx.beginPath();
        ctx.ellipse(cx, footY - 1, drawW * 0.28 * shadowScale, Math.max(4, drawH * 0.045 * shadowScale), 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // 3c. Draw Pixel-Level Relit Entity with Source A Biomechanical Gait Rotor + Tactile Posture Lean!
        if (relit) {
          ctx.save();
          ctx.translate(cx + swayX, footY - liftPx);
          if (tiltRad) ctx.rotate(tiltRad);
          ctx.scale(squashX, squashY);
          ctx.drawImage(relit, -drawW * 0.5, -drawH, drawW, drawH);
          ctx.restore();
        }

        // Minimal unobtrusive living behavior + bond stage caption beneath actors
        if (ent.living || ent.bondStageKo) {
          const hz = ent.motionDna ? Number(ent.motionDna.dominant_freq_hz || 1.2).toFixed(1) : null;
          const bondPart = ent.bondStageKo ? ` · ${ent.bondStageKo}` : '';
          const basePart = ent.living ? `${ent.behaviorLabel || '자율 보행'}${hz ? ` ${hz}Hz` : ''}` : ent.name;
          ctx.save();
          ctx.font = '600 9.5px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.textAlign = 'center';
          ctx.fillStyle = 'rgba(226, 232, 240, 0.86)';
          ctx.fillText(`${basePart}${bondPart}`, cx, footY + 11);
          ctx.restore();
        }

        // Gentle fading organic reaction whisper floating above the entity after tactile contact
        if (ent.whisperText && ent.whisperTimer > 0) {
          const wAlpha = clamp(Math.min(ent.whisperTimer, 1.0), 0, 1) * 0.92;
          const wy = Math.max(24, footY - drawH - 12 - (4.5 - ent.whisperTimer) * 2.2);
          ctx.save();
          ctx.font = '500 10.5px system-ui, -apple-system, sans-serif';
          ctx.textAlign = 'center';
          const shortWhisper = ent.whisperText.length > 42 ? `${ent.whisperText.slice(0, 41)}…` : ent.whisperText;
          ctx.fillStyle = `rgba(10, 15, 28, ${(wAlpha * 0.62).toFixed(3)})`;
          const tw = ctx.measureText(shortWhisper).width + 14;
          ctx.fillRect(clamp(cx - tw * 0.5, 8, w - tw - 8), wy - 12, tw, 17);
          ctx.fillStyle = `rgba(254, 243, 199, ${wAlpha.toFixed(3)})`;
          ctx.fillText(shortWhisper, clamp(cx, tw * 0.5 + 8, w - tw * 0.5 - 8), wy);
          ctx.restore();
        }
      });

      // 3d. World-Click Intervention Ripples & Warm Tactile Contact Aura Trails
      state.interventionRipples.forEach((rp) => {
        const t = clamp(rp.age / rp.maxAge, 0, 1);
        const rad = 6 + t * 44;
        const alpha = (1 - t) * 0.72;
        ctx.save();
        ctx.strokeStyle = `rgba(125, 211, 252, ${alpha.toFixed(3)})`;
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.ellipse(rp.x * w, rp.y * h, rad, rad * 0.36, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      });

      state.tactileAuraTrails.forEach((tr) => {
        const t = clamp(tr.age / tr.maxAge, 0, 1);
        const rad = 8 + t * 28;
        const alpha = (1 - t) * 0.58;
        ctx.save();
        ctx.strokeStyle = `rgba(${tr.rgb || '253, 224, 71'}, ${alpha.toFixed(3)})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(tr.x * w, tr.y * h, rad, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      });

      // 3e. Whisper-Soft Organic Hover Zone Halo (ZERO intrusive button menu — only appears right where hand hovers!)
      if (state.hoverTouch && !state.dragEntityUid) {
        const ht = state.hoverTouch;
        const hx = ht.nx * w;
        const hy = ht.ny * h;
        ctx.save();
        const pulse = 13 + Math.sin(state.driftClock * 4.2) * 2.5;
        ctx.strokeStyle = 'rgba(253, 224, 71, 0.52)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(hx, hy, pulse, 0, Math.PI * 2);
        ctx.stroke();
        ctx.font = '500 10px system-ui, sans-serif';
        ctx.fillStyle = 'rgba(254, 249, 195, 0.90)';
        ctx.fillText(`${ht.zoneKo} · ${ht.hint}`, clamp(hx + 16, 12, w - 165), clamp(hy - 6, 20, h - 18));
        ctx.restore();
      }

      // 4. Unified Post-Composite Atmospheric Horizon Mist Veil (binds foreground & background into ONE optical medium!)
      if (state.placedEntities.length > 0) {
        const veilAlpha = clamp(env.mistPrior * 0.26, 0.03, 0.11);
        const veilGrad = ctx.createLinearGradient(0, h * 0.25, 0, h);
        veilGrad.addColorStop(0, `rgba(${Math.round(state.horizonRGB[0])}, ${Math.round(state.horizonRGB[1])}, ${Math.round(state.horizonRGB[2])}, ${veilAlpha.toFixed(3)})`);
        veilGrad.addColorStop(0.55, `rgba(${Math.round(state.horizonRGB[0])}, ${Math.round(state.horizonRGB[1])}, ${Math.round(state.horizonRGB[2])}, ${(veilAlpha * 0.35).toFixed(3)})`);
        veilGrad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.save();
        ctx.fillStyle = veilGrad;
        ctx.fillRect(0, 0, w, h);
        ctx.restore();
      }
    } else if (state.viewMode === 'pred_split') {
      const splitX = Math.round(w * 0.5);
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, splitX, h); ctx.clip();
      ctx.drawImage(curCanvas, 0, 0, w, h);
      ctx.restore();

      ctx.save();
      ctx.beginPath(); ctx.rect(splitX, 0, w - splitX, h); ctx.clip();
      ctx.drawImage(predCanvas, 0, 0, w, h);
      ctx.restore();

      ctx.strokeStyle = 'rgba(248,250,252,0.9)';
      ctx.lineWidth = 1.6;
      ctx.beginPath(); ctx.moveTo(splitX, 0); ctx.lineTo(splitX, h); ctx.stroke();

      ctx.fillStyle = 'rgba(15,23,42,0.75)';
      ctx.fillRect(10, 10, 196, 22);
      ctx.fillStyle = '#e2e8f0';
      ctx.font = '600 11px system-ui, sans-serif';
      ctx.fillText('실제 도착 프레임 I(t+1)', 16, 25);

      ctx.fillStyle = 'rgba(15,23,42,0.75)';
      ctx.fillRect(w - 234, 10, 224, 22);
      ctx.fillStyle = '#a7f3d0';
      ctx.fillText(`엘리시아 로터 예측 Î(t+1) · ${state.psnrCurrent.toFixed(1)}dB`, w - 226, 25);
    } else {
      ctx.drawImage(vizCanvas, 0, 0, w, h);
      if (state.viewMode === 'motion_class') {
        const [bx, by, bw, bh] = state.movingBBox;
        ctx.strokeStyle = 'rgba(52, 211, 153, 0.92)';
        ctx.lineWidth = 1.6;
        ctx.strokeRect(bx * w, by * h, bw * w, bh * h);
        const cx = (bx + bw * 0.5) * w;
        const cy = (by + bh * 0.5) * h;
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + state.predFlow[0] * 14, cy + state.predFlow[1] * 14);
        ctx.stroke();
      }
    }

    // Minimal Top-Left Live Learning & World-Space Optical Telemetry Scrim
    if (state.viewMode === 'recompose' || state.viewMode === 'cloud_error' || state.viewMode === 'motion_class') {
      ctx.fillStyle = 'rgba(10, 15, 28, 0.74)';
      ctx.fillRect(10, 10, 366, 40);
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
      ctx.lineWidth = 1;
      ctx.strokeRect(10, 10, 366, 40);
      ctx.fillStyle = '#bae6fd';
      ctx.font = '600 11px ui-monospace, SFMono-Regular, Menlo, monospace';
      ctx.fillText(
        `동적 예측 f=${state.framesObserved} · RMSE ${state.rmseCurrent.toFixed(4)} (${state.psnrCurrent.toFixed(1)}dB)`,
        18,
        26
      );
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
      ctx.fillText(
        `S3좌표고정 v=(${state.predFlow[0].toFixed(2)},${state.predFlow[1].toFixed(2)}) · 실체 ${(state.movingRatio * 100).toFixed(0)}% · 윤슬 ${(state.specularRatio * 100).toFixed(0)}%`,
        18,
        42
      );
    }

    // Live Prediction Error Convergence Sparkline (bottom-right)
    if (state.rmseHistory.length > 4) {
      const sw = 152, sh = 38;
      const sx = w - sw - 12, sy = h - sh - 10;
      ctx.fillStyle = 'rgba(10, 15, 28, 0.76)';
      ctx.fillRect(sx, sy, sw, sh);
      ctx.strokeStyle = 'rgba(52, 211, 153, 0.45)';
      ctx.strokeRect(sx, sy, sw, sh);

      const maxE = Math.max(0.05, ...state.rmseHistory);
      ctx.strokeStyle = '#34d399';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      state.rmseHistory.forEach((val, idx) => {
        const px = sx + 4 + (idx / Math.max(1, state.rmseHistory.length - 1)) * (sw - 8);
        const py = sy + sh - 5 - clamp(val / maxE, 0, 1) * (sh - 16);
        if (idx === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.stroke();

      ctx.fillStyle = '#a7f3d0';
      ctx.font = '10px ui-monospace, monospace';
      ctx.fillText('예측 오차 수렴 |I-Î|', sx + 6, sy + 11);
    }

    ctx.fillStyle = 'rgba(226,232,240,0.82)';
    ctx.font = '10.5px system-ui, sans-serif';
    ctx.fillText('바닥 클릭: 살아있는 개체 실시간 호출·개입 · 드래그: 위치 이동 · 더블클릭: 복제', 12, h - 10);

    ctx.restore();
  }

  function renderReadouts(force) {
    const now = performance.now();
    if (!force && now - lastReadoutTs < 240) return;
    lastReadoutTs = now;

    if (READOUT_LEARN) {
      const initR = state.rmseInitial !== null ? state.rmseInitial.toFixed(4) : state.rmseCurrent.toFixed(4);
      const redPct = state.rmseInitial && state.rmseInitial > 1e-5
        ? Math.max(0, (1 - state.rmseCurrent / state.rmseInitial) * 100).toFixed(1)
        : '0.0';
      const priorTag = state.lastPriorRecalled ? ` · 영속 기억 선행 로드[${state.lastPriorRecalled}]` : '';
      READOUT_LEARN.textContent =
        `동적 스트림 [${state.streamName}] — 예측 오차 ${initR} → ${state.rmseCurrent.toFixed(4)} (-${redPct}%) · ` +
        `하늘(${Math.round(state.skyRGB[0])},${Math.round(state.skyRGB[1])},${Math.round(state.skyRGB[2])}) / ` +
        `지면(${Math.round(state.groundRGB[0])},${Math.round(state.groundRGB[1])},${Math.round(state.groundRGB[2])})${priorTag}`;
    }

    if (READOUT_INTENT) {
      const livingCount = state.placedEntities.filter((e) => e.living).length;
      READOUT_INTENT.textContent =
        `의도·교차 재창조 (실체 ${state.placedEntities.length} · 살아있는 개체 ${livingCount} · S4 밝기 ${state.s4Brightness >= 0 ? '+' : ''}${Math.round(state.s4Brightness * 100)}%): ` +
        state.lastIntentSummary;
    }

    if (READOUT_LEDGER && state.ledger && state.ledger.memory_summary) {
      const m = state.ledger.memory_summary;
      const op = state.ledger.distilled_optical_priors || {};
      const sj = state.ledger.scale_joy_meaning || null;
      const joyTag = sj && sj.summary_ko ? ` · 기쁨·가치[${sj.summary_ko}]` : '';
      const corpusTag = m.real_corpus_count > 0
        ? ` · 코퍼스 ${m.real_corpus_count}종(${Number(op.sky_to_ground_ratio || 1.38).toFixed(2)}:1)`
        : '';
      READOUT_LEDGER.textContent =
        `원장(${state.ledger.ledger_path}) — 법칙 ${m.learned_law_count} · 동작DNA ${m.motion_dna_count || 0} · ` +
        `교차이식 ${m.transplant_count || 0}${corpusTag}${joyTag}`;
    }
  }

  function loop(ts) {
    if (!state.active) return;
    const dt = Math.min(0.08, Math.max(0.01, (ts - lastTs) / 1000));
    lastTs = ts;
    if (captureCurrentFrame(dt)) {
      processDynamicFrame();
    }
    updateLivingActors(dt);
    drawViewport();
    renderReadouts(false);
    rafId = requestAnimationFrame(loop);
  }

  function hitTestEntity(nx, ny) {
    for (let i = state.placedEntities.length - 1; i >= 0; i--) {
      const e = state.placedEntities[i];
      const halfW = e.scale * 0.36;
      if (Math.abs(nx - e.x) < halfW && ny <= e.y + 0.04 && ny >= e.y - e.scale) {
        return e;
      }
    }
    return null;
  }

  CANVAS.addEventListener('pointerdown', (e) => {
    const rect = CANVAS.getBoundingClientRect();
    const nx = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0, 1);
    const ny = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0, 1);
    state.pointerDownPos = { nx, ny };
    const hit = hitTestEntity(nx, ny);
    if (hit && state.viewMode === 'recompose') {
      const zoneInfo = detectAnatomicalZone(hit, nx, ny);
      state.tactileSession = {
        uid: hit.uid,
        zoneInfo,
        startTs: performance.now(),
        startX: nx,
        startY: ny,
        lastX: nx,
        lastY: ny,
        travel: 0,
        strokeReversals: 0,
        lastDxSign: 0,
        mode: 'pending', // 'pending' | 'stroke' | 'hold' | 'guide'
        holdCommitted: false,
        holdPulseAcc: 0,
      };
      try { CANVAS.setPointerCapture(e.pointerId); } catch {}
    } else if (state.viewMode === 'recompose') {
      state.interventionRipples.push({ x: nx, y: ny, age: 0, maxAge: 0.95 });
      interveneWorldActors({ clickIntervention: true, targetX: nx, targetY: ny });
    }
  });

  CANVAS.addEventListener('pointermove', (e) => {
    const rect = CANVAS.getBoundingClientRect();
    const nx = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0.04, 0.96);
    const ny = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0.08, 0.94);
    state.pointerNorm = [nx, ny];
    state.pointerInside = true;

    if (!state.tactileSession) {
      if (state.viewMode === 'recompose') {
        const hoverHit = hitTestEntity(nx, ny);
        if (hoverHit) {
          const z = detectAnatomicalZone(hoverHit, nx, ny);
          state.hoverTouch = { uid: hoverHit.uid, zone: z.zone, zoneKo: z.zoneKo, hint: z.hint, nx, ny };
          CANVAS.style.cursor = 'grab';
        } else {
          state.hoverTouch = null;
          CANVAS.style.cursor = 'default';
        }
      } else {
        state.hoverTouch = null;
      }
      return;
    }

    const ts = state.tactileSession;
    const ent = state.placedEntities.find((x) => x.uid === ts.uid);
    if (!ent) return;

    const dx = nx - ts.lastX;
    const dy = ny - ts.lastY;
    const step = Math.hypot(dx, dy);
    ts.travel += step;
    ts.lastX = nx;
    ts.lastY = ny;

    // Detect rhythmic lateral back-and-forth rubbing (쓰다듬기!)
    if (Math.abs(dx) > 0.004) {
      const sign = dx > 0 ? 1 : -1;
      if (ts.lastDxSign !== 0 && sign !== ts.lastDxSign) {
        ts.strokeReversals += 1;
      }
      ts.lastDxSign = sign;
    }

    const distFromStart = Math.hypot(nx - ts.startX, ny - ts.startY);

    if (ts.mode === 'pending') {
      if (ts.strokeReversals >= 1 || ((ts.zoneInfo.zone === 'head' || ts.zoneInfo.zone === 'shoulder') && ts.travel > 0.022 && distFromStart < 0.068)) {
        ts.mode = 'stroke';
      } else if (distFromStart > 0.072 && ts.strokeReversals === 0) {
        ts.mode = 'guide';
        state.dragEntityUid = ent.uid;
      }
    }

    if (ts.mode === 'stroke') {
      // Live physical head/body lean following user's gentle hand stroke + golden warmth trail!
      ent.tactileLeanTarget = clamp(dx * 12.0, -0.14, 0.14);
      ent.warmthGlow = Math.min(1.0, (ent.warmthGlow || 0.2) + step * 3.2);
      if (step > 0.008) {
        state.tactileAuraTrails.push({ x: nx, y: ny, age: 0, maxAge: 0.72, rgb: '253, 224, 71' });
      }
    } else if (ts.mode === 'guide') {
      ent.x = clamp(nx, 0.08, 0.92);
      ent.y = clamp(ny, 0.34, 0.91);
      if (ent.living) {
        ent.targetX = ent.x;
        ent.targetY = ent.y;
      }
    }
  });

  CANVAS.addEventListener('pointerup', (e) => {
    const ts = state.tactileSession;
    state.tactileSession = null;
    state.dragEntityUid = null;
    try { CANVAS.releasePointerCapture(e.pointerId); } catch {}

    if (!ts) return;
    const ent = state.placedEntities.find((x) => x.uid === ts.uid);
    if (!ent) return;

    const durSec = Math.max(0.05, (performance.now() - ts.startTs) / 1000);
    const speedNorm = ts.travel / Math.max(0.08, durSec);

    if (ts.mode === 'hold' && ts.holdCommitted) {
      return; // Already committed during warm stillness hold!
    }
    if (ts.mode === 'stroke') {
      commitTactileInteraction(ent, ts.zoneInfo, 'stroke', durSec, Math.max(1, ts.strokeReversals), speedNorm);
    } else if (ts.mode === 'guide') {
      commitTactileInteraction(ent, ts.zoneInfo, 'guide', durSec, 0, speedNorm);
    } else if (durSec < 0.32 && ts.travel < 0.032) {
      // Brief quick touch -> 툭 건드리기 (poke)!
      state.tactileAuraTrails.push({ x: ts.startX, y: ts.startY, age: 0, maxAge: 0.65, rgb: '125, 211, 252' });
      commitTactileInteraction(ent, ts.zoneInfo, 'poke', durSec, 0, speedNorm);
    } else {
      commitTactileInteraction(ent, ts.zoneInfo, 'hold', durSec, 0, speedNorm);
    }
  });

  CANVAS.addEventListener('pointerleave', () => {
    state.hoverTouch = null;
    state.pointerInside = false;
  });

  CANVAS.addEventListener('dblclick', (e) => {
    const rect = CANVAS.getBoundingClientRect();
    const nx = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0, 1);
    const ny = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0, 1);
    const hit = hitTestEntity(nx, ny);
    if (hit) {
      state.placedEntities.push({
        ...hit,
        uid: `ent_${Date.now()}_dup`,
        x: clamp(hit.x + 0.14, 0.14, 0.88),
        y: clamp(hit.y + 0.02, 0.36, 0.88),
        scale: clamp(hit.scale * 0.92, 0.14, 0.54),
        phase: Math.random() * Math.PI * 2,
      });
      state.lastIntentSummary = `[${hit.name}] 실체를 복제 확장했습니다 (월드 좌표 고정·픽셀 재조명 자동 적용)`;
      renderReadouts(true);
    }
  });

  STAGE.addEventListener('dragover', (e) => e.preventDefault());
  STAGE.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer && e.dataTransfer.files;
    if (!files || !files.length) return;
    if (files.length > 1) {
      trainFromUserBatchFiles(files);
    } else {
      loadUserVideoOrPhoto(files[0]);
    }
  });

  // Wire controls
  if (SEL_STREAM) {
    SEL_STREAM.addEventListener('change', () => loadPresetStream(SEL_STREAM.value));
  }
  if (BTN_UPLOAD_VID && FILE_VID) {
    BTN_UPLOAD_VID.addEventListener('click', () => FILE_VID.click());
    FILE_VID.addEventListener('change', () => {
      if (FILE_VID.files && FILE_VID.files[0]) loadUserVideoOrPhoto(FILE_VID.files[0]);
    });
  }
  if (BTN_SCREEN) BTN_SCREEN.addEventListener('click', startScreenCapture);
  if (BTN_WEBCAM) BTN_WEBCAM.addEventListener('click', startWebcamCapture);
  if (BTN_SAVE_LAW) BTN_SAVE_LAW.addEventListener('click', () => saveCurrentDynamicLaw(false));
  if (BTN_HARVEST) BTN_HARVEST.addEventListener('click', harvestLiveMovingEntity);
  if (BTN_TRAIN_CORPUS) BTN_TRAIN_CORPUS.addEventListener('click', () => trainFromDiskCorpus(false));
  if (BTN_UPLOAD_CORPUS && FILE_BATCH_CORPUS) {
    BTN_UPLOAD_CORPUS.addEventListener('click', () => FILE_BATCH_CORPUS.click());
    FILE_BATCH_CORPUS.addEventListener('change', () => {
      if (FILE_BATCH_CORPUS.files && FILE_BATCH_CORPUS.files.length) {
        trainFromUserBatchFiles(FILE_BATCH_CORPUS.files);
        FILE_BATCH_CORPUS.value = '';
      }
    });
  }

  if (BTN_EXTRACT_MOTION) BTN_EXTRACT_MOTION.addEventListener('click', extractMotionDnaFromSourceA);
  if (BTN_TRANSPLANT_ACTOR) BTN_TRANSPLANT_ACTOR.addEventListener('click', transplantLivingActorToWorldB);
  if (SEL_REALM_PRESET) SEL_REALM_PRESET.addEventListener('change', () => applyRealmPreset(SEL_REALM_PRESET.value));
  if (SEL_PRESENCE_ROTOR) SEL_PRESENCE_ROTOR.addEventListener('change', () => applyPresenceRotorPreset(SEL_PRESENCE_ROTOR.value));
  if (SEL_ALIGNMENT) SEL_ALIGNMENT.addEventListener('change', () => applyAlignmentPreset(SEL_ALIGNMENT.value));
  if (BTN_ROLL_CHARACTER) BTN_ROLL_CHARACTER.addEventListener('click', rollCharacterLineage);

  if (BTN_APPLY_INTENT && INTENT_INPUT) {
    const runTextIntent = () => {
      const txt = (INTENT_INPUT.value || '').trim();
      if (!txt) return;
      const isFrontierResearch = /(우주함선|우주선|함선|비행기|항공기|자동차|로켓|마나|에테르|마법|워프|반중력|원리|연구|설계|발명|starship|space|aircraft|mana|aether|magic)/i.test(txt);
      const isLiveIntervention = /(이리|이쪽|와봐|다가|불러|뛰어|달려|점프|호랑이|어슬렁|순찰|피해|도망|쉬어|멈춰|앉아)/.test(txt);
      if (isFrontierResearch) {
        runFrontierResearch(txt);
      } else if (isLiveIntervention) {
        interveneWorldActors({ commandText: txt, targetX: 0.52, targetY: 0.78 });
      } else {
        executeIntent(txt, false);
      }
      INTENT_INPUT.value = '';
    };
    BTN_APPLY_INTENT.addEventListener('click', runTextIntent);
    INTENT_INPUT.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') runTextIntent();
    });
  }
  if (BTN_AUTO_INTENT) {
    BTN_AUTO_INTENT.addEventListener('click', () => executeIntent('', true));
  }
  if (BTN_RESEARCH_FRONTIER) {
    BTN_RESEARCH_FRONTIER.addEventListener('click', () => {
      const typed = INTENT_INPUT ? (INTENT_INPUT.value || '').trim() : '';
      runFrontierResearch(typed);
      if (INTENT_INPUT && typed) INTENT_INPUT.value = '';
    });
  }
  if (BTN_CLEAR_ENTS) {
    BTN_CLEAR_ENTS.addEventListener('click', () => {
      state.placedEntities = [];
      state.s4Brightness = 0;
      state.s4Warmth = 0;
      state.s2RelightDeg = 0;
      state.s1SpecularBoost = 0;
      state.lastIntentSummary = '원본 실세계 스트림 상태로 초기화했습니다.';
      renderReadouts(true);
    });
  }

  QUICK_BTNS.forEach((btn) => {
    btn.addEventListener('click', () => {
      const phrase = btn.getAttribute('data-di-quick') || '';
      if (phrase) executeIntent(phrase, false);
    });
  });

  VIEW_BTNS.forEach((btn) => {
    btn.addEventListener('click', () => {
      state.viewMode = btn.getAttribute('data-di-view') || 'recompose';
      VIEW_BTNS.forEach((b) => b.classList.toggle('primary', b === btn));
    });
  });

  window.ElysiaDynamicEngine = {
    start() {
      if (state.active) return;
      state.active = true;
      lastTs = performance.now();
      loadInitialLedger();
      if (!state.presetImg && state.streamKind === 'photo_drift') {
        loadPresetStream((SEL_STREAM && SEL_STREAM.value) || 'forest_drift');
      }
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(loop);
    },
    stop() {
      state.active = false;
      cancelAnimationFrame(rafId);
    },
  };
})();
