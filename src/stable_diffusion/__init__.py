from src.stable_diffusion._stable_diffusion import StableDiffusion
from src.stable_diffusion.stable_diffusion_provider import StableDiffusionProvider


class StableDiffusionService(StableDiffusion):
    @staticmethod
    def add_to_queue(j_locations, config):
        StableDiffusionProvider.add_to_queue(j_locations, config)

    @staticmethod
    def get_index_from_queue(queue_path, queue_path_index):
        StableDiffusionProvider.get_index_from_queue(queue_path, queue_path_index)

    @staticmethod
    def remove_from_queue(queue_path, queue_path_index, config):
        StableDiffusionProvider.remove_from_queue(queue_path, queue_path_index, config)

    def __init__(self, config):
        self.provider = StableDiffusionProvider(config)

    def run(self):
        self.provider.run()

    def stop(self):
        self.provider.stop()

    def force_stop(self):
        self.provider.force_stop()

    def is_running(self):
        return self.provider.is_running()
