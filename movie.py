import glob
import os
import random
import argparse
from PIL import Image
from logg import logg
from downlaod import youtube
from moviepy.editor import *
from moviepy.editor import AudioFileClip, VideoFileClip
from moviepy.editor import ImageSequenceClip

class clip:

    def __init__(self, Vname, start_time=0, end_time=10):

        # Enable logging
        self.logging = logg()

        # setting output directory
        self.SAMPLE_OUTPUTS='Q:\PlayGround\clipPy'

        # Pics dirctory
        self.thumbnail_dir = os.path.join(self.SAMPLE_OUTPUTS, "photos")
        
        # Final video 2 mp4 path
        self.output_video = os.path.join(self.SAMPLE_OUTPUTS, 'videos', "preparing")

        # Setting start and end duration of the video
        input_start = start_time.split(":")
        self.start_dur = int(input_start[0])*60 + int(input_start[1])

        input_end = end_time.split(":")
        self.end_dur = int(input_end[0])*60 + int(input_end[1])

        # Songs liberary
        self.song_lib = "Q:\PlayGround\clipPy\songs"

        # dowloading video from youtube
        you = youtube()
        you.download(Vname)

    def get_downloaded_song(self):
        list_of_files = glob.glob(self.song_lib + "\*")
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def mp4(self):
        this_dir = os.listdir(self.thumbnail_dir)
        self.logging.log.info("Finding the pictures from {}".format(this_dir))

        # finding all the pics with jpg extension
        filepaths = [os.path.join(self.thumbnail_dir, fname) for fname in this_dir if fname.endswith("jpg")]

        directory = {}
        for root, dirs, files in os.walk(self.thumbnail_dir):
            for fname in files:
                filepath = os.path.join(root, fname)
                try:
                    key = fname.replace(".jpg", "")
                except:
                    key = None
                if key != None:
                    directory[key] = filepath

        new_path = []
        for k in sorted(directory.keys()):
            filepath = directory[k]
            new_path.append(filepath)

        # Setting Image time duration
        self.logging.log.info("Setting start and end audio duration")
        pic_duration = (int(self.end_dur) - int(self.start_dur)) / len(new_path)
        clips = [ImageClip(m).set_duration(pic_duration).crossfadein(0.5) for m in new_path]

        # Concatinate all the videos
        concat_clip = concatenate_videoclips(clips, method="compose")

        # Find downloaded song from youtuebe & if not found pick any random from liberary
        self.logging.log.info("Fetching song ....")
        song = self.get_downloaded_song()

        self.logging.log.info("Setting background music")
        background_audio_clip = AudioFileClip(song)
        bg_music = background_audio_clip.subclip(self.start_dur, self.end_dur)
        
        self.logging.log.info("Preparing final video")
        final_clip = concat_clip.set_audio(bg_music)
        final_clip.write_videofile(os.path.join(self.output_video,"final.mp4"), codec='libx264', audio_codec="aac", fps=24)

        return self.output_video + "\\final.mp4"

if __name__ == '__main__':
    '''
        This is just for testing purpose.
    '''
    
    url="https://www.youtube.com/watch?v=-j0dlcfekqw&list=PLkP2P3Ib84SO5A6ivwueX6sg47-CumGIZ&index=41"
    a = clip(url, "00:08", "00:20")
    a.mp4()

    parser = argparse.ArgumentParser(description='Proggram to convert pic Videos')
    parser.add_argument("-url", help="Enter the youtube URL", required=True)
    parser.add_argument("-start", help="Enter the youtube URL", required=True)
    parser.add_argument("-end", help="Enter the youtube URL", required=True)

    args = parser.parse_args()

    input_start = args.start.split(":")
    start_dur = int(input_start[0])*60 + int(input_start[1])

    input_end = args.end.split(":")
    end_dur = int(input_end[0])*60 + int(input_end[1])

    Convert = Clip(args.url, start_dur, end_dur)
    Convert.mp4()