import youtube_dl
from logg import logg

class youtube:

    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': 'Q:\PlayGround\clipPy\songs\%(title)s.mp3',
            'prefer_ffmpeg': True,
            "noplaylist": True,
            "forcetitle": True
        }
        
        self.logging = logg()

    def download(self, VideoUrl):
        try:
            print(VideoUrl)
            self.logging.log.info("Downloading youtube video")
            with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([VideoUrl])
            self.logging.log.info("Youtube video downloaded successfully")
        except Exception as e:
            self.logging.log.error("ERROR: {}".format(e))
            self.logging.log.error("Not able to download the video")

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=fKopy74weus&list=PLkP2P3Ib84SO5A6ivwueX6sg47-CumGIZ&index=18"
    a = youtube()
    a.download(url)