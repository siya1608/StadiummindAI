---
name: Apex Pitch
colors:
  surface: '#101415'
  surface-dim: '#101415'
  surface-bright: '#363a3b'
  surface-container-lowest: '#0b0f10'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#272a2c'
  surface-container-highest: '#323537'
  on-surface: '#e0e3e5'
  on-surface-variant: '#c3c6d6'
  inverse-surface: '#e0e3e5'
  inverse-on-surface: '#2d3133'
  outline: '#8d90a0'
  outline-variant: '#434654'
  surface-tint: '#b2c5ff'
  primary: '#b2c5ff'
  on-primary: '#002b73'
  primary-container: '#0052cc'
  on-primary-container: '#c4d2ff'
  inverse-primary: '#0c56d0'
  secondary: '#7dffa2'
  on-secondary: '#003918'
  secondary-container: '#05e777'
  on-secondary-container: '#00622e'
  tertiary: '#b1c7f2'
  on-tertiary: '#193053'
  tertiary-container: '#455b80'
  on-tertiary-container: '#bdd3ff'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dae2ff'
  primary-fixed-dim: '#b2c5ff'
  on-primary-fixed: '#001848'
  on-primary-fixed-variant: '#0040a2'
  secondary-fixed: '#62ff96'
  secondary-fixed-dim: '#00e475'
  on-secondary-fixed: '#00210b'
  on-secondary-fixed-variant: '#005226'
  tertiary-fixed: '#d6e3ff'
  tertiary-fixed-dim: '#b1c7f2'
  on-tertiary-fixed: '#001b3d'
  on-tertiary-fixed-variant: '#31476b'
  background: '#101415'
  on-background: '#e0e3e5'
  surface-variant: '#323537'
typography:
  headline-xl:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 2rem
  gutter: 1.5rem
  card-gap: 1rem
  section-margin: 3rem
---

## Brand & Style
The design system is engineered for the high-stakes, high-energy environment of the FIFA World Cup 2026. It targets stadium operators, security leads, and logistics coordinators who require immediate data clarity under pressure. 

The aesthetic is **Futuristic Glassmorphism**, blending the deep, atmospheric shadows of a night-lit stadium with hyper-modern digital overlays. The UI should evoke a sense of "Mission Control" for global sport—authoritative, high-tech, and immersive. By utilizing frosted glass textures and vibrant light-source highlights, the system maintains depth and hierarchy even within a data-dense dashboard environment.

## Colors
The palette is rooted in the "Stadium Night" experience. 

- **Primary (Electric Blue):** Used for interactive elements, primary actions, and active states. It represents the energy of the event.
- **Secondary (Stadium Grass Green):** Reserved for positive status indicators, "Live" markers, and success states. It provides a high-contrast pop against the dark base.
- **Tertiary (Deep Navy):** The foundation of the UI. This color is used for the background and base layers to minimize eye strain during long shifts.
- **Neutral (Whites/Grays):** Used strictly for high-readability text and subtle borders. 

Backgrounds use a radial gradient starting from `#002A5A` at the top center to `#001B3D` at the edges to simulate stadium floodlight falloff.

## Typography
The typography system prioritizes rapid scanning of metrics. 

- **Headlines:** Use Hanken Grotesk for its sharp, contemporary geometry. It feels athletic and authoritative.
- **Body:** Inter provides maximum legibility for operational notes and status descriptions.
- **Labels & Data:** Geist (monospaced qualities) is utilized for timestamps, seating coordinates, and fluctuating metrics to prevent "jumping" text as values change.

All headings should be high-contrast white, while body text should use a slightly muted gray (`#CBD5E1`) to maintain hierarchy.

## Layout & Spacing
The design system employs a **Fluid Grid** model with strict 8px increments. 

- **Desktop:** 12-column grid. Modules like "Pitch Heatmap" or "Crowd Flow" should span 8 columns, while "Metrics" sidebars span 4.
- **Tablet:** 6-column grid. Content stacks into a two-column primary layout.
- **Mobile:** 2-column grid. All complex data visualizations must revert to simplified "Key Metric" cards.

The "Glass" panels require a 24px padding internal to the card to prevent content from touching the luminous borders.

## Elevation & Depth
Depth is achieved through **Glassmorphism** rather than traditional drop shadows. 

1.  **Base Layer:** Solid Deep Navy (`#001B3D`).
2.  **Surface Layer (Cards):** Background-blur (20px to 40px) with a semi-transparent fill (`#FFFFFF` at 5% opacity).
3.  **Borders:** 1px solid stroke with a linear gradient (Top-Left: `#FFFFFF20` to Bottom-Right: `#FFFFFF05`). This creates a "rim light" effect on the glass.
4.  **Interactive Glow:** When an element is focused or active, apply a subtle outer glow using the Primary Electric Blue (`#0052CC`) with a 15px spread and 0.3 opacity.

## Shapes
The design system uses high-radius curves to soften the technical data and create a premium, organic feel.

- **Standard Containers:** `rounded-2xl` (1rem / 16px).
- **Primary Buttons/Inputs:** `rounded-xl` (0.75rem / 12px).
- **Status Pills:** Fully rounded (pill-shaped) to distinguish them from actionable buttons.
- **Interactive Graphs:** Line charts should use smooth bezier curves rather than jagged angles to align with the soft shape language.

## Components
- **Glass Cards:** The primary container. Must include a `backdrop-filter: blur(12px)` and a subtle inner glow.
- **Metric Chips:** Small, semi-transparent badges. For "Live" data, include a pulsing dot using the Stadium Grass Green.
- **Action Buttons:** Primary buttons are solid Electric Blue with white text. Secondary buttons are "Ghost" style with the 1px white-gradient border.
- **Data Inputs:** Darker than the card background (`#00000030`) to provide a "recessed" look. Use Geist for the input text.
- **Segmented Controls:** Used for switching between "Upper Tier," "Lower Tier," and "Pitch Level." These should look like physical toggles integrated into the glass.
- **Icons:** Use thin (1.5px) line weights. All icons should be encased in a subtle circular glass housing when used in navigation.
- **Live Feed HUD:** A specialized component for CCTV or drone footage, featuring an Electric Blue "scanning" corner bracket overlay.