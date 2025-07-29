#!/usr/bin/env python3
"""
Phase D: ë°±ì—”???„ë¡ ?¸ì—”???µí•© ?ŒìŠ¤??(ê°œì„ ??ë²„ì „)
- ê³ ìœ ???ŒìŠ¤???°ì´???¬ìš©
- ?„ì²´ ?Œì›ê°€????ë¡œê·¸???Œë¡œ???ŒìŠ¤??
- ?ëŸ¬ ì¼€?´ìŠ¤ ê²€ì¦?
"""

import requests
import json
import time
import random
import string
from datetime import datetime

# ?œë²„ ?¤ì •
BASE_URL = "http://127.0.0.1:8001"

def generate_unique_id(prefix="test"):
    """ê³ ìœ ???ŒìŠ¤??ID ?ì„±"""
    timestamp = int(time.time() * 1000)  # ë°€ë¦¬ì´ˆ
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_health_check():
    """?œë²„ ?íƒœ ?•ì¸"""
    print("?” ?œë²„ ?íƒœ ?•ì¸...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("???œë²„ ?íƒœ: ?•ìƒ")
            return True
        else:
            print(f"???œë²„ ?íƒœ: ?¤ë¥˜ {response.status_code}")
            return False
    except Exception as e:
        print(f"???œë²„ ?°ê²° ?¤íŒ¨: {e}")
        return False

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_invite_code_generation():
    """ì´ˆë?ì½”ë“œ ?ì„± ?ŒìŠ¤??""
    print("\n?« ì´ˆë?ì½”ë“œ ?ì„± ?ŒìŠ¤??..")
    try:
        response = requests.post(f"{BASE_URL}/api/admin/invite-codes", 
                                json={"count": 1}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            invite_code = data["codes"][0]
            print(f"??ì´ˆë?ì½”ë“œ ?ì„±: {invite_code}")
            return invite_code
        else:
            print(f"??ì´ˆë?ì½”ë“œ ?ì„± ?¤íŒ¨: {response.status_code}")
            return None
    except Exception as e:
        print(f"??ì´ˆë?ì½”ë“œ ?ì„± ?¤ë¥˜: {e}")
        return None

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_complete_user_flow():
    """?„ì „???¬ìš©???Œë¡œ???ŒìŠ¤?? ì´ˆë?ì½”ë“œ ???Œì›ê°€????ë¡œê·¸??""
    print("\n?? ?„ì „???¬ìš©???Œë¡œ???ŒìŠ¤???œì‘...")
    
    # 1. ì´ˆë?ì½”ë“œ ?ì„±
    invite_code = test_invite_code_generation()
    if not invite_code:
        return False
    
    # 2. ê³ ìœ ???ŒìŠ¤???°ì´???ì„±
    unique_site_id = generate_unique_id("user")
    test_data = {
        "site_id": unique_site_id,
        "nickname": f"?ŒìŠ¤?¸ìœ ?€_{int(time.time())}",
        "phone_number": f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "password": "test123!@#",
        "invite_code": invite_code
    }
    
    print(f"?“ ?ŒìŠ¤???°ì´?? {test_data['site_id']}, {test_data['nickname']}, {test_data['phone_number']}")
    
    # 3. ?Œì›ê°€???ŒìŠ¤??
    print("\n?‘¤ ?Œì›ê°€???ŒìŠ¤??..")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", 
                                json=test_data, timeout=10)
        if response.status_code == 200:
            signup_data = response.json()
            print(f"???Œì›ê°€???±ê³µ: {signup_data.get('message', '?±ê³µ')}")
            user_id = signup_data.get('user_id')
            print(f"   ?¬ìš©??ID: {user_id}")
        else:
            error_data = response.json()
            print(f"???Œì›ê°€???¤íŒ¨: {response.status_code}")
            print(f"   ?¤ë¥˜ ?´ìš©: {error_data.get('detail', '?????†ìŒ')}")
            return False
    except Exception as e:
        print(f"???Œì›ê°€???¤ë¥˜: {e}")
        return False
    
    # 4. ë¡œê·¸???ŒìŠ¤??
    print("\n?” ë¡œê·¸???ŒìŠ¤??..")
    login_data = {
        "site_id": test_data["site_id"],
        "password": test_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json=login_data, timeout=10)
        if response.status_code == 200:
            login_response = response.json()
            print(f"??ë¡œê·¸???±ê³µ: {login_response.get('user', {}).get('nickname', 'Unknown')}")
            print(f"   ? í° ?€?? {login_response.get('token_type', 'Unknown')}")
            return True
        else:
            error_data = response.json()
            print(f"??ë¡œê·¸???¤íŒ¨: {response.status_code}")
            print(f"   ?¤ë¥˜ ?´ìš©: {error_data.get('detail', '?????†ìŒ')}")
            return False
    except Exception as e:
        print(f"??ë¡œê·¸???¤ë¥˜: {e}")
        return False

@pytest.mark.skip(reason=" ¿ÜºÎ ¼­¹ö ¿¬°á Å×½ºÆ® - ¹èÆ÷ ½Ã Á¦¿Ü\)
def test_error_cases():
    """?ëŸ¬ ì¼€?´ìŠ¤ ?ŒìŠ¤??""
    print("\n?š¨ ?ëŸ¬ ì¼€?´ìŠ¤ ?ŒìŠ¤??..")
    
    # 1. ?˜ëª»??ì´ˆë?ì½”ë“œë¡??Œì›ê°€??
    print("1ï¸âƒ£ ?˜ëª»??ì´ˆë?ì½”ë“œ ?ŒìŠ¤??..")
    invalid_signup = {
        "site_id": generate_unique_id("invalid"),
        "nickname": "?˜ëª»?œì´ˆ?€ì½”ë“œ",
        "phone_number": "010-0000-0000",
        "password": "test123",
        "invite_code": "INVALID123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/signup", 
                                json=invalid_signup, timeout=10)
        if response.status_code == 400:
            print("???˜ëª»??ì´ˆë?ì½”ë“œ ê±°ë???)
        else:
            print(f"???ˆìƒê³??¤ë¥¸ ?‘ë‹µ: {response.status_code}")
    except Exception as e:
        print(f"???ŒìŠ¤???¤ë¥˜: {e}")
    
    # 2. ì¡´ì¬?˜ì? ?ŠëŠ” ?¬ìš©??ë¡œê·¸??
    print("2ï¸âƒ£ ì¡´ì¬?˜ì? ?ŠëŠ” ?¬ìš©??ë¡œê·¸???ŒìŠ¤??..")
    invalid_login = {
        "site_id": "nonexistent_user_12345",
        "password": "anypassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                                json=invalid_login, timeout=10)
        if response.status_code == 401:
            print("??ì¡´ì¬?˜ì? ?ŠëŠ” ?¬ìš©??ë¡œê·¸??ê±°ë???)
        else:
            print(f"???ˆìƒê³??¤ë¥¸ ?‘ë‹µ: {response.status_code}")
    except Exception as e:
        print(f"???ŒìŠ¤???¤ë¥˜: {e}")

def main():
    """ë©”ì¸ ?ŒìŠ¤???¤í–‰"""
    print("?§ª Phase D: ë°±ì—”???„ë¡ ?¸ì—”???µí•© ?ŒìŠ¤??(ê°œì„ ??ë²„ì „)")
    print("=" * 60)
    print(f"???ŒìŠ¤???œì‘ ?œê°„: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ?œë²„ ?íƒœ ?•ì¸
    if not test_health_check():
        print("???œë²„ê°€ ?¤í–‰?˜ì? ?Šì•˜?µë‹ˆ?? test_server_phase_d.pyë¥?ë¨¼ì? ?¤í–‰?˜ì„¸??")
        return
    
    # ?„ì „???¬ìš©???Œë¡œ???ŒìŠ¤??
    flow_success = test_complete_user_flow()
    
    # ?ëŸ¬ ì¼€?´ìŠ¤ ?ŒìŠ¤??
    test_error_cases()
    
    # ê²°ê³¼ ?”ì•½
    print("\n" + "=" * 60)
    print("?“Š ?ŒìŠ¤??ê²°ê³¼ ?”ì•½")
    print("=" * 60)
    if flow_success:
        print("???„ì²´ ?¬ìš©???Œë¡œ?? ?±ê³µ")
        print("??Phase D ?µí•© ?ŒìŠ¤?? ?„ë£Œ")
        print("\n?‰ ëª¨ë“  ?ŒìŠ¤?¸ê? ?±ê³µ?ˆìŠµ?ˆë‹¤!")
        print("?”œ ?¤ìŒ ?¨ê³„: ?„ë¡ ?¸ì—”???¼ê³¼ ë°±ì—”??API ?°ë™ ?ŒìŠ¤??)
    else:
        print("???„ì²´ ?¬ìš©???Œë¡œ?? ?¤íŒ¨")
        print("??Phase D ?µí•© ?ŒìŠ¤?? ë¯¸ì™„ë£?)
        print("\n?”§ ë¬¸ì œë¥??´ê²°?????¤ì‹œ ?ŒìŠ¤?¸í•˜?¸ìš”.")
    
    print(f"???ŒìŠ¤???„ë£Œ ?œê°„: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
