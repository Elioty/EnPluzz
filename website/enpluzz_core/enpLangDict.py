# EnPluzz
# Copyright (C) 2025  Elioty <roadkiller.cl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from pathlib import Path
from io import TextIOWrapper, StringIO
import json

class ENPLangDict:
    '''Class to handle an EnP language localization.'''

    #TODO: rework it to have a single dictionary level, no need to have an actual tree structure

    __REMOVE_SPECIAL_CODE = re.compile(r'\[(#!|##element(purple|yellow|blue|green|red)|#[0-9a-f]{6}|%[0-9]{1,3}|-|#|%)\]')

    def __init__(self, lang:str = 'English', dictionary:str|Path|TextIOWrapper = '', override:str|Path|TextIOWrapper|dict = '{}') -> None:
        self.langDictionary = dict(sub = dict())
        self.insert(lang, dictionary, override)

    def insert(self, lang:str = 'English', dictionary:str|Path|TextIOWrapper = '"KEY","TEXT"\n', override:str|Path|TextIOWrapper|dict = '{}') -> None:
        '''Method to insert multiple dictionary entries from a CSV formatted string, file (with its path) or IO wrapper + any language override configuration if given.'''
        self.lang = lang

        dictionaryToClose = False
        if isinstance(dictionary, Path):
            # We got a path so load the dictionary ourself
            if dictionary.is_dir():
                # Path to a directory so append the language file's name
                dictionary = dictionary / lang
            dictionary = open(dictionary, 'r', encoding = 'UTF-8')
            dictionaryToClose = True # Close it only if we opened it ourself
        elif isinstance(dictionary, str):
            # The dictionary is a string, just make a StringIO out of it
            dictionary = StringIO(dictionary)

        if isinstance(override, Path):
            # We got a path so load the override ourself
            if override.is_dir():
                # Path to a directory so append the language override file's name
                override = override / 'languageOverrides.json'
            with open(override, mode='r', encoding='UTF-8') as fd:
                override = json.load(fd)
        elif isinstance(override, str):
            override = json.loads(override)
        elif isinstance(override, TextIOWrapper):
            override = json.load(override)

        # Read the header line
        if dictionary.readline() != '"KEY","TEXT"\n':
            raise Exception('The given dictionary does not contain the expected header.')

        # And read the dictionary line by line
        multipleLine = False
        for line in dictionary:
            if not multipleLine:
                keyEnd = line.index('"', 1)
                key = line[1:keyEnd]
                if line[-2] == '"':
                    text = line[keyEnd + 3:-2]
                else:
                    text = line[keyEnd + 3:]
                    multipleLine = True
            else:
                if line != '\n' and line[-2] == '"':
                    text = text + line[:-2]
                    multipleLine = False
                else:
                    text = text + line

            if not multipleLine:
                self.insertOne(key, text)

        if len(override):
            override = override['languageOverridesConfig']['overrides'][lang]
            for entry in override['overrideEntries']:
                self.insertOne(entry['key'], entry['text'])

        if dictionaryToClose:
            dictionary.close()

    def insertOne(self, key:str, text:str) -> None:
        '''Method to insert one dictionary entry with its key and value.'''
        key  = key.split('.')
        node = self.langDictionary['sub']
        for keyPart in key[:-1]:
            if keyPart not in node:
                node[keyPart] = dict(sub = dict())
            elif 'sub' not in node[keyPart]:
                node[keyPart]['sub'] = dict()
            node = node[keyPart]['sub']
        if key[-1] not in node:
            node[key[-1]] = dict(val = text)
        else:
            node[key[-1]]['val'] = text

    def get(self, key:str, args:None|int|list|dict = None, default:None|str = None, removeStyle:bool = True) -> str:
        '''Method to get a dictionary entry's value, filled with the given format arguments if given.'''
        splitKey = key.split('.')
        node     = self.langDictionary['sub']
        for keyPart in splitKey[:-1]:
            if keyPart in node and 'sub' in node[keyPart]:
                node = node[keyPart]['sub']
            else:
                return default if default is not None else key

        text = None
        if splitKey[-1] in node and 'val' in node[splitKey[-1]]:
            text = node[splitKey[-1]]['val']
        elif isinstance(args, int):
            if args == 1:
                if splitKey[-1] + '#1' in node and 'val' in node[splitKey[-1] + '#1']:
                    text = node[splitKey[-1] + '#1']['val']
            else:
                if splitKey[-1] + '#2' in node and 'val' in node[splitKey[-1] + '#2']:
                    text = node[splitKey[-1] + '#2']['val']

        if text is None:
            return default if default is not None else key
        if isinstance(args, int):
            text = text.format(args)
        elif isinstance(args, list):
            text = text.format(*args)
        elif isinstance(args, dict):
            text = text.format(**args)

        if removeStyle is False:
            return text
        else:
            return self.__REMOVE_SPECIAL_CODE.sub('', text)

    def has(self, key:str) -> bool:
        '''Method to check whether a dictionary entry exists.'''
        splitKey = key.split('.')
        node     = self.langDictionary['sub']
        for keyPart in splitKey[:-1]:
            if keyPart in node and 'sub' in node[keyPart]:
                node = node[keyPart]['sub']
            else:
                return False

        if splitKey[-1] in node and 'val' in node[splitKey[-1]]:
            return True
        else:
            return False
