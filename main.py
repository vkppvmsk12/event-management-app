from os import path, remove, getenv
from json import dump, load
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv('.env')
api: str = OpenAI(api_key=getenv('API_KEY'))

conversation_history = [
    {'role':'user','content':'I am an attendee at the event. Your job is tot give me info about the event.'}
]

def get_response(prompt):
    response=api.chat.completions.create(
        messages=[
            *conversation_history,
            {'role':'user','content':prompt}
        ],
        model='gpt-3.5-turbo',
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user','content':user_input},
        {'role':'system','content':response}
    ])

def get_info():
    global event_info
    event_info={}
    if path.exists('.json'):
        with open('.json', 'r') as JSON:
            event_info=load(JSON)
    
    print('\nI will ask you some questions about the event. If an answer isn\'t applicable, press enter.')
    print('If you want to keep any of the options the same, enter \'same\'.\n')
    event_name=input('What do you want to name the event? ')
    event_desctiption=input('\nCan you provide a description of the event? ')
    location=input('\nWhat is the location of the event? ')
    date=input('\nWhat are the days that the event is taking place? ')
    time=input('\nWhat time is the event taking place? ')
    parking=input('\nIs there any parking available? If so where? ')
    food_options=input('\nAre there any food options for the event? ')
    seating=input('\nAre there any specific seats for this event? ')
    wifi_info=input('\nWhat\'s the Wi-fi information for the venue? ')
    agenda=input('\nWhat\'s on the agenda for the event? ')

    if not event_name.lower()=='same':event_info['event name']=event_name
    if not event_desctiption.lower()=='same':event_info['event description']=event_desctiption
    if not location.lower()=='same':event_info['location']=location
    if not date.lower()=='same':event_info['date']=date 
    if not time.lower()=='same':event_info['time']=time
    if not parking.lower()=='same':event_info['parking']=parking
    if not food_options.lower()=='same':event_info['food options']=food_options
    if not seating.lower()=='same':event_info['seating']=seating
    if not wifi_info.lower()=='same':event_info['wifi inforamtion']=wifi_info
    if not agenda.lower()=='same':event_info['agenda']=agenda

    for key in event_info:
        if event_info[key]=='': event_info[key]=None
    
    global conversation_history
    
    with open('.json', 'w') as JSON:
        dump(event_info, JSON)
        
    with open('.json', 'r') as JSON:
        conversation_history=[{'role':'user','content':str(load(JSON))}]

def get_details():
    print('Here are the details:')
    for key in event_info:
        print(f'{key}: {event_info[key]}')

def change_event():
    change='change'
    while change.lower()=='change':
        change=input('\nIf you want to change the details, type \'change\'. Otherwise, press enter to continue.\n')
        if change.lower()=='change':
            get_info()
            print('Thanks for the info. Your event has been updated.')
            get_details()

if path.exists('.json'):
    with open('.json', 'r') as JSON:
        conversation_history=[{'role':'user','content':str(load(JSON))}]

while True:
    role=input('Are you an event organizer or an attendee? Answer with attendee/organizer.\n')
    print()
    match role.lower():
        case 'organizer':
            if not path.exists('.json'):
                create_event=input('Do you want to create an event? Enter \'yes\' to create event. Otherwise press enter to exit program.\n')
                if not create_event=='yes':quit()
                get_info()
                print('Thanks for the info. Your event has been organized.\n')
                get_details()
                change_event()
                break

            else:
                with open ('.json', 'r') as JSON:
                    event_info = load(JSON)

                print('Good, your event is already organized.\n')
                delete=input('Do you want to delete your event? Enter \'yes\' to delete. Otherwise, press enter to continue.\n')
                if delete.lower()=='yes':
                    remove('.json')
                    print('Your event has been deleted')
                    quit()

                get_details()
                change_event()
                break

        case 'attendee':
            if not path.exists('.json'):
                print('There aren\'t any events planned for you yet.')
                break
            else:
                print('Hello, I will be your AI assistant today.')
                print('Feel free to ask me any questions about the event that you\'re attending.')
                print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')
                conversation_history.append(
                    {
                    'role':'user', 
                    'content':'If you are asked when, give date and time if provided.'
                    }
                )

                while True:
                    user_input=input('''User: ''')
                    if user_input.lower() in ['exit', 'quit']: 
                        print('Bye')
                        quit()
                    refined_input=f'''Act as an event organizer and provide an 
                    answer to the question based on the JSON file. 
                    Include all details while answering the question,
                    but don't make the answer too long by inlcuding
                    unnecessary details. Do you understand?\n\n{user_input}'''
                    response=get_response(refined_input)
                    print('Chatbot:', response, '\n')
                    store_message(refined_input, response)

        case _:
            print('Please answer with either \'attendee\' or \'organizer\'.\n')