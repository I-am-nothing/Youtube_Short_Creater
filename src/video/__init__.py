from src.video._video import Video
from src.video._video_provider import VideoProvider


class VideoService(Video):
    @staticmethod
    def add_to_queue(j_queue, config):
        VideoProvider.add_to_queue(j_queue, config)

    @staticmethod
    def remove_from_queue(queue_path, execute_type, config):
        VideoProvider.remove_from_queue(queue_path, execute_type, config)

    @staticmethod
    def get_index_from_queue(queue_path, execute_type):
        VideoProvider.get_index_from_queue(queue_path, execute_type)

    def __init__(self, config):
        self.provider = VideoProvider(config)

    def run(self):
        self.provider.run()

    def stop(self):
        self.provider.stop()

    def force_stop(self):
        self.provider.force_stop()

    def is_running(self):
        return self.provider.is_running()
