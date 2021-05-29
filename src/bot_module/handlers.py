from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# States
class UserStates(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    audio = State()  # Will be represented in storage as 'Form:audio'


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


async def cmd_help(message: types.Message):
    text = "/start - начать работу с ботом\n" \
           "/help - показать список команд\n" \
           "/add_voice - зарегистрировать новый голос\n" \
           "/cancel - прекратить выполнение любого процесса"
    await message.reply(text)


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


async def add_voice(message: types.Message):
    # Set state
    await UserStates.name.set()

    text = '''Как Вас зовут?'''
    await message.reply(text)


async def process_name_invalid(message: types.Message):
    return await message.reply("Вы должны написать свое имя")


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await UserStates.next()
    await message.reply(f"Теперь отправьте мне голосовое сообщение или аудиофайл с Вашим голосом")


# Check if we got something that isn't audio or voice
async def process_audio_invalid(message: types.Message):
    return await message.reply("Вы должны отправить аудиофайл формата .mp3 или голосовое сообщение")
