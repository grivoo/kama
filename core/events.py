import discord
import traceback
import datetime
import logging

from discord.ext import commands
from core.utils.chat_formatting import inline

log = logging.getLogger("red")


def init_events(bot):

    @bot.event
    async def on_connect():
        if bot.uptime is None:
            print("conectado ao discord. preparando tudo...")

    @bot.event
    async def on_ready():
        if bot.uptime is None:
            bot.uptime = datetime.datetime.utcnow()

            print("carregando e inicializando cogs...")

            total_channels = len([c for c in bot.get_all_channels()])
            total_users = len(set([m for m in bot.get_all_members()]))

            print("pronto e operacional em {} servidores...\n"
                  "".format(len(bot.guilds)))

    @bot.event
    async def on_command_error(error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await bot.send_cmd_help(ctx)

        elif isinstance(error, commands.BadArgument):
            await bot.send_cmd_help(ctx)

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("esse comando está desativado...")

        elif isinstance(error, commands.CommandInvokeError):
            # necessário testar se ainda funciona

            """
            no_dms = "não será possível enviar mensagens para este usuário"
            is_help_cmd = ctx.command.qualified_name == "help"
            is_forbidden = isinstance(error.original, discord.Forbidden)
            if is_help_cmd and is_forbidden and error.original.text == no_dms:
                msg = ("eu não pude enviar a mensagem de ajuda na sua dm. você me bloqueou e/ou desativou minha permissão de acessar a dm dos usuários deste servidor...")
                await ctx.send(msg)
                return
            """

            log.exception("excessão no comando '{}'"
                          "".format(ctx.command.qualified_name),
                          exc_info=error.original)

            message = ("ocorreu um erro no comando '{}'. veja seu console ou "
                       "logs para detalhes..."
                       "".format(ctx.command.qualified_name))

            exception_log = ("excessão no comando '{}'\n"
                             "".format(ctx.command.qualified_name))

            exception_log += "".join(traceback.format_exception(type(error),
                                     error, error.__traceback__))

            bot._last_exception = exception_log

            await ctx.send(inline(message))

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.CheckFailure):
            await ctx.send("⛔")

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("esse comando não está disponível para dms...")

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("esse comando está em cooldown. "
                           "tente novamente em {:.2f}s"
                           "".format(error.retry_after))

        else:
            log.exception(type(error).__name__, exc_info=error)

    @bot.event
    async def on_message(message):
        bot.counter["messages_read"] += 1

        await bot.process_commands(message)

    @bot.event
    async def on_resumed():
        bot.counter["sessions_resumed"] += 1

    @bot.event
    async def on_command(command):
        bot.counter["processed_commands"] += 1