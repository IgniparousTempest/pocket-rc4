from enum import Enum

value_for_letter = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12,
                    'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23,
                    'x': 24, 'y': 25, 'z': 26, ' ': 27}
letter_for_value = {v: k for k, v in value_for_letter.items()}


class Colour(Enum):
    """Possible card colours."""
    red = 1
    black = 2


class Card:
    """A class representing a card."""
    def __init__(self, card):
        self.full_card = card
        self.rank = card_rank(card)
        self.suit = card_suit(card)
        self.colour = card_colour(card)
        self.value = card_value(card)

    def __str__(self):
        return self.full_card

    def __repr__(self):
        return str(self).rjust(3)  # The rjust makes it easy to compare print outs of different deck configurations


def card_colour(card):
    """Determine card's colour from a string representation. 
    I.e Red, Black"""
    if card_suit(card) in "HDR":
        return Colour.red
    else:
        return Colour.black


def card_suit(card):
    """Determine card's suit from a string representation. 
    E.g. Diamonds, Spades"""
    return card[-1]


def card_rank(card):
    """Determine card's rank from a string representation. 
    E.g. Ace, 2, 3."""
    return card[:-1]


def card_value(card):
    """Determine card's value from a string representation.
    The value is the face value, unless it is a diamonds or clubs, in which case it is 13 higher."""
    offset = 13 if card_suit(card) in "DC" else 0
    rank = card_rank(card)

    if rank == 'A':
        value = 1
    elif rank == 'J':
        value = 11
    elif rank == 'Q':
        value = 12
    elif rank == 'K':
        value = 13
    elif rank == 'JO':
        value = 27
    else:
        value = int(rank)

    return value + offset


def create_deck(string_deck):
    """Creates a list of card string representations from a sing deck string.
    IN: 'AD 2s jH JoB
    OUT: ['AD', '2S', 'JH', 'JOB']'"""
    return [Card(card.upper()) for card in string_deck.split()]


def card_index(deck, value, colour):
    """Returns the index of a card of a [value] and [colour] in a particular [deck]."""
    for i in range(len(deck)):
        card = deck[i]
        if card.value == value and card.colour == colour:
            return i


def interleave_key_deck(key_deck):
    red_cards = []
    black_cards = []
    interleaved_deck = []

    for card in key_deck:
        if card.colour == Colour.red:
            red_cards.append(card)
        else:
            black_cards.append(card)

    for red, black in zip(red_cards, black_cards):
        interleaved_deck += [red, black]

    return interleaved_deck


def prepare_deck(deck_in, initialisation_vector):
    deck = deck_in[:]
    for c in initialisation_vector.lower():
        # Find black card corresponding to current letter of IV
        black_index = card_index(deck, value_for_letter[c], Colour.black)
        # Swop top red card with red card above IV black card
        deck[0], deck[black_index - 1] = deck[black_index - 1], deck[0]
        # Move black IV card and the red card above it to the bottom of the deck
        deck = deck[:black_index - 1] + deck[black_index + 1:] + deck[black_index - 1:black_index + 1]
        # Put the top two cards on the bottom.
        deck = deck[2:] + deck[:2]
    return deck


def crypt(deck_in, in_text, is_encrypting):
    textstream = ""
    deck = deck_in[:]

    for c in in_text:
        c = c.lower()
        # Set j to the value of the bottom red card
        j = deck[-2].value

        # Add the value of the top red card to j, modulo 27.
        j += deck[0].value
        j = (j - 1) % 27 + 1

        # Find the black card corresponding to 'j'.
        black_j = card_index(deck, j, Colour.black)

        # Add the red card above the j black card to the top red card, modulo 27.
        k = deck[black_j - 1].value + deck[0].value  # k is the keystream value
        k = (k - 1) % 27 + 1

        # Add the plainext letter to this number, modulo 27.
        # OR subtract if we are decrypting
        if is_encrypting:
            k = value_for_letter[c] + k
        else:
            k = value_for_letter[c] - k
        k = (k - 1) % 27 + 1
        textstream += letter_for_value[k]

        # Exchange the two red cards.
        deck[0], deck[black_j - 1] = deck[black_j - 1], deck[0]

        # Move the top black/red card pair to the bottom.
        deck = deck[2:] + deck[:2]

    return textstream


def encrypt(deck_in, plaintext):
    return crypt(deck_in, plaintext, True)


def decrypt(deck_in, ciphertext):
    return crypt(deck_in, ciphertext, False)


if __name__ == "__main__":
    # The agreed upon deck order
    key_deck = "AD AC 2D 2C 3D 3C 4D 4C 5D 5C 6D 6C 7D 7C 8D 8C 9D 9C 10D 10C JD JC QD QC KD KC " \
               "AH AS 2H 2S 3H 3S 4H 4S 5H 5S 6H 6S 7H 7S 8H 8S 9H 9S 10H 10S JH JS QH QS KH KS JOR JOB"
    initialisation_vector = "MagicDoesRuleMugglesDoDrool"  # 27+ character long IV
    plaintext = "The trick is to use two aces"  # The text to be encrypted

    key_deck = create_deck(key_deck)
    key_deck = interleave_key_deck(key_deck)
    key_deck = prepare_deck(key_deck, initialisation_vector)
    ciphertext = encrypt(key_deck, plaintext)
    plaintext_output = decrypt(key_deck, ciphertext)
    print("Original text:", plaintext)
    print("Ciphertext:   ", ciphertext)
    print("Plaintext:    ", plaintext_output)
