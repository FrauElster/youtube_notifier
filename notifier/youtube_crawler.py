import logging
from datetime import datetime
from typing import Dict, List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from notifier.STRINGS import STRINGS
from notifier.filehandler import load_file


LOGGER: logging.Logger = logging.getLogger(__name__)

class Video:
    def __init__(self, title:str, id: str, querry: str):
        self.title: str = title
        self.url: str = f'https://www.youtube.com/watch?v={id}'
        self.querry: str = querry

    def serialize(self):
        return f'{self.querry} - {self.title}: {self.url}'

class YoutubeCrawler:
    def __init__(self):
        secrets: Dict[str, str] = self._load_config()
        self.youtube = build(serviceName='youtube', version='v3', developerKey=secrets["youtube_api_key"])
        LOGGER.info(f'{type(self).__name__} initialized')

    def search(self, search_term:str, last_check_date: datetime) -> List[Video]:
        videos: List[Video] = []

        search_response = self.youtube.search().list(
            q=search_term,
            part='id,snippet',
            order='date',
            type='video',
            maxResults=50
        ).execute()

        for search_result in search_response.get('items', []):
            search_result_date_str: str = search_result['snippet']['publishedAt']
            search_result_date_str = search_result_date_str.replace("T", " ").replace("Z", " ").split(".")[0]
            search_result_date: datetime = datetime.strptime(search_result_date_str, '%Y-%m-%d %H:%M:%S')
            if search_result_date < last_check_date:
                break

            videos.append(Video(title=search_result['snippet']['title'], id=search_result['id']['videoId'], querry=search_term))

        LOGGER.info(f'Querrying {search_term}: found {len(videos)} new results')
        return videos

    @staticmethod
    def _load_config() -> Dict[str, str]:
        obligated_keys: List[str] = ["youtube_api_key"]

        config: Dict[str, str] = load_file(STRINGS.SECRETS_FILE)

        for obligated_key in obligated_keys:
            if obligated_key not in config.keys() or not config[obligated_key]:
                raise ValueError(f'{obligated_key} not specified in {STRINGS.SECRETS_FILE}')

        return config
