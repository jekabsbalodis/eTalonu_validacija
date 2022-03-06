from helpers.constants import ADD_DATA, DOWNLOAD_DATA, EXIT, SEARCH_DATA, SHOW_DATA


menuOptions = {
    1: SHOW_DATA,
    2: DOWNLOAD_DATA,
    3: ADD_DATA,
    4: SEARCH_DATA,
    5: EXIT
}


def printMenu():
    print('----------')
    for key in menuOptions.keys():
        print(key, '---', menuOptions[key])
    print('----------')
