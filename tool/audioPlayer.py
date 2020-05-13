
import traceback

from tool.models import Song
from ffmpy3 import FFmpeg
import time
import json
import threading
import os
from tool.youget import YouGet,time_out_Error,return_one_Error
import shutil


class AudioPlayer():
    def __init__(self, *args, **kwargs):

        self.browser_current_song = 0
        self.current_buffering_index = None
        self.entered_download_ffmpeg=[]
        self.waiting_for_buffer = []
        self.lock_waiting_for_buffer = threading.Lock()
        self.downdload_video_thread=threading.Thread(target=self.downdload_video_thread_function)


        self.waiting_for_convert = []
        self.loc_waiting_for_convert=threading.Lock()
        self.convert_to_mp3_thread=threading.Thread(target=self.convert_to_mp3_thread_function)

        self.current_songlist = []
        self.current_songlist_flag_buffered = None


        self.buffer_file_waiting_for_del = []
        self.lock_buffer_file_waiting_for_del = threading.Lock()
        self.debud_his=[]

        if os.path.exists("./media/"):
            shutil.rmtree("./media/")
        os.mkdir("./media/")

        self.startSonThread()

    def startSonThread(self):
        self.downdload_video_thread.start()
        self.convert_to_mp3_thread.start()
    def stopSonThread(self):
        pass

    def check_currentsong(self,index):
        flag=self.current_songlist_flag_buffered[index]
        self.lock_waiting_for_buffer.acquire()
        if flag==1: # finish_buffer
            back_message = {"type": "message", "message": "finish_buffer", "finish_buffer": index}
        elif flag==-1:# error
            back_message = {"type": "message", "message": "error", "error": index}
        elif index in self.entered_download_ffmpeg:
            #back_message = {"type": "message", "message": "歌曲" + str(index) + "当前正在缓冲"}
            back_message = {"type": "message", "message": "buffering","buffering": index}
        elif index in self.waiting_for_buffer:#in buffer queue
            self.buffer_single_song(index)
            #back_message = {"type": "message", "message": "歌曲" + str(index) + "已在正在缓冲队列,现调整为最优先"}
            back_message = {"type": "message", "message": "buffering", "buffering": index}
        else:
            self.buffer_single_song(index)
            #back_message = {"type": "message", "message": "歌曲" + str(index) + "完成进入缓冲队列,目前最优先"}
            back_message = {"type": "message", "message": "buffering", "buffering": index}
        self.lock_waiting_for_buffer.release()
        return back_message

    def buffer_single_song(self,index):


        self.waiting_for_buffer = []
        self.waiting_for_buffer.append(index)


    def update_browser_currentsong(self,index):
        self.browser_current_song = index
        self.lock_waiting_for_buffer.acquire()
        self.buffer_stack_update(index+1)
        self.lock_waiting_for_buffer.release()
        return {"type": "message", "message": "server received update"}



    def buffer_stack_update(self,index):
        max_buffer_index = index
        while max_buffer_index < index + 2 and max_buffer_index < len(self.current_songlist) - 1:
            max_buffer_index += 1


        self.waiting_for_buffer = []

        while max_buffer_index >= index:
            # pathsss = self.get_mp3_path(max_buffer_index)
            if self.current_songlist_flag_buffered[max_buffer_index] == 0 and max_buffer_index not in self.entered_download_ffmpeg:  # 0 means the song(mp3 file) has been at server
                self.waiting_for_buffer.append(max_buffer_index)
            max_buffer_index -= 1


    def buffer_manager_thread_function(self):
        pass

    def you_get_thread_function(self,index):
        if Song.objects.get(id_list=index).url1:
            arg = Song.objects.get(id_list=index).url1
        else:
            song_title_singer = self.current_songlist[index]["title"] + "-" + \
                                self.current_songlist[index]["singer"]
            arg = song_title_singer

        you_get = YouGet(arg)
        try:
            flag = you_get.try_to_get()

        except return_one_Error as e:
            self.current_songlist_flag_buffered[index] = -1
            print(e)
            print("download exception:", arg)

        except Exception as e:
            self.current_songlist_flag_buffered[index] = -1
            print(e)
            print("download exception:", arg)
        else:
            if flag:
                self.loc_waiting_for_convert.acquire()
                self.waiting_for_convert.append({"video_path": "./media/" + you_get.file_name, "index": index})
                self.loc_waiting_for_convert.release()
                print("download success,waiting for convert:",arg,"-->",you_get.file_name)

            else:
                self.current_songlist_flag_buffered[index] = -1
                print("download failed,no file name:",arg)


        '''
        if you_get.try_to_get():
            if you_get.file_name:
                self.loc_waiting_for_convert.acquire()
                self.waiting_for_convert.append({"video_path":"./media/"+you_get.file_name,"index":index})
                self.loc_waiting_for_convert.release()
                print(you_get.file_name,"download finish,waiting for convert")
            else:
                self.current_songlist_flag_buffered[index] = -1
                print(you_get.file_name, "download error,no name")
        else:
            self.current_songlist_flag_buffered[index] = -1
            print(you_get.file_name, "download error,exception")
        '''
    def downdload_video_thread_function(self):
        while 1:
            self.lock_waiting_for_buffer.acquire()
            if self.waiting_for_buffer:

                index = self.waiting_for_buffer.pop()
                if index not in self.entered_download_ffmpeg:
                    self.entered_download_ffmpeg.append(index)
                else:
                    self.lock_waiting_for_buffer.release()
                    time.sleep(3)
                    continue
                self.lock_waiting_for_buffer.release()
            else:
                self.lock_waiting_for_buffer.release()
                time.sleep(3)
                continue

            thread_son=threading.Thread(target=self.you_get_thread_function,args=(index,))
            thread_son.start()


            '''
            if Song.objects.get(id_list=index).url1:
                 arg= Song.objects.get(id_list=index).url1
            else:
                song_title_singer = self.current_songlist[index]["title"] + "-" + \
                                   self.current_songlist[index]["singer"]
                arg=song_title_singer



            try:
                print("*****************************************")
                print("download_url:"+download_url+"index"+str(index))
                any_download(download_url, **kwargs)
                if VideoExtractor.latest_title:
                    video_path = "./media/" + get_filename(
                        VideoExtractor.latest_title) + "." + VideoExtractor.latest_ext

                    if os.path.exists(video_path):
                        self.loc_waiting_for_convert.acquire()
                        self.waiting_for_convert.append({"video_path":video_path,"index":index})
                        print("get from you-get:" + video_path + "index" + str(index))
                        self.debud_his.append({"video_path":video_path,"index":index})
                        self.loc_waiting_for_convert.release()
                    else:
                        print("********************************************************")
                        print(download_url + "download成功运行，但本地访问失败,index:" + str(index))
                        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        self.current_songlist_flag_buffered[index] = -1
            except Exception as e:
                print("********************************************************")
                print(download_url+"download失败,index:"+str(index))
                traceback.print_exc()
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                self.current_songlist_flag_buffered[index] = -1
            finally:
                VideoExtractor.latest_title = None
                VideoExtractor.latest_ext = None
            '''


    def ffmpeg_thread_function(self,task_unit):
        index = task_unit["index"]
        mp3_path = self.get_mp3_path(index)
        video_path = task_unit["video_path"]
        assert os.path.exists(video_path)
        ff = FFmpeg(inputs={video_path: None},
                    outputs={mp3_path: "-vn -ar 44100 -ac 2 -ab 192 -f mp3 -y -v 8"})
        ff.cmd
        print("convert try:",mp3_path)
        try:
            ff.run()
        except Exception:
            self.current_songlist_flag_buffered[index] = -1
            print("convert exception",mp3_path)
        else:
            if os.path.exists(mp3_path):
                self.current_songlist_flag_buffered[index] = 1
                print("convert finish",mp3_path )
            else:
                self.current_songlist_flag_buffered[index] = -1
                print("convert fail,no get planned mp3 file in specific path",mp3_path)


    def convert_to_mp3_thread_function(self):
        while 1:
            self.loc_waiting_for_convert.acquire()
            if self.waiting_for_convert:
                task_unit=self.waiting_for_convert.pop(0)
                self.loc_waiting_for_convert.release()
            else:
                self.loc_waiting_for_convert.release()
                time.sleep(1)
                continue

            thread_son = threading.Thread(target=self.ffmpeg_thread_function, args=(task_unit,))
            thread_son.start()

            '''
            index=task_unit["index"]
            mp3_path=self.get_mp3_path(index)
            video_path=task_unit["video_path"]
            ff = FFmpeg(inputs={video_path: None},
                        outputs={mp3_path: "-vn -ar 44100 -ac 2 -ab 192 -f mp3 -y -v 8"})
            ff.cmd
            try:
                ff.run()
            except Exception as e:
                pass
            finally:
                if os.path.exists(mp3_path):
                    self.current_songlist_flag_buffered[index]=1
                else:
                    self.current_songlist_flag_buffered[index]=-1
                #if os.path.exists(video_path):
                 #   os.remove(video_path)

            '''



    def getsongslist(self):
        # song_json = serializers.serialize('json', Song.objects.all(), fields=('id_list', 'song_title', 'singer'))
        self.updatesonglist()
        message = {'type': 'song_list', 'song_list': self.current_songlist}
        return message

    def updatesonglist(self):
        self.current_songlist = None
        self.current_songlist = []
        for song in Song.objects.all():
            single_song_info = {'id': song.id_list, 'title': song.song_title, 'singer': song.singer}
            self.current_songlist.append(single_song_info)
        self.current_songlist_flag_buffered = [0] * len(self.current_songlist)



    def exit_rm_sources(self):
        if os.path.exists("./media/"):
            shutil.rmtree("./media/")
        os.mkdir("./media/")




    def get_mp3_path(self, index_currentsonglist):
        song_title_singer = self.current_songlist[index_currentsonglist]["title"] + "-" + \
                            self.current_songlist[index_currentsonglist]["singer"]
        mp3_path = "./media/" + song_title_singer + ".mp3"
        return mp3_path

    '''
    def buffer_song_via_index(self, index_currentsonglist):
        if index_currentsonglist == self.current_buffering_index:
            back_message = {"type": "message", "message": "歌曲" + str(index_currentsonglist) + "当前正在缓冲"}
        elif self.current_songlist_flag_buffered[index_currentsonglist] == -1:  # error
            back_message = {"type": "message", "message": "error", "error": index_currentsonglist}

        elif self.current_songlist_flag_buffered[index_currentsonglist] == 1:  # finish_buffer
            back_message = {"type": "message", "message": "finish_buffer", "finish_buffer": index_currentsonglist}
        else:
            back_message = {"type": "message", "message": "歌曲" + str(index_currentsonglist) + "进入缓冲队列"}

        # buffer three songs at same time,note this is stack,reverse operation
        max_buffer_index = index_currentsonglist
        while max_buffer_index < index_currentsonglist + 2 and max_buffer_index < len(self.current_songlist) - 1:
            max_buffer_index += 1

        self.lock_waiting_for_buffer.acquire()
        self.waiting_for_buffer = []

        while max_buffer_index >= index_currentsonglist:
            # pathsss = self.get_mp3_path(max_buffer_index)
            if self.current_songlist_flag_buffered[max_buffer_index] == 0 and max_buffer_index != self.current_buffering_index:  # 0 means the song(mp3 file) has been at server
                self.waiting_for_buffer.append(max_buffer_index)
            max_buffer_index -= 1
        self.lock_waiting_for_buffer.release()

        if self.download_thread is None or not self.download_thread.is_alive():
            self.download_thread = threading.Thread(target=self.buffer_thread_function)
            self.download_thread.start()

        return back_message
'''

'''
    def buffer_thread_function(self):
        while not len(self.waiting_for_buffer) == 0:
            self.lock_waiting_for_buffer.acquire()
            index_currentsonglist = self.waiting_for_buffer.pop()
            self.lock_waiting_for_buffer.release()
            self.current_buffering_index = index_currentsonglist

            kwargs = {'output_dir': './static/media/', 'merge': True, 'info_only': False, 'json_output': False,
                      'caption': True,
                      'password': None}

            song_title_singer = self.current_songlist[index_currentsonglist]["title"] + "-" + \
                                self.current_songlist[index_currentsonglist]["singer"]

            if Song.objects.get(id_list=index_currentsonglist).url1:
                download_url = Song.objects.get(id_list=index_currentsonglist).url1
            else:
                download_url = "http://" + song_title_singer
            mp3_path = "./static/media/" + song_title_singer + ".mp3"
            video_path = ""
            loop_times = 0

            try:

                any_download(download_url, **kwargs)

                video_path = "./static/media/" + get_filename(VideoExtractor.latest_title) + "." + VideoExtractor.latest_ext

                ff = FFmpeg(inputs={video_path: None},
                            outputs={mp3_path: "-vn -ar 44100 -ac 2 -ab 192 -f mp3"})
                ff.cmd
                ff.run()
                self.current_songlist_flag_buffered[index_currentsonglist] = 1
                back_message = {"type": "message", "message": "finish_buffer", "finish_buffer": index_currentsonglist}
                back_message_json = json.dumps(back_message)
                self.send(back_message_json)
                # if os.path.exists(video_path):
                # os.remove(video_path)
                # self.lock_buffer_file_waiting_for_del.acquire()
                # self.buffer_file_waiting_for_del.append({"type":"mp3","path":mp3_path,"time":time.time()})
                # self.buffer_file_waiting_for_del.append({"type":"video","path":video_path})
                # self.lock_buffer_file_waiting_for_del.release()
            except BaseException or Exception as e:
                if os.path.exists(mp3_path):
                    self.current_songlist_flag_buffered[index_currentsonglist] = 1
                    back_message = {"type": "message", "message": "finish_buffer",
                                    "finish_buffer": index_currentsonglist}
                    back_message_json = json.dumps(back_message)
                    self.send(back_message_json)

                    # self.lock_buffer_file_waiting_for_del.acquire()
                    # self.buffer_file_waiting_for_del.append({"type": "mp3", "path": mp3_path, "time": time.time()})
                    # self.buffer_file_waiting_for_del.append({"type": "video", "path": video_path})
                    # self.lock_buffer_file_waiting_for_del.release()
                else:
                    self.current_songlist_flag_buffered[index_currentsonglist] = -1
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    print("$$$$$$" + song_title_singer + ",此歌曲失败$$$$$$$$$$$$$$$$$$$$$$")
                    traceback.print_exc()
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

                    back_message = {"type": "message", "message": "error", "error": index_currentsonglist}
                    back_message_json = json.dumps(back_message)
                    self.send(back_message_json)
            finally:
                if os.path.exists(video_path):
                    os.remove(video_path)
            self.current_buffering_index = None
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
