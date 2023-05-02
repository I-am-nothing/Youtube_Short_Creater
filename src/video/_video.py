from abc import ABC, abstractmethod


class Video(ABC):
    JOKES_YOUTUBE_SHORT = "jokes-youtube-short"

    @staticmethod
    @abstractmethod
    def add_to_queue(j_queue, config):
        pass

    @staticmethod
    @abstractmethod
    def remove_from_queue(queue_path, execute_type, config):
        pass

    @staticmethod
    @abstractmethod
    def get_index_from_queue(queue_path, execute_type):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def force_stop(self):
        pass

    @abstractmethod
    def is_running(self):
        pass
