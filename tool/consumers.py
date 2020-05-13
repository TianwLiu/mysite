import ctypes
import inspect
import traceback

from channels.generic.websocket import WebsocketConsumer

from tool.models import SongList,Song
from django.core import serializers
from tool.audioPlayer import AudioPlayer

import time
import json


class SearchSong(WebsocketConsumer):

    def connect(self):
        self.accept()


    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        self.send(str(text_data))
        self.send(type(text_data))
        msg1="please wait for the result of "+text_data
        self.send(msg1)
        time_start=time.time()

        kwargs = {'output_dir': '.', 'merge': True, 'info_only': False, 'json_output': False, 'caption': True,'password': None}
        #set_sender(self)
        any_download("http://" + text_data,  **kwargs)
        time_use= time.time() - time_start
        self.send("以下一首歌曲处理用时："+str(time_use))
        log="last ************ is ---->:"+ VideoExtractor.latest_title+"\next:"+VideoExtractor.latest_ext+"\nurl:"+VideoExtractor.latest_url
        self.send(log)


class ListManager(WebsocketConsumer):

    def connect(self):
        self.accept()
        song_json = serializers.serialize('json', Song.objects.all(), fields=('id_list', 'song_title', 'singer'))
        self.send(song_json)

    def disconnect(self, code):
        pass

    def receive(self, text_data):
        message=json.loads(text_data)
        self.parse_message_exc(message)

    def parse_message_exc(self,message):
        if message["order"]=="seturl":
            url=message["url"]
            song_id=message["id"]
            Song.objects.filter(id_list=song_id).update(url1=url)


class UpdloadSonglist(WebsocketConsumer):

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self,text_data):
        lines=str(text_data).splitlines()
        for line in lines:
            song_name_singer_name=line.split('-',-1)
            song_name=song_name_singer_name[0].rstrip()
            singer_name=song_name_singer_name[1].lstrip()
            current_song=Song(id_list=len(Song.objects.all()),
                              song_title=song_name,
                              singer=singer_name
                              )
            current_song.save()
        for song in Song.objects.all():
            self.send(str(song.id_list)+"歌曲名字："+song.song_title+"\n")

class Player(WebsocketConsumer):


    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waiting_for_buffer=[]
        self.lock_waiting_for_buffer = threading.Lock()
        self.current_buffering_index = None
        self.current_songlist = []
        self.current_songlist_flag_buffered = None
        self.download_thread = None
        self.buffer_file_waiting_for_del=[]
        self.lock_buffer_file_waiting_for_del = threading.Lock()
        if os.path.exists("./static/media/"):
            shutil.rmtree("./static/media/")
        os.mkdir("./static/media/")
    '''


    '''
    def del_buffer_thread_function(self):

        while 1:

            time.sleep(30)
            new_buffer_file_waiting_for_del = []
            indexs_preserve_files = []
            time_thistime=time.time()
            index_preserve_file=0

            for buffer_file in self.buffer_file_waiting_for_del:
                if buffer_file["type"]=="video":
                    if os.path.exists(buffer_file["path"]):
                        os.remove(buffer_file["path"])

                elif buffer_file["type"]=="mp3":
                    if time_thistime-buffer_file["time"]>30:
                        if os.path.exists(buffer_file["path"]):
                            os.remove(buffer_file["path"])
                    elif time_thistime-buffer_file["time"]<30:
                        indexs_preserve_files.append(index_preserve_file)
                index_preserve_file+=1

            for i in indexs_preserve_files:
                new_buffer_file_waiting_for_del.append(self.buffer_file_waiting_for_del[i])
            self.lock_buffer_file_waiting_for_del.acquire()
            if index_preserve_file<len(self.buffer_file_waiting_for_del):
                new_buffer_file_waiting_for_del.extend(self.buffer_file_waiting_for_del[index_preserve_file:])
                self.buffer_file_waiting_for_del=new_buffer_file_waiting_for_del
            self.lock_buffer_file_waiting_for_del.release()
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audioPlayer = AudioPlayer()

    def connect(self):
        self.accept()
        #self.updatesonglist()
        self.sendMessage(self.audioPlayer.getsongslist())

    def receive(self, text_data):
        message=json.loads(text_data)
        self.parse_message_exc(message)

    def parse_message_exc(self,message):
        if message["order"]=="buffer":
            #self.sendMessage(self.audioPlayer.buffer_song_via_index(int(message["data"])))
            pass
        elif message["order"]=="song_list":
            self.sendMessage(self.audioPlayer.getsongslist())
        elif message["order"] == "report_currentsong":
            self.sendMessage(self.audioPlayer.update_browser_currentsong(int(message["report_currentsong"])))
        elif message["order"]=="check_currentsong":
            self.sendMessage(self.audioPlayer.check_currentsong(int(message["check_currentsong"])))
    def sendMessage(self,message):
        message_json = json.dumps(message)
        self.send(message_json)



    def disconnect(self, code):

        self.audioPlayer.exit_rm_sources()
    '''
    def updatesonglist(self):
        self.current_songlist=None
        self.current_songlist=[]
        for song in Song.objects.all():
            single_song_info={'id':song.id_list,'title':song.song_title,'singer':song.singer}
            self.current_songlist.append(single_song_info)
        self.current_songlist_flag_buffered=[0]*len(self.current_songlist)
    '''


        #self.exit_rm_sources()

    '''
    def exit_rm_sources(self):
        if os.path.exists("./static/media/"):
            shutil.rmtree("./static/media/")
        os.mkdir("./static/media/")
    '''



    '''
    def get_mp3_path(self,index_currentsonglist):
        song_title_singer = self.current_songlist[index_currentsonglist]["title"] + "-" + \
                            self.current_songlist[index_currentsonglist]["singer"]
        mp3_path = "./static/media/" + song_title_singer + ".mp3"
        return mp3_path
    '''
    '''
    def buffer_song_via_index(self,index_currentsonglist):

        if index_currentsonglist==self.current_buffering_index:
            back_message = {"type": "message", "message": "歌曲"+str(index_currentsonglist)+"当前正在缓冲"}
            back_message_json = json.dumps(back_message)
            self.send(back_message_json)

        if self.current_songlist_flag_buffered[index_currentsonglist]==-1:#error
            back_message = {"type": "message", "message": "error","error":index_currentsonglist}
            back_message_json = json.dumps(back_message)
            self.send(back_message_json)



        if  self.current_songlist_flag_buffered[index_currentsonglist]==1:#finish_buffer
                back_message = {"type": "message", "message": "finish_buffer", "finish_buffer": index_currentsonglist}
                back_message_json = json.dumps(back_message)
                self.send(back_message_json)

        #buffer three songs at same time,note this is stack,reverse operation
        max_buffer_index=index_currentsonglist
        while max_buffer_index<index_currentsonglist+2 and max_buffer_index<len(self.current_songlist)-1:
            max_buffer_index+=1

        self.lock_waiting_for_buffer.acquire()
        self.waiting_for_buffer=[]

        while max_buffer_index>=index_currentsonglist:
            #pathsss = self.get_mp3_path(max_buffer_index)
            if self.current_songlist_flag_buffered[index_currentsonglist]==0  and max_buffer_index !=self.current_buffering_index:#0 means the song(mp3 file) has been at server
                self.waiting_for_buffer.append(max_buffer_index)
            max_buffer_index-=1
        self.lock_waiting_for_buffer.release()

        if self.download_thread is None or not self.download_thread.is_alive():
            self.download_thread = threading.Thread(target=self.buffer_thread_function)
            self.download_thread.start()

        back_message = {"type": "message", "message": "歌曲"+str(index_currentsonglist)+"进入缓冲队列"}
        back_message_json = json.dumps(back_message)
        self.send(back_message_json)
        return
    '''

    '''
    def buffer_thread_function(self):

        while not len(self.waiting_for_buffer)==0:
            self.lock_waiting_for_buffer.acquire()
            index_currentsonglist=self.waiting_for_buffer.pop()
            self.lock_waiting_for_buffer.release()
            self.current_buffering_index=index_currentsonglist

            kwargs = {'output_dir': './static/media/', 'merge': True, 'info_only': False, 'json_output': False, 'caption': True,
                      'password': None}

            song_title_singer = self.current_songlist[index_currentsonglist]["title"] + "-" + \
                                self.current_songlist[index_currentsonglist]["singer"]

            if Song.objects.get(id_list=index_currentsonglist).url1:
                download_url=Song.objects.get(id_list=index_currentsonglist).url1
            else:
                download_url="http://"+song_title_singer
            mp3_path="./static/media/" + song_title_singer + ".mp3"
            video_path=""
            loop_times=0

            try:

                any_download(download_url,  **kwargs)

                video_path="./static/media/" + get_filename(VideoExtractor.latest_title) + "." + VideoExtractor.latest_ext

                ff = FFmpeg(inputs={video_path: None},
                            outputs={mp3_path: "-vn -ar 44100 -ac 2 -ab 192 -f mp3"})
                ff.cmd
                ff.run()
                self.current_songlist_flag_buffered[index_currentsonglist] = 1
                back_message = {"type": "message", "message": "finish_buffer", "finish_buffer": index_currentsonglist}
                back_message_json = json.dumps(back_message)
                self.send(back_message_json)
                #if os.path.exists(video_path):
                    #os.remove(video_path)
                #self.lock_buffer_file_waiting_for_del.acquire()
                #self.buffer_file_waiting_for_del.append({"type":"mp3","path":mp3_path,"time":time.time()})
                #self.buffer_file_waiting_for_del.append({"type":"video","path":video_path})
                #self.lock_buffer_file_waiting_for_del.release()
            except BaseException or Exception as e:
                if os.path.exists(mp3_path):
                    self.current_songlist_flag_buffered[index_currentsonglist] = 1
                    back_message = {"type": "message", "message": "finish_buffer",
                                    "finish_buffer": index_currentsonglist}
                    back_message_json = json.dumps(back_message)
                    self.send(back_message_json)

                    #self.lock_buffer_file_waiting_for_del.acquire()
                    #self.buffer_file_waiting_for_del.append({"type": "mp3", "path": mp3_path, "time": time.time()})
                    #self.buffer_file_waiting_for_del.append({"type": "video", "path": video_path})
                    #self.lock_buffer_file_waiting_for_del.release()
                else:
                    self.current_songlist_flag_buffered[index_currentsonglist] = -1
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    print("$$$$$$"+song_title_singer+",此歌曲失败$$$$$$$$$$$$$$$$$$$$$$")
                    traceback.print_exc()
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                    back_message = {"type": "message", "message": "error", "error": index_currentsonglist}
                    back_message_json = json.dumps(back_message)
                    self.send(back_message_json)
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
            self.current_buffering_index=None

    '''
    '''
    def sendsongslist(self):

        #song_json = serializers.serialize('json', Song.objects.all(), fields=('id_list', 'song_title', 'singer'))

        message={'type':'song_list','song_list':self.current_songlist}
        message_json=json.dumps(message)
        self.send(message_json)
    '''

