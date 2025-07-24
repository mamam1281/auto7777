'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Choice, GameResult, GameScore } from './types';

interface ResultScreenProps {
  result: GameResult;
  playerChoice: Choice | null;
  aiChoice: Choice | null;
  onPlayAgain: () => void;
  onReset: () => void;
  cjaiMessage: string;
  score: GameScore;
  playerWinStreak: number;
  playerLossStreak: number;
  isPopup?: boolean;
}

const choiceEmojis: Record<Choice, string> = {
  rock: '🪨',
  paper: '📄',
  scissors: '✂️'
};

const choiceLabels: Record<Choice, string> = {
  rock: '🪨 바위',
  paper: '📄 보자기',
  scissors: '✂️ 가위'
};

const resultConfig = {
  win: {
    title: '✨ 대승리! ✨',
    message: '� 놀라운 실력이에요! 또 이겨볼까요? �',
    color: 'var(--casino-win-color, #ffd700)', /* 골드 컬러로 변경 */
    gradient: 'var(--casino-win-gradient, linear-gradient(135deg, #ffd700, #ffb700))',
    borderColor: 'var(--casino-win-border, #ffd700)'
  },
  lose: {
    title: '� 아쉬워요!',
    message: '� 단 한번만 더! 이번엔 이길 수 있어요! 🔥',
    color: 'var(--casino-lose-color, #ff5252)',
    gradient: 'var(--casino-lose-gradient, linear-gradient(135deg, #ff5252, #ff8a80))',
    borderColor: 'var(--casino-lose-border, #ff5252)'
  },
  draw: {
    title: '✋ 엇비슷한 실력!',
    message: '⚡ 한 번 더 하면 승부가 날 것 같아요! ⚡',
    color: 'var(--casino-draw-color, #7c4dff)',
    gradient: 'var(--casino-draw-gradient, linear-gradient(135deg, #7c4dff, #b388ff))',
    borderColor: 'var(--casino-draw-border, #7c4dff)'
  }
};

export const ResultScreen: React.FC<ResultScreenProps> = ({
  result,
  playerChoice,
  aiChoice,
  onPlayAgain,
  onReset,
  cjaiMessage,
  score,
  playerWinStreak,
  playerLossStreak,
  isPopup = false,
}) => {
  if (!result || !playerChoice || !aiChoice) return null;

  const config = resultConfig[result];

  const overlayVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.3 }
    },
    exit: {
      opacity: 0,
      transition: { duration: 0.2 }
    }
  };

  const modalVariants = {
    hidden: { 
      opacity: 0, 
      scale: isPopup ? 0.9 : 0.8, 
      y: isPopup ? 20 : 50,
      rotateX: isPopup ? 0 : -15
    },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      rotateX: 0,
      transition: {
        type: "spring" as const,
        stiffness: 300,
        damping: 25,
        duration: 0.5
      }
    },
    exit: {
      opacity: 0,
      scale: 0.8,
      y: -50,
      transition: { duration: 0.2 }
    }
  };

  const choiceVariants = {
    hidden: { opacity: 0, scale: 0.5, rotate: -180 },
    visible: (custom: number) => ({
      opacity: 1,
      scale: 1,
      rotate: 0,
      transition: {
        delay: custom * 0.1,
        type: "spring" as const,
        stiffness: 400,
        damping: 20
      }
    })
  };

  const buttonVariants = {
    hover: {
      scale: 1.05,
      y: -2,
      transition: { type: "spring" as const, stiffness: 400, damping: 25 }
    },
    tap: {
      scale: 0.95,
      transition: { type: "spring" as const, stiffness: 600, damping: 30 }
    }
  };

  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: "spring",
        damping: 15,
        stiffness: 200,
        when: "beforeChildren",
        staggerChildren: 0.1,
      }
    },
    exit: {
      opacity: 0,
      y: -50,
      transition: { duration: 0.2 }
    }
  };

  const containerClass = isPopup 
    ? "result-modal-popup bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-2xl w-full max-w-sm p-6 border border-gray-700/80"
    : "result-modal bg-gray-900/60 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-md p-8 border border-gray-700/50";

  return (
    <motion.div
      className="fixed inset-0 flex items-center justify-center z-50 p-2 result-overlay"
      variants={overlayVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
    >
      <motion.div
        className={`rounded-xl border shadow-xl max-w-sm w-full mx-2 min-h-[350px] result-modal-container result-${result}`}
        variants={modalVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        {/* Header */}
        <div className="text-center p-1 pb-1">
          <motion.h2
            className={`text-4xl sm:text-4xl font-bold mb-4 result-title-${result}`}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
          >
            {config.title}
          </motion.h2>
          <motion.p
            className="text-slate-300 font-semibold px-1 leading-relaxed"
            style={{ fontSize: '22px' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.4 }}
          >
            {cjaiMessage}
          </motion.p>
        </div>

        {/* Choices Display */}
        <div className="flex items-center justify-center px-4 py-4">
          <motion.div 
            className="text-center"
            variants={choiceVariants}
            initial="hidden"
            animate="visible"
            custom={0}
          >
            <div className="result-choice-icon rounded-xl bg-white/10 border border-white/20">
              {choiceEmojis[playerChoice!]}
            </div>
            <p className="text-xl sm:text-xl text-slate-300 font-bold">
              당신
            </p>
          </motion.div>

          <motion.div
            className={`result-vs-text result-vs-${result}`}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.3, type: "spring" as const }}
          >
            VS
          </motion.div>

          <motion.div 
            className="text-center"
            variants={choiceVariants}
            initial="hidden"
            animate="visible"
            custom={1}
          >
            <div className="result-choice-icon rounded-xl bg-white/10 border border-white/20">
              {choiceEmojis[aiChoice!]}
            </div>
            <p className="text-xl sm:text-xl text-slate-300 font-bold">
              AI
            </p>
          </motion.div>
        </div>

        {/* Stats Display */}
        <div className="px-4 py-3 text-white text-center">
          <div className="flex justify-around items-center bg-white/5 rounded-lg p-2">
            <div>
              <span className="text-sm text-slate-400">승리</span>
              <p className="font-bold text-lg">{score.player}</p>
            </div>
            <div>
              <span className="text-sm text-slate-400">패배</span>
              <p className="font-bold text-lg">{score.ai}</p>
            </div>
            <div>
              <span className="text-sm text-slate-400">무승부</span>
              <p className="font-bold text-lg">{score.draws}</p>
            </div>
            {playerWinStreak > 1 && (
              <div>
                <span className="text-sm text-slate-400">연승</span>
                <p className="font-bold text-lg text-yellow-400">{playerWinStreak} 🔥</p>
              </div>
            )}
            {playerLossStreak > 1 && (
              <div>
                <span className="text-sm text-slate-400">연패</span>
                <p className="font-bold text-lg text-red-400">{playerLossStreak} 💧</p>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col items-center gap-3 p-4 pt-3">
          <motion.button
            className={`inline-block py-3 px-6 rounded-lg font-bold transition-all duration-200 text-lg result-btn result-btn-${result}`}
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            onClick={onPlayAgain}
          >
            🔄 다시 플레이
          </motion.button>
          <button
            onClick={onReset}
            className="text-xs text-gray-400 hover:text-white transition-colors duration-200 mt-3 opacity-70 hover:opacity-100 border border-gray-600 py-1 px-3 rounded-md"
          >
            점수 초기화
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ResultScreen;
