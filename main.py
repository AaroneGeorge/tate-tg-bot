# main.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import asyncio
import random

# Load environment variables
load_dotenv()

# Store channel IDs where the bot should send repeated messages
active_channels = set()

# List of quotes with emojis
QUOTES = [
    "💭 Success comes to those who embrace discomfort and push through.",
    "⚡ The most important part of any plan is taking action.",
    "🌟 Your mind must be stronger than your emotions.",
    "🎯 Arrogance breeds complacency, and complacency breeds failure.",
    "💪 Discipline is doing what you hate to do but doing it like you love it."
]

# List of image URLs (using placeholder images for demonstration)
IMAGES = [
    "https://us-tuna-sounds-images.voicemod.net/c5af4866-4419-430a-8cc7-5b13c769efcb-1664233443548.jpg",  # Replace with your actual image URLs
    "https://us-tuna-sounds-images.voicemod.net/86744f05-b1bb-446e-b9e3-7073e091a0eb-1692997370694.jpg",
    "https://static.wikia.nocookie.net/memeverse-scaling/images/f/fb/Andrew_Tate.jpeg/revision/latest?cb=20221126210254"
]

async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE):
    """Send periodic message to all active channels with random content."""
    for channel_id in active_channels:
        try:
            # Get a random quote and image
            quote = random.choice(QUOTES)
            image_url = random.choice(IMAGES)
            
            # Combine them in a single message with additional emojis
            message = f"✨ Daily Inspiration ✨\n\n{quote}\n\n🌈 Keep shining! 🌈"
            
            # Send photo with caption
            await context.bot.send_photo(
                chat_id=channel_id,
                photo=image_url,
                caption=message
            )
        except Exception as e:
            print(f"Error sending to channel {channel_id}: {e}")

async def handle_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message in channel, including commands"""
    try:
        if update.channel_post:
            chat_id = update.channel_post.chat.id
            text = update.channel_post.text if update.channel_post.text else ""
            
            print(f"Received channel post: {text} in {chat_id}")  # Debug print
            
            if text.startswith('/start'):
                if chat_id not in active_channels:
                    active_channels.add(chat_id)
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text='Starting periodic messages every 5 seconds with random quotes and images! 🚀'
                    )
            elif text.startswith('/stop'):
                if chat_id in active_channels:
                    active_channels.remove(chat_id)
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text='Stopped periodic messages! 👋'
                    )
    except Exception as e:
        print(f"Error in handle_channel_command: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command in private chats and groups"""
    try:
        if update.message and update.message.chat.type in ['private', 'group', 'supergroup']:
            chat_id = update.message.chat.id
            if chat_id not in active_channels:
                active_channels.add(chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Starting periodic messages every 5 seconds with random quotes and images! 🚀'
                )
    except Exception as e:
        print(f"Error in start command: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stop command in private chats and groups"""
    try:
        if update.message and update.message.chat.type in ['private', 'group', 'supergroup']:
            chat_id = update.message.chat.id
            if chat_id in active_channels:
                active_channels.remove(chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Stopped periodic messages! 👋'
                )
    except Exception as e:
        print(f"Error in stop command: {e}")

async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bot being added to or removed from a channel/group."""
    try:
        chat_id = update.my_chat_member.chat.id
        
        if (update.my_chat_member.new_chat_member.status in ['administrator', 'member'] and 
            update.my_chat_member.old_chat_member.status == 'left'):
            active_channels.add(chat_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text='Hello! I was just added. I will start sending random quotes and images every 5 seconds! 🎉'
            )
        elif update.my_chat_member.new_chat_member.status == 'left':
            if chat_id in active_channels:
                active_channels.remove(chat_id)
    except Exception as e:
        print(f"Error in my_chat_member: {e}")

def main():
    try:
        # Create the Application with job queue enabled
        application = (
            ApplicationBuilder()
            .token(os.getenv('TELEGRAM_BOT_TOKEN'))
            .build()
        )
        
        # Add job queue
        job_queue = application.job_queue
        
        # Schedule the periodic message task
        if job_queue:
            job_queue.run_repeating(send_periodic_message, interval=5, first=1)
        else:
            print("Error: Job queue is not available!")
            return
        
        # Add command handlers for private chats and groups
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("stop", stop))
        
        # Add channel post handler
        application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_command))
        
        # Add handler for bot being added to or removed from channels/groups
        from telegram.ext import ChatMemberHandler
        application.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
        
        print("Bot started successfully!")  # Debug print
        
        # Run the bot until the user presses Ctrl-C
        application.run_polling()
        
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == '__main__':
    main()