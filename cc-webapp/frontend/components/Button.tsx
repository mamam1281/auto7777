import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'accent' | 'success' | 'error' | 'info' | 'outline' | 'text' | 'neon' | 'glass' | 'animated';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  iconOnly?: boolean;
  rounded?: boolean;
  disabled?: boolean;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  className?: string;
  children?: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  type?: 'button' | 'submit' | 'reset';
  ripple?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  iconOnly = false,
  rounded = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className = '',
  children,
  onClick,
  type = 'button',
  ripple = false,
}) => {
  const [coords, setCoords] = React.useState({ x: -1, y: -1 });
  const [isRippling, setIsRippling] = React.useState(false);
  
  React.useEffect(() => {
    if (coords.x !== -1 && coords.y !== -1) {
      setIsRippling(true);
      setTimeout(() => setIsRippling(false), 600);
    } else {
      setIsRippling(false);
    }
  }, [coords]);

  React.useEffect(() => {
    if (!isRippling) setCoords({ x: -1, y: -1 });
  }, [isRippling]);
  
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (ripple && !disabled) {
      const rect = e.currentTarget.getBoundingClientRect();
      setCoords({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
    if (onClick) onClick(e);
  };

  // 크기별 스타일 매핑
  const sizeStyles = {
    xs: { height: '32px', padding: '8px 12px', fontSize: '12px' },
    sm: { height: '36px', padding: '10px 16px', fontSize: '13px' },
    md: { height: '44px', padding: '12px 20px', fontSize: '14px' },
    lg: { height: '56px', padding: '16px 32px', fontSize: '16px' },
  };

  // 변형별 스타일 매핑 - 2025 Neumorphism/Clay UI 트렌드
  const variantStyles = {
    primary: {
      background: `
        linear-gradient(145deg, rgba(255, 182, 193, 0.9) 0%, rgba(255, 160, 200, 0.8) 50%, rgba(230, 190, 255, 0.7) 100%)
      `,
      color: '#ffffff',
      border: 'none',
      boxShadow: `
        12px 12px 24px rgba(0, 0, 0, 0.15),
        -12px -12px 24px rgba(255, 255, 255, 0.1),
        inset 2px 2px 4px rgba(255, 255, 255, 0.3),
        inset -2px -2px 4px rgba(0, 0, 0, 0.1)
      `,
      borderRadius: '20px',
      hoverBackground: `
        linear-gradient(145deg, rgba(255, 182, 193, 1) 0%, rgba(255, 160, 200, 0.9) 50%, rgba(230, 190, 255, 0.8) 100%)
      `,
    },
    secondary: {
      background: `
        linear-gradient(145deg, rgba(255, 182, 193, 0.7) 0%, rgba(255, 160, 200, 0.6) 50%, rgba(230, 190, 255, 0.5) 100%)
      `,
      color: '#ffffff',
      border: 'none',
      boxShadow: `
        10px 10px 20px rgba(0, 0, 0, 0.12),
        -10px -10px 20px rgba(255, 255, 255, 0.08),
        inset 1px 1px 3px rgba(255, 255, 255, 0.25),
        inset -1px -1px 3px rgba(0, 0, 0, 0.08)
      `,
      borderRadius: '18px',
      hoverBackground: `
        linear-gradient(145deg, rgba(255, 182, 193, 0.85) 0%, rgba(255, 160, 200, 0.75) 50%, rgba(230, 190, 255, 0.65) 100%)
      `,
    },
    accent: {
      background: `
        linear-gradient(145deg, rgba(255, 192, 203, 0.8) 0%, rgba(230, 190, 255, 0.7) 50%, rgba(255, 182, 193, 0.6) 100%)
      `,
      color: '#ffffff',
      border: 'none',
      boxShadow: `
        10px 10px 20px rgba(0, 0, 0, 0.12),
        -10px -10px 20px rgba(255, 255, 255, 0.08),
        inset 1px 1px 3px rgba(255, 255, 255, 0.25),
        inset -1px -1px 3px rgba(0, 0, 0, 0.08)
      `,
      borderRadius: '18px',
      hoverBackground: `
        linear-gradient(145deg, rgba(255, 192, 203, 0.95) 0%, rgba(230, 190, 255, 0.85) 50%, rgba(255, 182, 193, 0.75) 100%)
      `,
    },
  };

  const iconSizeMap = {
    xs: 14,
    sm: 16,
    md: 20,
    lg: 24,
  };

  const currentIconSize = iconSizeMap[size] || iconSizeMap.md;
  const currentSizeStyle = sizeStyles[size];
  const currentVariantStyle = variantStyles[variant] || variantStyles.primary;

  const renderContent = () => {
    if (iconOnly) {
      return Icon ? <Icon size={currentIconSize} /> : null;
    }
    if (Icon) {
      return (
        <>
          {iconPosition === 'left' && <Icon size={currentIconSize} className={children ? "mr-2" : ""} />}
          {children}
          {iconPosition === 'right' && <Icon size={currentIconSize} className={children ? "ml-2" : ""} />}
        </>
      );
    }
    return children;
  };

  return (
    <motion.button
      type={type}
      className={`relative overflow-hidden font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:ring-opacity-75 ${
        rounded ? 'rounded-full' : ''
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'} ${className}`}
      style={{
        ...currentSizeStyle,
        ...currentVariantStyle,
        textShadow: 'none',
        borderRadius: rounded ? '50%' : (currentVariantStyle.borderRadius || '20px'),
      }}
      onClick={handleClick}
      disabled={disabled}
      aria-label={typeof children === 'string' ? children : undefined}
      whileHover={
        !disabled
          ? {
              scale: 1.02,
              y: -2,
              boxShadow: `
                16px 16px 32px rgba(0, 0, 0, 0.2),
                -16px -16px 32px rgba(255, 255, 255, 0.15),
                inset 3px 3px 6px rgba(255, 255, 255, 0.4),
                inset -3px -3px 6px rgba(0, 0, 0, 0.15)
              `,
              borderRadius: '22px',
            }
          : {}
      }
      whileTap={!disabled ? { 
        scale: 0.98, 
        y: 0,
        boxShadow: `
          6px 6px 12px rgba(0, 0, 0, 0.25),
          -6px -6px 12px rgba(255, 255, 255, 0.05),
          inset 4px 4px 8px rgba(0, 0, 0, 0.2),
          inset -2px -2px 4px rgba(255, 255, 255, 0.1)
        `,
        borderRadius: '18px',
      } : {}}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
    >
      {/* 컨텐츠 */}
      <span className="relative z-10 flex items-center justify-center">
        {renderContent()}
      </span>

      {/* 리플 효과 */}
      {ripple && isRippling && (
        <motion.span
          className="absolute rounded-full bg-white/30"
          style={{
            left: coords.x - 10,
            top: coords.y - 10,
            width: 20,
            height: 20,
          }}
          initial={{ scale: 0, opacity: 1 }}
          animate={{ scale: 4, opacity: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        />
      )}
    </motion.button>
  );
};

export default Button;
