from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = 'Your Bot api'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_info = KeyboardButton(text='Информация')
button_calc = KeyboardButton(text='Рассчитать')
kb.add(button_info)
kb.add(button_calc)

kb_calc = InlineKeyboardMarkup(resize_keyboard=True)
button_calc_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_calc_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_calc.add(button_calc_calories)
kb_calc.add(button_calc_formulas)

class UserState(StatesGroup):
    age = State()
    gender = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer(f'Привет! Я бот помогающий твоему здоровью.', reply_markup = kb)

@dp.message_handler(text=['Информация'])
async def inform(message):
    await message.answer(f'Информация о боте')


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup = kb_calc)

@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer(f'''Формула Миффлина-Сан Жеора упрощённая:

Для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5;
Для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161''')
    await call.answer()

@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await call.message.answer(f'Введите свой возраст:')
    await UserState.age.set()
    await call.answer()

@dp.message_handler(state= UserState.age)
async def set_gender(message, state):
    await state.update_data(age = message.text)
    await message.answer(f'Введите свой пол (М/Ж):')
    await UserState.gender.set()

@dp.message_handler(state= UserState.gender)
async def set_growth(message, state):
    await state.update_data(gender = message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()
    
@dp.message_handler(state= UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state= UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight = message.text)
    
    data = await state.get_data()
    
    # Используется упрощенный вариант формулы Миффлина-Сан Жеора
    if data['gender'] == 'М':
        print(data['growth'])
        calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5

    elif data['gender'] == 'Ж':
        calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 161
    else:
        await message.answer(f' Страшно! Очень страшно! Мы не знаем что это такое, если бы мы знали, что это такое, но мы не знаем, что это такое!')
    
    try:
        await message.answer(f'Ваша норма калорий: {calories}')
    except Exception as exc:
        print(f'Exception: {exc}')
        await state.finish()

@dp.message_handler()
async def all_messages(message):
    await message.answer(f'Введите команду /start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)