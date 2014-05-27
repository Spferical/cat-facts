import random
import getfact

# get promos from file
promofile = open("promos.txt")
promos = promofile.readlines()
promofile.close()

#remove all lines that are just whitespace/empty
for p in promos[:]:
    if p == '' or p.isspace():
        promos.remove(p)


def get_promo():
    """Get a random promo."""
    return random.choice(promos)


def get_text():
    """Get a random text."""
    return getfact.get_fact() + " " + get_promo()
