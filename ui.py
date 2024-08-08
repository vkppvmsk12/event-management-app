import streamlit as st
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from organizer import events, users
from bson.objectid import ObjectId
from pymongo import MongoClient

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
            *st.session_state.messages, 
            *st.session_state.hidden_messages, 
            {"role":"user","content":prompt}
        ],
        model = "gpt-4o-mini",
        temperature = 0.3
    )
    return response.choices[0].message.content.strip()

def init_chat_history():
    """Initialize chat history"""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize messages not seen by the user
    if "hidden_messages" not in st.session_state:
        st.session_state.hidden_messages = []

def display():
    """Configuring display."""

    st.title("Chatbot")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def get_attendee_events(id):
    email = users.find_one({"_id":ObjectId(id)}).get("email")
    attendee_events = []

    for event in events.find():
        if email in event.get("attendees", []):
            attendee_events.append([event.get("event name"), event.get("organizer")])
    
    if not attendee_events:
        with st.chat_message("assistant"):
            st.markdown("No events planned for you.")
            st.session_state.messages.append({"role":"assistant","content":"No events planned for you."})
        return
    
    list_events = "Here are the list of events:"
    for nr, event in enumerate(attendee_events, start=1):
        full_name = users.find_one({"_id":ObjectId(event[1])}).get("firstName") + " " + users.find_one({"_id":ObjectId(event[1])}).get("lastName")
        list_events += (f"\n{nr}) name: {event[0]}, organizer: {full_name}")

    with st.chat_message("assistant"):
        st.markdown(list_events)
        st.markdown("Please enter the number of the event that you want to get info about or press enter to exit.")
    
    st.session_state.messages.append({"role":"assistant","content":list_events})
    st.session_state.messages.append({"role":"assistant","content":"Please enter the number of the event "
                                      "that you want to get info about or press enter to exit."})
    key_nr = 1
    while True:
        with st.chat_message("assistant"):
            event_nr = st.chat_input("Enter the number here.", key=f"enter-event-number {key_nr}")
            if event_nr:
                with st.chat_message("user"):
                    st.markdown(event_nr)
                st.session_state.messages.append({"role":"user","content":event_nr})

        try:
            event_nr = int(event_nr)
        except Exception as e:
            error = f"Error: {str(e)}. Please enter a valid event number."
            with st.chat_message("assistant"):
                st.markdown(error)
            st.session_state.messages.append({"role":"assistant","content":error})
            key_nr += 1
            continue

        if not 1 <= event_nr <= len(attendee_events):
            with st.chat_message("assistant"):
                st.markdown("Event number not in range. Please enter a valid event number.")
            st.session_state.messages.append({
                "role":"assistant",
                "content":"Event number not in range. Please enter a valid event number."
            })
            key_nr += 1
            continue
        break

    st.session_state_messages.append({"role":"user","content":event_nr})

    event_info = events.find_one({"event name":attendee_events[event_nr - 1][0]})
    if event_info:
        return event_info.get("_id")
    return

def chat(id):
    """Chat with the chatbot and get info about an event"""

    if not id:
        return

    # Giving the event info to the chatbot
    event_info = f"""Here is the information for a event: {events.find_one({"_id":ObjectId(id)})}.
You're a helpful assistant and your job is to provide the info that is asked about the event."""
    
    st.session_state.hidden_messages.append({"role":"system","content":event_info})

    prompt = st.chat_input("Type your message here.", key="get-event-info") # React to user input

    if prompt: # If something was typed by the user
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role":"user","content":prompt}) # Add message to chat history
        
        # Generate and display ChatGPT output
        response = get_response(prompt)
        with st.chat_message("assistant"):
            response = st.empty()
            response.markdown(response)
        
        st.session_state.messages.append({"role":"assistant","content":response}) # Add ChatGPT output to chat history

if __name__ == "__main__":
    main()