from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import json

load_dotenv('.env')
api:str=OpenAI(api_key=getenv('API_KEY'))
conversation_history=[]

def get_response(prompt):
    response=api.chat.completions.create(
        messages=[*conversation_history,{'role':'user','content':prompt}],
        model='gpt-4o',
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user','content':user_input},{'role':'system','content':response}
    ])

event_info={}

def iterate_questions(prompt):
    try:
        response=get_response(prompt)
        for question in json.loads(response):
            ans=input(question)
            if ans.lower()=='skip':ans=None
            event_info[question]=ans
    except json.decoder.JSONDecodeError:
        print('Sorry, something went wrong, please try again.')
        print(response)
        quit()

prompt='''
We are organizing an event and we would like to get the following details from the organizer:
    
    - Mandatory details: event name, event description, location, date, start time, end time, 
      the schedule of the event, the contact information of the organizer.

    - Optional details: parking location, food options, seating, wifi info of the venue.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be skipped by entering 'Skip'
    4. For each detail there should be 1 question i.e. no combining details into 1 question 
       or separating details into multiple questions.
    5. The questions should be explicit e.g. If the question is about date, 
       ask 'What date is the event happening?' instead of asking 'When is the event?'
    6. There should be a space after the question i.e. '...? ' instead of '...?'
    7. There shouldn't be any duplicate question. Include each question only once
    8. The questions should all be in a JSON array in vector form. Avoid nested objects.
    9. Avoid using '```json```' or any other text besides the JSON array. 
       That gives me an error while parsing.

e.g. :
    [
        "What do you want to name the event? ", 
        "Where is parking available? (Enter Skip if not applicable) "
    ]
'''

iterate_questions(prompt)

while True:
    print('\nPlease include more details for the following questions:')
    prompt2=f'''
Here's the information that we got from the organizer:

{event_info}

Recheck from my previous prompt which details are mandatory and which are optional.

Make sure that all mandatory details are filled in and not empty.
Also make sure that all mandatory details are complete and no information is missing.
e.g. Schedule isn't complete

It's okay if the optional details aren't present.

If all information from the mandatory fields is complete and no information is missing, then give me a 
JSON object with all the event details. It doesn't matter if the optional fields are empty.

The object should meet the following criteria:
    1. The keys should be the parameters specified e.g. "date", "time", "location", etc.
    2. Avoid nested objects.
    3. If certain optional details are not provided, the value should be null.
    4. No mandatory detail e.g. date, location, etc. may have the value null.
    5. Use the following keys in order: event name, event description, location, start time,
       end time, schedule, contact information, parking, food options, seating, wifi.

    e.g. {'{'}"date":"8 September 2024","time":"4PM - 7PM"{'}'}

If not all information from the mandatory fields is present or complete, give me a JSON array in vector form of 
all questions where extra details must be provided. Don't ask me questions if the details are already complete.

The array should meet the following criteria:
    1. The array must be in vector form. Avoid nested arrays.
    2. The questions must be exactly the same as the ones from your previous response
       so that I can overwrite the previous questions in my dictionary. 
       Don't forget the space after the question mark
    3. Don't include questions for optional details e.g. parking, wifi information, etc.
    4. Don't include ```json``` or any other text besides the JSON array. 
       That gives me an error while parsing.
'''
    #if type(json.loads(get_response(prompt2))) != dict: iterate_questions(prompt2)
    #else: break
    print(prompt2)
    print(get_response(prompt2))
    break

#print(json.loads(get_response(prompt2)))