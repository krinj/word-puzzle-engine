from wpg.interface.command import Command


class Menu:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.commands = []  # Commands that can be executed from this menu.

    def add_command(self, key, desc_text, action, usage_text=None):
        command = Command(key, desc_text, action, usage_text)
        self.commands.append(command)
