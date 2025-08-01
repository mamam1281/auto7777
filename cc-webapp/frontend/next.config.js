/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  experimental: {
    // turbo 관련 실험적 기능 비활성화
    turbo: {
      resolveAlias: {
        // 폰트 문제 해결을 위한 alias
        '@vercel/turbopack-next/internal/font/google/font': './public/fonts'
      }
    }
  },
  // 폰트 최적화 설정
  optimizeFonts: false
};

module.exports = nextConfig;
