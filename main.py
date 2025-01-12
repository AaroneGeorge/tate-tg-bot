# main.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import asyncio

# Load environment variables
load_dotenv()

# Store channel IDs where the bot should send repeated messages
active_channels = set()

async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE):
    """Send periodic message to all active channels."""
    for channel_id in active_channels:
        try:
            await context.bot.send_message(
                chat_id=channel_id,
                text='Hello World!'
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
                        text='Starting periodic messages every 5 seconds!'
                    )
            elif text.startswith('/stop'):
                if chat_id in active_channels:
                    active_channels.remove(chat_id)
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text='Stopped periodic messages!'
                    )
    except Exception as e:
        print(f"Error in handle_channel_command: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start command in private chats and groups"""
    try:
        # Only handle private chats and groups here
        if update.message and update.message.chat.type in ['private', 'group', 'supergroup']:
            chat_id = update.message.chat.id
            if chat_id not in active_channels:
                active_channels.add(chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Starting periodic messages every 5 seconds!'
                )
    except Exception as e:
        print(f"Error in start command: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stop command in private chats and groups"""
    try:
        # Only handle private chats and groups here
        if update.message and update.message.chat.type in ['private', 'group', 'supergroup']:
            chat_id = update.message.chat.id
            if chat_id in active_channels:
                active_channels.remove(chat_id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text='Stopped periodic messages!'
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
                text='Hello! I was just added. I will start sending messages every 5 seconds!'
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