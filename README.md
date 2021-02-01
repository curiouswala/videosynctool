# videosynctool
Got one file with good audio and one with good video? Worry not! videosynctool will automagically sync and create a new file with the best of both.

## Setup
```git clone https://github.com/curiouswala/videosynctool```

```cd videosynctool```

```pip install -r requirements.txt```

## Usage
```python videosynctool.py audio_source_file/youtube_url video_source_file/youtube_url [time_offset]```

Output is saved in synced.mp4

## TODO
* Add auto quality selection for youtube(for now it only runs with 720p)
* Add visual sync for situation where one video doesn't have any audio.
* Make a manual offset finder gui with two videos playing side by side with an offset tuner.
* Windows compatibility
