'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
    ChevronLeft,
    Activity,
    Search,
    Filter,
    Calendar,
    User,
    Gamepad2,
    DollarSign,
    LogIn,
    UserPlus,
    Gift,
    Settings,
    ChevronRight,
    Download,
    RefreshCw
} from 'lucide-react';

interface ActivityLog {
    id: number;
    user_id: number;
    user_nickname: string;
    activity_type: string;
    details: string;
    ip_address: string;
    timestamp: string;
    metadata?: any;
}

const AdminLogsPage = () => {
    const [logs, setLogs] = useState<ActivityLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('ALL');
    const [filterDate, setFilterDate] = useState('ALL');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const logsPerPage = 20;

    useEffect(() => {
        fetchLogs();
    }, [currentPage, searchTerm, filterType, filterDate]);

    const fetchLogs = async () => {
        try {
            setLoading(true);

            // 테스트 데이터
            const testLogs: ActivityLog[] = [
                {
                    id: 1,
                    user_id: 1,
                    user_nickname: '플레이어123',
                    activity_type: 'LOGIN',
                    details: '사용자 로그인',
                    ip_address: '192.168.1.100',
                    timestamp: '2024-07-28T14:30:00Z',
                    metadata: { device: 'Chrome Browser' }
                },
                {
                    id: 2,
                    user_id: 2,
                    user_nickname: '게이머456',
                    activity_type: 'GAME_PLAY',
                    details: '슬롯머신 게임 시작 - 베팅: 50 토큰',
                    ip_address: '192.168.1.101',
                    timestamp: '2024-07-28T14:25:00Z',
                    metadata: { game_id: 'slot_001', bet_amount: 50 }
                },
                {
                    id: 3,
                    user_id: 1,
                    user_nickname: '플레이어123',
                    activity_type: 'REWARD_RECEIVED',
                    details: '일일 로그인 보너스 500 토큰 획득',
                    ip_address: '192.168.1.100',
                    timestamp: '2024-07-28T14:20:00Z',
                    metadata: { reward_type: 'DAILY_BONUS', amount: 500 }
                },
                {
                    id: 4,
                    user_id: 3,
                    user_nickname: '카지노킹',
                    activity_type: 'GAME_WIN',
                    details: '슬롯머신 게임 승리 - 상금: 150 토큰',
                    ip_address: '192.168.1.102',
                    timestamp: '2024-07-28T14:15:00Z',
                    metadata: { game_id: 'slot_001', win_amount: 150 }
                },
                {
                    id: 5,
                    user_id: 4,
                    user_nickname: '럭키777',
                    activity_type: 'SIGNUP',
                    details: '새 사용자 회원가입',
                    ip_address: '192.168.1.103',
                    timestamp: '2024-07-28T14:10:00Z',
                    metadata: { referral_code: null }
                },
                {
                    id: 6,
                    user_id: 2,
                    user_nickname: '게이머456',
                    activity_type: 'PURCHASE',
                    details: '토큰 구매 - 1000 토큰',
                    ip_address: '192.168.1.101',
                    timestamp: '2024-07-28T14:05:00Z',
                    metadata: { payment_method: 'credit_card', amount: 1000 }
                },
                {
                    id: 7,
                    user_id: 1,
                    user_nickname: '플레이어123',
                    activity_type: 'PROFILE_UPDATE',
                    details: '프로필 정보 업데이트',
                    ip_address: '192.168.1.100',
                    timestamp: '2024-07-28T14:00:00Z',
                    metadata: { fields_updated: ['nickname', 'email'] }
                },
                {
                    id: 8,
                    user_id: 3,
                    user_nickname: '카지노킹',
                    activity_type: 'LOGOUT',
                    details: '사용자 로그아웃',
                    ip_address: '192.168.1.102',
                    timestamp: '2024-07-28T13:55:00Z',
                    metadata: { session_duration: 3600 }
                },
                {
                    id: 9,
                    user_id: 5,
                    user_nickname: '스핀마스터',
                    activity_type: 'PASSWORD_CHANGE',
                    details: '비밀번호 변경',
                    ip_address: '192.168.1.104',
                    timestamp: '2024-07-28T13:50:00Z',
                    metadata: { security_level: 'high' }
                },
                {
                    id: 10,
                    user_id: 2,
                    user_nickname: '게이머456',
                    activity_type: 'GAME_LOSS',
                    details: '슬롯머신 게임 패배 - 손실: 75 토큰',
                    ip_address: '192.168.1.101',
                    timestamp: '2024-07-28T13:45:00Z',
                    metadata: { game_id: 'slot_001', loss_amount: 75 }
                }
            ];

            // 필터링 적용
            let filteredLogs = testLogs;

            if (searchTerm) {
                filteredLogs = filteredLogs.filter(log =>
                    log.user_nickname.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    log.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    log.ip_address.includes(searchTerm)
                );
            }

            if (filterType !== 'ALL') {
                filteredLogs = filteredLogs.filter(log => log.activity_type === filterType);
            }

            if (filterDate !== 'ALL') {
                const now = new Date();
                const filterDate_ms = {
                    'TODAY': 24 * 60 * 60 * 1000,
                    'WEEK': 7 * 24 * 60 * 60 * 1000,
                    'MONTH': 30 * 24 * 60 * 60 * 1000
                }[filterDate];

                if (filterDate_ms) {
                    filteredLogs = filteredLogs.filter(log => {
                        const logDate = new Date(log.timestamp);
                        return (now.getTime() - logDate.getTime()) <= filterDate_ms;
                    });
                }
            }

            setLogs(filteredLogs);
            setTotalPages(Math.ceil(filteredLogs.length / logsPerPage));

        } catch (err) {
            console.error('Error fetching logs:', err);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    const getActivityIcon = (type: string) => {
        const iconClass = "w-5 h-5";
        switch (type) {
            case 'LOGIN':
                return <LogIn className={`${iconClass} text-green-400`} />;
            case 'LOGOUT':
                return <LogIn className={`${iconClass} text-red-400`} />;
            case 'SIGNUP':
                return <UserPlus className={`${iconClass} text-blue-400`} />;
            case 'GAME_PLAY':
            case 'GAME_WIN':
            case 'GAME_LOSS':
                return <Gamepad2 className={`${iconClass} text-purple-400`} />;
            case 'REWARD_RECEIVED':
                return <Gift className={`${iconClass} text-yellow-400`} />;
            case 'PURCHASE':
                return <DollarSign className={`${iconClass} text-green-400`} />;
            case 'PROFILE_UPDATE':
            case 'PASSWORD_CHANGE':
                return <Settings className={`${iconClass} text-orange-400`} />;
            default:
                return <Activity className={`${iconClass} text-gray-400`} />;
        }
    };

    const getActivityColor = (type: string) => {
        switch (type) {
            case 'LOGIN':
            case 'SIGNUP':
                return 'text-green-400';
            case 'LOGOUT':
                return 'text-red-400';
            case 'GAME_WIN':
            case 'REWARD_RECEIVED':
                return 'text-yellow-400';
            case 'GAME_LOSS':
                return 'text-red-400';
            case 'GAME_PLAY':
                return 'text-purple-400';
            case 'PURCHASE':
                return 'text-green-400';
            default:
                return 'text-gray-400';
        }
    };

    // 페이지네이션을 위한 현재 페이지 로그들
    const currentLogs = logs.slice(
        (currentPage - 1) * logsPerPage,
        currentPage * logsPerPage
    );

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-white text-xl flex items-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    활동 로그를 불러오는 중...
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Compact Header with Filters */}
            <div className="bg-gray-800 border-b border-gray-700 px-4 py-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <Link href="/admin" className="text-gray-400 hover:text-white transition-colors">
                            <ChevronLeft className="w-5 h-5" />
                        </Link>
                        <div>
                            <h1 className="text-lg font-bold">활동 로그</h1>
                            <p className="text-gray-400 text-xs">{logs.length}개 로그</p>
                        </div>
                    </div>

                    {/* Inline Controls */}
                    <div className="flex items-center space-x-3">
                        <div className="relative">
                            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="검색..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-48 bg-gray-700 border border-gray-600 rounded pl-8 pr-3 py-1 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            />
                        </div>
                        <select
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="ALL">모든 활동</option>
                            <option value="LOGIN">로그인</option>
                            <option value="GAME_PLAY">게임</option>
                            <option value="REWARD_RECEIVED">보상</option>
                            <option value="PURCHASE">구매</option>
                        </select>
                        <select
                            value={filterDate}
                            onChange={(e) => setFilterDate(e.target.value)}
                            className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                        >
                            <option value="ALL">전체</option>
                            <option value="TODAY">오늘</option>
                            <option value="WEEK">7일</option>
                            <option value="MONTH">30일</option>
                        </select>
                        <button
                            onClick={fetchLogs}
                            className="bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded text-sm transition-colors flex items-center"
                        >
                            <RefreshCw className="w-4 h-4 mr-1" />
                            새로고침
                        </button>
                    </div>
                </div>
            </div>

            {/* Dense Logs Table */}
            <div className="p-4 h-[calc(100vh-140px)] flex flex-col">
                {/* Stats Row */}
                <div className="grid grid-cols-4 gap-4 mb-4">
                    <div className="bg-gray-800 rounded p-2 border border-gray-700 text-center">
                        <div className="text-xs text-gray-400">총 로그</div>
                        <div className="text-lg font-bold text-white">{logs.length}</div>
                    </div>
                    <div className="bg-gray-800 rounded p-2 border border-gray-700 text-center">
                        <div className="text-xs text-gray-400">고유 사용자</div>
                        <div className="text-lg font-bold text-white">{new Set(logs.map(log => log.user_id)).size}</div>
                    </div>
                    <div className="bg-gray-800 rounded p-2 border border-gray-700 text-center">
                        <div className="text-xs text-gray-400">게임 활동</div>
                        <div className="text-lg font-bold text-white">{logs.filter(log => log.activity_type.startsWith('GAME_')).length}</div>
                    </div>
                    <div className="bg-gray-800 rounded p-2 border border-gray-700 text-center">
                        <div className="text-xs text-gray-400">로그인</div>
                        <div className="text-lg font-bold text-white">{logs.filter(log => log.activity_type === 'LOGIN').length}</div>
                    </div>
                </div>

                {/* Logs Table */}
                <div className="flex-1 bg-gray-800 rounded border border-gray-700 overflow-hidden">
                    <div className="overflow-auto h-full">
                        <table className="w-full text-sm">
                            <thead className="bg-gray-700 sticky top-0">
                                <tr>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">시간</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">활동</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">사용자</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">상세 내용</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">IP</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">메타데이터</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {currentLogs.map((log) => (
                                    <tr key={log.id} className="hover:bg-gray-700 transition-colors">
                                        <td className="px-3 py-2 text-gray-400 text-xs whitespace-nowrap">
                                            {new Date(log.timestamp).toLocaleString('ko-KR', {
                                                month: '2-digit',
                                                day: '2-digit',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: '2-digit'
                                            })}
                                        </td>
                                        <td className="px-3 py-2 whitespace-nowrap">
                                            <div className="flex items-center">
                                                {getActivityIcon(log.activity_type)}
                                                <span className={`ml-2 font-medium ${getActivityColor(log.activity_type)}`}>
                                                    {log.activity_type}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-3 py-2 whitespace-nowrap">
                                            <Link
                                                href={`/admin/users/${log.user_id}`}
                                                className="text-blue-400 hover:text-blue-300 font-medium"
                                            >
                                                {log.user_nickname}
                                            </Link>
                                        </td>
                                        <td className="px-3 py-2 text-gray-300 max-w-xs">
                                            <div className="truncate">{log.details}</div>
                                        </td>
                                        <td className="px-3 py-2 text-gray-400 font-mono text-xs">
                                            {log.ip_address}
                                        </td>
                                        <td className="px-3 py-2 text-xs text-gray-500 max-w-xs">
                                            {log.metadata && (
                                                <div className="truncate">
                                                    {Object.entries(log.metadata).map(([key, value]) => (
                                                        <span key={key} className="mr-2">
                                                            {key}:{JSON.stringify(value)}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {/* Compact Pagination */}
                    {totalPages > 1 && (
                        <div className="bg-gray-700 px-4 py-2 border-t border-gray-600 flex items-center justify-between text-sm">
                            <span className="text-gray-400">
                                {((currentPage - 1) * logsPerPage) + 1}-{Math.min(currentPage * logsPerPage, logs.length)} / {logs.length}
                            </span>
                            <div className="flex space-x-1">
                                <button
                                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                    disabled={currentPage === 1}
                                    className="px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50"
                                >
                                    <ChevronLeft className="w-4 h-4" />
                                </button>
                                <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs">
                                    {currentPage}
                                </span>
                                <button
                                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                    disabled={currentPage === totalPages}
                                    className="px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50"
                                >
                                    <ChevronRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminLogsPage;
