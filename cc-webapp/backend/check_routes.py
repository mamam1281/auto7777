#!/usr/bin/env python3
"""
등록된 라우트 확인 스크립트
"""

import sys
sys.path.append('/app')

from app.main import app

def check_routes():
    print("🔍 등록된 admin 관련 라우트들:")
    admin_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path'):
            if 'admin' in route.path.lower():
                methods = getattr(route, 'methods', {'GET'})
                admin_routes.append(f"{list(methods)} {route.path}")
    
    if admin_routes:
        for route in admin_routes:
            print(f"  ✅ {route}")
    else:
        print("  ❌ admin 관련 라우트를 찾을 수 없습니다.")
    
    print(f"\n📊 전체 라우트 수: {len([r for r in app.routes if hasattr(r, 'path')])}")

if __name__ == "__main__":
    check_routes()
