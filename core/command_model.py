class CommandModel:
    def __init__(self, registry):
        self.registry = registry
        self.query = ""

    def set_query(self, query):
        self.query = query.strip().lower()

    def visible_commands(self):
        commands = [
            command
            for command in self.registry.palette_commands()
            if command.is_enabled()
        ]

        if not self.query:
            return commands

        return [
            command
            for command in commands
            if self.matches(command)
        ]

    def matches(self, command):
        haystack = " ".join(
            [
                command.name,
                command.id,
                command.category,
                command.shortcut or "",
            ]
        ).lower()

        return self.query in haystack

    def first_match(self):
        commands = self.visible_commands()

        if not commands:
            return None

        return commands[0]