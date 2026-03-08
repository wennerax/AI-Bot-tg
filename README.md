# AI-Bot-tg

An AI-powered Telegram chatbot based on ChatGPT, capable of:

- Engaging in conversations with brief responses
- Generating images using DALL-E
- Analyzing chat conversations
- Understanding and responding to local jokes and cultural references

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/botfather) and get the token.
2. Get an OpenAI API key from [OpenAI](https://platform.openai.com/).
3. Copy `.env.example` to `.env` and fill in your tokens.
4. Install dependencies: `pip install -r requirements.txt`
5. Run the bot: `python index.py`

## Branches

- `main`: Core bot functionality
- `image-generation`: Enhancements for image creation features
- `chat-analysis`: Improvements to conversation analysis
- `local-jokes`: Better handling of local/cultural jokes
- `brief-responses`: Optimizations for keeping responses concise

## Commands

- `/start`: Start the bot
- `/help`: Show help
- `/image <prompt>`: Generate an image
- `/analyze`: Analyze the conversation
- `/clear`: Clear conversation history

## Usage

Send messages to chat with the bot. It maintains conversation history per chat for context.