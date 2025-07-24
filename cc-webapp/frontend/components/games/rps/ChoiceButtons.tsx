'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { Choice } from './types';

interface ChoiceButtonsProps {
  onChoice: (choice: Choice) => void;
  selectedChoice: Choice | null;
  disabled: boolean;
  isPopup?: boolean;
}

const choiceConfig = {
  rock: { emoji: '🪨', label: '바위' },
  paper: { emoji: '📄', label: '보' },
  scissors: { emoji: '✂️', label: '가위' }
};

const choices: Choice[] = ['rock', 'paper', 'scissors'];

export const ChoiceButtons: React.FC<ChoiceButtonsProps> = ({
  onChoice,
  selectedChoice,
  disabled,
  isPopup = false
}) => {
  const containerClass = "choice-buttons-container";
  const buttonClass = isPopup ? "choice-button-popup" : "choice-button-normal";

  const buttonVariants = {
    initial: (index: number) => ({
      opacity: 0,
      y: 30,
      scale: 0.8,
      transition: { 
        delay: index * 0.15,
      }
    }),
    animate: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { 
        duration: 0.6,
        type: "spring" as const, 
        stiffness: 280, 
        damping: 20
      }
    },
    hover: {
      scale: 1.08,
      y: -6,
      transition: { 
        duration: 0.3,
        type: "spring" as const,
        stiffness: 400,
        damping: 15
      }
    },
    tap: { 
      scale: 0.95,
      y: 2,
      transition: { 
        duration: 0.15,
        type: "tween" as const 
      }
    },
    selected: {
      scale: [1, 1.15, 1.1],
      boxShadow: [
        "0px 0px 0px rgba(255,199,0,0)", 
        "0px 0px 35px rgba(255,199,0,0.9)", 
        "0px 0px 25px rgba(255,199,0,0.7)"
      ],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        repeatType: "reverse" as const
      }
    }
  };

  return (
    <div className={containerClass}>
      {choices.map((choice, index) => {
        const config = choiceConfig[choice];
        const isSelected = selectedChoice === choice;
        
        return (
          <motion.button
            key={choice}
            custom={index}
            variants={buttonVariants}
            initial="initial"
            animate={isSelected ? "selected" : "animate"}
            whileHover={disabled ? {} : "hover"}
            whileTap={disabled ? {} : "tap"}
            className={`${buttonClass} ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onChoice(choice)}
            disabled={disabled}
          >
            <div className="icon">{config.emoji}</div>
            <div className="text">{config.label}</div>
          </motion.button>
        );
      })}
    </div>
  );
};

export default ChoiceButtons;
