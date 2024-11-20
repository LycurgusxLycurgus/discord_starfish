# bot.py

import discord
import asyncio
import json
import logging
import random
from discord.ext import commands
import openai
from config import Config
from prompts import SYSTEM_PROMPTS, TOPICS
from discord.ext import tasks
from datetime import datetime, time
from memory_processor import process_daily_memories
from memory_decision import select_relevant_memories
from story_circle_manager import get_current_context, update_story_circle, progress_narrative

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')

# Initialize OpenAI
openai.api_key = Config.OPENAI_API_KEY
openai.api_base = "https://glhf.chat/api/openai/v1"

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.guilds = True  # Enable basic guild intent
intents.guild_messages = True  # Enable guild messages

bot = commands.Bot(command_prefix='!', intents=intents)

# Load length formats
with open('src/length_formats.json', 'r') as f:
    length_formats = json.load(f)['formats']

# In-memory conversation history
user_conversations = {}
MAX_MEMORY = 2

def add_to_conversation_history(user_id, message, is_bot):
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({
        'content': message,
        'is_bot': is_bot,
        'timestamp': asyncio.get_event_loop().time()
    })
    
    # Keep only the last MAX_MEMORY messages
    if len(user_conversations[user_id]) > MAX_MEMORY:
        user_conversations[user_id].pop(0)

def get_conversation_context(user_id):
    history = user_conversations.get(user_id, [])
    return '\n'.join([
        f"{'Assistant' if msg['is_bot'] else 'User'}: {msg['content']}"
        for msg in history
    ])

def get_random_format():
    random_format = random.choice(length_formats)['format']
    logger.info(f"Selected random format: {random_format}")
    return random_format

async def generate_content(user_message, user_id, username):
    try:
        # First, gather all required data
        random_format = get_random_format()
        conversation_context = get_conversation_context(user_id)
        user_identifier = f"@{username}" if username else f"User#{user_id}"
        
        # Get relevant memories for this conversation - add await here
        memories = await select_relevant_memories(user_identifier, user_message)
        
        # Get current story circle context
        narrative_context = get_current_context()
        
        # Now that we have all data, log it
        logger.info("=== Message Generation Details ===")
        logger.info(f"Conversation Context: {conversation_context}")
        logger.info(f"User Identifier: {user_identifier}")
        logger.info(f"User Message: {user_message}")
        logger.info(f"Random Format: {random_format}")
        logger.info(f"Memories: {memories}")
        logger.info(f"Current Event: {narrative_context['current_event']}")
        logger.info(f"Inner Dialogue: {narrative_context['current_inner_dialogue']}")
        logger.info("===============================")
        
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPTS["style1"] + "\n."
            },
            {
                "role": "user",
                "content": f"""Previous conversation:
{conversation_context}

New message from {user_identifier}: "{user_message}"

Let this emotion shape your response: {random_format}. Remember to respond like a text message using text-speak and replacing 'r' with 'fw' and 'l' with 'w'. And do not use emojis. Keep the conversation context in mind when responding; keep your memories in mind when responding: {memories}. Your character has an arc, if it seems relevant to your response, mention it, where the current event is: {narrative_context['current_event']} and the inner dialogue to such an event is: {narrative_context['current_inner_dialogue']}."""
            }
        ]
        
        response = await openai.ChatCompletion.acreate(
            model=Config.AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=70
        )
        
        content = response.choices[0].message['content']
        
        # Remove any @ mentions from the start of the response
        if content.startswith('@'):
            content = content.split(' ', 1)[1] if ' ' in content else ''
        
        # Add to conversation history
        add_to_conversation_history(user_id, user_message, False)
        add_to_conversation_history(user_id, content, True)
        
        return content
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise e

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} - {bot.user.id}')
    logger.info(f'Bot mention string: <@{bot.user.id}>')
    process_memories.start()  # Start the memory processing task
    update_narrative.start()  # Start the narrative update task
    print('Discord AI Bot is online!')

@bot.event
async def on_message(message):
    # Add debug logging
    logger.debug(f'Received message: {message.content}')
    
    if message.author == bot.user:
        return  # Prevent bot from responding to its own messages
    
    # Update mention detection to use Discord's built-in mention system
    if bot.user in message.mentions:
        try:
            logger.info(f'Bot was mentioned in message: {message.content}')
            
            user_id = message.author.id
            username = message.author.name
            # Remove the mention using Discord's proper mention format
            user_message = message.content.replace(f'<@{bot.user.id}>', '').strip()
            
            response = await generate_content(user_message, user_id, username)
            
            await message.reply(response)
            logger.info('Bot replied to mention successfully')
        except Exception as e:
            logger.error(f'Error handling mention: {e}')
            await message.reply("Sorry, I couldn't process your request at the moment.")
    
    await bot.process_commands(message)

@bot.command(name='chatid')
async def chatid(ctx):
    """Utility command to get the chat ID."""
    chat_id = ctx.guild.id if ctx.guild else ctx.author.id
    await ctx.send(f'Chat ID: {chat_id}')

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'Error in event {event}: {args} {kwargs}')
    if event == 'on_message':
        await args[0].reply("An unexpected error occurred while processing your message.")

@tasks.loop(time=time(hour=23, minute=55))  # Run at 23:55 every day
async def process_memories():
    try:
        logger.info("Starting nightly memory processing...")
        await process_daily_memories(user_conversations)
        # Clear the day's conversations after processing
        user_conversations.clear()
        logger.info("Nightly memory processing completed")
    except Exception as e:
        logger.error(f"Error in nightly memory processing: {e}")

@tasks.loop(hours=6)
async def update_narrative():
    try:
        logger.info("Progressing story circle narrative...")
        await progress_narrative()  # This will either move to next event or generate new content
        logger.info("Story circle progression completed")
    except Exception as e:
        logger.error(f"Error in story circle progression: {e}")

# Startup message
if __name__ == "__main__":
    logger.info('Discord AI Bot started! Ready to respond to mentions...')
    bot.run(Config.DISCORD_BOT_TOKEN)
