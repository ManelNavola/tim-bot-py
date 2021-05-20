from helpers.command import Command
from helpers.translate import tr


async def set_language(cmd: Command, language: str):
    if cmd.guild:
        if cmd.user.member.guild_permissions.administrator:
            cmd.guild.set_lang(language)
            await cmd.send_hidden(tr(language, "SETUP.LANG", lang=tr(language, "LANGUAGE")))
        else:
            await cmd.error(tr('en', "SETUP.ADMIN"))
    else:
        cmd.user.set_lang(language)
        await cmd.send_hidden(tr(language, "SETUP.LANG", lang=tr(language, "LANGUAGE")))
