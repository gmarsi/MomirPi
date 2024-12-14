from escpos.printer import Usb

def FindPrinter():
    # these two numbers are vendor id and product id
    # you may have to change this depending on your driver situation
    dev = Usb(idVendor=0x09C5, idProduct=0x583E) 
    if dev is None:
        print("device not found")
        return None
    else:
        return dev

def PrintImage(device, imagePath):
    device.image(imagePath)
    device.text("\n\n\n")
    
def PrintText(device, str):
    device.text(str)
    device.text("\n\n\n")
