from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import json
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

load_dotenv('.env')
api:str=OpenAI(api_key = getenv('API_KEY'))
conversation_history = []

def get_response(prompt):
    response = api.chat.completions.create(
        messages = [*conversation_history, {'role':'user','content':prompt}],
        model = 'gpt-4o',
        temperature = 0.3
    )
    return response.choices[0].message.content.strip()

def get_json_object_response(prompt):
    response = api.chat.completions.create(
        messages = [*conversation_history,{'role':'user','content':prompt}],
        model = 'gpt-4o',
        temperature = 0.3,
        response_format = {'type':'json_object'}
    )
    return response.choices[0].message.content.strip()

def store_message(user_input, response):
    conversation_history.extend([
        {'role':'user', 'content':user_input},{'role':'system', 'content':response}
    ])

client = MongoClient('mongodb://localhost:27017')
db = client['mydb']
events = db['events']

def iterate_questions(questions):
    event_questions = []
    try:
        for question in questions:
            ans = input(question)
            if ans.lower() == 'skip':
                ans = None
            event_questions.append({'question':question,'answer':ans})
        return event_questions
    except json.decoder.JSONDecodeError:
        print('Sorry, something went wrong, please try again.')

def create_event():
    answered_questions = {}
    event = {}
    while True:
        prompt = f'''
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date, start time, end time, contact info of organizer
    - Optional details: parking, food options, seating, wifi info of venue, schedule of event 

The following questions and answers are already available in JSON array format:
{json.dumps(answered_questions, indent=4)}
It is possible that this JSON array is empty, that just means that I haven't given any info yet.

The following 'event' JSON object is already built:
{json.dumps(event, indent=4)}

Update the above 'event' JSON object with all the details populated from the answers if any.

The object should meet the following criteria:
    1. The keys should be the specified parameters: 'event name', 'event description', ... (The ones mentioned above).
    2. Avoid nested objects.
    3. Each parameter may be present only once i.e. no duplicates.
    
    e.g. {'{"date":"8 September 2024", "event name":"Bob\'s Birthday party"}'}

If for some event details the value is an empty string, build a 'questions' JSON array 
in vector form of questions for those details. 
Don't inlcude questions of the details that are already present. 

The array must be in vector form. Avoid nested arrays.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be left empty by entering 'N/A'.
    4. The questions for the mandatory details should have an asterisk (*)  at the end indicating
       that they are mandatory
    5. For each detail there should be 1 question i.e. no combining details into 1 question 
    or separating details into multiple questions.
    6. The questions should be explicit e.g. If the question is about date, 
    ask 'What date is the event happening?' instead of asking 'When is the event?'.
    7. There should be a space after the question i.e. '...? ' instead of '...?'.
    8. There shouldn't be any duplicate question. Include each question only once.
    
Make sure the response is a valid JSON array with no parsing errors.

Return a JSON object containing the 'event' JSON object and the 'questions' JSON array.

Example: 

{'''{
"event": {
    "event name": "xyz",
    "event description": "abc",
    "location": "",
    "date": "",
    "start time":"def"
    "end time": "ghi"
    "contact info of organizer":"jkl"
    "parking": "",
    "food options": "",
    "seating": "seat 3A"
    "wifi info of venue": "mno"
    "schedule of event":"pqr"
},
"questions": [
    "What is the location of the event?* ",
    "What date is the event happening?* ",
    "Is there parking available at the event? (enter N/A if none) ",
    "What food options are available? (enter N/A if none) "
]
}'''}    
'''
        
        response = get_json_object_response(prompt)
        response = response[response.index('{'):response.rfind('}')+1]

        try:
            response_object = json.loads(response)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong, please try again'
        store_message(prompt, response)
        
        if response_object.get('event'):
            event = response_object.get('event')

        if len(response_object.get('questions', [])) > 0: 
            print('\nPlease include the details for the following questions:')
            answered_questions = iterate_questions(response_object['questions'])
            continue
        break

    id = events.insert_one(event)
    return f'''\nEvent was succesfully created. Here is the event id: {id.inserted_id}. Store 
it somewhere, because you\'ll need it to edit or delete your event.'''

def delete_event(event_id):
    try:
        result = events.delete_one({'_id':ObjectId(event_id)})
    except InvalidId:
        return 'Sorry, invalid id'
    
    if result.deleted_count: 
        return 'The event was succesfully deleted.'
    
    return 'Sorry, no event with that id found.'

def chat(event_id):
    try:
        event_id = ObjectId(event_id)
    except InvalidId:
        return 'Sorry invalid id.'
    
    print('Hello, I will be your AI assistant today.')
    print('Feel free to ask me any questions about the event that you\'re attending.')
    print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')

    if not [doc for doc in events.find({'_id':event_id})]:
        return 'Sorry no event with that id found'
    
    prompt = f'''
Here is the event info:
{[doc for doc in events.find({'_id':ObjectId(event_id)})][0]}
Give me information about this event
'''
    conversation_history.append({'role':'user','content':prompt})
    
    while True:
        user_input = input('User: ')
        if user_input in ['exit','quit']:
            return 'Thanks for talking to me!. If you have anymore questions, don\'t hesitate to ask!'

        refined_input = f'''Act as an event organizer and provide an 
                    answer to the question. Refer to the MongoDB collection provided.
                    Give a short and concise answer. Only give an answer to the
                    question that was asked. Don't include any unnecessary details.
                    
                    {user_input}'''

        response = get_response(refined_input)
        store_message(refined_input, response)
        print('Chatbot:',response)

def get_details(event_id):
    try:
        event_id = ObjectId(event_id)
    except InvalidId:
        return 'Sorry, invalid id.'
    
    if not [doc for doc in events.find({'_id': event_id})]: 
        return 'This event doesn\'t exist'
    
    event_info = [doc for doc in events.find({'_id':event_id})][0]

    print('\nHere are the event details for your event:')
    for key in event_info:
        if key != '_id':
            print(f'{key}: {event_info[key]}')

    return ''

def change_event(event_id, wrong_details):
    try:
        event_id = ObjectId(event_id)
    except InvalidId:
        return 'Sorry invalid id.'
    
    if not [doc for doc in events.find({'_id':event_id})][0]: 
        return 'Sorry event not found.'
    
    prompt=f'''
The organizer of an event has made a mistake while entering a detail for this event.

Here are the original event details for context:
{[doc for doc in events.find({'_id':ObjectId(event_id)},{'_id':0})][0]}

The organizer would like to update the following details: 
{wrong_details}

Can you please generate a JSON object containing only the updated details? 
The key should be the detail, and the value should be the given info from the organizer

For the keys, choose from the following: event name, event description, location, date, start time,
end time, contact info of organizer, parking, food options, seating, wifi info of venue, schedule of event.

Copy the keys exactly as sepcified above, so that they can be overwritten in the database.
Don't include an underscore to separate words. Include all details provided

Example: 
If the correction specified by the organizer is 
'I want the attendees to contact me by my e-mail: xyz@gmail.com and I want to shorten the event to 8pm',

then your response should be:
{'''{
    "contact info of organizer":"e-mail: xyz@gmail.com"
    "end time": "8pm"
}'''}

Avoid nested objects, and make all the keys and values strings only.
'''

    response = get_json_object_response(prompt)
    response = response[response.index('{') : response.rfind('}')+1]
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return 'Sorry, something went wrong, please try again'
    
    list_keys = ['event name','event description','location','date','start time', 'end time', 'food options',
    'contact info of organizer','parking', 'seating','wifi info of venue', 'schedule of event']
    
    for key in response:
        if key.strip() not in list_keys: 
            return 'Sorry, something went wrong, please try again.'
    
    events.update_many({'_id':ObjectId(event_id)}, {'$set':response})
    
    return 'Event succesfully updated.'