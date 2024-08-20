
# zpool.ca Stats Webhook

## Overview
This Python script is designed for cryptocurrency miners who need to track and monitor their mining statistics across multiple wallets. It fetches wallet stats from zpool.ca, converts mined coins to USD based on live exchange rates, aggregates the data, updates the hashrate history, and sends all relevant information to specified Discord webhooks. This tool is useful for miners who want to keep a close eye on multiple mining operations and receive regular updates directly via Discord.

## Features
- **Multi-Wallet Management**: Handles multiple wallet addresses and coins, allowing for broad monitoring across different cryptocurrencies.
- **Real-Time Data**: Fetches live data from mining zpool and converts cryptocurrency balances to USD. (Every 10 mins, can be adjusted)
- **Automatic Updates**: Sends periodic updates to a Discord webhook, formatted with current mining statistics.
- **Data Persistence**: Maintains a history of hashrates to calculate and compare daily averages.
- **Configurable**: All settings are managed through a `config.json` file, making it easy to add or remove wallets without altering the script code.

## Prerequisites
Before you want to run this script yourself, ensure you have the following:
- Python 3.6 or higher
- `requests` library installed in your Python environment

## Setup
To set up the script, checkout the release [here](https://github.com/Exohayvan/zpool.ca-discord-webhook/releases/tag/Initial) or follow these steps to run the script on your own:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Create and Activate a Virtual Environment** (optional but recommended):
   For Windows:
   ```bash
   python -m venv venv
   .\\venv\\Scripts\\activate
   ```
   For Unix or MacOS:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install requests
   ```

## Configuration
Edit the `config.json` file to include your wallet addresses, webhook URLs, and other relevant details. Here is an example of what the configuration might look like:

```json
[
    {
        "wallet_address": "YourWalletAddress1",
        "webhook_url": "https://discord.com/api/webhooks/YourWebhookURL1",
        "coin": "ravencoin",
        "ticker": "RVN"
    },
    {
        "wallet_address": "YourWalletAddress2",
        "webhook_url": "https://discord.com/api/webhooks/YourWebhookURL2",
        "coin": "bitcoin",
        "ticker": "BTC"
    }
]
```

## Usage
To use this script, simply run it in your terminal or command prompt:

```bash
python zpool.py
```

The script will continue running and send updates every 10 minutes. To stop the script, press `Ctrl+C` in your terminal.

## Contributing
Contributions to this project are welcome! You can contribute by:
- Reporting a bug
- Submitting a fix
- Proposing new features
- Improving documentation

If you want to contribute, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

## License
Distributed under the MIT License. See `LICENSE` for more information.


## Acknowledgements
- zpool.ca for providing the mining pool API
- CoinGecko for providing the crypto to fiat conversion rates API
- Discord for enabling webhook integrations