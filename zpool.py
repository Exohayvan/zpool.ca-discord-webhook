import requests
import time
import json
from collections import deque
from datetime import datetime, timedelta

def load_config():
    """Load configuration from a JSON file."""
    with open('config.json', 'r') as file:
        return json.load(file)

def fetch_wallet_stats(wallet_address):
    """Fetch wallet statistics from the zpool API."""
    api_url = f"https://www.zpool.ca/api/walletEX?address={wallet_address}"
    response = requests.get(api_url)
    return response.json()

def fetch_coin_to_usd(coin):
    """Fetch the current COIN to USD exchange rate."""
    api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(api_url)
    price = response.json().get(coin, {}).get('usd', 0)
    return price

def format_hashrate(value):
    """Format hashrate values with appropriate suffixes."""
    if value < 1e3:
        return f"{value:.2f} H/s"
    elif value < 1e6:
        return f"{value / 1e3:.2f} kH/s"
    elif value < 1e9:
        return f"{value / 1e6:.2f} MH/s"
    elif value < 1e12:
        return f"{value / 1e9:.2f} GH/s"
    else:
        return f"{value / 1e12:.2f} TH/s"

def aggregate_hashrates(miners):
    """Aggregate hashrates by miner version and algorithm, and count the workers."""
    hashrate_dict = {}
    worker_count = {}
    for miner in miners:
        if float(miner['accepted']) > 0:  # Check if hashrate is greater than 0
            key = f"{miner['algo']}"
            if key in hashrate_dict:
                hashrate_dict[key] += float(miner['accepted'])
                worker_count[key] += 1
            else:
                hashrate_dict[key] = float(miner['accepted'])
                worker_count[key] = 1
    return hashrate_dict, worker_count

def save_hashrate_history(history):
    """Save the hashrate history to a JSON file, converting deques to lists."""
    history_for_json = {key: list(value) for key, value in history.items()}
    with open('hashrate_history.json', 'w') as file:
        json.dump(history_for_json, file)

def load_hashrate_history():
    """Load hashrate history from a JSON file, converting lists back to deques."""
    try:
        with open('hashrate_history.json', 'r') as file:
            loaded_history = json.load(file)
        return {key: deque(value, maxlen=144) for key, value in loaded_history.items()}
    except (IOError, ValueError):
        return {}

def update_hashrate_history(history, key, value):
    """Update the hashrate history with timestamped values and remove entries older than 24 hours."""
    if key not in history:
        history[key] = deque(maxlen=144)
    timestamp = datetime.now()
    history[key].append({'timestamp': timestamp.isoformat(), 'hashrate': value})
    
    # Remove entries older than 24 hours
    cutoff_time = datetime.now() - timedelta(hours=24)
    while history[key] and datetime.fromisoformat(history[key][0]['timestamp']) < cutoff_time:
        history[key].popleft()

def calculate_average_hashrate(history, key):
    """Calculate the average hashrate from the history."""
    if key in history and len(history[key]) > 0:
        total = sum(item['hashrate'] for item in history[key])
        return total / len(history[key])
    return 0

def send_to_webhook(webhook_url, stats, aggregated_hashrates, worker_counts, hashrate_history, coin_to_usd, ticker):
    """Send formatted data to a Discord webhook, including USD prices."""
    balance_usd = float(stats['balance']) * coin_to_usd
    unsold_usd = float(stats['unsold']) * coin_to_usd
    paid24h_usd = float(stats['paid24h']) * coin_to_usd
    paidtotal_usd = float(stats['paidtotal']) * coin_to_usd

    content = (
        f"**Wallet Balance Update:**\n"
        f"Balance: {stats['balance']} {ticker} (${balance_usd:.2f})\n"
        f"Pending (Unsold): {stats['unsold']} {ticker} (${unsold_usd:.2f})\n"
        f"Earned last 24h: {stats['paid24h']} {ticker} (${paid24h_usd:.2f})\n"
        f"Total Earned: {stats['paidtotal']} {ticker} (${paidtotal_usd:.2f})\n\n"
        f"**Worker Stats:**"
    )
    for key, hashrate in aggregated_hashrates.items():
        algo = key
        workers = worker_counts[key]
        current_hashrate = format_hashrate(hashrate)
        average_hashrate = format_hashrate(calculate_average_hashrate(hashrate_history, key))
        content += f"\n- {algo} - {workers} workers\n*Current: {current_hashrate} | 24hr Avg: {average_hashrate}*"

    data = {"content": content, "username": "Zpool Stats"}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=data, headers=headers)
    return response.status_code, response.text

if __name__ == "__main__":
    configurations = load_config()
    hashrate_histories = {config['wallet_address']: load_hashrate_history() for config in configurations}

    try:
        while True:
            for config in configurations:
                coin_to_usd = fetch_coin_to_usd(config['coin'])
                wallet_stats = fetch_wallet_stats(config['wallet_address'])
                aggregated_hashrates, worker_counts = aggregate_hashrates(wallet_stats['miners'])
                
                for key, hashrate in aggregated_hashrates.items():
                    update_hashrate_history(hashrate_histories[config['wallet_address']], key, hashrate)
                
                result, response_text = send_to_webhook(config['webhook_url'], wallet_stats, aggregated_hashrates, worker_counts, hashrate_histories[config['wallet_address']], coin_to_usd, config['ticker'])
                save_hashrate_history(hashrate_histories[config['wallet_address']])
                
                print(f"Data sent to webhook for {config['wallet_address']}. Status code:", result)
                print("Response text:", response_text)

            time.sleep(600)  # Pause for 10 minutes before next cycle
    except KeyboardInterrupt:
        for wallet in hashrate_histories:
            save_hashrate_history(hashrate_histories[wallet])
