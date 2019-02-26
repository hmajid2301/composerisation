class IncorrectConfigException(Exception):
    def __init__(self, config_name, incorrect_key):
        self.config_name = config_name
        self.incorrect_key = incorrect_key
