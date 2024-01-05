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
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "assistant", "content": "How can I help you?"}]


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

# Page 3: Chatbot Conversation
def page3():
    st.title("💬 Chatbot")
    st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
    
    # Chatbot messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # User input for chatbot
    if prompt := st.chat_input():
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        # Select the model based on user choice
        model = "gpt-3.5-turbo" if st.session_state['gpt_version'] == '3.5' else "gpt-4"

        client = OpenAI(api_key=openai_api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(model=model, messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

# Page 4: Proposed Trip Overview
def page4():
    st.title("🌍 Proposed Trip Overview")

    # Display collected information
    st.subheader("Travel Details")
    st.write(f"📅 Dates: {st.session_state['start_date']} to {st.session_state['end_date']}")
    st.write(f"🌐 Countries: {', '.join(st.session_state['selected_countries'])}")
    st.write(f"👥 Number of Participants: {st.session_state['num_people']}")

    st.subheader("Participants")
    for i, participant in enumerate(st.session_state['participants'], 1):
        st.markdown(f"**Participant {i}:**")
        st.markdown(f"- Name: {participant['name']}")
        st.markdown(f"- Age: {participant['age']}")
        st.markdown(f"- Gender: {participant['gender']}")
        st.markdown(f"- Preference: {participant['preference']}")
        st.markdown(f"- Additional Preferences: {participant['additional_preferences']}")

    # Generate a travel plan using GPT model
    if st.button("Generate Travel Plan"):
        if not openai_api_key:
            st.error("OpenAI API key is missing.")
            return
        
        # Prepare the prompt for the GPT model
        prompt = generate_trip_overview_prompt()

        # Make an API call to GPT
        client = OpenAI(api_key=openai_api_key)
        model = "gpt-3.5-turbo" if st.session_state['gpt_version'] == '3.5' else "gpt-4"
        response = client.chat.completions.create(model=model, messages=[{"role": "system", "content": prompt}])
        trip_plan = response.choices[0].message.content

        st.subheader("Generated Travel Plan")
        st.write(trip_plan)

# Function to generate the prompt for the trip overview
def generate_trip_overview_prompt():
    prompt = "Create a travel plan for the following group:\n"
    prompt += f"Dates: {st.session_state['start_date']} to {st.session_state['end_date']}\n"
    prompt += f"Countries: {', '.join(st.session_state['selected_countries'])}\n"
    prompt += "Participants:\n"
    for participant in st.session_state['participants']:
        prompt += f"- Name: {participant['name']}, Age: {participant['age']}, "
        prompt += f"Gender: {participant['gender']}, Preferences: {participant['preference']}, "
        prompt += f"Additional Preferences: {participant['additional_preferences']}\n"
    return prompt

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

