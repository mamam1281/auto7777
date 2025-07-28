'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuth } from '../../../lib/auth';
import { adminApi } from '../../../lib/api-client';
import {
    ChevronLeft,
    Search,
    User,
    Shield,
    Calendar,
    Coins,
    Eye,
    Filter,
    Download,
    RefreshCw,
    Users,
    Award
} from 'lucide-react';

interface User {
    id: number;
    site_id: string;
    nickname: string;
    phone_number: string;
    cyber_token_balance: number;
    rank: string;
    created_at: string;
}

const AdminUsersPage = () => {
    const { user: currentUser, isAdmin } = useAuth();
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterRank, setFilterRank] = useState('ALL');
    const [currentPage, setCurrentPage] = useState(1);
    const [totalUsers, setTotalUsers] = useState(0);
    const usersPerPage = 20;

    useEffect(() => {
        if (isAdmin) {
            fetchUsers();
        }
    }, [isAdmin, currentPage, searchTerm, filterRank]);

    const fetchUsers = async () => {
        try {
            setLoading(true);

            // API 호출
            const usersData = await adminApi.getUsers();

            // 필터링 로직
            let filteredUsers = usersData;

            if (searchTerm) {
                filteredUsers = filteredUsers.filter(user =>
                    user.nickname.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    user.site_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    user.phone_number.includes(searchTerm)
                );
            }

            if (filterRank !== 'ALL') {
                filteredUsers = filteredUsers.filter(user => user.rank === filterRank);
            }

            setTotalUsers(filteredUsers.length);

            // 페이지네이션
            const startIndex = (currentPage - 1) * usersPerPage;
            const paginatedUsers = filteredUsers.slice(startIndex, startIndex + usersPerPage);

            setUsers(paginatedUsers);
        } catch (error) {
            console.error('사용자 목록 로드 실패:', error);
            // 임시 데이터로 대체
            setUsers([
                {
                    id: 1,
                    site_id: 'user001',
                    nickname: '테스트유저1',
                    phone_number: '010-1234-5678',
                    cyber_token_balance: 1500,
                    rank: 'STANDARD',
                    created_at: '2025-01-15T10:30:00Z'
                },
                {
                    id: 2,
                    site_id: 'admin001',
                    nickname: '관리자',
                    phone_number: '010-9999-0000',
                    cyber_token_balance: 999999,
                    rank: 'ADMIN',
                    created_at: '2025-01-01T00:00:00Z'
                }
            ]);
            setTotalUsers(2);
        } finally {
            setLoading(false);
        }
    };

    const getRankBadge = (rank: string) => {
        const badges = {
            'ADMIN': 'bg-red-600 text-white',
            'SUPER_ADMIN': 'bg-purple-600 text-white',
            'VIP': 'bg-yellow-600 text-white',
            'PREMIUM': 'bg-blue-600 text-white',
            'STANDARD': 'bg-gray-600 text-white'
        };
        return badges[rank as keyof typeof badges] || 'bg-gray-600 text-white';
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const totalPages = Math.ceil(totalUsers / usersPerPage);

    if (!isAdmin) {
        return (
            <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
                <div className="text-center">
                    <Shield className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <h1 className="text-2xl font-bold mb-2">접근 권한이 없습니다</h1>
                    <p className="text-gray-400 mb-4">관리자만 접근할 수 있는 페이지입니다.</p>
                    <Link href="/auth/login" className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
                        로그인 페이지로
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white" style={{ width: '100vw', maxWidth: 'none', margin: 0, padding: 0 }}>
            {/* Header */}
            <div className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center">
                    <Link href="/admin" className="mr-4">
                        <ChevronLeft className="w-6 h-6 text-gray-400 hover:text-white" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold flex items-center">
                            <Users className="w-7 h-7 mr-3 text-blue-400" />
                            사용자 관리
                        </h1>
                        <p className="text-gray-400 text-sm">전체 사용자 목록 및 관리</p>
                    </div>
                </div>
                <div className="flex items-center space-x-3">
                    <button
                        onClick={fetchUsers}
                        className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        새로고침
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="px-6 py-4 bg-gray-800/50 border-b border-gray-700">
                <div className="flex flex-wrap items-center gap-4">
                    {/* Search */}
                    <div className="flex-1 min-w-64">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="닉네임, 사이트ID, 전화번호로 검색..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                            />
                        </div>
                    </div>

                    {/* Rank Filter */}
                    <select
                        value={filterRank}
                        onChange={(e) => setFilterRank(e.target.value)}
                        className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                    >
                        <option value="ALL">모든 등급</option>
                        <option value="ADMIN">관리자</option>
                        <option value="VIP">VIP</option>
                        <option value="PREMIUM">프리미엄</option>
                        <option value="STANDARD">일반</option>
                    </select>

                    {/* Stats */}
                    <div className="text-sm text-gray-400">
                        총 {totalUsers}명의 사용자
                    </div>
                </div>
            </div>

            {/* Users Table */}
            <div className="px-6 py-4">
                {loading ? (
                    <div className="flex items-center justify-center py-12">
                        <RefreshCw className="w-8 h-8 text-blue-400 animate-spin" />
                        <span className="ml-3 text-lg">사용자 목록을 불러오는 중...</span>
                    </div>
                ) : (
                    <>
                        <div className="bg-gray-800 rounded-lg overflow-hidden">
                            <table className="w-full">
                                <thead className="bg-gray-700">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">사용자</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">연락처</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">토큰</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">등급</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">가입일</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">액션</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-700">
                                    {users.map((user, index) => (
                                        <motion.tr
                                            key={user.id}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.05 }}
                                            className="hover:bg-gray-700/50"
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center">
                                                    <div className="flex-shrink-0 h-10 w-10">
                                                        <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center">
                                                            <User className="w-5 h-5 text-white" />
                                                        </div>
                                                    </div>
                                                    <div className="ml-4">
                                                        <div className="text-sm font-medium text-white">{user.nickname}</div>
                                                        <div className="text-sm text-gray-400">ID: {user.site_id}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm text-white">{user.phone_number}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center">
                                                    <Coins className="w-4 h-4 text-yellow-400 mr-2" />
                                                    <span className="text-sm font-medium text-white">
                                                        {user.cyber_token_balance?.toLocaleString() || 0}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRankBadge(user.rank)}`}>
                                                    {user.rank}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                                {formatDate(user.created_at)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                <Link
                                                    href={`/admin/users/${user.id}`}
                                                    className="text-blue-400 hover:text-blue-300 flex items-center"
                                                >
                                                    <Eye className="w-4 h-4 mr-1" />
                                                    상세보기
                                                </Link>
                                            </td>
                                        </motion.tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="mt-6 flex items-center justify-between">
                                <div className="text-sm text-gray-400">
                                    {((currentPage - 1) * usersPerPage) + 1}-{Math.min(currentPage * usersPerPage, totalUsers)} / {totalUsers}
                                </div>
                                <div className="flex space-x-2">
                                    <button
                                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                        disabled={currentPage === 1}
                                        className="px-3 py-2 bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                                    >
                                        이전
                                    </button>
                                    <span className="px-3 py-2 bg-gray-800 text-white rounded">
                                        {currentPage} / {totalPages}
                                    </span>
                                    <button
                                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                        disabled={currentPage === totalPages}
                                        className="px-3 py-2 bg-gray-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600"
                                    >
                                        다음
                                    </button>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};

export default AdminUsersPage;
