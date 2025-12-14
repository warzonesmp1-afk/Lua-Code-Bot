import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- 1. Load Environment Variables (.env) - THE ROBUST FIX ---
# FIX: Explicitly define the path to the .env file for Pydroid 3 compatibility.
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("DEBUG: .env file found and successfully loaded.")
else:
    print(f"DEBUG: .env file NOT FOUND at expected path: {env_path}")


# --- 2. Configuration & Initialization ---

# 1. Manually load both keys from the environment variables (where dotenv placed them)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# --- IMPORTANT VERIFICATION ---
# Halt if the Gemini key is missing.
if not GEMINI_API_KEY:
    print("FATAL ERROR: GEMINI_API_KEY is missing or empty.")
    print("Action: Check your .env file syntax and ensure the key is correctly regenerated.")
    raise ValueError("GEMINI_API_KEY is missing or empty. Please populate your .env file.")

# 2. Initialize the Gemini Client by manually passing the loaded key.
try:
    # This is part of the Pydroid fix: explicitly passing the key value.
    GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"FATAL ERROR: Could not initialize Gemini Client. Error: {e}")
    raise e

MODEL_NAME = 'gemini-2.5-flash' 
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 3. Bot Events ---

@bot.event
async def on_ready():
    """Confirms the bot is logged in and ready."""
    print(f'🤖 Lua Code Bot is ready and logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Generating Lua | !code"))

# --- 4. The Lua Code Generation Command (FINAL SYNTAX FIX APPLIED) ---

@bot.command(name='code', help='Generates ONLY Lua code. Usage: !code <prompt>')
async def generate_code(ctx, *, prompt: str):
    await ctx.defer()
    
    # 1. System Instruction: Define the AI's role and language restriction.
    system_instruction = (
        "You are an expert Lua software engineer. "
        "Your only task is to write clean, concise, and functional **Lua code** "
        "based on the user's request. **You must only output the code**, "
        "wrapping it in the appropriate Markdown code block (specifically: ```lua ... ```). "
        "Do not write code in any other language or include any explanatory text outside the code block."
    )

    full_prompt = f"User Request: {prompt}"

    try:
        # 2. Configure the API call
        config = types.GenerateContentConfig(
            # FINAL FIX: Pass the system instruction here
            system_instruction=system_instruction,
            temperature=0.2 
        )

        # 3. Call the Gemini API with ONLY the user role
        response = GEMINI_CLIENT.models.generate_content(
            model=MODEL_NAME,
            # FINAL FIX: Only include the 'user' content here
            contents=[
                types.Content(role="user", parts=[types.Part(text=full_prompt)]),
            ],
            config=config
        )
        
        if response.text:
            await ctx.send(f"**Generated Lua Code for:** `{prompt}`\n\n{response.text}")
        else:
            await ctx.send("The AI generated an empty response. Please try a different prompt.")

    except Exception as e:
        # Log the error to your terminal for diagnosis
        print(f"Gemini API Error: {e}")
        await ctx.send(f"❌ **API Error:** A problem occurred during code generation. Check the terminal for details.")

# ... (All of the code for the generate_code function should end here) ...
# The code below should have NO INDENTATION (be at the very far left)

# --- 5. Run the Bot ---
if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not found. Bot cannot connect.")
    else:
        # Start the bot
        try:
            bot.run(DISCORD_TOKEN)
        except Exception as e:
            # Catch errors that happen during login, like token issues or connection errors
            print(f"FATAL RUNTIME ERROR: The bot failed to start! Reason: {e}")
