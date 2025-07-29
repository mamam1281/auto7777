"""
Swagger API 문서화 설정 모듈
"""

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles


def setup_api_docs(app: FastAPI, title: str, version: str, description: str = None):
    """
    FastAPI 애플리케이션에 Swagger 및 ReDoc 문서화 설정

    Args:
        app: FastAPI 애플리케이션 인스턴스
        title: API 제목
        version: API 버전
        description: API 설명 (선택적)
    """
    # OpenAPI 스키마 설정
    app.title = title
    app.version = version
    if description:
        app.description = description
    
    # 정적 파일 설정 (Swagger UI의 JS, CSS 파일용)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Swagger UI 커스텀 설정
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        """커스텀 Swagger UI HTML 생성"""
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
            swagger_favicon_url="/static/favicon.png",
        )
    
    # Swagger UI OAuth 리디렉션 설정
    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    async def swagger_ui_redirect():
        """Swagger UI OAuth 리디렉션"""
        return get_swagger_ui_oauth2_redirect_html()
    
    # ReDoc 설정
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        """ReDoc HTML 생성"""
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - ReDoc",
            redoc_js_url="/static/redoc.standalone.js",
            redoc_favicon_url="/static/favicon.png",
        )
    
    return app


def customize_openapi(app: FastAPI):
    """
    OpenAPI 스키마 사용자 정의 설정
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    
    Returns:
        커스터마이징된 OpenAPI 스키마 함수
    """
    # 기본 OpenAPI 스키마 저장
    openapi_schema = app.openapi()
    
    # API 태그에 대한 메타데이터 추가
    if "tags" not in openapi_schema:
        openapi_schema["tags"] = []
    
    # API 태그 정보 설정
    tags_metadata = [
        {
            "name": "users",
            "description": "사용자 관리 및 인증 관련 API 엔드포인트"
        },
        {
            "name": "games",
            "description": "게임 관련 API 엔드포인트"
        },
        {
            "name": "rewards",
            "description": "보상 및 이벤트 관련 API 엔드포인트"
        },
        {
            "name": "admin",
            "description": "관리자 전용 API 엔드포인트"
        }
    ]
    
    openapi_schema["tags"] = tags_metadata
    
    # 보안 스키마 설정
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT 인증 토큰 입력 (Bearer {token})"
        }
    }
    
    # 기본 보안 요구사항 설정
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # 커스터마이징된 스키마를 반환하는 함수
    def custom_openapi():
        return openapi_schema
    
    return custom_openapi
