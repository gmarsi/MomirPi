import glob
import os
import pathlib
import random
import re
import sqlite3
import textwrap

import escpos_printer

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

    query = f"select uuid, name from cards where manaValue = {cmc}"
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
    
    #print(query)
    return query

def SelectCard(input, dbCursor):
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

    random.shuffle(dbResult)
    resultDict = dict((y, x) for x, y in dbResult)
    dedupedResults = list(resultDict.values())
    if not dedupedResults:
        return ""

    return random.choice(dedupedResults)

def GetCardImageRepresentation(uuid, dbCursor):
    results = dbCursor.execute(f"select name, setCode from cards where uuid = \"{uuid}\"").fetchall()
    if not results:
        return False
    
    cardName = results[0][0]
    cardSet = results[0][1]

    # handle double-faced cards
    if " // " in cardName:
        # just get the name of the top face
        cardName = cardName.split(" // ")[0]

    resultPath = ""
    setPath = pathlib.Path(f"./cardImages/{cardSet}")
    if setPath.exists():
        filePath = pathlib.Path(f"./cardImages/{cardSet}/{cardName}*.jpg")
        filenameList = glob.glob(str(filePath))
        if(filenameList):
            return random.choice(filenameList)

    filePath = pathlib.Path(f"./cardImages/{cardName}*.jpg")
    filenameList = glob.glob(str(filePath))
    if(filenameList):
            return random.choice(filenameList)
    
    return False

def GetCardCompactTextRepresentation(uuid, dbCursor):
    results = dbCursor.execute(f"select name, manaCost, type, text, flavorText, loyalty, power, toughness, setCode from cards where uuid = \"{uuid}\"").fetchall()
    if not results:
        return ""
    
    cardInfo = results[0]

    toReturn  = f"/-------------------------------\\"
    toReturn += "\n| " + '\n'.join([textwrap.fill(p, 32) for p in (f"{cardInfo[0]}   {cardInfo[1]}").split('\\n')])
    toReturn += f"\n| /--------------------------\ |"
    toReturn += f"\n| |                          | |"
    toReturn += f"\n| |                          | |"
    toReturn += f"\n| |                          | |"
    toReturn += f"\n| |                          | |"
    toReturn += f"\n| \--------------------------/ |"
    toReturn += f"\n|                              |"
    toReturn += "\n| " + '\n'.join([textwrap.fill(p, 32) for p in (f"{cardInfo[2]}              {cardInfo[8]}").split('\\n')])
    toReturn += f"\n|                              |"
    toReturn += "\n| " + (cardInfo[3] and '\n'.join([textwrap.fill(p, 32) for p in cardInfo[3].split('\\n')]) or "")
    toReturn += f"\n|                              |"
    toReturn += "\n| " + (cardInfo[4] and '\n'.join([textwrap.fill(p, 32) for p in cardInfo[4].split('\\n')]) or "")
    toReturn += f"\n|                        {(cardInfo[5] or '')}{((cardInfo[6] or cardInfo[7]) and cardInfo[6]+'/'+cardInfo[7] or '')}"
    toReturn += f"\n\------------------------------/"

    return toReturn

def GetCardFullTextRepresentation(uuid, dbCursor):
    results = dbCursor.execute(f"select name, manaCost, type, text, flavorText, loyalty, power, toughness, setCode from cards where uuid = \"{uuid}\"").fetchall()
    if not results:
        return ""
    
    cardInfo = results[0]

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

printer = escpos_printer.FindPrinter()

userInput = "."
while(userInput != ""):

    userInput = input()

    cardUUID = SelectCard(userInput, dbCursor)
    
    # force a card for debugging
    # cardUUID = "4ccb3303-fe0b-5de4-9c42-86d9931e67f6"

    cardImageFile = GetCardImageRepresentation(cardUUID,  dbCursor);
    if(cardImageFile):
        escpos_printer.PrintImage(printer, cardImageFile)
    else:
        escpos_printer.PrintText(printer, GetCardCompactTextRepresentation(cardUUID, dbCursor))

