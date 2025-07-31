import React from 'react';
import { motion } from 'framer-motion';

export interface QuickStartItemProps {
  id: string;
  label: string;
  iconBgColor: string;
  iconPlaceholder: string;
  onClick?: () => void;
}

export const QuickStartItem: React.FC<QuickStartItemProps> = ({
  id,
  label,
  iconBgColor,
  iconPlaceholder,
  onClick,
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
  };

  return (
    <motion.button
      className="group cursor-pointer w-full h-full focus:outline-none focus:ring-2 focus:ring-pink-400 focus:ring-opacity-75 rounded-2xl"
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      aria-label={`${label} 바로가기`}
      role="button"
      tabIndex={0}
    >
      <div
        className="relative rounded-2xl border transition-all duration-300 h-full"
        style={{
          padding: '20px 16px', // 더 균형잡힌 패딩
          background: 'linear-gradient(135deg, rgba(255, 182, 193, 0.4) 0%, rgba(255, 160, 200, 0.3) 30%, rgba(255, 192, 203, 0.25) 70%, rgba(230, 190, 255, 0.2) 100%)',
          border: '1px solid rgba(255, 182, 193, 0.5)',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1)', // 글로우 → 깊이감 있는 쉐도우
        }}
      >
        {/* 시각적 상태 표시 (색상 외 추가 정보) */}
        <div 
          className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 group-focus:opacity-100 transition-opacity duration-300"
          aria-hidden="true"
        >
          <div className="w-2 h-2 bg-white rounded-full shadow-lg"></div>
        </div>

        <div className="flex flex-col items-center justify-center h-full gap-4">
          {/* 아이콘 영역 - 크기와 위치 최적화 */}
          <motion.div
            className="flex items-center justify-center rounded-xl shadow-lg border border-white/20"
            style={{
              background: `linear-gradient(135deg, ${iconBgColor}88, ${iconBgColor}44)`,
              width: '56px', // 52px → 56px 약간 증가
              height: '56px',
              fontSize: '28px', // 26px → 28px 
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.25)' // 부드러운 쉐도우
            }}
            whileHover={{ rotate: 2, scale: 1.05 }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
            aria-hidden="true" // 장식적 요소이므로 스크린리더에서 제외
          >
            {iconPlaceholder}
          </motion.div>

          {/* 텍스트 영역 - 가독성과 균형 개선 */}
          <div className="text-center w-full">
            <span 
              className="font-semibold transition-colors duration-300 leading-tight block" 
              style={{ 
                fontSize: '14px', // 15px → 14px (아이콘과 더 균형잡힌 크기)
                lineHeight: '1.3', // 1.2 → 1.3 (더 여유로운 줄간격)
                color: 'rgba(255,255,255,0.95)',
                fontWeight: '600',
                wordBreak: 'keep-all', // 한글 단어 단위로 줄바꿈
                overflowWrap: 'break-word'
              }}
            >
              {label}
            </span>
            
            {/* 접근성을 위한 숨겨진 설명 텍스트 */}
            <span className="sr-only">
              {label} 기능으로 이동하려면 엔터키 또는 스페이스바를 누르세요
            </span>
          </div>
        </div>

        {/* 키보드 포커스를 위한 시각적 피드백 */}
        <div 
          className="absolute inset-0 rounded-2xl opacity-0 group-focus:opacity-100 transition-opacity duration-200 pointer-events-none"
          style={{
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 182, 193, 0.1) 100%)',
            border: '2px solid rgba(255, 182, 193, 0.6)'
          }}
          aria-hidden="true"
        />
      </div>
    </motion.button>
  );
};

export default QuickStartItem;
