import requests,random,asyncio
from aiogram import Router, types,F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram_sentinel import Sentinel, SentinelConfig, debounce
from collections import defaultdict
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, CallbackQuery,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


_user_locks = defaultdict(asyncio.Lock)


router = Router()


GITHUB_RAW_URL = "https://raw.githubusercontent.com/Nikitoskaaa/Japan-facts/refs/heads/main/japan_facts.txt"
INFO_TEXT = (
    "🌸 <b>Гид по Японии</b>\n\n"
    "Я бот-гид: рассказываю интересное о Японии, показываю погоду "
    "и иногда делюсь фактами про кошек.\n\n"
    "<b>Что я умею:</b>\n"
    "Fact⛩️ — случайный факт о Японии\n"
    "Weather🌦️ — температура в любом городе (например: Токио, Осака, Киото)\n"
    "Cat🐱 — случайный факт про кошек\n"
    "Infoℹ️ — это сообщение\n\n"
    "Данные беру из интернета, поэтому иногда ответ может прийти не сразу."
)



# 1. Определяем состояния
class FUNCGet_city(StatesGroup):
    data_from_weather_command = State()

# 2. Команда save💾 — запускаем ожидание
@router.message(F.text == "Weather🌦️")
async def get_data_from_command_weather_state(message: Message, state: FSMContext):
    await message.answer("Напишите название города, например(Токио,Осака):",reply_markup=get_main_reply_keyboard())
    await state.set_state(FUNCGet_city.data_from_weather_command)


# 3. Ловим ответ пользователя
@router.message(FUNCGet_city.data_from_weather_command)
async def get_temperature(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city:
        await message.answer("Напишите текст.",reply_markup=get_main_reply_keyboard())
        return
    try:
        print("парсим погоду...")
        await message.answer("Ждем ответ...")
        link = f"https://wttr.in/{city}?format=%t&lang=ru"
        x = requests.get(link).text
        if "location not found" in x.lower() or not x:
            await message.answer(f"Ненашлось города |-> {city} <-| попробуйте скопировать название города и вставить",reply_markup=get_main_reply_keyboard())
            return
        x = x.replace("°C", "")
        x = x.replace("Â", "")
        await message.answer(f"В городе {city} {x} градусов 🌡️",reply_markup=get_main_reply_keyboard())
        await state.clear()
    except(requests.exceptions.RequestException) as e:
        await message.answer(f"Не удалось узнать погоду в {city} ошибка: '{e}'",reply_markup=get_main_reply_keyboard())
        await message.answer("Что-то пошло не так. Подождите некоторое время и попробуйте позже.")
        await state.clear()


#----keyboards----
def get_main_inline_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Github",url="https://github.com/GDKopat")],
            [InlineKeyboardButton(text="Info",callback_data="CallInfo")]
        ]
    )
    return keyboard


def get_main_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Fact⛩️"),KeyboardButton(text="Weather🌦️")],
            [KeyboardButton(text="Cat🐱"),KeyboardButton(text="Infoℹ️")],
        ],
        resize_keyboard=True
    )
    return keyboard


#----main functions----
@router.callback_query(lambda call: call.data == "CallInfo")
async def Call_info_func(callback: CallbackQuery):
    await callback.message.answer(INFO_TEXT, parse_mode="HTML",reply_markup=get_main_reply_keyboard())
    await callback.answer()



@router.message(Command("start"))  #ПРАВИЛЬНО - через Command
@debounce(5.0)
async def start(message: Message):
    await message.answer("Привет 👋 Бот работает!",reply_markup=get_main_inline_keyboard())


@router.message(F.text == "Infoℹ️")
@debounce(5.0)
async def info(message:Message):
    await message.answer(INFO_TEXT, parse_mode="HTML",reply_markup=get_main_reply_keyboard())


@router.message(F.text == "Fact⛩️")
async def get_random_japan_fact_from_github(message:Message):
    user_id = message.from_user.id
    lock = _user_locks[user_id]
    if lock.locked():
        return
    async with lock:
        print("парсим факт о японии...")
        await message.answer("Ждем ответ...",reply_markup=get_main_reply_keyboard())
        try:
            response = requests.get(GITHUB_RAW_URL,timeout=10)
            response.raise_for_status()
            facts = response.text.strip().split("\n")
            facts = [fact.strip() for fact in facts if fact.strip()]
            fact = random.choice(facts)
            await message.answer(f"\n🌸 Случайный факт о Японии: {fact}\n",reply_markup=get_main_reply_keyboard())
            print("Факт о японии выдан!")
        except requests.exceptions.RequestException as e:
            await message.answer("Что-то пошло не так. Подождите некоторое время и попробуйте позже.")
            print(f"Ошибка соединения: {e}. Проверьте интернет или ссылку.")



@router.message(F.text == "Cat🐱")
async def get_daily_quote(message:Message):
    user_id = message.from_user.id
    lock = _user_locks[user_id]
    if lock.locked():
        return
    async with lock:
        print("парсим кошек...")
        await message.answer("Ждем ответ...",reply_markup=get_main_reply_keyboard())
        try:
            url = "https://meowfacts.herokuapp.com/?lang=rus"
            response = requests.get(url)
            data = response.json()
            fact = data["data"][0]
            await message.answer(f"Факт про кошек: {fact}",reply_markup=get_main_reply_keyboard())
            print("Факт про кошек выдан!")
        except Exception as e:
            await message.answer("Что-то пошло не так. Подождите некоторое время и попробуйте позже.")
            print(f"Не удалось получить факт о кошках: {e}")