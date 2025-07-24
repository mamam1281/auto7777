'use client';

import React from 'react';
import Button from '../../Button';
import { Volume2, VolumeX } from 'lucide-react';

interface SlotMachineHeader2Props {
  balance: number;
  isSoundEnabled: boolean;
  setIsSoundEnabled: (enabled: boolean) => void;
  className?: string;
}

export const SlotMachineHeader2: React.FC<SlotMachineHeader2Props> = ({
  balance,
  isSoundEnabled,
  setIsSoundEnabled,
  className = '',
}) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className={`w-full bg-gradient-to-br from-[var(--color-surface-primary)] 
    to-[var(--color-surface-secondary)] rounded-2xl border border-[var(--color-border-primary)] 
    px-3 sm:px-6 mx-auto ${className}`} style={{ paddingBottom: '4px' }}>
      <div className="w-full flex items-center justify-center">
        <div className="w-full flex items-center justify-between">
          <div className="text-[var(--color-text-primary)] text-sm md:text-base font-medium opacity-90">
            Balance: <span className="text-[var(--color-accent-amber)] font-bold">{formatNumber(balance)}</span>
          </div>
          <Button
            variant="text"
            size="sm"
            onClick={() => setIsSoundEnabled(!isSoundEnabled)}
            className="text-[var(--color-text-primary)] hover:bg-white/10"
          >
            {isSoundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SlotMachineHeader2;
