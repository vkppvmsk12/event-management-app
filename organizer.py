from bson.objectid import ObjectId
from json import dumps, loads
from pymongo import MongoClient
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from json.decoder import JSONDecodeError

client = MongoClient("mongodb://localhost:27017")
db = client["event-management-app"]
users = db["users"]
events = db["events"]

conversation_history = []

def main():
    """Handle actions for event organizers."""

    global user_id, api
    user_id = login()

    load_dotenv(".env")
    api = OpenAI(api_key = getenv("API_KEY"))
    
    choose_action()

def choose_action():
    """Allow user to choose between the actions: create, edit, delete an event."""

    choice = input("\nDo you want to create, delete, or edit an event? " 
                "Answer with create/edit/delete, otherwise press enter to exit. ").strip().lower()
    
    while choice not in ["create", "edit", "delete"]:
        if not choice:
            return
        print("Sorry, this is not a valid response")
        choice = input("\nDo you want to create, delete, or edit an event? "
                    "Answer with create/edit/delete, otherwise press enter to exit. ").strip().lower()

    if choice == "create":
        id = create_event()
        try: 
            ObjectId(id)
        except TypeError:
            print(id)
            raise SystemExit
        
        events.update_one({"_id":ObjectId(id)},{"$set":{"organizer":user_id}})
    
    elif choice == "edit":  
        print(edit_event())
    
    elif choice == "delete":
        print(delete_event())

def get_json_object_response(prompt):
    """Get a JSON object response from the OpenAI API for a given prompt."""
    response = api.chat.completions.create(
        messages = [*conversation_history,{"role":"user","content":prompt}],
        model = "gpt-4o-2024-08-06",
        temperature = 0.3,
        response_format = {"type":"json_object"}
    )
    output = response.choices[0].message.content.strip()
    conversation_history.extend([
        {"role":"user", "content":prompt}, 
        {"role":"system", "content":response}
    ])
    return output

def iterate_questions(questions):
    """Iterate through a list of questions and collect answers from the user."""
    event_questions = []
    try:
        for question in questions:
            ans = input(question)
            if ans.lower() == "skip":
                ans = None
            event_questions.append({"question":question,"answer":ans})
        return event_questions
    except JSONDecodeError:
        print("Sorry, something went wrong, please try again.")

def login():
    global username, password
    username = input("\nPlease enter your username or press enter to exit: ").strip()
    if not username:
        raise SystemExit

    while not users.find_one({"username":username}):
        print("Sorry, that username doesn't exist.")
        username = input("\nPlease enter a valid username or press enter to skip: ").strip()
        if not username:
            raise SystemExit

    password = input("\nPlease enter your password or press enter to exit: ")
    if not password:
        raise SystemExit
    
    user_info = users.find_one({"username":username})
    while password not in user_info.values():
        print("Sorry, invalid password.")
        password = input("Please enter a valid password or press enter to exit: ")
        if not password:
            SystemExit
    
    return str(users.find_one({"username":username, "password":password})["_id"])

def get_details(event_id):
    """Get an event's details."""
    
    if not events.find_one({"_id": event_id}): 
        return "This event doesn't exist."
    
    event_info = events.find_one({"_id":event_id})

    print("\nHere are the event details for your event:")
    for key in event_info:
        if key not in ["_id", "organizer"]:
            print(f"{key}: {event_info[key]}")

    return

def create_event():
    """Create a new event by collecting details from the organizer."""

    answered_questions = {}
    event_info = {}
    while True:
        prompt = f"""
We are organizing an event and we would like to get the following details from the organizer:
    - Mandatory details: event name, event description, location, date, start time, end time, contact info of organizer
    - Optional details: parking, food options, seating, wifi info of venue, schedule of event 

The following questions and answers are already available in JSON array format:
{dumps(answered_questions, indent = 4)}
It is possible that this JSON array is empty, that just means that I haven't given any info yet.

The following 'event' JSON object is already built:
{dumps(event_info, indent = 4)}

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

{"""{
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
}"""}    
"""
        
        response = get_json_object_response(prompt)

        sliced_response = response[response.find("{"):response.rfind("}")+1]
        if not sliced_response:
            return "Sorry, something went wrong, please try again"

        try:
            response_object = loads(sliced_response)
        except JSONDecodeError:
            return "Something went wrong, please try again"
        
        if response_object.get("event"):
            event_info = response_object.get("event")

        if len(response_object.get("questions", [])) > 0: 
            print("\nPlease include the details for the following questions:")
            answered_questions = iterate_questions(response_object["questions"])
            continue
        break

    attendees = []
    while True:
        attendee = input("\nPlease enter the e-mails of the attendees for your event or press enter to stop. ").strip()
        if not attendee:
            break
            
        if not users.find_one({"email":attendee}):
            print("Sorry, this user doesn't exist. Please enter a valid email.")
            continue
        attendees.append(attendee)
    event_info["attendees"] = attendees

    id = events.insert_one(event_info)
    
    print(f"\nEvent was succesfully created.")
    return id.inserted_id

def get_organizer_events():
    """Shows organizer the available events."""

    username = users.find_one({"_id":ObjectId(user_id)}).get("username")
    organizer_events = [event.get("event name") for event in events.find() 
                        if users.find_one({"_id":ObjectId(event.get("organizer"))}).get("username") == username]
    if not organizer_events:
        print("You don't have any events organized yet.")
        raise SystemExit
    print("\nHere are your events:")
    for nr, event in enumerate(organizer_events, start = 1):
        print(nr, event)
    
    while True:
        try:
            event_nr = int(input("\nPlease enter the number of the event that you want to access (see above): "))
        except ValueError:
            print("Please enter a valid event number.")
            continue

        if not 1 <= event_nr <= len(organizer_events):
            print("Please enter a valid event number.")
            continue

        break

    return events.find_one({"event name": organizer_events[event_nr - 1]}).get("_id")

def edit_event():
    """Edit an existing event with the corrected details"""

    event_id = get_organizer_events()
    wrong_details = input("What do you want to change about the event? ")
    
    prompt = f"""
The organizer of an event has made a mistake while entering a detail for this event.

Here are the original event details for context:
{events.find_one({"_id":ObjectId(event_id)},{"_id":0})}

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
{"""{
    "contact info of organizer":"e-mail: xyz@gmail.com"
    "end time": "8pm"
}"""}

Avoid nested objects (except for the list of invited attendees for which the value should be an array), 
and make all the keys and values strings only (except for list of attendees which should be an array).
"""

    response = get_json_object_response(prompt)

    sliced_response = response[response.find("{"):response.rfind("}")+1]
    if not sliced_response:
        return "Sorry, something went wrong, please try again."

    try:
        response = loads(sliced_response)
    except JSONDecodeError:
        return "Sorry, something went wrong, please try again"
    
    list_keys = ["event name","event description","location","date","start time", "end time", "food options",
    "contact info of organizer","parking", "seating","wifi info of venue", "schedule of event", "attendees"]
    
    for key in response:
        if key.strip() not in list_keys: 
            return "Sorry, something went wrong, please try again."
    
    attendees = response.get("attendees", [])[:]
    for attendee in attendees:
        is_user = False
        for user in users.find():
            print(attendee)
            if attendee.strip() == user.get("email"):
                is_user = True
        if not is_user:
            response.get("attendees", []).remove(attendee)
            print(f"\n{attendee} was removed because this user doesn't exist")

    events.update_many({"_id":ObjectId(event_id)}, {"$set":response})
    details = get_details(event_id)
    if details:
        print(details)
    
    return "Event succesfully updated."

def delete_event():
    """Delete an existing event."""
   
    event_id = get_organizer_events()

    details = get_details(event_id)
    
    confirm = input("Are you sure that you want to delete this event? This action can't be undone. "
                    "Enter yes to continue, or press enter to exit: ").strip().lower()
    
    if confirm != "yes":
        return "Event not deleted"

    result = events.delete_one({"_id":ObjectId(event_id)})
    
    if result.deleted_count: 
        return "The event was succesfully deleted."
    
    return "Sorry, no event with that id found."

if __name__ == "__main__":
    main()