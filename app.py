import streamlit as st
from openai import OpenAI
import geopandas as gpd
import os

# Function to load countries data
def load_countries():
    data = gpd.read_file(os.path.join('data', 'merged_file.gpkg'))
    data = data[data['field_3'].notna()]
    return sorted(data['field_3'].unique().tolist())

# Initialize session state variables if they don't exist
if 'selected_countries' not in st.session_state:
    st.session_state['selected_countries'] = []
if 'participants' not in st.session_state:
    st.session_state['participants'] = []
    
openai_api_key = os.getenv('openai_api_key')

# Page 1: Initial Setup
def page1():
    with st.sidebar:
        # GPT Selection
        gpt_version = st.radio("Choose GPT Version", ('3.5', '4'))
        
        # Travel Dates
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        # Country Selection
        countries = load_countries()
        selected_countries = st.multiselect('Choose countries', countries, default=st.session_state.selected_countries)
        st.session_state.selected_countries = selected_countries

        # Number of People
        num_people = st.number_input("Number of People", min_value=1, max_value=100)

    # Save settings to session state
    st.session_state['gpt_version'] = gpt_version
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date
    st.session_state['num_people'] = num_people

# Page 2: Participant Details
def page2():
    st.session_state['participants'] = []
    for i in range(st.session_state['num_people']):
        st.subheader(f"Participant {i+1}")
        with st.form(f"participant_{i}"):
            name = st.text_input(f"Name of Participant {i+1}")
            age = st.number_input(f"Age of Participant {i+1}", min_value=0, max_value=120)
            gender = st.selectbox(f"Gender of Participant {i+1}", ['Male', 'Female', 'Other'])
            preference = st.selectbox(f"Vacation Preference of Participant {i+1}", ['Adventure', 'Relax', 'Culture'])
            additional_preferences = st.text_area("Additional Preferences")
            submitted = st.form_submit_button("Save Participant")

            if submitted:
                participant = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'preference': preference,
                    'additional_preferences': additional_preferences
                }
                st.session_state['participants'].append(participant)

# Page 3: Dynamic Chatbot for Travel Planning
def page3():
    st.title("💬 Dynamic Travel Planning Chatbot")

    # Initialize chatbot with specific questions based on context
    if "chat_initialized" not in st.session_state:
        st.session_state.chat_initialized = True
        travel_context = generate_travel_context()
        ask_specific_questions(travel_context)

    # Display chatbot messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # User input for chatbot
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        generate_next_question()

# Function to ask specific questions based on the travel context
def ask_specific_questions(travel_context):
    client = OpenAI(api_key=openai_api_key)
    context_prompt = f"Based on the following travel plan details:\n{travel_context}\nGenerate a series of specific questions to refine the trip planning."
    response = client.chat.completions.create(
        model=get_chatbot_model(),
        messages=[{"role": "system", "content": context_prompt}]
    )
    questions = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": questions})


# Function to generate the travel context for the chatbot
def generate_travel_context():
    context = "As your travel agent, I need to refine our travel plan. Here's the information I have:\n"
    context += f"Travel Dates: {st.session_state['start_date']} to {st.session_state['end_date']}\n"
    context += f"Destinations: {', '.join(st.session_state['selected_countries'])}\n"
    context += "Participants:\n"
    for participant in st.session_state['participants']:
        context += f"- {participant['name']}, {participant['age']} years old, {participant['gender']}, "
        context += f"prefers {participant['preference']}. Additional notes: {participant['additional_preferences']}\n"
    return context

# Function to generate the next question after user input
def generate_next_question():
    client = OpenAI(api_key=openai_api_key)
    next_question_response = client.chat.completions.create(
        model=get_chatbot_model(),
        messages=st.session_state.messages
    )
    next_question = next_question_response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": next_question})

# Helper function to get the correct chatbot model
def get_chatbot_model():
    return "gpt-3.5-turbo" if st.session_state['gpt_version'] == '3.5' else "gpt-4"

# Function to generate the travel context for the chatbot
def generate_travel_context():
    context = "As a travel agent, I need to refine our travel plan. Here's the information I have:\n"
    context += f"Travel Dates: {st.session_state['start_date']} to {st.session_state['end_date']}\n"
    context += f"Destinations: {', '.join(st.session_state['selected_countries'])}\n"
    context += "Participants:\n"
    for participant in st.session_state['participants']:
        context += f"- {participant['name']}, {participant['age']} years old, {participant['gender']}, "
        context += f"prefers {participant['preference']}. Additional notes: {participant['additional_preferences']}\n"
    return context
    
# Page 4: Final Trip Overview
def page4():
    st.title("🌍 Final Trip Overview")

    # Display the final travel plan
    st.subheader("Your Customized Travel Plan:")
    
    # Extracting and displaying the final plan from the chatbot's responses
    plan = extract_final_plan()
    st.write(plan)

# Function to extract the final plan from the chatbot's responses
def extract_final_plan():
    final_plan = ""
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            final_plan += msg["content"] + "\n"
    return final_plan

# Extend the main function
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ('Page 1', 'Page 2', 'Page 3', 'Page 4'))

    if page == 'Page 1':
        page1()
    elif page == 'Page 2':
        page2()
    elif page == 'Page 3':
        page3()
    elif page == 'Page 4':
        page4()

if __name__ == "__main__":
    main()

