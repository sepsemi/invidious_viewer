import os
import uvloop
import asyncio

from src.client import YoutubeClient
from pyfzf.pyfzf import FzfPrompt

def create_playlist(client, result, items):
    processes = []
    for index, element in enumerate(items):
        if index < 1:
            processes.append(client.play_audio(result[element], paused = False))
        else:
            processes.append(client.play_audio(result[element], paused=True))
    
    return processes

def get_videos_from_fzf_display(fzf, result):
    pretty_result = ['{i}. {v.title} {v.author} {v.published} {v.views} {v.lenght} {v.url}'.format(i=i, v=v) for i, v in enumerate(result, start=1)]
    selected = fzf.prompt(pretty_result, '--layout=reverse-list --multi --cycle')
    
    if len(selected) == 1:
        # We selected just 1 result return one item
        return [result[int(selected[0].split('.')[0]) -1]]
    
    # Otherwise we have multiple results and we need to create a list
    return [result[int(line.split('.')[0]) -1] for line in selected]
     
async def main(loop):
    client = YoutubeClient(loop)
    fzf = FzfPrompt()
    
    result = None
    while True:
        text = input('> ')

        if isinstance(text, str) and len(text) > 0:
            if '=popular' in text:
                result = await client.popular()            
            else: 
                result = await client.search(text)
        
        elif isinstance(text, str) and len(text) == 0:
            # We want another view of the previous run
            result = result

         # Promt the fzf promt to select one or more videos
        videos = get_videos_from_fzf_display(fzf, result)

        for index, video in enumerate(videos, start=1):
            # Start the mpv process and detach
            #process = client.play_video(video.url)
            process = client.play_video(video.url)
            
            if len(videos) > 1:
                # It's a playlist so we should wait for the process to exit and then release
                print('[playlist({}-{})] playing: {video.title} {video.author} {video.published} {video.views} {video.lenght} {video.url}'.format(
                    len(videos), index, video=video))

                process.wait()
            
            else:
                print('playing: {video.title} {video.author} {video.published} {video.views} {video.lenght} {video.url}'.format(video=video))
                
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main(loop))

