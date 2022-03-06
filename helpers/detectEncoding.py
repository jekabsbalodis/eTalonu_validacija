import os
from charset_normalizer import detect

def get_file_encoding_chardet(file_path):
    with open(file_path, 'rb') as f:

        result = detect(f.read())
        return result['encoding']


for paths, dirs, files in os.walk('raw_data'):
    for file in files:
        if file.startswith('.'):
            continue
        filePath = os.path.join(paths, file)
        print(filePath)
        print(get_file_encoding_chardet(filePath))