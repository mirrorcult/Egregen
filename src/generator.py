from character import Character, charDict
from datetime import timedelta
import config
import requests
import logging

server = "127.0.0.1"

params = {
    'max_new_tokens': 100,
    'do_sample': True,
    'temperature': 0.8,
    'top_p': 0.9,
    'typical_p': 1,
    'repetition_penalty': 1.1,
    'top_k': 5,
    'min_length': 0,
    'no_repeat_ngram_size': 0,
    'num_beams': 1,
    'penalty_alpha': 0,
    'length_penalty': 1,
    'early_stopping': False,
}


async def prompt_webui(character: Character, discord_message):
    cont = await build_dialogue_context(discord_message)
    prompt = build_pygmalion_prompt(character, cont)

    response = requests.post(f"http://{server}:7860/run/textgen", json={
        "data": [
            prompt,
            params['max_new_tokens'],
            params['do_sample'],
            params['temperature'],
            params['top_p'],
            params['typical_p'],
            params['repetition_penalty'],
            params['top_k'],
            params['min_length'],
            params['no_repeat_ngram_size'],
            params['num_beams'],
            params['penalty_alpha'],
            params['length_penalty'],
            params['early_stopping'],
        ]
    }).json()

    logging.info(prompt)
    logging.info(response["data"])

    # cut out prompt & any generations after what we want
    return response["data"][0].replace(prompt, '').split('\n')[0]


def build_pygmalion_prompt(character: Character, history: str):
    return f"{character.name}'s Persona: {character.prompt}\n<START>\n{history}\n{character.name}: "


async def build_dialogue_context(message):
    cont = []
    startTime = message.created_at
    async for message in message.channel.history(limit=100):
        content = message.content

        if (content.startswith("<RESETCONV>")):
            break
        elif (message.author.name == "Home Debot"):
            continue
        elif content.startswith(">prompt") and len(content) > 8:
            # first word after `.prompt ` (char id)
            content = content[8:]
            id = content.split()[0]
            if id not in charDict:
                continue
            # .prompt teto Hi there -> Hi there
            content = content[len(id):]
        elif content.startswith(">") or content.startswith("<"):
            continue
        time = message.created_at
        if (startTime - timedelta(minutes=10) > time):
            break

        # captioning
        captions = ""
        if config.BLIP_MODULE:
            for a in message.attachments:
                if "image" in a.content_type:
                    pass
                    # captions += f" attached image: {blip_caption(a.proxy_url)}, "
            for e in message.embeds:
                if e.image is not None:
                    pass
                    # captions += f" embedded image: {blip_caption(e.image.url)}, "
        #cont.append(f"{message.author.name}: {content}{captions}")
        cont.append(f"You: {content}{captions}")

    return "\n".join(cont[::-1])
