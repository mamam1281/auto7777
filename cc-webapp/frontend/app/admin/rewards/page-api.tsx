'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
    ChevronLeft,
    Gift,
    Search,
    User,
    DollarSign,
    Calendar,
    Plus,
    Send,
    History,
    CheckCircle,
    AlertCircle,
    RefreshCw
} from 'lucide-react';
import { adminApi } from '../../../lib/api-client';

interface User {
    id: number;
    nickname: string;
    site_id: string;
    phone_number: string;
    cyber_token_balance: number;
    rank: string;
    created_at: string;
    updated_at?: string;
}

interface RewardHistory {
    id: number;
    user_id: number;
    user_nickname: string;
    reward_type: string;
    amount: number;
    reason: string;
    admin_id: number;
    admin_nickname: string;
    created_at: string;
    status: 'COMPLETED' | 'PENDING' | 'FAILED';
}

interface RewardForm {
    user_id: number;
    reward_type: string;
    amount: number;
    reason: string;
}

const AdminRewardsPage = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [rewardHistory, setRewardHistory] = useState<RewardHistory[]>([]);
    const [loading, setLoading] = useState(true);
    const [historyLoading, setHistoryLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showRewardModal, setShowRewardModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);
    const [rewardForm, setRewardForm] = useState<RewardForm>({
        user_id: 0,
        reward_type: 'BONUS',
        amount: 0,
        reason: ''
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchUsers();
        fetchRewardHistory();
    }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);

            // API에서 실제 사용자 데이터 가져오기
            const response = await adminApi.getUsers();

            if (response && Array.isArray(response.items)) {
                setUsers(response.items);
            } else {
                console.error('사용자 목록이 올바른 형식이 아닙니다:', response);
                setUsers([]);
            }
        } catch (err) {
            console.error('사용자 목록을 불러오는데 실패했습니다:', err);
            setUsers([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchRewardHistory = async () => {
        try {
            setHistoryLoading(true);

            // API를 통해 보상 내역 가져오기
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/rewards`);

            if (response.ok) {
                const data = await response.json();
                if (Array.isArray(data.items)) {
                    setRewardHistory(data.items);
                } else if (Array.isArray(data)) {
                    setRewardHistory(data);
                } else {
                    setRewardHistory([]);
                }
            } else {
                console.error('보상 내역을 불러오는데 실패했습니다:', response.status);
                setRewardHistory([]);
            }
        } catch (error) {
            console.error('보상 내역 API 호출 오류:', error);
            setRewardHistory([]);
        } finally {
            setHistoryLoading(false);
        }
    };

    const filteredUsers = users.filter(user => {
        const searchValue = searchTerm.toLowerCase();
        return user.nickname?.toLowerCase().includes(searchValue) ||
            user.site_id?.toLowerCase().includes(searchValue) ||
            user.phone_number?.toLowerCase().includes(searchValue);
    });

    const handleGiveReward = async () => {
        if (!selectedUser || !rewardForm.amount || !rewardForm.reason.trim()) {
            alert('모든 필드를 입력해주세요.');
            return;
        }

        try {
            setSubmitting(true);

            // 실제 API 호출
            await adminApi.giveReward({
                user_id: selectedUser.id,
                amount: rewardForm.amount,
                reason: rewardForm.reason
            });

            // 보상 내역과 사용자 목록 다시 불러오기
            await Promise.all([fetchRewardHistory(), fetchUsers()]);

            setShowRewardModal(false);
            setSelectedUser(null);
            setRewardForm({
                user_id: 0,
                reward_type: 'BONUS',
                amount: 0,
                reason: ''
            });

            alert('보상이 성공적으로 지급되었습니다!');
        } catch (err) {
            console.error('보상 지급에 실패했습니다:', err);
            alert('보상 지급에 실패했습니다. 다시 시도해주세요.');
        } finally {
            setSubmitting(false);
        }
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'COMPLETED':
                return 'bg-green-600 text-white';
            case 'PENDING':
                return 'bg-yellow-600 text-white';
            case 'FAILED':
                return 'bg-red-600 text-white';
            default:
                return 'bg-gray-600 text-white';
        }
    };

    const formatDate = (dateString: string) => {
        try {
            return new Date(dateString).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return '날짜 오류';
        }
    };

    const RewardModal = () => (
        <div className="fixed inset-0 bg-gray-900/80 flex items-center justify-center z-50">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4"
            >
                <h2 className="text-xl font-bold mb-4 flex items-center">
                    <Gift className="w-5 h-5 mr-2 text-yellow-400" />
                    보상 지급
                </h2>

                {selectedUser && (
                    <div className="mb-6 p-4 bg-gray-700 rounded-lg">
                        <div className="flex items-center">
                            <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center mr-3">
                                <User className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <div className="font-medium text-white">{selectedUser.nickname || selectedUser.site_id}</div>
                                <div className="text-sm text-gray-300">ID: {selectedUser.id}</div>
                            </div>
                            <div className="ml-auto flex items-center">
                                <DollarSign className="w-4 h-4 text-yellow-400 mr-1" />
                                <span className="text-sm font-medium">
                                    {selectedUser.cyber_token_balance?.toLocaleString() || 0} 토큰
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm text-gray-400 mb-1">보상 유형</label>
                        <select
                            value={rewardForm.reward_type}
                            onChange={(e) => setRewardForm({ ...rewardForm, reward_type: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="BONUS">보너스</option>
                            <option value="EVENT">이벤트 보상</option>
                            <option value="COMPENSATION">보상/환불</option>
                            <option value="ADMIN">관리자 수동 지급</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">금액 (토큰)</label>
                        <input
                            type="number"
                            min="1"
                            value={rewardForm.amount || ''}
                            onChange={(e) => setRewardForm({ ...rewardForm, amount: parseInt(e.target.value) || 0 })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-400 mb-1">지급 이유</label>
                        <textarea
                            value={rewardForm.reason}
                            onChange={(e) => setRewardForm({ ...rewardForm, reason: e.target.value })}
                            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500 h-24 resize-none"
                            placeholder="보상 지급 이유를 입력하세요..."
                        />
                    </div>
                </div>

                <div className="mt-6 flex space-x-3">
                    <button
                        onClick={() => setShowRewardModal(false)}
                        className="px-4 py-2 bg-gray-700 text-white rounded hover:bg-gray-600 flex-1"
                    >
                        취소
                    </button>
                    <button
                        onClick={handleGiveReward}
                        disabled={submitting}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex-1 flex items-center justify-center"
                    >
                        {submitting ? (
                            <>
                                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                처리 중...
                            </>
                        ) : (
                            <>
                                <Send className="w-4 h-4 mr-2" />
                                보상 지급
                            </>
                        )}
                    </button>
                </div>
            </motion.div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center">
                    <Link href="/admin" className="mr-4">
                        <ChevronLeft className="w-6 h-6 text-gray-400 hover:text-white" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold flex items-center">
                            <Gift className="w-7 h-7 mr-3 text-yellow-400" />
                            보상 관리
                        </h1>
                        <p className="text-gray-400 text-sm">사용자에게 토큰 및 아이템 보상 지급</p>
                    </div>
                </div>
                <div>
                    <button
                        onClick={fetchRewardHistory}
                        className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 mr-2 flex items-center"
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        새로고침
                    </button>
                </div>
            </div>

            <div className="p-6">
                {/* 사용자 검색 */}
                <div className="mb-8">
                    <h2 className="text-xl font-semibold mb-4 flex items-center">
                        <User className="w-5 h-5 mr-2 text-blue-400" />
                        사용자 선택
                    </h2>

                    <div className="relative mb-6">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            placeholder="사용자 ID, 닉네임 또는 전화번호로 검색..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div className="bg-gray-800 rounded-lg overflow-hidden">
                        <div className="overflow-x-auto">
                            {loading ? (
                                <div className="flex items-center justify-center py-12">
                                    <RefreshCw className="w-8 h-8 text-blue-400 animate-spin" />
                                    <span className="ml-3 text-lg">사용자 데이터를 불러오는 중...</span>
                                </div>
                            ) : (
                                <table className="min-w-full divide-y divide-gray-700">
                                    <thead className="bg-gray-700">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                사용자
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                현재 잔액
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                등급
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                액션
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-700">
                                        {filteredUsers.length > 0 ? (
                                            filteredUsers.map((user) => (
                                                <tr key={user.id} className="hover:bg-gray-700/50 transition">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <div className="flex-shrink-0 h-10 w-10">
                                                                <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center">
                                                                    <User className="w-5 h-5 text-white" />
                                                                </div>
                                                            </div>
                                                            <div className="ml-4">
                                                                <div className="text-sm font-medium text-white">
                                                                    {user.nickname || user.site_id}
                                                                </div>
                                                                <div className="text-sm text-gray-400">
                                                                    {user.phone_number}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <DollarSign className="w-4 h-4 text-yellow-400 mr-2" />
                                                            <span className="text-sm font-medium">
                                                                {user.cyber_token_balance?.toLocaleString() || 0} 토큰
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${user.rank === 'VIP' ? 'bg-purple-600' :
                                                                user.rank === 'PREMIUM' ? 'bg-blue-600' :
                                                                    user.rank === 'ADMIN' ? 'bg-red-600' : 'bg-gray-600'
                                                            } text-white`}>
                                                            {user.rank || 'BASIC'}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                        <button
                                                            onClick={() => {
                                                                setSelectedUser(user);
                                                                setRewardForm({
                                                                    ...rewardForm,
                                                                    user_id: user.id
                                                                });
                                                                setShowRewardModal(true);
                                                            }}
                                                            className="text-blue-400 hover:text-blue-300 flex items-center"
                                                        >
                                                            <Plus className="w-4 h-4 mr-1" />
                                                            보상 지급
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan={4} className="px-6 py-8 text-center text-gray-400">
                                                    {searchTerm ? '검색 결과가 없습니다.' : '사용자 데이터가 없습니다.'}
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                </div>

                {/* 보상 내역 */}
                <div>
                    <h2 className="text-xl font-semibold mb-4 flex items-center">
                        <History className="w-5 h-5 mr-2 text-green-400" />
                        최근 보상 내역
                    </h2>

                    <div className="bg-gray-800 rounded-lg overflow-hidden">
                        <div className="overflow-x-auto">
                            {historyLoading ? (
                                <div className="flex items-center justify-center py-12">
                                    <RefreshCw className="w-8 h-8 text-blue-400 animate-spin" />
                                    <span className="ml-3 text-lg">보상 내역을 불러오는 중...</span>
                                </div>
                            ) : (
                                <table className="min-w-full divide-y divide-gray-700">
                                    <thead className="bg-gray-700">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                사용자
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                보상 유형
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                금액
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                지급 이유
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                지급 시간
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                                상태
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-700">
                                        {rewardHistory.length > 0 ? (
                                            rewardHistory.map((reward) => (
                                                <tr key={reward.id} className="hover:bg-gray-700/50 transition">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm">{reward.user_nickname}</div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm">{reward.reward_type}</div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <DollarSign className="w-4 h-4 text-yellow-400 mr-2" />
                                                            <span className="text-sm font-medium">
                                                                {reward.amount?.toLocaleString() || 0} 토큰
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        <div className="text-sm">{reward.reason}</div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm text-gray-400 flex items-center">
                                                            <Calendar className="w-4 h-4 mr-1" />
                                                            {formatDate(reward.created_at)}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(reward.status)}`}>
                                                            {reward.status === 'COMPLETED' && <CheckCircle className="w-3 h-3 mr-1" />}
                                                            {reward.status === 'FAILED' && <AlertCircle className="w-3 h-3 mr-1" />}
                                                            {reward.status}
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan={6} className="px-6 py-8 text-center text-gray-400">
                                                    보상 내역이 없습니다.
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* 보상 지급 모달 */}
            {showRewardModal && <RewardModal />}
        </div>
    );
};

export default AdminRewardsPage;
