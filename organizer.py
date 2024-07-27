from functions import create_event, delete_event, get_details, edit_event, events, login
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('organizer.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    '''Handle actions for event organizers.'''

    global user_id
    user_id = login()

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
            print(details)
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