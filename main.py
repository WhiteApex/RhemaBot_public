from telebot import types, TeleBot
import db_worker
import config
import traceback


token = config.token
theme_lits = ['Библиотека', 'Расписание', 'Ячейки-Домашние группы', 'Хочу служить!']
bot = TeleBot(token)


#Функция добавляющая кнопку "На Главную"
def addBackButton(keybord: types.ReplyKeyboardMarkup):
    backButton = types.KeyboardButton('На Главную')
    keybord.add(backButton)


#Функция создающая гиперссылку
def get_link_text(text, link):
    new_link = '"' + link + '"'
    return f'<a href={new_link}>{text}</a>'


#Функция удаления последних сообщений
def delete(m: types.Message, count=0):
    try:
        for i in range(count):
            bot.delete_message(chat_id=m.chat.id, message_id=m.message_id - i)
    except:
        print('Нельзя удалить сообщение!')


#Начальная функция, Готова
@bot.message_handler(commands=['start',])
@bot.message_handler(func=lambda message: message.text == 'На Главную' or message.text == ' ')
def start(message: types.Message):
    #Записываем информацию о пользователе в таблицу users
    db_worker.set_info_for_user(message.from_user)

    # Создание клавиатуры с двумя кнопками
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Библиотека')
    button2 = types.KeyboardButton('Расписание')
    button3 = types.KeyboardButton('Ячейки-Домашние группы')
    button4 = types.KeyboardButton('Хочу служить!')

    keyboard.add(button1, button2, button3, button4)

    bot.send_message(message.chat.id,
                     'Привет, ты попал в бот молодежки Rhema! Что тебя интересует?', reply_markup=keyboard)
    delete(message)


#Функция выдает айди фото для хранения в бд. Айди заносится вручную. Подумать, как можно автоматизировать
@bot.message_handler(content_types=['photo'])
def take_photo(message: types.Message):
    # print('message.photo =', message.photo)
    # fileID = message.photo[-1].file_id
    # print('fileID =', fileID)
    # file_info = bot.get_file(fileID)
    # print('file.file_path =', file_info.file_path)
    if message.from_user.id in config.admin_id:
        id_file = message.photo[-1].file_id
        text = message.text
        with open('info_photo.txt', 'w') as f:
            f.write(f'{id_file} - {text}\n')

        bot.send_message(message.chat.id, text=f'id этого фото:\n{id_file}')
    else:
        pass


#Выводит информацию о ячейках, Готова
#функция начальной обработки ветки "домашки"

#Начальная функция для обработки ветки Домашки, Готова
@bot.message_handler(commands=['cells',])
@bot.message_handler(func=lambda message: message.text == 'Ячейки-Домашние группы')
def cells_1_city(message: types.Message):
    #Получаем список городов
    citys = db_worker.get_cells_citys()
    keybord = types.ReplyKeyboardMarkup()

    for city in citys:
        city = city
        keybord.add(types.KeyboardButton(text=city))

    # Создание клавиатуры с двумя кнопками
    addBackButton(keybord)

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id,
                     'Привет! Очень рады, что ты интересуешься домашними группами! \nА из какого ты города?',
                     reply_markup=keybord)
    delete(message)


#Второй этап ячеек, проверка возраст, города с 1 домашкой сразу отправляются на следующий этап, Готова
@bot.message_handler(func=lambda message: message.text in db_worker.get_cells_citys())
def cells_2_age(message: types.Message):
    delete(message)
    #Проверка на то, что в выбранном городе 1 домашняя группа далее ДГ
    if message.text in db_worker.get_single_city():
        #формируем список адресов для одиночек
        adress_list = db_worker.get_adress_to_city(message.text)

        keybord = types.ReplyKeyboardMarkup()
        for adress in adress_list:
            btn = types.KeyboardButton(text=adress)
            keybord.add(btn)
        addBackButton(keybord)

        #Просим выбрать адрес, игнорируя проверку возраста - идем к функции cells_4_contact
        delete(message)
        msg = bot.send_message(chat_id=message.chat.id, text='Выбери удобный адрес:', reply_markup=keybord)
        bot.register_next_step_handler(msg, cells_4_contact, city=message.text)
        return

    #Если в городе несколько групп просим человека ввести возраст
    age_list = db_worker.get_cells_age_whera_city(message.text)

    keybord = types.ReplyKeyboardMarkup()
    for age in age_list:
        btn = types.KeyboardButton(text=age)
        keybord.add(btn)
    addBackButton(keybord)
    msg = bot.send_message(chat_id=message.chat.id, text='А сколько тебе лет:', reply_markup=keybord)
    bot.register_next_step_handler(msg, cells_3_adress, city=message.text)

    delete(message)


# Обработчик нажатия на кнопку по возрасту, Готова
@bot.message_handler(func=lambda message: message.text in db_worker.get_age_cells())
def cells_3_adress(message: types.Message, **kwargs):

    if message.text == '13 - 18':
        gender_list = db_worker.get_gender_to_age(message.text, kwargs['city'])
        keybord = types.ReplyKeyboardMarkup()
        for adress in gender_list:
            btn = types.KeyboardButton(text=adress)
            keybord.add(btn)
        addBackButton(keybord)

        delete(message)
        msg = bot.send_message(chat_id=message.chat.id, text='Кто ты:', reply_markup=keybord)
        bot.register_next_step_handler(msg, cells_3_1_adress, city=kwargs['city'], age=message.text, gender= message.text)
        return

    #Формируем список адресов
    adress_list = db_worker.get_adress_to_age(message.text, kwargs['city'])

    keybord = types.ReplyKeyboardMarkup()
    for adress in adress_list:
        btn = types.KeyboardButton(text=adress)
        keybord.add(btn)
    addBackButton(keybord)

    #Отправляем в функцию cells_4_contact
    msg = bot.send_message(chat_id=message.chat.id, text='Выбери удобный адрес:', reply_markup=keybord)
    bot.register_next_step_handler(msg, cells_4_contact, city=kwargs['city'], age=message.text)
    delete(message)



def cells_3_1_adress(message: types.Message, **kwargs):
    adress_list = db_worker.get_adress_to_age_gender(kwargs['age'], kwargs['city'], message.text)

    keybord = types.ReplyKeyboardMarkup()
    for adress in adress_list:
        btn = types.KeyboardButton(text=adress)
        keybord.add(btn)
    addBackButton(keybord)

    # Отправляем в функцию cells_4_contact
    msg = bot.send_message(chat_id=message.chat.id, text='Выбери удобный адрес:', reply_markup=keybord)
    bot.register_next_step_handler(msg, cells_4_contact, city=kwargs['city'], age=kwargs['age'], gender=message.text)
    delete(message)

#Финальная функция ветки Домашки, выдает полноценную информациб с фото, Готова
def cells_4_contact(message: types.Message, **kwargs):
    delete(message)

    #((message.text not in db_worker.get_all_adress() and message.text not in db_worker.get_all_age()) or
    if message.text == 'На Главную':
        delete(message)
        #bot.send_message(message.chat.id, text='Вы ввели некоректную информацию!')
        start(message)
        return

    #Проверяем какой тип домашки к нам пришел - из города с 1 ячейкой или несколькими
    #Основная разница в sql запросах, которые мы делаем к базе данных
    if len(kwargs) == 1:
        #Алгоритм для города с 1 ячейкой
        info = db_worker.get_finale_info_cells_single(message.text, kwargs['city'])
    elif len(kwargs) == 2:
        # Алгоритм для города с более 1 ячейки
        info = db_worker.get_finale_info_cells(message.text, kwargs['city'], kwargs['age'])
    elif len(kwargs) == 3:
        info = db_worker.get_finale_info_cells_whith_gender(message.text, kwargs['city'], kwargs['age'], kwargs['gender'])
    else:
        return
    #Подготавливаем все необходимое для сообщения
    keybord = types.ReplyKeyboardMarkup()
    addBackButton(keybord)
    link = f'Ты можешь написать лидеру прямо сейчас: {info["link_tg"]}'
    text = f'''Лидера домашки зовут: {info["name"]}
    \nС ним можно связаться по номеру: {info["telephone"]}
    \nА проживает он по адресу: {info["adress"]}\n{link}'''
    bot.send_photo(message.chat.id, photo=info['link_img'], caption=text, reply_markup=keybord)


#Бот показывает расписание собраний пользователю, подумать насколько нужна?, Готова
@bot.message_handler(func=lambda message: message.text == 'Расписание')
def timelane(message):
    # Создание клавиатуры с двумя кнопками
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Написать')
    button2 = types.KeyboardButton('Нет, ещё не был')
    #keyboard.add(button1, button2)
    addBackButton(keyboard)


    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id,
                     'Привет! У нас есть Воскресное Богослужение в 9:30, 11:00 и 12:30. \nТакже есть молодежное служение, которое проходит в 18:00 каждую субботу! \n А ешё есть Домашние группы и многое другое!',
                     reply_markup=keyboard)
    try:
        delete(message)
    except:
        print('Не удалось удалить сообщение!')


#Можно для каждого пользователя сделать "Список его книг" для ускоренного поиска <<<---- Крутая идея. но.Как?
#Решение в SQL мне кажется
#Бот просит человека выбрать категорию книг, Готова
@bot.message_handler(commands=['books',])
@bot.message_handler(func=lambda message: message.text == 'Библиотека')
def library_1_chouse_category(message):

    categorys = db_worker.get_category_books()

    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    for category in categorys:
        keyboard.add(types.KeyboardButton(category))

    addBackButton(keyboard)

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id,
                     'По какой теме ты бы хотел выбрать книгу:',
                     reply_markup=keyboard)
    delete(message)


#Предлагаем названия книг из выбранной категории, Готова
@bot.message_handler(func=lambda message: message.text in db_worker.get_category_books())
def library_2_chouse_books(message: types.Message):
    books = db_worker.get_books_by_category(str(message.text))

    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    for book in books:
        keyboard.add(types.KeyboardButton(book))

    addBackButton(keyboard)

    # Отправка сообщения с клавиатурой
    bot.send_message(message.chat.id,
                     'Выбери книгу:',
                     reply_markup=keyboard)
    delete(message)

#Показываем картинку с книгой, надо добавить возможность "Бронировать", Связываться с библиотекарем, а также прикреплять описание книги
@bot.message_handler(func=lambda message: message.text in db_worker.get_books())
def library_3_get_book(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup()

    button_add = types.KeyboardButton(text='Забронировать')

    keyboard.add(button_add)
    addBackButton(keyboard)

    book = db_worker.get_book_by_title(title=message.text)

    msg = bot.send_photo(message.chat.id, photo=book['link_img'], reply_markup=keyboard)
    bot.register_next_step_handler(msg, block_book, dict_book=book)
    delete(message)

    delete(message)


#Начало ветки со служением, где человеку предлагают выбрать название служения
@bot.message_handler(commands=['ministry',])
@bot.message_handler(func=lambda message: message.text == 'Хочу служить!')
def start_ministry(message: types.Message):
    # Создание клавиатуры с кнопками служений
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    ministry = db_worker.get_ministry()
    for key in ministry:
        key = str(key)
        bt = types.KeyboardButton(text=key)
        keyboard.add(bt)

    addBackButton(keyboard)

    bot.send_message(message.chat.id,
                     'О каком служении ты бы хотел узнать больше?',
                     reply_markup=keyboard)
    delete(message)


#Показываем полную информацию о служении по названию
@bot.message_handler(func=lambda message: message.text in db_worker.get_ministry())
def get_ministry(message: types.Message):

    info = db_worker.get_ministry_by_title(str(message.text))

    img = info['link_img']
    contact = info['contact']
    text = info['text']
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    addBackButton(keyboard)

    bot.send_photo(message.chat.id, photo=img, caption=text, reply_markup=keyboard)

    delete(message)


@bot.message_handler(commands=['echo'])
def block_book(message: types.Message, **kwargs):

    if message.text == 'На Главную':
        delete(message)
        start(message)
        return

    book = kwargs['dict_book']
    librarian_chat_id = config.id_librian_chat


    keybord = types.ReplyKeyboardMarkup()
    addBackButton(keybord)
    text = f'Хочет взять книгу:{book["title"]} \nКто хочет:@{message.from_user.username}'
    bot.send_photo(librarian_chat_id,photo=book['link_img'], caption=text)

    bot.send_message(message.chat.id, 'Информация о вашем бронировании передана библиотекарю, можете связаться с ним, написав в личные сообщения:' + config.link_librian, reply_markup=keybord)


if __name__ == '__main__':

    try:
        db_worker.create_bd()
    except:
        print('Проблемы с БД.')

    while True:
        try:

            bot.polling(non_stop=True, interval=0, skip_pending=True)
        except:
            print('Ошибка в запуске бота')
            print(traceback.format_exc())