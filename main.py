from os import path, remove, getenv
from json import dump, load
from openai import OpenAI
from dotenv import load_dotenv
import pymongo

load_dotenv('.env')
api: str = OpenAI(api_key=getenv('API_KEY'))

client = pymongo.MongoClient('mongodb://localhost:27017')
db=client['db']
events=db['events']

conversation_history = [
    {'role':'user','content':'I am an attendee at the event. Your job is tot give me info about the event.'}
]

change='change'
access=''

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
    global access
    event_info=events.find_one({'password':access})
    
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
    contact_organizer=input('\nHow can the attendees of the event contact you if necessary? ')
    password=input('''\nCan you provide a password that the attendees can use to access the event details of the event? 
The password may not be \'same\', and it may not match any other password. ''')

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
    if not contact_organizer.lower()=='same':event_info['contact details of organizer']=contact_organizer

    for key in event_info:
        if event_info[key]=='': event_info[key]=None

    while ('password' not in event_info and password.lower()=='same') or (password==''):
        password=input('Invalid input. Please enter a valid password. ')
    
    if password.lower()=='same' and password in event_info: password = event_info['password']
    
    while password in events.find({'password': password}):
        password=input('That password\'s taken. Please enter a different password. ')

    global conversation_history
 
    if change=='change':events.delete_one({'password':access})
    events.insert_one(event_info)

def get_details():
    print('Here are the details:')
    for key in events.find_one():
        if key!='_id':print(f'{key}: {events.find_one()[key]}')

def change_event():
    global change
    while change.lower()=='change':
        change=input('\nIf you want to change the details, type \'change\'. Otherwise, press enter to continue.\n')
        if change.lower()=='change':
            get_info()
            print('Thanks for the info. Your event has been updated.')
            get_details()

def create_event():
    global change
    change=False
    get_info()
    print('Thanks for the info. Your event has been organized.\n')
    get_details()
    change_event()

role = ''
while not (role.lower() in ['attendee', 'organizer']):
    role=input('Are you an event organizer or an attendee? Answer with attendee/organizer.\n')
    print()
    if not (role in ['attendee', 'organizer']): 
        print('Please answer with either \'attendee\' or \'organizer\'.\n')

else:
    match role.lower():
        case 'organizer': 
            create=input('Do you want to create an event? Enter \'yes\' to create event. Otherwise press enter to continue.\n')
            if create.lower()=='yes': 
                create_event()
            else:
                if events.count_documents({})==0:
                    print('There are any saved events that you\'ve organized')
                    quit()
                access=input('Which event do you want to access? Enter the password of the event. Otherwise press enter to exit.\n')
                if access=='': quit()
                
                while not any(event for event in events.find({'password': access})):
                    access=input('Invalid password. Please enter a valid password or press enter to exit. ')
                    if access=='': quit()

                delete=input('\nDo you want to delete your event? Enter \'yes\' to delete. Otherwise, press enter to continue.\n')
                if delete.lower()=='yes':
                    events.delete_one({'password': access})
                    print('Your event has been deleted')
                    quit()

                get_details()
                change_event()

        case 'attendee':
            if not events.count_documents({}):
                print('There aren\'t any events planned for you yet.')
            else:
                entry=input('Please provide a password for the event for which you want details. Press enter to exit program. ')
                if entry=='':quit()
                while not events.find_one({'password':entry}):
                    entry=input('Invalid password. Please provide a correct password, or press enter to exit. ')
                    if entry=='':quit()

                print('Hello, I will be your AI assistant today.')
                print('Feel free to ask me any questions about the event that you\'re attending.')
                print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')
                conversation_history.extend([
                    {'role':'user','content':str(events.find())},
                    {'role':'user','content':f'Here is the password provided to access details: {entry}'},
                    {'role':'user', 'content':'If you are asked when, give date and time if provided.'}
                ])
                
                conversation_history = [
                    {'role':'user','content':str(events.find_one())}
                ]

                while True:
                    user_input=input('''User: ''')
                    if user_input.lower() in ['exit', 'quit']:
                        print('Bye')
                        quit()
                    refined_input=f'''Act as an event organizer and provide an 
                    answer to the question. Give information for the event for 
                    which the password was provided. Refer to the MongoDB collection provided.
                    Include all details while answering the question,
                    but don't make the answer too long by inlcuding
                    unnecessary details. Do you understand?\n\n{user_input}'''
                    response=get_response(refined_input)
                    print('Chatbot:', response, '\n')
                    store_message(refined_input, response)