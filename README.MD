# `Libra Bot`

A small bot project, responsible for the basic CRUD operations of the library and getting the report via GET request.

___

## *Project Status*

***Completed &#10003;***
___
## Functionality
- Basic CRUD operations on books via SQLAlchemy
- Flask app, resonsible for saving and downloading book stats
- DatabaseConnector class, responsible for implementing ORM to work with DB
- TelegramBot class, responsible for client interface and commands

## Technologies and Frameworks
- Python 3.11 
- Flask 2.3.2
- SQLAlchemy 2.0.1
___

## Installation

1. Clone the repository to the local machine

    ```shell
    git clone https://github.com/Segfaul/libra_bot.git
    ```

2. Go to the repository directory

    ```shell
    cd libra_bot
    ```

3. Create and activate a virtual environment

    ```shell
    python -m venv env
    source env/bin/activate
    ```

4. Set project dependencies

    ```shell
    pip install -r requirements.txt
    ```

5. Configure telegram api_token via [telegram.py](https://github.com/Segfaul/libra_bot/blob/d22e4db68f36005ae6d6b01499cb66649bc83716/telegram.py#L323-L326)

    ```python
    tg_bot = TelegramBot("...")
    ```

6. Run the libra bot logic in the background

    ```python
    python __init.py__ &
    ```

7. In case of a problem, the program will stop automatically or you can stop execution using

    ```shell
    ps aux | grep ".py"
    kill PID
    ```
___
