-- Casino-Club F2P Database 개발용 테스트 데이터
-- 테스트 및 개발을 위한 샘플 데이터 생성

-- 추가 테스트 사용자 생성
INSERT INTO users (nickname, email, invite_code, vip_tier, regular_coins, premium_gems, play_xp, battlepass_level) 
VALUES 
    ('whale_player', 'whale@casino-club.com', 'WHALE001', 'PREMIUM', 1000000, 10000, 5000, 25),
    ('casual_gamer', 'casual@example.com', 'CASUAL01', 'STANDARD', 15000, 50, 800, 5),
    ('high_roller', 'roller@casino-club.com', 'ROLL001', 'VIP', 500000, 2500, 3200, 18),
    ('newbie_user', 'newbie@example.com', 'NEW001', 'STANDARD', 1000, 10, 50, 1),
    ('dormant_user', 'dormant@example.com', 'DORM001', 'STANDARD', 800, 0, 100, 2)
ON CONFLICT (nickname) DO NOTHING;

-- 사용자 세그먼트 업데이트
UPDATE user_segments SET 
    rfm_group = 'Whale', 
    ltv_score = 2500.00, 
    risk_profile = 'High'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'whale_player');

UPDATE user_segments SET 
    rfm_group = 'High_Engaged', 
    ltv_score = 450.00, 
    risk_profile = 'Medium'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'high_roller');

UPDATE user_segments SET 
    rfm_group = 'Medium', 
    ltv_score = 120.00, 
    risk_profile = 'Low'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'casual_gamer');

UPDATE user_segments SET 
    rfm_group = 'At_Risk', 
    ltv_score = 25.00, 
    risk_profile = 'Low'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'dormant_user');

-- 사용자 액션 로그 샘플 데이터
INSERT INTO user_actions (user_id, action_type, action_data) 
SELECT 
    u.id, 
    'SLOT_SPIN',
    jsonb_build_object('bet_amount', 100, 'result', 'win', 'payout', 300)
FROM users u WHERE u.nickname IN ('whale_player', 'high_roller', 'casual_gamer');

INSERT INTO user_actions (user_id, action_type, action_data) 
SELECT 
    u.id, 
    'GACHA_SPIN',
    jsonb_build_object('gacha_type', 'premium', 'cost', 50, 'items', '["rare_item", "common_item"]')
FROM users u WHERE u.nickname IN ('whale_player', 'high_roller');

INSERT INTO user_actions (user_id, action_type, action_data) 
SELECT 
    u.id, 
    'SHOP_PURCHASE',
    jsonb_build_object('item', 'gem_pack_500', 'cost_usd', 9.99)
FROM users u WHERE u.nickname = 'whale_player';

-- 리워드 로그 샘플 데이터
INSERT INTO user_rewards (user_id, reward_type, reward_amount, source_action)
SELECT 
    u.id,
    'REGULAR_COINS',
    300,
    'SLOT_SPIN'
FROM users u WHERE u.nickname IN ('whale_player', 'high_roller', 'casual_gamer');

INSERT INTO user_rewards (user_id, reward_type, reward_amount, source_action)
SELECT 
    u.id,
    'PREMIUM_GEMS',
    10,
    'DAILY_LOGIN'
FROM users u WHERE u.nickname IN ('whale_player', 'high_roller');

-- 가챠 로그 샘플 데이터
INSERT INTO gacha_log (user_id, gacha_type, cost_gems, result_items)
SELECT 
    u.id,
    'premium_box',
    50,
    jsonb_build_array(
        jsonb_build_object('type', 'character', 'rarity', 'rare', 'name', 'Neon Warrior'),
        jsonb_build_object('type', 'currency', 'rarity', 'common', 'amount', 1000)
    )
FROM users u WHERE u.nickname = 'whale_player';

-- 상점 거래 로그
INSERT INTO shop_transactions (user_id, item_type, item_id, cost_gems)
SELECT 
    u.id,
    'gem_pack',
    'pack_500',
    0  -- 실제로는 현금 결제
FROM users u WHERE u.nickname = 'whale_player';

-- 알림 샘플 데이터
INSERT INTO notifications (user_id, notification_type, title, message, data)
SELECT 
    u.id,
    'REWARD',
    '일일 보상 도착!',
    '오늘의 로그인 보상으로 젬 10개와 코인 1000개를 받았습니다.',
    jsonb_build_object('reward_gems', 10, 'reward_coins', 1000)
FROM users u;

INSERT INTO notifications (user_id, notification_type, title, message, data)
SELECT 
    u.id,
    'PROMOTION',
    '🎰 특별 이벤트 진행 중!',
    '이번 주말 한정! 슬롯머신에서 2배 보상을 받아보세요.',
    jsonb_build_object('event_type', 'double_slot_reward', 'end_date', '2025-08-03')
FROM users u WHERE u.vip_tier IN ('VIP', 'PREMIUM');

-- 배틀패스 상태 업데이트
UPDATE battlepass_status SET 
    current_level = 25,
    current_xp = 4800,
    is_premium = true,
    premium_purchased_at = CURRENT_TIMESTAMP - INTERVAL '5 days'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'whale_player');

UPDATE battlepass_status SET 
    current_level = 18,
    current_xp = 3100,
    is_premium = true,
    premium_purchased_at = CURRENT_TIMESTAMP - INTERVAL '2 days'
WHERE user_id = (SELECT id FROM users WHERE nickname = 'high_roller');

-- 마지막 로그인 시간 업데이트
UPDATE users SET 
    last_login = CURRENT_TIMESTAMP - INTERVAL '1 hour'
WHERE nickname IN ('whale_player', 'high_roller', 'casual_gamer');

UPDATE users SET 
    last_login = CURRENT_TIMESTAMP - INTERVAL '5 days'
WHERE nickname = 'dormant_user';

-- 통계 업데이트
ANALYZE users;
ANALYZE user_segments;
ANALYZE user_actions;
ANALYZE user_rewards;
ANALYZE gacha_log;
ANALYZE shop_transactions;
ANALYZE battlepass_status;
ANALYZE notifications;
