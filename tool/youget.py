import os
import subprocess
import re

class return_one_Error(Exception):
    pass
class time_out_Error(Exception):
    pass

class YouGet:
    def __init__(self, name_url):
        self.name_url =  name_url
        self.control_args = "--no-caption"
        self.file_name = None

    def try_to_get(self):
        time_out_times=0
        return_one_times=0
        file_no_name_times=0
        while 1:

            try:
                sh = subprocess.run(args=["you-get","-o" ,"./media", "--no-caption",self.name_url], stdout=subprocess.PIPE,stderr=subprocess.PIPE, timeout=200)
            except subprocess.TimeoutExpired:
                time_out_times+=1
                if time_out_times<2:
                    continue
                raise time_out_Error("this song time out")
            else:
                # grep=subprocess.run(args=["grep","Downloading"],stdin=sh.stdout)
                # print(sh)
                # print(sh.stdout)
                # print(sh.returncode)
                if sh.returncode == 0:
                    res = re.findall(r"^Downloading.*$", str(sh.stdout, encoding='utf8'), flags=re.MULTILINE)
                    res1=re.findall(r"^.*file already exists$", str(sh.stderr, encoding='utf8'), flags=re.MULTILINE)
                    # print(res)
                    # print(grep)
                    # print("grep----->",grep.stdout)

                    if res:
                        # print(res[0].split("Downloading "))
                        file_name = res[0].split("Downloading ")[1].replace(" ...", "")

                        #print("file_name:" + file_name)
                        self.file_name = file_name
                        return True

                    elif res1:
                        file_name = res1[0].split("./media/")[1].replace(": file already exists", "")

                        print("file_name:" + file_name)
                        self.file_name = file_name
                        return True

                    else:
                        file_no_name_times+=0
                        if file_no_name_times<5:
                            continue
                        return False
                else:
                    return_one_times += 1

                    if return_one_times<5:
                        continue
                    raise return_one_Error("you-get return 1")


if __name__ == "__main__":
    you_get = YouGet("Running In The “90S” - Max Cover")
    try:
        you_get.try_to_get()
    except Exception as w:
        print(w)
