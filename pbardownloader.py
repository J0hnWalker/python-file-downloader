# coding:utf-8
import sys
import os
import time
import urlparse
import requests
import helper
from contextlib import closing


class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        _info = self.info % (
        self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
        self.unit)
        return _info


    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        sys.stdout.write(self.__get_info() + '\r')


class DownLoader(object):
    def __init__(self, url, out=None):
        super(DownLoader, self).__init__()
        self.url = url
        self.output = out

    def detect_filename(self):
        url = self.url #http://xxx.com/abcd.exe
        fname = os.path.basename(urlparse.urlparse(url).path)
        if len(fname.strip()) == 0:
            return None
        return fname

    def detect_directory(self):
        if not self.output:
            self.output = ""
        else:
            pass
            #netloc = os.path.basename(urlparse.urlparse(self.url).netloc)  
        return self.output

    def is_continuable(self):
        '''
        判断是否支持断点续传
        :return:
        '''
        headers = {
            'Range': 'bytes=0-1'
        }
        try:
            r = requests.get(self.url, headers=headers, timeout=5)
            header = dict(r.headers)
            return (True, int(header['Content-Range'].split('/')[1])) if header.has_key('Content-Range') else (False, int(header['Content-Length']))
        except Exception,e:
            pass
        return (False, 0)

    def download(self, headers={}):
        filename = self.detect_filename()
        s = self.detect_directory()
        directory = s + "\\" if s.strip() else s
        #print directory
        isTrue, Length = self.is_continuable()
        if os.path.exists(directory + filename):
            current_size = int(os.path.getsize(directory + filename))
        else:
            current_size = 0
        if isTrue:
            headers['Range'] = 'bytes=%d-' % current_size
        else:
            pass
        try:
            with closing(requests.get(self.url, stream=True, headers=headers, timeout=5)) as response:
                #print response.headers['Content-Range']
                chunk_size = 1024
                #content_size = int(response.headers['content-length'])
                content_size = Length
                print content_size
                progress = ProgressBar(filename, count=current_size, total=content_size, unit="KB", chunk_size=chunk_size, run_status="downloding", fin_status="downloaded")
                with open(directory + filename, "ab+") as file:
                    file.seek(current_size)
                    file.truncate()
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        file.flush()
                        progress.refresh(count=len(data))

                print "Saved in " + directory + filename
        except KeyboardInterrupt:
            #print "Failed to connect [" + filename + "]"
            sys.stdout.write("\n" + "^C download paused by user")
        except requests.exceptions.ReadTimeout, e:
            print e.message
            pass

if __name__ == '__main__':
        t = DownLoader("http://localhost:81/1.png",out="C:\\Users\\test")
        t.download()

