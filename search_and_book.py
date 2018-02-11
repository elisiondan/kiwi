'''Usage:
  get_flights.py (--date=<date>) (--from=<flyFrom>) (--to=<flyTo>)
                 [--one-way | --return=<nights>] [--cheapest | --fastest]
                 [--bags=<bags>]

  Options:
    -h --help           Show help screen.
    --date=<date>       date in yyyy-mm-dd format (required)
    --from=<flyFrom>    IATA code of airport of departure (required)
    --to=<flyTo>        IATA code of airport of arrival (required)

    --one-way   Book a one-way flight (optional) [default: True]
    --return=<nights>    Book a return flight (optional)

    --cheapest  Sort flights by price (optional) [default: True]
    --fastest   Sort flights by duration (optional) [default: False]

    --bags=<bags>      Number of booked flight. (optional) [default: 0]
'''

import requests
import datetime
import json
from docopt import docopt


''' Dependencies
    pip install docopt==0.6.2
'''


# Passenger's booking details
# Hardcoded for the demo purposes
passengers = [
    {
        'title': 'Mr',
        'firstName': 'John',
        'lastName': 'Doe',
        'documentID': '111',
        'email': 'test@test.com',
        'birthday': '1980-01-01'
    }
]


def get_flights(payload):
    ''' Get flights information

    @param {dict} payload - Flight details for API get request
    @return {dict} flights.text - Returns JSON-like flights details

    '''

    flights = requests.get('https://api.skypicker.com/flights', params=payload)

    if (flights.status_code != 200):
        print('Error while connecting to API. '
              'Response code: {}'.format(flights.status_code)
              )
        return

    return json.loads(flights.text)


def prepare_payload(search_options):
    ''' Prepare header for get request

    @param {dict} search_options - Search details coming from CLI arguemnts
    @returns {dict} payload - a formatted header for get request

    '''

    dateFrom = convert_date(search_options['--date'], '%Y-%m-%d', 'object')

    typeFlight = 'round' if search_options['--return'] is not None else 'oneway'
    payload = {
        'v': 3,
        'dateFrom': convert_date(dateFrom, '%d/%m/%Y', 'string'),
        'dateTo': convert_date(dateFrom, '%d/%m/%Y', 'string'),
        'flyFrom': search_options['--from'],
        'to': search_options['--to'],
        'typeFlight': typeFlight,
        'adults': 1,
        'limit': 1,
        'sort': 'price' if search_options['--cheapest'] is True else 'duration'
    }

    if typeFlight == 'round':
        payload['daysInDestinationFrom'] = search_options['--return']
        payload['daysInDestinationTo'] = payload['daysInDestinationFrom']

    return payload


def convert_date(date, format, type):
    ''' Converts string date to object type and vice-versa

    @param {object | string} date - date as object or string
    @param {string} format - formatting of the date param
    @param {type} type - desired return date type (string or object)
    @returns {string | object} date as string or object
    '''

    if type == 'object':
        return datetime.datetime.strptime(date, format)
    elif type == 'string':
        return datetime.datetime.strftime(date, format)
    else:
        print('Unsupported convertsion')
        return


def book_flight(search_options, flight_details, passengers):
    ''' Books a single flight

    @param {dict} search_options - Search details coming from CLI arguemnts
    @param {dict} flight_details - All data about flight satisfying look up conditions
    @param {dict} passengers - Details about booking passengers
    @returns {dict} response - if post request was successful, returns booking confirmation and code
    '''

    flight_data = flight_details['data'][0]

    payload = {
        'currency': flight_details['currency'],
        'passengers': passengers,
        'bags': search_options['--bags'],
        'booking_token': flight_data['booking_token']
    }

    return json.loads(requests.post('http://128.199.48.38:8080/booking',
                      json=payload).text)


def search_and_book(search_options):
    ''' Handles search and booking process

    @param {dict} search_options - Search details coming from CLI arguemnts
    '''

    payload = prepare_payload(search_options)
    flight_details = get_flights(payload)
    booking = book_flight(search_options, flight_details, passengers)

    if (booking['status'] == 'confirmed'):
        currency = flight_details['currency']
        price = flight_details['data'][0]['price']
        flyFrom = flight_details['data'][0]['cityFrom']
        flyTo = flight_details['data'][0]['cityTo']

        print(currency)
        print('Flight succesfully booked')
        print('Price:', price, currency)
        print('Departure:', flyFrom)
        print('Arrival:', flyTo)
        print('Your booking number is {}'.format(booking['pnr']))
    else:
        print('Could not book the flight')


if __name__ == '__main__':
    ''' Get CLI arguments and go through the booking process
    '''
    search_options = docopt(__doc__, version='Kiwi Sky Picker 1.0')
    search_and_book(search_options)
