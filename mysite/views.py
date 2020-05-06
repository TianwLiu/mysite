

from django.http import HttpResponse
from django.shortcuts import render
import datetime


def default(request):
    return render(request,'base.html')

def hello(request,first,second,):
    return HttpResponse("Hello world,tianwei,first is %s and second is %s "%( second,first))

def test_hello(request):
    return HttpResponse("Hello world,tianwei,this is test hello")

def get_currenttime(request,name):
    now=datetime.datetime.now()
    return render(request,"gettime.html",locals())

'''
def audioplayer(request,song_name):
    file_name=song_name+".mp3"
    file_type="audio/mp3"
    return render(request,"Audioplayer.html",locals())
'''

def audioplayer(request,song_name):
    pass
def download(request,song_name):
    pass