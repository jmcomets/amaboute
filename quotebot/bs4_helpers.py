import re

def element_contents(element):
    if isinstance(element, str):
        return element.strip()
    return ' '.join(filter(None, map(element_contents, element.contents))).strip()

def element_visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    else:
        return True
