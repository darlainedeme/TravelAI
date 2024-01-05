# =============================================================================
# # -*- coding: utf-8 -*-
# """
# Created on Wed Aug 23 16:49:07 2023
# 
# @author: darla
# """
# 
# API_KEY = '33720238D99A442FB8B2BC4A1A642240'
# 
# import requests
# 
# # Define the API endpoint and your key
# BASE_URL = "https://api.tripadvisor.com/api/partner/2.0/"
# 
# # Query for Paris (You might need to adjust this according to API documentation)
# LOCATION = "Paris"
# endpoint = f"{BASE_URL}location_search/{LOCATION}"
# 
# headers = {
#     "X-TripAdvisor-API-Key": API_KEY
# }
# 
# response = requests.get(endpoint, headers=headers)
# 
# # Extract top 10 locations from the response
# if response.status_code == 200:
#     data = response.json()
#     locations = data.get('data', [])[:10]
#     for location in locations:
#         print(location.get('name', 'Unknown Location'))
# else:
#     print(f"Error {response.status_code}: {response.text}")
# 
# 
# =============================================================================

# Import the libraries.
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Extract the HTML and create a BeautifulSoup object.
url = 'https://www.tripadvisor.com/Hotel_Review-g187147-d230525-Reviews-Hotel_Duette_Paris-Paris_Ile_de_France.html?spAttributionToken=MjE4MjI3NTM'

user_agent = ({'User-Agent':
			'Chrome',
			'Accept-Language': 'en-US, en;q=0.5'})

def get_page_contents(url):
    page = requests.get(url, headers = user_agent)
    return BeautifulSoup(page.text, 'html.parser')

soup = get_page_contents(url)

# Find and extract the data elements.
hotels = []
for name in soup.findAll('div',{'class':'listing_title'}):
    hotels.append(name.text.strip())

ratings = []
for rating in soup.findAll('a',{'class':'ui_bubble_rating'}):
    ratings.append(rating['alt'])  

reviews = []
for review in soup.findAll('a',{'class':'review_count'}):
    reviews.append(review.text.strip())

prices = []
for p in soup.findAll('div',{'class':'price-wrap'}):
    prices.append(p.text.replace('₹','').strip())  

# Create the dictionary.
dict = {'Hotel Names':hotels,'Ratings':ratings,'Number of Reviews':reviews,'Prices':prices}

# Create the dataframe.
hawaii = pd.DataFrame.from_dict(dict)
hawaii.head(10)

# Convert dataframe to CSV file.
hawaii.to_csv('hotels.csv', index=False, header=True)