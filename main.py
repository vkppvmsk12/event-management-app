# Parameters: location, date, time, parking, meal times.
from os import path
from json import dump, load
from chatbot import openai, get_response, store_message, conversation_history

def get_info():
    global event_info
    event_info={}
    
    print('I will ask you some questions about the event. If an answer isn\'t applicable, press enter.\n')
    event_name=input(f'What do you want to name the event? ')
    location=input(f'\nWhat is the location of the event? ')
    date=input(f'\nWhat are the days that the event is taking place? ')
    time=input(f'\nWhat time is the event taking place? ')
    parking=input(f'\nWhere is the parking available? ')
    food_options=input(f'\nAre there any food options for the event? If so, list a few of them. ')

    event_info['event name']=event_name
    event_info['location']=location
    event_info['date']=date 
    event_info['time']=time
    event_info['parking']=parking
    event_info['food options']=food_options.split(', ')

    for key in event_info:
        if event_info[key]=='':
            event_info[key]=None
    
    with open('.json', 'w') as JSON:
        dump(event_info, JSON)

def get_details():
    print('Here are the details:')
    for key in event_info:
        print(f'{key}: {event_info[key]}')

while True:
    role=input('Are you an event organizer or an attendee? Answer with attendee/organizer.\n')
    print()
    match role.lower():
        case 'organizer':
            if not path.exists('.json'):
                get_info()
                print('Thanks for the info. Your event has been organized.\n')
                get_details()

                break
            else:
                with open ('.json', 'r') as JSON:
                    event_info = load(JSON)
                print('Good, your event is already organized.\n')
                get_details()
                change='change'
                while change.lower()=='change':
                    change=input('\nIf you want to change the details, type \'change\'. Press enter to continue.\n')
                    if change.lower()=='change':
                        get_info()
                        print('Thanks for the info. Your event has been updated.')
                        get_details()
                
                print('Thanks for the info. Your event has been updated.')
                #stored_info=f'{event_info}\n\n'
                break

        case 'attendee':
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
                refined_prompt=f'''{user_input}\n\nRefer to this .json file:\n\n{text}\n
                Answer me as if I was someone attending the event. 
                Only give the answer to the question that was asked. Don't include any other parameters.'''
                response=get_response(refined_prompt)
                print('Chatbot:',response)
                print()
                store_message(user_input, response)

        case _:
            print('Please answer with either \'attendee\' or \'organizer\'.\n')
