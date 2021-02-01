# Multi-video sync tool
import os
import pathlib
import youtube_dl
from pySmartDL import SmartDL
import ffmpy
import validators
import sys


class VideoSyncTool: 
    def __init__(self):
        self.ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s.%(ext)s'})
        self.match_length = 1000
        
    def get_url(self, youtube_url, format_id):
        with self.ydl:
            result = self.ydl.extract_info(
                youtube_url,
                download=False # We just want to extract the info
            )

        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result

        video_url = [ f['url'] for f in video['formats'] if f['format_id'] == format_id ][0]
        return video_url
    
    def download_file(self, download_url, filename):
        dest_path = os.path.join(pathlib.Path().absolute(), filename)
        obj = SmartDL(download_url, dest_path)
        obj.start()
        path = obj.get_dest()
        return path
    
    def extract_audio(self, filename, match_length):
        pre, ext = os.path.splitext(filename)
        ff = ffmpy.FFmpeg(
                inputs={filename: f'-hide_banner -loglevel panic -ss 0 -t {match_length}'},
                outputs={f'{pre}.wav': None}
        )

        ff.run()
        return f'{pre}.wav'
    
    def calculate_offset(self, as_wave, vs_wave):
        p = os.popen(f"bash compute-sound-offset.sh '{as_wave}' '{vs_wave}' 0")
        offset_value = p.read().strip()
        return offset_value
    
    def make_synced_video(self, as_path, vs_path, offset_value):
        ff = ffmpy.FFmpeg(
            inputs={vs_path: '-hide_banner -loglevel panic', as_path:  f'-itsoffset {offset_value}'},
            outputs={'synced.mp4': '-c copy -map 0:0 -map 1:1 -shortest'}
        )
        ff.run()
        return 'synced.mp4'
    
    def clean_up(self, file_list):
        for file in file_list:
            os.remove(file)

            
help_message = """
Got one file with good audio and one with good video? Worry not!
videosynctool will automagically sync and create a new file with the best of both.
Usage: python videosynctool.py audio_source_file/youtube_url video_source_file/youtube_url [time_offset]
Outputs synced.mp4
"""
if __name__ == '__main__':
    cleanup_list = []
    sync_tool = VideoSyncTool()
    if len(sys.argv) < 3:
        print(help_message)
        exit(0)

    audio_source = sys.argv[1]
    video_source = sys.argv[2]

    as_url=validators.url(audio_source)
    vs_url=validators.url(video_source)

    if as_url:
        print('Downloading Audio Source File.')
        as_download_link = sync_tool.get_url(audio_source, '22')
        as_path = sync_tool.download_file(as_download_link, 'audio_source.mp4')
        cleanup_list.append(as_path)
    else:
        as_path = audio_source

    if vs_url:
        print('Downloading Video Source File.')
        vs_download_link = sync_tool.get_url(video_source, '22')
        vs_path = sync_tool.download_file(vs_download_link, 'video_source.mp4')
        cleanup_list.append(vs_path)
    else:
        vs_path = video_source

    
    if len(sys.argv) == 4:
        offset_value = sys.argv[3]
    else:
        print('Calculating Offset Value.')
        as_wave = sync_tool.extract_audio(as_path, 1000)
        vs_wave = sync_tool.extract_audio(vs_path, 1000)
        cleanup_list.append(as_wave)
        cleanup_list.append(vs_wave)
        offset_value = sync_tool.calculate_offset(as_wave, vs_wave)
    print('Making The Synced Video File.')
    sync_tool.make_synced_video(as_path, vs_path, offset_value)
    print('Output Saved at synced.mp4')
    print('Cleaning up.')
    sync_tool.clean_up(cleanup_list)
    print('Done')