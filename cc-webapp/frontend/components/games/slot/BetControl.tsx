'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Minus, Plus, Gem } from 'lucide-react';
import { cn } from '../../../utils/cn';

interface BetControlProps {
  betAmount: number;
  setBetAmount: (amount: number) => void;
  minBet?: number;
  maxBet: number;
  step?: number;
  quickBetOptions?: number[];
  disabled?: boolean;
  className?: string;
}

export const BetControl: React.FC<BetControlProps> = ({
  betAmount,
  setBetAmount,
  minBet = 5,
  maxBet,
  step = 5,
  quickBetOptions = [5, 10, 25, 50, 100],
  disabled = false,
  className = '',
}) => {
  const increaseBet = () => {
    setBetAmount(Math.min(betAmount + step, maxBet));
  };

  const decreaseBet = () => {
    setBetAmount(Math.max(betAmount - step, minBet));
  };

  const handleQuickBetSelect = (amount: number) => {
    if (amount <= maxBet && amount >= minBet) {
      setBetAmount(amount);
    } else if (amount > maxBet) {
      setBetAmount(maxBet);
    } else {
      setBetAmount(minBet);
    }
  };

  return (
    <div className={cn("w-full bg-gradient-to-br from-[var(--color-surface-primary)] to-[var(--color-surface-secondary)] rounded-2xl border border-[var(--color-border-primary)] py-[20px] px-8 sm:px-12 mx-auto", className)}>
      {/* Bet Amount Adjust Buttons & Display */}
      <div style={{ marginBottom: "50px" }}>
        <div style={{ marginBottom: "20px", textAlign: "center" }}>
          <h3 className="text-lg sm:text-xl font-semibold text-[var(--color-accent-amber)]">베팅 금액 조절</h3>
        </div>
      
        <div className="w-full flex items-center justify-center gap-4 sm:gap-6 mb-4">
          <motion.button
            onClick={decreaseBet}
            disabled={disabled || betAmount <= minBet}
            className={cn(
              "h-12 w-12 sm:h-14 sm:w-14 text-[var(--color-accent-amber)] rounded-xl shadow-xl transform transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-amber)]/50 disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed flex items-center justify-center",
              disabled || betAmount <= minBet 
                ? "bg-[var(--color-surface-tertiary)] border-2 border-[var(--color-border-secondary)]" 
                : "bg-gradient-to-b from-[var(--color-accent-amber)]/20 to-[var(--color-accent-amber)]/10 border-2 border-[var(--color-accent-amber)]/60 hover:from-[var(--color-accent-amber)]/30 hover:to-[var(--color-accent-amber)]/20 hover:border-[var(--color-accent-amber)]/80 active:scale-95"
            )}
            whileTap={!(disabled || betAmount <= minBet) ? { scale: 0.90 } : {}}
          >
            <Minus className="h-5 w-5 sm:h-6 sm:w-6" />
          </motion.button>

          <div className="text-center px-3 py-1 sm:px-8 sm:py-4 bg-gradient-to-r from-[var(--color-accent-amber)]/30 via-[var(--color-accent-yellow)]/30 to-[var(--color-accent-amber)]/30 border-2 border-[var(--color-accent-amber)]/50 rounded-2xl backdrop-blur-sm shadow-xl min-w-[160px] sm:min-w-[200px]">
            <div className="text-sm font-medium text-[var(--color-accent-amber)]/90 mb-1 tracking-wide">현재 베팅액</div>
            <div className="text-2xl sm:text-3xl font-bold text-[var(--color-text-primary)] flex items-center justify-center gap-2">
              <Gem size={20} className="opacity-80 inline-block" />
              {betAmount}
            </div>
          </div>

          <motion.button
            onClick={increaseBet}
            disabled={disabled || betAmount >= maxBet}
            className={cn(
              "h-12 w-12 sm:h-14 sm:w-14 text-[var(--color-accent-amber)] rounded-xl shadow-xl transform transition-all duration-150 ease-out focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-amber)]/50 disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed flex items-center justify-center",
              disabled || betAmount >= maxBet 
                ? "bg-[var(--color-surface-tertiary)] border-2 border-[var(--color-border-secondary)]" 
                : "bg-gradient-to-b from-[var(--color-accent-amber)]/20 to-[var(--color-accent-amber)]/10 border-2 border-[var(--color-accent-amber)]/60 hover:from-[var(--color-accent-amber)]/30 hover:to-[var(--color-accent-amber)]/20 hover:border-[var(--color-accent-amber)]/80 active:scale-95"
            )}
            whileTap={!(disabled || betAmount >= maxBet) ? { scale: 0.90 } : {}}
          >
            <Plus className="h-5 w-5 sm:h-6 sm:w-6" />
          </motion.button>
        </div>
      </div>

      {/* Quick Bet Options with Card Title */}
      <div className="w-full">
        <div style={{ marginBottom: "30px", textAlign: "center" }}>
          <h3 className="text-lg sm:text-xl font-semibold text-[var(--color-accent-amber)]">빠른 베팅 선택</h3>
        </div>
        
        <div className="w-full flex justify-center gap-2 sm:gap-3">{/* flex-wrap 제거하여 한 줄로 배치 */}
          {quickBetOptions.map((amount) => (
            <button
              key={amount}
              onClick={() => handleQuickBetSelect(amount)}
              disabled={disabled}
              className={cn(
                "text-sm sm:text-base px-2 py-2 min-w-[32px] h-10 rounded-lg border-2 font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
                betAmount === amount ? 
                  "bg-[var(--color-accent-red)] border-[var(--color-accent-red)] text-white" : 
                  "bg-transparent border-[var(--color-border-primary)] text-[var(--color-text-primary)] hover:border-[var(--color-accent-red)] hover:text-[var(--color-accent-red)]"
              )}
            >
              {amount}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BetControl;
