import pandas as pd
import spacy
import re

# Load spaCy's English model for NER
nlp = spacy.load("en_core_web_sm")

# Load the dataset of US cities and states
cities_data = pd.read_csv('us_cities.csv')
cities = set(cities_data['CITY'].str.lower())
states = set(cities_data['STATE_NAME'].str.lower())
state_codes = dict(zip(cities_data['STATE_NAME'].str.lower(), cities_data['STATE_CODE']))

def extract_city_state_ner(address):
    doc = nlp(address)
    extracted_city, extracted_state_code = None, None

    for ent in doc.ents:
        if ent.label_ == "GPE":
            ent_text = ent.text.lower()
            if ent_text in cities and not extracted_city:
                extracted_city = ent_text.title()
            elif ent_text in states and not extracted_state_code:
                extracted_state_code = state_codes[ent_text]

    return extracted_city, extracted_state_code

def extract_city_state(address):
    city, state_code = extract_city_state_ner(address)
    if city and state_code:
        return city, state_code
    
    # Fallback to regex and simple string matching
    match = re.search(r'([A-Za-z\s]+),\s*([A-Z]{2})', address)
    if match:
        city, state_abbr = match.group(1).strip().title(), match.group(2)
        if city.lower() in cities and state_abbr in state_codes.values():
            return city, state_abbr

    return '', ''  # Return empty strings if no match found

# Load your original data
data = pd.read_excel('INSERT_FILE_PATH_HERE')
location_data = data['Location'].fillna('')

extracted_data = location_data.apply(extract_city_state)
data['City'] = extracted_data.apply(lambda x: x[0])
data['State Code'] = extracted_data.apply(lambda x: x[1])

# Save the results
data.to_excel('extracted_city_state_with_codes_ner.xlsx')
