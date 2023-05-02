import json
import multiprocessing
import threading


class Config:
    def __init__(self, manager):
        self.text_2_speech_item_done = manager.list()
        self.text_2_speech_lock = multiprocessing.Lock()

        self.video_item_done = manager.list()
        self.video_lock = multiprocessing.Lock()

        self.stable_diffusion_item_done = manager.list()
        self.stable_diffusion_lock = multiprocessing.Lock()

        self.shared_lock = multiprocessing.Lock()

    @staticmethod
    def get_config():
        with open("config.json", 'r') as j_file:
            data = json.load(j_file)
            j_file.close()
        return data

    def text_2_speech_add_done_listener(self, path, func):
        self.text_2_speech_item_done.append((path, func))

    def text_2_speech_done(self, path):
        for listen_path, func in self.text_2_speech_item_done:
            if path == listen_path:
                func(path, self)

    def stable_diffusion_add_done_listener(self, listeners):
        self.stable_diffusion_item_done.extend(listeners)

    def stable_diffusion_done(self, path, index):
        for listen_path, listen_index, func in self.stable_diffusion_item_done:
            if path == listen_path and index == listen_index:
                func(path, index, self)

    def video_add_done_listener(self, path, execute_type, func):
        self.video_item_done.append((path, execute_type, func))

    def video_done(self, path, execute_type):
        for listen_path, listen_execute_type, func in self.video_item_done:
            if path == listen_path and execute_type == listen_execute_type:
                func(path, execute_type, self)

    def access_shard_file(self):
        return self.shared_lock
