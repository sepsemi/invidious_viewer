import os
import asyncio
import aiohttp
import subprocess

from src.http import HTTPClient, API_HOST
from src.models import Author, Video
from src.ipc import MpvIPCClient

class YoutubeClient:

    def __init__(self, loop):
        self.loop = loop
        self.api = API_HOST
        self.mpv_path = '/usr/bin/mpv'
        self.aiohttp_session = aiohttp.ClientSession()
        self.ipc = MpvIPCClient(self.mpv_ipc_socket_path)
        self.http = HTTPClient(loop=loop, session=self.aiohttp_session)
    
    @property
    def mpv_ipc_socket_path(self):
        # Try and accept XDG standards
        xdg_runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
        if xdg_runtime_dir is not None:
            return xdg_runtime_dir + '/mpv_ipc_socket'
        
        # move to /tmp/ instead
        return '/tmp/mpv_ipc_socket'

    async def popular(self):
        return [Video(element) for element in await self.http.get_popular()]

    async def trending(self):
        return [Video(element) for element in await self.http.get_trending()]

    async def search(self, query):
        pages, tasks, results = 5, [], []
        for page in range(pages):
            tasks.append(self.loop.create_task(self.http.get_search_result(query, page=page + 1)))
        
        for task in asyncio.as_completed(tasks):
            results.extend(await task)

        return [Video(element) for element in results]

    def play_video(self, url):
        # Launches the process and plays the video
        return subprocess.Popen([
            self.mpv_path,
            "--input-ipc-server={}".format(self.mpv_ipc_socket_path),
            "--fullscreen=yes", 
            "--ytdl-format=bestvideo[height<=1080]+bestaudio/best[height<=1080]", 
            url
        ],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL)

    def play_audio(self, url, paused=False):
        # Launches the process and plays audio only
        arguments = [
            self.mpv_path,
            "--input-ipc-server={}".format(self.mpv_ipc_socket_path),
            "--no-video",
            "--vo=null",
            "--ytdl-format=bestaudio[ext=m4a]",
            url
        ]
        if paused is True:
            arguments.insert(2, '--pause')

        return subprocess.Popen(arguments, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL)

        def from_anonymous_youtube_playlist(self, string):
            raise NotImplementedError

        def from_youtube_playlist_file(self, path):
            raise NotImplementedError

