from helpers.constants import INT_INPUT_ERROR


def stringInput(message):
    userInput = str(input(message))
    if userInput == '':
        return stringInput(message)
    else:
        return userInput


def intInput(message):
    userInputAsString = stringInput(message)
    try:
        userInputAsInt = int(userInputAsString)
        return userInputAsInt
    except:
        print(INT_INPUT_ERROR)
        return intInput(message)
