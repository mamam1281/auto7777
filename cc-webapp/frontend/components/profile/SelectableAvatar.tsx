'use client';

import { useState } from 'react';
import { AVATAR_CHARACTERS, AvatarCharacterType } from './AvatarCharacters';

interface SelectableAvatarProps {
    selectedCharacter?: AvatarCharacterType;
    onCharacterSelect?: (character: AvatarCharacterType) => void;
    nickname: string;
    size?: 'sm' | 'md' | 'lg';
}

export default function SelectableAvatar({
    selectedCharacter = 'GOLD',
    onCharacterSelect,
    nickname,
    size = 'md'
}: SelectableAvatarProps) {
    const [isSelecting, setIsSelecting] = useState(false);

    const sizeClasses = {
        sm: 'w-12 h-12 text-lg',
        md: 'w-16 h-16 text-xl',
        lg: 'w-20 h-20 text-2xl'
    };

    const character = AVATAR_CHARACTERS[selectedCharacter];

    const handleAvatarClick = () => {
        if (onCharacterSelect) {
            setIsSelecting(!isSelecting);
        }
    };

    const handleCharacterSelect = (characterType: AvatarCharacterType) => {
        onCharacterSelect?.(characterType);
        setIsSelecting(false);
    };

    return (
        <div className="relative">
            {/* 메인 아바타 */}
            <div
                className={`${sizeClasses[size]} rounded-full flex items-center justify-center cursor-pointer transition-all duration-300 hover:scale-105`}
                style={{
                    background: character.gradient,
                    boxShadow: `0 4px 12px ${character.shadow}`
                }}
                onClick={handleAvatarClick}
            >
                <span className="font-bold text-white drop-shadow-lg">
                    {character.icon}
                </span>
            </div>

            {/* 캐릭터 선택 팝업 */}
            {isSelecting && (
                <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 z-50">
                    <div className="bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 rounded-xl p-3 shadow-2xl">
                        <div className="grid grid-cols-3 gap-2">
                            {Object.entries(AVATAR_CHARACTERS).map(([key, char]) => (
                                <button
                                    key={key}
                                    className="w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
                                    style={{
                                        background: char.gradient,
                                        boxShadow: `0 2px 8px ${char.shadow}`
                                    }}
                                    onClick={() => handleCharacterSelect(key as AvatarCharacterType)}
                                    title={char.name}
                                >
                                    <span className="text-lg font-bold text-white drop-shadow-lg">
                                        {char.icon}
                                    </span>
                                </button>
                            ))}
                        </div>
                        <div className="text-center mt-2">
                            <p className="text-xs text-gray-300">캐릭터 선택</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
