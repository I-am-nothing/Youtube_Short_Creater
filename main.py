import multiprocessing
import threading
import time
import random
import string

import pyttsx3

from src.config import Config
from src.jokes_youtube_short import JokesYoutubeShort
from src.stable_diffusion import StableDiffusionService

from src.text_2_speech import Text2SpeechService
from src.video import VideoService

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    config = Config(manager)

    stable_diffusion_service = StableDiffusionService(config)
    text_2_speech_service = Text2SpeechService(config)
    video_service = VideoService(config)
    jokes_youtube_short = JokesYoutubeShort(config)

    stable_diffusion_service.run()
    #
    # text_2_speech_service.run()
    video_service.run()
    jokes_youtube_short.running_joke.generate_video("cea639ff-4928-4589-b7dd-7ee584c0b030")
    #
    # jokes_youtube_short.running_joke.generate_speech("cea639ff-4928-4589-b7dd-7ee584c0b030")

    # jokes_youtube_short.running_joke.generate_images("cea639ff-4928-4589-b7dd-7ee584c0b030")

    # jokes_youtube_short.running_joke.set_image_prompts("cea639ff-4928-4589-b7dd-7ee584c0b030", [
    #     {
    #         "index": 0,
    #         "prompt": "a man goes to the doctor for a checkup"
    #     },
    #     {
    #         "index": 9,
    #         "prompt": "after the exam the doctor delivers the news",
    #     },
    #     {
    #         "index": 17,
    #         "prompt": "i have good news and bad news he says"
    #     },
    #     {
    #         "index": 26,
    #         "prompt": "the man replies ok give me the good news first",
    #     },
    #     {
    #         "index": 36,
    #         "prompt": "the doctor smiles and says"
    #     },
    #     {
    #         "index": 41,
    #         "prompt": "you have twenty four hours to live",
    #     },
    #     {
    #         "index": 48,
    #         "prompt": "shocked the man"
    #     },
    #     {
    #         "index": 51,
    #         "prompt": "asks what could possibly be the bad news",
    #     },
    #     {
    #         "index": 59,
    #         "prompt": "the doctor responds"
    #     },
    #     {
    #         "index": 62,
    #         "prompt": "oh i forgot to tell you yesterday",
    #     },
    # ])

    time.sleep(10)
    while input("type stop to stop service") != "stop":
        continue

    # joke_id = JokesYoutubeShort().new_joke.add({
    #     "title": "The Good News and the Bad News",
    #     "joke": """A man goes to the doctor for a checkup. After the exam, the doctor delivers the news. "I have good news and bad news," he says.
    #
    #     The man replies, "Okay, give me the good news first."
    #
    #     The doctor smiles and says, "You have 24 hours to live."
    #
    #     Shocked, the man asks, "What could possibly be the bad news?"
    #
    #     The doctor responds, "I forgot to tell you yesterday.\""""
    # })
    # JokesYoutubeShort().confirm_new_joke(joke_id)
    #
    # JokesYoutubeShort().running_joke.generate_speech(joke_id)

    # time.sleep(5)
    # text_2_speech_service.stop()
    # time.sleep(30)
    # print(text_2_speech_service.is_running())
    # text_2_speech_service.run()
    # print(text_2_speech_service.is_running())


    #
    # stable_diffusion = StableDiffusion()
    # process = multiprocessing.Process(target=stable_diffusion.run(), args=())
    # process.start()

    # text_arr = [
    #     "A man goes to the doctor for a checkup.",
    #     "After the exam, the doctor delivers the news.",
    #     "I have good news and bad news, he says.",
    #     "The man replies, Okay, give me the good news first.",
    #     "The doctor smiles and says, You have 24 hours to live."
    #     "Shocked, the man asks, What could possibly be the bad news?",
    #     "The doctor responds, I forgot to tell you yesterday.",
    # ]
    # engine = pyttsx3.init()
    # for i in text_arr:
    #     engine.say(i)
    #     engine.runAndWait()
