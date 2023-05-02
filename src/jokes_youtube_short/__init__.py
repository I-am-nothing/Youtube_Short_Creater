import os

from src.config import Config
from src.jokes_youtube_short.new_joke import NewJoke
from src.jokes_youtube_short.running_joke import RunningJoke


class JokesYoutubeShort:
    def __init__(self, config2):
        config = Config.get_config()
        self.game_play_path = config["file_root"]["game_play"]
        self.background_audio_path = config["file_root"]["background_audio"]
        self.output_path = config["file_root"]["jokes_youtube_short"]

        if not os.path.exists(self.game_play_path):
            raise ValueError("Couldn't find the game play directory.")
        if not os.path.exists(self.background_audio_path):
            raise ValueError("Couldn't find the background audio directory.")
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path, exist_ok=True)

        self.new_joke = NewJoke(self.output_path)
        self.running_joke = RunningJoke(self.output_path, config2)

    def confirm_new_joke(self, joke_id):
        j_joke = self.new_joke.get(joke_id)

        if j_joke is None:
            raise FileNotFoundError(f"Could not find joke with {joke_id}")

        self.running_joke.add(joke_id, j_joke)
        self.new_joke.remove_joke(joke_id)

        # path = os.path.join(self.output_path, "items", joke_id)
        #
        # split_joke = []
        # image_queue = []
        # for i in re.split(r"[.!?]", j_joke["joke"]):
        #     text = i.strip().replace('"', "").replace("\n\n", "\n")
        #     if len(text) == 0:
        #         continue
        #     split_joke.append({
        #         "prompt": text,
        #         "negative_prompt": None,
        #         "width": 512,
        #         "height": 384,
        #         "selected": None
        #     })
        #     image_queue.append({
        #         "path": path,
        #         "index": len(split_joke) - 1
        #     })
        # j_joke["image_options"] = split_joke
        #
        # if not os.path.exists(path):
        #     os.makedirs(path, exist_ok=True)
        #
        # with open(os.path.join(path, "setting.json"), 'w') as j_file:
        #     json.dump(j_joke, j_file, indent=2)
        #     j_file.close()
        #
        # self.joke.remove_joke(joke_id)
        #
        # StableDiffusion.add_to_queues(image_queue)
