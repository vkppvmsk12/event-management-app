from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

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
    answered_questions={}
    event={}
    while True:
        prompt=f'''
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date
    - Optional details: parking, food options, seating

The following questions and answers are already available in JSON list format:
{json.dumps(answered_questions, indent=4)}

Make sure that all details are filled in and not empty.

The following 'event' JSON object is already built:
{json.dumps(event, indent=4)}

Update the above 'event' JSON object with all the details populated from the answers.

The object should meet the following criteria:
    1. The keys should be the specified parameters: 'event name', 'event description', ... (The ones mentioned above).
    2. Avoid nested objects.
    3. Each parameter may be present only once i.e. no duplicates.
    
    e.g. {'{"date":"8 September 2024", "event name":"Bob\'s Birthday party"}'}

If for some event details the value is an empty string, build a 'questions' JSON array 
in vector form of questions for those details. Don't inlcude questions of the details 
that are already present.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be left empty by entering 'N/A'.
    4. The questions for the mandatory details should have an asterisk at the end indicating
       that they are mandatory
    5. For each detail there should be 1 question i.e. no combining details into 1 question 
    or separating details into multiple questions.
    6. The questions should be explicit e.g. If the question is about date, 
    ask 'What date is the event happening?' instead of asking 'When is the event?'.
    7. There should be a space after the question i.e. '...? ' instead of '...?'.
    8. There shouldn't be any duplicate question. Include each question only once.

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
    "Is there parking available at the event? (enter N/A if none) ",
    "What food options are available? (enter N/A if none) "
]
}'''}    
'''
        
        response=get_response(prompt)
        try:
            response_object=json.loads(response)
        except json.decoder.JSONDecodeError:
            return 'Something went wrong, please try again'
        store_message(prompt, response)
        if response_object.get('event'):
            event=response_object.get('event')

        if len(response_object.get('questions', [])) >0: 
            print('\nPlease include the details for the following questions:')
            answered_questions=iterate_questions(response_object['questions'])
            continue
        break

    id=events.insert_one(event)
    return f'''Event was succesfully created. Here is the event id: {id.inserted_id}. 
    Store it somewhere, because you\'ll need it to change or delete your event.'''

def delete_event(event_id):
    result=events.delete_one({'_id':ObjectId(event_id)})
    if result.deleted_count: return 'The event was succesfully deleted.'
    return 'Sorry, no event with that id found.'

def chat(event_id):
    event_id=ObjectId(event_id)
    print('Hello, I will be your AI assistant today.')
    print('Feel free to ask me any questions about the event that you\'re attending.')
    print('If you want to stop talking to me, just enter \'exit\' or \'quit\'.\n')

    if not [doc for doc in events.find({'_id':event_id})]:
        return 'Sorry no event with that id found'
    
    prompt=f'''
Here is the event info:
{[doc for doc in events.find({'_id':ObjectId(event_id)})][0]}
Give me information about this event
'''
    conversation_history.append({'role':'user','content':prompt})
    
    while True:
        user_input=input('User: ')
        if user_input in ['exit','quit']:
            return 'Bye'

        refined_input=f'''Act as an event organizer and provide an 
                    answer to the question. Refer to the MongoDB collection provided.
                    Give a short and concise answer. Only give an answer to the
                    question that was asked. Don't include any unnecessary details.
                    
                    {user_input}'''

        response=get_response(refined_input)
        store_message(refined_input, response)
        print('Chatbot:',response)

def get_details(event_id):
    if not [doc for doc in events.find({'_id': ObjectId(event_id)})]: return 'This event doesn\'t exist'
    event_info=[doc for doc in events.find({'_id':ObjectId(event_id)})][0]
    for key in event_info:
        if key!='_id':print(f'{key}: {event_info[key]}')
    return ''

def change_event(event_name, wrong_parameters):
    answered_questions={}
    while True:
        prompt=f'''
The organizer of the event {event_name} has made some mistakes while entering the details for the event.
The parameters that the organizer would like to update are in the 'wrong_parameters' list: 
{wrong_parameters}

The following 'event' dictionary with all event information has already been built: 
{[doc for doc in events.find({'event name': event_name})][0]}

This 'answered_questions' dictionary contains the questions already answered by the organizer and their answers:
{answered_questions}

Update the 'event' dictionary with the answers from the answered_questions dictionary. 

For the event details that need to be updated, build a 'questions' JSON array 
in vector form of questions for those details. Don't ask me questions if the details aren't present
in the wrong_parameters list.

The questions should meet the following criteria:
    1. The questions should be short and concise
    2. The questions should be grammatically correct i.e. include capital letter and question mark
    3. The questions should indicate that the optional details can be left empty by entering 'N/A'.
    4. The questions for the mandatory details should have an asterisk at the end indicating
       that they are mandatory.
    5. For each detail there should be 1 question i.e. no combining details into 1 question 
    or separating details into multiple questions.
    6. The questions should be explicit e.g. If the question is about date, 
    ask 'What date is the event happening?' instead of asking 'When is the event?'.
    7. There should be a space after the question i.e. '...? ' instead of '...?'.
    8. There shouldn't be any duplicate question. Include each question only once.

The array should meet the following criteria:
    1. The array must be in vector form. Avoid nested arrays.
    2. Don't include ```json``` or any other text besides the JSON array. 
Make sure the response is a valid JSON array with no parsing errors.

Return a JSON object containing the 'event' JSON object and the 'questions' JSON array.

Example:
If wrong_parameters = ["date", "seating", "parking"],
and if event = {'''{
    "event name": "abc",
    "event description":"def",
    "location":"ghi",
    "date":"jkl",
    "parking":"mno",
    "food options":"pqr",
    "seating": "stu"
}'''}
and if answered_questions = {'''{
    {"question":"Is there parking available at the event? (enter N/A if none) ",
     "answer":"123"}
}'''}
then your response should be:
{'''{

"event":{
    "event name": "abc",
    "event description":"def",
    "location":"ghi",
    "date":"jkl",
    "parking":"123",
    "food options":"pqr",
    "seating": "stu"
}

"questions": [
    "On what date does the event take place? ",
    "How are the seating arrangements? "
]
   
}'''}

'''
        response=get_response(prompt)
        try:
            response_object=json.loads(response[response.index('{'):response.rfind('}')+1])
        except json.decoder.JSONDecodeError:
            return 'Something went wrong, please try again.'
        store_message(prompt, response)
        
        
        if response_object.get('questions')!=None:
            if len(response_object.get('questions')) >0:
                print('\nPlease include the details for the following questions:')
                answered_questions=iterate_questions(response_object['questions'])
                continue
            if response_object.get('event'):
                event=response_object.get('event')
            else:
                return 'Something went wrong, please try again.'
            events.delete_one({'event name':event_name})
            events.insert_one(event)
            return 'Event succesfully changed'
        else:
            return 'Something went wrong please try again.'

chat('669d9038b21960c1a1e66a43')