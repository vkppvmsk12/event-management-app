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
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user','content':user_input},{'role':'system','content':response}
    ])

event_info={}

def iterate_questions(questions):
    event_questions=[]
    try:
        for question in questions:
            ans=input(question)
            if ans.lower()=='skip':ans=None
            event_questions.append({'question':question,'answer':ans})
        return event_questions
    except json.decoder.JSONDecodeError:
        print('Sorry, something went wrong, please try again.')
        quit()

prompt='''
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date
    - Optional details: parking location, food options, seating

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

Provide the list of questions back to me in a JSON array in vector form. Avoid nested objects.
Avoid using '```json```' or any other text besides the JSON array. 
Make sure the response is a valid JSON list with no parsing errors.

Example of a valid JSON list response:
[
    "What do you want to name the event? ", 
    "Where is parking available? (Enter Skip if not applicable) "
]
'''

response=get_response(prompt)
event_questions=iterate_questions(json.loads(response))
event={}

while True:
    prompt2=f'''
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date
    - Optional details: parking, food options, seating

The following questions and answers are already available in JSON list format:
{json.dumps(event_questions, indent=4)}

Make sure that all mandatory details are filled in and not empty.
It's okay if the optional details aren't present.

The following 'event' JSON object is already built:
{json.dumps(event, indent=4)}

Update the above 'event' JSON object with all the details populated from the answers.
It doesn't matter if the optional fields are empty.

The object should meet the following criteria:
    1. The keys should be the specified parameters: 'event name', 'event description', ... (The ones mentioned earlier).
    2. Avoid nested objects.
    3. If certain optional details aren't provided, the value should be null.
    4. A mandatory detail (date, location, etc) may not have the value null.
    
    e.g. {'{"date":"8 September 2024","time":"4PM - 7PM"}'}

If not all information from the mandatory fields is present or complete, build a 'questions' JSON array 
in vector form of all questions where extra details must be provided. 
Don't ask me questions if the details are already complete.

The array should meet the following criteria:
    1. The array must be in vector form. Avoid nested arrays.
    3. Don't include questions for optional details e.g. parking, seating, etc.
    4. Don't include ```json``` or any other text besides the JSON array. 
       Make sure the response is a valid JSON array with no parsing errors.

Return a JSON object containing the 'event' JSON object and the 'questions' JSON array.

Example: 

{'''{
  "event": {
    "name": "xyz",
    "description": "abc",
    "location": "",
    "date": "",
    "parking": null,
    "food options": null,
    "seating": "seat 3A"
  },
  "questions": [
    "What is the location of the event? ",
    "What date is the event happening? "
  ]
}'''}    
'''
    
    response=get_response(prompt2)
    print(response)
    response_object=json.loads(response)
    event=response_object['event']

    if len(response_object.get('questions', [])) >0: 
        print('\nPlease include more details for the following questions:')
        event_questions=iterate_questions(response_object['questions'])
        continue
    break