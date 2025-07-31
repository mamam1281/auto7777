// 브라우저 개발자 도구 콘솔에서 실행할 코드
// F12 -> Console 탭에서 아래 코드를 복사해서 실행하세요

console.log('🧹 브라우저 localStorage 정리 시작...');

// 모든 localStorage 데이터 삭제
localStorage.clear();

// 세션 스토리지도 정리
sessionStorage.clear();

// 쿠키도 정리 (현재 도메인)
document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
});

console.log('✅ 모든 브라우저 데이터 정리 완료!');
console.log('🔄 페이지를 새로고침합니다...');

// 페이지 새로고침
setTimeout(() => {
    window.location.reload();
}, 1000);
