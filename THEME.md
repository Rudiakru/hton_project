### Theme: JetBrains Devtools × Cloud9 Esports (Demo Mode)

#### Goal
Projector-friendly “professional esports + devtools” aesthetic: dark, crisp, high-contrast, minimal chrome, strong accent color, confident typography.

#### Palette (practical)
- Base background: `slate-950` / near-black gradients
- Surfaces: translucent panels `white/5` with subtle borders `white/10`
- Primary accent (Cloud9-leaning): Cyan/Sky
  - CTA / focus: `cyan-500` (hover `cyan-400`)
  - Secondary accents: `sky-600`, `indigo-600`, `violet-600`
- Status:
  - Verified/OK: `emerald-300`
  - Error/blocked: `rose-300` / `rose-950/60`

#### Typography
- UI text: system sans (Tailwind defaults)
- Tech labels + IDs: JetBrains Mono
  - Used for `evidence_id` chips, integrity metrics, hashes/timings
  - Loaded via `@fontsource/jetbrains-mono` (offline-friendly)

#### Layout & component rules
- Radius: 12–16px (`rounded-xl` / `rounded-2xl`)
- Borders: always subtle (`border-white/10`) rather than heavy outlines
- Shadows: soft and sparing; CTAs may use a faint colored shadow
- Tap targets: primary demo buttons are large (`px-5 py-3`) and high-contrast

#### Components (demo impact)
- Demo header
  - Shows “Offline / Deterministic / Verified” badges
  - Dataset scope callout: “Demo pack = 6 matches, baselines computed within pack”
- Demo route controls
  - One obvious path: `Start Demo` → `Next`
- Evidence drawer
  - Right-side devtools panel with match-scoped context, internal-only evidence (no external replay links)
- Scouting report cards
  - Clear hierarchy; confidence label uses mono and explains low confidence when `n=6`
- Integrity panel (“trust console”)
  - Mono metrics; `broken_refs` highlighted and expected to be `0` in the demo pack
