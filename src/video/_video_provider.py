import multiprocessing
import os.path
import random
import time

from src.video._video import Video
from src.config import Config

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip, ImageClip, \
    concatenate_videoclips
from moviepy.audio.fx.all import volumex
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip

import json


class VideoProvider(Video):

    @staticmethod
    def add_to_queue(j_queue, config):
        if not ("path" in j_queue and "execute_type" in j_queue):
            raise ValueError("Invalid j_queue data, it must contains path and execute_type")

        if j_queue["execute_type"] == Video.JOKES_YOUTUBE_SHORT:
            if not os.path.exists(os.path.join(j_queue["path"], "speech.wav")):
                raise NotImplemented("You need to generate speech.wav first.")
            with open(os.path.join(j_queue["path"], "setting.json"), "r") as j_file:
                j_setting = json.load(j_file)
                j_file.close()
            if "audio_durations" not in j_setting:
                raise NotImplemented("You need to generate audio_durations in setting.json first.")

        index, _ = VideoProvider.get_index_from_queue(j_queue["path"], j_queue["execute_type"])
        if index is None:
            with config.video_lock:
                with open("video.json", "r") as j_file:
                    j_config = json.load(j_file)
                    j_file.close()
                j_config["queue"].append(j_queue)
                with open("video.json", "w") as j_file:
                    json.dump(j_config, j_file, indent=2)
                    j_file.close()

    @staticmethod
    def remove_from_queue(queue_path, execute_type, config):
        with config.video_lock:
            with open("video.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            index, _ = VideoProvider.get_index_from_queue(queue_path, execute_type)

            if index is not None:
                del j_config["queue"][index]

            with open("video.json", "w") as j_file:
                json.dump(j_config, j_file, indent=2)
                j_file.close()

    @staticmethod
    def get_index_from_queue(queue_path, execute_type):
        with open("video.json", "r") as j_file:
            j_config = json.load(j_file)
            j_file.close()

        for i, data in enumerate(j_config["queue"]):
            if data["path"] == queue_path and data["execute_type"] == execute_type:
                return i, len(j_config["queue"])
        else:
            return None, None

    def _get_top_from_queue(self):
        with self.config.video_lock:
            with open("video.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            if len(j_config["queue"]) > 0:
                j_config["current_item"] = j_config["queue"][0]
            else:
                j_config["current_item"] = None

            with open("video.json", "w") as j_file:
                json.dump(j_config, j_file, indent=2)
                j_file.close()

        return j_config["queue"][0] if len(j_config["queue"]) else None

    def __init__(self, config):
        self.config = config
        self.process = multiprocessing.Process(target=self._run, args=())
        self.stop_event = None

    def run(self):
        self.process = multiprocessing.Process(target=self._run, args=())
        self.stop_event = multiprocessing.Event()
        if not self.process.is_alive():
            self.process.start()

    def stop(self):
        self.stop_event.set()

    def force_stop(self):
        self.process.terminate()

    def is_running(self):
        return self.process.is_alive()

    def _run(self):
        while not self.stop_event.is_set():
            item = self._get_top_from_queue()
            if item is None:
                time.sleep(1)
                continue

            if item["execute_type"] == Video.JOKES_YOUTUBE_SHORT:
                game = random.choice(os.listdir(Config.get_config()["file_root"]["game_play"]))
                game_video = random.choice(
                    os.listdir(os.path.join(Config.get_config()["file_root"]["game_play"], game))
                )
                laugh = random.choice(os.listdir(Config.get_config()["file_root"]["laugh_audio"]))

                speech_audio = AudioFileClip(os.path.join(item["path"], "speech.wav"))
                laugh_audio = AudioFileClip(
                    os.path.join(Config.get_config()["file_root"]["laugh_audio"], laugh)
                ).fx(volumex, 0.1)

                combined_audio = CompositeAudioClip(
                    [speech_audio, laugh_audio.set_start(speech_audio.duration - 1)]
                )
                game_video = VideoFileClip(
                    os.path.join(Config.get_config()["file_root"]["game_play"], game, game_video)
                )

                video_start = random.uniform(0, game_video.duration - combined_audio.duration)
                game_video = game_video.subclip(video_start, video_start + combined_audio.duration)

                combined_audio.fps = speech_audio.fps
                final_video = game_video.set_audio(combined_audio)
                final_video = crop(final_video, width=607.5, height=1080, x_center=960, y_center=540)
                final_video = final_video.resize(width=1080, height=1920)

                subtitle_data = []
                image_data = []

                with open(os.path.join(item["path"], "setting.json"), "r") as j_file:
                    j_setting = json.load(j_file)
                    j_file.close()

                    texts = []
                    for i in range(len(j_setting["audio_words"]) - 1):
                        texts.append(j_setting["audio_words"][i].replace("\n", ""))
                        if len(" ".join(texts)) < 10 and len(" ".join(texts)) + len(j_setting["audio_words"][i + 1]) \
                                + 1 < 15:
                            continue

                        start = j_setting["audio_durations"][i - len(texts)][1] if i - len(texts) > 0 else 0
                        subtitle_data.append((
                            (start, j_setting["audio_durations"][i][1]),
                            " ".join(texts)
                        ))
                        texts = []

                    texts.append(j_setting["audio_words"][len(j_setting["audio_words"]) - 1])
                    start = j_setting["audio_durations"][len(j_setting["audio_words"]) - 1 - len(texts)][1] \
                        if len(j_setting["audio_words"]) - 1 - len(texts) > 0 else 0
                    subtitle_data.append((
                        (start, j_setting["audio_durations"][len(j_setting["audio_words"]) - 1][1]),
                        " ".join(texts)
                    ))

                    j_setting["image_prompts"].sort(key=lambda x: x["index"])
                    for image in j_setting["image_prompts"]:
                        if image["selected"] is not None:
                            image_data.append((
                                os.path.join(
                                    item["path"], "images", '{:02d}'.format(image["index"]),
                                    '{:02d}.png'.format(image["selected"])
                                ),
                                j_setting["audio_durations"][image["index"]][0]
                            ))

                generator = lambda txt: TextClip(txt, font='Arial-Bold', fontsize=128, color='white',
                                                 stroke_color='black', stroke_width=4)
                subtitles = SubtitlesClip(subtitle_data, generator)

                image_clip = concatenate_videoclips([
                    ImageClip(image_data[i][0])
                    .set_start(image_data[i][1])
                    .set_duration(
                        (image_data[i + 1][1] - image_data[i][1])
                        if i != len(image_data)-1 else final_video.duration - image_data[i][1]
                    )
                    for i in range(len(image_data))
                ], method="compose").resize((896, 672)).set_position(("center", 1920 / 4 - 336))

                final_video = CompositeVideoClip(
                    [final_video, image_clip, subtitles.set_position(('center', 'center'))])

                final_video.write_videofile(
                    os.path.join(item["path"], "video.mp4"), fps=game_video.fps, codec='libx264'
                )

            self.remove_from_queue(item["path"], item["execute_type"], self.config)
            self.config.video_done(item["path"], item["execute_type"])
