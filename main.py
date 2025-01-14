# main.py
import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
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
    "💪 Discipline is doing what you hate to do but doing it like you love it.",
    "🚀 The universe rewards consistent effort, not fleeting passion.",
    "🧠 A focused mind is a powerful weapon.",
    "🔥 Fear is fuel; channel it into power.",
    "💼 Every setback is a setup for a stronger comeback.",
    "🎢 Life's highs and lows build resilience—embrace both.",
    "🥇 Winners don’t wait for opportunities; they create them.",
    "🕰️ Time is your most precious resource; use it wisely.",
    "🛡️ Protect your energy and prioritize your mission.",
    "🌍 You can't change the world if you can't change yourself.",
    "💡 Great ideas are worthless without execution.",
    "🏋️ Strength isn't just physical; it's mental and emotional, too.",
    "🔗 The right connections can multiply your impact exponentially.",
    "📈 Progress requires sacrifice—embrace the grind.",
    "💬 Your words should carry the weight of your actions.",
    "🌱 Growth begins where comfort ends.",
]

# List of image URLs (using placeholder images for demonstration)
IMAGES = [
    "./assets/Screenshot_164.png",
    "./assets/Screenshot_165.png",
    "./assets/Screenshot_166.png",
    "./assets/Screenshot_167.png",
    "./assets/Screenshot_168.png",
    "./assets/Screenshot_169.png",
    "./assets/Screenshot_170.png",
]

# Add these new variables after active_channels definition
available_quotes = []
available_images = []

async def send_periodic_message(context: ContextTypes.DEFAULT_TYPE):
    """Send periodic message to all active channels with random content."""
    global available_quotes, available_images
    
    # Refill the available items if empty
    if not available_quotes:
        available_quotes = QUOTES.copy()
    if not available_images:
        available_images = IMAGES.copy()
    
    for channel_id in active_channels:
        try:
            # Get a random quote and image, then remove them from available lists
            quote = random.choice(available_quotes)
            image_path = random.choice(available_images)
            
            available_quotes.remove(quote)
            available_images.remove(image_path)
            
            # Combine them in a single message with additional emojis
            message = f"✨ Message from the Top G 📣\n\n{quote}\n\n💪 Join the Movement: www.pump.fun 💊💊"
            
            # Send photo with caption
            await context.bot.send_photo(
                chat_id=channel_id,
                photo=image_path,
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