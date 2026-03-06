from django.db import models
from subway.models import Station

class Webtoon(models.Model):
    webtoon_id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='station_id')
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="webtoons/thumbnails/", blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "webtoons"
        managed = True
        app_label = 'stories'

class Episode(models.Model):
    episode_id = models.BigAutoField(primary_key=True)
    # 📌 주의: episodes 테이블에는 station_id가 없고 webtoon_id만 있음
    webtoon = models.ForeignKey(Webtoon, on_delete=models.CASCADE, related_name='episodes', db_column='webtoon_id')
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=255)
    history_summary = models.TextField()
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "episodes"
        managed = True
        app_label = 'stories'

class Cut(models.Model):
    cut_id = models.BigAutoField(primary_key=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name="cuts", db_column='episode_id')
    image = models.CharField(max_length=255) 
    caption = models.TextField(blank=True, null=True)
    cut_order = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cuts"
        managed = True
        app_label = 'stories'

# 📌 명세 6번: 역과 직접 연결된 에피소드 테이블 (station_id 존재)
class StoriesEpisode(models.Model):
    id = models.BigAutoField(primary_key=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, db_column='station_id')
    title = models.CharField(max_length=200)
    episode_num = models.IntegerField()
    subtitle = models.CharField(max_length=255)
    history_summary = models.TextField()
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "stories_episode"
        managed = True
        app_label = 'stories'