'use client';

import { useState, useEffect } from 'react';
import {
    apiClient,
    DashboardData,
    UserAnalytics,
    PersonalizedOffer,
    RecentActivity,
    UserRealtimeStatus,
    ActiveEvent
} from '@/lib/api';
import { useUser } from './useUser';

/**
 * 대시보드 개인화 데이터를 관리하는 커스텀 훅
 */
export function useDashboardData() {
    const { user } = useUser();
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [userAnalytics, setUserAnalytics] = useState<UserAnalytics | null>(null);
    const [personalizedOffers, setPersonalizedOffers] = useState<PersonalizedOffer[]>([]);
    const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // 대시보드 데이터 로드
    const loadDashboardData = async () => {
        if (!user) return;

        try {
            setIsLoading(true);
            setError(null);

            // 병렬로 데이터 로드
            const [
                dashboardResponse,
                analyticsResponse,
                offersResponse,
                activityResponse
            ] = await Promise.allSettled([
                apiClient.getDashboardData(),
                apiClient.getUserAnalytics(),
                apiClient.getPersonalizedOffers(),
                apiClient.getRecentActivity(5) // 최근 5개 활동만
            ]);

            // 성공한 응답들만 처리
            if (dashboardResponse.status === 'fulfilled') {
                setDashboardData(dashboardResponse.value);
            }
            if (analyticsResponse.status === 'fulfilled') {
                setUserAnalytics(analyticsResponse.value);
            }
            if (offersResponse.status === 'fulfilled') {
                setPersonalizedOffers(offersResponse.value);
            }
            if (activityResponse.status === 'fulfilled') {
                setRecentActivity(activityResponse.value);
            }

            console.log('✅ 대시보드 데이터 로드 완료');
        } catch (error) {
            console.error('❌ 대시보드 데이터 로드 실패:', error);
            setError('대시보드 데이터를 불러오는데 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    };

    // 사용자 로그인 시 데이터 로드
    useEffect(() => {
        if (user) {
            loadDashboardData();
        } else {
            // 로그아웃 시 데이터 초기화
            setDashboardData(null);
            setUserAnalytics(null);
            setPersonalizedOffers([]);
            setRecentActivity([]);
            setIsLoading(false);
            setError(null);
        }
    }, [user]);

    // 데이터 새로고침 함수
    const refreshData = () => {
        loadDashboardData();
    };

    return {
        dashboardData,
        userAnalytics,
        personalizedOffers,
        recentActivity,
        isLoading,
        error,
        refreshData
    };
}

/**
 * 실시간 사용자 상태를 관리하는 커스텀 훅
 */
export function useRealtimeStatus() {
    const { user } = useUser();
    const [realtimeStatus, setRealtimeStatus] = useState<UserRealtimeStatus | null>(null);
    const [unreadCount, setUnreadCount] = useState(0);
    const [activeEvents, setActiveEvents] = useState<ActiveEvent[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    // 실시간 상태 업데이트
    const updateRealtimeStatus = async () => {
        if (!user) return;

        try {
            const [statusResponse, unreadResponse, eventsResponse] = await Promise.allSettled([
                apiClient.getUserRealtimeStatus(),
                apiClient.getUnreadNotificationsCount(),
                apiClient.getActiveEvents()
            ]);

            if (statusResponse.status === 'fulfilled') {
                setRealtimeStatus(statusResponse.value);
            }
            if (unreadResponse.status === 'fulfilled') {
                setUnreadCount(unreadResponse.value.count || 0);
            }
            if (eventsResponse.status === 'fulfilled') {
                setActiveEvents(eventsResponse.value);
            }
        } catch (error) {
            console.warn('⚠️ 실시간 상태 업데이트 실패 (무시됨):', error);
        } finally {
            setIsLoading(false);
        }
    };

    // 주기적 상태 업데이트 (30초마다)
    useEffect(() => {
        if (!user) {
            setRealtimeStatus(null);
            setUnreadCount(0);
            setActiveEvents([]);
            setIsLoading(false);
            return;
        }

        // 즉시 한 번 업데이트
        updateRealtimeStatus();

        // 30초마다 업데이트
        const interval = setInterval(updateRealtimeStatus, 30 * 1000);

        // 페이지 포커스 시에도 업데이트
        const handleFocus = () => {
            if (!document.hidden) {
                updateRealtimeStatus();
            }
        };

        window.addEventListener('focus', handleFocus);
        document.addEventListener('visibilitychange', handleFocus);

        return () => {
            clearInterval(interval);
            window.removeEventListener('focus', handleFocus);
            document.removeEventListener('visibilitychange', handleFocus);
        };
    }, [user]);

    return {
        realtimeStatus,
        unreadCount,
        activeEvents,
        isLoading,
        refreshStatus: updateRealtimeStatus
    };
}

/**
 * 개인화된 추천을 관리하는 커스텀 훅
 */
export function usePersonalizedRecommendations() {
    const { user } = useUser();
    const [recommendations, setRecommendations] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const loadRecommendations = async (emotion?: string) => {
        if (!user) return;

        try {
            setIsLoading(true);
            const response = await apiClient.getPersonalizedRecommendations();
            setRecommendations(response.data?.recommendations || []);
            console.log('🎯 개인화 추천 로드 완료:', response.data?.recommendations?.length || 0);
        } catch (error) {
            console.warn('🎯 개인화 추천 로드 실패 (무시됨):', error);
            setRecommendations([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (user) {
            loadRecommendations();
        } else {
            setRecommendations([]);
        }
    }, [user]);

    return {
        recommendations,
        isLoading,
        refreshRecommendations: loadRecommendations
    };
}
