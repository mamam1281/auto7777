-- Casino-Club F2P Database 상태 확인 쿼리
-- 개발 환경에서 데이터베이스 상태를 빠르게 확인하기 위한 쿼리 모음

-- 1. 기본 테이블 목록 및 레코드 수 확인
SELECT 
    schemaname,
    tablename,
    n_tup_ins as "총 삽입",
    n_tup_upd as "총 업데이트", 
    n_tup_del as "총 삭제",
    n_live_tup as "현재 레코드 수",
    n_dead_tup as "삭제된 레코드 수"
FROM pg_stat_user_tables 
ORDER BY schemaname, tablename;

-- 2. 사용자 개요
SELECT 
    COUNT(*) as "총 사용자 수",
    COUNT(CASE WHEN vip_tier = 'STANDARD' THEN 1 END) as "일반 사용자",
    COUNT(CASE WHEN vip_tier = 'VIP' THEN 1 END) as "VIP 사용자", 
    COUNT(CASE WHEN vip_tier = 'PREMIUM' THEN 1 END) as "프리미엄 사용자",
    COUNT(CASE WHEN last_login > CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 1 END) as "최근 24시간 활성 사용자"
FROM users;

-- 3. 사용자별 상세 정보
SELECT 
    u.nickname as "닉네임",
    u.vip_tier as "등급",
    u.regular_coins as "일반 코인",
    u.premium_gems as "프리미엄 젬",
    u.battlepass_level as "배틀패스 레벨",
    us.rfm_group as "RFM 그룹",
    us.ltv_score as "LTV 점수",
    u.last_login as "마지막 로그인"
FROM users u
LEFT JOIN user_segments us ON u.id = us.user_id
ORDER BY u.created_at DESC;

-- 4. 사용자 액션 통계 (최근 24시간)
SELECT 
    action_type as "액션 타입",
    COUNT(*) as "실행 횟수",
    COUNT(DISTINCT user_id) as "고유 사용자 수"
FROM user_actions 
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY action_type
ORDER BY COUNT(*) DESC;

-- 5. 리워드 지급 현황
SELECT 
    reward_type as "리워드 타입",
    COUNT(*) as "지급 횟수",
    SUM(reward_amount) as "총 지급량",
    AVG(reward_amount::decimal) as "평균 지급량"
FROM user_rewards
WHERE claimed_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY reward_type
ORDER BY SUM(reward_amount) DESC;

-- 6. 가챠 통계
SELECT 
    gacha_type as "가챠 타입",
    COUNT(*) as "총 이용 횟수",
    SUM(cost_gems) as "총 소모 젬",
    AVG(cost_gems::decimal) as "평균 소모 젬"
FROM gacha_log
GROUP BY gacha_type
ORDER BY COUNT(*) DESC;

-- 7. 상점 거래 현황 
SELECT 
    item_type as "아이템 타입",
    COUNT(*) as "거래 횟수",
    SUM(COALESCE(cost_gems, 0)) as "총 소모 젬",
    SUM(COALESCE(cost_coins, 0)) as "총 소모 코인"
FROM shop_transactions
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY item_type
ORDER BY COUNT(*) DESC;

-- 8. 배틀패스 진행 상황
SELECT 
    bs.season_id as "시즌",
    COUNT(*) as "참여 사용자 수",
    COUNT(CASE WHEN bs.is_premium THEN 1 END) as "프리미엄 구매자",
    AVG(bs.current_level::decimal) as "평균 레벨",
    MAX(bs.current_level) as "최고 레벨"
FROM battlepass_status bs
GROUP BY bs.season_id
ORDER BY bs.season_id;

-- 9. 알림 현황
SELECT 
    notification_type as "알림 타입",
    COUNT(*) as "총 발송",
    COUNT(CASE WHEN is_read THEN 1 END) as "읽음",
    ROUND((COUNT(CASE WHEN is_read THEN 1 END)::decimal / COUNT(*) * 100), 2) as "읽음율 (%)"
FROM notifications
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY notification_type
ORDER BY COUNT(*) DESC;

-- 10. 데이터베이스 연결 정보
SELECT 
    current_database() as "현재 데이터베이스",
    current_user as "현재 사용자",
    inet_server_addr() as "서버 주소",
    inet_server_port() as "서버 포트",
    version() as "PostgreSQL 버전";
