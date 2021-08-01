"""
INSTRUCTIONS:

1. Install requirements:

    pip install -r requirements.txt

2. Run this script:

    python cut.py

3. Then upload the files in the `output/` directory to the following Google Drive folder:
https://drive.google.com/drive/folders/1ksa4G63bM_dtMHKV0rTsQZJlltrj4wiM

"""
import csv
import os
from io import StringIO
import shutil
import urllib.request
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
# from moviepy.video.io.VideoFileClip import VideoFileClip
import ffmpeg
import requests

from io import TextIOWrapper

INPUT_VIDEOS_URL = "https://docs.google.com/spreadsheet/ccc?key=1eE4wMzl2xdSYZYPV71UHvAe63d2SqPOJkAZchMESWVU&output=csv"
OUTPUT_DIRECTORY = "output"

# if os.path.exists(OUTPUT_DIRECTORY):
#     shutil.rmtree(OUTPUT_DIRECTORY)
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

QUIET = False

def extract_video(input_name, output_name, start_time, end_time):
    if not os.path.exists(input_name):
        raise Exception(f"File {input_name} does not exist, aborting")
    output_path_video = os.path.join(OUTPUT_DIRECTORY, output_name + ".mp4")
    output_path_audio = os.path.join(OUTPUT_DIRECTORY, output_name + ".mp3")
    if os.path.exists(output_path_video) and os.path.exists(output_path_audio):
        print(f"File {output_name} already exists, skipping")
        return
    print("Processing", input_name)

    # .filter('trim', start=start_time, end=end_time)
    def trim(x, audio=False):
        return x.filter('atrim' if audio else 'trim', start=0, end=end_time - start_time)
    
    input = ffmpeg.input(input_name, ss=start_time)
    video = trim(input.video)
    audio = trim(input.audio, audio=True)

    ffmpeg.output(audio, video, output_path_video).run(quiet=QUIET)

    ffmpeg.output(audio, output_path_audio).run(quiet=QUIET)


    print(f"Finished file: {input_name}, output: {output_name}", os.path.exists(input_name))


def get_seconds(time_str):
    hours, minutes, seconds = [int(x) for x in time_str.split(":")]
    return hours * 3600 + minutes * 60 + seconds

def main():
    response = requests.get(INPUT_VIDEOS_URL).text
    with StringIO(response) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # {'YouTube video name': 'Prakashananda - Wk7- July 30', 'File name': '', 'Start time (HH:MM:SS)': '', 'End time (HH:MM:SS)': '', 'Name': 'Rām Rāvaṇa Yuddha'}
            # if 'GMT20210618' not in row['File name']:
            #     continue
            try:
                extract_video(row['File name'], row['YouTube video name'] + ' - ' + row['Name'], get_seconds(row['Start time (HH:MM:SS)']), get_seconds(row['End time (HH:MM:SS)']))
            except Exception as e:
                # pass
                print(f"=== EXCEPTION for file {row['YouTube video name']}: {e}")


if __name__ == '__main__':
    main()