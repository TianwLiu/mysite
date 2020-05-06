from django.urls import path
from tool.consumers import SearchSong,UpdloadSonglist,ListManager,Player

websocket_urlpatterns=[
    path('tool/',SearchSong),
    path('uploadsonglist/',UpdloadSonglist),
    path('listmanager/',ListManager),
    path('playersocket/',Player)
]