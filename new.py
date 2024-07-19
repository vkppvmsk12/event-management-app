from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import json
from pymongo import MongoClient

load_dotenv('.env')
api:str=OpenAI(api_key=getenv('API_KEY'))
conversation_history=[]

def get_response(prompt):
    response=api.chat.completions.create(
        messages=[*conversation_history,{'role':'user','content':prompt}],
        model='gpt-4o',
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user','content':user_input},{'role':'system','content':response}
    ])

client=MongoClient('mongodb://localhost:27017')
db=client['mydb']
events=db['events']

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

def create_event():
    event_questions={}
    event={}
    while True:
        prompt=f'''
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date
    - Optional details: parking, food options, seating

The following questions and answers are already available in JSON list format:
{json.dumps(event_questions, indent=4)}

Make sure that all mandatory details are filled in and not empty.
It's okay if the optional details are empty.

The following 'event' JSON object is already built:
{json.dumps(event, indent=4)}

Update the above 'event' JSON object with all the details populated from the answers.
It doesn't matter if the optional fields are empty.

The object should meet the following criteria:
    1. The keys should be the specified parameters: 'event name', 'event description', ... (The ones mentioned above).
    2. Avoid nested objects.
    3. Each parameter may be present only once i.e. no duplicates.
    
    e.g. {'{"date":"8 September 2024", "event name":"Bob\'s Birthday party"}'}

If for some event details the value is an empty string, build a 'questions' JSON array 
in vector form of questions for those details. Don't ask me questions if the details are already present.
If a detail was given, adding the information is mandatory.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be left empty by entering 'N/A'.
    4. For each detail there should be 1 question i.e. no combining details into 1 question 
    or separating details into multiple questions.
    5. The questions should be explicit e.g. If the question is about date, 
    ask 'What date is the event happening?' instead of asking 'When is the event?'.
    6. There should be a space after the question i.e. '...? ' instead of '...?'.
    7. There shouldn't be any duplicate question. Include each question only once.

The array should meet the following criteria:
    1. The array must be in vector form. Avoid nested arrays.
    2. Don't include ```json``` or any other text besides the JSON array. 
    Make sure the response is a valid JSON array with no parsing errors.

Return a JSON object containing the 'event' JSON object and the 'questions' JSON array.

Example: 

{'''{
"event": {
    "event name": "xyz",
    "event description": "abc",
    "location": "",
    "date": "",
    "parking": "",
    "food options": "",
    "seating": "seat 3A"
},
"questions": [
    "What is the location of the event? ",
    "What date is the event happening? ",
    "What food options are available? "
]
}'''}    
'''
        
        response=get_response(prompt)
        response_object=json.loads(response)
        event=response_object['event']

        if len(response_object.get('questions', [])) >0: 
            print('\nPlease include the details for the following questions:')
            event_questions=iterate_questions(response_object['questions'])
            continue
        break

    events.insert_one(event)
    return 'Event was succesfully created'

def delete_event(event_name):
    prompt=f'''We want to delete an event from a MongoDB database. 
Here's the name of the event we want to delete: {event_name}

Can you generate a query in JSON object format to delete the event where the key is 'event name' and the 
value is the name of the event provided? e.g. If the event name is 'abc', 
your answer should be '{'{"event name":"abc"}'}'

Avoid including ```json``` or any other text that could give an error while parsing.
The output should be a valid parsable JSON object.
'''
    
    response=get_response(prompt)
    print(response)
    try:
        query=json.loads(response)
    except json.decoder.JSONDecodeError:
        print('Sorry something went wrong. Please try again.')
    
    print(query)
    result=events.delete_one(query)
    
    if result.deleted_count: return 'The event was succesfully deleted.'
    return 'Sorry, no event with that name found.'

def chat(event_name):
    print('Hello, I will be your AI assistant today.')
    print('Feel free to ask me any questions about the event that you\'re attending.')
    print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')

    prompt=f'''
Here is the 'events' collection in my database:
{[event for event in events.find()]}
Give me information about the following event: {event_name}
'''
    conversation_history.append({'role':'user','content':prompt})
    
    while True:
        user_input=input('User: ')
        if user_input in ['exit','quit']:
            print('Bye')
            break

        refined_input=f'''Act as an event organizer and provide an 
                    answer to the question. Refer to the MongoDB collection provided.
                    Give a short and concise answer. Only give an answer to the
                    question that was asked. Don't include any unnecessary details.
                    
                    {user_input}'''

        response=get_response(refined_input)
        print('Chatbot:',response)