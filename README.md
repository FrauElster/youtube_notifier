# Youtube Notifier

Is a telegram bot where users can subscribe to certain search terms and will be notified if a new video
 matching these was uploaded. The check is done periodically after 6 hours or manually by the user with the "/check"
  command.
  
# Installation

```shell script
git clone {url} ~/.youtube_new
cd ~/.youtube_new
pip install --user -r requirements.txt
```

# Usage

Run it simply by
```shell script
cd ~/.youtube_new/
python -m notifier
```

The `config.yaml` file has to contain:

|key|description|
|---|---|
|youtube_api_key|The youtube api key|
|telegram_bot_token|The telegram bot token|

# Telegram commands

- "/add {search term}" to add a search term. You can add multiple search terms separated by ", "
- "/rm {search term}" to remove a search term. You can remove multiple search terms separated by ", "
- "/list" to show all your subscribed search terms.
- "/check" to check for new uploads. There will be a check every 6hrs in addition to that
- "/start" will send you the welcome message as well as remove all your search terms"
