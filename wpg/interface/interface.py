import os

from wpg.engine.engine import Engine
from wpg.interface.color import Color
from wpg.interface.menu import Menu


class Interface:
    def __init__(self):

        self.engine = Engine()
        self.show_instructions = True
        self.current_menu = None

        # Declare Menus.
        self.menu_main = None
        self.menu_editor = None
        self.menu_generator = None
        self.menu_data = None

        # Initialize Commands.
        self.initialize_commands()

    # ==================================================================================================================
    # Initialize
    # ==================================================================================================================

    def initialize_commands(self):
        self.initialize_main_menu()
        self.initialize_data_menu()
        self.initialize_editor_menu()
        self.initialize_generator_menu()
        self.current_menu = self.menu_main

    def initialize_main_menu(self):
        self.menu_main = Menu("Main Menu", "Word Engine Main Menu.")
        self.menu_main.add_command(
            key="data",
            desc_text="Load, save and import databases.",
            action=self.cmd_go_to_data
        )
        self.menu_main.add_command(
            key="editor",
            desc_text="Add, remove, and verify words in the database.",
            action=self.cmd_go_to_editor
        )
        self.menu_main.add_command(
            key="generator",
            desc_text="Go to the generator mode, where you can create new puzzles.",
            action=self.cmd_go_to_generator
        )
        self.menu_main.add_command(
            key="exit",
            desc_text="Exit this program.",
            action=self.cmd_exit
        )

    def initialize_data_menu(self):
        self.menu_data = Menu("Data Menu", "Import, save, and export word databases.")
        self.menu_data.add_command(
            key="load_db",
            desc_text="Load a database for editing.",
            usage_text="$ [file_path]",
            action=self.cmd_load_db
        )
        self.menu_data.add_command(
            key="load_txt",
            desc_text="Create a new database from a text file.",
            usage_text="$ [file_path]",
            action=self.cmd_load_txt
        )
        self.menu_data.add_command(
            key="info",
            desc_text="Get the stats and information about the currently loaded database.",
            action=self.cmd_info
        )
        self.menu_data.add_command(
            key="save",
            desc_text="Save the database.",
            action=self.cmd_save
        )
        self.menu_data.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )

    def initialize_editor_menu(self):
        self.menu_editor = Menu("Editor Menu", "Edit, add, remove, verify words.")
        self.menu_editor.add_command(
            key="add",
            desc_text="Add the word(s) to the database.",
            usage_text="$ [word]",
            action=self.cmd_add,
        )
        self.menu_editor.add_command(
            key="remove",
            desc_text="Remove the word(s) from the database.",
            usage_text="$ [word]",
            action=self.cmd_remove
        )
        self.menu_editor.add_command(
            key="verify",
            desc_text="Enter the verification mode.",
            action=self.cmd_verify
        )
        self.menu_editor.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )

    def initialize_generator_menu(self):
        self.menu_generator = Menu("Generator Menu", "Generate and test word puzzles.")
        self.menu_generator.add_command(
            key="generate",
            desc_text="Generate a set of puzzles into an output folder.",
            action=self.cmd_generate
        )
        self.menu_generator.add_command(
            key="single",
            desc_text="Generate a single puzzle for the given letters.",
            action=self.cmd_single,
            usage_text="$ [num_of_letters]"
        )
        self.menu_generator.add_command(
            key="inspect",
            desc_text="Inspect a word for anagrams.",
            action=self.cmd_inspect,
            usage_text="$ [word]"
        )
        self.menu_generator.add_command(
            key="back",
            desc_text="Return to the main menu.",
            action=self.cmd_go_to_main_menu
        )

    # ==================================================================================================================
    # Virtual Machine Loop
    # ==================================================================================================================

    def run(self):
        while True:
            self.run_select_mode()

    def show_header(self):
        print("Word Puzzle Engine {}".format(Color.set_green("1.0")))
        print("Loaded Database: {}".format(Color.set_green("None")))
        print("Current Mode: {}".format(Color.set_green(self.current_menu.name)))
        print("--------------------------------------")
        print

    @staticmethod
    def clear_terminal():
        os.system("clear || cls")

    @staticmethod
    def show_command(command):
        print(Color.set_yellow(command.usage_text.replace("$", command.key)))
        print(command.desc_text)
        print

    def show_menu(self, menu):
        for command in menu.commands:
            self.show_command(command)

    def run_select_mode(self):
        print
        if self.show_instructions:
            self.clear_terminal()
            self.show_header()
            self.show_menu(self.current_menu)
            self.show_instructions = False

        code = raw_input(Color.set_green("Enter Command: "))
        print

        key, args = self.read_input_string(code)
        self.execute_input_command(key, args)

    @staticmethod
    def read_input_string(input_string):
        input_array = input_string.split(" ")
        input_key = input_array[0].lower()
        if len(input_array) > 1:
            input_args = input_array[1:]
            return input_key, input_args
        else:
            return input_key, None

    def execute_input_command(self, key, args):
        command_found = False
        for command in self.current_menu.commands:
            if key == command.key:
                # Valid action found.
                command_found = True
                self.execute_command_with_args(command, args)

        # No action found
        if not command_found:
            print("Invalid command: '{}' not recognized.".format(key))

    @staticmethod
    def execute_command_with_args(command, args):
        if command.action is None:
            print("Command has no action.")
            return

        if command.has_args:
            if args is None:
                print("You must supply some input arguments.")
                print(command.usage_text)
            else:
                command.action(args)
        else:
            command.action()

    # ==================================================================================================================
    # Menu Commands
    # ==================================================================================================================

    def _go_to_menu(self, menu):
        self.current_menu = menu
        self.show_instructions = True

    def cmd_go_to_data(self):
        self._go_to_menu(self.menu_data)

    def cmd_go_to_editor(self):
        self._go_to_menu(self.menu_editor)

    def cmd_go_to_generator(self):
        self._go_to_menu(self.menu_generator)

    def cmd_go_to_main_menu(self):
        self._go_to_menu(self.menu_main)

    def cmd_exit(self):
        self.clear_terminal()
        exit(1)

    # ==================================================================================================================
    # Data Commands
    # ==================================================================================================================

    def cmd_load_db(self, args):
        file_path = args[0]
        print("Load DB: {}".format(file_path))
        self.engine.load_db(file_path)

    def cmd_load_txt(self, args):
        file_path = args[0]
        self.engine.load_txt(file_path)
        print("Load Text: {}".format(file_path))

    def cmd_save(self):
        self.engine.save()
        print("Save DB")

    def cmd_info(self):
        self.engine.print_info()
        print("Info")

    # ==================================================================================================================
    # Editor Commands
    # ==================================================================================================================

    def cmd_add(self, args):
        print("Add: {}".format(args))

    def cmd_remove(self, args):
        print("Remove: {}".format(args))

    def cmd_verify(self):
        print("Verify")

    # ==================================================================================================================
    # Generator Commands
    # ==================================================================================================================

    def cmd_single(self, args):
        n = int(args[0])
        print("Single: {}".format(n))

    def cmd_inspect(self, args):
        word = args[0]
        print("Inspect: {}".format(word))

    def cmd_generate(self):
        print("Generate")
