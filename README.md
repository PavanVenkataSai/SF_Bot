# Salesforce AI Chatbot 🤖

An intelligent Python-based chatbot that integrates with Salesforce to answer user queries in natural language by dynamically generating SOQL queries using AI.

## 🧠 Features

- 🗣️ Conversational interface for Salesforce interaction
- 🧾 AI-powered SOQL query generation using OpenAI
- 🔐 Secure authentication with Salesforce and AWS
- ⚡ Fast and reliable performance

## 🗂️ Project Structure

salesforce-ai-chatbot/ 
├── bot.py # Main bot logic and orchestration 
├── sf_query_extractor.py # Module to construct Salesforce SOQL queries using LLM 
├── main.py # Entry point to run the bot 
├── .env # Environment variables
└── requirements.txt # Dependencies (optional)


## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/salesforce-ai-chatbot.git
cd salesforce-ai-chatbot
```

### 2. Set Up Virtual Environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Create a .env File
Add your credentials:

```bash
# Salesforce Credentials
SF_USERNAME="your_username"
SF_PASSWORD="your_password"
SF_SECURITY_TOKEN="your_token"
SF_INSTANCE_URL="https://login.salesforce.com"
SF_CLIENT_ID="your_client_id"
SF_CLIENT_SECRET="your_client_secret"

# AWS and OpenAI
AWS_SECRET_ACCESS_KEY="your_aws_secret"
AWS_ACCESS_KEY_ID="your_aws_access"
openai_key="your_openai_key"
⚠️ Do not commit your .env file. It contains sensitive information.
```
### 5. Run the Bot
```bash
python main.py
```
##🛡️ Security Notes
All sensitive data is stored in .env and excluded via .gitignore

You should rotate your secrets regularly
