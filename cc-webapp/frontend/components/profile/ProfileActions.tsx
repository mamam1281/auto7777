'use client';

import { Settings, ExternalLink } from 'lucide-react';
import type { ProfileActionsProps } from './types';

export default function ProfileActions({ onLogout }: ProfileActionsProps) {
  const handleSettings = () => {
    console.log('Opening settings...');
    // Navigate to settings page
  };

  const handleVisitSite = () => {
    console.log('Visiting main site...');
    // Open main company site
    window.open('https://casinoclub.com', '_blank');
  };

  return (
    <div className="space-y-4">
      {/* 본사 사이트 바로가기 - 핑크 테마로 변경 */}
      <div className="rounded-xl p-8 relative overflow-hidden bg-black/60 backdrop-blur-sm border border-pink-500/30 shadow-xl w-full"
        style={{
          maxWidth: '100% !important',
          width: '100% !important',
          padding: '32px !important',
          background: 'linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(26,26,26,0.6) 50%, rgba(0,0,0,0.8) 100%)',
          borderColor: 'rgba(236, 72, 153, 0.3)',
          boxShadow: '0 8px 32px rgba(236, 72, 153, 0.15)'
        }}>
        <div className="absolute inset-0 bg-gradient-to-br from-pink-900/20 via-transparent to-pink-800/15 pointer-events-none" />
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-pink-500/20 to-transparent rounded-full filter blur-3xl" />

        <div className="relative z-10 text-center space-y-4">
          <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-pink-600 rounded-full 
                         flex items-center justify-center mx-auto shadow-lg border-2 border-pink-400/30">
            <ExternalLink className="w-8 h-8 text-white" />
          </div>

          <div className="space-y-2">
            <h3 className="text-lg font-bold text-white">모델 사이트</h3>
            <p className="text-sm text-pink-200">모델 공식 사이트로 이동</p>
          </div>

          <button
            onClick={handleVisitSite}
            className="w-full h-12 rounded-lg text-white font-bold transform hover:scale-105 active:scale-95 transition-all duration-200
                       shadow-lg hover:shadow-xl"
            style={{
              background: 'linear-gradient(to right, #ec4899, #be185d)',
              border: '2px solid rgba(236, 72, 153, 0.3)',
              borderRadius: '0.5rem'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'linear-gradient(to right, #f472b6, #db2777)';
              e.currentTarget.style.borderColor = 'rgba(236, 72, 153, 0.5)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'linear-gradient(to right, #ec4899, #be185d)';
              e.currentTarget.style.borderColor = 'rgba(236, 72, 153, 0.3)';
            }}
          >
            모델 사이트 바로가기
          </button>
        </div>
      </div>
    </div>
  );
}
