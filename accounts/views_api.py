# accounts/views_api.py
import os
import json
import sys
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import login, logout, get_user_model
from supabase import create_client, Client

User = get_user_model()

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY are missing.")
    return create_client(url, key)

def get_request_data(request):
    if request.content_type == 'application/json':
        try:
            return json.loads(request.body)
        except:
            return {}
    return request.POST

@ensure_csrf_cookie
def csrf_api_view(request):
    return JsonResponse({"success": True})

@csrf_exempt
@require_POST
def signup_api_view(request):
    try:
        data = get_request_data(request)
        email = data.get("email")
        password = data.get("password") or data.get("password1")
        username = data.get("username")
        
        sys.stderr.write(f"DEBUG: Signup attempt for {email}\n")

        if not email or not password:
            return JsonResponse({"success": False, "error": "Email and password are required"}, status=400)
            
        # Django DB 동기화 전 사전 체크 (중복 유저네임 방지)
        if username and User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": f"Username '{username}' is already taken."}, status=400)

        supabase = get_supabase_client()
        # 최신 버전 표준 호출 방식
        res = supabase.auth.sign_up({
            "email": email, 
            "password": password,
            "options": {"data": {"username": username}}
        })
        
        # Django DB 동기화
        if not User.objects.filter(email=email).exists():
            User.objects.create_user(username=username or email.split('@')[0], email=email, password=password)

        msg = "Signup successful."
        if res.session is None:
            msg += " Please check your email for confirmation link."

        return JsonResponse({"success": True, "message": msg})
    except Exception as e:
        sys.stderr.write(f"ERROR Signup: {str(e)}\n")
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@csrf_exempt
@require_POST
def login_api_view(request):
    try:
        data = get_request_data(request)
        email = data.get("email")
        password = data.get("password")
        
        sys.stderr.write(f"DEBUG: Login attempt for {email}\n")

        if not email or not password:
            return JsonResponse({"success": False, "error": "Email and password are required"}, status=400)
            
        supabase = get_supabase_client()
        # 최신 버전 표준 호출 방식 (credentials 키워드 제거)
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # Django 세션 처리
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(username=email.split('@')[0], email=email)
        
        login(request, user)

        return JsonResponse({
            "success": True,
            "access_token": res.session.access_token,
            "user": {"id": user.id, "username": user.username, "email": user.email}
        })
    except Exception as e:
        err_msg = str(e)
        sys.stderr.write(f"ERROR Login: {err_msg}\n")
        # 이메일 인증 안 됨 등의 구체적 사유 포함
        return JsonResponse({"success": False, "error": err_msg}, status=401)

@csrf_exempt
@require_POST
def logout_api_view(request):
    try:
        try:
            supabase = get_supabase_client()
            supabase.auth.sign_out()
        except:
            pass
        logout(request)
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

@require_GET
def me_api_view(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "success": True, 
            "is_authenticated": True,
            "id": request.user.id, 
            "username": request.user.username,
            "email": request.user.email
        })
    return JsonResponse({"success": False, "is_authenticated": False}, status=401)
