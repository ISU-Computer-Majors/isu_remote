#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2014 Kevin Townsend
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from html.parser import *
from urllib.request import *
from subprocess import *


user_info = "user_config.py"

def _PrepareFileData(file_lines):
    # For each line, remove comments and trim all spaces at beginning and the end.
    for i in range(len(file_lines)):
        comment_index = file_lines[i].find('#')
        if comment_index != -1:
            file_lines[i] = file_lines[i][:comment_index]
        file_lines[i] = file_lines[i].strip()

    # Join all lines into a single string, being careful to remove empty lines.
    return '\n'.join(line for line in file_lines if line)

def _ReadDataImpl(filename):
    """Read the persistent data from the specified file, which should be
    formatted as a python dict.

    Args:
        filename: Name of the file with the data to load.

    Returns:
        A python dictionary with the file contents.

    Raises:
        error.InternalError: If there is any error while reading the data from the
            file.
    """
    try:
        # Open the configuration file and read all lines from it.
        file = open(filename, 'rt')
        file_lines = file.readlines()
        file.close()

        # Prepare the file data to prevent mistakes and evaluate it as if it were a
        # python dictionary.
        file_data = _PrepareFileData(file_lines)
        return eval(file_data, {}, {})
    except IOError as e:
        raise IOError('IO error happened while reading data from file '
                              '"{0}" : {1}.\n'.format(filename, e))

try:
    userInfo = _ReadDataImpl(user_info)
except IOError:
    print("""no user_config.py file
Create a file called user_config.py with contents:
{
'username'  : '',
'password'  : ''
}
""")
username = userInfo['username']
password = userInfo['password']
if(username == ""):
    username = input("Enter username:")

lowestLoadServer = "none"
serverLoadPairs = []
class MyHTMLParser(HTMLParser):
    encounteredContent = 0
    lowestLoad = 100
    global lowestLoadServer
    def handle_starttag(self,tag,attrs):
        if(tag == "div"):
            if(attrs[0][1] == "content"):
                self.encounteredContent = 4
    def handle_comment(self, data):
        global lowestLoadServer
        if(self.encounteredContent):
            self.encounteredContent = self.encounteredContent - 1
            if(self.encounteredContent == 0):
                servers = data.split("\\n")
                for i in servers:
                    parts = i.split(',')
                    if(len(parts) > 6):
                        load = float(parts[4].split()[2]) - float(parts[2])
                        server = parts[0].lstrip("\'b\'")
                        server = parts[0].lstrip("\"b\'")
                        if(self.lowestLoad > load and not server.startswith("linuxremote")):
                            self.lowestLoad = load
                            lowestLoadServer = server
                        serverLoadPairs.append((load,server))

try:
    f = urlopen("http://it.engineering.iastate.edu/remote")
except URLError:
    print("Unable to open it.engineering.iastate.edu. Try connecting to the internet.")

feed = ""
for line in f:
    try:
        data = str(line)
    except EOFError:
        break
    feed = feed + data

parser = MyHTMLParser()
parser.feed(feed)
serverLoadPairs.sort()
i = 0

for pair in serverLoadPairs:
    if(i == 3):
        break;
    login = username + "@" + pair[1];
    i = i + 1
    try:
        if(password == ""):
            call(["ssh", "-X", login])
        else:
            call(["sshpass", "-p", password, "ssh", "-X", login])
            pass
        break
    except KeyboardInterrupt:
        print("Trying next server")

#NOTICE:
# The software from Google contains significant changes. I am not a lawyer and am not sure of
# the correct way to attribute the first two functions to the Google open source project 
# "Google Code Jam Commandline".
