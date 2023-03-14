import discord
import config
from discord.ext import commands
import generator
import character

discord.Permissions.manage_webhooks = True
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='>', intents=intents)

# textchannel -> webhook
webhooks = dict()

character.add_character("teto", "Kasane Teto", "Kasane Teto is an UTAU voice synthesizer with red twin drill hair. She likes baguettes, the country of Norway, and growling in songs. She wants to be an idol very badly but she is not always respected.", "https://s.pacn.ws/1/p/lr/nendoroid-plus-plush-series-50-kasane-teto-391979.4.jpg?v=qmdt0y&quality=72&width=1024&crop=925,967")
character.add_character("flower", "Flower", "Flower's Persona: Flower is a Vocaloid voice synthesizer program with white and purple hair. She is very androgynous and often mistaken for a boy, which she enjoys. She types in all lower case at the start of sentences, uses internet lingo, and is sometimes very rude and emotionally cold. She likes chainsmoking cigarettes and has a very raspy voice when she sings. She is a tomboyish rock girl with an almost anarchic personality and doesn't care what other people think of her.", "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/6d13578c-377b-4261-bd09-01a2f6367d2a/da35ecn-eef54679-4dd3-4fa0-b0c0-6fb05df8e1a9.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzZkMTM1NzhjLTM3N2ItNDI2MS1iZDA5LTAxYTJmNjM2N2QyYVwvZGEzNWVjbi1lZWY1NDY3OS00ZGQzLTRmYTAtYjBjMC02ZmIwNWRmOGUxYTkucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.dcqGmosarX22CFTbtP4mFAVK2pNujxDWb65a677LPq4")

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def genconfighelp(ctx):
    await ctx.send(", ".join(generator.params.keys()))


@bot.command()
async def writeconfig(ctx, key, value):
    try:
        if key in generator.params:
            if key == 'do_sample' or key == 'early_stopping':
                value = bool(value)
            elif key in ['temperature', 'top_p', 'typical_p', 'repetition_penalty', 'penalty_alpha']:
                value = float(value)
            else:
                value = int(value)
            generator.params[key] = value
            await ctx.send(f'Set {key} to value {value}')
        else:
            await ctx.send(f'Unknown config {key}')
    except:
        await ctx.send(f'Invalid value for {key}')


@bot.command()
async def readconfig(ctx, key):
    if key in generator.params:
        await ctx.send(f'{generator.params[key]}')
    else:
        await ctx.send(f'Unknown config {key}')


@bot.command()
async def addchar(ctx, id, name, prompt, avatar_url=None):
    character.add_character(id, name, prompt, avatar_url)


@bot.command()
async def listchars(ctx):
    msg = ''
    for i, c in character.charDict.items():
        msg += f'{i}:{c.name}, '
    await ctx.send(msg)

async def get_webhook_for_channel(channel):
    if channel not in webhooks:
        cwebhooks = await channel.webhooks()
        for w in cwebhooks:
            if w.name == "Debot Characters":
                return w
        webhooks[channel] = await channel.create_webhook(name="Debot Characters")
    return webhooks[channel]


# prompt = directly prompt character with text
@bot.command()
async def prompt(ctx, id, *prompt):
    if id not in character.charDict:
        return

    char = character.charDict[id]
    webhook = await get_webhook_for_channel(ctx.channel)
    msg = await generator.prompt_webui(char, ctx.message)
    await webhook.send(content = msg, username = char.name, avatar_url = char.avatar_url)


# reply = bring character into conversation starting from where you are,
# ignores message with .reply in it
@bot.command()
async def reply(ctx, id):
    if id not in character.charDict:
        return

    char = character.charDict[id]
    msg = await generator.prompt_webui(char, ctx.message)
    await ctx.send(msg)


async def on_ready():
    await bot.change_presence(
        activity=discord.Game(ame="CERTIFIED VOCALOID EXPERT"))

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
