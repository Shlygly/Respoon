from enum import Enum
import hexchat
import re

__module_name__ = 'Respoon'
__module_version__ = '2.0'
__module_description__ = 'Automatic response manager'
__author__ = 'Stockage'

CONF_PREFIX = "respoon_"
ELEM_PREFIX = CONF_PREFIX + "elem_"


class RespoonType(Enum):
    MSG = 0
    CMD = 1


class Respoon:
    def __init__(self, name, server, channel, trigger, type, action):
        self.name = name
        self.server = server
        self.channel = channel
        self.trigger = trigger
        self.type = type
        self.action = action
    
    def checkOrigin(self, server, channel):
        valid = True
        if self.server.startswith("*"):
            valid = valid and server.lower().endswith(self.server.lower()[1:])
        else:
            valid = valid and server.lower() == self.server.lower()
        if self.channel.startswith("*"):
            valid = valid and channel.lower().endswith(self.channel.lower()[1:])
        else:
            valid = valid and channel.lower() == self.channel.lower()
        return valid
    
    def checkTrigger(self, msg):
        return re.findall(self.trigger, msg)
    
    def performAction(self, context, user, message, params):
        cmd = self.action.format(server=context.get_info("server"), channel=context.get_info("channel"), user=user, message=message, params=params)
        if self.type == RespoonType.MSG:
            cmd = "MSG {} {}".format(context.get_info("channel"), cmd)
        context.command(cmd)
    
    def getPrefs(self):
        prefs = {}
        prefs[ELEM_PREFIX + "name_{}".format(self.name)] = self.name
        prefs[ELEM_PREFIX + "{}_server".format(self.name)] = self.server
        prefs[ELEM_PREFIX + "{}_channel".format(self.name)] = self.channel
        prefs[ELEM_PREFIX + "{}_trigger".format(self.name)] = self.trigger
        prefs[ELEM_PREFIX + "{}_type".format(self.name)] = self.type.name
        prefs[ELEM_PREFIX + "{}_action".format(self.name)] = self.action
        return prefs
    
    @staticmethod
    def loadFromPref(name, method):
        server = method(ELEM_PREFIX + "{}_server".format(name))
        channel = method(ELEM_PREFIX + "{}_channel".format(name))
        trigger = method(ELEM_PREFIX + "{}_trigger".format(name))
        type = RespoonType[method(ELEM_PREFIX + "{}_type".format(name))]
        action = method(ELEM_PREFIX + "{}_action".format(name))
        return Respoon(name, server, channel, trigger, type, action)


def load_pref():
    resp_list = []
    for pref in hexchat.list_pluginpref():
        if pref.startswith(ELEM_PREFIX + "name"):
            name = hexchat.get_pluginpref(pref)
            resp_list.append(Respoon.loadFromPref(name, hexchat.get_pluginpref))
    return resp_list

def save_pref(resp_list):
    for pref in hexchat.list_pluginpref():
        if pref.startswith(ELEM_PREFIX):
            hexchat.del_pluginpref(pref)
    for resp in resp_list:
        for rpk, rpv in resp.getPrefs().items():
            hexchat.set_pluginpref(rpk, rpv)

respoon_list = []

def msg_cmd(word, word_eol, userdata):
    context = hexchat.get_context()
    for respoon in respoon_list:
        if respoon.checkOrigin(context.get_info("server"), context.get_info("channel")):
            params = respoon.checkTrigger(word[1])
            if len(params) > 0:
                respoon.performAction(context, word[0], word[1], params)

def respoon_cmd(word, word_eol, userdata):
    global respoon_list
    if len(word) < 2:
        hexchat.command("HELP RESPOON")
    elif word[1].upper() == "ADD":
        respoon_list = load_pref()
        if len(word) < 8:
            print("\00302Set your new respoon properties this way :")
            print("\00302  name : the name of your respoon (ex : auto_hello)")
            print("\00302  server : the server where your respoon should be active. Use '*' to match any (ex : *.server.com)")
            print("\00302  channel : the channel where your respoon should be active. Use '*' to match any (ex : #mychannel)")
            print("\00302  trigger : the regex that trigger your respoon. Keep the double-quote if your regex has spaces (ex : \"^Hello.*$\")")
            print("\00302  MSG|CMD : Use MSG if your respoon will send a message. Use CMD to perform a command.")
            print("\00302  action : the action to perform (ex: \"Hi {user} !\" for a MSG type or \"NOTICE {user} Hi {user} !\" for a CMD type)")
            print("")
            print("\00302You can use those escape sequences in the action property :")
            print("\00302  {user} : the nick of the user")
            print("\00302  {message} : the full message that has been sent")
            print("\00302  {server} : the server where the message has been sent")
            print("\00302  {channel} : the channel where the message has been sent")
            print("\00302  {params[x]} : the match of your regex at index 'x'")
            print("")
            print("\00302Example (MSG type) :")
            print("\00302  with trigger \"^!say (.+)$\"")
            print("\00302  and action \"{user} said ${params[0]}\"")
            print("\00302  if someone called User1234 says \"!say hi everyone !\" your respoon will send \"User1234 said hi everyone !\"")
            print("")
            hexchat.command("SETTEXT /RESPOON ADD <name> <server> <channel> \"<trigger>\" MSG|CMD <action>")
            hexchat.command("SETCURSOR 13")
        elif any(respoon.name.lower() == word[2].lower() for respoon in respoon_list):
            print("\00303A respoon with that name already exists !\017")
        else:
            name = word[2]
            server = word[3]
            channel = word[4]
            trigger = word[5]
            type = RespoonType[word[6]]
            action = word_eol[7]
            respoon_list.append(Respoon(name, server, channel, trigger, type, action))
            save_pref(respoon_list)
            print("\00304Your respoon \"{}\" has been created".format(name))
            hexchat.command("RESPOON SHOW {}".format(name))
    elif word[1].upper() == "LIST":
        respoon_list = load_pref()
        titles = ["name", "server", "channel", "trigger", "type"] #, "action"]
        cols_len = [len(title) for title in titles]
        for respoon in respoon_list:
            for i in range(len(titles)):
                cols_len[i] = max(cols_len[i], len("{}".format(getattr(respoon, titles[i]).name if titles[i] == "type" else getattr(respoon, titles[i]))))
        line = '\00306+-' + '-+-'.join('-'*l for l in cols_len) + '-+\017'
        pline = '\00306|\017 ' + ' \00306|\017 '.join("{params[" + str(i) + "]:<" + str(cols_len[i]) + "}" for i in range(len(cols_len))) + ' \00306|\017'
        print(line)
        print(pline.format(params=titles))
        print(line)
        for respoon in respoon_list:
            print(pline.format(params=[getattr(respoon, title).name if title == "type" else getattr(respoon, title) for title in titles]))
        print(line)
    elif word[1].upper() == "SHOW":
        respoon_list = load_pref()
        if len(word) < 3:
            print("\00303You have to specify a respoon name !\017")
            hexchat.command("SETTEXT /RESPOON SHOW <name>")
            hexchat.command("SETCURSOR 14")
        elif not any(respoon.name.lower() == word_eol[2].lower() for respoon in respoon_list):
            print("\00303This respoon doesn't exists !\017")
        else:
            respoon = next(r for r in respoon_list if r.name.lower() == word_eol[2].lower())
            properties = ["name", "server", "channel", "trigger", "type", "action"]
            for prop in properties:
                print("\00307{}\017 : \00306{}\017".format(prop, getattr(respoon, prop)))
    elif word[1].upper() == "EDIT":
        respoon_list = load_pref()
        if len(word) < 8:
            print("\00303You have to specify a respoon name and properties to edit !\017")
            hexchat.command("SETTEXT /RESPOON EDIT <name> <server> <channel> \"<trigger>\" MSG|CMD <action>")
            hexchat.command("SETCURSOR 14")
        elif not any(respoon.name.lower() == word[2].lower() for respoon in respoon_list):
            print("\00303This respoon doesn't exists !\017")
        else:
            for i in range(len(respoon_list)):
                if respoon_list[i].name.lower() == word[2].lower():
                    respoon_list[i].server = word[3]
                    respoon_list[i].channel = word[4]
                    respoon_list[i].trigger = word[5]
                    respoon_list[i].type = RespoonType[word[6]]
                    respoon_list[i].action = word_eol[7]
                    break
            save_pref(respoon_list)
            print("\00304Your respoon \"{}\" has been edited".format(word[2]))
            hexchat.command("RESPOON SHOW {}".format(word[2]))
    elif word[1].upper() == "DELETE":
        respoon_list = load_pref()
        if len(word) < 3:
            print("\00303You have to specify a respoon name !\017")
            hexchat.command("SETTEXT /RESPOON DELETE <name>")
            hexchat.command("SETCURSOR 16")
        elif not any(respoon.name.lower() == word_eol[2].lower() for respoon in respoon_list):
            print("\00303This respoon doesn't exists !\017")
        else:
            for i in range(len(respoon_list)):
                if respoon_list[i].name.lower() == word_eol[2].lower():
                    del respoon_list[i]
                    break
            save_pref(respoon_list)
            print("\00304The respoon \"{}\" has been deleted".format(word_eol[2]))
    else:
        hexchat.command("HELP RESPOON")
    return hexchat.EAT_ALL

respoon_list = load_pref()
hexchat.hook_print("Channel Message", msg_cmd),
hexchat.hook_print("Channel Msg Hilight", msg_cmd)
hexchat.hook_command('RESPOON', respoon_cmd, help="/RESPOON ADD|LIST|SHOW|EDIT|DELETE")

print("\00307{} v{}\017 : Activated with \00306{} respoons\017 !".format(__module_name__, __module_version__, len(respoon_list)))