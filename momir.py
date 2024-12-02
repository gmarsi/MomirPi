import sqlite3
import re
import random
import textwrap

def ConstructCostQuery(cost: str, types=[]):

    costPattern = re.compile("^[1-9]?[0-9]?[CWUBRG]*$")
    if(costPattern == "" or not costPattern.fullmatch(cost)):
        print("Invalid Pattern")
        return ""

    numbers = re.compile("[0-9]*").search(cost).group() or 0
    symbols = list("".join(re.compile("[CWUBRG]*").findall(cost)))
    cmc = float(int(numbers) + len(symbols))

    dedupe = list(dict.fromkeys(list(symbols)))
    symbolCounts = {symbol:symbols.count(symbol) for symbol in dedupe}

    antisymbols = ['W', 'U', 'B', 'R', 'G', 'X']
    antisymbols = [symbol for symbol in antisymbols if symbol not in dedupe]

    query = f"select name from cards where manaValue = {cmc}"
    if types:
        query = query + " and ("
        for type in types:
            query = query + f"types like '{type}' or "
        query = query + "false)"
    for symbol, symbolCount in symbolCounts.items():
        symbolConstraint = "".join(["{"+symbol+"}" for x in range(symbolCount+1)])
        query = query + f" and manaCost not like '%{symbolConstraint}%'"
    for symbol in antisymbols:
        query = query + f" and manaCost not like '%{symbol}%'"
    query = query + ";"
    
    print(query)
    return query

def SelectCardName(input, dbCursor):
    dbResult = ""
    creatureResult = dbCursor.execute(ConstructCostQuery(input, ["Creature"])).fetchall();
    noncreatureResult = dbCursor.execute(ConstructCostQuery(input, ["Artifact", "Enchantment", "Planeswalker", "Battle"])).fetchall();
    spellResult = dbCursor.execute(ConstructCostQuery(input, ["Sorcery", "Instant"])).fetchall();

    choice = random.randint(0, 9)
    if creatureResult != [] and (choice <= 5 or (choice <= 8 and noncreatureResult == []) or (choice == 9 and spellResult == [])):
        dbResult = creatureResult
    elif noncreatureResult != [] and (choice <= 8 or (choice <= 5 and noncreatureResult == []) or (choice == 9 and spellResult == [])):
        dbResult = noncreatureResult
    else:
        dbResult = spellResult

    dedupedResults = list(dict.fromkeys(dbResult))
    if not dedupedResults:
        return ""

    return random.choice(dedupedResults)[0]

def GetCardImageRepresentation(name):
    pass

def GetCardTextRepresentation(name, dbCursor):
    results = dbCursor.execute(f"select name, manaCost, type, text, flavorText, loyalty, power, toughness, setCode from cards where name = \"{name}\"").fetchall()
    if not results:
        return ""
    
    cardInfo = random.choice(results);

    toReturn  = f"/----------------------------------------\\"
    toReturn += "\n| " + '\n'.join([textwrap.fill(p, 40) for p in (f"{cardInfo[0]}        {cardInfo[1]}").split('\\n')])
    toReturn += f"\n| /------------------------------------\ |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| |                                    | |"
    toReturn += f"\n| \------------------------------------/ |"
    toReturn += f"\n|                                        |"
    toReturn += "\n| " + '\n'.join([textwrap.fill(p, 40) for p in (f"{cardInfo[2]}                   {cardInfo[8]}").split('\\n')])
    toReturn += f"\n|                                        |"
    toReturn += "\n| " + (cardInfo[3] and '\n'.join([textwrap.fill(p, 40) for p in cardInfo[3].split('\\n')]) or "")
    toReturn += f"\n|                                        |"
    toReturn += "\n| " + (cardInfo[4] and '\n'.join([textwrap.fill(p, 40) for p in cardInfo[4].split('\\n')]) or "")
    toReturn += f"\n|                                   {(cardInfo[5] or '')}{((cardInfo[6] or cardInfo[7]) and cardInfo[6]+'/'+cardInfo[7] or '')}"
    toReturn += f"\n\----------------------------------------/"

    return toReturn

dbConnection = sqlite3.connect("AllPrintings.sqlite")
dbCursor = dbConnection.cursor();

userInput = "."
while(userInput != ""):
    userInput = input()

    chosenCard = SelectCardName(userInput, dbCursor)

    if(GetCardImageRepresentation(chosenCard)):
        pass
    else:
        print(GetCardTextRepresentation(chosenCard, dbCursor))

