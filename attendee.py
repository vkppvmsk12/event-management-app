from functions import chat, login
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('attendee.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    '''Handle actions for event attendees.'''
    
    user_id = login()
    username = users.find_one({'_id':user_id}).get('username')
    attendee_events = []

    for event in events.find():
        if username in event.get(attendees, []):
            attendee_events.append(event.get('event name'))
    
    if not attendee_events:
        print('No events planned for you.')
        raise SystemExit 

    print('Here are the list of events:')
    for number, event_name in enumerate(attendee_events, 1):
        print(number, event_name)

    while True:
        try:
            event_nr = int(input('Please enter the number of the event that you want to attend or press enter to exit: ').strip()
            if not event_nr:
                raise SystemExit 
        except ValueError:
            print('Please enter a valid event number.')
            continue

        if event_nr > len(attendee_events):
            print('Please enter a valid event number.')
            continue

    chat_id = str(events.find_one({'event name':attendee_events[event_nr - 1]}).get('_id'))
    print(chat(chat_id))

if __name__ == '__main__':
    main()
