#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👤 사용자 관리 API 라우터 (완전한 기능 버전)
사용자 프로필, 세그먼트, 진행상황 관리를 위한 통합 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from .. import models
from ..database import get_db
from ..services.user_service import UserService
from ..services.user_segment_service import UserSegmentService
from ..schemas.user import (
    UserResponse, 
    UserProfileResponse, 
    UserProgressResponse, 
    UserStatisticsResponse, 
    UserSegmentResponse,
    UserUpdateRequest
)
from ..dependencies import get_current_user

router = APIRouter()


# === 사용자 프로필 관리 ===

@router.get("/profile", response_model=UserProfileResponse, tags=["User Profile"])
async def get_user_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """현재 사용자의 프로필 정보 조회"""
    try:
        user_service = UserService(db)
        profile_data = user_service.get_user_profile(current_user.id)
        
        return UserProfileResponse(**profile_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 조회 실패: {str(e)}"
        )


@router.put("/profile", response_model=UserProfileResponse, tags=["User Profile"])
async def update_user_profile(
    update_data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """사용자 프로필 업데이트"""
    try:
        user_service = UserService(db)
        updated_profile = user_service.update_user_profile(
            current_user.id, 
            update_data.dict(exclude_unset=True)
        )
        
        return UserProfileResponse(**updated_profile)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 업데이트 실패: {str(e)}"
        )


# === 사용자 세그먼트 관리 ===

@router.get("/segment", response_model=UserSegmentResponse, tags=["User Segmentation"])
async def get_user_segment(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """현재 사용자의 세그먼트 정보 조회"""
    try:
        segment_service = UserSegmentService(db)
        segment_label = segment_service.get_segment_label(current_user.id)
        
        return UserSegmentResponse(
            user_id=current_user.id,
            segment=segment_label,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세그먼트 조회 실패: {str(e)}"
        )


# === 사용자 진행상황 ===

@router.get("/progress", response_model=UserProgressResponse, tags=["User Progress"])
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """현재 사용자의 진행상황 조회"""
    try:
        user_service = UserService(db)
        progress_data = user_service.get_user_progress(current_user.id)
        
        return UserProgressResponse(**progress_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"진행상황 조회 실패: {str(e)}"
        )


# === 사용자 통계 ===

@router.get("/statistics", response_model=UserStatisticsResponse, tags=["User Statistics"])
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """현재 사용자의 통계 정보 조회"""
    try:
        user_service = UserService(db)
        stats_data = user_service.get_user_statistics(current_user.id)
        
        return UserStatisticsResponse(**stats_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 실패: {str(e)}"
        )


# === 계정 관리 ===

@router.delete("/account", tags=["Account Management"])
async def delete_user_account(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """사용자 계정 삭제 (소프트 삭제)"""
    try:
        user_service = UserService(db)
        result = user_service.soft_delete_user(current_user.id)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"계정 삭제 실패: {str(e)}"
        )


# === 관리자 전용 엔드포인트 ===

@router.get("/admin/users", response_model=List[UserResponse], tags=["Admin"])
async def get_all_users(
    skip: int = Query(0, ge=0, description="건너뛸 사용자 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 사용자 수"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """모든 사용자 목록 조회 (관리자 전용)"""
    # TODO: 관리자 권한 확인 로직 추가
    try:
        user_service = UserService(db)
        users_data = user_service.get_all_users(skip=skip, limit=limit)
        
        return [UserResponse(**user_data) for user_data in users_data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 실패: {str(e)}"
        )


@router.get("/admin/users/{user_id}", response_model=UserResponse, tags=["Admin"])
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """특정 사용자 정보 조회 (관리자 전용)"""
    # TODO: 관리자 권한 확인 로직 추가
    try:
        user_service = UserService(db)
        user_data = user_service.get_user_by_id(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        return UserResponse(**user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 조회 실패: {str(e)}"
        )


# === 추가 유틸리티 엔드포인트 ===

@router.get("/me", response_model=UserResponse, tags=["User Profile"])
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """현재 로그인한 사용자 정보 조회 (간단 버전)"""
    return UserResponse(
        id=current_user.id,
        site_id=current_user.site_id,
        nickname=current_user.nickname,
        phone_number=current_user.phone_number,
        invite_code=current_user.invite_code,
        cyber_token_balance=current_user.cyber_token_balance,
        created_at=current_user.created_at,
        rank=current_user.rank
    )


@router.get("/health", tags=["Health Check"])
async def users_health_check():
    """사용자 라우터 상태 확인"""
    return {
        "status": "healthy",
        "service": "users",
        "timestamp": datetime.utcnow(),
        "endpoints": {
            "profile": "active",
            "segment": "active", 
            "progress": "active",
            "statistics": "active",
            "admin": "active"
        }
    }
