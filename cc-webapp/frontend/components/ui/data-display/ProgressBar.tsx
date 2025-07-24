'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  variant?: 'default' | 'gradient' | 'animated';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  className,
  variant = 'default',
  size = 'md',
  showLabel = false,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  const variantClasses = {
    default: 'bg-slate-700',
    gradient: 'bg-gradient-to-r from-blue-500 to-purple-500',
    animated: 'bg-gradient-to-r from-green-400 to-blue-500 animate-pulse',
  };

  return (
    <div className={cn('w-full', className)}>
      {showLabel && (
        <div className="flex justify-between text-sm text-slate-300 mb-1">
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
      <div className={cn(
        'w-full bg-slate-800 rounded-full overflow-hidden border border-slate-600',
        sizeClasses[size]
      )}>
        <div
          className={cn(
            'h-full transition-all duration-500 ease-out rounded-full',
            variantClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="text-xs text-slate-400 mt-1 text-right">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
