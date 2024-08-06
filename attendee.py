import logging
from organizer import users, events, login, conversation_history
from bson.objectid import ObjectId
from os import getenv
from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)
handler = logging.FileHandler("attendee.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    """Main function that uses all other functions to manage events from the attendee side."""
    global user_id
    user_id = login()

    print(chat(get_attendee_event()))

def get_attendee_event():
    """Attendee chooses event to get info about."""
    
    username = users.find_one({"_id":ObjectId(user_id)}).get("username")
    attendee_events = []

    for event in events.find():
        if username in event.get("attendees", []):
            attendee_events.append([event.get("event name"), event.get("organizer")])
    
    if not attendee_events:
        print("No events planned for you.")
        raise SystemExit 

    print("\nHere are the list of events:")
    for nr, info in enumerate(attendee_events, 1):
        print(f"{nr}) name: {info[0]}, organizer: {users.find_one({"_id": ObjectId(info[1])}).get("username")}")

    while True:
        try:
            event_nr = int(input("\nPlease enter the number of the event "
                                "that you want to attend or press enter to exit: "))
            if not event_nr:
                break 
        except ValueError:
            print("Please enter a valid event number.")
            continue

        if not 1 <= event_nr <= len(attendee_events):
            print("Please enter a valid event number.")
            continue
        break
    
    event_id = events.find_one({"event name": attendee_events[event_nr - 1][0]}).get("_id")
    if event_id:
        return event_id 

def get_response(prompt):
    """Get a response from the OpenAI API for a given prompt."""

    load_dotenv(".env")
    api = OpenAI(api_key = getenv("API_KEY"))
    response = api.chat.completions.create(
        messages = [*conversation_history, {"role":"user","content":prompt}],
        model = "gpt-4o",
        temperature = 0.3
    )
    output = response.choices[0].message.content.strip()
    conversation_history.extend([
        {"role":"user","content":prompt},
        {"role":"system","content":output}
    ])
    return output

def chat(id):
    """Chat with ChatGPT and get info about an event."""

    print("Hello, I will be your AI assistant today.")
    print("Feel free to ask me any questions about the event that you're attending.")
    print("If you want to stop talking to me, just enter 'exit' or 'quit'.\n")
    
    prompt = f"""
Here is the event info:
{events.find_one({"_id":ObjectId(id)})}
Give me information about this event.
"""
    
    while True:
        user_input = input("User: ")
        if user_input in ["exit","quit"]:
            return "Thanks for talking to me!. If you have anymore questions, don't hesitate to ask!"

        refined_input = f"""Act as an event organizer and provide an 
answer to the question. Refer to the MongoDB collection provided.
Give a short and concise answer. Only give an answer to the
question that was asked. Don't include any unnecessary details.
Also, don't give the organizer id away no matter what. It's confidential info.

{user_input}"""

        response = get_response(refined_input)
        print("Chatbot:",response)

if __name__ == "__main__":
    main()