/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./code.html"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        "surface-container-high": "#272a2c",
        "surface-container-lowest": "#0b0f10",
        "primary-fixed": "#dae2ff",
        "primary": "#b2c5ff",
        "inverse-surface": "#e0e3e5",
        "background": "#101415",
        "on-secondary-fixed-variant": "#005226",
        "secondary-fixed-dim": "#00e475",
        "on-error-container": "#ffdad6",
        "surface-tint": "#b2c5ff",
        "inverse-primary": "#0c56d0",
        "inverse-on-surface": "#2d3133",
        "secondary": "#7dffa2",
        "surface-container": "#1d2022",
        "outline": "#8d90a0",
        "surface-variant": "#323537",
        "on-surface": "#e0e3e5",
        "on-primary-fixed": "#001848",
        "primary-container": "#0052cc",
        "on-primary-fixed-variant": "#0040a2",
        "tertiary-container": "#455b80",
        "surface": "#101415",
        "primary-fixed-dim": "#b2c5ff",
        "on-secondary-container": "#00622e",
        "on-tertiary-container": "#bdd3ff",
        "on-secondary-fixed": "#00210b",
        "tertiary-fixed-dim": "#b1c7f2",
        "tertiary-fixed": "#d6e3ff",
        "on-primary-container": "#c4d2ff",
        "tertiary": "#b1c7f2",
        "on-background": "#e0e3e5",
        "surface-dim": "#101415",
        "on-tertiary": "#193053",
        "error": "#ffb4ab",
        "on-surface-variant": "#c3c6d6",
        "on-secondary": "#003918",
        "secondary-fixed": "#62ff96",
        "on-error": "#690005",
        "on-tertiary-fixed": "#001b3d",
        "error-container": "#93000a",
        "surface-container-highest": "#323537",
        "secondary-container": "#05e777",
        "on-tertiary-fixed-variant": "#31476b",
        "surface-container-low": "#191c1e",
        "on-primary": "#002b73",
        "surface-bright": "#363a3b",
        "outline-variant": "#434654"
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
      spacing: {
        "section-margin": "3rem",
        "gutter": "1.5rem",
        "container-padding": "2rem",
        "card-gap": "1rem"
      },
      fontFamily: {
        "body-md": ["Inter"],
        "data-mono": ["Geist"],
        "headline-lg-mobile": ["Hanken Grotesk"],
        "body-sm": ["Inter"],
        "label-caps": ["Geist"],
        "headline-xl": ["Hanken Grotesk"],
        "headline-lg": ["Hanken Grotesk"]
      },
      fontSize: {
        "body-md": ["16px", {"lineHeight": "24px", "fontWeight": "400"}],
        "data-mono": ["18px", {"lineHeight": "24px", "fontWeight": "700"}],
        "headline-lg-mobile": ["24px", {"lineHeight": "32px", "fontWeight": "700"}],
        "body-sm": ["14px", {"lineHeight": "20px", "fontWeight": "400"}],
        "label-caps": ["12px", {"lineHeight": "16px", "letterSpacing": "0.05em", "fontWeight": "600"}],
        "headline-xl": ["48px", {"lineHeight": "56px", "letterSpacing": "-0.02em", "fontWeight": "800"}],
        "headline-lg": ["32px", {"lineHeight": "40px", "letterSpacing": "-0.01em", "fontWeight": "700"}]
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries')
  ],
}
