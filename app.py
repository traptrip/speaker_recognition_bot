import yaml
from pathlib import Path

from src.bot_module.bot import TGBot
from src.storage_manager import StorageManager
from src.recognition.speaker_recognizer import SpeakerRecognizer


with open(Path(__file__).parent / "config.yml", "r") as yml_file:
    cfg = yaml.load(yml_file, Loader=yaml.FullLoader)


class App:
    def __init__(self, config):
        self.config = config
        self.storage_manager = StorageManager()
        self.speaker_recognizer = SpeakerRecognizer(self, self.config['recognizer'])
        self.bot = TGBot(self, self.config['bot'])

    def run(self):
        self.bot.run()


if __name__ == '__main__':
    app = App(cfg)
    app.run()
