import requests
import os


def downloadData(input):
    url = input
    fileName = url.split('/')[-1]
    scriptPath = os.path.realpath(__file__)
    folderPath = os.path.join(os.path.dirname(
        os.path.dirname(scriptPath)), 'raw_data\\zips')
    # [x] Fix relative folder path
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    filePath = folderPath + '\\' + fileName
    file = requests.get(url)
    open(filePath, 'wb').write(file.content)
