# 🤖 Voran: Privacy Shield & Automation Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Live-green)
![Platform](https://img.shields.io/badge/Platform-Telegram-blue)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple)

**Voran** is an asynchronous Telegram chatbot designed to demonstrate modern backend architecture, non-blocking I/O operations, and cloud deployment strategies.

It primarily acts as a **Privacy Shield**, allowing users to generate temporary, disposable email addresses to avoid spam and protect their identity during online sign-ups.

## 🚀 Live Demo
You can interact with the bot here: **@voran_crow_bot**
*(Note: As this is a portfolio project on a free tier, it may take 50s to wake up (or more). If not available, it can still be run locally)*

## 🛠️ Tech Stack & Architecture

* **Core:** Python 3.10+
* **Framework:** `python-telegram-bot` (Async implementation)
* **Network:** `httpx` for non-blocking asynchronous API calls
* **Integrations:** GuerrillaMail API (Session-based authentication)
* **Database:** SQLite for user persistence and metrics
* **Infrastructure:** Flask (Health-check server) + Threading
* **Deployment:** Render Cloud (CI/CD via GitHub)

## ✨ Key Features

* **🛡️ Disposable Email System:** Integrates with external REST APIs to generate random email addresses and fetch live inboxes in real-time.
* **🔐 Session State Management:** Manages complex user states (Session IDs/Tokens) using in-memory context data (`context.user_data`), allowing the bot to maintain a "logged in" state across multiple commands.
* **🕵️‍♂️ Advanced API Handling:** Implements custom `User-Agent` headers and redirect handling to bypass bot protection systems (WAFs) on public APIs.
* **💾 Persistence Layer:** Automatically tracks unique users and interaction timestamps in a SQL database.
* **📢 Admin Broadcast System:** Implements Role-Based Access Control (RBAC) allowing admins to send mass notifications to all database users.
* **❤️ Self-Healing:** Runs a parallel Flask server to maintain uptime and handle health checks on ephemeral cloud infrastructure.

## 📂 Project Structure

```text
├── main.py           # Entry point, App Builder, and Handler registration
├── handlers.py       # Business logic (Tempmail, Inbox fetching, API wrappers)
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
    BOT_NAME = 'any_name_you_like'
    TELEGRAM_TOKEN = '5555555:something_like_this'
    MY_CHAT_ID = 55555555 # this is an integer, so no quotes!
```

5.  **Run the Bot:**
```bash
    python main.py
```
