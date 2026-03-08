import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from openai import OpenAI

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store conversation history per chat
conversation_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your AI chatbot powered by ChatGPT. Send me a message or use /help for more info.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    /image <prompt> - Generate an image based on the prompt
    /analyze - Analyze the current conversation
    /clear - Clear conversation history
    Just send a message to chat with me!
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message and respond with ChatGPT."""
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # Initialize history if not exists
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    # Add user message to history
    conversation_history[chat_id].append({"role": "user", "content": user_message})

    # Keep only last 10 messages to avoid token limit
    if len(conversation_history[chat_id]) > 20:
        conversation_history[chat_id] = conversation_history[chat_id][-20:]

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history[chat_id],
            max_tokens=150,  # Keep answers brief
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content.strip()

        # Add bot reply to history
        conversation_history[chat_id].append({"role": "assistant", "content": bot_reply})

        await update.message.reply_text(bot_reply)
    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        await update.message.reply_text("Sorry, I couldn't process your message right now.")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate an image based on the prompt."""
    if not context.args:
        await update.message.reply_text("Please provide a prompt for the image. Usage: /image <prompt>")
        return

    prompt = ' '.join(context.args)
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        await update.message.reply_photo(photo=image_url, caption=f"Image for: {prompt}")
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        await update.message.reply_text("Sorry, I couldn't generate the image right now.")

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyze the current conversation."""
    chat_id = update.effective_chat.id
    if chat_id not in conversation_history or not conversation_history[chat_id]:
        await update.message.reply_text("No conversation history to analyze.")
        return

    # Create a summary prompt
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[chat_id]])
    analysis_prompt = f"Analyze this conversation and provide a brief summary, including any local jokes or cultural references:\n\n{history_text}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=200
        )
        analysis = response.choices[0].message.content.strip()
        await update.message.reply_text(f"Conversation Analysis:\n{analysis}")
    except Exception as e:
        logger.error(f"Error analyzing conversation: {e}")
        await update.message.reply_text("Sorry, I couldn't analyze the conversation right now.")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the conversation history."""
    chat_id = update.effective_chat.id
    if chat_id in conversation_history:
        conversation_history[chat_id] = []
    await update.message.reply_text("Conversation history cleared.")

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        logger.error("Please set TELEGRAM_BOT_TOKEN and OPENAI_API_KEY in .env file")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("image", image_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
