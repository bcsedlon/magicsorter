from __future__ import print_function

import os
import sqlite3
import sys
import urllib
import json
import phash
import time
from progressbar import Bar, Counter, ETA, Percentage, ProgressBar
from datetime import datetime as dt

from mtgexception import MTGException

"""Reference DB module

This module is responsible for handling all the reference data
"""

DateLimit = "2003-10-02"  # Only use sets from Mirrodin and after (Modern legal)


class MTG_Reference_DB:
    """Attributes:
        PATH (string): Path of the reference database file
        JSON_URL (string): URL to the card data json file
        IMAGE_URL (string): URL to the card image on the gatherer
        IMAGE_FILE (string): Path to local image files
        connection (sqlite): Established sqlite connection
    """
    
    ROOT_PATH = os.path.dirname(__file__)
    #PATH = '%s/reference.db' % (ROOT_PATH,)
    PATH = '%s/referenceallinfo.db' % (ROOT_PATH,)
    JSON_URL = 'http://mtgjson.com/json/AllSets.json'
    #JSON_URL = 'http://mtgjson.com/json/LEA.json'

    IMAGE_URL = 'http://gatherer.wizards.com/Handlers/Image.ashx' + \
        '?multiverseid=%d&type=card'
    IMAGE_FILE = 'img/%d.jpg'
    
    

    def __init__(self):
        try:
            print(self.PATH)
            self.connection = sqlite3.connect(self.PATH)
        except sqlite3.Error, e:
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def check_rebuild(self):
        """Check to see if the reference db needs to be rebuilt
        """

        rebuild = False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT name FROM sqlite_master
                WHERE type='table';""")
            data = cursor.fetchall()
            if (not len(data)):
                rebuild = True
            else:
                if (
                    ((u'Sets',) not in data) or ((u'Cards',) not in data) or
                    ((u'Hashes',) not in data)
                ):
                    rebuild = True
                else:
                    cursor.execute("""SELECT
                        (SELECT COUNT(*) FROM Sets) as SetCount,
                        (SELECT COUNT(*) FROM Cards) as CardCount,
                        (SELECT COUNT(*) FROM Hashes) as HashCount""")
                    data = cursor.fetchone()
                    if (not data[0] or not data[1] or not data[2]):
                        rebuild = True
                    elif (data[1] != data[2]):
                        rebuild = True
                    else:
                        cursor.execute("SELECT MultiverseID FROM Cards")
                        data = cursor.fetchall()
                        for card in data:
                            if (not os.path.isfile(self.IMAGE_FILE % card[0])):
                                rebuild = True
        except sqlite3.Error, e:
            print("Error %s:" % e.args[0])
            sys.exit(1)

        return rebuild

    def import_cards(self):
        """Import card data from MTGJSON
        """

        print('Fetching card data...')
        print (self.JSON_URL)
        
        #data = json.load(urllib.urlopen(self.JSON_URL))

        fp = open('AllSets.json')
        #fp = open('LEA.json')
        data = json.load(fp)
        fp.close()

        '''
        "artist":"Richard Thomas",
        "cmc":5,
        "colorIdentity":["U"],
        "colors":["Blue"],
        "flavor":"These spirits of the air are winsome and wild, and cannot be truly contained. Only marginally intelligent, they often substitute whimsy for strategy, delighting in mischief and mayhem.",
        "id":"926234c2fe8863f49220a878346c4c5ca79b6046",
        "imageName":"air elemental",
        "layout":"normal",
        "manaCost":"{3}{U}{U}",
        "mciNumber":"47",
        "multiverseid":94,
        "name":"Air Elemental",
        "power":"4",
        "rarity":"Uncommon",
        "subtypes":["Elemental"],
        "text":"Flying",
        "toughness":"4",
        "type":"Creature - Elemental",
        "types":["Creature"]
        '''
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS Sets
                (ID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Code TEXT NOT NULL)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS Cards (
                MultiverseID INTEGER NOT NULL PRIMARY KEY,
                SetID INTEGER NOT NULL,
                Name TEXT NOT NULL,
                
                artist TEXT,
                cmc TEXT,
                colorIdentity TEXT,
                colors TEXT,
                flavor TEXT,
                id TEXT,
                imageName TEXT,
                layout TEXT,
                manaCost TEXT,
                mciNumber TEXT,
                multiverseid2 TEXT,
                name2 TEXT,
                power TEXT,
                rarity TEXT,
                subtypes TEXT,
                text TEXT,
                toughness TEXT,
                type TEXT,
                types TEXT
                
                
                )""")
            cursor.execute("DELETE FROM Sets")
            cursor.execute("DELETE FROM Cards")
            self.connection.commit()
        except sqlite3.Error, e:
            self.connection.rollback()
            print("Error %s:" % e.args[0])
            sys.exit(1)

        print('Importing card data...')
        dateLimit = dt.strptime(DateLimit, "%Y-%m-%d")
        try:
            for setid in data:
                UseSet = True
                if (
                    (data[setid]['type'] != 'expansion' and
                        data[setid]['type'] != 'core')
                ):
                    UseSet = False
                else:
                    date = data[setid].get('releaseDate', 'ERR')
                    if (
                        date == 'ERR' or
                            dt.strptime(date, "%Y-%m-%d") < dateLimit
                    ):
                        UseSet = False

                if (UseSet):
                    code = data[setid].get(
                        'gathererCode',
                        data[setid].get('code', 'ERR')
                    )
                    cursor.execute("""SELECT ID FROM Sets
                    WHERE Code = ?""", (code,))
                    r = cursor.fetchone()
                    if (r is None):
                        cursor.execute("""INSERT INTO Sets (Name, Code)
                            VALUES(?, ?)""", (data[setid]['name'], code))
                        sid = cursor.lastrowid
                    else:
                        sid = r[0]

                    for card in data[setid]['cards']:
                        #print(card)
       
                        cursor.execute("""SELECT * FROM Cards WHERE
                            MultiverseID = ?""", (str(card['multiverseid']),))
                        if (cursor.fetchone() is None):
                            '''
                            cursor.execute(
                                """INSERT INTO Cards
                                (MultiverseID, SetID, Name) VALUES(?, ?, ?)""",
                                (card['multiverseid'], sid, card['name'])
                            )
                            '''
                            cursor.execute(
                                """
                                INSERT INTO Cards
                                (MultiverseID, SetID, Name,
                                
                                artist, cmc, colorIdentity, colors, flavor, id, imageName, layout, manaCost, mciNumber, multiverseid2, name2, power, rarity, subtypes, text, toughness, type, types                               
                                
                                ) VALUES(?, ?, ?,
                                
                                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                                
                                )
                                """,
                                (card['multiverseid'], sid, card['name'],
                                
                                self.getCardAttr(card, 'artist'),
                                self.getCardAttr(card, 'cmc'),
                                self.getCardAttr(card, 'colorIdentity'), 
                                self.getCardAttr(card, 'colors'),
                                self.getCardAttr(card, 'flavor'), 
                                self.getCardAttr(card, 'id'), 
                                self.getCardAttr(card, 'imageName'), 
                                self.getCardAttr(card, 'layout'), 
                                self.getCardAttr(card, 'manaCost'), 
                                self.getCardAttr(card, 'mciNumber'), 
                                self.getCardAttr(card, 'multiverseid'), 
                                self.getCardAttr(card, 'name'), 
                                self.getCardAttr(card, 'power'), 
                                self.getCardAttr(card, 'rarity'), 
                                self.getCardAttr(card, 'subtypes'), 
                                self.getCardAttr(card, 'text'),
                                self.getCardAttr(card, 'toughness'), 
                                self.getCardAttr(card, 'type'),
                                self.getCardAttr(card, 'types')
                                
                                )
                            )
                            

            self.connection.commit()
        except sqlite3.Error, e:
            self.connection.rollback()
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def getCardAttr(self, card, attr):
        try:
            result = unicode(card[attr])
        except:
            result = None
        return result
        
    def download_images(self):
        """Download images from the gatherer
        """

        print('Downloading images...')
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MultiverseID FROM Cards")
            cards = cursor.fetchall()
            if (len(cards)):
                pbar = ProgressBar(
                    widgets=[
                        Percentage(), ': ', Counter(),
                        '/' + str(len(cards)) + ' ', Bar(), ' ', ETA()
                    ]
                )
                for card in pbar(cards):
                    MultiverseID = card[0]
                    path = self.IMAGE_FILE % MultiverseID
                    if (not os.path.isfile(path)):
                        urllib.urlretrieve(self.IMAGE_URL % MultiverseID, path)
                        os.system(
                            "convert " + path +
                            " -background black -flatten " + path)

        except sqlite3.Error, e:
            self.connection.rollback()
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def calculate_hashes(self):
        """Calculate the hashes for all the cards
        """

        print('Calculating hashes...')
        try:
            cursor = self.connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS Hashes
                (MultiverseID INTEGER NOT NULL PRIMARY KEY,
                Hash TEXT NOT NULL)""")
            cursor.execute("DELETE FROM Hashes")
            self.connection.commit()

            cursor.execute("SELECT MultiverseID FROM Cards")
            cards = cursor.fetchall()
            if (len(cards)):
                pbar = ProgressBar(
                    widgets=[
                        Percentage(), ' ', Bar(), ' ', ETA()
                    ]
                )
                for card in pbar(cards):
                    MultiverseID = card[0]
                    path = self.IMAGE_FILE % MultiverseID
                    cursor.execute("""SELECT * FROM Hashes WHERE
                        MultiverseID = ?""", (MultiverseID,))
                    if (cursor.fetchone() is None):
                        ihash = phash.dct_imagehash(path)
                        cursor.execute(
                            """INSERT INTO Hashes
                            (MultiverseID, Hash) VALUES(?, ?)""",
                            (MultiverseID, str(ihash))
                        )

            self.connection.commit()
        except sqlite3.Error, e:
            self.connection.rollback()
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def get_hashes(self):
        """Get the list of hashes
        """

        hashes = {}
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MultiverseID, Hash FROM Hashes")
            for row in cursor.fetchall():
                hashes[row[0]] = row[1]

            return hashes
        except sqlite3.Error, e:
            print("Error %s:" % e.args[0])
            sys.exit(1)

    def get_card_info(self, MultiverseID):
        """Get the name and set code for a single card
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute("""SELECT C.Name, S.Code, C.rarity FROM Cards C
                LEFT JOIN Sets S on S.ID = C.SetID
                WHERE C.MultiverseID = ?""", (MultiverseID,))
            r = cursor.fetchone()
            if (r is None):
                raise MTGException('No such card')

            return r[0], r[1], r[2]
        except sqlite3.Error, e:
            self.connection.rollback()
            print("Error %s:" % e.args[0])
            sys.exit(1)
