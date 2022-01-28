import numpy as np
import pandas as pd
import requests
import multiprocessing
import random
import time
from functools import partial


def seniority(job_title):
    """
    Return seniority of job title

    :param job_title: Input Job title
    """

    experience = {'junior': ['beginner', 'entry', 'junior', 'jr'],
                  'senior': ['senior', 'lead', 'sr', 'master']}

    # Return Junior or Senior
    for exp, words in experience.items():
        for w in words:
            if w in job_title.lower():
                return exp.title()

    # Returns Regular if above doesn't apply
    not_regular = experience['junior'] + experience['senior']
    for word in not_regular:
        if word not in job_title.lower():
            return 'Regular'


def get_geocode(address):
    """
    Grab the geocode for any street address
    """

    print(f'Grabbing Geocode for {address} ... ')

    geo_api = "https://nominatim.openstreetmap.org/search"
    params = {'q': address, 'format': 'jsonv2'}
    response = requests.get(geo_api, params=params).json()
    output = {'lat': response[0]['lat'], 'lng': response[0]['lon']}

    return output


def cleanup(raw_data):
    """
    The whole dirty da_jobs table gets cleaned up here.
    Yes. This function is too big.

    Also the operations here are straight from a Jupyter Notebook.
    """

    # Add Experience column
    raw_data['Experience'] = raw_data['Job Title'].map(seniority)

    # Add Salary ranges
    raw_data[['Salary Lower', 'Salary Upper']] = raw_data['Salary Estimate'].str\
        .split('-', expand=True)\
        .replace('[a-zA-Z$.\(\)]', '', regex=True)

    raw_data['Salary Lower'], raw_data['Salary Upper'] = \
        pd.to_numeric(raw_data['Salary Lower'], errors='coerce') * 1000,\
        pd.to_numeric(raw_data['Salary Upper'], errors='coerce') * 1000

    # Add company size ranges
    raw_data[['Company Size Min', 'Company Size Max']] = raw_data['Size'].str\
        .replace('[a-zA-Z+]', '', regex=True)\
        .str.split(expand=True)

    raw_data['Company Size Min'], raw_data['Company Size Max'] = \
        pd.to_numeric(raw_data['Company Size Min'], errors='coerce'),\
        pd.to_numeric(raw_data['Company Size Max'], errors='coerce')

    # Fix \n and ratings in Company names
    regex_pattern = r'(\n)[0-9.]{3}$'
    raw_data['Company Name'] = \
        raw_data['Company Name'].str.replace(regex_pattern, '', regex=True)

    # Add latitude and longitude for geocoding
    api_time0 = time.time()
    location_data = raw_data[['Location']]
    print(f"About to do {location_data.shape[0]} API requests now. Sorry my dear API...")

    raw_data[['Latitude', 'Longitude']] = \
        location_data.apply(get_geocode, axis=1, result_type='expand')

    print(f"Did {location_data.shape[0]} API requests now")
    print(f'It took {time.time() - api_time0} seconds')

    # Get rid off the garbage
    # Drop some columns with irrelevant information and garbage raw_data
    raw_data = raw_data.drop(columns=['Unnamed: 0', 'Easy Apply', 'Competitors',
                            'Headquarters', 'Founded', 'Type of ownership',
                            'Sector', 'Revenue', 'Industry', 'Salary Estimate', 'Size'])
    # Reoder the columns
    raw_data = raw_data[['Job Title', 'Experience', 'Salary Lower', 'Salary Upper',
                'Job Description', 'Company Name', 'Rating', 'Location',
                'Latitude', 'Longitude', 'Company Size Min', 'Company Size Max']]

    # Replace garbage values with numps nan's
    raw_data = raw_data\
        .replace(-1, np.nan)\
        .replace('-1', np.nan)\
        .replace('Unknown', np.nan)

    # Drop rows with garbage company names and job descriptions
    raw_data.loc[raw_data['Job Description'].str.len() < 10, 'Job Description'] = np.nan
    raw_data.loc[raw_data['Company Name'].str.len() < 2, 'Company Name'] = np.nan # 1 company is deleted

    # Let's impute the missign ratings with the mean
    mean_rating = raw_data['Rating'].mean().round(1)
    raw_data['Rating'] = raw_data['Rating'].replace(np.nan, mean_rating)


    # Let's also impute the missing max company size values for those 10000+ employee companies
    raw_data['Company Size Max'] = raw_data['Company Size Max'].mask(pd.isnull, raw_data['Company Size Min'])

    # Allright, min is less than max but the values seem quite high for the company size mean.
    # Let's continue under the assumption that this is what we want for now.
    mean_min_company_size = raw_data['Company Size Min'].mean().round(0)
    mean_max_company_size = raw_data['Company Size Max'].mean().round(0)

    raw_data['Company Size Min'] = raw_data['Company Size Min'].replace(np.nan, mean_min_company_size)
    raw_data['Company Size Max'] = raw_data['Company Size Max'].replace(np.nan, mean_max_company_size)

    # Finishing touches
    raw_data = raw_data.dropna()
    raw_data = raw_data.convert_dtypes()

    # Let's also reorder the table to see job-related information first and company information second.

    raw_data = raw_data[['Job Title', 'Experience', 'Salary Lower', 'Salary Upper',
                'Job Description', 'Company Name', 'Rating', 'Location',
                'Latitude', 'Longitude', 'Company Size Min', 'Company Size Max']]

    return raw_data
