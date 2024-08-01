import logging
from organizer import users, events, store_message, api, login
from bson.objectid import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)
handler = logging.FileHandler("attendee.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def main():
    """Handle actions for event attendees."""
    
    global user_id
    user_id = login()
    username = users.find_one({"_id":ObjectId(user_id)}).get("username")
    attendee_events = []

    for event in events.find():
        if username in event.get("attendees", []):
            attendee_events.append(event.get("event name"))
    
    if not attendee_events:
        print("No events planned for you.")
        raise SystemExit 

    print("\nHere are the list of events:")
    for nr, event_name in enumerate(attendee_events, 1):
        print(nr, event_name)

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


    chat_id = str(events.find_one({"event name":attendee_events[event_nr - 1]}).get("_id"))
    print(chat(chat_id))

conversation_history = []

def get_response(prompt):
    """Get a response from the OpenAI API for a given prompt."""
    response = api.chat.completions.create(
        messages = [*conversation_history, {"role":"user","content":prompt}],
        model = "gpt-4o",
        temperature = 0.3
    )
    return response.choices[0].message.content.strip()

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
    conversation_history.append({"role":"user","content":prompt})
    
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
        store_message(refined_input, response)
        print("Chatbot:",response)

if __name__ == "__main__":
    main()
