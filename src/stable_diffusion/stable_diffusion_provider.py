import json
import multiprocessing
import os
import time

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

from src.stable_diffusion._stable_diffusion import StableDiffusion
from src.stable_diffusion.prompt_engineering import joke_art_styles

from src.config import Config


#
# # SDV5_MODEL_PATH = os.getenv('SDV5_MODEL_PATH')
# SAVE_PATH = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'SD_OUTPUT')
#
# prompt = 'A red panda eating birthday cake'
# negative_prompt = 'cats, people, humans, ugly, unrealistic, bad, contrast, bad lighting, poorly drawn, morphed, disfigured, weird, odd'
#
# num_images_per_prompt = 5
# num_inference_step = 100
#
# width = 1024
# height = 768
#
# device_type = 'cuda'
# low_v_ram = True
#
#
# def uniquify(path):
#     filename, extension = os.path.splitext(path)
#     counter = 1
#
#     while os.path.exists(path):
#         path = f'{filename} ({counter}){extension}'
#         counter += 1
#
#     return path
#
#
# def render_prompt():
#     shorted_prompt = (prompt[:25] + '...') if len(prompt) > 25 else prompt
#     shorted_prompt = shorted_prompt.replace(' ', '_')
#
#     generation_path = os.path.join(SAVE_PATH, shorted_prompt.removesuffix('...'))
#
#     if not os.path.exists(SAVE_PATH):
#         os.mkdir(SAVE_PATH)
#     if not os.path.exists(generation_path):
#         os.mkdir(generation_path)
#
#     if device_type == 'cuda':
#          if low_v_ram:
#              pipe = StableDiffusionPipeline.from_pretrained(
#                  SDV5_MODEL_PATH,
#                  torch_dtype=torch.float16,
#                  revision='fp16'
#              )
#          else:
#              pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH)
#
#          pipe = pipe.to('cuda')
#
#          if low_v_ram:
#              pipe.enable_attention_slicing()
#
#     elif device_type == 'cpu':
#         pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH)
#     else:
#         print('Invalid Device Type Selected, use "cpu" or "cuda" only.')
#         return
#
#     for style_type, style_prompt in art_styles.items():
#         prompt_stylized = f'{prompt}, {style_prompt}'
#
#         print(f'\nFull Prompt : \n{prompt_stylized}\n')
#         print(f'Characters in promote: {len(prompt_stylized)}, limit: 200')
#
#         for i in range(num_images_per_prompt):
#             if device_type == 'cuda':
#                 with autocast('cuda'):
#                     image = pipe(
#                         prompt_stylized,
#                         negative_prompt=negative_prompt,
#                         width=width,
#                         height=height,
#                     ).images[0]
#             else:
#                 image = pipe(prompt).images[0]
#
#             image_path = uniquify(os.path.join(SAVE_PATH, generation_path, style_type + ' - ' + shorted_prompt) + '.png')
#             print(image_path)
#
#             image.save(image_path)
#     print('\nRENDER FINISHED\n')
#
# render_prompt()

class StableDiffusionProvider(StableDiffusion):
    @staticmethod
    def add_to_queue(j_locations, config):
        del_number = 0
        for idx, j_location in enumerate(j_locations):
            if not ("path" in j_location and "index" in j_location):
                raise ValueError("Invalid j_location data, it must contains path and index.")
            idx, _ = StableDiffusionProvider.get_index_from_queue(j_location["path"], j_location["index"])
            if idx is not None:
                del j_locations[idx - del_number]
                del_number += 1

        with config.stable_diffusion_lock:
            with open("stable_diffusion.json", "r") as j_file:
                j_queue = json.load(j_file)
                j_file.close()
            j_queue["queue"].extend(j_locations)

            with open("stable_diffusion.json", "w") as j_file:
                json.dump(j_queue, j_file, indent=2)

    @staticmethod
    def get_index_from_queue(queue_path, queue_path_index):
        with open("stable_diffusion.json", "r") as j_file:
            j_config = json.load(j_file)
            j_file.close()

        for i, data in enumerate(j_config["queue"]):
            if data["path"] == queue_path and data["index"] == queue_path_index:
                return i, len(j_config["queue"])
        else:
            return None, None

    @staticmethod
    def remove_from_queue(queue_path, queue_path_index, config):
        with config.stable_diffusion_lock:
            with open("stable_diffusion.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            index, _ = StableDiffusionProvider.get_index_from_queue(queue_path, queue_path_index)
            if index is not None:
                del j_config["queue"][index]

            with open("stable_diffusion.json", "w") as j_file:
                json.dump(j_config, j_file, indent=2)
                j_file.close()

    def _get_top_from_queue(self):
        with self.config.stable_diffusion_lock:
            with open("stable_diffusion.json", "r") as j_file:
                j_config = json.load(j_file)
                j_file.close()

            if len(j_config["queue"]) > 0:
                j_config["current_item"] = j_config["queue"][0]
            else:
                j_config["current_item"] = None

            with open("stable_diffusion.json", "w") as j_file:
                json.dump(j_config, j_file, indent=2)
                j_file.close()

        return j_config["queue"][0] if len(j_config["queue"]) else None

    def __init__(self, config):
        self.config = config
        self.process = multiprocessing.Process(target=self._run, args=())
        self.stop_event = None

        with open("stable_diffusion.json", "r") as j_file:
            j_queue = json.load(j_file)
            j_file.close()
            self.SDV5_MODEL_PATH = Config.get_config()["file_root"]["stable_diffusion"]
            self.device_type = j_queue["device_type"]
            self.low_v_ram = j_queue["low_v_ram"]
            self.num_images_per_prompt = j_queue["num_images_per_prompt"]
            self.num_inference_step = j_queue["num_inference_step"]
            self.stop = True

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
        while not self.stop_event.is_set():
            item = self._get_top_from_queue()

            if item is None:
                time.sleep(1)
                continue

            self._render_prompt(item)
            self.remove_from_queue(item["path"], item["index"], self.config)

    @staticmethod
    def _uniquify(file_path):
        counter = 1

        while os.path.exists(f'{file_path}/{"{:02d}".format(counter)}.png'):
            counter += 1

        return f'{file_path}/{"{:02d}".format(counter)}.png'

    def _render_prompt(self, prompt):
        path = os.path.join(prompt["path"], "images", '{:02d}'.format(prompt["index"]))

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        if self.device_type == 'cuda':
            if self.low_v_ram:
                pipe = StableDiffusionPipeline.from_pretrained(
                    self.SDV5_MODEL_PATH,
                    torch_dtype=torch.float16,
                    revision='fp16',
                )
            else:
                pipe = StableDiffusionPipeline.from_pretrained(self.SDV5_MODEL_PATH)

            pipe = pipe.to('cuda')

            if self.low_v_ram:
                pipe.enable_attention_slicing()

        elif self.device_type == 'cpu':
            pipe = StableDiffusionPipeline.from_pretrained(self.SDV5_MODEL_PATH)
        else:
            print('Invalid Device Type Selected, use "cpu" or "cuda" only.')
            return

        for style_type, style_prompt in joke_art_styles.items():
            prompt_stylized = f'{prompt["prompt"]}, {style_prompt}'

            print(f'\nFull Prompt: \n{prompt_stylized}\n')
            print(f'Characters in promote: {len(prompt_stylized)}, limit: 200')

            for i in range(self.num_images_per_prompt):
                if self.device_type == 'cuda':
                    with autocast('cuda'):
                        image = pipe(
                            prompt_stylized,
                            negative_prompt=prompt["negative_prompt"],
                            width=prompt["width"],
                            height=prompt["height"],
                            num_inference_steps=self.num_inference_step,
                        ).images[0]
                else:
                    image = pipe(prompt["prompt"]).images[0]

                image.save(StableDiffusionProvider._uniquify(path))

        self.config.stable_diffusion_done(prompt["path"], prompt["index"])
