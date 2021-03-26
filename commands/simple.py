from commands.command import Command
class Hello(Command):
    async def issue(self):
        self.send("Hey")