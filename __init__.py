from threading import Thread

from telegram import main
from app import app


class FlaskThread(Thread):
    def run(self) -> None:
        app.run("0.0.0.0", port=8080)


class TelegramThread(Thread):
    def run(self) -> None:
        main()

if __name__ == '__main__':

    flask_t = FlaskThread()
    flask_t.start()
    main()
