from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from app.services.weather import get_temperature_by_city
from app.services.calories import calculate_calories
from app.services.water import water_calculate
from app.services.openfood_calories import get_product_calories
from app.services.workouts import calculate_workout
from config_reader import config
from app.services.plots import build_progress_plot
from aiogram.types import BufferedInputFile
from app.services.recommendations import LOW_CAL_FOODS, WORKOUT_RECS
from app.middlewares.profile_required import ProfileRequiredMiddleware

router = Router()
router.message.middleware(ProfileRequiredMiddleware())


class Form(StatesGroup):
    name = State()
    weight = State()
    age = State()
    height = State()
    sex = State()
    activity_time = State()
    city = State()
    calories_goal = State()
    water_input = State()

class FoodLog(StatesGroup):
    grams = State()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет 👋\n"
        "Используй /set_profile для заполнения профиля\n"
        "Используй /help, чтобы после заполнения профиля узнать команды"
    )


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Форма отменена")

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "/set_profile — заполнить профиль\n"
        "/log_water — записать воду\n"
        "/log_food — записать калории\n"
        "/recommend - получить рекомендации по еде и тренировкам "
        "/cancel — отменить действие"
    )

@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await state.clear()

    await message.answer("Как вас зовут?")
    await state.set_state(Form.name)


@router.message(Form.name, F.text)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите вес (кг):")
    await state.set_state(Form.weight)


@router.message(Form.weight, F.text)
async def weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.answer("Введите возраст:")
    await state.set_state(Form.age)


@router.message(Form.age, F.text)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите рост (см):")
    await state.set_state(Form.height)


@router.message(Form.height, F.text)
async def height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.answer("Введите пол (мужчина/женщина):")
    await state.set_state(Form.sex)


@router.message(Form.sex, F.text)
async def sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await message.answer("Сколько минут активности в день?")
    await state.set_state(Form.activity_time)


@router.message(Form.activity_time, F.text)
async def activity(message: Message, state: FSMContext):
    await state.update_data(activity_time=message.text)
    await message.answer("В каком городе вы находитесь?")
    await state.set_state(Form.city)


@router.message(Form.city, F.text)
async def city(message: Message, state: FSMContext):
    temperature = await get_temperature_by_city(
        message.text,
        config.openweather_api_key
    )

    if temperature is None:
        await message.answer("Город не найден. Попробуйте снова.")
        return

    await state.update_data(city=message.text, temperature=temperature)

    await message.answer(
        f"Сейчас в городе {message.text} примерно {temperature}°C\n\n"
        "Введите цель по калориям или напишите /skip"
    )
    await state.set_state(Form.calories_goal)


@router.message(Form.calories_goal, Command("skip"))
async def skip_calories(message: Message, state: FSMContext):
    data = await state.get_data()
    calories = calculate_calories(data)
    await finish_profile(message, state, calories)


@router.message(Form.calories_goal, F.text)
async def calories_manual(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число или /skip")
        return

    await finish_profile(message, state, int(message.text))


async def finish_profile(message: Message, state: FSMContext, calories: int):
    data = await state.get_data()
    water_norma = water_calculate(data)

    await state.update_data(
        calories_goal=calories,
        water_norma=water_norma,
        water_today=0,
        calories_today=0,
        burned_calories=0
    )
    await state.update_data(
        water_history=[],
        calories_history=[],
        burned_history=[]
    )


    await message.answer(
        "✅ Профиль сохранён\n\n"
        f"Калории: {calories} ккал\n"
        f"Норма воды: {water_norma} мл\n\n"
        "Для записи воды:\n"
        "/log_water\n"
        "Для записи калорий:\n"
        "/log_food название_еды\n"
        "Для записи тренировок:\n"
        "/log_workout название_тренировки время_минуты\n"
        "Для информации о прогрессе за день:\n"
        "/check_progress\n"
        "Для получения рекомендаций по еде и тренировкам:\n"
        "/recommend\n"  
        "График траты калорий:\n"
        "/calories_graph\n"    
        "График траты воды:\n"
        "/water_graph\n"      
    )

    await state.set_state(None)



@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    await message.answer("Сколько воды вы выпили (мл)?")
    await state.set_state(Form.water_input)

@router.message(Form.water_input, F.text)
async def water_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число")
        return

    amount = int(message.text)
    data = await state.get_data()

    water_today = data["water_today"] + amount
    water_norma = data["water_norma"]

    await state.update_data(water_today=water_today)
    water_history = data.get("water_history", [])
    water_history.append(water_today)
    await state.update_data(water_history=water_history)

    left = max(water_norma - water_today, 0)

    if left > 0:
        await message.answer(
            f"Выпито сегодня: {water_today} мл\n"
            f"Осталось: {left} мл"
        )
    else:
        await message.answer(
            f"🎉 Поздравляем!\n"
            f"Вы выпили {water_today} мл и выполнили норму воды 💪"
        )

    await state.set_state(None)

@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        await message.answer("Формат: /log_food" \
        " продукт")
        return

    calories_100g = await get_product_calories(args[1])
    if calories_100g is None:
        await message.answer("Продукт не найден")
        return

    await state.update_data(
        food_name=args[1],
        calories_100g=calories_100g
    )

    await message.answer(
        f"{args[1]} — {calories_100g} ккал / 100 г\n"
        "Сколько грамм вы съели?"
    )

    await state.set_state(FoodLog.grams)

@router.message(FoodLog.grams, F.text)
async def process_food_grams(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число грамм")
        return

    grams = int(message.text)
    data = await state.get_data()

    calories = round(data["calories_100g"] * grams / 100, 1)
    calories_today = data.get("calories_today", 0) + calories

    await state.update_data(calories_today=calories_today)

    await message.answer(
        f"{data['food_name']}\n"
        f"Вес: {grams} г\n"
        f"Калории: {calories} ккал\n\n"
        f"Всего сегодня: {calories_today} ккал"
    )
    calories_history = data.get("calories_history", [])
    calories_history.append(calories_today)
    await state.update_data(calories_history=calories_history)

    await state.set_state(None)

@router.message(Command('log_workout'))
async def log_workout(message: Message, state: FSMContext):
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Формат: /log_workout workoutName time")
        return

    data = await state.get_data()
    workout, minutes = args[1], args[2]

    if not minutes.isdigit():
        await message.answer("Время должно быть числом (в минутах)")
        return

    data = await state.get_data()

    result = calculate_workout(
        workout=workout,
        minutes=int(minutes),
        weight=float(data["weight"])
    )

    if result is None:
        await message.answer(
            "Неизвестный тип тренировки.\n"
            "Примеры: бег, ходьба, велосипед, силовая"
        )
        return

    calories, water = result

    await message.answer(
        f"{workout.capitalize()} {minutes} минут\n"
        f"Сожжено: {calories} ккал\n"
        f"Дополнительно: выпейте {water} мл воды"
    )
    burned_today = data.get("burned_calories", 0) + calories
    burned_history = data.get("burned_history", [])
    burned_history.append(burned_today)
    await state.update_data(burned_history=burned_history, burned_calories=burned_today)


@router.message(Command("check_progress"))
async def check_progress(message: Message, state: FSMContext):
    data = await state.get_data()

    water_today = data.get("water_today", 0)
    water_norma = data["water_norma"]

    calories_today = data.get("calories_today", 0)
    calories_goal = data["calories_goal"]

    burned = data.get("burned_calories", 0)
    balance = round(calories_today - burned,1)

    await message.answer(
        "Прогресс за день:\n\n"
        "Вода:\n"
        f"- Выпито: {water_today} мл из {water_norma} мл\n"
        f"- Осталось: {max(water_norma - water_today, 0)} мл\n\n"
        "Калории:\n"
        f"- Потреблено: {calories_today} ккал из {calories_goal} ккал\n"
        f"- Сожжено: {burned} ккал\n"
        f"- Баланс: {balance} ккал"
    )



@router.message(Command("water_graph"))
async def water_graph(message: Message, state: FSMContext):
    data = await state.get_data()

    image = build_progress_plot(
        values=data["water_history"],
        goal=data["water_norma"],
        title="Прогресс по воде",
        ylabel="мл"
    )

    photo = BufferedInputFile(
        image.getvalue(),
        filename="water.png"
    )

    await message.answer_photo(photo)


@router.message(Command("calories_graph"))
async def calories_graph(message: Message, state: FSMContext):
    data = await state.get_data()

    history = data.get("calories_history", [])
    if not history:
        await message.answer("Нет данных по калориям")
        return

    buf = build_progress_plot(
        values=history,
        goal=data["calories_goal"],
        title="Потребление калорий",
        ylabel="ккал"
    )

    photo = BufferedInputFile(
        buf.getvalue(),
        filename="calories.png"
    )

    await message.answer_photo(photo)

@router.message(Command("recommend"))
async def recommend(message: Message, state: FSMContext):
    data = await state.get_data()

    consumed = data.get("calories_today", 0)
    burned = data.get("burned_calories", 0)
    goal = data["calories_goal"]

    balance = consumed - burned

    left = round(goal - balance,1)

    if left > 300:
        food, kcal = min(LOW_CAL_FOODS.items(), key=lambda x: x[1])
        await message.answer(
            "Рекомендация по еде:\n"
            f"Можно съесть: {food} (~{kcal} ккал на 100 г)\n"
            f"Осталось до цели: {left} ккал"
        )

    elif 0 < left <= 300:
        await message.answer(
            "Вы почти достигли дневной цели по калориям.\n"
            "Лучше выбрать лёгкий перекус или воду."
        )

    else:
        workout, burn = min(WORKOUT_RECS.items(), key=lambda x: x[1])
        minutes = abs(left) // burn + 5

        await message.answer(
            "Калорий перебрано.\n"
            f"Рекомендую: {workout} {minutes} минут\n"
            f"Это сожжёт ~{minutes * burn} ккал"
        )

