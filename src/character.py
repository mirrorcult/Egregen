# TODO sqlite
charDict = dict()


class Character:
    name = ""
    prompt = ""
    avatar_url = None

    def __init__(self, name, prompt, avatar_url):
        self.name = name
        self.prompt = prompt
        self.avatar_url = avatar_url


def add_character(id, name, prompt, avatar_url=None):
    char = Character(name, prompt, avatar_url)
    charDict[id] = char
