from django.db import models

# Create your models here.

class Song(models.Model):
    id_list=models.IntegerField(db_index=True)
    song_title=models.CharField(max_length=50)
    singer=models.CharField(max_length=50)
    data_add_song=models.DateField(auto_now_add=True)
    note_song=models.CharField(max_length=50)
    url1=models.URLField(null=True)
    url2=models.URLField(null=True)
    url3=models.URLField(null=True)

class SongList(models.Model):
    song_list_name=models.CharField(max_length=100)
    data_add_list=models.DateField(auto_now_add=True)
    note_list=models.CharField(max_length=50)
    songs=models.ManyToManyField(Song)

class SongLibrary(models.Model):
    user_name=models.CharField(max_length=50)
    song_lists=models.ManyToManyField(SongList,null=True)

