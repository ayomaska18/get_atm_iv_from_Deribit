from web3 import Web3
import json
import math
import time
import csv
import datetime


def convert_sqrt_price_x96(sqrt_price_x96: int):
    price = (sqrt_price_x96 / (2 ** 96)) ** 2
    return price

def calculate_reserves(liquidity, sqrt_price_x96, tick):
    # Convert sqrtPriceX96 to a decimal
    sqrt_price = sqrt_price_x96 / (2**96)
    
    # Calculate the tick spacing (3 for this WBTC/ETH 0.3% fee tier pool)
    tick_spacing = 60
    
    # Calculate the lower and upper ticks of the current range
    lower_tick = math.floor(tick / tick_spacing) * tick_spacing
    upper_tick = lower_tick + tick_spacing
    
    # Calculate square root of prices for lower and upper ticks
    sqrt_price_lower = 1.0001 ** (lower_tick / 2)
    sqrt_price_upper = 1.0001 ** (upper_tick / 2)
    
    # Calculate the amounts of each token
    if sqrt_price <= sqrt_price_lower:
        # All liquidity is in token0 (WBTC)
        amount0 = liquidity * ((1 / sqrt_price_lower) - (1 / sqrt_price_upper))
        amount1 = 0
    elif sqrt_price < sqrt_price_upper:
        # Liquidity is in both tokens
        amount0 = liquidity * ((1 / sqrt_price) - (1 / sqrt_price_upper))
        amount1 = liquidity * (sqrt_price - sqrt_price_lower)
    else:
        # All liquidity is in token1 (ETH)
        amount0 = 0
        amount1 = liquidity * (sqrt_price_upper - sqrt_price_lower)
    
    # Adjust for token decimals
    amount0_adjusted = amount0 / 1e8  # WBTC has 8 decimals
    amount1_adjusted = amount1 / 1e18  # ETH has 18 decimals
    
    return amount0_adjusted, amount1_adjusted

def save_to_csv(timestamp: datetime, atm_iv: int, file_name: str):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, atm_iv])

# rpc url
url = 'https://mainnet.infura.io/v3/f86474993783479baa1c55febc6a1274'
w3 = Web3(Web3.HTTPProvider(url))

# erc20 abi
erc20_abi = json.loads('''
[
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
''')

# uniswap v3 pool abi
uniswap_v3_pool_abi = json.loads('''
[
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {
                "internalType": "uint160",
                "name": "sqrtPriceX96",
                "type": "uint160"
            },
            {
                "internalType": "int24",
                "name": "tick",
                "type": "int24"
            },
            {
                "internalType": "uint16",
                "name": "observationIndex",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "observationCardinality",
                "type": "uint16"
            },
            {
                "internalType": "uint16",
                "name": "observationCardinalityNext",
                "type": "uint16"
            },
            {
                "internalType": "uint8",
                "name": "feeProtocol",
                "type": "uint8"
            },
            {
                "internalType": "bool",
                "name": "unlocked",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [
            {
                "internalType": "uint128",
                "name": "",
                "type": "uint128"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal0X128",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal1X128",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
''')

# pool address
pool_address = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'

# define pool contract
pool_contract = w3.eth.contract(address=pool_address, abi=uniswap_v3_pool_abi)


def main():

    csv_file = 'uniswap_data_ratio/USDCETH_price_ratio.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Price Ratio'])
    
    while True:
        try:
            slot0 = pool_contract.functions.slot0().call()

            sqrtPriceX96, tick, observationIndex, observationCardinality, observationCardinalityNext, feeProtocol, unlocked = slot0

            price = convert_sqrt_price_x96(sqrtPriceX96)

            price = 1 / (price / 1e12)

            timestamp = datetime.datetime.now().isoformat()
            save_to_csv(timestamp, price, csv_file)

            print(f"Price Ratio: {price}")

            time.sleep(5)

        except Exception as e:
            print(f"Exception occured: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()

