from functions import create_event, delete_event, chat, get_details, change_event

role=input('Are you an event organizer or an event attendee? Answer with attendee/organizer or press enter to exit. ')
if role.strip()=='': quit()

while role.lower() not in ['attendee','organizer']:
    role=input('Please answer with attendee/organizer or press enter to exit. ')
    if role.strip()=='':quit()

match role.lower():
    case 'attendee':
        chat_id=input('\nPlease provide an event id for your event, or press enter to exit. ')
        if chat_id.strip()=='':quit()
        print(chat(chat_id))
    
    case 'organizer':
        choice=input('''\nDo you want to create, delete, or edit an event? 
Answer with create/edit/delete, otherwise press enter to exit. ''')

        match choice.lower():
            case 'create':
                print(result:=create_event())
                if result[0]=='E':get_details(result[result.index(':')+2:result.index('. S')])
            
            case 'edit':
                id=input('\nPlease provide id to edit event. ')
                print(details:=get_details(id))
                if details: quit()
                
                change=input('What do you want to change about the event? ')
                print(change_event(id, change))
                
                get_details(id)
            
            case 'delete':
                id=input('\nPlease provide id to delete event. ')
                print(details:=get_details(id))
                if details: quit()

                confirm=input('''Are you sure you want to delete the event? 
Enter yes to delete, otherwise press enter to exit. ''')
                if confirm.lower()=='yes':
                    delete_event(id)
                    print('Event succesfully deleted.')