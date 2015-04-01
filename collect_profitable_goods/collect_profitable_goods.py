import requests
import xml.etree.ElementTree as etree
import sys


"""
http://api.eve-central.com/api/quicklook?typeid=34&usesystem=30002659
https://docs.google.com/spreadsheet/ccc?key=0AlHsU_rOxWl4dHcyeVhPYU9TeklZZmRPZF9sQl9LUnc#gid=5

34 = Tritanium

30000142 :: Jita system
60003760 = Jita IV - Moon 4 - Caldari Navy Assembly Plant

30002187  :: Domain
60008494 = Amarr VIII (Oris) - Emperor Family Academy

30002659  :: Sinq Laison
60011866 = Dodixie IX - Moon 20 - Federation Navy Assembly Plant

30002510  :: Heimatar
60004588 = Rens VI - Moon 8 - Brutor Tribe Treasury

30002053  :: Metropolis
60005686 = Hek VIII - Moon 12 - Boundless Creation Factory
"""


class RequestAtSystem:
    root = ""
    PROFITFACTOR = 0.2

    def __init__(self, typeid, systemid):
        self.xmldata = self.collect_data(typeid, systemid)
        self.root = self.parse_xmlinput(self.xmldata, "string")
        if self.root is None:
            print("Error while parsing xml, exit program.")
            sys.exit()

    def collect_data(self, typeid, systemid):
        url = "http://api.eve-central.com/api/quicklook?typeid={}&usesystem={}".format(typeid, systemid)
        r = requests.get(url)
        return r.text

    def parse_xmlinput(self, inp, inptype):
        if inptype == "file":
            tree = etree.parse(inp)  # inp: Dateipfad zum xml-file
            root = tree.getroot()
            return root
        elif inptype == "string":
            root = etree.fromstring(inp)  # inp: Ein xml-String
            return root
        else:
            return None

    def itemname_and_id(self):
        returnstring = str(self.root[0].find('itemname').text) + " (ID: " + str(
            self.root[0].find('item').text) + ")"
        return returnstring

    # zeigt alle selloders von jita (hauptstation) an: voellig unnoetig
    def all_sellorders(self):
        for sellorder in self.root[0].find('sell_orders'):
            if sellorder.find('station').text == '60003760':
                print(sellorder.get('id'))
                print(sellorder.find('price').text)

    def lowest_selloders_sorted_by_station(self, station_filter=None):
        lowest_sellorders_by_station = {}
        for sellorder in self.root[0].find('sell_orders'):
            if station_filter is not None:
                if str(sellorder.find('station').text) != str(station_filter):
                    continue
            station = str(sellorder.find('station').text)
            price = str(sellorder.find('price').text)
            if not lowest_sellorders_by_station:
                lowest_sellorders_by_station[station] = price
            elif station not in lowest_sellorders_by_station:
                lowest_sellorders_by_station[station] = price
            elif float(lowest_sellorders_by_station[station]) > float(price):
                lowest_sellorders_by_station[station] = price
        if len(lowest_sellorders_by_station) == 0:
            return None
        else:
            return lowest_sellorders_by_station

    def highest_buyorders_sorted_by_station(self, station_filter=None):
        highest_sellorders_sorted_by_station = {}
        for buyorder in self.root[0].find('buy_orders'):
            if station_filter is not None:
                if str(buyorder.find('station').text) != str(station_filter):
                    continue
            station = str(buyorder.find('station').text)
            price = str(buyorder.find('price').text)
            if not highest_sellorders_sorted_by_station:
                highest_sellorders_sorted_by_station[station] = price
            elif station not in highest_sellorders_sorted_by_station:
                highest_sellorders_sorted_by_station[station] = price
            elif float(highest_sellorders_sorted_by_station[station]) < float(price):
                highest_sellorders_sorted_by_station[station] = price
        if len(highest_sellorders_sorted_by_station) == 0:
            return None
        else:
            return highest_sellorders_sorted_by_station

    def analyse_station(self, station_filter):
        try:
            buyorder_exists = True
            sellorder_exists = True
            vk_tmp = self.lowest_selloders_sorted_by_station(int(station_filter))
            if vk_tmp is None:
                sellorder_exists = False
                # print("No selloder for:   " + str(self.itemname_and_id()))
                # return None
            ek_tmp = self.highest_buyorders_sorted_by_station(int(station_filter))
            if ek_tmp is None:
                buyorder_exists = False
                # print("No buyorder for:   " + str(self.itemname_and_id()))
                # return None
            if (buyorder_exists is False) or (sellorder_exists is False):
                ausgabe_string = ""
                if (buyorder_exists is False) and (sellorder_exists is True):
                    ausgabe_string = "{:70} EK: {:15,.0f}   VK: {:>15s}    Differenz: {:>15s}".format(
                        self.itemname_and_id(), 1, "unknown", "unknown")  # float(ek_tmp[str(station_filter)])
                if (sellorder_exists is False) and (buyorder_exists is True):
                    ausgabe_string = "{:70} EK: {:>15s}   VK: {:15,.0f}    Differenz: {:>15s}".format(
                        self.itemname_and_id(), "unknown", 1, "unknown")  # float(vk_tmp[str(station_filter)])
                if (buyorder_exists is False) or (sellorder_exists is False):
                    ausgabe_string = "{:70} EK: {:>15s}   VK: {:>15s}    Differenz: {:>15s}".format(
                        self.itemname_and_id(), "unknown", "unknown", "unknown")
                print(ausgabe_string)
                # with open('results.txt', 'a') as of:
                    # of.write(ausgabe_string + "\n")
                return None

            vk_preis = float(vk_tmp[str(station_filter)])
            ek_preis = float(ek_tmp[str(station_filter)])
            differenz = vk_preis - ek_preis
            if differenz > (vk_preis * self.PROFITFACTOR):  #  UEBER DIE FORMEL WIRD NOCH DISKUTIERT
                ausgabe_string = "{:70} EK: {:15,.0f}   VK: {:15,.0f}    Differenz: {:15,.0f}".format(
                    self.itemname_and_id(), ek_preis, vk_preis, differenz)
                print(ausgabe_string)
                with open('results.txt', 'a') as of:
                    of.write(ausgabe_string + "\n")
            else:
                print("No profit with:    " + str(self.itemname_and_id()))
                # pass
        except:
            print("Error in VK:EK comparison")
            # pass


'''
erster = RequestAtSystem(34, 30000142)
print(erster.itemname_and_id())
#print(erster.all_sellorders())
print(erster.lowest_selloders_sorted_by_station(60003760))
print(erster.highest_buyorders_sorted_by_station(60003760))
'''

'''
with open('id_map_name_2.txt', encoding="utf-8") as f:
    inhalt = f.readlines()
    for line in inhalt:
        typeid = int(line.split(':::')[0])
        req = RequestAtSystem(typeid, 30000142)
        req.analyse_station(60003760)
'''
with open('2048_interessante_ids.txt', encoding="utf-8") as f:
    inhalt = f.readlines()
    for line in inhalt:
        req = RequestAtSystem(int(line), 30000142)
        req.analyse_station(60003760)
