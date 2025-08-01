'use client';

import { Metadata } from 'next';
import AdminLoginForm from '../../../components/auth/AdminLoginForm';
import { Suspense } from 'react';

export default function AdminLoginPage() {
    return (
        <div className="auth-container">
            <div className="auth-card">
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
