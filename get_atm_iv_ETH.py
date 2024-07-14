import requests
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import time
import csv

base_url = 'https://deribit.com/api/v2/public'

# get current index_price of the asset
def get_index_price(index_name: str):
    endpoint = '/get_index_price'
    url = base_url + endpoint
    params = {
        'index_name': index_name
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_data = response.json()
        index_price = response_data['result']['index_price']
        return index_price
    else:
        print(f"Failed to retrieve data: {response.status_code} {response.text}")
        return None
    
# get the order book of the specifized instrument
def get_order_book(instrument_name: str, depth: int):
    endpoint = '/get_order_book'
    url = base_url + endpoint
    params = {
        'instrument_name': instrument_name,
        'depth': depth

    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        print(f"Failed to retrieve data: {response.status_code} {response.text}")
        return None

# get the list of instruments
def get_instruments(currency: str, kind: str, expired: str):
    endpoint = '/get_instruments'
    url = base_url + endpoint
    params = {
        'currency': currency,
        'kind': kind,
        'expired': expired

    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        print(f"Failed to retrieve data: {response.status_code} {response.text}")
        return None

# get all instruments that expire tomorrow
def get_tomorrows_instruments(data: dict):
    instruments = data['result']
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    start_of_tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
    end_of_tomorrow = start_of_tomorrow + datetime.timedelta(days=1)
    
    start_timestamp = int(start_of_tomorrow.timestamp() * 1000)
    end_timestamp = int(end_of_tomorrow.timestamp() * 1000)

    tomorrow_options = []

    for instrument in instruments:
        expiration_timestamp = instrument['expiration_timestamp']
        if start_timestamp <= expiration_timestamp < end_timestamp:
            tomorrow_options.append(instrument)
        elif expiration_timestamp >= end_timestamp:
            break
    
    return tomorrow_options

# get the atm option 
def get_atm_option_iv(instrument_list: list, current_price: int):
    atm_option = min(instrument_list, key=lambda x: abs(x['strike'] - current_price))
    return atm_option

def save_to_csv(timestamp: datetime, atm_iv: int, file_name: str):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, atm_iv])
     
def main():
    csv_file = 'atm_iv_ETH.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'ATM IV'])
    
    while True:

        instruments = get_instruments('ETH', 'option', 'false')

        data = get_tomorrows_instruments(instruments)

        current_price = get_index_price('eth_usd')
        
        atm_option = get_atm_option_iv(data, current_price)

        atm_instrument_name = atm_option['instrument_name']

        atm_order_book = get_order_book(atm_instrument_name,1)
        
        atm_iv = atm_order_book['result']['mark_iv']

        timestamp = datetime.datetime.now().isoformat()
        save_to_csv(timestamp, atm_iv, csv_file)

        print(atm_iv)

        time.sleep(1)

if __name__ == "__main__":
    main()
