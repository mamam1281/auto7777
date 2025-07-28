'use client';

import { useState, useEffect, useRef } from 'react';
// SheetJS 라이브러리 임포트 (npm install xlsx 필요)
import * as XLSX from 'xlsx';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { adminApi } from '../../../lib/api-client';
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
    AlertCircle
} from 'lucide-react';

interface User {
    id: number;
    nickname: string;
    email: string;
    cyber_token_balance: number;
    current_rank: string;
}

interface RewardHistory {
    id: number;
    user_id: number;
    user_nickname: string;
    reward_type: string;
    amount: number;
    reason: string;
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

    // 엑셀 업로드 input ref
    const fileInputRef = useRef<HTMLInputElement>(null);
    // 엑셀 업로드 핸들러
    const handleExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
            const data = evt.target?.result;
            if (!data) return;
            const workbook = XLSX.read(data, { type: 'binary' });
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            // TODO: 서버 연동 API로 전송 (아래는 샘플 콘솔)
            console.log('엑셀 업로드 데이터:', jsonData);
            alert('엑셀 데이터가 정상적으로 파싱되었습니다. (서버 연동은 추후 구현)');
        };
        reader.readAsBinaryString(file);
        // 파일 선택 후 input 초기화(동일 파일 재업로드 가능)
        e.target.value = '';
    };


    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            // 사용자 데이터
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/users`);
                if (response.ok) {
                    const data = await response.json();
                    const usersData = Array.isArray(data.items) ? data.items : [];
                    const formattedUsers: User[] = usersData.map((u: any) => ({
                        id: u.id,
                        nickname: u.nickname || u.site_id,
                        email: u.email || '',
                        cyber_token_balance: u.cyber_token_balance || 0,
                        current_rank: u.rank || 'BASIC'
                    }));
                    setUsers(formattedUsers);
                } else {
                    setUsers([]);
                }
            } catch (error) {
                setUsers([]);
            }
            // 보상 내역 데이터
            try {
                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/rewards`);
                if (response.ok) {
                    const data = await response.json();
                    const rewardsData = Array.isArray(data.items) ? data.items : [];
                    const formattedRewards: RewardHistory[] = rewardsData.map((r: any) => ({
                        id: r.id,
                        user_id: r.user_id,
                        user_nickname: r.user_nickname || '알 수 없음',
                        reward_type: r.reward_type || 'BONUS',
                        amount: r.amount || 0,
                        reason: r.reason || '',
                        admin_nickname: r.admin_nickname || 'Admin',
                        created_at: r.created_at || new Date().toISOString(),
                        status: r.status || 'COMPLETED'
                    }));
                    setRewardHistory(formattedRewards);
                } else {
                    setRewardHistory([]);
                }
            } catch (error) {
                setRewardHistory([]);
            }
        } catch (err) {
            setUsers([]);
            setRewardHistory([]);
        } finally {
            setLoading(false);
        }
    };

    const filteredUsers = users.filter(user =>
        user.nickname.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleGiveReward = async () => {
        if (!selectedUser || !rewardForm.amount || !rewardForm.reason.trim()) {
            alert('모든 필드를 입력해주세요.');
            return;
        }

        try {
            setSubmitting(true);

            // 실제 API 호출
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/admin/rewards/give`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: selectedUser.id,
                    reward_type: rewardForm.reward_type,
                    amount: rewardForm.amount,
                    reason: rewardForm.reason
                })
            });

            if (response.ok) {
                // API 응답에서 새로 생성된 보상 정보 가져오기
                const data = await response.json();

                // 보상 내역에 새 항목 추가
                const newReward: RewardHistory = {
                    id: data.id || Date.now(),
                    user_id: selectedUser.id,
                    user_nickname: selectedUser.nickname,
                    reward_type: rewardForm.reward_type,
                    amount: rewardForm.amount,
                    reason: rewardForm.reason,
                    admin_nickname: data.admin_nickname || 'Admin',
                    created_at: data.created_at || new Date().toISOString(),
                    status: data.status || 'COMPLETED'
                };

                setRewardHistory(prev => [newReward, ...prev]);

                // 사용자 잔액 업데이트
                setUsers(prev => prev.map(user =>
                    user.id === selectedUser.id
                        ? { ...user, cyber_token_balance: user.cyber_token_balance + rewardForm.amount }
                        : user
                ));

                setShowRewardModal(false);
                setSelectedUser(null);
                setRewardForm({
                    user_id: 0,
                    reward_type: 'BONUS',
                    amount: 0,
                    reason: ''
                });

                alert('보상이 성공적으로 지급되었습니다!');
            } else {
                const errorData = await response.json().catch(() => ({}));
                console.error('보상 지급 API 오류:', response.status, errorData);
                alert(`보상 지급에 실패했습니다. 오류: ${errorData.message || response.statusText}`);
            }
        } catch (err) {
            console.error('Error giving reward:', err);
            alert('보상 지급에 실패했습니다. 네트워크 오류가 발생했습니다.');
        } finally {
            setSubmitting(false);
        }
    };

    const openRewardModal = (user: User) => {
        setSelectedUser(user);
        setRewardForm(prev => ({ ...prev, user_id: user.id }));
        setShowRewardModal(true);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'COMPLETED':
                return 'bg-green-600 text-green-100';
            case 'PENDING':
                return 'bg-yellow-600 text-yellow-100';
            case 'FAILED':
                return 'bg-red-600 text-red-100';
            default:
                return 'bg-gray-600 text-gray-100';
        }
    };

    const getRewardTypeColor = (type: string) => {
        switch (type) {
            case 'BONUS':
                return 'text-blue-400';
            case 'EVENT':
                return 'text-purple-400';
            case 'COMPENSATION':
                return 'text-orange-400';
            case 'ADMIN':
                return 'text-red-400';
            default:
                return 'text-gray-400';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-white text-xl flex items-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    데이터를 불러오는 중...
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header + 엑셀 업로드 버튼 */}
            <div className="bg-gray-800 border-b border-gray-700 p-6 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Link href="/admin" className="text-gray-400 hover:text-white transition-colors">
                            <ChevronLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-3xl font-bold">보상 관리</h1>
                            <p className="text-gray-400 mt-1">사용자 보상 지급 및 내역 관리</p>
                        </div>
                    </div>
                    <div className="flex items-center space-x-4">
                        <Gift className="w-8 h-8 text-green-400" />
                    </div>
                </div>
                {/* 엑셀 업로드 버튼 */}
                <div className="flex justify-end">
                    <button
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <Plus className="w-4 h-4" />
                        엑셀 업로드
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".xlsx,.xls"
                        style={{ display: 'none' }}
                        onChange={handleExcelUpload}
                    />
                </div>
            </div>

            <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 사용자 선택 및 보상 지급 */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gray-800 rounded-lg p-6 border border-gray-700"
                >
                    <h2 className="text-xl font-bold mb-4 flex items-center">
                        <User className="w-5 h-5 mr-2 text-blue-400" />
                        사용자 선택
                    </h2>

                    {/* 검색 */}
                    <div className="mb-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                placeholder="사용자 검색..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* 사용자 목록 */}
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                        {filteredUsers.map((user) => (
                            <div
                                key={user.id}
                                className="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
                            >
                                <div className="flex-1">
                                    <div className="font-medium text-white">{user.nickname}</div>
                                    <div className="text-sm text-gray-400">{user.email}</div>
                                    <div className="text-sm text-yellow-400">
                                        {user.cyber_token_balance.toLocaleString()} 토큰
                                    </div>
                                </div>
                                <button
                                    onClick={() => openRewardModal(user)}
                                    className="bg-green-600 hover:bg-green-700 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center"
                                >
                                    <Gift className="w-4 h-4 mr-1" />
                                    지급
                                </button>
                            </div>
                        ))}
                    </div>
                </motion.div>

                {/* 최근 보상 내역 */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-gray-800 rounded-lg p-6 border border-gray-700"
                >
                    <h2 className="text-xl font-bold mb-4 flex items-center">
                        <History className="w-5 h-5 mr-2 text-purple-400" />
                        최근 보상 내역
                    </h2>


                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {rewardHistory.length === 0 ? (
                            <div className="text-center text-gray-400 py-8">보상 내역이 없습니다.</div>
                        ) : (
                            rewardHistory.map((reward) => (
                                <div
                                    key={reward.id}
                                    className="p-4 bg-gray-700 rounded-lg border border-gray-600"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center space-x-2">
                                            <span className="font-medium text-white">{reward.user_nickname}</span>
                                            <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(reward.status)}`}>
                                                {reward.status}
                                            </span>
                                        </div>
                                        <div className="text-yellow-400 font-bold">
                                            +{reward.amount.toLocaleString()}
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className={`${getRewardTypeColor(reward.reward_type)} font-medium`}>
                                            {reward.reward_type}
                                        </span>
                                        <span className="text-gray-400">
                                            {formatDate(reward.created_at)}
                                        </span>
                                    </div>
                                    <div className="text-sm text-gray-400 mt-1">
                                        {reward.reason}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    <Link
                        href="/admin/logs"
                        className="mt-4 block text-center text-blue-400 hover:text-blue-300 text-sm font-medium"
                    >
                        전체 내역 보기 →
                    </Link>
                </motion.div>
            </div>

            {/* 보상 지급 모달 */}
            {showRewardModal && selectedUser && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700"
                    >
                        <h3 className="text-xl font-bold mb-4 flex items-center">
                            <Gift className="w-5 h-5 mr-2 text-green-400" />
                            보상 지급
                        </h3>

                        <div className="mb-4 p-3 bg-gray-700 rounded-lg">
                            <div className="font-medium text-white">{selectedUser.nickname}</div>
                            <div className="text-sm text-gray-400">{selectedUser.email}</div>
                            <div className="text-sm text-yellow-400">
                                현재 잔액: {selectedUser.cyber_token_balance.toLocaleString()} 토큰
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    보상 유형
                                </label>
                                <select
                                    value={rewardForm.reward_type}
                                    onChange={(e) => setRewardForm({ ...rewardForm, reward_type: e.target.value })}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                >
                                    <option value="BONUS">보너스</option>
                                    <option value="EVENT">이벤트</option>
                                    <option value="COMPENSATION">보상</option>
                                    <option value="ADMIN">관리자 지급</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    지급 금액
                                </label>
                                <input
                                    type="number"
                                    value={rewardForm.amount}
                                    onChange={(e) => setRewardForm({ ...rewardForm, amount: parseInt(e.target.value) || 0 })}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                    placeholder="지급할 토큰 수량"
                                    min="1"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-2">
                                    지급 사유
                                </label>
                                <textarea
                                    value={rewardForm.reason}
                                    onChange={(e) => setRewardForm({ ...rewardForm, reason: e.target.value })}
                                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                    rows={3}
                                    placeholder="보상 지급 사유를 입력하세요..."
                                />
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button
                                onClick={() => setShowRewardModal(false)}
                                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                                disabled={submitting}
                            >
                                취소
                            </button>
                            <button
                                onClick={handleGiveReward}
                                disabled={!rewardForm.amount || !rewardForm.reason.trim() || submitting}
                                className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                            >
                                {submitting ? (
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                ) : (
                                    <Send className="w-4 h-4 mr-2" />
                                )}
                                {submitting ? '지급 중...' : '지급하기'}
                            </button>
                        </div>
                    </motion.div>
                </div>
            )}
        </div>
    );
};

export default AdminRewardsPage;
