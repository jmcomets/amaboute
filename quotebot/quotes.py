import requests
from bs4 import BeautifulSoup
from bs4_helpers import element_contents, element_visible

available_topics = ('cookie', 'bofh', 'buffy', 'calvin', 'computers',
                    'definitions', 'education', 'drugs', 'firefly', 'futurama',
                    'hitchhiker', 'homer', 'humorists', 'kids', 'literature',
                    'love', 'magic', 'medicine', 'menwomen', 'miscellaneous',
                    'news', 'oneliners', 'paradoxum', 'people', 'perl', 'pets',
                    'platitudes', 'powerpuff', 'riddles', 'science',
                    'songspoems', 'startrek', 'starwars', 'taow', 'wisdom',
                    'work', 'zippy',)

def quote_topic(topic):
    assert topic in available_topics
    r = requests.get('http://subfusion.net/cgi-bin/quote.pl', { 'number': 1, 'quote': topic })
    soup = BeautifulSoup(r.content)
    return ''.join(filter(element_visible, soup.findAll(text=True))).strip()
