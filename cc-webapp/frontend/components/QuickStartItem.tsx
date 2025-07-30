import React from 'react';
import { motion } from 'framer-motion';

export interface QuickStartItemProps {
  id: string;
  label: string;
  iconBgColor: string; // 이제 Tailwind 클래스를 받습니다
  iconPlaceholder: string;
  onClick?: () => void;
}

export const QuickStartItem: React.FC<QuickStartItemProps> = ({
  label,
  iconBgColor,
  iconPlaceholder,
  onClick,
}) => (
  <motion.div
    className="group cursor-pointer"
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    transition={{ type: "spring", stiffness: 300, damping: 25 }}
    onClick={onClick}
  >
    <div
      className="relative rounded-2xl p-4 border border-pink-300/20 transition-all duration-300"
      style={{
        height: '200px',
        maxHeight: '200px',
        minWidth: '120px',
        background: 'linear-gradient(135deg, rgba(236,72,153,0.15) 0%, rgba(236,72,153,0.08) 50%, rgba(0,0,0,0.95) 100%)',
        boxShadow: '0 8px 32px rgba(236, 72, 153, 0.2), inset 0 1px 0 rgba(236,72,153,0.2), inset 0 -1px 0 rgba(236,72,153,0.1)',
        border: '1px solid rgba(236, 72, 153, 0.25)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(236,72,153,0.25) 0%, rgba(236,72,153,0.15) 50%, rgba(0,0,0,0.85) 100%)';
        e.currentTarget.style.boxShadow = '0 0 25px rgba(236, 72, 153, 0.4), 0 12px 40px rgba(236, 72, 153, 0.3), inset 0 1px 0 rgba(236,72,153,0.3)';
        e.currentTarget.style.border = '1px solid rgba(236, 72, 153, 0.4)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = 'linear-gradient(135deg, rgba(236,72,153,0.15) 0%, rgba(236,72,153,0.08) 50%, rgba(0,0,0,0.95) 100%)';
        e.currentTarget.style.boxShadow = '0 8px 32px rgba(236, 72, 153, 0.2), inset 0 1px 0 rgba(236,72,153,0.2), inset 0 -1px 0 rgba(236,72,153,0.1)';
        e.currentTarget.style.border = '1px solid rgba(236, 72, 153, 0.25)';
      }}
    >
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <motion.div
          className="flex items-center justify-center rounded-lg shadow-lg border"
          style={{
            background: `linear-gradient(135deg, ${iconBgColor}CC, ${iconBgColor}88)`,
            width: '52px',
            height: '52px',
            fontSize: '26px',
            boxShadow: `0 0 15px ${iconBgColor}66, 0 4px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.3)`,
            border: `1px solid ${iconBgColor}AA`
          }}
          whileHover={{ rotate: 2, scale: 1.05 }}
          transition={{ type: "spring", stiffness: 250, damping: 20 }}
        >
          {iconPlaceholder}
        </motion.div>
        <span className="text-center font-semibold transition-colors duration-300" style={{
          fontSize: '15px',
          lineHeight: '1.2',
          color: '#ffffff',
          fontWeight: '600',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          maxWidth: '100%',
          textShadow: '0 2px 8px rgba(255, 20, 147, 0.3)'
        }}>
          {label}
        </span>
      </div>
    </div>
  </motion.div>
);

export default QuickStartItem;
