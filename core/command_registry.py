from core.command import Command


class CommandRegistry:
    def __init__(self):
        self._commands = []

    def register(self, command: Command):
        self._commands.append(command)
        return command

    def all(self):
        return list(self._commands)

    def find(self, command_id):
        for command in self._commands:
            if command.id == command_id:
                return command

        return None

    def help_commands(self):
        return [
            command
            for command in self._commands
            if command.show_in_help
        ]

    def palette_commands(self):
        return [
            command
            for command in self._commands
            if command.show_in_palette
        ]

    def by_category(self, category):
        return [
            command
            for command in self._commands
            if command.category == category
        ]