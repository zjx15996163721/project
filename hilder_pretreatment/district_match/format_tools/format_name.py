import re

__all__ = ['format_name_address']

# todo
specific_symbol = [".", "|", "•", "、", ";", "；", ",", "，", "·", " "]


def format_name_address(name):
    if name == None:
        return name
    for spe in specific_symbol:
        name = name.replace(spe, '')

    other_words = re.search(r'(\(.*\))', name)
    if other_words:
        name = name.replace(other_words.group(), '')

    return name