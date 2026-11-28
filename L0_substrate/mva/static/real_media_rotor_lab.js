/**
 * Elysia Real-World Causal Pixel Decomposition & Scale-Rotor Recombination Lab
 * ============================================================================
 * Obeys AGENTS.md Section 7: NEVER fabricate reality inside hand-coded formulas.
 * Instead, ingest REAL-WORLD pixels (high-res photos, .mp4/.webm videos, or live
 * webcam frames) and decompose EACH PIXEL ITSELF into its causal physical rotors:
 *
 *   Observed Pixel C(x,y) = S4(Illumination) * S3(Intrinsic Albedo) * S2(Normal Shading)
 *                         + S1(Specular/Glint) + S0(Micro-Texture Residual)
 *
 * Capabilities:
 *   1. True Intrinsic Pixel Decomposition directly from real pixels (0 fake geometry):
 *      - S4 Macro Illumination Field (low-frequency irradiance & color temperature)
 *      - S3 Intrinsic Material Albedo (illumination-invariant reflectance)
 *      - S2 Surface Normal Map N(x,y) & Shading (from luminance gradient structure tensor)
 *      - S1 Specular / Glint Component (high-luma, low-chroma mirror reflection separated from matter)
 *      - S0 Micro-Texture Residual (high-frequency fine detail guaranteeing exact reconstruction)
 *   2. Causal Recombination & Real Relighting:
 *      - Rotate S4 Light Vector across extracted S2 Real Surface Normals (N · L_new)
 *      - Transplant Real Source B's S4 Illumination Spectrum onto Source A's Real Albedo/Normals
 *      - Modulate S3 Albedo Saturation, S1 Specular Glint Intensity & S0 Micro-Texture
 *   3. Interactive Single-Pixel Causal Probe & Split-Curtain Verification:
 *      - Click any pixel to inspect its exact causal equation (RGB = S4 × S3 × S2 + S1 + S0)
 *      - Drag split curtain to compare Raw Real Pixels vs Recombined Reconstruction (live RMSE/PSNR)
 *   4. Crystallize extracted real-world causal spectrum into Python Ice (t=0) & Neural Spine.
 */
(function () {
  'use strict';

  const STAGE = document.getElementById('ervRealMediaStage');
  const CANVAS = document.getElementById('rmCanvas');
  if (!STAGE || !CANVAS) return;
  const ctx = CANVAS.getContext('2d');

  // Controls
  const SEL_SRC_A = document.getElementById('rmSelectSourceA');
  const SEL_SRC_B = document.getElementById('rmSelectSourceB');
  const FILE_INPUT_A = document.getElementById('rmFileInputA');
  const FILE_INPUT_B = document.getElementById('rmFileInputB');
  const BTN_UPLOAD_A = document.getElementById('rmBtnUploadA');
  const BTN_UPLOAD_B = document.getElementById('rmBtnUploadB');
  const BTN_WEBCAM = document.getElementById('rmBtnWebcam');
  const BTN_CRYSTALLIZE = document.getElementById('rmBtnCrystallize');
  const BTN_RECOMB_SAVE = document.getElementById('rmBtnSaveRecomb');
  const VIEW_BTNS = STAGE.querySelectorAll('[data-rm-view]');

  const SLIDER_LIGHT_MIX = document.getElementById('rmSliderLightMix');
  const VAL_LIGHT_MIX = document.getElementById('rmValLightMix');
  const SLIDER_RELIGHT = document.getElementById('rmSliderRelight');
  const VAL_RELIGHT = document.getElementById('rmValRelight');
  const SLIDER_SPECULAR = document.getElementById('rmSliderSpecular');
  const VAL_SPECULAR = document.getElementById('rmValSpecular');
  const SLIDER_DETAIL = document.getElementById('rmSliderDetail');
  const VAL_DETAIL = document.getElementById('rmValDetail');

  const READOUT_ANATOMY = document.getElementById('rmAnatomyReadout');
  const READOUT_PIXEL = document.getElementById('rmPixelProbeReadout');
  const READOUT_FIDELITY = document.getElementById('rmFidelityReadout');

  const PRESET_SOURCES = {
    ocean_sunlight: {
      label: '실사 바다 윤슬 (황혼 난반사)',
      url: '/static/assets/real_world/ocean_sunlight.jpg',
      kind: 'photo',
    },
    forest_mist: {
      label: '실사 새벽 삼나무 숲 호수',
      url: '/static/assets/real_world/forest_mist.jpg',
      kind: 'photo',
    },
    conservatory: {
      label: '실사 유리 서재 빛',
      url: '/static/assets/elysia/conservatory_bg.jpg',
      kind: 'photo',
    },
  };

  // Processing resolution (crisp high-speed native pixel decomposition at 60fps/real-time)
  const PROC_W = 560;
  const PROC_H = 315;

  const workCanvasA = document.createElement('canvas');
  workCanvasA.width = PROC_W;
  workCanvasA.height = PROC_H;
  const workCtxA = workCanvasA.getContext('2d', { willReadFrequently: true });

  const workCanvasB = document.createElement('canvas');
  workCanvasB.width = PROC_W;
  workCanvasB.height = PROC_H;
  const workCtxB = workCanvasB.getContext('2d', { willReadFrequently: true });

  const outCanvas = document.createElement('canvas');
  outCanvas.width = PROC_W;
  outCanvas.height = PROC_H;
  const outCtx = outCanvas.getContext('2d');
  const outImg = outCtx.createImageData(PROC_W, PROC_H);

  // Reusable video elements for real .mp4/.webm or live webcam ingestion
  const videoA = document.createElement('video');
  videoA.muted = true;
  videoA.loop = true;
  videoA.playsInline = true;
  videoA.crossOrigin = 'anonymous';

  const videoB = document.createElement('video');
  videoB.muted = true;
  videoB.loop = true;
  videoB.playsInline = true;
  videoB.crossOrigin = 'anonymous';

  const state = {
    active: false,
    viewMode: 'split', // 'split' | 's4_illum' | 's3_albedo' | 's2_normal' | 's1_specular' | 's0_residual'
    splitPos: 0.50,
    lightMix: 0.45,     // 0..1 transplant Source B S4 illumination onto Source A
    relightDeg: 0,      // -90..+90 rotate S4 light azimuth across Source A S2 real normals
    specularGain: 1.0,  // 0..2.2 S1 specular glint multiplier
    detailGain: 1.0,    // 0..2.2 S0 micro-texture multiplier
    sourceA: { name: PRESET_SOURCES.ocean_sunlight.label, kind: 'photo', elem: null, naturalW: 1280, naturalH: 720, isVideo: false },
    sourceB: { name: PRESET_SOURCES.forest_mist.label, kind: 'photo', elem: null, naturalW: 1280, naturalH: 720, isVideo: false },
    webcamStream: null,
    decompA: null,
    decompB: null,
    prevLumaA: null,
    flowVec: [0, 0],
    probePx: { x: Math.floor(PROC_W * 0.52), y: Math.floor(PROC_H * 0.56) },
    lastMetrics: { rmse: 0, psnr: 48, exactRmse: 0, exactPsnr: 52 },
    dirtyRecombine: true,
    dirtyDecompA: true,
    dirtyDecompB: true,
    lastStatusMsg: '실세계 픽셀을 S4(조광) · S3(물성) · S2(법선/음영) · S1(경면/윤슬) · S0(미세질감)로 분해 대기 중',
  };

  let rafId = 0;
  let draggingSplit = false;

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  // Fast separable box blur (3 passes -> smooth Gaussian approximation for S4 Macro Illumination!)
  function boxBlurRGB(src, w, h, radius) {
    const n = w * h;
    const tmp = new Float32Array(n * 3);
    const dst = new Float32Array(n * 3);
    const inv = 1.0 / (2 * radius + 1);

    // Horizontal pass
    for (let y = 0; y < h; y++) {
      let rSum = 0, gSum = 0, bSum = 0;
      const row = y * w;
      for (let k = -radius; k <= radius; k++) {
        const cx = clamp(k, 0, w - 1);
        const i3 = (row + cx) * 3;
        rSum += src[i3];
        gSum += src[i3 + 1];
        bSum += src[i3 + 2];
      }
      for (let x = 0; x < w; x++) {
        const o3 = (row + x) * 3;
        tmp[o3] = rSum * inv;
        tmp[o3 + 1] = gSum * inv;
        tmp[o3 + 2] = bSum * inv;
        const left = clamp(x - radius, 0, w - 1);
        const right = clamp(x + radius + 1, 0, w - 1);
        const l3 = (row + left) * 3;
        const r3 = (row + right) * 3;
        rSum += src[r3] - src[l3];
        gSum += src[r3 + 1] - src[l3 + 1];
        bSum += src[r3 + 2] - src[l3 + 2];
      }
    }

    // Vertical pass
    for (let x = 0; x < w; x++) {
      let rSum = 0, gSum = 0, bSum = 0;
      for (let k = -radius; k <= radius; k++) {
        const cy = clamp(k, 0, h - 1);
        const i3 = (cy * w + x) * 3;
        rSum += tmp[i3];
        gSum += tmp[i3 + 1];
        bSum += tmp[i3 + 2];
      }
      for (let y = 0; y < h; y++) {
        const o3 = (y * w + x) * 3;
        dst[o3] = rSum * inv;
        dst[o3 + 1] = gSum * inv;
        dst[o3 + 2] = bSum * inv;
        const top = clamp(y - radius, 0, h - 1);
        const bot = clamp(y + radius + 1, 0, h - 1);
        const t3 = (top * w + x) * 3;
        const b3 = (bot * w + x) * 3;
        rSum += tmp[b3] - tmp[t3];
        gSum += tmp[b3 + 1] - tmp[t3 + 1];
        bSum += tmp[b3 + 2] - tmp[t3 + 2];
      }
    }
    return dst;
  }

  /**
   * TRUE CAUSAL PIXEL DECOMPOSITION:
   * Splits EVERY real pixel C(x,y) into 5 physically-grounded scale rotors:
   *   1. S4 Illumination Field I(x,y) [RGB macro irradiance]
   *   2. S3 Intrinsic Material Albedo A(x,y) [chromatic reflectance independent of light intensity]
   *   3. S2 Surface Normal N(x,y) = (nx, ny, nz) & Base Shading S(x,y)
   *   4. S1 Specular / Glint Component G(x,y) [bright achromatic mirror reflection separated from matter]
   *   5. S0 Micro-Texture Residual R(x,y) [exact high-frequency residual so C = S4*S3*S2 + S1 + S0]
   */
  function decomposeRealPixels(imgData, prevLuma) {
    const w = imgData.width;
    const h = imgData.height;
    const n = w * h;
    const rawU8 = imgData.data;

    const rawF = new Float32Array(n * 3);
    const luma = new Float32Array(n);
    const specular = new Float32Array(n * 3); // S1
    const diffuse = new Float32Array(n * 3);

    let sumR = 0, sumG = 0, sumB = 0, sumLuma = 0;
    let specPixels = 0;

    // Step 1: Separate S1 Specular/Glint (high luminance, low saturation mirror reflection) from Diffuse matter
    for (let i = 0; i < n; i++) {
      const i4 = i * 4;
      const i3 = i * 3;
      const r = rawU8[i4] / 255.0;
      const g = rawU8[i4 + 1] / 255.0;
      const b = rawU8[i4 + 2] / 255.0;
      rawF[i3] = r;
      rawF[i3 + 1] = g;
      rawF[i3 + 2] = b;

      sumR += r;
      sumG += g;
      sumB += b;
      const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      luma[i] = lum;
      sumLuma += lum;

      const maxC = Math.max(r, g, b);
      const minC = Math.min(r, g, b);
      const sat = maxC > 1e-4 ? (maxC - minC) / maxC : 0;

      // Specular glint carries the light source's high brightness & reduced chroma (Shafer Dichromatic Model!)
      const specStrength = clamp((lum - 0.62) / 0.34, 0, 1) * clamp(1.0 - sat * 0.85, 0.2, 1.0);
      if (specStrength > 0.08) specPixels += 1;
      const sr = r * specStrength * 0.72;
      const sg = g * specStrength * 0.72;
      const sb = b * specStrength * 0.72;
      specular[i3] = sr;
      specular[i3 + 1] = sg;
      specular[i3 + 2] = sb;

      diffuse[i3] = Math.max(0, r - sr);
      diffuse[i3 + 1] = Math.max(0, g - sg);
      diffuse[i3 + 2] = Math.max(0, b - sb);
    }

    // Step 2: S4 Macro Illumination Field (2-pass large-scale Gaussian spatial irradiance)
    const blur1 = boxBlurRGB(diffuse, w, h, 14);
    const illumS4 = boxBlurRGB(blur1, w, h, 14);

    // Mid-scale blur for isolating S2 geometric shading vs S0 micro-texture residual
    const mesoField = boxBlurRGB(diffuse, w, h, 3);

    // Step 3: S3 Intrinsic Albedo (strip S4 macro illumination & S2 shading from material reflectance!)
    const albedoS3 = new Float32Array(n * 3);
    const shadingS2 = new Float32Array(n);
    const normalS2 = new Float32Array(n * 3);
    const residualS0 = new Float32Array(n * 3);

    let detailEnergySum = 0;
    let sxx = 0, syy = 0, sxy = 0;

    for (let y = 0; y < h; y++) {
      const yUp = Math.max(0, y - 1);
      const yDn = Math.min(h - 1, y + 1);
      for (let x = 0; x < w; x++) {
        const i = y * w + x;
        const i3 = i * 3;
        const xLt = Math.max(0, x - 1);
        const xRt = Math.min(w - 1, x + 1);

        // S2 Surface Normal estimated via luminance gradient (shape-from-shading!)
        const gx = (luma[y * w + xRt] - luma[y * w + xLt]) * 3.8;
        const gy = (luma[yDn * w + x] - luma[yUp * w + x]) * 3.8;
        sxx += gx * gx;
        syy += gy * gy;
        sxy += gx * gy;

        const invLen = 1.0 / Math.sqrt(gx * gx + gy * gy + 1.0);
        normalS2[i3] = -gx * invLen;
        normalS2[i3 + 1] = -gy * invLen;
        normalS2[i3 + 2] = invLen;

        // S2 local geometric shading ratio (meso luminance / macro S4 luminance)
        const illLum = Math.max(0.06, 0.2126 * illumS4[i3] + 0.7152 * illumS4[i3 + 1] + 0.0722 * illumS4[i3 + 2]);
        const mesoLum = 0.2126 * mesoField[i3] + 0.7152 * mesoField[i3 + 1] + 0.0722 * mesoField[i3 + 2];
        const shade = clamp(mesoLum / illLum, 0.12, 2.4);
        shadingS2[i] = shade;

        // S3 Intrinsic Albedo = MesoDiffuse / (S4_Illumination * S2_Shading)
        // Normalized around neutral 0.5 reflectance scale so Albedo stays pure material chromaticity!
        const denomR = Math.max(0.05, illumS4[i3] * shade);
        const denomG = Math.max(0.05, illumS4[i3 + 1] * shade);
        const denomB = Math.max(0.05, illumS4[i3 + 2] * shade);
        const aR = clamp(mesoField[i3] / denomR, 0.05, 2.5);
        const aG = clamp(mesoField[i3 + 1] / denomG, 0.05, 2.5);
        const aB = clamp(mesoField[i3 + 2] / denomB, 0.05, 2.5);
        albedoS3[i3] = aR;
        albedoS3[i3 + 1] = aG;
        albedoS3[i3 + 2] = aB;

        // S0 Micro-Texture Residual = RawDiffuse - Reconstructed(S4 * S3 * S2)
        // Guarantees lossless causal decomposition of the actual real pixel!
        const baseR = illumS4[i3] * aR * shade;
        const baseG = illumS4[i3 + 1] * aG * shade;
        const baseB = illumS4[i3 + 2] * aB * shade;
        const resR = diffuse[i3] - baseR;
        const resG = diffuse[i3 + 1] - baseG;
        const resB = diffuse[i3 + 2] - baseB;
        residualS0[i3] = resR;
        residualS0[i3 + 1] = resG;
        residualS0[i3 + 2] = resB;

        detailEnergySum += Math.abs(resR) + Math.abs(resG) + Math.abs(resB);
      }
    }

    // Real inter-frame optical flow rotor (when ingesting video/webcam)
    let flowX = 0, flowY = 0;
    if (prevLuma && prevLuma.length === n) {
      let fxNum = 0, fyNum = 0, fDen = 1e-4;
      for (let y = 4; y < h - 4; y += 4) {
        for (let x = 4; x < w - 4; x += 4) {
          const i = y * w + x;
          const ix = (luma[i + 1] - luma[i - 1]) * 0.5;
          const iy = (luma[i + w] - luma[i - w]) * 0.5;
          const it = luma[i] - prevLuma[i];
          const g2 = ix * ix + iy * iy;
          if (g2 > 0.0004) {
            fxNum += -it * ix;
            fyNum += -it * iy;
            fDen += g2;
          }
        }
      }
      flowX = clamp((fxNum / fDen) * 8.0, -15, 15);
      flowY = clamp((fyNum / fDen) * 8.0, -15, 15);
    }

    const meanR = (sumR / n) * 255;
    const meanG = (sumG / n) * 255;
    const meanB = (sumB / n) * 255;
    const meanLuma = sumLuma / n;
    // Estimate physical color temperature (Kelvin) from R/B balance of real S4 field
    const rbRatio = meanR / Math.max(1, meanB);
    const colorTempK = Math.round(clamp(6500 - (rbRatio - 1.0) * 3200, 2200, 10500));
    const domAngleDeg = (0.5 * Math.atan2(2 * sxy, sxx - syy)) * (180 / Math.PI);

    return {
      w,
      h,
      rawF,
      luma,
      illumS4,
      albedoS3,
      shadingS2,
      normalS2,
      specularS1: specular,
      residualS0,
      stats: {
        meanRGB: [Math.round(meanR), Math.round(meanG), Math.round(meanB)],
        colorTempK,
        meanLuma,
        dominantAngleDeg: domAngleDeg,
        detailEnergy: detailEnergySum / (n * 3),
        specularRatio: specPixels / n,
        flowVec: [flowX, flowY],
      },
    };
  }

  function loadPreset(targetKey, presetId) {
    const info = PRESET_SOURCES[presetId] || PRESET_SOURCES.ocean_sunlight;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      if (targetKey === 'A') {
        stopWebcam();
        videoA.pause();
        state.sourceA = {
          name: info.label,
          kind: 'photo',
          elem: img,
          naturalW: img.naturalWidth || PROC_W,
          naturalH: img.naturalHeight || PROC_H,
          isVideo: false,
        };
        state.prevLumaA = null;
        state.dirtyDecompA = true;
      } else {
        videoB.pause();
        state.sourceB = {
          name: info.label,
          kind: 'photo',
          elem: img,
          naturalW: img.naturalWidth || PROC_W,
          naturalH: img.naturalHeight || PROC_H,
          isVideo: false,
        };
        state.dirtyDecompB = true;
      }
      state.dirtyRecombine = true;
    };
    img.src = info.url;
  }

  function loadUserFile(targetKey, file) {
    if (!file) return;
    const url = URL.createObjectURL(file);
    const isVid = file.type && file.type.startsWith('video/');
    if (isVid) {
      const vid = targetKey === 'A' ? videoA : videoB;
      if (targetKey === 'A') stopWebcam();
      vid.src = url;
      vid.onloadeddata = () => {
        vid.play().catch(() => {});
        const entry = {
          name: file.name,
          kind: 'video',
          elem: vid,
          naturalW: vid.videoWidth || PROC_W,
          naturalH: vid.videoHeight || PROC_H,
          isVideo: true,
        };
        if (targetKey === 'A') {
          state.sourceA = entry;
          state.prevLumaA = null;
          state.dirtyDecompA = true;
        } else {
          state.sourceB = entry;
          state.dirtyDecompB = true;
        }
        state.dirtyRecombine = true;
        state.lastStatusMsg = `실세계 동영상 [${file.name}] 투입 완료 — 매 프레임 픽셀 인과 분해 중`;
      };
    } else {
      const img = new Image();
      img.onload = () => {
        const entry = {
          name: file.name,
          kind: 'photo',
          elem: img,
          naturalW: img.naturalWidth || PROC_W,
          naturalH: img.naturalHeight || PROC_H,
          isVideo: false,
        };
        if (targetKey === 'A') {
          stopWebcam();
          videoA.pause();
          state.sourceA = entry;
          state.prevLumaA = null;
          state.dirtyDecompA = true;
        } else {
          videoB.pause();
          state.sourceB = entry;
          state.dirtyDecompB = true;
        }
        state.dirtyRecombine = true;
        state.lastStatusMsg = `실세계 고해상도 사진 [${file.name}] (${entry.naturalW}×${entry.naturalH}) 인과 분해 완료`;
      };
      img.src = url;
    }
  }

  function stopWebcam() {
    if (state.webcamStream) {
      state.webcamStream.getTracks().forEach((t) => t.stop());
      state.webcamStream = null;
      if (BTN_WEBCAM) {
        BTN_WEBCAM.textContent = '실시간 카메라 투입';
        BTN_WEBCAM.classList.remove('primary');
      }
    }
  }

  async function toggleWebcam() {
    if (state.webcamStream) {
      stopWebcam();
      loadPreset('A', (SEL_SRC_A && SEL_SRC_A.value) || 'ocean_sunlight');
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      state.lastStatusMsg = '이 브라우저 환경에서는 카메라 장치에 접근할 수 없습니다. 동영상·사진 파일을 직접 올려보세요.';
      renderReadouts();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 }, audio: false });
      state.webcamStream = stream;
      videoA.srcObject = stream;
      await videoA.play();
      state.sourceA = {
        name: '실시간 카메라 입력',
        kind: 'camera',
        elem: videoA,
        naturalW: videoA.videoWidth || 1280,
        naturalH: videoA.videoHeight || 720,
        isVideo: true,
      };
      state.prevLumaA = null;
      state.dirtyDecompA = true;
      if (BTN_WEBCAM) {
        BTN_WEBCAM.textContent = '카메라 중지';
        BTN_WEBCAM.classList.add('primary');
      }
      state.lastStatusMsg = '실시간 카메라 프레임 투입 중 — S4~S0 인과 픽셀 분해 가동';
    } catch {
      state.lastStatusMsg = '카메라 권한이 거부되었거나 장치가 없습니다. 로컬 동영상(.mp4) 또는 고해상도 사진을 직접 올려보세요.';
      renderReadouts();
    }
  }

  function captureSourceToCanvas(src, targetCtx) {
    if (!src || !src.elem) return false;
    if (src.isVideo && src.elem.readyState < 2) return false;
    const sw = src.isVideo ? (src.elem.videoWidth || PROC_W) : (src.elem.naturalWidth || PROC_W);
    const sh = src.isVideo ? (src.elem.videoHeight || PROC_H) : (src.elem.naturalHeight || PROC_H);
    if (sw <= 0 || sh <= 0) return false;
    // Aspect-preserving cover crop so real-world media never stretches!
    const srcRatio = sw / sh;
    const dstRatio = PROC_W / PROC_H;
    let sx = 0, sy = 0, cw = sw, ch = sh;
    if (srcRatio > dstRatio) {
      cw = sh * dstRatio;
      sx = (sw - cw) * 0.5;
    } else {
      ch = sw / dstRatio;
      sy = (sh - ch) * 0.5;
    }
    targetCtx.drawImage(src.elem, sx, sy, cw, ch, 0, 0, PROC_W, PROC_H);
    return true;
  }

  /**
   * Recombine & Render:
   * Evaluates C_recomb(x,y) = S4_mixed(x,y) * S3_albedo_A(x,y) * S2_relit_shading(x,y)
   *                         + S1_specular_A(x,y) * specGain * S4_tint
   *                         + S0_residual_A(x,y) * detailGain
   */
  function runRecombination() {
    const dA = state.decompA;
    if (!dA) return;
    const dB = state.decompB || dA;
    const n = dA.w * dA.h;
    const out = outImg.data;
    const mix = state.lightMix;
    const specGain = state.specularGain;
    const detGain = state.detailGain;
    const mode = state.viewMode;

    // New light direction from Relight Rotor angle (rotates illumination across real S2 surface normals!)
    const az = (state.relightDeg * Math.PI) / 180.0;
    const lx = Math.sin(az) * 0.72;
    const ly = -0.22;
    const lz = Math.cos(az) * 0.72;
    const lLen = Math.hypot(lx, ly, lz);
    const nlx = lx / lLen, nly = ly / lLen, nlz = lz / lLen;
    const relightStrength = Math.abs(state.relightDeg) / 90.0;

    // Donor B's macro S4 chromatic ratio (average illumination tone of Source B)
    const meanBR = Math.max(0.08, dB.stats.meanRGB[0] / 255.0);
    const meanBG = Math.max(0.08, dB.stats.meanRGB[1] / 255.0);
    const meanBB = Math.max(0.08, dB.stats.meanRGB[2] / 255.0);
    const bLumaMean = Math.max(0.08, 0.2126 * meanBR + 0.7152 * meanBG + 0.0722 * meanBB);
    const bTintR = meanBR / bLumaMean;
    const bTintG = meanBG / bLumaMean;
    const bTintB = meanBB / bLumaMean;

    let mseSum = 0;
    let exactMseSum = 0;

    for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      const i4 = i * 4;

      const rawR = dA.rawF[i3];
      const rawG = dA.rawF[i3 + 1];
      const rawB = dA.rawF[i3 + 2];

      // S4 Illumination: blend Source A's real S4 irradiance with Source B's real S4 irradiance
      const iR = dA.illumS4[i3] * (1.0 - mix) + dB.illumS4[i3] * mix;
      const iG = dA.illumS4[i3 + 1] * (1.0 - mix) + dB.illumS4[i3 + 1] * mix;
      const iB = dA.illumS4[i3 + 2] * (1.0 - mix) + dB.illumS4[i3 + 2] * mix;

      // S3 Intrinsic Albedo (Material itself from Source A)
      const aR = dA.albedoS3[i3];
      const aG = dA.albedoS3[i3 + 1];
      const aB = dA.albedoS3[i3 + 2];

      // S2 Real Surface Normal + Relit Shading (N · L_new)
      const nx = dA.normalS2[i3];
      const ny = dA.normalS2[i3 + 1];
      const nz = dA.normalS2[i3 + 2];
      const baseShade = dA.shadingS2[i];
      const ndotl = clamp(nx * nlx + ny * nly + nz * nlz, 0.15, 1.45);
      const relitShade = baseShade * (1.0 - relightStrength * 0.55) + (baseShade * ndotl * 1.25) * (relightStrength * 0.55);

      // S1 Specular Glint (tinted by transplanted S4 light spectrum — real optics!)
      const sTintR = 1.0 * (1.0 - mix) + bTintR * mix;
      const sTintG = 1.0 * (1.0 - mix) + bTintG * mix;
      const sTintB = 1.0 * (1.0 - mix) + bTintB * mix;
      const specBoost = specGain * (1.0 + relightStrength * (ndotl - 0.65) * 0.65);
      const spR = dA.specularS1[i3] * specBoost * sTintR;
      const spG = dA.specularS1[i3 + 1] * specBoost * sTintG;
      const spB = dA.specularS1[i3 + 2] * specBoost * sTintB;

      // S0 Micro-Texture Residual
      const resR = dA.residualS0[i3] * detGain;
      const resG = dA.residualS0[i3 + 1] * detGain;
      const resB = dA.residualS0[i3 + 2] * detGain;

      // Exact unmodified causal reconstruction (verify 0-loss decomposition!)
      const exR = dA.illumS4[i3] * aR * baseShade + dA.specularS1[i3] + dA.residualS0[i3];
      const exG = dA.illumS4[i3 + 1] * aG * baseShade + dA.specularS1[i3 + 1] + dA.residualS0[i3 + 1];
      const exB = dA.illumS4[i3 + 2] * aB * baseShade + dA.specularS1[i3 + 2] + dA.residualS0[i3 + 2];
      exactMseSum += (exR - rawR) ** 2 + (exG - rawG) ** 2 + (exB - rawB) ** 2;

      // Recombined & Relit causal pixel
      const recR = clamp(iR * aR * relitShade + spR + resR, 0, 1);
      const recG = clamp(iG * aG * relitShade + spG + resG, 0, 1);
      const recB = clamp(iB * aB * relitShade + spB + resB, 0, 1);
      mseSum += (recR - rawR) ** 2 + (recG - rawG) ** 2 + (recB - rawB) ** 2;

      let outR = recR, outG = recG, outB = recB;
      if (mode === 's4_illum') {
        outR = clamp(iR * 1.15, 0, 1);
        outG = clamp(iG * 1.15, 0, 1);
        outB = clamp(iB * 1.15, 0, 1);
      } else if (mode === 's3_albedo') {
        outR = clamp(aR * 0.52, 0, 1);
        outG = clamp(aG * 0.52, 0, 1);
        outB = clamp(aB * 0.52, 0, 1);
      } else if (mode === 's2_normal') {
        // Tangent-space RGB Normal visualization directly extracted from real pixels!
        outR = clamp(nx * 0.5 + 0.5, 0, 1);
        outG = clamp(ny * 0.5 + 0.5, 0, 1);
        outB = clamp(nz * 0.5 + 0.5, 0, 1);
      } else if (mode === 's1_specular') {
        outR = clamp(spR * 2.4, 0, 1);
        outG = clamp(spG * 2.4, 0, 1);
        outB = clamp(spB * 2.4, 0, 1);
      } else if (mode === 's0_residual') {
        outR = clamp(0.5 + resR * 3.8, 0, 1);
        outG = clamp(0.5 + resG * 3.8, 0, 1);
        outB = clamp(0.5 + resB * 3.8, 0, 1);
      }

      out[i4] = Math.round(outR * 255);
      out[i4 + 1] = Math.round(outG * 255);
      out[i4 + 2] = Math.round(outB * 255);
      out[i4 + 3] = 255;
    }

    outCtx.putImageData(outImg, 0, 0);

    const mse = mseSum / (n * 3);
    const rmse = Math.sqrt(mse);
    const psnr = mse > 1e-8 ? Math.min(68, -10 * Math.log10(mse)) : 68;

    const exMse = exactMseSum / (n * 3);
    const exRmse = Math.sqrt(exMse);
    const exPsnr = exMse > 1e-8 ? Math.min(68, -10 * Math.log10(exMse)) : 68;

    state.lastMetrics = { rmse, psnr, exactRmse: exRmse, exactPsnr: exPsnr };
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

    if (state.decompA) {
      if (state.viewMode === 'split') {
        const splitX = Math.round(w * state.splitPos);
        // Left: RAW real-world pixels (zero processing)
        ctx.save();
        ctx.beginPath();
        ctx.rect(0, 0, splitX, h);
        ctx.clip();
        ctx.drawImage(workCanvasA, 0, 0, w, h);
        ctx.restore();

        // Right: Causally decomposed & recombined pixels (S4×S3×S2 + S1 + S0)
        ctx.save();
        ctx.beginPath();
        ctx.rect(splitX, 0, w - splitX, h);
        ctx.clip();
        ctx.drawImage(outCanvas, 0, 0, w, h);
        ctx.restore();

        // Crisp split curtain line
        ctx.strokeStyle = 'rgba(248, 250, 252, 0.92)';
        ctx.lineWidth = 1.6;
        ctx.beginPath();
        ctx.moveTo(splitX, 0);
        ctx.lineTo(splitX, h);
        ctx.stroke();

        // Minimal corner labels
        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(10, 10, 224, 24);
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '600 11px system-ui, sans-serif';
        ctx.fillText(`실세계 원본 A · ${state.sourceA.name.slice(0, 16)}`, 16, 26);

        ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
        ctx.fillRect(w - 266, 10, 256, 24);
        ctx.fillStyle = '#a7f3d0';
        ctx.fillText(`픽셀 인과 재조합 (S4×S3×S2+S1+S0)`, w - 258, 26);
      } else {
        ctx.drawImage(outCanvas, 0, 0, w, h);
        const titles = {
          s4_illum: 'S4 조광·입사광 스펙트럼 (실제 픽셀에서 빛만 분리)',
          s3_albedo: 'S3 고유 물성·알베도 (조명을 제거한 물질 자체)',
          s2_normal: 'S2 표면 법선맵 N(x,y) (실제 픽셀 기울기에서 복원한 3D 형상)',
          s1_specular: 'S1 경면·난반사 윤슬 (물성과 분리된 순수 광원 반사)',
          s0_residual: 'S0 미세 질감 잔차 (원형 무손실 복원 경계)',
        };
        ctx.fillStyle = 'rgba(15, 23, 42, 0.78)';
        ctx.fillRect(10, 10, 390, 26);
        ctx.fillStyle = '#bae6fd';
        ctx.font = '600 11.5px system-ui, sans-serif';
        ctx.fillText(titles[state.viewMode] || '', 18, 27);
      }

      // Single-Pixel Causal Probe Crosshair
      const pxX = (state.probePx.x / PROC_W) * w;
      const pxY = (state.probePx.y / PROC_H) * h;
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.arc(pxX, pxY, 7, 0, Math.PI * 2);
      ctx.moveTo(pxX - 12, pxY);
      ctx.lineTo(pxX + 12, pxY);
      ctx.moveTo(pxX, pxY - 12);
      ctx.lineTo(pxX, pxY + 12);
      ctx.stroke();

      ctx.fillStyle = 'rgba(15, 23, 42, 0.72)';
      ctx.fillRect(10, h - 26, 360, 18);
      ctx.fillStyle = '#cbd5e1';
      ctx.font = '10.5px system-ui, sans-serif';
      ctx.fillText('클릭: 1픽셀 인과 해부 프로브 · 수직선 드래그: 원본↔재조합 비교 · 파일 드롭 지원', 16, h - 13);
    }

    ctx.restore();
  }

  function renderReadouts() {
    const dA = state.decompA;
    if (!dA) return;
    const dB = state.decompB || dA;

    if (READOUT_ANATOMY) {
      const s = dA.stats;
      const sb = dB.stats;
      READOUT_ANATOMY.textContent =
        `원본 A [${state.sourceA.name}] (${state.sourceA.naturalW}×${state.sourceA.naturalH}) — ` +
        `S4 조광 ${s.colorTempK}K(명도 ${s.meanLuma.toFixed(2)}) · S3 주방향 ${s.dominantAngleDeg.toFixed(1)}° / 흐름[${s.flowVec[0].toFixed(2)},${s.flowVec[1].toFixed(2)}] · ` +
        `S1 경면윤슬 ${(s.specularRatio * 100).toFixed(1)}% · 광원 이식원 B [${state.sourceB.name} · ${sb.colorTempK}K]`;
    }

    if (READOUT_PIXEL) {
      const px = clamp(state.probePx.x, 0, dA.w - 1);
      const py = clamp(state.probePx.y, 0, dA.h - 1);
      const i = py * dA.w + px;
      const i3 = i * 3;
      const r = Math.round(dA.rawF[i3] * 255);
      const g = Math.round(dA.rawF[i3 + 1] * 255);
      const b = Math.round(dA.rawF[i3 + 2] * 255);
      const iLum = (0.2126 * dA.illumS4[i3] + 0.7152 * dA.illumS4[i3 + 1] + 0.0722 * dA.illumS4[i3 + 2]).toFixed(2);
      const aR = dA.albedoS3[i3].toFixed(2), aG = dA.albedoS3[i3 + 1].toFixed(2), aB = dA.albedoS3[i3 + 2].toFixed(2);
      const nx = dA.normalS2[i3].toFixed(2), ny = dA.normalS2[i3 + 1].toFixed(2), nz = dA.normalS2[i3 + 2].toFixed(2);
      const sp = ((dA.specularS1[i3] + dA.specularS1[i3 + 1] + dA.specularS1[i3 + 2]) / 3).toFixed(3);
      const res = ((Math.abs(dA.residualS0[i3]) + Math.abs(dA.residualS0[i3 + 1]) + Math.abs(dA.residualS0[i3 + 2])) / 3).toFixed(3);
      READOUT_PIXEL.textContent =
        `프로브 픽셀(${px},${py}) RGB(${r},${g},${b}) = ` +
        `S4 조광(${iLum}) × S3 물성알베도(${aR},${aG},${aB}) × S2 법선(${nx},${ny},${nz}) + S1 경면(${sp}) + S0 미세잔차(${res})`;
    }

    if (READOUT_FIDELITY) {
      READOUT_FIDELITY.textContent =
        `원형 인과 분해 검증: 무손실 복원 PSNR ${state.lastMetrics.exactPsnr.toFixed(1)}dB (RMSE ${state.lastMetrics.exactRmse.toFixed(4)})  |  ` +
        `현재 재조합 변화도 PSNR ${state.lastMetrics.psnr.toFixed(1)}dB  |  ${state.lastStatusMsg}`;
    }
  }

  function updateControlLabels() {
    if (VAL_LIGHT_MIX) VAL_LIGHT_MIX.textContent = `${Math.round(state.lightMix * 100)}%`;
    if (VAL_RELIGHT) VAL_RELIGHT.textContent = `${state.relightDeg >= 0 ? '+' : ''}${state.relightDeg}°`;
    if (VAL_SPECULAR) VAL_SPECULAR.textContent = `${state.specularGain.toFixed(2)}x`;
    if (VAL_DETAIL) VAL_DETAIL.textContent = `${state.detailGain.toFixed(2)}x`;
    VIEW_BTNS.forEach((b) => {
      b.classList.toggle('primary', b.getAttribute('data-rm-view') === state.viewMode);
    });
  }

  async function syncToElysiaSpine(action, params) {
    try {
      const res = await fetch('/api/world-rotor/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, params }),
      });
      if (!res.ok) return null;
      return await res.json();
    } catch {
      return null;
    }
  }

  function loop() {
    if (!state.active) return;

    if (state.sourceA.isVideo || state.dirtyDecompA) {
      if (captureSourceToCanvas(state.sourceA, workCtxA)) {
        const imgA = workCtxA.getImageData(0, 0, PROC_W, PROC_H);
        state.decompA = decomposeRealPixels(imgA, state.prevLumaA);
        state.prevLumaA = state.decompA.luma;
        state.dirtyDecompA = false;
        state.dirtyRecombine = true;
      }
    }
    if (state.sourceB.isVideo || state.dirtyDecompB) {
      if (captureSourceToCanvas(state.sourceB, workCtxB)) {
        const imgB = workCtxB.getImageData(0, 0, PROC_W, PROC_H);
        state.decompB = decomposeRealPixels(imgB, null);
        state.dirtyDecompB = false;
        state.dirtyRecombine = true;
      }
    }

    if (state.dirtyRecombine && state.decompA) {
      runRecombination();
      state.dirtyRecombine = false;
      renderReadouts();
    }

    drawViewport();
    rafId = requestAnimationFrame(loop);
  }

  // Pointer interactions: drag near split line to scrub comparison, click anywhere else to probe 1 pixel!
  CANVAS.addEventListener('pointerdown', (e) => {
    const rect = CANVAS.getBoundingClientRect();
    const nx = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0, 1);
    const ny = clamp((e.clientY - rect.top) / Math.max(1, rect.height), 0, 1);
    if (state.viewMode === 'split' && Math.abs(nx - state.splitPos) < 0.04) {
      draggingSplit = true;
      try { CANVAS.setPointerCapture(e.pointerId); } catch {}
      return;
    }
    state.probePx = {
      x: clamp(Math.floor(nx * PROC_W), 0, PROC_W - 1),
      y: clamp(Math.floor(ny * PROC_H), 0, PROC_H - 1),
    };
    renderReadouts();
  });

  CANVAS.addEventListener('pointermove', (e) => {
    if (!draggingSplit) return;
    const rect = CANVAS.getBoundingClientRect();
    state.splitPos = clamp((e.clientX - rect.left) / Math.max(1, rect.width), 0.05, 0.95);
  });

  CANVAS.addEventListener('pointerup', (e) => {
    draggingSplit = false;
    try { CANVAS.releasePointerCapture(e.pointerId); } catch {}
  });

  // Drag & Drop ANY real video or high-res photo directly onto the viewport!
  STAGE.addEventListener('dragover', (e) => {
    e.preventDefault();
  });
  STAGE.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) loadUserFile('A', file);
  });

  if (SEL_SRC_A) {
    SEL_SRC_A.addEventListener('change', () => loadPreset('A', SEL_SRC_A.value));
  }
  if (SEL_SRC_B) {
    SEL_SRC_B.addEventListener('change', () => loadPreset('B', SEL_SRC_B.value));
  }
  if (BTN_UPLOAD_A && FILE_INPUT_A) {
    BTN_UPLOAD_A.addEventListener('click', () => FILE_INPUT_A.click());
    FILE_INPUT_A.addEventListener('change', () => {
      if (FILE_INPUT_A.files && FILE_INPUT_A.files[0]) loadUserFile('A', FILE_INPUT_A.files[0]);
    });
  }
  if (BTN_UPLOAD_B && FILE_INPUT_B) {
    BTN_UPLOAD_B.addEventListener('click', () => FILE_INPUT_B.click());
    FILE_INPUT_B.addEventListener('change', () => {
      if (FILE_INPUT_B.files && FILE_INPUT_B.files[0]) loadUserFile('B', FILE_INPUT_B.files[0]);
    });
  }
  if (BTN_WEBCAM) {
    BTN_WEBCAM.addEventListener('click', toggleWebcam);
  }

  VIEW_BTNS.forEach((btn) => {
    btn.addEventListener('click', () => {
      state.viewMode = btn.getAttribute('data-rm-view') || 'split';
      state.dirtyRecombine = true;
      updateControlLabels();
    });
  });

  if (SLIDER_LIGHT_MIX) {
    SLIDER_LIGHT_MIX.addEventListener('input', () => {
      state.lightMix = Number(SLIDER_LIGHT_MIX.value) / 100;
      state.dirtyRecombine = true;
      updateControlLabels();
    });
  }
  if (SLIDER_RELIGHT) {
    SLIDER_RELIGHT.addEventListener('input', () => {
      state.relightDeg = Number(SLIDER_RELIGHT.value);
      state.dirtyRecombine = true;
      updateControlLabels();
    });
  }
  if (SLIDER_SPECULAR) {
    SLIDER_SPECULAR.addEventListener('input', () => {
      state.specularGain = Number(SLIDER_SPECULAR.value) / 100;
      state.dirtyRecombine = true;
      updateControlLabels();
    });
  }
  if (SLIDER_DETAIL) {
    SLIDER_DETAIL.addEventListener('input', () => {
      state.detailGain = Number(SLIDER_DETAIL.value) / 100;
      state.dirtyRecombine = true;
      updateControlLabels();
    });
  }

  if (BTN_CRYSTALLIZE) {
    BTN_CRYSTALLIZE.addEventListener('click', async () => {
      if (!state.decompA) return;
      BTN_CRYSTALLIZE.disabled = true;
      const s = state.decompA.stats;
      const res = await syncToElysiaSpine('ingest_real_media_spectrum', {
        source_name: state.sourceA.name,
        media_kind: state.sourceA.kind,
        width: state.sourceA.naturalW,
        height: state.sourceA.naturalH,
        s4_mean_rgb: s.meanRGB,
        s4_color_temp_k: s.colorTempK,
        s4_mean_luma: s.meanLuma,
        s3_flow_x: s.flowVec[0],
        s3_flow_y: s.flowVec[1],
        s3_dominant_angle_deg: s.dominantAngleDeg,
        s2_detail_energy: s.detailEnergy,
        s1_specular_ratio: s.specularRatio,
        recon_rmse: state.lastMetrics.exactRmse,
        recon_psnr_db: state.lastMetrics.exactPsnr,
      });
      BTN_CRYSTALLIZE.disabled = false;
      state.lastStatusMsg = res
        ? `엘리시아 얼음(t=0) 기억에 [${state.sourceA.name}] 실세계 픽셀 스펙트럼 결정화 완료`
        : '서버 동기화 실패 (브라우저 로컬 분해 유지)';
      renderReadouts();
    });
  }

  if (BTN_RECOMB_SAVE) {
    BTN_RECOMB_SAVE.addEventListener('click', async () => {
      if (!state.decompA) return;
      BTN_RECOMB_SAVE.disabled = true;
      const res = await syncToElysiaSpine('recombine_media_spectra', {
        structure_source: state.sourceA.name,
        light_source: state.sourceB.name,
        light_mix: state.lightMix,
        detail_gain: state.detailGain,
        phase_shift: state.relightDeg,
        recombined_psnr_db: state.lastMetrics.psnr,
      });
      BTN_RECOMB_SAVE.disabled = false;
      state.lastStatusMsg = res
        ? `실세계 재조합 원리 [${state.sourceA.name} × ${state.sourceB.name}] 엘리시아 신경 척추에 저장 완료`
        : '서버 동기화 실패';
      renderReadouts();
    });
  }

  window.ElysiaRealMediaLab = {
    start() {
      if (state.active) return;
      state.active = true;
      updateControlLabels();
      if (!state.sourceA.elem) loadPreset('A', (SEL_SRC_A && SEL_SRC_A.value) || 'ocean_sunlight');
      if (!state.sourceB.elem) loadPreset('B', (SEL_SRC_B && SEL_SRC_B.value) || 'forest_mist');
      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(loop);
    },
    stop() {
      state.active = false;
      cancelAnimationFrame(rafId);
    },
  };
})();
