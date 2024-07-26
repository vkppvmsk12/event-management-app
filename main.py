from functions import create_event, delete_event, chat, get_details, edit_event, users, events
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('main.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    '''Main function to handle the user role and corresponding actions.'''

    global user_id
    user_id = login()

    role = input('Are you an event organizer or an event attendee? Answer with attendee/organizer or press enter to exit. ').lower().strip()
    if role == '':
        raise SystemExit

    while role not in ['attendee', 'organizer']:
        role = input('Please answer with attendee/organizer or press enter to exit. ').lower().strip()
        if role == '':
            raise SystemExit

    if role == 'attendee':
        handle_attendee()
    elif role == 'organizer':
        handle_organizer()

def handle_attendee():
    '''Handle actions for event attendees.'''
    chat_id = input('\nPlease provide an event id for your event, or press enter to exit. ').strip()
    if chat_id == '':
        raise SystemExit
    print(chat(chat_id))

def login():
    global username, password
    username = input('\nPlease enter your username or press enter to exit: ').strip()
    if not username:
        raise SystemExit

    while not [doc for doc in users.find({'username':username})]:
        print('Sorry, that username doesn\'t exist.')
        username = input('\nPlease enter a valid username or press enter to skip: ').strip()
        if not username:
            raise SystemExit

    password = input('\nPlease enter your password or press enter to exit: ')
    if not password:
        raise SystemExit
    
    user_info = [doc for doc in users.find({'username':username})][0]
    while password not in user_info.values():
        print('Sorry, invalid password.')
        password = input('Please enter a valid password or press enter to exit: ')
        if not password:
            raise SystemExit
    
    return str(users.find_one({'username':username, 'password':password})['_id'])

def handle_organizer():
    '''Handle actions for event organizers.'''

    choice = input('''\nDo you want to create, delete, or edit an event? 
Answer with create/edit/delete, otherwise press enter to exit. ''').strip().lower()

    if choice == 'create':
        result = create_event()
        print(result)
        if result.strip()[0] == 'E':
            id = result[result.index(':') + 2:result.index('. S')]
            print(id)
            get_details(id)

            events.update_one({'_id':ObjectId(id)},{'$set':{'organizer':user_id}})
    
    elif choice == 'edit':
        id = input('\nPlease provide id to edit event. ').strip()

        details = get_details(id)
        if details:
            raise SystemExit
        
        if user_id != events.find_one({'_id':ObjectId(id)}).get('organizer'):
            print('\nSorry, you don\'t have access to this event.')
            raise SystemExit
        
        change = input('What do you want to change about the event? ')
        print(edit_event(id, change))
        get_details(id)
    
    elif choice == 'delete':
        id = input('\nPlease provide id to delete event. ')
        details = get_details(id)
        if details:
            raise SystemExit

        if user_id != events.find_one({'_id':ObjectId(id)}).get('organizer'):
            print('\nSorry, you don\'t have access to this event.')
            raise SystemExit
        
        confirm = input('Are you sure you want to delete the event? Enter yes to delete, otherwise press enter to exit. ').strip().lower()
        if confirm == 'yes':
            delete_event(id)
            print('Event successfully deleted.')

if __name__ == '__main__':
    main()