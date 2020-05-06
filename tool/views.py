from django.shortcuts import render


# Create your views here.
def index_tool(request):
    return render(request,"index_tool.html")

def index_uploadsonglist(request):
    return render(request,'index_uploadsonglist.html')

def index_listmanager(request):
    return render(request,'index_listmanager.html')

def index_player(request):
    return render(request,'index_player.html')