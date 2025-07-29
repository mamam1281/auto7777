"""
JWT 인증 시스템 단위 테스트
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from jose import jwt

from app.auth.jwt_auth import (
    create_jwt_token, create_tokens, get_current_user, 
    get_user_by_rank, refresh_access_token,
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)

# 테스트용 사용자 데이터
TEST_USER_ID = 1
TEST_USER_RANK = "VIP"


def test_create_jwt_token():
    """JWT 토큰 생성 테스트"""
    # 토큰 생성 테스트
    data = {"sub": str(TEST_USER_ID), "rank": TEST_USER_RANK}
    expires = timedelta(minutes=15)
    
    token = create_jwt_token(data=data, expires_delta=expires)
    
    # 토큰 검증
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == str(TEST_USER_ID)
    assert payload["rank"] == TEST_USER_RANK
    assert "exp" in payload


def test_create_tokens():
    """액세스 토큰 및 리프레시 토큰 생성 테스트"""
    # 토큰 세트 생성
    tokens = create_tokens(user_id=TEST_USER_ID, rank=TEST_USER_RANK)
    
    # 액세스 토큰 검증
    access_payload = jwt.decode(tokens.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert access_payload["sub"] == str(TEST_USER_ID)
    assert access_payload["rank"] == TEST_USER_RANK
    assert "exp" in access_payload
    
    # 리프레시 토큰 검증
    refresh_payload = jwt.decode(tokens.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert refresh_payload["sub"] == str(TEST_USER_ID)
    assert refresh_payload.get("refresh") is True
    assert "exp" in refresh_payload
    
    # 만료 시간 확인
    assert tokens.token_type == "bearer"
    assert tokens.expires_at > int(time.time())


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """유효한 토큰으로 현재 사용자 가져오기 테스트"""
    # 테스트용 DB 세션 목 생성
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = MagicMock(
        id=TEST_USER_ID, 
        nickname="testuser", 
        rank=TEST_USER_RANK
    )
    
    # 테스트용 토큰 생성
    token = create_jwt_token(
        data={"sub": str(TEST_USER_ID), "rank": TEST_USER_RANK},
        expires_delta=timedelta(minutes=30)
    )
    
    # 현재 사용자 가져오기 테스트
    user = await get_current_user(token=token, db=mock_db)
    
    assert user.id == TEST_USER_ID
    assert user.nickname == "testuser"
    assert user.rank == TEST_USER_RANK
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """유효하지 않은 토큰으로 현재 사용자 가져오기 실패 테스트"""
    # 테스트용 DB 세션 목 생성
    mock_db = MagicMock()
    
    # 잘못된 토큰으로 테스트
    invalid_token = "invalid.jwt.token"
    
    # 예외 발생 확인
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=invalid_token, db=mock_db)
    
    assert exc.value.status_code == 401
    assert "인증 정보가 유효하지 않습니다" in str(exc.value.detail)


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """만료된 토큰으로 현재 사용자 가져오기 실패 테스트"""
    # 테스트용 DB 세션 목 생성
    mock_db = MagicMock()
    
    # 만료된 토큰 생성
    expired_token = create_jwt_token(
        data={"sub": str(TEST_USER_ID), "rank": TEST_USER_RANK},
        expires_delta=timedelta(minutes=-1)  # 이미 만료
    )
    
    # 예외 발생 확인
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token=expired_token, db=mock_db)
    
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_rank_sufficient_rank():
    """충분한 등급의 사용자 접근 허용 테스트"""
    # 테스트 설정
    current_user = MagicMock(id=TEST_USER_ID, rank="VIP")
    
    # VIP 사용자가 STANDARD 요구사항에 접근
    user_check = get_user_by_rank(required_rank="STANDARD")
    user = await user_check(current_user=current_user)
    
    assert user.id == TEST_USER_ID
    assert user.rank == "VIP"
    
    # VIP 사용자가 PREMIUM 요구사항에 접근
    user_check = get_user_by_rank(required_rank="PREMIUM")
    user = await user_check(current_user=current_user)
    
    assert user.id == TEST_USER_ID
    assert user.rank == "VIP"
    
    # VIP 사용자가 VIP 요구사항에 접근
    user_check = get_user_by_rank(required_rank="VIP")
    user = await user_check(current_user=current_user)
    
    assert user.id == TEST_USER_ID
    assert user.rank == "VIP"


@pytest.mark.asyncio
async def test_get_user_by_rank_insufficient_rank():
    """불충분한 등급의 사용자 접근 거부 테스트"""
    # 테스트 설정
    current_user = MagicMock(id=TEST_USER_ID, rank="STANDARD")
    
    # STANDARD 사용자가 PREMIUM 요구사항에 접근
    user_check = get_user_by_rank(required_rank="PREMIUM")
    
    # 예외 발생 확인
    with pytest.raises(HTTPException) as exc:
        await user_check(current_user=current_user)
    
    assert exc.value.status_code == 403
    assert "접근 권한이 부족합니다" in str(exc.value.detail)
    
    # STANDARD 사용자가 VIP 요구사항에 접근
    user_check = get_user_by_rank(required_rank="VIP")
    
    # 예외 발생 확인
    with pytest.raises(HTTPException) as exc:
        await user_check(current_user=current_user)
    
    assert exc.value.status_code == 403


def test_refresh_access_token_valid():
    """유효한 리프레시 토큰으로 액세스 토큰 갱신 테스트"""
    # 테스트용 DB 세션 목 생성
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = MagicMock(
        id=TEST_USER_ID, 
        rank=TEST_USER_RANK
    )
    
    # 리프레시 토큰 생성
    refresh_token = create_jwt_token(
        data={"sub": str(TEST_USER_ID), "refresh": True},
        expires_delta=timedelta(days=7)
    )
    
    # 리프레시 토큰으로 새 토큰 세트 얻기
    tokens = refresh_access_token(refresh_token=refresh_token, db=mock_db)
    
    # 새 액세스 토큰 검증
    access_payload = jwt.decode(tokens.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert access_payload["sub"] == str(TEST_USER_ID)
    assert access_payload["rank"] == TEST_USER_RANK
    assert "exp" in access_payload
    
    # 새 리프레시 토큰 검증
    refresh_payload = jwt.decode(tokens.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert refresh_payload["sub"] == str(TEST_USER_ID)
    assert refresh_payload.get("refresh") is True
    assert "exp" in refresh_payload
