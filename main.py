# Parameters: location, date, time, parking, meal times.
from os import path
from json import dump
from chatbot import openai, get_response

if not path.exists('.json'):
    event_info={}
    end_of_input='If it doesn\'t exist, then just hit enter.\n\n'

    location=input(f'What is the location of the event? {end_of_input}')
    date=input(f'\nWhat are the days that the event is taking place? {end_of_input}')
    time=input(f'\nWhat time is the event taking place? {end_of_input}')
    parking=input(f'\nWhere is the parking available? {end_of_input}')
    meal_timings=input(f'\nWhat are the meal timings for the event? {end_of_input}')

    event_info['location']=location
    event_info['date']=date 
    event_info['time']=time
    event_info['parking']=parking
    event_info['meal timings']=meal_timings

    for key in event_info:
        if event_info[key] == '':
            event_info[key]=None

    print(event_info)

    with open('.json', 'w') as JSON:
        dump(event_info, JSON)

print('Hello, I will be your AI assistant today.')
print('Feel free to ask me any questions about the event that you\'re attending.\n')
while True:
    with open('.json', 'r') as JSON:
        text = ' '.join(line.rstrip() for line in JSON)
    user_input=input('User: ')
    if user_input.lower() in ['exit', 'quit']: print('Bye'); break
    refined_input=f'''{user_input}\n\nRefer to this .json file:\n\n{text}\n
    Answer me as if I was someone attending the event. 
    Only give the answer to the question that was asked. Don't include any other parameters.'''
    response=get_response(refined_input)
    print('Chatbot:',response)
    print('')