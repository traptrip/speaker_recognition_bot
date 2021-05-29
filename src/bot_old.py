import yaml
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor


with open(Path(__file__).parent / "../config.yml", "r") as yml_file:
    cfg = yaml.load(yml_file, Loader=yaml.FullLoader)
audio_data_path = Path(__file__).parent / "../data/audios"

bot = Bot(token=cfg['bot']['BOT_TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# States
class UserStates(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    audio = State()  # Will be represented in storage as 'Form:audio'


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    text = "Приветствую!\n" \
           "Я бот идентифицирующий людей по их голосу\n" \
           "Чтобы добавить свой голос и я мог узнать Вас напишите \n" \
           "/add_voice\n" \
           "Если Вы зарегистрированны просто пришлите мне голосовое сообщение или аудиофайл и я скажу кто Вы"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/add_voice", "/cancel", "/help"]
    keyboard.add(*buttons)

    await message.reply(text, reply_markup=keyboard)


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    text = "/start - начать работу с ботом\n" \
           "/help - показать список команд\n" \
           "/add_voice - зарегистрировать новый голос\n" \
           "/cancel - прекратить выполнение любого процесса"
    await message.reply(text)


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    # Cancel state and inform user about it
    await state.finish()
    # Remove keyboard (just in case)
    await message.reply('Операция прекращена.')


@dp.message_handler(commands='add_voice')
async def add_voice(message: types.Message):
    # Set state
    await UserStates.name.set()

    text = '''Как Вас зовут?'''
    await message.reply(text)


@dp.message_handler(lambda message: message.text is None, state=UserStates.name)
async def process_name_invalid(message: types.Message):
    return await message.reply("Вы должны написать свое имя")


@dp.message_handler(state=UserStates.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await UserStates.next()
    await message.reply(f"Теперь отправьте мне голосовое сообщение или аудиофайл с Вашим голосом")


# Check if we got something that isn't audio or voice
@dp.message_handler(lambda message: message.audio is None and message.voice is None, state=UserStates.audio)
async def process_audio_invalid(message: types.Message):
    return await message.reply("Вы должны отправить аудиофайл формата .mp3 или голосовое сообщение")


@dp.message_handler(content_types=types.ContentTypes.AUDIO | types.ContentTypes.VOICE, state=UserStates.audio)
async def process_audio(message: types.Message, state: FSMContext):
    audio = message.audio or message.voice
    await message.reply("Голос обрабатывается...")
    file = await bot.get_file(audio.file_id)
    file_path = file.file_path
    async with state.proxy() as data:
        await bot.download_file(file_path, f"{audio_data_path}/{data['name']}_{audio.file_unique_id}.wav")

    await message.reply("Голос добавлен")
    # Finish conversation
    await state.finish()


@dp.message_handler(content_types=types.ContentTypes.AUDIO | types.ContentTypes.VOICE)
async def process_audio_no_stage(message: types.Message):
    audio = message.audio or message.voice
    await message.reply("Голос обрабатывается...")
    file = await bot.get_file(audio.file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f"{audio_data_path}/user_{audio.file_unique_id}.wav")
    await message.reply("Голос проверяется нейросетью...")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
