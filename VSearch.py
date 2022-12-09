def search4vowals(phrase: str):
    vowals = set('aeiyuo')
    return vowals.intersection(set(phrase))


def search4letters(phrase: str, letters: str):
    return set(letters).intersection(set(phrase))


