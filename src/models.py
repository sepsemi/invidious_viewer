from datetime import datetime
from src.http import API_HOST

def number_to_unit(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

class Author:
    def __init__(self, data):
        self.id = data['authorId']
        self.name = data['author']
        self.url = data['authorUrl']

    def __str__(self):
        return self.name

class Video:
    def __init__(self, data):
        self.id = data['videoId']
        self.type = data['type']
        self.title = data['title']
        self.views = number_to_unit(int(data['viewCount']))
        self.lenght = '{lenght}s'.format(lenght=data['lengthSeconds'])
        self.published = datetime.fromtimestamp(data['published'])
        self.author = Author(data)

    @property
    def url(self):
        return 'https://{}/watch?v={}'.format(API_HOST, self.id)

    def __str__(self):
        return 'title={}, author={}'.format(self.title, self.author.name)
