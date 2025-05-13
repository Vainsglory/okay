import discord
import json
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# Load token from environment variable (more secure than config.json)
TOKEN = os.getenv('DISCORD_TOKEN')  # Set in Koyeb/Fly.io dashboard
BANNED_ROLE_ID = 1371571043302379521

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_member_update(before, after):
    if len(before.roles) < len(after.roles):
        new_roles = [role for role in after.roles if role not in before.roles]
        for role in new_roles:
            if role.id == BANNED_ROLE_ID:
                try:
                    await after.send(
                        "⚠️ You were automatically banned for selecting "
                        f"the restricted role: {role.name}\n\n"
                        "Contact server staff if this was a mistake."
                    )
                except discord.HTTPException:
                    pass
                
                await after.ban(reason=f"Auto-ban: Selected {role.name} role")
                print(f"Banned {after.name} (ID: {after.id}) in {after.guild.name}")

# Flask web server for uptime monitoring
app = Flask(__name__)

@app.route('/')
def home():
    return "Auto-ban bot is operational!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    # Start Flask in a thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True  # Ensures thread exits when main program does
    flask_thread.start()
    
    # Start Discord bot
    bot.run(TOKEN)
