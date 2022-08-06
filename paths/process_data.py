from . import query_data
import os
from dotenv import load_dotenv


def create_data_model():

    trucks, demands = query_data.query_data()

    data = {}

    data['addresses'] = []
    data['demands'] = []

    for demand in demands:

        address = demand[1]
        load = demand[2]

        print("Load: " + str(load))

        data['addresses'].append(process_address(address))
        data['demands'].append(load)

    print("demands", data['demands'])

    data['num_vehicles'] = len(trucks)
    data['vehicle_capacities'] = []

    for truck in trucks:
        capacity = truck[1]

        data['vehicle_capacities'].append(capacity)

    print("capacities:", data['vehicle_capacities'])

    data['depot'] = 0

    load_dotenv()
    data['API_KEY'] = os.getenv('API_KEY')

    return data


def process_address(address):

    formated_address = ''

    split_address = address.split(' ')
    stripped_address = []
    for word in split_address:
        stripped_address.append(word.strip(","))

    for word in stripped_address:
        if not is_state_code(word):
            formated_address += "+"
            formated_address += word
        else:
            formated_address += word
            break

    return formated_address


def is_state_code(word):

    states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
    }

    if word in states:
        return True
    else:
        return False
