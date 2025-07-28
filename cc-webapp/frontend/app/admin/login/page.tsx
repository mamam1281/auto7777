'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../lib/auth';

const AdminLoginPage = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [formData, setFormData] = useState({
        site_id: '',
        password: '',
    });
    const [error, setError] = useState('');

    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch(`http://localhost:8000/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    site_id: formData.site_id,
                    password: formData.password
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || '관리자 인증 실패');
            }

            const data = await response.json();

            // 강제 관리자 로그인 처리 (단순화)
            const adminData = {
                id: 1,
                site_id: formData.site_id,
                nickname: "관리자",
                phone_number: "010-0000-0000",
                cyber_token_balance: 999999,
                rank: "ADMIN"
            };

            // 로컬 스토리지에 직접 저장
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('user', JSON.stringify(adminData));

            // 관리자 페이지로 이동
            router.push('/admin');

        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="bg-gray-800 p-8 rounded-lg border border-gray-700 w-96">
                <h1 className="text-2xl font-bold text-white mb-6 text-center">
                    관리자 로그인
                </h1>

                {error && (
                    <div className="bg-red-600 text-white p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="admin-site-id" className="block text-gray-300 text-sm mb-2">관리자 ID</label>
                        <input
                            id="admin-site-id"
                            type="text"
                            value={formData.site_id}
                            onChange={(e) => setFormData({ ...formData, site_id: e.target.value })}
                            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                            required
                        />
                    </div>

                    <div>
                        <label htmlFor="admin-password" className="block text-gray-300 text-sm mb-2">비밀번호</label>
                        <input
                            id="admin-password"
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white py-3 px-4 rounded transition-colors"
                    >
                        {isLoading ? '처리 중...' : '관리자 로그인'}
                    </button>
                </form>

                <div className="mt-4 text-center">
                    <button
                        onClick={() => router.push('/auth')}
                        className="text-blue-400 hover:text-blue-300 text-sm"
                    >
                        일반 로그인으로 돌아가기
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdminLoginPage;
