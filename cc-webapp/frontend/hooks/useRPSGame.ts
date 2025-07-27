'use client';

import { useState, useCallback } from 'react';
import { Choice, GameResult, GameScore, GameState } from '../components/games/rps/types';

export const useRPSGame = (isPopup = false) => {
  const [gameState, setGameState] = useState<GameState>({
    playerChoice: null,
    aiChoice: null,
    result: null,
    isPlaying: false, // 계속 false로 유지됩니다 (호환성을 위해 유지)
    score: { player: 0, ai: 0, draws: 0 },
    showResultScreen: false,
    cjaiMessage: isPopup 
      ? "게임을 시작해 보세요! 행운을 빌어요! 🚀"
      : "가위, 바위, 보 중 하나를 선택하세요!",
    playerWinStreak: 0,
    playerLossStreak: 0,
  });

  // 심리적 효과를 위한 추가 상태
  const [isAIThinking, setIsAIThinking] = useState(false);
  const [showPsychMessage, setShowPsychMessage] = useState(false);

  // 프론트 승률/결과 결정 로직 분리
  const WINNING_COMBINATIONS = {
    rock: 'scissors',
    paper: 'rock',
    scissors: 'paper',
  };
  const getWinningChoice = (userChoice: Choice): Choice => {
    if (userChoice === 'rock') return 'paper';
    if (userChoice === 'paper') return 'scissors';
    return 'rock';
  };

  // 실제 승률/표시 승률, streak 등 UX 제어
  const getAIChoiceAndResult = (userChoice: Choice, streak: number): { aiChoice: Choice, result: GameResult } => {
    // 예시: 3연승 시 강제 패배, 실제 승률 30%, 무승부 10%, 패배 60%
    if (streak >= 3) {
      return { aiChoice: getWinningChoice(userChoice), result: 'lose' };
    }
    const rand = Math.random();
    if (rand < 0.3) {
      // 승리
      return { aiChoice: WINNING_COMBINATIONS[userChoice] as Choice, result: 'win' };
    } else if (rand < 0.4) {
      // 무승부
      return { aiChoice: userChoice, result: 'draw' };
    } else {
      // 패배
      return { aiChoice: getWinningChoice(userChoice), result: 'lose' };
    }
  };

  const handlePlayerChoice = useCallback((choice: Choice) => {
    if (gameState.isPlaying || isAIThinking) return;
    setIsAIThinking(true);
    setGameState(prev => ({
      ...prev,
      playerChoice: choice,
      cjaiMessage: "🤖 AI가 전략을 분석 중..."
    }));

    setTimeout(() => {
      // 프론트 승률/결과 결정
      const { aiChoice, result } = getAIChoiceAndResult(choice, gameState.playerWinStreak);

      // 점수 및 상태 업데이트
      const newScore = { ...gameState.score };
      const newWinStreak = result === 'win' ? gameState.playerWinStreak + 1 : 0;
      const newLossStreak = result === 'lose' ? gameState.playerLossStreak + 1 : 0;
      if (result === 'win') newScore.player++;
      else if (result === 'lose') newScore.ai++;
      else newScore.draws++;

      // 심리적 메시지
      let message = "좋은 게임이었어요! 🎮";
      if (result === 'win') {
        if (newWinStreak >= 3) message = "🔥 연승 중이에요! 이 기세를 계속 이어가세요!";
        else message = "🎉 승리했어요! 한 번 더 도전해보세요!";
      } else if (result === 'lose') {
        if (newLossStreak >= 3) message = "😅 패턴을 바꿔보세요! 반전의 기회가 올 거예요!";
        else message = "😔 아쉽네요... 다음엔 이길 수 있어요!";
      } else {
        message = "🤝 무승부! 이번엔 승부를 가려보세요!";
      }

      setGameState(prev => ({
        ...prev,
        playerChoice: choice,
        aiChoice: aiChoice,
        result: result,
        isPlaying: false,
        score: newScore,
        showResultScreen: true,
        cjaiMessage: message,
        playerWinStreak: newWinStreak,
        playerLossStreak: newLossStreak,
      }));
      setIsAIThinking(false);

      // 백엔드 연동: 결과/보상 저장 (선택적)
      // fetch('/api/games/rps/play', { method: 'POST', body: JSON.stringify({ choice, bet_amount: 0 }) ... })
      // .then(res => res.json()).then(data => { /* 토큰, 잔고 등 상태 업데이트 */ })
    }, 1500);
  }, [gameState.isPlaying, gameState.score, gameState.playerWinStreak, gameState.playerLossStreak, isAIThinking]);

  const handlePlayAgain = useCallback(() => {
    setGameState(prev => ({
      ...prev,
      playerChoice: null,
      aiChoice: null,
      result: null,
      isPlaying: false,
      showResultScreen: false,
      cjaiMessage: "선택하시면 바로 결과가 나옵니다! 🎯",
    }));
  }, []);

  const handleResetScore = useCallback(() => {
    setGameState(prev => ({
      ...prev,
      playerChoice: null,
      aiChoice: null,
      result: null,
      isPlaying: false,
      score: { player: 0, ai: 0, draws: 0 },
      showResultScreen: false,
      cjaiMessage: "새로운 시작이에요! 화이팅! 🚀",
      playerWinStreak: 0,
      playerLossStreak: 0,
    }));
  }, []);

  return {
    gameState,
    handlePlayerChoice,
    handlePlayAgain,
    handleResetScore,
    isAIThinking,
    showPsychMessage,
  };
};
