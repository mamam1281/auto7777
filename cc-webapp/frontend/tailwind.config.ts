import type { Config } from 'tailwindcss'

const config: Config = {
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
        // 네온 컬러 팔레트
        'neon-cyan': '#00FFFF',
        'neon-pink': '#FF00FF',
        'neon-green': '#00FF00',
        'neon-blue': '#0080FF',
        'neon-purple': '#8000FF',
        'neon-orange': '#FF8000',
        'neon-yellow': '#FFFF00',
        
        // 카지노 컬러
        'casino-gold': '#FFD700',
        'casino-red': '#DC143C',
        'casino-green': '#228B22',
        'casino-blue': '#1E90FF',
        
        // 커스텀 컬러
        'gold': '#FFD700',
        'gold-soft': '#FFF8DC',
        'primary': '#8B5CF6',
        'primary-light': '#A78BFA',
        'primary-soft': '#EDE9FE',
        'secondary': '#6B7280',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'info': '#3B82F6',
        
        // 다크 테마
        'background': '#0A0A0A',
        'foreground': '#FFFFFF',
        'muted': '#374151',
        'muted-foreground': '#9CA3AF',
        'border': '#374151',
        'border-secondary': '#4B5563',
        
        // 게임 전용 컬러
        'game-bg': '#111827',
        'game-card': '#1F2937',
        'slot-gold': '#FFD700',
        'rps-blue': '#3B82F6',
        'gacha-purple': '#8B5CF6',
        'crash-red': '#EF4444',
      },
      gradientColorStops: {
        'gradient-primary': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
        'gradient-gold': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
        'gradient-game': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
        'gradient-success': 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
        'gradient-error': 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px currentColor' },
          '100%': { boxShadow: '0 0 20px currentColor, 0 0 30px currentColor' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      fontFamily: {
        'neon': ['Orbitron', 'sans-serif'],
        'casino': ['Playfair Display', 'serif'],
      },
      boxShadow: {
        'neon': '0 0 5px currentColor, 0 0 20px currentColor, 0 0 35px currentColor',
        'neon-lg': '0 0 10px currentColor, 0 0 40px currentColor, 0 0 80px currentColor',
        'gold': '0 0 10px #FFD700, 0 0 20px #FFD700, 0 0 40px #FFD700',
        'purple': '0 0 10px #8B5CF6, 0 0 20px #8B5CF6, 0 0 40px #8B5CF6',
        'glass': '0 8px 32px rgba(31, 38, 135, 0.37)',
      },
      backdropBlur: {
        'xs': '2px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
    },
  },
  plugins: [
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
  ],
}

export default config
