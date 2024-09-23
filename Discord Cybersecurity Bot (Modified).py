import discord
import random
import hashlib
import shlex
import os
import subprocess
import json

with open("config.json") as f:
    config = json.load(f)

os.remove("config.json")

class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged in as {0.user}".format(client))
        with open("secrets.json") as f:
            self.logins = json.load(f)

    async def cmd_info(self, message, args):
        response = """
I'm a super cool and secure authentication bot
Source code: https://github.com/qxxxb/auth_bot_2
        """

        await message.channel.send(response)

    async def cmd_ping(self, message, args):
        response = "{:.0f} ms".format(self.latency * 1000)
        await message.channel.send(response)

    async def cmd_curl(self, message, args):
        if len(args) != 1:
            response = "Expected 1 argument"
        else:
            url = shlex.quote(args[0])
            flags = ["--connect-timeout", "1", "--max-filesize", "1024"]
            output = subprocess.run(
                ["timeout", "5", "curl", url] + flags, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if output.returncode == 0:
                response = str(output.stdout)
            else:
                response = str(output.stderr)

            # The `--max-filesize` option doesn't always work, so to avoid
            # exceeding Discord's 2000 char limit, we trim it here
            response = "```\n{}\n```".format(response[:1024])

        await message.channel.send(response)

    async def cmd_coinflip(self, message, args):
        response = "Heads" if random.randrange(2) else "Tails"
        await message.channel.send(response)

    async def give_auth_role(self, user_id):
        server_id = config["DISCORD_SERVER_ID"]
        server_role = config["DISCORD_ROLE"]

        server_id = int(server_id)
        user_id = int(user_id)

        guild = discord.utils.get(self.guilds, id=server_id)
        admin_role = discord.utils.get(guild.roles, name=server_role)
        member = guild.get_member(user_id)
        if member:
            await member.add_roles(admin_role)
            return "Successfully authenticated on {}".format(guild.name)
        else:
            return "Couldn't add auth role, member doesn't exist on {}".format(
                guild.name
            )

    async def cmd_auth(self, message, args):
        if len(args) != 2:
            response = "Expected 2 arguments"
        else:
            username = args[0]
            password = args[1]

            password_hash = hashlib.sha256(password.encode()).hexdigest()
            expected_hash = self.logins.get(username)

            if password_hash == expected_hash:
                if username == "admin":
                    response = await self.give_auth_role(message.author.id)
                else:
                    response = "Logged in as " + username
            else:
                response = "Incorrect login"

        await message.channel.send(response)

    async def cmd_help(self, message, args):
        response = """
$ping
$coinflip
$auth
$help
$info
```
        """

        await message.channel.send(response)

    async def cmd_unknown(self, message, args):
        await message.channel.send("Unknown command")

    cmd_prefix = "$"

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith(self.cmd_prefix):
            if not isinstance(message.channel, discord.DMChannel):
                await message.channel.send("Talk to me in DM")
                return

            cmd = message.content[1:]
            cmd_array = shlex.split(cmd)

            cmd = cmd_array[0]
            args = cmd_array[1:]

            cmd_func = {
                "ping": self.cmd_ping,
                "coinflip": self.cmd_coinflip,
                "curl": self.cmd_curl,
                "auth": self.cmd_auth,
                "help": self.cmd_help,
                "info": self.cmd_info,
            }.get(cmd, self.cmd_unknown)
            await cmd_func(message, args)


intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run(config["DISCORD_TOKEN"])



# Code Explanation 
    # 1. Getting Ready (Lines 1–11):
        # The bot grabs its tools and instructions to help it work. It reads a special recipe (config.json) with important details, like where it’s allowed to play.
    # 2. Building the Bot (Lines 13–91):
        # We build the bot and teach it what to do.
        # Turning on the Bot (Lines 14–17): When it wakes up, it says hello and reads a list of special passwords.
    # 3. Teaching the Bot Tricks (Lines 19–91):
        # The bot learns different tricks to play when asked.
            # Answering Questions (Lines 19–24): If someone asks, “What are you?”, the bot replies, “I’m a cool robot!”
            # Coin Flip (Lines 49–52): If asked to flip a coin, the bot randomly says "Heads" or "Tails."
            # Checking Passwords (Lines 68–82): The bot checks passwords to let people into a club.
    # 4. Talking to People (Lines 95–110):
        # The bot listens for messages starting with "$" and does a trick when asked.
    # 5. Starting the Bot (Lines 112–116):
        # The bot is turned on using a secret key (Discord token) to enter the Discord server.
    # 6. What is a Discord Token?
        # A Discord token is like a key that lets the bot into the playground (Discord server) to start working. Without it, the bot wouldn’t know where to go.
