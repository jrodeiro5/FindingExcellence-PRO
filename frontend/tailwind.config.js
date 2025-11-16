export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      colors: {
        // Geist Background Colors
        background: {
          1: 'var(--background-1)',
          2: 'var(--background-2)',
        },
        // Geist Gray Scale (1-10)
        gray: {
          1: 'var(--gray-1)',
          2: 'var(--gray-2)',
          3: 'var(--gray-3)',
          4: 'var(--gray-4)',
          5: 'var(--gray-5)',
          6: 'var(--gray-6)',
          7: 'var(--gray-7)',
          8: 'var(--gray-8)',
          9: 'var(--gray-9)',
          10: 'var(--gray-10)',
        },
        // Geist Blue Scale (Primary/Interactive)
        blue: {
          1: 'var(--blue-1)',
          2: 'var(--blue-2)',
          3: 'var(--blue-3)',
          4: 'var(--blue-4)',
          5: 'var(--blue-5)',
          6: 'var(--blue-6)',
          7: 'var(--blue-7)',
          8: 'var(--blue-8)',
          9: 'var(--blue-9)',
          10: 'var(--blue-10)',
        },
      },
      borderRadius: {
        'geist-sm': '8px',
        'geist-md': '12px',
        'geist-lg': '16px',
      },
      boxShadow: {
        'geist-tooltip': 'var(--shadow-tooltip)',
        'geist-menu': 'var(--shadow-menu)',
        'geist-modal': 'var(--shadow-modal)',
        'geist-fullscreen': 'var(--shadow-fullscreen)',
      },
      fontSize: {
        // Geist Typography Scale
        'heading-72': ['72px', { lineHeight: '1', fontWeight: '700' }],
        'heading-48': ['48px', { lineHeight: '1.1', fontWeight: '700' }],
        'heading-32': ['32px', { lineHeight: '1.2', fontWeight: '600' }],
        'heading-24': ['24px', { lineHeight: '1.3', fontWeight: '600' }],
        'heading-20': ['20px', { lineHeight: '1.4', fontWeight: '600' }],
        'heading-18': ['18px', { lineHeight: '1.4', fontWeight: '600' }],
        'heading-16': ['16px', { lineHeight: '1.5', fontWeight: '600' }],
        'heading-14': ['14px', { lineHeight: '1.5', fontWeight: '600' }],

        // Buttons
        'button-16': ['16px', { lineHeight: '1.5', fontWeight: '500' }],
        'button-14': ['14px', { lineHeight: '1.5', fontWeight: '500' }],
        'button-12': ['12px', { lineHeight: '1.5', fontWeight: '500' }],

        // Labels (Single-line)
        'label-20': ['20px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-18': ['18px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-16': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-14': ['14px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-13': ['13px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-12': ['12px', { lineHeight: '1.6', fontWeight: '400' }],

        // Copy (Multi-line)
        'copy-24': ['24px', { lineHeight: '1.7', fontWeight: '400' }],
        'copy-20': ['20px', { lineHeight: '1.7', fontWeight: '400' }],
        'copy-18': ['18px', { lineHeight: '1.7', fontWeight: '400' }],
        'copy-16': ['16px', { lineHeight: '1.7', fontWeight: '400' }],
        'copy-14': ['14px', { lineHeight: '1.7', fontWeight: '400' }],
        'copy-13': ['13px', { lineHeight: '1.7', fontWeight: '400' }],
      },
      transitionTimingFunction: {
        'geist': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      transitionDuration: {
        'geist': '150ms',
      },
      spacing: {
        '0.5': '2px',
        '1': '4px',
        '1.5': '6px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
        '24': '96px',
      },
    },
  },
  plugins: [],
}
