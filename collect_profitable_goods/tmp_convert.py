"""
from bs4 import BeautifulSoup

with open('all_typeid_and_names.txt', encoding="utf-8") as f:
    inhalt = f.read()

soup = BeautifulSoup(inhalt)

with open('id_map_name.txt', 'w', encoding="utf-8") as f:
    for link in soup.find_all('a'):
        linkteil = link.get('href')
        id = linkteil.split('typeid=')[1]
        text = link.get_text()
        tmp = str(id) + ":::" + str(text) + "\n"
        #print(tmp)
        f.write(tmp)
"""

with open('id_map_name_2nd_version.txt', encoding="utf-8") as fr:
    inhalt = fr.readlines()

with open('id_map_name_2nd_version_edited.txt', 'w', encoding="utf-8") as fw:
    for line in inhalt:
        a = line.split(' ')
        b = a[0] + ":::" + line.replace(a[0]+' ','')
        #print(b)
        fw.write(b)