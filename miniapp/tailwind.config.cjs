const tokens = require("../packages/design-tokens/tokens.json");

module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: tokens.color.bg,
        bg2: tokens.color.bg2,
        card: tokens.color.card,
        border: tokens.color.border,
        cyan: tokens.color.cyan,
        violet: tokens.color.violet,
        success: tokens.color.success,
        warning: tokens.color.warning,
        danger: tokens.color.danger,
        text: tokens.color.text,
        muted: tokens.color.muted,
      },
      fontFamily: {
        heading: ['Space Grotesk', 'Rajdhani', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      borderRadius: {
        card: tokens.radius.card,
        pill: tokens.radius.pill,
      },
      boxShadow: {
        glowCyan: '0 0 24px rgba(24,229,240,0.35)',
        glowViolet: '0 0 24px rgba(139,92,246,0.35)',
        card: '0 4px 20px rgba(0,0,0,0.35)',
      },
    },
  },
  plugins: [],
};
