from telebot import TeleBot, types
import requests

from database.dbapi import DatabaseConnector

commands = ["/start", "/add", "/delete", "/list", "/find", "/borrow", "/retrieve", "/stats"]


class TelegramBot:

    def keyboard(self, commands: list) -> types.InlineKeyboardMarkup:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for command in commands:
            markup.add(types.KeyboardButton(command))

        return markup

    def __init__(self, api_token: str):
        self.bot = TeleBot(api_token)
        self.db = DatabaseConnector()
        self.handlers()


    def handlers(self):

        @self.bot.message_handler(commands=['start'])
        def start(message) -> None:
            self.bot.send_message(message.chat.id, f"Welcome to the library chatbot, @{message.from_user.username}.\n"
                                              f"The following commands are available:\n\n"
                                              f"/add - add a book to the library\n"
                                              f"/delete - delete book from the library\n"
                                              f"/list - get list of all books\n"
                                              f"/find - find related book\n"
                                              f"/borrow - borrow the book\n"
                                              f"/retrieve - retrieve the book\n"
                                              f"/stats - stats about related book\n\n"
                                              f"@Libriotic_bot", reply_markup=self.keyboard(commands))

        @self.bot.message_handler(commands=['add'])
        def add_book(message) -> None:
            try:
                new_book: dict = {}
                self.bot.send_message(message.chat.id, "To add a book you will need:\n"
                                      "\t- Title\n"
                                      "\t- Author\n"
                                      "\t- Publication Year\n")
                self.bot.reply_to(message, "Input book title: ")
                self.bot.register_next_step_handler(message, reg_author, new_book, reg_book)

            except Exception as ex:
                print(repr(ex))

        def reg_author(message, new_book: dict, func_end: callable) -> None:
            try:
                new_book["title"] = message.text
                self.bot.reply_to(message, "Input Author: ")
                self.bot.register_next_step_handler(message, reg_year, new_book, func_end)

            except Exception as ex:
                print(repr(ex))

        def reg_year(message, new_book: dict, func_end: callable) -> None:
            try:
                new_book["author"] = message.text
                self.bot.reply_to(message, "Input publication year: ")
                self.bot.register_next_step_handler(message, func_end, new_book)

            except Exception as ex:
                print(repr(ex))

        def reg_book(message, new_book: dict) -> None:
            try:
                new_book["year"] = int(message.text)
                response = self.db.add(new_book["title"], new_book["author"], new_book["year"])

                if type(response) == int:
                    self.bot.send_message(message.chat.id, f"Record successfully added ({response}):\n"
                                                           f"{new_book['title'], new_book['author'], new_book['year']}", reply_markup=self.keyboard(commands))
                else:
                    self.bot.send_message(message.chat.id, "Error while adding the book", reply_markup=self.keyboard(commands))

            except ValueError:
                self.bot.send_message(message.chat.id, "Incorrect date format\n"
                                      "Try again later using command /add", reply_markup=self.keyboard(['/add']))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['delete'])
        def delete_book(message):
            try:
                new_book: dict = {}
                self.bot.send_message(message.chat.id, "Для удаления книги потребуются:\n"
                                                       "\t- Название\n"
                                                       "\t- Автор\n"
                                                       "\t- Год издания\n")
                self.bot.reply_to(message, "Введите название книги: ")
                self.bot.register_next_step_handler(message, reg_author, new_book, delete_check)

            except Exception as ex:
                print(repr(ex))

        def delete_check(message, new_book: dict) -> None:
            try:
                new_book["year"] = int(message.text)
                book_id = self.db.get_book(new_book["title"], new_book["author"])

                if type(book_id) == str:
                    self.bot.send_message(message.chat.id, "Книга с выбранным id не найдена")

                else:
                    self.bot.reply_to(message,
                                f"Найдена книга: {new_book['title'], new_book['author'], new_book['year']}. Удаляем?", reply_markup=self.keyboard(['да', 'нет']))
                    self.bot.register_next_step_handler(message, delete_result, book_id)

            except ValueError:
                self.bot.send_message(message.chat.id, "Неккоректный формат даты\n"
                                      "Попробуйте снова по команде /delete")

            except Exception as ex:
                print(repr(ex))

        def delete_result(message, book_id: int) -> None:
            try:
                if message.text.lower() == 'нет':
                    self.bot.send_message(message.chat.id, f"Запись {book_id} оставлена без изменений", reply_markup=self.keyboard(commands))

                elif message.text.lower() == 'да':
                    response = self.db.delete(book_id)

                    if type(response) == str or not response:
                        self.bot.send_message(message.chat.id, "Невозможно удалить книгу", reply_markup=self.keyboard(['/delete']))

                    elif response:

                        if response:
                            self.bot.send_message(message.chat.id, "Книга удалена", reply_markup=self.keyboard(commands))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['list'])
        def list_books(message):
            try:
                books_records: list[tuple] = self.db.list_books()
                book_list: list[dict] = []

                if len(books_records) == 0:
                    self.bot.send_message(message.chat.id, "Ваша библиотека пуста. Для начала добавьте пару книг с помощью команды /add", reply_markup=self.keyboard(['/add']))

                for book in books_records:
                    # if type(self.db.get_book(book[1], book[2])) == int:

                    if book[-1] == None:
                        book_list.append(f"{book[1]}, {book[2]}, {book[3]}")

                    else:
                        book_list.append(f"{book[1]}, {book[2]}, {book[3]} (удалена)")
                    
                if len(book_list) > 0:
                    self.bot.send_message(message.chat.id, '\n'.join(book_list), reply_markup=self.keyboard(commands))
                
                else:
                    self.bot.send_message(message.chat.id, "Ваша библиотека пуста. Для начала добавьте пару книг с помощью команды /add", reply_markup=self.keyboard(['/add']))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['find'])
        def find_book(message):
            try:
                new_book: dict = {}
                self.bot.send_message(message.chat.id, "Для поиска книги потребуются:\n"
                                                       "\t- Название\n"
                                                       "\t- Автор\n"
                                                       "\t- Год издания\n")
                self.bot.reply_to(message, "Введите название книги: ")
                self.bot.register_next_step_handler(message, reg_author, new_book, find_check)

            except Exception as ex:
                print(repr(ex))

        def find_check(message, new_book: dict) -> None:
            try:
                new_book["year"] = int(message.text)
                book_id = self.db.get_book(new_book["title"], new_book["author"])
                if type(book_id) == str:
                    self.bot.send_message(message.chat.id, "Такой книги у нас нет", reply_markup=self.keyboard(commands))

                else:
                    self.bot.reply_to(message,
                                f"Найдена книга: {new_book['title'], new_book['author'], new_book['year']}.", reply_markup=self.keyboard(commands))

            except ValueError:
                self.bot.send_message(message.chat.id, "Неккоректный формат даты\n"
                                      "Попробуйте снова по команде /find", reply_markup=self.keyboard(['/find']))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['borrow'])
        def borrow_book(message):
            try:
                new_book: dict = {}
                self.bot.send_message(message.chat.id, "Для аренды книги потребуются:\n"
                                                       "\t- Название\n"
                                                       "\t- Автор\n"
                                                       "\t- Год издания\n")
                self.bot.reply_to(message, "Введите название книги: ")
                self.bot.register_next_step_handler(message, reg_author, new_book, borrow_check)

            except Exception as ex:
                print(repr(ex))

        def borrow_check(message, new_book: dict) -> None:
            try:
                new_book["year"] = int(message.text)
                book_id = self.db.get_book(new_book["title"], new_book["author"])
                if type(book_id) == str:
                    self.bot.send_message(message.chat.id, "Книга в библиотеке не найдена.", reply_markup=self.keyboard(commands))

                else:
                    self.bot.reply_to(message,
                                f"Найдена книга: {new_book['title'], new_book['author'], new_book['year']}. Берем?", reply_markup=self.keyboard(['да', 'нет']))
                    self.bot.register_next_step_handler(message, borrow_result, book_id)

            except ValueError:
                self.bot.send_message(message.chat.id, "Неккоректный формат даты\n"
                                      "Попробуйте снова по команде /borrow", reply_markup=self.keyboard(['/borrow']))

            except Exception as ex:
                print(repr(ex))

        def borrow_result(message, book_id: int) -> None:
            try:
                if message.text.lower() == 'нет':
                    self.bot.send_message(message.chat.id, f"Запись {book_id} оставлена без изменений", reply_markup=self.keyboard(commands))

                elif message.text.lower() == 'да':
                    # print(message.from_user.id, book_id)
                    response = self.db.borrow(book_id, message.from_user.id)

                    if type(response) == str:
                        self.bot.send_message(message.chat.id, "Книгу сейчас невозможно взять", reply_markup=self.keyboard(commands))

                    elif type(response) == int:
                        self.bot.send_message(message.chat.id, "Вы взяли книгу", reply_markup=self.keyboard(commands))

                    elif type(response) == bool:

                        if not response:
                            user_borrows = self.db.get_borrow(message.from_user.id)

                            if type(user_borrows) == str:
                                self.bot.send_message(message.chat.id, "Книгу уже взял кто-то другой.", reply_markup=self.keyboard(commands))

                            else:
                                self.bot.send_message(message.chat.id, f"Вы уже брали книгу. Сначала верните её с помощью команды /retrieve.", reply_markup=self.keyboard(['/retrieve']))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['retrieve'])
        def borrow_book(message):
            try:
                users_book = self.db.get_borrow(message.from_user.id)

                if type(users_book) == str:
                    self.bot.send_message(message.chat.id, "Вы не можете вернуть книгу, так как ещё не брали 1.\nВоспользуйтесь командой /borrow", reply_markup=self.keyboard(['/borrow']))
                    raise Exception("Вы не можете вернуть книгу, так как ещё не брали 1.")

                response = self.db.retrieve(users_book)

                if type(response) == str:
                    raise Exception("Проблемы с возвратом...")

                self.bot.send_message(message.chat.id, f"Вы вернули книгу.", reply_markup=self.keyboard(commands))

            except Exception as ex:
                print(repr(ex))

        @self.bot.message_handler(commands=['stats'])
        def stats_book(message):
            try:
                new_book: dict = {}
                self.bot.send_message(message.chat.id, "Для получения данных о книге потребуются:\n"
                                                       "\t- Название\n"
                                                       "\t- Автор\n"
                                                       "\t- Год издания\n")
                self.bot.reply_to(message, "Введите название книги: ")
                self.bot.register_next_step_handler(message, reg_author, new_book, stats_result)

            except Exception as ex:
                print(repr(ex))

        def stats_result(message, new_book: dict) -> None:
            try:
                new_book["year"] = int(message.text)
                book_id: int or str = self.db.get_book(new_book["title"], new_book["author"])

                if type(book_id) == str:
                    self.bot.send_message(message.chat.id, "Нет такой книги\n"
                                                           "Попробуйте ещё раз /stats", reply_markup=self.keyboard(['/stats']))
                    raise Exception("Книга не найдена")

                else:
                    req = requests.post("http://127.0.0.1:8080/borrow/stats", json={"book_id": book_id})
                    url = f"http://127.0.0.1:8080/download/{book_id}"
                    self.bot.send_message(message.chat.id, f"Статистика доступна по адресу {url}", reply_markup=self.keyboard(commands))

            except ValueError:
                self.bot.send_message(message.chat.id, "Неккоректный формат даты\n"
                                      "Попробуйте снова по команде /stats", reply_markup=self.keyboard(['/stats']))

            except Exception as ex:
                print(repr(ex))

    def start_polling(self, none_stop: bool = True):
        self.bot.polling(none_stop=none_stop)


def main() -> None:
    tg_bot = TelegramBot("ssd")
    tg_bot.start_polling()

