import multiprocessing

from src.text_2_speech._text_2_speech import Text2Speech
from src.text_2_speech._text_2_speech_provider import Text2SpeechProvider


class Text2SpeechService(Text2Speech):
    @staticmethod
    def add_to_queue(j_queue, config):
        Text2SpeechProvider.add_to_queue(j_queue, config)

    @staticmethod
    def remove_from_queue(queue_path, config):
        Text2SpeechProvider.remove_from_queue(queue_path, config)

    @staticmethod
    def get_index_from_queue(queue_path):
        Text2SpeechProvider.remove_from_queue(queue_path)

    def __init__(self, config):
        self.provider = Text2SpeechProvider(config)

    def run(self):
        self.provider.run()

    def stop(self):
        self.provider.stop()

    def force_stop(self):
        self.provider.force_stop()

    def is_running(self):
        return self.provider.is_running()
