import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from google import genai
from aiohttp import web

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user.name}")

@bot.command(name="ask")
async def ask(ctx, *, prompt: str):
    async with ctx.typing():
        try:
            response = ai_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            reply_text = response.text
            
            if len(reply_text) > 2000:
                for chunk in [reply_text[i:i+1900] for i in range(0, len(reply_text), 1900)]:
                    await ctx.send(chunk)
            else:
                await ctx.reply(reply_text)

        except Exception as e:
            await ctx.send(f"Error processing request: {str(e)}")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

@bot.event
async def setup_hook():
    bot.loop.create_task(run_web_server())

bot.run(DISCORD_TOKEN)
