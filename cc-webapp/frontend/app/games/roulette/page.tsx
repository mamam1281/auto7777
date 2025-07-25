'use client';

import { motion } from 'framer-motion';
import PrizeRoulette from '../../../components/games/roulette/PrizeRoulette';

function RouletteMainContent() {
  return (
    <div className="w-full bg-gradient-to-br from-[var(--color-primary-dark-navy)] via-[var(--color-primary-charcoal)] 
    to-[var(--color-primary-dark-navy)] min-h-screen flex flex-col items-center">
      <motion.header
        className="z-20 py-3 sm:py-4 px-4 sm:px-6 w-full bg-gradient-to-br from-[var(--color-primary-dark-navy)]/80 via-[var(--color-primary-charcoal)]/80 to-[var(--color-primary-dark-navy)]/80 backdrop-blur-md border-b border-[var(--border)]/20"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="max-w-6xl mx-auto flex flex-col items-center justify-center gap-2">
          <motion.h1
            className="text-4xl sm:text-6xl font-bold bg-gradient-to-r from-[var(--color-accent-red)] 
            via-[var(--color-accent-amber)] to-[var(--color-accent-red)] bg-clip-text text-transparent text-center tracking-wide"
            whileHover={{ scale: 1.02 }}
          >
            경품추첨 룰렛
          </motion.h1>
          <p className="text-[var(--text-secondary)] text-sm text-center">
            하루 3번까지 무료로 경품을 추첨해보세요!
          </p>
        </div>
      </motion.header>

      <div className="flex-1 w-full flex flex-col items-center justify-center p-4">
        <PrizeRoulette />
      </div>
    </div>
  );
}

export default function RoulettePage() {
  return <RouletteMainContent />;
}