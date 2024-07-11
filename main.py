# Parameters: location, date, time, parking, meal times.
from os import path
from json import dump

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
            event_info[key] = None

    print(event_info)
    with open('files/.json', 'w') as JSON:
        dump(event_info, JSON)