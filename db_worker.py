import sqlite3

import info

con = sqlite3.connect("rhema.db", check_same_thread=False)
cursor = con.cursor()

query_bd_create = [
    """CREATE TABLE IF NOT EXISTS books
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    title TEXT, 
                    theme TEXT,
                    reviews TEXT,
                    author TEXT,
                    link_img BLOM)
                """,
    """CREATE TABLE IF NOT EXISTS cells
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    city TEXT, 
                    adres TEXT, 
                    name_lider TEXT,
                    description TEXT,
                    telephone TEXT,
                    link_tg_lider TEXT,
                    age_criteria INT,
                    family TEXT,
                    link_img BLOM,
                    gender TEXT)
                """,
    """CREATE TABLE IF NOT EXISTS ministry
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    title TEXT, 
                    link_img BLOM,
                    text TEXT,
                    contact TEXT)
                """,
    """CREATE TABLE IF NOT EXISTS leaders
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    tg_id INTEGER, 
                    name TEXT,
                    surname TEXT,
                    link_tg TEXT)
                """,
    """CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                    tg_id INTEGER, 
                    name TEXT,
                    surname TEXT)
                """

]


def create_bd():
    for query in query_bd_create:
        cursor.execute(query)
    fill_books()
    fill_cells()
    fiil_ministry()


def get_info_cells_to_age(age_criteria):
    info_cells = cursor.execute("SELECT * FROM cells WHERE age_criteria = (?)", (age_criteria,))
    print(info_cells)


#Проверяем есть ли человек в базе, если его нет, возвращаем True, если есть False
def check_user(user_id):
    info = cursor.execute('SELECT * FROM users WHERE tg_id = (?)', (int(user_id),))
    return info.fetchall() is None


#проверка на наличие человека с id_tg в базе данных для избежания повторных записей
def set_info_for_user(user_dict):
    if check_user(user_dict.id):
        return 'Информация уже есть в базе'

    cursor.execute('INSERT INTO users (tg_id, name, surname) VALUES (?,?,?)',
                   (user_dict.id, user_dict.first_name, user_dict.last_name))
    con.commit()


def check_table_empty(sql_table=''):
    try:
        info = cursor.execute(f'SELECT * FROM {sql_table}')
        info = info.fetchall()
        print(f"Количество записей в таблице {sql_table}:", len(info))
        return len(info) <= 0
    except:
        print('Неверное имя таблицы:', sql_table)
        return False


def get_category_books():
    categorys = []
    for row in cursor.execute('SELECT theme FROM books').fetchall():
        categorys.append(row[0])
    return set(categorys)


def get_book_by_title(title: str):
    query = '''SELECT title, theme, reviews, author, link_img
    FROM books
    WHERE title = (?)'''
    rows = cursor.execute(query, (title,)).fetchall()
    info_book = {
        'title': rows[0][0],
        'theme': rows[0][1],
        'reviews': rows[0][2],
        'author': rows[0][3],
        'link_img': rows[0][4]
    }
    return info_book


def get_books():
    categorys = []
    for row in cursor.execute('SELECT title FROM books').fetchall():
        categorys.append(row[0])
    return set(categorys)


def get_books_by_category(category: str):
    books = []
    for row in cursor.execute('SELECT title FROM books WHERE theme = (?)', (category,)).fetchall():
        books.append(row[0])
    cells_age = set(books)
    return cells_age


def fill_books():
    if check_table_empty('books'):
        dict_info = info.dibrary_dict
        for key in dict_info:
            cursor.execute('INSERT INTO books (title, theme, reviews, link_img, author) VALUES (?,?,?,?,?)',
                           (dict_info[key]["название"], dict_info[key]["тема"],
                            dict_info[key]["рецензии"], dict_info[key]["картинка"], dict_info[key]['автор']))
        con.commit()


def fiil_ministry():
    if check_table_empty('ministry'):
        dict_info = info.ministry_dict

        for key in dict_info:
            cursor.execute('INSERT INTO ministry (title, link_img, text, contact) VALUES (?,?,?,?)',
                           (key, dict_info[key]['картинка'], dict_info[key]['текст'], dict_info[key]['контакт']))
    con.commit()


def fill_leaders():
    pass
    #А нужны ли leaders?
    # if check_table_empty('leaders'):
    #     leaders_ls = info.leaders
    #     cursor.execute('INSERT INTO leaders (tg_id, name, surname,link_tg) VALUES (?,?,?,?)', leaders_ls)
    #     con.commit()


def fill_cells():
    if check_table_empty('cells'):
        contact_list = info.cells
        for key in contact_list:
            cursor.execute('''INSERT INTO cells (city, adres, name_lider, description, telephone, link_tg_lider, 
                age_criteria, family,link_img, gender) VALUES (?,?,?,?,?,?,?,?,?,?)''',
                           (contact_list[key]['город'], contact_list[key]['адрес'], contact_list[key]['лидер'],
                            contact_list[key]['описание'], contact_list[key]['телефон'],contact_list[key]['тг_ссылка'],
                            contact_list[key]['возраст'], contact_list[key]['семья'], contact_list[key]['картинка'],
                            contact_list[key]['пол']))
        con.commit()


def get_cells_age_whera_city(city):
    cells_age = []
    for row in cursor.execute('SELECT age_criteria FROM cells WHERE city = (?)', (city,)).fetchall():
        cells_age.append(row[0])
    cells_age = set(cells_age)
    return cells_age


def get_cells_citys():
    cells_city = []
    rows = cursor.execute('SELECT city FROM cells')
    for row in cursor.execute('SELECT city FROM cells').fetchall():
        cells_city.append(row[0])
    return set(cells_city)


def get_single_city():
    query = f'''SELECT city, COUNT(*) as count
FROM cells
GROUP BY city'''
    cursor.execute(query)
    list_sigle_city = []
    info = cursor.fetchall()
    for element in info:
        if element[1] == 1:
            list_sigle_city.append(element[0])
    return list_sigle_city


def get_age_cells():
    cells_age = []
    for row in cursor.execute('SELECT age_criteria FROM cells').fetchall():
        cells_age.append(row[0])
    return set(cells_age)


def get_adress_to_city(city):
    cursor.execute("SELECT adres FROM cells WHERE city = (?)", (city,))
    return cursor.fetchall()[0]


def get_all_adress():
    cursor.execute("SELECT adres FROM cells", )
    return cursor.fetchall()[0]


def get_all_age():
    cursor.execute("SELECT age_criteria FROM cells", )
    return cursor.fetchall()[0]


def get_finale_info_cells_single(adress, city):
    query = '''SELECT name_lider, telephone, link_tg_lider, description, link_img, adres
    FROM cells
    WHERE adres = (?) and city = (?)'''
    rows = cursor.execute(query, (adress, city)).fetchall()
    info_cells = {
        'name': rows[0][0],
        'telephone': rows[0][1],
        'link_tg': rows[0][2],
        'description': rows[0][3],
        'link_img': rows[0][4],
        'adress': rows[0][5]
    }
    return info_cells


def get_finale_info_cells(adress, city, age):
    query = '''SELECT name_lider, telephone, link_tg_lider, description, link_img, adres
    FROM cells
    WHERE adres = (?) and city = (?) and age_criteria = (?)'''
    rows = cursor.execute(query, (adress, city, age)).fetchall()

    image_path = 'res/worship.jpg'

    info_cells = {
        'name': rows[0][0],
        'telephone': rows[0][1],
        'link_tg': rows[0][2],
        'description': rows[0][3],
        'link_img': rows[0][4],
        'adress': rows[0][5]
    }
    return info_cells

def get_finale_info_cells_whith_gender(adress, city, age, gender):
    query = '''SELECT name_lider, telephone, link_tg_lider, description, link_img, adres
    FROM cells
    WHERE adres = (?) and city = (?) and age_criteria = (?) and gender = (?)'''
    rows = cursor.execute(query, (adress, city, age, gender)).fetchall()

    image_path = 'res/worship.jpg'

    info_cells = {
        'name': rows[0][0],
        'telephone': rows[0][1],
        'link_tg': rows[0][2],
        'description': rows[0][3],
        'link_img': rows[0][4],
        'adress': rows[0][5]
    }
    return info_cells


def get_adress_to_age_gender(age, city, gender):
    cells_adress = []
    query = '''SELECT adres FROM cells WHERE age_criteria = (?) and city = (?) and gender = (?)'''
    rows = cursor.execute(query, (age, city, gender))
    for row in rows:
        cells_adress.append(row[0])
    return cells_adress

def get_adress_to_age(age, city):
    cells_adress = []
    query = '''SELECT adres FROM cells WHERE age_criteria = (?) and city = (?)'''
    rows = cursor.execute(query, (age, city))
    for row in rows:
        cells_adress.append(row[0])
    return cells_adress

def get_ministry():
    ministy_list = []
    for row in cursor.execute('SELECT title FROM ministry').fetchall():
        ministy_list.append(row[0])
    return set(ministy_list)


def get_ministry_by_title(title: str):
    query = '''SELECT title, text, contact, link_img
    FROM ministry
    WHERE title = (?)'''
    rows = cursor.execute(query, (title,)).fetchall()
    info_ministry = {
        'title': rows[0][0],
        'text': rows[0][1],
        'contact': rows[0][2],
        'link_img': rows[0][3]
    }
    return info_ministry


def get_gender_to_age(age, city):
    cells_gender = []
    query = '''SELECT gender FROM cells WHERE age_criteria = (?) and city = (?)'''
    rows = cursor.execute(query, (age, city))
    for row in rows:
        row = row[0].split()
        cells_gender += row
    list_gender = list(set(cells_gender))
    return list_gender