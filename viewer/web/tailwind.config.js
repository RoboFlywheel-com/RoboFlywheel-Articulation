// SPDX-License-Identifier: Apache-2.0

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["DM Sans", "system-ui", "-apple-system", "sans-serif"],
        mono: ["IBM Plex Mono", "SF Mono", "Consolas", "monospace"],
      },
      colors: {
        background: "#ffffff",
        foreground: "#111111",
      },
      // Tailwind v4 parity: bare `border`/`ring` default to currentColor, bare `ring` is 1px
      borderColor: {
        DEFAULT: "currentColor",
      },
      ringWidth: {
        DEFAULT: "1px",
      },
      ringColor: {
        DEFAULT: "currentColor",
      },
    },
  },
  plugins: [],
};
