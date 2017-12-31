class Command:
    def __init__(self, key, desc_text, action, usage_text=None):

        self.key = key
        self.desc_text = desc_text
        self.usage_text = usage_text
        self.action = action

        if usage_text is None:
            self.usage_text = self.key
            self.has_args = False
        else:
            self.usage_text = usage_text.replace("$", key)
            self.has_args = True