import discord 
from discord.ext import commands 
import json

# Wczytaj konfigurację
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config["token"]
WELCOME_CHANNEL_ID = config["welcome_channel"]
PUNISHMENT_CHANNEL_ID = config["punishment_channel"]
POLL_CHANNEL_ID = config["poll_channel"]
CONTEST_CHANNEL_ID = config["contest_channel"]
BANNED_WORDS = config["banned_words"]

# Ustawienia bota
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Słownik przewinień użytkowników
user_warnings = {}

# 🐼 Powitania 🐼
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🐼 Witaj na serwerze!",
            description=f"Cześć {member.mention}! 🎉\n"
                        f"Jesteś teraz częścią **Pandy Trelka🐼❤**!\n"
                        f"Miłej zabawy i pamiętaj, by przestrzegać zasad! 😊",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        await channel.send(embed=embed)

# 🛑 System przewinień 🛑
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for word in BANNED_WORDS:
        if word in message.content.lower():
            user_id = message.author.id

            # Dodaj przewinienie
            if user_id not in user_warnings:
                user_warnings[user_id] = 0
            user_warnings[user_id] += 1

            # Informuj użytkownika
            await message.delete()
            embed = discord.Embed(
                title="⚠️ Niedozwolone słowo!",
                description=f"{message.author.mention}, użyłeś słowa, które jest zakazane! 🐼\n"
                            f"Masz jeszcze **{10 - user_warnings[user_id]} prób** przed karą.",
                color=discord.Color.red()
            )
            await message.channel.send(embed=embed)

            # Jeśli próby się skończą
            if user_warnings[user_id] >= 10:
                punishment_channel = bot.get_channel(PUNISHMENT_CHANNEL_ID)
                if punishment_channel:
                    embed = discord.Embed(
                        title="🚫 Kara za przewinienia!",
                        description=f"{message.author.mention} został ukarany za wielokrotne łamanie zasad serwera! ❌\n"
                                    f"Timeout: **10 minut**.",
                        color=discord.Color.dark_red()
                    )
                    await punishment_channel.send(embed=embed)
                await message.author.timeout_for(duration=60*10)  # Timeout na 10 minut
            return

    await bot.process_commands(message)

# 📊 Ankiety 📊
@bot.command(name="ankieta")
async def poll(ctx, *, question):
    poll_channel = bot.get_channel(POLL_CHANNEL_ID)
    if poll_channel:
        embed = discord.Embed(
            title="📊 Ankieta!",
            description=f"**{question}**\nReaguj poniżej, aby oddać swój głos! 👍/👎",
            color=discord.Color.blue()
        )
        message = await poll_channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    else:
        await ctx.send("Kanał do ankiet nie został poprawnie skonfigurowany.")

# 🎉 Konkursy 🎉
@bot.command(name="konkurs")
async def contest(ctx, *, description):
    contest_channel = bot.get_channel(CONTEST_CHANNEL_ID)
    if contest_channel:
        embed = discord.Embed(
            title="🎉 Konkurs!",
            description=f"{description}\nReaguj 🎉, aby wziąć udział!",
            color=discord.Color.purple()
        )
        embed.set_footer(text="Powodzenia! 🐼❤")
        message = await contest_channel.send(embed=embed)
        await message.add_reaction("🎉")
    else:
        await ctx.send("Kanał do konkursów nie został poprawnie skonfigurowany.")

# Komenda testowa
@bot.command(name="info")
async def info(ctx):
    embed = discord.Embed(
        title="🐼 Bot Pandy Trelka🐼❤",
        description="Cześć! Jestem Twoim botem i pomagam w zarządzaniu serwerem. 🐾\n\n"
                    "- **!ankieta [pytanie]**: Tworzy ankietę z reakcjami 👍/👎.\n"
                    "- **!konkurs [opis konkursu]**: Tworzy post konkursowy z reakcją 🎉.\n"
                    "- Mam także system powitań i przewinień! 🔥",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Stworzony z myślą o Pandy Trelka🐼❤")
    await ctx.send(embed=embed)

# Uruchomienie bota
bot.run(TOKEN)
