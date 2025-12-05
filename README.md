# 🤖 Voran: Automated Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Live-green)
![Platform](https://img.shields.io/badge/Platform-Telegram-blue)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple)

**Voran** is an asynchronous Telegram chatbot designed to demonstrate modern backend architecture, non-blocking I/O operations, and cloud deployment strategies. It acts as a cryptocurrency monitor and an automated broadcast system.

## 🚀 Live Demo
You can interact with the bot here: **@voran_crow_bot**
*(Note: As this is a portfolio project on a free tier, it may take up to 50s to wake up)*

## 🛠️ Tech Stack & Architecture

* **Core:** Python 3.10+
* **Framework:** `python-telegram-bot` (Async implementation)
* **Network:** `httpx` for non-blocking asynchronous API calls (CoinGecko)
* **Database:** SQLite for user persistence and session tracking
* **Infrastructure:** Flask (Health-check server) + Threading
* **Deployment:** Render Cloud (CI/CD via GitHub)

## ✨ Key Features

* **Real-Time Data:** Fetches live cryptocurrency prices via external REST APIs using asynchronous requests.
* **Persistence Layer:** Automatically tracks unique users and timestamps in a SQL database.
* **Admin Broadcast System:** Implements Role-Based Access Control (RBAC) allowing admins to send mass notifications to all database users.
* **Automated Jobs:** Uses `JobQueue` for scheduled background tasks and alerts.
* **Self-Healing:** Runs a parallel Flask server to maintain uptime and handle health checks on ephemeral cloud infrastructure.

## 📂 Project Structure

```text
├── main.py           # Entry point, App Builder, and JobQueue setup
├── handlers.py       # Business logic (Commands, Messages, API calls)
├── db.py             # Database interface (SQLite connection & Schema)
├── keep_alive.py     # Flask server for uptime management
├── check_db.py       # Utility script to inspect database state
└── Procfile          # Deployment instructions for Render
```

## ⚙️ Local Installation
If you want to run this bot locally:

1.  **Clone the repository:**

```bash
git clone [https://github.com/YOUR_USERNAME/voran_telegram_bot.git](https://github.com/YOUR_USERNAME/voran_telegram_bot.git)
cd voran_telegram_bot
```

2.  **Create a Virtual Environment:**
```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
```

3.  **Install Dependencies:**
```bash
    pip install -r requirements.txt
```

4.  **Configure Environment Create a .env file in the root directory:**
```env
    TELEGRAM_TOKEN=your_telegram_bot_token
    MY_CHAT_ID=your_personal_telegram_id
    BOT_NAME=Voran
```

5.  **Run the Bot:**
```bash
    python main.py
```

## 🧠 What I Learned
**Building Voran helped me transition from scripting to engineering:**

* **Async vs. Sync:** Understanding why time.sleep() kills a bot and why asyncio.sleep() is necessary for concurrency.

* **State Management:** Moving from memory-based storage to persistent SQL databases.

* **DevOps:** Managing environment variables, secrets, and deploying a background worker as a web service using a "Keep-Alive" strategy.
