-- Casino-Club F2P Database Status Check Queries (English Version)
-- Quick database status check queries for development environment

-- 1. Basic table list and record counts
SELECT 
    schemaname,
    tablename,
    n_tup_ins as "total_inserts",
    n_tup_upd as "total_updates", 
    n_tup_del as "total_deletes",
    n_live_tup as "current_records",
    n_dead_tup as "deleted_records"
FROM pg_stat_user_tables 
ORDER BY schemaname, tablename;

-- 2. User overview
SELECT 
    COUNT(*) as "total_users",
    COUNT(CASE WHEN vip_tier = 'STANDARD' THEN 1 END) as "standard_users",
    COUNT(CASE WHEN vip_tier = 'VIP' THEN 1 END) as "vip_users", 
    COUNT(CASE WHEN vip_tier = 'PREMIUM' THEN 1 END) as "premium_users",
    COUNT(CASE WHEN last_login > CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 1 END) as "active_24h"
FROM users;

-- 3. User details
SELECT 
    u.nickname,
    u.vip_tier,
    u.regular_coins,
    u.premium_gems,
    u.battlepass_level,
    us.rfm_group,
    us.ltv_score,
    u.last_login
FROM users u
LEFT JOIN user_segments us ON u.id = us.user_id
ORDER BY u.created_at DESC;

-- 4. User actions stats (last 24 hours)
SELECT 
    action_type,
    COUNT(*) as "action_count",
    COUNT(DISTINCT user_id) as "unique_users"
FROM user_actions 
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY action_type
ORDER BY COUNT(*) DESC;

-- 5. Rewards distribution
SELECT 
    reward_type,
    COUNT(*) as "reward_count",
    SUM(reward_amount) as "total_amount",
    AVG(reward_amount::decimal) as "avg_amount"
FROM user_rewards
WHERE claimed_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY reward_type
ORDER BY SUM(reward_amount) DESC;

-- 6. Gacha statistics  
SELECT 
    gacha_type,
    COUNT(*) as "total_spins",
    SUM(cost_gems) as "total_gems_spent",
    AVG(cost_gems::decimal) as "avg_gems_per_spin"
FROM gacha_log
GROUP BY gacha_type
ORDER BY COUNT(*) DESC;

-- 7. Shop transactions
SELECT 
    item_type,
    COUNT(*) as "transaction_count",
    SUM(COALESCE(cost_gems, 0)) as "total_gems_spent",
    SUM(COALESCE(cost_coins, 0)) as "total_coins_spent"
FROM shop_transactions
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY item_type
ORDER BY COUNT(*) DESC;

-- 8. Battle pass progress
SELECT 
    bs.season_id,
    COUNT(*) as "participants",
    COUNT(CASE WHEN bs.is_premium THEN 1 END) as "premium_buyers",
    AVG(bs.current_level::decimal) as "avg_level",
    MAX(bs.current_level) as "max_level"
FROM battlepass_status bs
GROUP BY bs.season_id
ORDER BY bs.season_id;

-- 9. Notification stats
SELECT 
    notification_type,
    COUNT(*) as "total_sent",
    COUNT(CASE WHEN is_read THEN 1 END) as "read_count",
    ROUND((COUNT(CASE WHEN is_read THEN 1 END)::decimal / COUNT(*) * 100), 2) as "read_rate_percent"
FROM notifications
WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY notification_type
ORDER BY COUNT(*) DESC;

-- 10. Database connection info
SELECT 
    current_database() as "current_db",
    current_user as "current_user",
    inet_server_addr() as "server_address",
    inet_server_port() as "server_port",
    version() as "postgresql_version";
