import streamlit as st
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from organizer import events, users
from bson.objectid import ObjectId
from streamlit import session_state as ss, chat_message as msg, markdown as md, chat_input as inp

def main():    
    """Main function which runs all other functions"""
    init_chat_history()
    display()
    chat(get_attendee_events('66b1729026d2550a25e8a671'))

def get_response(prompt):
    """Getting response from ChatGPT"""

    load_dotenv(".env")
    api = OpenAI(api_key=getenv("API_KEY"))

    response = api.chat.completions.create(
        messages = [
            *ss.messages, 
            *ss.hidden_messages, 
            {"role":"user","content":prompt}
        ],
        model = "gpt-4o-mini",
        temperature = 0.3
    )
    return response.choices[0].message.content.strip()

def init_chat_history():
    """Initialize chat history"""

    if "messages" not in ss:
        ss.messages = []

    # Initialize messages not seen by the user
    if "hidden_messages" not in ss:
        ss.hidden_messages = []

def display():
    """Configuring display."""

    st.title("Chatbot")
    for message in ss.messages:
        with msg(message["role"]):
            md(message["content"])

def get_attendee_events(user_id):
    if "error_msg" not in ss:
        ss.error_msg = True

    if ss.error_msg:
        user_email = users.find_one({"_id":ObjectId(user_id)}).get("email")
        attendee_events = []

        for event in events.find():
            if user_email in event.get("attendees", []):
                attendee_events.append([event.get("event name"), event.get("organizer")])
        
        if not attendee_events:
            with msg("assistant"):
                md("No events planned for you")
            ss.messages.append({"role":"assistant","content":"No events planned for you"})
            return
        
        list_events = "Here are the list of events planned for you: "
        for nr, event in enumerate(attendee_events, start=1):
            organizer = users.find_one({"_id": ObjectId(event[1])})
            full_name = organizer.get("firstName") + " " + organizer.get("lastName")
            list_events += f"\n{nr}) name: {event[0]}, organizer: {full_name}."

        with msg("assistant"):
            md(list_events) 
            md("Please enter the number of the event that you want the info of.")

        ss.event_nr = inp("Enter the event number here: ")
        if ss.event_nr:
            with msg("user"):
                md(ss.event_nr)
            ss.messages.append({"role":"assistant","content":list_events})
            ss.messages.append({"role":"user","content":ss.event_nr})
        
            try:
                if not 1 <= int(ss.event_nr) <= len(attendee_events):
                    ss.error_msg = f"Error: Number out of range."
                else:
                    ss.error_msg = None
            except Exception as e:
                ss.error_msg = f"Error: {e}"
        
        if ss.error_msg is not True:
            with msg("assistant"):
                md(ss.error_msg)
            ss.messages.append({"role":"assistant","content":ss.error_msg})

        return

    return ss.event_nr
    
def chat(id):
    """Chat with the chatbot and get info about an event"""

    if not id:
        return

    # Giving the event info to the chatbot
    event_info = f"""Here is the information for a event: {events.find_one({"_id":ObjectId(id)})}.
You're a helpful assistant and your job is to provide the info that is asked about the event."""
    
    ss.hidden_messages.append({"role":"system","content":event_info})

    prompt = inp("Type your message here.", key="get-event-info") # React to user input

    if prompt: # If something was typed by the user
        # Display user message in chat message container
        with msg("user"):
            md(prompt)

        ss.messages.append({"role":"user","content":prompt}) # Add message to chat history
        
        # Generate and display ChatGPT output
        response = get_response(prompt)
        with msg("assistant"):
            response = st.empty()
            response.markdown(response)
        
        ss.messages.append({"role":"assistant","content":response}) # Add ChatGPT output to chat history

if __name__ == "__main__":
    main()