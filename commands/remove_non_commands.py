from disco.bot import Plugin, Config
from disco.bot.command import CommandError
from disco.types import message
from roleBot import roleBotConfig

#This feature is to prevent people from chatting in the reporting channels and the approval queue, so they can only use bot commands there.
#Doing so will help us keep everything organized.

UNAUTHORIZED_MSG = "{}, this channel is for bot-commands only."
UH_OH_WTF = "Some unknown error has occured."
BotIDNum = 380451786797875200

functions = ['role ', 'rolelist', 'translator ']

class noFunAllowed(Plugin):
    @Plugin.listen('MessageCreate')
    def yell_at_user(self, event):

        #only allow bot commands, anything that doesn't start with ! is not a bot command
        if event.message.content[0] != "!":

            #bot responding to itself is bad, infinite loops are bad
            if event.author.id == BotIDNum:
                return

            #admins can talk though
            if not any(role in roleBotConfig.adminRoles.values() for role in event.member.roles):
                event.message.reply(UNAUTHORIZED_MSG.format(event.author.mention)).after(10).delete()
                event.message.delete()

        if event.message.content[0] == "!":
            #determines if the funcion being called is a valid one or not, responds appropriately.
            for i in functions:
                if i in event.message.content:
                    return
            event.message.reply("Sorry, that isn't a valid command.").after(10).delete()
            event.message.delete()
