class Color:

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    END = '\033[0m'

    def __init__(self):
        pass

    @staticmethod
    def set_yellow(string):
        return Color.YELLOW + string + Color.END

    @staticmethod
    def set_green(string):
        return Color.GREEN + string + Color.END

    @staticmethod
    def set_blue(string):
        return Color.BLUE + string + Color.END
