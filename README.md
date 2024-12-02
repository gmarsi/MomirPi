# MomirPi
Make proxies for Momir Basic with a rPi and receipt printer!

Simply run momir.py 

Program takes input in the form of ^[1-9]?[0-9]?[CWUBRG]*$ and will return a representation of a card that matches that mana cost.
- Note that you can use "nonstandard" formatting to represent the actual mana paid (i.e. "WUUUWRRR")
- Cards updated 12/1/24

There are a few differences from classic Momir Basic:
- The program matches on mana types (i.e. it will respect colors) rather than using CMC
- A given input has a 60% chance to return a creature, 30% to return a noncreature permanent, and 10% to return an instant or sorcery.
- Cards with X in their cost will never be returned

Known issues:
- Currently cards with hybrid or phyrexian mana symbols may behave unpredictably