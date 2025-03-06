import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
import time
import datetime
import threading
from database_create import SessionLocal, Workout

bot = telebot.TeleBot('7998073894:AAFGKmuO_ZRwEmnS-GTsdRvV1Ql7pOTAxiQ', parse_mode = 'HTML')

final_plan_list = {}

wait_user = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет!')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 'Вот список того что я могу:\n/start(Запуск бота)\n/setreminder(Установить время)\n/currentplan(Показывает текущий план)\n/plan(Установить план)')

@bot.message_handler(commands=['setreminder'])
def send_reminder_ask(message):
    bot.reply_to(message, 'На какое время вы хотите поставить напоминание?')
    bot.register_next_step_handler(message, save_time)

#related to setreminder command
def save_time(message):
    global hour, minute
    time = message.text
    if re.match(r'^\d{2}:\d{2}$', time):
        clean_time = time.replace(':', '')
        hour = int((clean_time[0:2]))
        minute = int(clean_time[2:])
        if hour > 23 or minute > 59:
            bot.reply_to(message, "Некорректный формат времени. Попробуйте ввести снова.")
            bot.register_next_step_handler(message, save_time)
        else:
            print(hour, minute)
            save_time_to_db()
            bot.reply_to(message, f"Напоминание установлено на {time}!")
    else:
        bot.reply_to(message, "Некорректный формат времени. Попробуйте ввести снова.")
        bot.register_next_step_handler(message, save_time)


@bot.message_handler(commands=['currentplan'])
def show_currentplan(message):
    user_plan = get_details()
    result = ''
    for g in user_plan: ##formatting text
        result+=g
    if result:
        bot.reply_to(message, f'Вот ваш текущий план:\n{result}')
    else:
        bot.reply_to(message, 'У вас пока нет сохраненённого плана! Напишите команду /plan, чтоб сделать это.')
        
@bot.message_handler(commands=['plan'])
def set_plan(message):
    session = SessionLocal()
    session.query(Workout).delete()
    session.commit()
    session.close()
    wait_user[message.chat.id] = "waiting_for_plan"
    bot.reply_to(message, 'Введите ваш план тренировок ниже.')


#related to plan command
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    state = wait_user.get(message.chat.id, None)

    if state == "waiting_for_plan":
        plan = message.text
        save_plan_to_db(message.chat.id, plan)
        wait_user[message.chat.id] = None
        bot.reply_to(message, "Ваш план тренировок сохранён!")
    else:
        bot.reply_to(message, "Я вас не понял. Напишите /help для помощи.")

def save_time_to_db():
    session = SessionLocal()
    new_time = session.query(Workout).filter_by(id=1).one_or_none()
    new_time.hour = hour
    new_time.minute = minute
    session.commit()
    session.close()

def save_plan_to_db(chat_id, plan):
    session = SessionLocal()
    new_plan = Workout(
        details = plan,
        hour = '67890',
        minute = '67890',
        id_of_chat = chat_id
    )
    session.add(new_plan)
    session.commit()
    session.close()
    print(f'План от пользователя {chat_id} сохранён: {plan}')


def get_details():
    session = SessionLocal()
    workouts_get_all = session.query(Workout).all()
    result = []
    for workout in workouts_get_all:
        got_it = (workout.details)
        result.append(got_it)
    session.close()
    return result

def get_time():
    session = SessionLocal()
    workouts_get_all = session.query(Workout).all()
    result_time = [(workout.hour, workout.minute) for workout in workouts_get_all]
    session.close()
    return result_time


def get_id():
    session = SessionLocal()
    id_get_all = session.query(Workout).all()
    result_id = []
    for id_a in id_get_all:
        got_it = (id_a.id_of_chat)
        result_id.append(got_it)
    session.close()
    return result_id


def get_one_day():
    global final_plan_list
    text_list = get_details()
    text = ' '.join(text_list)

    final_plan_list = {}
    for line in text.split('\n'):
        day, workout = line.split(':', 1)
        final_plan_list[day.strip()] = workout.strip()


def notification():
    get_one_day()
    while True:
        now = datetime.datetime.now()
        chat_ids = get_id()
        workout_times = get_time()
        for notif_hour, notif_minute in workout_times:
            if now.weekday() == 0 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['пн'])
            if now.weekday() == 1 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['вт'])
            if now.weekday() == 2 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['ср'])
            if now.weekday() == 3 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['чт'])
            if now.weekday() == 4 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['пт'])
            if now.weekday() == 5 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                    bot.send_message(chat_id, final_plan_list['сб'])
            if now.weekday() == 6 and now.hour == notif_hour and now.minute == notif_minute:
                for chat_id in chat_ids:
                        bot.send_message(chat_id, final_plan_list['вс'])
            time.sleep(60)
        time.sleep(1)

thread = threading.Thread(target=notification)
thread.daemon = True
thread.start()


def start_polling():
    while True:
        try:
            bot.polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}. Перезапуск")
            time.sleep(15)
        

start_polling()