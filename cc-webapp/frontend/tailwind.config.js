/** @type {import('tailwindcss').Config} */
const config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // CSS 변수 기반 색상 (v4 호환)
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        card: {
          DEFAULT: 'var(--card)',
          foreground: 'var(--card-foreground)'
        },
        popover: {
          DEFAULT: 'var(--popover)',
          foreground: 'var(--popover-foreground)'
        },
        primary: {
          DEFAULT: 'var(--primary)',
          foreground: 'var(--primary-foreground)',
          hover: 'var(--primary-hover)',
          light: 'var(--primary-light)',
          dark: 'var(--primary-dark)',
          soft: 'var(--primary-soft)'
        },
        secondary: {
          DEFAULT: 'var(--secondary)',
          foreground: 'var(--secondary-foreground)',
          hover: 'var(--secondary-hover)'
        },
        muted: {
          DEFAULT: 'var(--muted)',
          foreground: 'var(--muted-foreground)'
        },
        accent: {
          DEFAULT: 'var(--accent)',
          foreground: 'var(--accent-foreground)'
        },
        destructive: {
          DEFAULT: 'var(--destructive)',
          foreground: 'var(--destructive-foreground)'
        },
        border: {
          DEFAULT: 'var(--border)',
          secondary: 'var(--border-secondary)'
        },
        input: {
          DEFAULT: 'var(--input)',
          background: 'var(--input-background)',
          border: 'var(--input-border)'
        },
        ring: 'var(--ring)',
        
        // 게임 특화 색상
        gold: {
          DEFAULT: 'var(--gold)',
          light: 'var(--gold-light)',
          dark: 'var(--gold-dark)',
          soft: 'var(--gold-soft)'
        },
        silver: {
          DEFAULT: 'var(--silver)',
          light: 'var(--silver-light)',
          dark: 'var(--silver-dark)',
          soft: 'var(--silver-soft)'
        },
        bronze: {
          DEFAULT: 'var(--bronze)',
          light: 'var(--bronze-light)',
          dark: 'var(--bronze-dark)',
          soft: 'var(--bronze-soft)'
        },
        emerald: {
          DEFAULT: 'var(--emerald)',
          light: 'var(--emerald-light)',
          dark: 'var(--emerald-dark)',
          soft: 'var(--emerald-soft)'
        },
        sapphire: {
          DEFAULT: 'var(--sapphire)',
          light: 'var(--sapphire-light)',
          dark: 'var(--sapphire-dark)',
          soft: 'var(--sapphire-soft)'
        },
        ruby: {
          DEFAULT: 'var(--ruby)',
          light: 'var(--ruby-light)',
          dark: 'var(--ruby-dark)',
          soft: 'var(--ruby-soft)'
        },
        // 추가 색상
        sky: {
          DEFAULT: 'var(--sky)',
          light: 'var(--sky-light)',
          dark: 'var(--sky-dark)',
          soft: 'var(--sky-soft)'
        },
        grass: {
          DEFAULT: 'var(--grass)',
          light: 'var(--grass-light)',
          dark: 'var(--grass-dark)',
          soft: 'var(--grass-soft)'
        },
        flame: {
          DEFAULT: 'var(--flame)',
          light: 'var(--flame-light)',
          dark: 'var(--flame-dark)',
          soft: 'var(--flame-soft)'
        },
        smoke: {
          DEFAULT: 'var(--smoke)',
          light: 'var(--smoke-light)',
          dark: 'var(--smoke-dark)',
          soft: 'var(--smoke-soft)'
        },
        // 상태 색상
        success: {
          DEFAULT: 'var(--success)',
          foreground: 'var(--success-foreground)',
          hover: 'var(--success-hover)',
          light: 'var(--success-light)',
          dark: 'var(--success-dark)',
          soft: 'var(--success-soft)'
        },
        warning: {
          DEFAULT: 'var(--warning)',
          foreground: 'var(--warning-foreground)',
          hover: 'var(--warning-hover)',
          light: 'var(--warning-light)',
          dark: 'var(--warning-dark)',
          soft: 'var(--warning-soft)'
        },
        error: {
          DEFAULT: 'var(--error)',
          foreground: 'var(--error-foreground)',
          hover: 'var(--error-hover)',
          light: 'var(--error-light)',
          dark: 'var(--error-dark)',
          soft: 'var(--error-soft)'
        },
        info: {
          DEFAULT: 'var(--info)',
          foreground: 'var(--info-foreground)',
          hover: 'var(--info-hover)',
          light: 'var(--info-light)',
          dark: 'var(--info-dark)',
          soft: 'var(--info-soft)'
        },
      },
    },
  },
  plugins: [],
}

export default config;
