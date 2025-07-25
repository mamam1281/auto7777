'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChoiceButtons } from './ChoiceButtons';
import OpponentDisplay from './OpponentDisplay';
import ResultScreen from './ResultScreen';
import { useRPSGame } from '../../../hooks/useRPSGame';
import './rps-compact-theme.css'; // 팝업 스타일도 함께 가져옵니다.

interface RPSGameProps {
  isPopup?: boolean;
}

const RPSGame: React.FC<RPSGameProps> = ({ isPopup = false }) => {
  const { gameState, handlePlayerChoice, handlePlayAgain, handleResetScore, isAIThinking, showPsychMessage } = useRPSGame(isPopup);

  const containerClassName = isPopup ? "rps-popup-container" : "rps-game-container mx-auto p-4 flex flex-col items-center justify-center";

  return (
    <div className={containerClassName}>
      <AnimatePresence mode="wait">
        {gameState.showResultScreen ? (
          <ResultScreen
            key="result"
            result={gameState.result}
            playerChoice={gameState.playerChoice}
            aiChoice={gameState.aiChoice}
            onPlayAgain={handlePlayAgain}
            onReset={handleResetScore}
            cjaiMessage={gameState.cjaiMessage}
            score={gameState.score}
            playerWinStreak={gameState.playerWinStreak}
            playerLossStreak={gameState.playerLossStreak}
            isPopup={isPopup}
          />
        ) : (
          <motion.div key="game" className="rps-game-area">
            <OpponentDisplay choice={gameState.aiChoice} isThinking={isAIThinking} />
            
            <div className="w-full my-4 border-t border-gray-600/50"></div>

            <div className="player-area">
              <AnimatePresence>
                <motion.p 
                  key={gameState.cjaiMessage}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  transition={{ duration: 0.3 }}
                  className="text-center text-sm text-gray-300 mb-3 h-8 flex items-center justify-center"
                >
                  {gameState.cjaiMessage}
                </motion.p>
              </AnimatePresence>
              
              <ChoiceButtons
                onChoice={handlePlayerChoice}
                selectedChoice={gameState.playerChoice}
                disabled={gameState.isPlaying}
                isPopup={isPopup}
              />
            </div>

            <div className={`absolute top-2 right-2 text-xs ${isPopup ? 'text-gray-400' : 'text-gray-500'}`}>
              <p>승: {gameState.score.player} | 패: {gameState.score.ai} | 무: {gameState.score.draws}</p>
              {gameState.playerWinStreak >= 2 && (
                <motion.p 
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="text-green-400 font-bold"
                >
                  🔥 {gameState.playerWinStreak}연승!
                </motion.p>
              )}
              {gameState.playerLossStreak >= 3 && (
                <motion.p 
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="text-red-400 font-bold"
                >
                  💪 반전 기회!
                </motion.p>
              )}
            </div>

            {/* AI 사고 중 표시 */}
            {isAIThinking && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute inset-0 flex items-center justify-center bg-black/50"
              >
                <motion.div
                  animate={{ 
                    rotate: [0, 360],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{ 
                    duration: 1,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                  className="bg-blue-500/90 text-white px-6 py-3 rounded-lg font-bold"
                >
                  🤖 AI 분석 중...
                </motion.div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RPSGame;
