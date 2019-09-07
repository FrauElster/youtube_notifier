class STRINGS:
    # filenames
    OUTPUT_FILE: str = 'results.yaml'
    CONFIG_FILE: str = 'config.yaml'
    SECRETS_FILE: str = 'secrets.yaml'
    LOG_FILENAME: str = 'youtube_notifier.log'

    # messages
    TELEGRAM_WELCOME: str = 'Welcome to the YoutubeNotification\n\n' \
                            'This service will notify you, if new videos of certain search terms are uploaded\n\n' \
                            'Type "/add {search term}" to add a search term.\n' \
                            'Type "/rm {search term}" to remove a search term\n' \
                            'Type "/check" to check for new uploads. There will be a check every 6hrs in addition to that'
    TELEGRAM_EMPTY_QUERY: str = 'Your Query can`t be empty.\nType "/help" for help'
    TELEGRAM_ALREADY_REG_QUERIES: str = 'The following queries were already registered: '
    TELEGRAM_QUERIES:str = 'You have subscribed to the following queries: '
    TELEGRAM_REFUSED_QUERIES: str = 'You cant remove the following queries, because you don`t follow them: '
    TELEGRAM_REMOVED_QUERIES: str = 'You removed the following queries: '


