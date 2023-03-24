from discord.ext import commands
from collections import Counter
from core.utils.helpers import JsonGuildDB

import os


class Red(commands.Bot):
    def __init__(self, cli_flags, **kwargs):
        self._shutdown_mode = None

        self.db = JsonGuildDB("core/data/settings.json",
                              autosave=True,
                              create_dirs=True)

        def prefix_manager(bot, message):
            global_prefix = self.db.get_global("prefix", [])

            if message.guild is None:
                return global_prefix

            server_prefix = self.db.get(message.guild, "prefix", [])

            return server_prefix if server_prefix else global_prefix

        # prioridade: args que passaram > bandeiras de cli > banco de dados
        if "command_prefix" not in kwargs:
            if cli_flags.prefix:
                kwargs["command_prefix"] = lambda bot, message: cli_flags.prefix
            else:
                kwargs["command_prefix"] = None

        if kwargs["command_prefix"] is None:
            kwargs["command_prefix"] = prefix_manager

        self.counter = Counter()
        self.uptime = None

        super().__init__(**kwargs)

    async def is_owner(self, user, allow_coowners=True):
        if allow_coowners:
            if user.id in self.settings.coowners:
                return True

        return await super().is_owner(user)

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)

            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)

            for page in pages:
                await ctx.send(page)

    async def logout(self, *, restart=False):
        """quita a kama com o código de saída 0 (exit code 0)
        
        se restart estiver como True, o código de saída será então 26.
        então assim, o launcher reiniciará a kama..."""

        self._shutdown_mode = not restart

        await super().logout()

    def list_packages(self):
        """lista as packages presentes na pasta de cogs"""

        return os.listdir("cogs")