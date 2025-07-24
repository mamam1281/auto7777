'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star } from 'lucide-react';
import SlotReel from './SlotReel';

interface WinResult {
  isWin: boolean;
  payout: number;
  multiplier: number;
  winningPositions: number[];
  type: string;
}

interface SlotMachineMainProps {
  reels: string[];
  isSpinning: boolean;
  winResult: WinResult | null;
  className?: string;
}

export const SlotMachineMain: React.FC<SlotMachineMainProps> = ({
  reels,
  isSpinning,
  winResult,
  className = '',
}) => {
  return (
    <div className={`w-full bg-gradient-to-br from-[var(--color-surface-primary)] to-[var(--color-surface-secondary)] rounded-2xl border border-[var(--color-border-primary)] py-[20px] px-8 sm:px-12 mx-auto ${className}`}>
      {/* Slot Reels */}
      <div className="w-full flex justify-center mb-6">
        <div className="grid grid-cols-3 gap-6 sm:gap-8 h-40 sm:h-48 w-full max-w-md mx-auto">
          {reels.map((symbol, index) => (
            <SlotReel
              key={index}
              symbol={symbol}
              isSpinning={isSpinning}
              delayFactor={index * 0.3}
              isWinning={winResult?.isWin && winResult?.winningPositions?.includes(index)}
              className="bg-gradient-to-b from-[var(--color-surface-secondary)] to-[var(--color-surface-tertiary)] shadow-xl shadow-black/40 border-2 border-[var(--color-border-primary)] min-w-[100px] sm:min-w-[120px]"
            />
          ))}
        </div>
      </div>
      
      {/* Win Display */}
      <AnimatePresence>
        {winResult?.isWin && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.8 }}
            className="w-full text-center p-4 sm:p-6 bg-gradient-to-r from-[var(--color-accent-amber)]/30 to-[var(--color-accent-yellow)]/30 border-2 border-[var(--color-accent-amber)]/50 rounded-xl mx-auto"
          >
            <div className="flex items-center justify-center gap-3 text-[var(--color-accent-amber)] 
            text-xl sm:text-2xl font-bold mb-2">
              <Star className="w-6 h-6" />
              WIN! +{winResult.payout}
              <Star className="w-6 h-6" />
            </div>
            <div className="text-[var(--color-text-secondary)] text-base sm:text-lg">
              {winResult.multiplier}x multiplier
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SlotMachineMain;
