import os

def get_chinese(artist_name):
    file_name='artistName.txt'
    print("artistName in english: ",artist_name)

    with open(file_name, 'r',encoding='utf-8') as f:
        lines = f.readlines()

    key =[]
    value = []
    for line in lines:
        english_name = line.split(':')[0]
        chinese_name = line.split(':')[1]
        key.append(english_name)
        value.append(chinese_name)

    my_dict = dict(zip(key,value))

    if(my_dict.get(artist_name)):
        get_chinese_name = my_dict.get(artist_name)
    else:
        get_chinese_name = artist_name
    print("ChineseName: ",get_chinese_name.strip())
    return get_chinese_name