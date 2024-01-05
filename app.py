import os
import geopandas as gpd
import streamlit as st
from openai import OpenAI

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def page1():
    st.sidebar.title("Page 1: Setup")
    # Choose GPT Version
    gpt_version = st.sidebar.radio("Select GPT Version", ("gpt-3.5", "gpt-4"))

    # Travel Dates
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    # Select Countries
    data = gpd.read_file(os.path.join('data', 'merged_file.gpkg'))
    data = data[data['field_3'].notna()]
    countries = sorted(data['field_3'].unique().tolist())
    selected_countries = st.sidebar.multiselect('Choose Countries', countries)
    st.session_state.selected_countries = selected_countries

    # Number of People
    num_people = st.sidebar.number_input("Number of People", min_value=1, step=1)
    st.session_state.num_people = num_people

    return gpt_version

def page2():
    st.title("Page 2: Participant Details")
    participant_data = []
    for i in range(st.session_state.num_people):
        with st.expander(f"Participant {i+1}"):
            name = st.text_input(f"Name of Participant {i+1}")
            age = st.number_input(f"Age of Participant {i+1}", min_value=0, max_value=100)
            gender = st.radio(f"Gender of Participant {i+1}", ["Male", "Female", "Other"])
            preferences = st.multiselect(f"Preferences of Participant {i+1}", ["Adventure", "Relax", "Culture"])
            more_info = st.text_area(f"More about Participant {i+1}")
            participant_data.append({"name": name, "age": age, "gender": gender, "preferences": preferences, "more_info": more_info})
    st.session_state.participant_data = participant_data

def page3(gpt_version):
    st.title("💬 Chatbot")
    st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        if not openai.api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI(api_key=openai.api_key)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        response = client.chat.completions.create(model=gpt_version + "-turbo", messages=st.session_state.messages)
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

def main():
    st.set_page_config(page_title="Travel Plan Assistant", layout="wide")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

    pages = {
        "Setup Travel Plan": page1,
        "Input Participant Details": page2,
        "Chatbot Interaction": page3
    }

    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio("Choose a page", list(pages.keys()))

    if selected_page == "Setup Travel Plan":
        gpt_version = pages[selected_page]()
    elif selected_page == "Input Participant Details":
        pages[selected_page]()
    else:
        pages[selected_page](gpt_version)

if __name__ == "__main__":
    main()
