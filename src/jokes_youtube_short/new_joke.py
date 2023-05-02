import os
import uuid
import json


class NewJoke:
    def __init__(self, output_path):
        self.output_path = os.path.join(output_path, "new-jokes")

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

    def remove_joke(self, joke_id):
        os.remove(os.path.join(self.output_path, joke_id + ".json"))

    def get(self, joke_id):
        try:
            with open(os.path.join(self.output_path, joke_id + ".json")) as j_file:
                j_joke = json.load(j_file)
                j_file.close()

            return j_joke
        except FileNotFoundError:
            return None

    def get_ids(self):
        return list(map(lambda s: s[:-5], [
            f for f in os.listdir(self.output_path)
            if os.path.isfile(os.path.join(self.output_path, f))
        ]))

    def get_list(self):
        j_jokes = {}
        for i in self.get_ids():
            j_jokes[i] = self.get(i)

        return j_jokes

    def add(self, j_joke):
        if not ("title" in j_joke and "joke" in j_joke):
            raise ValueError("Invalid j_joke data, it must contain title and joke")

        f_name = uuid.uuid4()

        with open(os.path.join(self.output_path, str(f_name) + ".json"), "w") as j_file:
            json.dump(j_joke, j_file, indent=2)
            j_file.close()

        return str(f_name)

    def add_from_chat_gpt(self):
        # todo
        pass