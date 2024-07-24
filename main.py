from functions import create_event, delete_event, chat, get_details, update_event

def main():
    # Main function to handle the user role and corresponding actions.
    role = input('Are you an event organizer or an event attendee? Answer with attendee/organizer or press enter to exit. ')
    if role.strip() == '':
        quit()

    while role.lower() not in ['attendee', 'organizer']:
        role = input('Please answer with attendee/organizer or press enter to exit. ')
        if role.strip() == '':
            quit()

    if role.lower() == 'attendee':
        handle_attendee()
    elif role.lower() == 'organizer':
        handle_organizer()

def handle_attendee():
    # Handle actions for event attendees.
    chat_id = input('\nPlease provide an event id for your event, or press enter to exit. ')
    if chat_id.strip() == '':
        quit()
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
        details = get_details(id)
        if details:
            quit()
        
        change = input('What do you want to change about the event? ')
        print(update_event(id, change))
        get_details(id)
    
    elif choice == 'delete':
        id = input('\nPlease provide id to delete event. ')
        details = get_details(id)
        if details:
            quit()

        confirm = input('Are you sure you want to delete the event? Enter yes to delete, otherwise press enter to exit. ').strip().lower()
        if confirm == 'yes':
            delete_event(id)
            print('Event successfully deleted.')

if __name__ == '__main__':
    main()