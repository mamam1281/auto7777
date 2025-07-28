'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../lib/auth';
import { adminApi, UserResponse } from '../../../lib/api-client';

const AdminUsersPage = () => {
    const { user, isAdmin, loading: authLoading } = useAuth();
    const [users, setUsers] = useState<UserResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const router = useRouter();

    useEffect(() => {
        if (authLoading) return;

        // 관리자 권한 체크
        if (!user || !isAdmin) {
            router.push('/auth');
            return;
        }

        fetchUsers();
    }, [user, isAdmin, authLoading, router]);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            setError(null);

            // 테스트 데이터 - 실제로는 API에서 가져옴
            const testUsers: User[] = [
                {
                    id: 1,
                    nickname: '플레이어123',
                    email: 'player123@example.com',
                    cyber_token_balance: 1250,
                    current_rank: 'VIP',
                    is_verified: true,
                    is_active: true,
                    created_at: '2024-01-15T09:30:00Z',
                    last_login: '2024-07-28T14:20:00Z'
                },
                {
                    id: 2,
                    nickname: '게이머456',
                    email: 'gamer456@example.com',
                    cyber_token_balance: 850,
                    current_rank: 'PREMIUM',
                    is_verified: true,
                    is_active: true,
                    created_at: '2024-02-20T11:15:00Z',
                    last_login: '2024-07-27T16:45:00Z'
                },
                {
                    id: 3,
                    nickname: '카지노킹',
                    email: 'casinoking@example.com',
                    cyber_token_balance: 2100,
                    current_rank: 'VIP',
                    is_verified: true,
                    is_active: true,
                    created_at: '2024-01-10T08:00:00Z',
                    last_login: '2024-07-28T13:10:00Z'
                },
                {
                    id: 4,
                    nickname: '럭키777',
                    email: 'lucky777@example.com',
                    cyber_token_balance: 320,
                    current_rank: 'BASIC',
                    is_verified: false,
                    is_active: true,
                    created_at: '2024-06-15T14:30:00Z',
                    last_login: '2024-07-26T10:30:00Z'
                },
                {
                    id: 5,
                    nickname: '스핀마스터',
                    email: 'spinmaster@example.com',
                    cyber_token_balance: 450,
                    current_rank: 'BASIC',
                    is_verified: true,
                    is_active: false,
                    created_at: '2024-05-20T16:00:00Z',
                    last_login: '2024-07-20T09:15:00Z'
                }
            ];

            // 필터링 적용
            let filteredUsers = testUsers;

            if (searchTerm) {
                filteredUsers = filteredUsers.filter(user =>
                    user.nickname.toLowerCase().includes(searchTerm.toLowerCase()) ||
                    user.email.toLowerCase().includes(searchTerm.toLowerCase())
                );
            }

            if (filterRank !== 'ALL') {
                filteredUsers = filteredUsers.filter(user => user.current_rank === filterRank);
            }

            if (filterStatus !== 'ALL') {
                if (filterStatus === 'ACTIVE') {
                    filteredUsers = filteredUsers.filter(user => user.is_active);
                } else if (filterStatus === 'INACTIVE') {
                    filteredUsers = filteredUsers.filter(user => !user.is_active);
                }
            }

            setUsers(filteredUsers);
            setTotalPages(Math.ceil(filteredUsers.length / usersPerPage));

        } catch (err) {
            console.error('Error fetching users:', err);
            setError('사용자 목록을 불러오는데 실패했습니다.');
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
            minute: '2-digit'
        });
    };

    const getRankBadge = (rank: string) => {
        const colors = {
            'VIP': 'bg-yellow-600 text-yellow-100',
            'PREMIUM': 'bg-purple-600 text-purple-100',
            'BASIC': 'bg-green-600 text-green-100',
            'ADMIN': 'bg-blue-600 text-blue-100',
            'SUPER_ADMIN': 'bg-red-600 text-red-100'
        };
        return colors[rank as keyof typeof colors] || 'bg-gray-600 text-gray-100';
    };

    const getStatusBadge = (isActive: boolean) => {
        return isActive
            ? 'bg-green-600 text-green-100'
            : 'bg-red-600 text-red-100';
    };

    // 페이지네이션을 위한 현재 페이지 사용자들
    const currentUsers = users.slice(
        (currentPage - 1) * usersPerPage,
        currentPage * usersPerPage
    );

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center">
                <div className="text-white text-xl flex items-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                    사용자 목록을 불러오는 중...
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Compact Header */}
            <div className="bg-gray-800 border-b border-gray-700 px-4 py-2 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <Link href="/admin" className="text-gray-400 hover:text-white transition-colors">
                        <ChevronLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-lg font-bold">사용자 관리</h1>
                        <p className="text-gray-400 text-xs">총 {users.length}명</p>
                    </div>
                </div>

                {/* Inline Filters */}
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
                        value={filterRank}
                        onChange={(e) => setFilterRank(e.target.value)}
                        className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                    >
                        <option value="ALL">모든 등급</option>
                        <option value="VIP">VIP</option>
                        <option value="PREMIUM">PREMIUM</option>
                        <option value="BASIC">BASIC</option>
                    </select>
                    <select
                        value={filterStatus}
                        onChange={(e) => setFilterStatus(e.target.value)}
                        className="bg-gray-700 border border-gray-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:border-blue-500"
                    >
                        <option value="ALL">모든 상태</option>
                        <option value="ACTIVE">활성</option>
                        <option value="INACTIVE">비활성</option>
                    </select>
                </div>
            </div>

            {/* Dense Users Table */}
            <div className="p-4 h-[calc(100vh-80px)] overflow-auto">
                {error ? (
                    <div className="text-center py-8">
                        <div className="text-red-500 text-lg mb-4">{error}</div>
                        <button
                            onClick={fetchUsers}
                            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors"
                        >
                            다시 시도
                        </button>
                    </div>
                ) : (
                    <div className="bg-gray-800 rounded border border-gray-700 overflow-hidden">
                        <table className="w-full text-sm">
                            <thead className="bg-gray-700">
                                <tr>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">ID</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">사용자</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">이메일</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">토큰</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">등급</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">상태</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">가입일</th>
                                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-300">마지막 로그인</th>
                                    <th className="px-3 py-2 text-center text-xs font-medium text-gray-300">작업</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {currentUsers.map((user) => (
                                    <tr key={user.id} className="hover:bg-gray-700 transition-colors">
                                        <td className="px-3 py-2 text-gray-400">{user.id}</td>
                                        <td className="px-3 py-2">
                                            <div className="flex items-center">
                                                <div className="font-medium text-white">
                                                    {user.nickname}
                                                    {user.is_verified && <Shield className="inline w-3 h-3 text-blue-400 ml-1" />}
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-3 py-2 text-gray-400">{user.email}</td>
                                        <td className="px-3 py-2">
                                            <span className="font-bold text-yellow-400">
                                                {user.cyber_token_balance.toLocaleString()}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2">
                                            <span className={`px-2 py-1 text-xs rounded ${getRankBadge(user.current_rank)}`}>
                                                {user.current_rank}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2">
                                            <span className={`px-2 py-1 text-xs rounded ${getStatusBadge(user.is_active)}`}>
                                                {user.is_active ? '활성' : '비활성'}
                                            </span>
                                        </td>
                                        <td className="px-3 py-2 text-gray-400 text-xs">
                                            {new Date(user.created_at).toLocaleDateString('ko-KR')}
                                        </td>
                                        <td className="px-3 py-2 text-gray-400 text-xs">
                                            {user.last_login ? new Date(user.last_login).toLocaleDateString('ko-KR') : '-'}
                                        </td>
                                        <td className="px-3 py-2">
                                            <div className="flex justify-center space-x-1">
                                                <Link
                                                    href={`/admin/users/${user.id}`}
                                                    className="text-blue-400 hover:text-blue-300 p-1 rounded hover:bg-blue-400/10 transition-colors"
                                                    title="상세 보기"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </Link>
                                                <button
                                                    className="text-green-400 hover:text-green-300 p-1 rounded hover:bg-green-400/10 transition-colors"
                                                    title="보상 지급"
                                                >
                                                    <Gift className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Compact Pagination */}
                        {totalPages > 1 && (
                            <div className="bg-gray-700 px-4 py-2 border-t border-gray-600 flex items-center justify-between text-sm">
                                <span className="text-gray-400">
                                    {((currentPage - 1) * usersPerPage) + 1}-{Math.min(currentPage * usersPerPage, users.length)} / {users.length}
                                </span>
                                <div className="flex space-x-1">
                                    <button
                                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                        disabled={currentPage === 1}
                                        className="px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <ChevronLeft className="w-4 h-4" />
                                    </button>
                                    <span className="px-2 py-1 bg-blue-600 text-white rounded text-xs">
                                        {currentPage}
                                    </span>
                                    <button
                                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                        disabled={currentPage === totalPages}
                                        className="px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <ChevronRight className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminUsersPage;
