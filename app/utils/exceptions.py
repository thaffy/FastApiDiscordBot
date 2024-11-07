class DiscordBotNotInitializedError(Exception):
    def __init__(self, message: str = "Discord bot is not initialized"):
        self.message = message
        super().__init__(message)