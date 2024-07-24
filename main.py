from functions import create_event, delete_event, chat, get_details, edit_event, events
from bson.objectid import ObjectId

def main():
    # Main function to handle the user role and corresponding actions.
    role = input('Are you an event organizer or an event attendee? Answer with attendee/organizer or press enter to exit. ')
    if role.strip() == '':
        raise SystemExit

    while role.lower() not in ['attendee', 'organizer']:
        role = input('Please answer with attendee/organizer or press enter to exit. ')
        if role.strip() == '':
            raise SystemExit

    if role.lower() == 'attendee':
        handle_attendee()
    elif role.lower() == 'organizer':
        handle_organizer()

def handle_attendee():
    # Handle actions for event attendees.
    chat_id = input('\nPlease provide an event id for your event, or press enter to exit. ')
    if chat_id.strip() == '':
        raise SystemExit

    print(chat(chat_id))

def handle_organizer():
    # Handle actions for event organizers.
    choice = input('''\nDo you want to create, delete, or edit an event? 
Answer with create/edit/delete, otherwise press enter to exit. ''').strip().lower()

    if choice == 'create':
        result = create_event()
        if result:
            print(result)
            if result[0] == 'E':
                get_details(result[result.index(':') + 2:result.index('. S')])
    
    elif choice == 'edit':
        id = input('\nPlease provide id to edit event. ')
        if get_details(id):
            print('Sorry, id not found.')
            raise SystemExit
        
        password = input('Please provide the password for the event that you want to edit or press enter to exit: ')
        if not password.strip():
            raise SystemExit
    
        while [doc for doc in events.find({'_id':ObjectId(id)})][0].get('password') != password:
            print('Sorry, wrong password.')
            password = input('Please provide the correct password or press enter to exit: ')
            if not password.strip():
                raise SystemExit

        print(details := get_details(id))
        if details:
            raise SystemExit
        
        change = input('What do you want to change about the event? ')
        print(edit_event(id, change))
        get_details(id)
    
    elif choice == 'delete':
        id = input('\nPlease provide id to delete event. ')
        if get_details(id):
            print('Sorry, id not found.')
            raise SystemExit
        
        password = input('\nPlease provide the password for the event that you want to delete or press enter to exit: ')
        if not password.strip():
            raise SystemExit
        
        while [doc for doc in events.find({'_id':ObjectId(id)})][0].get('password') != password:
            print('Sorry, wrong password')
            password = input('\nPlease provide the correct password or press enter to exit: ')
            if not password.strip():
                raise SystemExit

        details = get_details(id)
        if details:
            raise SystemExit

        confirm = input('Are you sure you want to delete the event? Enter yes to delete, otherwise press enter to exit. ').strip().lower()
        if confirm == 'yes':
            delete_event(id)
            print('Event successfully deleted.')

if __name__ == '__main__':
    main()