// Backend API Response Types
export interface User {
  id: number;
  email: string;
  nickname?: string;
  cyber_token_balance: number;
  segment_label: string;
  created_at: string;
}

export interface AdultContentGalleryItem {
  id: number;
  name: string;
  title: string;
  description: string;
  thumbnail_url: string;
  preview_url: string;
  content_type: string;
  stage_required: string;
  highest_unlocked_stage?: string;
  is_unlocked: boolean;
}

export interface GameResponse {
  id: number;
  name: string;
  type: 'slot' | 'roulette' | 'gacha' | 'poker' | 'blackjack';
  description?: string;
  min_bet: number;
  max_bet: number;
  rules: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ContentUnlockResponse {
  success: boolean;
  status: string;
  message: string;
  content_url?: string;
  unlocked_stage?: number;
  tokens_spent?: number;
  remaining_tokens?: number;
}

export interface FlashOfferResponseItem {
  id: number;
  title: string;
  description: string;
  original_price: number;
  discounted_price: number;
  discount_percentage: number;
  valid_until: string;
  is_active: boolean;
}

// API Request Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

export interface ContentUnlockRequest {
  content_id: number;
  stage_to_unlock: number;
}

export interface GamePlayRequest {
  game_id: number;
  bet_amount: number;
  options?: Record<string, any>;
}
