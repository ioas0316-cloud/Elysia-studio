# Universal Scale-Rotor Form Principle (범용 스케일 로터 형태 원리)

## 1. Core Axiom: One Form Grammar Across All Modalities
Every living, physical, linguistic, acoustic, visual, 3D-skeletal, and architectural phenomenon inside Elysia shares ONE irreducible generating form:

$$\Phi(t; \mathbf{u}) = \mathcal{B}_{\text{ice}} \otimes \mathcal{R}\big(\omega(u_{\text{tempo}})\, t + \phi(u_{\text{phase}}),\; \alpha(u_{\text{scale}}),\; \gamma(u_{\text{damping}})\big) \oplus \sum_{k=1}^{K} \kappa_k\, G_\sigma(t - t_k)$$

1. **Static Ice Base ($\mathcal{B}_{\text{ice}}$, $t=0$ Invariant):** The structural identity that does NOT need recomputation per frame (e.g., Korean nominal/predicate root skeleton, speaker neutral vocal-tract envelope, 3D rigged character rest skeleton, background scene DC spectrum).
2. **Continuous Form Operator ($\mathcal{R}(\mathbf{u})$, Water Flow):** Orthogonal continuous knobs acting on the same rotor algebra across domains:
   - `vertical_scale` ($u_v \in [0, 1]$): Micro analytic precision (Scale 0–2, Blue Order) ↔ Macro aesthetic gestalt (Scale 3–4, Red/Yellow Flux).
   - `horizontal_relational` ($u_h \in [-1, 1]$): Shy / high boundary distance ↔ Composed ↔ Theatrical / high contrast flip.
   - `tempo_rate` ($u_\omega \in [0.4, 2.2]$): Continuous temporal rotor frequency scaling.
   - `pitch_f0` ($u_{F0} \in [0.65, 1.50]$): Fundamental frequency / vocal fold oscillation axis (Elder ↔ Child).
   - `formant_tract` ($u_{\text{tract}} \in [0.75, 1.30]$): Vocal-tract length / spectral envelope scaling (Masculine low resonance ↔ Feminine bright resonance — **strictly orthogonal to F0 and linguistic stance**).
   - `law_damping` ($u_\gamma \in [-0.6, 0.8]$): Self-excitation ($<0$) ↔ Conservation ($0$) ↔ Viscous damping ($>0$).
3. **Sparse Event Knots ($\sum \kappa_k G_\sigma(t - t_k)$, Cloud → Water Boundary):** Residual impulses harvested strictly where continuous prediction mismatches reality (scene cuts, plosive consonants, sudden gaze turns, logical contradictions).

## 2. Open-Source External Organs as Sensory/Motor Transducers (Not Wrappers)
External open-source libraries are NEVER used as opaque black-box wrappers. They serve as high-precision **S0–S2 physical receptors/actuators** feeding and executing the Universal Form Rotor:
- **Korean Morphosyntactic Receptor (`kiwipiepy`):** Decomposes raw spoken/written Korean (including colloquial YouTube transcripts) into exact POS-verified nominals (`NNG/NNP`), verbal predicates (`VV/VA`), case particles (`JKS/JKO/JKB`), and endings (`EF/EC`) for `ScaleRotorHierarchy` & `LanguageScaleRotor`.
- **Vocal-Tract & F0 Acoustic Actuator (`praat-parselmouth` / LPC-Phase Vocoder):** Separates vocal-tract formant length ($u_{\text{tract}}$) from fundamental pitch ($u_{F0}$) and speaking cadence ($u_\omega$), enabling true cross-axis character voices (e.g., masculine vocal tract × gentle feminine stance).
- **Real-World Motion DNA Receptor & 3D Rig Actuator (`MediaPipe` / OpenCV Optical-Kinematic Landmarks → `Blender 5.3`):** Extracts real head yaw/pitch/roll, gaze drift, and body rhythm from real YouTube videos into a `UniversalFormRotor`, then transfers that exact dynamic signature onto a rigged 3D character (`CesiumMan.glb` / `Fox.glb`) coupled with voice and language.

## 3. Bidirectional Self-Verification & Cross-Domain Transfer
A form principle is valid ONLY when:
1. It can **re-create** real outputs (Korean utterances, `.wav` voices, `.mp4` videos, 3D rigged frames) from the compact Form Rotor;
2. It can **transfer** extracted form dynamics (`tempo`, `damping`, `event_knots`) across domains (e.g. YouTube motion DNA → 3D rig + vocal prosody envelope);
3. It **re-observes** its own outputs blindly and measures real residual error (`RMSE`, `Whisper STT`, `AudioStreamTrace`, `CodeArchitectureLens`).
