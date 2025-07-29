-- Alembic 인덱스/제약조건 고도화 스크립트 (2025-07-29)
-- 주요 컬럼 인덱스 추가 및 FK/제약조건 점검

CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions (user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions (action_type);
CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp ON user_actions (timestamp);
CREATE INDEX IF NOT EXISTS idx_user_segments_user_id ON user_segments (user_id);
CREATE INDEX IF NOT EXISTS idx_user_rewards_user_id ON user_rewards (user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id);

-- FK/제약조건 점검 예시 (PostgreSQL)
ALTER TABLE user_segments
    ADD CONSTRAINT fk_user_segments_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE user_actions
    ADD CONSTRAINT fk_user_actions_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE user_rewards
    ADD CONSTRAINT fk_user_rewards_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- 필요시 추가 인덱스/제약조건 아래에 계속 추가
