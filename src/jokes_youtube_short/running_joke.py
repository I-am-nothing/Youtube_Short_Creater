import os
import json
import re
import string
import random

from src.config import Config
from src.stable_diffusion import StableDiffusionService
from src.text_2_speech import Text2SpeechService
from src.video import VideoService


class RunningJoke:
    def __init__(self, output_path, config):
        self.config = config
        self.output_path = os.path.join(output_path, "running-jokes")

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

    def add(self, joke_id, j_joke):
        if not ("title" in j_joke and "joke" in j_joke):
            raise ValueError("Invalid j_joke data, it must contain title and joke")

        path = os.path.join(self.output_path, joke_id)
        if os.path.exists(path):
            raise FileExistsError(f"Joke: {joke_id} has already exist.")
        os.mkdir(path)

        with open(os.path.join(path, "setting.json"), 'w') as j_file:
            json.dump(j_joke, j_file, indent=2)
            j_file.close()

    def set_image_prompts(self, joke_id, prompts):
        with self.config.shared_lock:
            with open(os.path.join(self.output_path, joke_id, "setting.json"), "r") as j_file:
                j_setting = json.load(j_file)
                j_file.close()

            if not ("audio_durations" in j_setting and "audio_words" in j_setting):
                raise NotImplemented("Could not find audio_durations and audio_words in setting.json")

            for idx, prompt in enumerate(prompts):
                if "prompt" not in prompt:
                    raise ValueError(f"Could not find prompt data at {idx}")
                if not ("index" in prompt and prompt["index"] < len(j_setting["audio_words"])):
                    raise ValueError(f"index data error or out of range at {idx}")
                prompts[idx]["selected"] = None
                prompts[idx]["width"] = 512
                prompts[idx]["height"] = 384
                if "negative_prompt" not in prompt:
                    prompts[idx]["negative_prompt"] = "text, label, title, txt"

            j_setting["image_prompts"] = prompts

            with open(os.path.join(self.output_path, joke_id, "setting.json"), "w") as j_file:
                json.dump(j_setting, j_file, indent=2)

    @staticmethod
    def text_2_speech_done(path, config):
        print(f"text_2_speech_done listened, path: {path}")

    @staticmethod
    def stable_diffusion_done(path, index, config):
        print(f"stable_diffusion_done listened, path: {path}, index: {index}")

    @staticmethod
    def video_done(path, execute_type, config):
        print(f"video_done listened, path: {path}, execute_type: {execute_type}")

    def generate_speech(self, joke_id):
        path = os.path.join(self.output_path, joke_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find running joke: {joke_id}")

        with open(os.path.join(path, "setting.json"), "r") as j_file:
            j_joke = json.load(j_file)

        self.config.text_2_speech_add_done_listener(path, self.text_2_speech_done)

        Text2SpeechService.add_to_queue({
            "path": path,
            "text": j_joke["joke"]
        }, self.config)

    def generate_images(self, joke_id):
        path = os.path.join(self.output_path, joke_id)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Could not find running joke: {joke_id}")

        with open(os.path.join(path, "setting.json"), "r") as j_file:
            j_joke = json.load(j_file)
            j_file.close()

        if "image_prompts" not in j_joke:
            raise NotImplemented("Could not find image_prompts in setting.json")

        done_listeners = []

        for index in range(len(j_joke["image_prompts"])):
            j_joke["image_prompts"][index]["path"] = path
            j_joke["image_prompts"][index]["selected"] = None

            done_listeners.append((path, j_joke["image_prompts"][index]["index"], self.stable_diffusion_done))

        self.config.stable_diffusion_add_done_listener(done_listeners)
        StableDiffusionService.add_to_queue(j_joke["image_prompts"], self.config)

    def generate_video(self, joke_id):
        path = os.path.join(self.output_path, joke_id)
        self.config.video_add_done_listener(path, VideoService.JOKES_YOUTUBE_SHORT, RunningJoke.video_done)
        VideoService.add_to_queue({
            "path": path,
            "execute_type": VideoService.JOKES_YOUTUBE_SHORT
        }, self.config)
