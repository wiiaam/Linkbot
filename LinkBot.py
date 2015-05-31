__author__ = 'William'
import socket
import sys
import threading
import time
from urllib.request import urlopen, Request
import re
import urllib.error

try:
    s = socket.socket()
except socket.error:
    print('Failed to create socket')
    sys.exit()
print('Socket Created')

commandchar = '.'


def flush_socket():
    f = s.makefile()
    f.flush()


class Globals:
    linkson = True
    boton = True


def send(string):
    print('sending ' + string)
    s.sendall(str.encode('%s \r\n' % string))
    flush_socket()


def connect():
    host = 'irc.rizon.net'
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Hostname could not be resolved. Exiting')
        sys.exit()
    s.connect((remote_ip, 6667))


class ServerListener(threading.Thread):
    def run(self):
        while 1:
            reply = s.recv(4096)
            if reply == "":
                sys.exit(0)
            parse(reply.decode('ascii', 'ignore'))


def pm(room, message):
    tosend = 'PRIVMSG ' + room + ' :' + message
    send(tosend)


def nick(nickname):
    send('NICK ' + nickname)


def user(username):
    send('USER ' + username + ' 0 unused :Link Bot')


def login(password):
    send('PRIVMSG Nickserv :IDENTIFY ' + password)


def join(room):
    send('JOIN #' + room)


def parse(string):
    print(string)
    split = string.split()
    if split[0].startswith(':') is False:
        command = split[0]
        message = split[1][1:]
        param = ''
        sender = ''
    else:
        senderaddress = split[0][1:]
        command = split[1]
        sendersplit = senderaddress.split('!')
        sender = sendersplit[0]
        if split[2].startswith(':') is False:
            param = split[2]
            message = split[3][1:]
            for i in range(4, len(split)):
                message += ' ' + split[i]
        else:
            message = split[2][1:]
            param = ''
    botcom = message.startswith('.')
    if param == 'LinkBot':
        param = sender
    if command == 'PING':
        print('sending pong')
        s.send(str.encode("PONG :" + message))
    if command == 'PRIVMSG':
        if len(message.split()) < 1:
            return
        com = message.split()[0][1:]
        if botcom is True:
            print('is botcom')
            if com == 'bots':
                print('is .bots')
                pm(param, 'Reporting in! [Python]')
            elif sender == 'wiiaamm':
                if com == 'linkbot':
                    if len(message.split()) < 2:
                        pm(param, 'Commands are: linkson, linksoff, boton, botoff')
                        return
                    if message.split()[1] == "linksoff":
                        Globals.linkson = False
                        pm(param, 'Links are now off')
                    if message.split()[1] == "linkson":
                        Globals.linkson = True
                        pm(param, 'Links are now on')
                    if message.split()[1] == "boton":
                        Globals.boton = True
                        pm(param, 'Bot is now on')
                    if message.split()[1] == "botoff":
                        Globals.boton = False
                        pm(param, 'Bot is now off')
            if Globals.boton is True:
                if com == 'g':
                    print('scanning url')
                    search = message[3:]
                    search = re.sub('\s+', '%20', search)
                    print(search)
                    urltoopen = 'http://www.google.com/search?btnI=I\'m+Feeling+Lucky&q=' + search
                    print(urltoopen)
                    req = Request(urltoopen, None, {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de;'
                                                                  ' rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
                    res = urlopen(req)
                    finalurl = res.geturl()
                    pm(param, finalurl)
                if com == 'lmgtfy':
                    search = message[8:]
                    search = re.sub('\s+', '+', search)
                    urltoopen = 'https://www.google.com/webhp?hl=en#safe=off&hl=en&q=' + search
                    pm(param, urltoopen)
                    pm(param, 'Was that so hard?')
        elif Globals.linkson is True:
            messagesplit = message.split()
            print(messagesplit)
            for i in range(0, len(messagesplit)):
                if len(messagesplit[i]) > 10:
                    print('len longer than 10')
                    if messagesplit[i].startswith('http://') is True or messagesplit[i].startswith('https://') is True:
                        print('found url')
                        try:
                            urltoopen = messagesplit[i]
                            req = Request(urltoopen, None, {
                                'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; '
                                              'de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'})
                            res = urlopen(req)
                            html = res.read().decode('utf-8', 'ignore')
                            html = html.split('<title')[1]
                            html = html.split('>')[1]
                            html = html.split('</title')[0]
                            html.replace('&#039;','\'')
                            htmlsplit = html.split()
                            if len(htmlsplit) < 1:
                                return
                            html = '\x03' + htmlsplit[0]
                            for j in range(1,len(htmlsplit)):
                                html += ' ' + htmlsplit[j]
                                if j is 10:
                                    html += ' ...'
                                    break
                            pm(param,'[\x02URL\x02] ' + html)
                        except urllib.error.HTTPError:
                            pm(param, 'Four hundred and four error')
                        except IndexError:
                            pm(param, 'I currently don\'t support your shitty url')
                        except urllib.error.URLError:
                            pm(param, 'Thats not even a url you autist')

# pw = input('Password to login: \n')
# print(pw)

connect()

ServerListener().start()

nick('LinkBot')
user('LinkBot')

time.sleep(5)
join('pasta')
