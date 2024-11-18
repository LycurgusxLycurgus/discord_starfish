# Discord AI Bot

A Discord bot that responds to tagged questions using an AI API, similar to the existing Telegram bot.

## Features

- Listens for tagged messages and responds using OpenAI's GPT.
- Maintains conversation history for context-aware responses.
- Supports multiple response formats.
- Error handling and logging.

## Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/YourUsername/discord_ai_bot.git
   cd discord_ai_bot
   ```

2. **Create a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add Bot to Discord Server:**
   
   Use the following invitation link to add the bot to your Discord server:
   [Invite Discord AI Bot](https://discord.com/oauth2/authorize?client_id=1308084069929582674&permissions=67584&integration_type=0&scope=bot+applications.commands)

5. **Configure Environment Variables:**

   - Rename `.env.example` to `.env` and fill in your credentials.

6. **Run the Bot:**

   ```bash
   python src/bot.py
   ```

## Configuration

- **.env:** Contains sensitive information like API keys and tokens.
- **prompts.py:** Defines system prompts for different conversation styles.
- **length_formats.json:** Specifies various response formats.

## Deployment

Instructions for deploying the bot on platforms like Heroku, AWS, or others.

## Contributing

Guidelines for contributing to the project.

## License

Specify the license under which the project is distributed.
