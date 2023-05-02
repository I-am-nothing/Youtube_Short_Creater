from abc import ABC, abstractmethod


class StableDiffusion(ABC):
    @staticmethod
    @abstractmethod
    def add_to_queue(j_locations, config):
        pass

    @staticmethod
    @abstractmethod
    def get_index_from_queue(queue_path, queue_path_index):
        pass

    @staticmethod
    @abstractmethod
    def remove_from_queue(queue_path, queue_path_index, config):
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
