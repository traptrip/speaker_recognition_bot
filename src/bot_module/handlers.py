from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


# States
class UserStates(StatesGroup):
    name = State()  # Will be represented in storage as 'Form:name'
    audio = State()  # Will be represented in storage as 'Form:audio'


async def cmd_start(message: types.Message):
    text = "Приветствую!\n" \
           "Я бот идентифицирующий людей по их голосу.\n" \
           "Чтобы добавить свой голос, и я мог узнать Вас, напишите " \
           "/add_voice\n" \
           "Если Вы зарегистрированы, просто пришлите мне голосовое сообщение или аудиофайл, и я скажу, кто Вы.\n" \
           "Чтобы посмотреть список доступных команд напишите /help"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/add_voice", "/cancel", "/help"]
    keyboard.add(*buttons)

    await message.reply(text, reply_markup=keyboard)


async def cmd_help(message: types.Message):
    text = "/start - начать работу с ботом\n" \
           "/help - показать список команд\n" \
           "/add_voice - зарегистрировать новый голос\n" \
           "/cancel - прекратить процесс добавления человека"
    await message.reply(text)


async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Операция прекращена.')


async def add_voice(message: types.Message):
    await UserStates.name.set()
    await message.reply("Введите имя человека, которого хотите зарегистрировать")


async def process_name_invalid(message: types.Message):
    return await message.reply("Вы должны написать имя")


async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await UserStates.next()
    await message.reply(f"Теперь отправьте голосовое сообщение или аудиофайл с голосом этого человека\n"
                        f"Чтобы бот мог корректно распознать голос, аудио должно содержать не менее 3-5 секунд речи.")


async def process_audio_invalid(message: types.Message):
    return await message.reply("Вы должны отправить аудиофайл или голосовое сообщение")
