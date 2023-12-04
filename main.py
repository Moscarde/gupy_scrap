from modules.gupy_scraper import GupyScraper
from modules.data_handler import DataHandler
from modules.data_handler import update_google_sheets_dataset
from modules.telegram_message import TelegramMessage
from modules.telegram_bot import TelegramBot
from dotenv import load_dotenv
import os, sys
import webbrowser
import time
import subprocess


load_dotenv()
TOKEN = os.environ["TOKEN"]
MAIN_GROUP_CHAT_ID = os.environ["MAIN_GROUP_CHAT_ID"]
TEST_GROUP_CHAT_ID = os.environ["TEST_GROUP_CHAT_ID"]


def detect_environment():
    if "--dev" in sys.argv:
        print(">> DEVELOPMENT ENVIRONMENT SELECTED")
        return TEST_GROUP_CHAT_ID

    elif "--prod" in sys.argv:
        print(">> PRODUCTION ENVIRONMENT SELECTED")
        return MAIN_GROUP_CHAT_ID

    else:
        return select_environment()
    
def fast_run(chat_id):
    if "--request" in sys.argv:
        print(">> FAST RUN")
        request_data()
        process_request(chat_id)
        update_sheets_dataset()

        git_command = 'gitpush.bat'
        subprocess.call([git_command])

        print(">> WAITING 20s FOR THE PROCESS TO FINISH")
        time.sleep(10)
        url = "https://bit.ly/planilhaJuniorZone1"
        webbrowser.open(url)
        input('>> PRESS ENTER TO EXIT')
        #end app
        exit()


def select_environment():
    print("NO ENVIRONMENT SELECTED, PLEASE SELECT ONE:")
    groups_id = {1: MAIN_GROUP_CHAT_ID, 2: TEST_GROUP_CHAT_ID}

    print("ENVIRONMENTS:\n" "[1] PRODUCTION GROUP\n" "[2] DEVELOPMENT GROUP")
    option = int(input(">> SELECT ENVIRONMENT:"))

    if option in groups_id:
        chat_id = groups_id[option]
        return chat_id

    else:
        print("INVALID OPTION")
        return main()


def request_data():
    filter_labels = [
        "analista",
        "dados",
        "python",
        "data",
        "Desenvolvedor",
        "Dev",
        "Front",
        "Back",
        "Full Stack",
        "FullStack",
        "Software",
        "DevOps",
        "Business Intelligence",
        "Machine Learning",
        "Inteligência Artificial",
    ]
    scraper = GupyScraper(filter_labels)
    scraper.request_and_save()
    # main()


def process_request(chat_id):
    data_handler = DataHandler()
    filtered_vacancies_dfs = data_handler.filtered_dfs

    telegram_message = TelegramMessage(filtered_vacancies_dfs)

    send_message(
        message_content=telegram_message.header,
        message_type="text",
        chat_id=chat_id,
        disable_notification=False,
    )

    send_message(
        message_content=telegram_message.section_dados_image,
        message_type="image",
        chat_id=chat_id,
    )
    send_message(
        message_content=telegram_message.section_dados_messages,
        message_type="text",
        chat_id=chat_id,
    )

    send_message(
        message_content=telegram_message.section_dev_image,
        message_type="image",
        chat_id=chat_id,
    )
    send_message(
        message_content=telegram_message.section_dev_messages,
        message_type="text",
        chat_id=chat_id,
    )

    # if tag_data_as_submitted():
    data_handler.tag_as_submitted()
    print("TAGED!")


def send_message(message_content, message_type, chat_id, disable_notification=True):
    junior_bot = TelegramBot(TOKEN)

    if message_type == "text":
        junior_bot.send_message(chat_id, message_content, disable_notification)

    if message_type == "image":
        junior_bot.send_image(chat_id, message_content, disable_notification)


def tag_data_as_submitted():
    print("\nTAG DATA AS SUBMITTED?\n" "[1] YES\n" "[2] NO")
    tag = int(input(">> ANSWER:"))
    if tag == 1:
        return True
    else:
        return False


def send_custom_text(chat_id):
    text = input("\n>> ENTER CUSTON TEXT: ")
    converted_message = TelegramMessage.formatter_string(text)
    send_message(converted_message, "text", chat_id)
    main()


def send_image(chat_id):
    file_name = input(">> FILE NAME IN PICTURES FOLDER: ")
    content = open(f"pictures/{file_name}", "rb")
    send_message(content, "image", chat_id)


def update_sheets_dataset():
    try:
        update_google_sheets_dataset()
    except Exception as e:
        print(e)
    finally:
        print("UPDATED!")


def main():
    chat_id = detect_environment()
    fast_run(chat_id)

    options = {
        1: request_data,
        2: lambda: process_request(chat_id),
        3: lambda: send_custom_text(chat_id),
        4: lambda: send_image(chat_id),
        5: update_sheets_dataset,
    }
    print(
        "\n"
        "[1] REQUEST DATA\n"
        "[2] PROCESS AND SEND LAST REQUEST\n"
        "[3] SEND CUSTOM TEXT\n"
        "[4] SEND IMAGE\n"
        "[5] UPDATE SHEETS DATASET"
    )
    option = int(input(">> SELECT FUNCTION: "))

    if option in options:
        options[option]()
    else:
        print("INVALID OPTION")


if __name__ == "__main__":
    print(
        """
.·:''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''':·.
: :           #                                  #######                          : :
: :           # #    # #    # #  ####  #####          #   ####  #    # ######     : :
: :           # #    # ##   # # #    # #    #        #   #    # ##   # #          : :
: :           # #    # # #  # # #    # #    #       #    #    # # #  # #####      : :
: :     #     # #    # #  # # # #    # #####       #     #    # #  # # #          : :
: :     #     # #    # #   ## # #    # #   #      #      #    # #   ## #          : :
: :      #####   ####  #    # #  ####  #    #    #######  ####  #    # ######     : :
'·:...............................................................................:·'
"""
    )
    main()
