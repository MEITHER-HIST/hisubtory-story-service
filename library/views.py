from __future__ import annotations
from typing import Any, Dict
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from .models import UserViewedEpisode, Bookmark
from stories.models import Cut  # 🚩 stories 앱의 Cut 모델 임포트
import urllib.parse

# CSRF 검사를 건너뛰는 세션 인증 클래스
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

def _safe_episode_id(episode: Any) -> str:
    return str(
        getattr(
            episode,
            "episode_id",
            getattr(episode, "id", getattr(episode, "pk", "")),
        )
    )

def _safe_thumbnail_url(obj: Any) -> str:
    """
    webtoon 객체의 thumbnail 필드나 cut 객체의 image 필드로부터
    URL을 안전하게 추출하고 정제합니다.
    """
    if not obj:
        return ""

    # 🚩 [수정] DB 구조에 맞게 Cut은 'image', Webtoon은 'thumbnail' 필드 참조
    thumb = getattr(obj, "image", getattr(obj, "thumbnail", None))
    if not thumb:
        return ""

    try:
        url = ""
        if hasattr(thumb, "url"):
            url = thumb.url or ""
        elif isinstance(thumb, str):
            url = thumb

        url = urllib.parse.unquote(url)

        if 'http' in url:
            if '/media/http' in url:
                url = 'http' + url.split('/media/http')[-1]
            return url

        return url
    except Exception:
        return ""

def _make_item_from_episode(episode: Any) -> Dict[str, Any]:
    webtoon = getattr(episode, "webtoon", None)
    station = getattr(webtoon, "station", None) if webtoon else None
    
    # 🚩 [수정] DB의 'cut_order' 필드를 기준으로 첫 번째 장면을 가져옵니다.
    first_cut = Cut.objects.filter(episode=episode).order_by('cut_order').first()
    
    # 1순위: 에피소드 고유 장면(Cut.image) / 2순위: 웹툰 대표 이미지(Webtoon.thumbnail)
    if first_cut and getattr(first_cut, 'image', None):
        final_image_url = _safe_thumbnail_url(first_cut)
    else:
        final_image_url = _safe_thumbnail_url(webtoon)

    return {
        "id": _safe_episode_id(episode),
        "title": getattr(episode, "subtitle", "") or f"{getattr(webtoon, 'title', '')} 에피소드",
        "stationName": getattr(station, "station_name", "알 수 없는 역") if station else "알 수 없는 역",
        "imageUrl": final_image_url,
        "content": f"{getattr(webtoon, 'title', '웹툰')}의 이야기입니다.",
    }

@api_view(["GET"])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history_api(request):
    """최근 본 기록 10개와 내 이야기(북마크) 데이터를 반환"""
    user = request.user
    from stories.models import Episode

    # 1) 최근 본 이야기 10개
    viewed_records = (
        UserViewedEpisode.objects.using('default').filter(user=user)
        .order_by("-viewed_at")[:10]
    )
    viewed_episode_ids = [v.episode_id for v in viewed_records]
    # MySQL에서 에피소드 정보 일괄 조회
    episodes_mysql = Episode.objects.using('mysql').filter(episode_id__in=viewed_episode_ids).select_related("webtoon__station")
    episode_map = {e.episode_id: e for e in episodes_mysql}

    recent_data = []
    for v in viewed_records:
        ep = episode_map.get(v.episode_id)
        if ep:
            recent_data.append(_make_item_from_episode(ep))

    # 2) 저장한 이야기(북마크)
    bookmark_records = (
        Bookmark.objects.using('default').filter(user=user)
        .order_by("-created_at")
    )
    bookmark_episode_ids = [b.episode_id for b in bookmark_records]
    # MySQL에서 에피소드 정보 일괄 조회
    bookmarks_mysql = Episode.objects.using('mysql').filter(episode_id__in=bookmark_episode_ids).select_related("webtoon__station")
    bookmark_map = {e.episode_id: e for e in bookmarks_mysql}

    saved_data = []
    for b in bookmark_records:
        ep = bookmark_map.get(b.episode_id)
        if ep:
            saved_data.append(_make_item_from_episode(ep))

    return Response(
        {"recent": recent_data, "saved": saved_data},
        status=status.HTTP_200_OK,
    )