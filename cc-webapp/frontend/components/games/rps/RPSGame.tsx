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
  const { gameState, handlePlayerChoice, handlePlayAgain, handleResetScore } = useRPSGame(isPopup);

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
            <OpponentDisplay choice={gameState.aiChoice} isThinking={false} />
            
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
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default RPSGame;
