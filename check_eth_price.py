import requests

def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    try:
        response = requests.get(url)
        data = response.json()
        price = data['ethereum']['usd']
        print(f"Current Ethereum price: ${price:,.2f} USD")
    except Exception as e:
        print(f"Error fetching price: {e}")

if __name__ == "__main__":
    get_eth_price() 