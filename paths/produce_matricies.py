import pickle
import urllib.request
import json
from dotenv import load_dotenv
import os
import sys
from . import process_data


def create_matrices():
    """Takes the addresses and creates a distance matrix by calling the Google Maps API."""
    # addresses = ['4925+Oceanside+Blvd+Oceanside+CA',
    #              '420+S+Coast+Hwy+Oceanside+CA',
    #              '34671+Puerto+Pl+Dana+Point+CA',
    #              '883+Sebastopol+Rd+Santa+Rosa+CA',
    #              '7812+Auburn+Blvd+Citrus+Heights+CA',
    #              '159+Paseo+del+Sol+Ave+Lake+Havasu+City+AZ',
    #              '1601+N+Lincoln+Ave+Loveland+CO',
    #              '4351+S+89th+St+Omaha+NE',
    #              '11110+N+Stemmons+Fwy+Dallas+TX',
    #              '3959+US-61+White+Bear+Lake+MN',
    #              '32+Weber+Rd+Central+Square+NY',
    #              '5211+Old+Post+Rd+Charlestown+RI',
    #              '1400+S+Federal+Hwy+Fort+Lauderdale+FL',
    #              '3+Varney+Point+Rd+Gilford+NH']

    # load_dotenv()
    # API_key = os.getenv('API_KEY')

    print("here")
    data = process_data.create_data_model()

    addresses = data['addresses']
    API_key = data['API_KEY']

    max_elements = 100
    num_addresses = len(addresses)
    max_rows = max_elements // num_addresses

    q, r = divmod(num_addresses, max_rows)
    dest_addresses = addresses
    distance_matrix = []
    duration_matrix = []

    for i in range(q):
        origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
        response = send_request(origin_addresses, dest_addresses, API_key)
        print(response, origin_addresses)
        distance_matrix += build_distance_matrix(response)
        duration_matrix += build_duration_matrix(response)

    if r > 0:
        origin_addresses = addresses[q * max_rows: q * max_rows + r]
        response = send_request(origin_addresses, dest_addresses, API_key)
        print(response, origin_addresses)
        distance_matrix += build_distance_matrix(response)
        duration_matrix += build_duration_matrix(response)

    data['distance_matrix'], data['duration_matrix'] = set_depot_to_zero(
        distance_matrix), set_depot_to_zero(duration_matrix)

    return data
    # return distance_matrix, duration_matrix


def send_request(origin_addresses, dest_addresses, API_key):
    """ Build and send request for the given origin and destination addresses."""
    def build_address_str(addresses):
        address_str = ''
        for i in range(len(addresses) - 1):
            address_str += addresses[i] + '|'
        address_str += addresses[-1]
        return address_str

    request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
    origin_address_str = build_address_str(origin_addresses)
    dest_address_str = build_address_str(dest_addresses)
    # print(origin_address_str, dest_address_str)
    # print(API_key)
    # return
    request = request + '&origins=' + origin_address_str + '&destinations=' + \
        dest_address_str + '&key=' + API_key
    jsonResult = urllib.request.urlopen(request).read()
    response = json.loads(jsonResult)

    return response


def build_distance_matrix(response):
    """Takes response from Google Maps API and builds a distance matrix."""
    distance_matrix = []
    # print('responce:', response)
    for row in response['rows']:
        row_list = [row['elements'][j]['distance']['value']
                    for j in range(len(row['elements']))]
        distance_matrix.append(row_list)
    return distance_matrix


def build_duration_matrix(response):
    """Takes response from Google Maps API and builds a duration matrix."""
    duration_matrix = []
    for row in response['rows']:
        row_list = [row['elements'][j]['duration']['value']
                    for j in range(len(row['elements']))]
        duration_matrix.append(row_list)
    return duration_matrix


def set_depot_to_zero(matrix):
    dests = len(matrix[0])

    for i in range(dests):
        matrix[i][0] = 0

    return matrix


def main():
    """Main function."""

    data = create_matrices()

    # print(distance_matrix, duration_matrix)

    # distance_matrix_file = open('distance_matrix.pkl', 'wb')
    # duration_matrix_file = open('duration_matrix.pkl', 'wb')

    # pickle.dump(distance_matrix, distance_matrix_file)
    # pickle.dump(duration_matrix, duration_matrix_file)

    # distance_matrix_file.close()
    # duration_matrix_file.close()

    return data


if __name__ == '__main__':
    main()


# responce: {'destination_addresses': ['2500 Victory Park Ln, Dallas, TX 75219, USA', '400 W Church St, Orlando, FL 32805, USA', '1869 Industrial Dr, Neosho, MO 64850, USA'],
#  'origin_addresses': ['', '125 S Pennsylvania St, Indianapolis, IN 46204, USA', 'STAPLES Center, 1111 S Figueroa St, Los Angeles, CA 90015, USA'],
#   'rows': [{'elements': [{'status': 'NOT_FOUND'}, {'distance': {'text': '962 mi', 'value': 1548789}, 'duration': {'text': '13 hours 50 mins', 'value': 49822}, 'status': 'OK'}, {'distance': {'text': '583 mi', 'value': 938077}, 'duration': {'text': '9 hours 9 mins', 'value': 32934}, 'status': 'OK'}]},
# {'elements': [{'distance': {'text': '901 mi', 'value': 1449230}, 'duration': {'text': '13 hours 6 mins', 'value': 47141}, 'status': 'OK'}, {'distance': {'text': '970 mi', 'value': 1560626}, 'duration': {'text': '14 hours 8 mins', 'value': 50897}, 'status': 'OK'}, {'distance': {'text': '537 mi', 'value': 865005}, 'duration': {'text': '7 hours 55 mins', 'value': 28471}, 'status': 'OK'}]},
# {'elements': [{'distance': {'text': '1,438 mi', 'value': 2313993}, 'duration': {'text': '20 hours 54 mins', 'value': 75211}, 'status': 'OK'}, {'distance': {'text': '2,510 mi', 'value': 4039847}, 'duration': {'text': '1 day 12 hours', 'value': 129860}, 'status': 'OK'}, {'distance': {'text': '1,541 mi', 'value': 2480554}, 'duration': {'text': '22 hours 24 mins', 'value': 80636}, 'status': 'OK'}]}]
# , 'status': 'OK'}
