
import streamlit as st
from api.openai_api import get_response_from_gpt
from utils.itinerary_generator import generate_itinerary
from utils.data_fetcher import fetch_travel_data

st.title("Trip Planner")

user_input = st.text_input("Chat with our Trip Bot:")

if user_input:
    response = get_response_from_gpt(user_input)
    st.write(response)
    user_preferences = {
        'destination': 'City A',
        'days': 3,
        'activities': ['museum', 'food', 'historic sites']
    }
    itinerary = generate_itinerary(user_preferences)
    st.subheader("Your Itinerary")
    for day, activities in itinerary.items():
        st.write(day)
        for activity in activities:
            st.write(activity)
    