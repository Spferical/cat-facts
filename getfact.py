import random


facts = open("facts.txt", mode='r')
lines = facts.readlines()
facts.close()

#remove all lines that are just whitespace/empty
for line in lines[:]:
    if line == '' or line.isspace():
        lines.remove(line)


def get_fact():
    return random.choice(lines)
