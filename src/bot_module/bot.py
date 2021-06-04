import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from src.bot_module.handlers import *

audio_data_path = Path(__file__).parent / "../../data/audios"


class TGBot:
    def __init__(self, app, bot_config):
        self.config = bot_config
        self.storage_manager = app.storage_manager
        self.speaker_recognizer = app.speaker_recognizer
        self.bot = Bot(token=bot_config['BOT_TOKEN'])
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)

        self.dp.register_message_handler(cmd_start, commands="start")
        self.dp.register_message_handler(cmd_help, commands="help")
        self.dp.register_message_handler(cancel_handler,
                                         Text(equals='/cancel', ignore_case=True),
                                         state="*")
        self.dp.register_message_handler(add_voice,
                                         commands="add_voice")
        self.dp.register_message_handler(process_name_invalid,
                                         lambda message: not message.text,
                                         state=UserStates.name)
        self.dp.register_message_handler(process_name,
                                         state=UserStates.name)
        self.dp.register_message_handler(process_audio_invalid,
                                         lambda message: message.audio is None and message.voice is None,
                                         state=UserStates.audio)
        self.dp.register_message_handler(self.add_audio,
                                         state=UserStates.audio,
                                         content_types=types.ContentTypes.AUDIO | types.ContentTypes.VOICE)
        self.dp.register_message_handler(self.process_audio,
                                         content_types=types.ContentTypes.AUDIO | types.ContentTypes.VOICE,
                                         )

    async def add_audio(self, message: types.Message, state: FSMContext):
        audio = message.audio or message.voice
        file = await self.bot.get_file(audio.file_id)
        file_path = file.file_path
        async with state.proxy() as data:
            speaker_name = data['name']
        audio_path = f"{audio_data_path}/{speaker_name}_{audio.file_unique_id}.wav"
        await self.bot.download_file(file_path, audio_path)

        await message.reply("Голос обрабатывается...")
        speaker_vector = self.speaker_recognizer.get_speaker_vector(audio_path)
        os.remove(audio_path)
        self.storage_manager.add_speaker(speaker_name,
                                         speaker_vector[0])

        await message.answer("Голос добавлен")
        await message.answer("Теперь Вы можете отправить голосовое сообщение или аудиозапись, и бот скажет, кто Вы")

        # Finish conversation
        await state.finish()

    async def process_audio(self, message: types.Message):
        audio = message.audio or message.voice
        await message.reply("Голос обрабатывается...")
        file = await self.bot.get_file(audio.file_id)
        file_path = file.file_path
        audio_path = f"{audio_data_path}/user_{audio.file_unique_id}.wav"
        await self.bot.download_file(file_path, audio_path)
        await message.answer("Голос проверяется нейросетью...")
        speaker_info = self.speaker_recognizer.recognize_speaker(audio_path)
        os.remove(audio_path)
        if speaker_info[0]:
            await message.answer(f"ID: {speaker_info[0][0]}\n"
                                 f"NAME: {speaker_info[0][1]}\n"
                                 f"CONFIDENCE: {speaker_info[0][2]}")
        elif speaker_info[1]:
            await message.answer(f"Система не достаточно уверена, но возможно это Вы:\n"
                                 f"ID: {speaker_info[1][0]}\n"
                                 f"NAME: {speaker_info[1][1]}\n"
                                 f"CONFIDENCE: {speaker_info[1][2]:.4f}")
        else:
            await message.answer("В системе нет зарегистрированных голосов")

    def run(self):
        executor.start_polling(self.dp, skip_updates=True)

