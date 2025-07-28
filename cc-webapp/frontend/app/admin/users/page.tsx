'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuth } from '../../../lib/auth';
import { adminApi, UserResponse } from '../../../lib/api-client';
import {
    ChevronLeft,
    Search,
    User as UserIcon,
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

import type { User } from '../../../lib/types/user';
import type { PaginatedResponse } from '../../../lib/types/api';

const AdminUsersPage = () => {
    const { user: currentUser, isAdmin } = useAuth();
    const [users, setUsers] = useState<UserResponse[]>([]);
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

            // 백엔드 API 호출 (페이지네이션과 필터링을 서버에서 처리)
            const response: PaginatedResponse<UserResponse> = await adminApi.getUsers(currentPage, usersPerPage, {
                rank: filterRank,
                search: searchTerm
            });

            // 응답 데이터 처리 (데이터가 없는 경우도 정상적으로 처리)
            const items = response?.items || [];
            const totalItems = response?.totalItems || 0;

            setUsers(items);
            setTotalUsers(totalItems);

            // 현재 페이지가 마지막 페이지보다 크면 첫 페이지로 이동
            const totalPages = Math.max(1, Math.ceil(totalItems / usersPerPage));
            if (currentPage > totalPages && totalPages > 1) {
                setCurrentPage(1);
            }
        } catch (error) {
            console.error('사용자 목록 로드 실패:', error);

            // 에러 처리 개선
            if (error instanceof Error) {
                // 타임아웃 에러
                if (error.message === 'Request timeout' || error.message.includes('network')) {
                    alert('서버 연결에 실패했습니다. 네트워크 상태를 확인하고 다시 시도해주세요.');
                }
                // 인증 에러
                else if (error.message.includes('401')) {
                    alert('세션이 만료되었습니다. 다시 로그인해주세요.');
                    window.location.href = '/auth/login';
                }
                // 권한 에러
                else if (error.message.includes('403')) {
                    alert('관리자 권한이 필요한 페이지입니다.');
                    window.location.href = '/';
                }
                // 기타 에러
                else {
                    alert(`사용자 목록을 불러오는데 실패했습니다: ${error.message}`);
                }
            } else {
                alert('알 수 없는 오류가 발생했습니다.');
            }

            // 에러 발생 시 빈 배열 설정
            if (!users || !Array.isArray(users)) {
                setUsers([]);
            }
            setTotalUsers(0);
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
                                    {users && users.length > 0 ? users.map((user: UserResponse, index) => (
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
                                                            <UserIcon className="w-5 h-5 text-white" />
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
                                    )) : (
                                        <tr>
                                            <td colSpan={6} className="px-6 py-4 text-center text-gray-400">
                                                {loading ? '데이터를 불러오는 중...' : '조건에 맞는 사용자가 없습니다.'}
                                            </td>
                                        </tr>
                                    )}
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
