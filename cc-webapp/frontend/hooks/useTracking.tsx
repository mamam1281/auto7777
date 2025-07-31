'use client';

import { useEffect, useRef } from 'react';
import { apiClient } from '@/lib/api';
import { useUser } from './useUser';

/**
 * 사용자 행동 추적을 위한 커스텀 훅
 * 모든 클릭, 페이지 뷰, 체류 시간을 자동으로 추적
 */
export function useTracking() {
    const { user } = useUser();
    const pageStartTime = useRef<number>(Date.now());
    const lastPageRef = useRef<string>('');

    // 페이지 뷰 추적
    useEffect(() => {
        if (!user) return;

        const currentPage = window.location.pathname;
        const referrer = lastPageRef.current || document.referrer;

        // 페이지 뷰 추적 (비동기, 에러 무시)
        apiClient.trackPageView(currentPage, referrer).catch(err => {
            console.warn('📊 페이지 뷰 추적 실패 (무시됨):', err);
        });

        // 이전 페이지에서의 체류 시간 추적
        if (lastPageRef.current) {
            const timeSpent = Math.round((Date.now() - pageStartTime.current) / 1000);
            if (timeSpent > 5) { // 5초 이상 체류한 경우만 추적
                apiClient.trackTimeSpent(lastPageRef.current, timeSpent).catch(err => {
                    console.warn('⏱️ 체류 시간 추적 실패 (무시됨):', err);
                });
            }
        }

        // 현재 페이지 정보 업데이트
        lastPageRef.current = currentPage;
        pageStartTime.current = Date.now();

        // 페이지 언마운트 시 체류 시간 추적
        return () => {
            const timeSpent = Math.round((Date.now() - pageStartTime.current) / 1000);
            if (timeSpent > 5) {
                // Beacon API로 페이지 언마운트 시에도 데이터 전송
                if (navigator.sendBeacon) {
                    const data = {
                        action_type: 'TIME_SPENT',
                        metadata: {
                            page: currentPage,
                            duration_seconds: timeSpent,
                            timestamp: new Date().toISOString()
                        }
                    };
                    navigator.sendBeacon('/api/actions', JSON.stringify(data));
                }
            }
        };
    }, [user, window.location.pathname]);

    // 버튼 클릭 추적 함수
    const trackClick = async (buttonId: string, metadata: object = {}) => {
        if (!user) return;

        try {
            await apiClient.trackButtonClick(buttonId, {
                page: window.location.pathname,
                ...metadata
            });
            console.log(`🎯 버튼 클릭 추적: ${buttonId}`);
        } catch (error) {
            console.warn('🎯 버튼 클릭 추적 실패 (무시됨):', error);
        }
    };

    // 범용 액션 추적 함수
    const trackAction = async (actionType: string, metadata: object = {}) => {
        if (!user) return;

        try {
            await apiClient.trackUserAction(actionType, {
                page: window.location.pathname,
                user_id: user.id,
                ...metadata
            });
            console.log(`📊 액션 추적: ${actionType}`);
        } catch (error) {
            console.warn('📊 액션 추적 실패 (무시됨):', error);
        }
    };

    return {
        trackClick,
        trackAction,
        isTracking: !!user
    };
}

/**
 * 컴포넌트에 클릭 추적을 자동으로 추가하는 고차 함수
 */
export function withClickTracking<T extends React.ComponentType<any>>(
    Component: T,
    trackingId: string
): T {
    const TrackedComponent = (props: any) => {
        const { trackClick } = useTracking();

        const handleClick = async (originalOnClick?: () => void) => {
            await trackClick(trackingId, {
                component: Component.name || 'Unknown',
                props: Object.keys(props)
            });

            if (originalOnClick) {
                originalOnClick();
            }
        };

        return (
            <Component
                {...props}
                onClick={() => handleClick(props.onClick)}
            />
        );
    };

    return TrackedComponent as T;
}

/**
 * 게임별 특화 추적 함수들
 */
export function useGameTracking() {
    const { trackAction } = useTracking();

    const trackGameStart = (gameType: string) => {
        trackAction('GAME_START', { game_type: gameType });
    };

    const trackGameEnd = (gameType: string, result: 'WIN' | 'LOSE', duration: number) => {
        trackAction('GAME_END', {
            game_type: gameType,
            result,
            duration_seconds: duration
        });
    };

    const trackPurchaseIntent = (itemType: string, price: number) => {
        trackAction('PURCHASE_INTENT', {
            item_type: itemType,
            price
        });
    };

    const trackPurchaseComplete = (itemType: string, price: number, currency: string) => {
        trackAction('PURCHASE_COMPLETE', {
            item_type: itemType,
            price,
            currency
        });
    };

    return {
        trackGameStart,
        trackGameEnd,
        trackPurchaseIntent,
        trackPurchaseComplete,
    };
}
