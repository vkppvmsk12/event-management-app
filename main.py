from os import path, remove
from json import dump, load
from chatbot import api_key, get_response, store_message

conversation_history = []
with open('.json', 'r') as JSON:
    if path.exists('.json'):
        conversation_history=[{'role':'user','content':load(JSON)}]

def get_info():
    global event_info
    event_info={}
    with open('.json', 'r') as JSON:
        if path.exists('.json'): event_info=load(JSON)
    
    print('I will ask you some questions about the event. If an answer isn\'t applicable, press enter.')
    print('If you want to keep any of the options the same, enter \'same\'.\n')
    event_name=input(f'What do you want to name the event? ')
    location=input(f'\nWhat is the location of the event? ')
    date=input(f'\nWhat are the days that the event is taking place? ')
    time=input(f'\nWhat time is the event taking place? ')
    parking=input(f'\nWhere is the parking available? ')
    food_options=input(f'\nAre there any food options for the event? If so, list a few of them. ')

    if not event_name.lower()=='same':event_info['event name']=event_name
    if not location.lower()=='same':event_info['location']=location
    if not date.lower()=='same':event_info['date']=date 
    if not time.lower()=='same':event_info['time']=time
    if not parking.lower()=='same':event_info['parking']=parking
    if not food_options.lower()=='same':event_info['food options']=food_options.split(', ')

    for key in event_info:
        if event_info[key]=='':
            event_info[key]=None
    
    global conversation_history
    
    with open('.json', 'w') as JSON:
        dump(event_info, JSON)
        conversation_history=[{'role':'user','content':load(JSON)}]

def get_details():
    print('Here are the details:')
    for key in event_info:
        print(f'{key}: {event_info[key]}')

def change_event():
    change='change'
    while change.lower()=='change':
        change=input('\nIf you want to change the details, type \'change\'. Press enter to continue.\n')
        if change.lower()=='change':
            get_info()
            print('Thanks for the info. Your event has been updated.')
            get_details()

while True:
    role=input('Are you an event organizer or an attendee? Answer with attendee/organizer.\n')
    print()
    match role.lower():
        case 'organizer':
            if not path.exists('.json'):
                get_info()
                print('Thanks for the info. Your event has been organized.\n')
                get_details()
                change_event()
                break
            else:
                delete=input('Do you want to delete your event? Enter \'yes\' to delete. Otherwise, press enter to continue.\n')
                if delete.lower()=='yes':remove('.json')

                with open ('.json', 'r') as JSON:
                    event_info = load(JSON)
                stored_info_prompt=f'''{event_info}
                
                Please remember the data inside the JSON string.
                My company depends on you to do the job right. 
                You will be asked information about it. It may change in the future.'''
                stored_info_response=get_response(stored_info_prompt)
                store_message(stored_info_prompt, stored_info_response)

                print('Good, your event is already organized.\n')
                get_details()
                change_event()
                
                print('Thanks for the info. Your event has been updated.')
                break

        case 'attendee':
            if not path.exists('.json'):
                print('There aren\'t any events planned for you yet.')
                break
            else:
                print('Hello, I will be your AI assistant today.')
                print('Feel free to ask me any questions about the event that you\'re attending.')
                print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')
                while True:
                    with open('.json', 'r') as JSON:
                        text = ' '.join(line.rstrip() for line in JSON)
                    user_input=input('User: ')
                    if user_input.lower() in ['exit', 'quit']: 
                        print('Bye')
                        quit()
                    response=get_response(user_input)
                    print('Chatbot:',response)
                    print()
                    store_message(user_input, response)

        case _:
            print('Please answer with either \'attendee\' or \'organizer\'.\n')