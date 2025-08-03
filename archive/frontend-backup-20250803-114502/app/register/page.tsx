// /app/register/page.tsx
'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RegisterRedirect() {
  const router = useRouter();
  useEffect(() => {
    router.replace('/auth/register');
  }, [router]);
  return null;
}
