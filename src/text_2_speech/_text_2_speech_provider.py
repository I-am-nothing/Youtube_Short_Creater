import json
import multiprocessing
import os.path
import threading
import time
import random

import pyttsx3
import wave

from src.text_2_speech import Text2Speech
from src.video import VideoService
from src.config import Config

from vosk import Model, KaldiRecognizer, SetLogLevel


class Text2SpeechProvider(Text2Speech):

    @staticmethod
    def add_to_queue(j_queue, config):
        if not ("path" in j_queue and "text" in j_queue):
            raise ValueError("Invalid j_queue data, it must contains path and text")
        index, _ = Text2SpeechProvider.get_index_from_queue(j_queue["path"])
        if index is None:
            with config.text_2_speech_lock:
                with open("text_2_speech.json", "r") as j_file:
                    j_config = json.load(j_file)
                    j_file.close()
                j_config["queue"].append(j_queue)
                with open("text_2_speech.json", "w") as j_file:
                    json.dump(j_config, j_file, indent=2)
                    j_file.close()

    @staticmethod
    def remove_from_queue(queue_path, config):
        with config.text_2_speech_lock:
            with open("text_2_speech.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            index, _ = Text2SpeechProvider.get_index_from_queue(queue_path)
            if index is not None:
                del j_config["queue"][index]

            with open("text_2_speech.json", "w") as j_file:
                json.dump(j_config, j_file, indent=2)
                j_file.close()

    @staticmethod
    def get_index_from_queue(queue_path):
        with open("text_2_speech.json", "r") as j_file:
            j_config = json.load(j_file)
            j_file.close()

        for i, data in enumerate(j_config["queue"]):
            if data["path"] == queue_path:
                return i, len(j_config["queue"])
        else:
            return None, None

    def _get_top_from_queue(self):
        with self.config.text_2_speech_lock:
            with open("text_2_speech.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            if len(j_config["queue"]) > 0:
                j_config["current_item"] = j_config["queue"][0]
            else:
                j_config["current_item"] = None

            with open("text_2_speech.json", "w") as j_file:
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
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        english_voices = [v for v in voices if "English" in v.name]

        model = Model(Config.get_config()["file_root"]["speech_recognition"])

        while not self.stop_event.is_set():
            item = self._get_top_from_queue()

            if item is None:
                time.sleep(1)
                continue

            print("text_2_speech- execute start...")

            engine.setProperty("voice", random.choice(english_voices).id)
            durations = []
            audio_words = []

            engine.save_to_file(item["text"], os.path.join(item["path"], "speech.wav"))
            print("text_2_speech- making speech.wav...")
            engine.runAndWait()

            print("text_2_speech- run speech recognition...")
            wf = wave.open(os.path.join(item["path"], "speech.wav"), "rb")
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    part_result = json.loads(rec.Result())
                    results.append(part_result)
            part_result = json.loads(rec.FinalResult())
            results.append(part_result)
            wf.close()

            for sentence in results:
                if len(sentence) == 1:
                    continue
                for obj in sentence['result']:
                    durations.append([obj["start"], obj["end"]])
                    audio_words.append(obj["word"])

            print("text_2_speech- write setting file...")
            with self.config.access_shard_file():
                with open(os.path.join(item["path"], "setting.json"), "r") as j_file:
                    j_setting = json.load(j_file)
                    j_file.close()
                j_setting["audio_durations"] = durations
                j_setting["audio_words"] = audio_words
                with open(os.path.join(item["path"], "setting.json"), "w") as j_file:
                    json.dump(j_setting, j_file, indent=2)
                    j_file.close()

            # VideoService.add_to_queue({
            #     "path": item["path"],
            #     "execute_type": VideoService.YOUTUBE_SHORT_BACKGROUND
            # })
            self.remove_from_queue(item["path"], self.config)
            self.config.text_2_speech_done(item["path"])
            print("text_2_speech- done execute...")
