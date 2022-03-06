from functions.downloadData import downloadData
from helpers.menu import printMenu
from helpers.constants import DATA_URL, MENU_SELECTION, SELECTION_ERROR
from helpers.userInput import intInput, stringInput


def menuSelection():
    printMenu()
    option = intInput(MENU_SELECTION)
    match option:
        case 1: print('Show data')
        case 2: downloadData(stringInput(DATA_URL))
        case 3: print('Add data')
        case 4: print('Search data')
        case 5: exit()
        case _: print(SELECTION_ERROR)
    menuSelection()


menuSelection()
