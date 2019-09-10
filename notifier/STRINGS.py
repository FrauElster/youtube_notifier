class STRINGS:
    # filenames
    TELEGRAM_FILE: str = 'telegram.yaml'
    OUTPUT_FILE: str = 'results.yaml'
    CONFIG_FILE: str = 'config.yaml'
    LOG_FILENAME: str = 'youtube_notifier.log'

    # messages
    TELEGRAM_EMPTY_QUERY: str = 'Your Query can`t be empty.\nType "/help" for help'
    TELEGRAM_ALREADY_REG_QUERIES: str = 'The following queries were already registered: '
    TELEGRAM_QUERIES:str = 'You have subscribed to the following queries: '
    TELEGRAM_REFUSED_QUERIES: str = 'You cant remove the following queries, because you don`t follow them: '
    TELEGRAM_REMOVED_QUERIES: str = 'You removed the following queries: '
    TELEGRAM_NOTIFICATION_MSG: str = 'We found new videos according to your queries:'
    TELEGRAM_LIST_MSG: str = 'You have currently subscribed to the following queries: '
    TELEGRAM_NO_NEW_VIDEOS: str = 'There were no new videos found to you subscribed queries.'
    TELEGRAM_UNKNOWN_COMMAND: str = 'Sorry I don`t know that command. Type "/help" to see the instructions'
    TELEGRAM_HELP: str = 'This service will notify you, if new videos of certain search terms are uploaded\n\n' \
                            'Type "/add {search term}" to add a search term. You can add multiple search terms separated by ", "\n' \
                            'Type "/rm {search term}" to remove a search term. You can remove multiple search terms separated by ", "\n' \
                            'Type "/list" to show all your subscribed search terms.' \
                            'Type "/check" to check for new uploads. There will be a check every 6hrs in addition to that' \
                            'Type "/start" will send you the welcome message as well as remove all your search terms"'
    TELEGRAM_WELCOME: str = 'Welcome to the YoutubeNotification\n\nType "/help" for an overview of all the available commands.'




