Here’s a comprehensive `README.md` for the entire project, including pre-settings, code modifications, deployment, and usage instructions.

---

# Telegram Budget Bot

This repository contains a Telegram bot written in Python for tracking income and expenses in Google Sheets. The bot allows users to record income and expenses with customizable types and categories, which are then stored in a Google Sheets document with monthly summaries.

## Features

- **Income and Expense Tracking**: Log income and expenses with categories and descriptions.
- **Google Sheets Integration**: Automatically updates a Google Sheet with separate monthly tabs and calculates monthly summaries.
- **User-Friendly Commands**: Use Telegram commands to log data directly from the bot.
- **Automatic Monthly Tabs**: Automatically generates new tabs for each month.

## Prerequisites

To run this project, ensure you have:

1. **Python 3.10+** installed locally.
2. **Google Cloud Project** with the Sheets API enabled.
3. **Telegram Bot Token** created with [BotFather](https://core.telegram.org/bots#botfather).
4. **Google Sheets API Credentials JSON file** for authentication.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram-budget-bot.git
cd telegram-budget-bot
```

### 2. Google Cloud Configuration

#### Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project for this bot.

#### Step 2: Enable the Sheets and Drive APIs

1. In your project, go to **APIs & Services** > **Library**.
2. Enable both **Google Sheets API** and **Google Drive API**.

#### Step 3: Create and Download API Credentials

1. Go to **APIs & Services** > **Credentials**.
2. Select **Create Credentials** > **Service Account Key**.
3. Choose **JSON** as the key type, then download the credentials file.
4. Save this JSON file in your project folder and name it `credentials.json`.

### 3. Telegram Bot Token

1. **Create a new bot** with [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
2. Note the `API token` provided.
3. This token will be needed in the code to authenticate the bot with Telegram.

### 4. Code Modifications

There are a few areas in the code where you’ll need to insert your specific information:

1. **API Credentials Path**: In `main.py`, update the path to your `credentials.json` file:

   ```python
   CREDENTIALS_FILE = 'credentials.json'  # Update this path if needed
   ```

2. **Telegram Bot Token**: Replace `<YOUR_TELEGRAM_TOKEN>` in the code with your actual bot token:

   ```python
   TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'
   ```

3. **Google Sheets Document**: The bot will open or create a Google Sheet named "budget". Make sure you share this sheet with the email from your Google Cloud service account credentials.

### 5. Code Overview

The project structure is as follows:

- `main.py` – Contains the main bot code.
- `requirements.txt` – Lists all the necessary Python dependencies.
- `app.yaml` – Used for deployment to Google App Engine (Flexible Environment).
- `Dockerfile` – Specifies the Docker configuration for deployment on Google App Engine.

In `main.py`, there are several main functions:

1. **`start_income` and `start_outcome`**: Entry points for the bot's `/income` and `/outcome` commands.
2. **`income_name`, `income_amount`, `income_type`**: Handle each input step for income entries.
3. **`outcome_name`, `outcome_amount`, `outcome_type`**: Handle each input step for outcome entries.
4. **`get_monthly_sheet`**: Ensures there is a tab for the current month in Google Sheets.
5. **`update_row_counter`**: Updates the row counters to keep entries continuous.

The bot uses Google Sheets for data storage and requires monthly sheet creation, conditional formatting, and calculations for monthly totals.

### 6. Running the Bot Locally

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Bot**:

   ```bash
   python main.py
   ```

3. **Interacting with the Bot**: On Telegram, find your bot and use commands like `/income` or `/outcome` to start logging transactions.

### 7. Deploying to Google App Engine (Flexible Environment)

The bot can be deployed to Google Cloud Platform with Google App Engine in Flexible Environment using a custom Docker container.

#### Step 1: Configure `app.yaml` and `Dockerfile`

- **Dockerfile**:

  ```dockerfile
  FROM python:3.12-slim

  WORKDIR /app
  COPY . /app

  RUN pip install --upgrade pip
  RUN pip install -r requirements.txt

  ENV TELEGRAM_TOKEN="<your_telegram_token>"
  ENV GOOGLE_CREDENTIALS="<your_json_content_as_env>"

  CMD ["python", "main.py"]
  ```

- **app.yaml**:

  ```yaml
  runtime: custom
  env: flex

  manual_scaling:
    instances: 1

  resources:
    cpu: 1
    memory_gb: 0.5
  ```

#### Step 2: Deploy the App

Run the following commands in your terminal:

```bash
gcloud app deploy
gcloud app browse
```

After deploying, your bot should now be live.

### 8. Usage

1. Start the bot by sending the `/start` command on Telegram.
2. Use commands like `income` and `outcome` to log transactions.
3. The bot will save entries to Google Sheets, organize data by month, and calculate monthly summaries.

### 9. Troubleshooting

- **Bot Not Responding**: Check the Google App Engine logs for errors.
- **Credentials Issues**: Verify the `GOOGLE_CREDENTIALS` environment variable and ensure the service account has access to the Google Sheet.
- **Environment Variables**: Double-check that `TELEGRAM_TOKEN` and `GOOGLE_CREDENTIALS` are set correctly in the environment.

---

This README should provide a clear setup path and usage instructions for deploying and running your Telegram bot for budget tracking!