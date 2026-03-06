from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.conf import settings
# from stories.models import Episode

# User = settings.AUTH_USER_MODEL

# --- 사용자가 본 에피소드 기록 ---
# --- Proxy Models to break app dependencies ---
# activity-service는 다른 서비스의 앱(accounts, stories, subway)을 직접 포함하지 않습니다.
# 하지만 DB 테이블 간의 관계(Foreign Key)는 존재하므로,
# Django ORM이 정상적으로 동작하게 하려면 해당 테이블들을 가리키는 "프록시(대리) 모델"이 필요합니다.
# 아래 모델들은 managed = False 로 설정되어 DB 마이그레이션을 생성하거나 테이블 구조를 변경하지 않습니다.

class User(AbstractUser):
    # user-service의 accounts.User 모델을 대체하는 프록시 모델입니다.
    # AUTH_USER_MODEL로 지정하기 위해 AbstractUser를 상속합니다.
    email = models.EmailField(unique=True, blank=True, null=True) # 실제 테이블에 있는 필드

    class Meta:
        db_table = 'accounts_user'
        managed = False

class Line(models.Model):
    # subway 앱의 Line 모델 프록시
    id = models.BigAutoField(primary_key=True)
    line_name = models.CharField(max_length=100)

    class Meta:
        db_table = "subway_line"
        managed = False

class Station(models.Model):
    # subway 앱의 Station 모델 프록시
    id = models.BigAutoField(primary_key=True)
    station_name = models.CharField(max_length=100)

    class Meta:
        db_table = "subway_station"
        managed = False

class Webtoon(models.Model):
    # stories 앱의 Webtoon 모델 프록시
    webtoon_id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.DO_NOTHING, db_column='station_id')
    title = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "webtoons"
        managed = False

class Episode(models.Model):
    # stories 앱의 Episode 모델 프록시
    episode_id = models.BigAutoField(primary_key=True)
    webtoon = models.ForeignKey(Webtoon, on_delete=models.DO_NOTHING, related_name='episodes', db_column='webtoon_id')
    subtitle = models.CharField(max_length=255)

    class Meta:
        db_table = "episodes"
        managed = False

class Cut(models.Model):
    # stories 앱의 Cut 모델 프록시
    cut_id = models.BigAutoField(primary_key=True)
    episode = models.ForeignKey(Episode, on_delete=models.DO_NOTHING, related_name="cuts", db_column='episode_id')
    image = models.CharField(max_length=255)
    cut_order = models.SmallIntegerField()

    class Meta:
        db_table = "cuts"
        managed = False

class UserViewedEpisode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_episodes')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "library_userviewedepisode"
        unique_together = ('user', 'episode')
        managed = False

    def __str__(self):
        # return f"{self.user} - {self.episode.title}"
        try:
            # Episode 모델에는 title이 없고 subtitle이 있습니다.
            return f"{self.user} - {self.episode.subtitle}"
        except (AttributeError, Episode.DoesNotExist):
            return f"{self.user} - (삭제된 에피소드)"


# --- 북마크 모델 ---
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "library_bookmark"
        unique_together = ('user', 'episode')
        managed = False

    def __str__(self):
        # return f"{self.user} - 북마크: {self.episode.title}"
        try:
            # Episode 모델에는 title이 없고 subtitle이 있습니다.
            return f"{self.user} - 북마크: {self.episode.subtitle}"
        except (AttributeError, Episode.DoesNotExist):
            return f"{self.user} - 북마크: (삭제된 에피소드)"
