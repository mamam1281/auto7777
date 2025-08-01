import { Metadata } from 'next';
import { Suspense } from 'react';
import AdminLoginForm from '../../../components/auth/AdminLoginForm';

export const metadata: Metadata = {
    title: '관리자 로그인 - 모델카지노',
    description: '관리자 전용 로그인 페이지',
};

export default function AdminLoginPage() {
    return (
        <div className="w-full max-w-[420px] mx-auto min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-auto">
            <div className="auth-card" style={{ padding: '20px', boxSizing: 'border-box' }}>
                <Suspense fallback={null}>
                    <AdminLoginForm
                        onSwitchToLogin={() => {
                            window.location.href = '/auth';
                        }}
                    />
                </Suspense>
            </div>
        </div>
    );
}
