from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from json import loads

load_dotenv('.env')
api:str=OpenAI(api_key=getenv('API_KEY'))
conversation_history=[]

def get_response(prompt):
    response = api.chat.completions.create(
        messages=[*conversation_history,{'role':'user','content':prompt}],
        model='gpt-3.5-turbo',
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user','content':user_input},{'role':'system','content':response}
    ])

prompt='''
We are organizing an event and we would like to get the following details from the organizer:
    
    - Mandatory details: event name, event description, location, date, time (start and end together), 
      the schedule of the event and the contact information of the organizer.

    - Optional details: parking location, food options, seating, wifi info of the venue.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be skipped by entering 'Skip'
    4. For each detail there should be 1 question i.e. no combining details into 1 question 
    or separating details into multiple questions.
    5. The questions should be explicit e.g. If the question is about date, ask 'What date is the event happening?'
    instead of asking 'When is the event?'
    6. The questions should all be in a JSON array in vector form. Avoid nested objects.

e.g. :
    [
        "What do you want to name the event? ", 
        "Where is parking available? (Enter Skip if not applicable) "
    ]
'''
event_info={}

for question in loads(get_response(prompt)):
    ans=input(question)
    if ans.lower()=='skip':ans=None
    event_info[question]=ans

print(event_info)