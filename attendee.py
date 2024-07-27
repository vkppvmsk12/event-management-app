from functions import chat, login
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('attendee.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    login()

    '''Handle actions for event attendees.'''
    chat_id = input('\nPlease provide an event id for your event, or press enter to exit. ').strip()
    if chat_id == '':
        raise SystemExit
    print(chat(chat_id))

if __name__ == '__main__':
    main()