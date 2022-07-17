import ujson
import asyncio
import aiohttp
from urllib.parse import quote as _uriquote
         
INVIDIOUS_API = 'api.invidious.io'

# The default api host
API_VERSION = 1
API_HOST = 'inv.riverside.rocks'

def _get_and_set_api(value = None, version = None):
    global API_VERSION, API_HOST
    if value is None and version is None:
        return 'https://' + API_HOST + '/api/v{}'.format(API_VERSION)

class Route:
    API_URI = _get_and_set_api()

    def __init__(self, method, path, **parameters):
        self.method = method
        self.path = path
        url = self.API_URI + self.path
        if parameters:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in parameters.items()})
        self.url = url

class HTTPClient:
    
    def __init__(self, loop, session = None):
        self.loop = loop
        self.__session = session
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; rv:102.0) Gecko/20100101 Firefox/102.0'

    def __del__(self):
        self.loop.create_task(self.__session.close())

    async def request(self, route, **kwargs):
        method = route.method
        url = route.url

        # Set headers
        headers = {
            'user-agent': self.user_agent
        }

        if 'json' in kwargs:
            headers['content-type'] = 'application/json'
            kwargs['data'] = ujson.dumps(kwargs.pop('json'))

        kwargs['headers'] = headers

        async with self.__session.request(method, url, **kwargs) as response:
            if response.status != 200:
                print(response.text)
                if response.status == 429:
                    raise RuntimeError('ratlimited')
                return None

            data = await response.json()

            return data

    def get_channel(self, channel_id):
        return self.request(Route('GET', '/channels/{channel_id}', channel_id=channel_id))

    def get_channels(self, query):
        params = {
            'q': query,
            'type': 'channel'
        }
        return self.request(Route('GET', '/search', params=params))

    def get_video(self, video_id):
        return self.request(Route('GET', '/videos/{video_id}', video_id=video_id))

    def get_stats(self):
        return self.request(Route('GET', '/stats'))

    def get_comments(self, video_id):
        raise NotImplementedError

    def get_trending(self, catagory):
        return self.request(Route('GET', '/trending'))

    def get_popular(self):
        route = Route('GET', '/popular')
        return self.request(route) 

    def get_search_result(self, query, page=1):
        params = {
            'q': query,
            'page': page,
            'type': 'video'
        }
        return self.request(Route('GET', '/search'), params=params)

