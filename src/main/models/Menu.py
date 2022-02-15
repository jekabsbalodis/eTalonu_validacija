from common.Constants import ADD_DATA, SEARCH_DATA, SHOW_DATA


menuOptions = {
    1: SHOW_DATA,
    2: ADD_DATA,
    3: SEARCH_DATA
}


def printMenu():
    """
    Outputs the menu options on screen
    """
    for key in menuOptions.keys():
        print(key, '--', menuOptions[key])
    # printMenu()