from disco.bot import Plugin
from disco.api.http import APIException
from disco.api.client import APIClient
from disco.types.guild import GuildMember
from roleBot import roleBotConfig

from commands.roleBot import roleBotConfig

MSG_INVALID_ROLE = '{}, I\'m sorry, I don\'t recognize that role. LPT: ' + \
                   'If you use the `!rolelist` command you\'ll be DM\'d a list of all of the available roles.'
MSG_ROLE_REMOVED = '{}, I have removed the `{}` role from you. Use the same command again to add the role back.'
MSG_ROLE_ADDED = '{}, You have been given the `{}` role! Use the same command again to remove this role from yourself.'
MSG_CANNOT_DM = '{}, I\'m sorry but I can\'t DM you! You have to enable the option under Server Settings > Privacy Settings.'

ROLE_ID_ADD_SUCCESS = '{}, the role {} has been added successfully! Good job!'
USE_VALID_ROLE = '{}, Uh, sorry there friend. You need to use a valid role.'
ROLE_ALREADY_ADDED = '{}, Oh, role {} was already added'

TRANSLATOR_ROLE_ADDED = '<@{}> has been given the role of Translator.'
TRANSLATOR_ROLE_REMOVE = 'The Translator role has been removed from <@{}>.'
INVALID_TARGET = '{}, you\'re not allowed to give a bot a role.'

USE_VALID_ID = '{}, that doesn\'t appear to be a valid user. Please try again with a valid userID.'

class RolePlugin(Plugin):

    @Plugin.command('role', parser=True)
    @Plugin.add_argument('role', help='Name of the role to add or remove from the user', nargs='?')
    def add_or_remove_role(self, event, args):

        if args.role == "translator":
            event.msg.reply("This role cannot be added via this command. Speak with a Proofreader or a Mod to acquire this role.").after(10).delete()
            event.msg.delete()
            return

        try:
            # ensure role is legit, bail early if role is not valid
            Role = roleBotConfig.roles[args.role]
        except:
            if args.role == None:
                return
            event.msg.reply(MSG_INVALID_ROLE.format(event.author.mention)).after(10).delete()
            event.msg.delete()
            return

        if Role in event.member.roles:
            event.member.remove_role(Role)
            event.msg.reply(MSG_ROLE_REMOVED.format(event.author.mention, args.role)).after(10).delete()
            event.msg.delete()
            message_to_announce = ("**{}#{}** ({}) removed the role `{}` from themself.").format(event.author.username, event.author.discriminator, event.author.id, args.role)
            self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)
        else:
            event.member.add_role(Role)
            event.msg.reply(MSG_ROLE_ADDED.format(event.author.mention, args.role)).after(10).delete()
            event.msg.delete()
            message_to_announce = ("**{}#{}** ({}) gave themself the role `{}`.").format(event.author.username, event.author.discriminator, event.author.id, args.role)
            self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)

#    @Plugin.command('test')
#    def testing(self, event):
#        message_to_announce = ("**{}#{}** ({}) did a test.").format(event.author.username, event.author.discriminator, event.author.id)
#        self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)
#        event.msg.reply("Test!").after(10).delete()
#        event.msg.after(10).delete()


    @Plugin.command('rolelist')
    def rolelist(self, event):
        """allows a user to DM themselves the entire list of roles that can be added"""
        Role = roleBotConfig.roles
        channel = event.author.open_dm()
        message = 'Hi there! The available role commands are as follows:```{}```'
        commands = ['!role {}'.format(role) for role in sorted(Role)]

        try:
            channel.send_message(message.format('\n'.join(commands)))
        except APIException as ex:
            if ex.code == 50007:  # invlid message send user
                event.msg.reply(MSG_CANNOT_DM.format(event.author.mention)).after(10).delete()
            else:
                event.msg.reply('There was a disturbance in the force. Please contact a mod.').after(10).delete()
        message_to_announce = ("**{}#{}** ({}) used the command `!rolelist`").format(event.author.username, event.author.discriminator, event.author.id)
        self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)
        event.msg.after(10).delete()

    @Plugin.command('translator', parser=True)
    @Plugin.add_argument('userID', help='the ID of the user to gain the translator role', nargs='?')
    def add_or_remove_translator_role(self, event, args):
        guildID = 347510678858498050
        Role = roleBotConfig.roles['translator']

        #verify that the user has the correct ranks to be using this command
        if not any(role in roleBotConfig.adminRoles.values() for role in event.member.roles):
            event.msg.after(10).delete()
            return

        #prevents an API error when no userID is passed in.
        if args.userID == None:
            return

        #check to see if it's an @mention or not
        if args.userID[0] == "<":
            print args.userID
            if args.userID[2] == '!':
                args.userID = args.userID[3:-1]
                print args.userID
            else:
                args.userID = args.userID[2:-1]
                print args.userID

        #This validates the user and gets the member object.
        try:
            user_to_be_given_role = self.bot.client.api.guilds_members_get(guildID, args.userID)
        except APIException:
            event.msg.reply("That's not a valid user ID for this server.").after(10).delete()
            return

        #If they have the role, remove it. Otherwise, add it.
        if Role in user_to_be_given_role.roles:
            self.bot.client.api.guilds_members_roles_remove(guildID, args.userID, Role)
            event.msg.reply(TRANSLATOR_ROLE_REMOVE.format(args.userID)).after(10).delete()
            event.msg.delete()
            message_to_announce = ("**{}#{}** ({}) removed the Translator role from {}").format(event.author.username, event.author.discriminator, event.author.id, args.userID)
            self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)
        else:
            self.bot.client.api.guilds_members_roles_add(guildID, args.userID, Role)
            event.msg.reply(TRANSLATOR_ROLE_ADDED.format(args.userID)).after(10).delete()
            event.msg.delete()
            message_to_announce = ("**{}#{}** ({}) added the Translator role to {}").format(event.author.username, event.author.discriminator, event.author.id, args.userID)
            self.bot.client.api.channels_messages_create(roleBotConfig.adminChannels['role_Bot_Log'], message_to_announce)
