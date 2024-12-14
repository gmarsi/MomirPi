# MomirPi
Make proxies for Momir Basic with a rPi and receipt printer!

Installation:
1. Gather card images, if desired. They should be in /cardImages/[set code]/[name].jpg, and formatted as 400-pixel-wide, 200dpi, black-and-white images.
2. Open .venv\Lib\site-packages\escpos\printer.py and comment out lines 61-71. This step is required for windows and may (?) be required for other platforms as well.
3. Ensure your USB driver is compatible with esc/pos. You may have to install a new one (especially on Windows). See https://nyorikakar.medium.com/printing-with-python-and-epson-pos-printer-fbd17e127b6c for more.
4. Ensure that the vendor ID and product ID in escpos_printer.py match the device ID and vendor ID of your printer. 

Use:
- Run momir.py 
- Program takes input in the form of ^[1-9]?[0-9]?[CWUBRG]*$ and will return a representation of a card that matches that mana cost.
  - Note that you can use "nonstandard" formatting to represent the actual mana paid (i.e. "WUUUWRRR")
  - Cards updated 12/1/24

There are a few differences from classic Momir Basic:
- The program matches on mana types (i.e. it will respect colors) rather than using CMC
- A given input has a 60% chance to return a creature, 30% to return a noncreature permanent, and 10% to return an instant or sorcery.
- Cards with X in their cost will never be returned

Known issues:
- Currently cards with hybrid or phyrexian mana symbols may behave unpredictably