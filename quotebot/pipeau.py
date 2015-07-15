from selenium import webdriver
from bs4 import BeautifulSoup
from bs4_helpers import element_contents

__all__ = ('pipotronic', 'eddy_malou')

def load_page_source(url):
    """Loadng an url and returns its source."""
    driver = webdriver.PhantomJS()
    driver.get(url)
    page_source = driver.page_source
    driver.quit()
    return page_source

def pipotronic():
    page_source = load_page_source('http://www.pipotronic.com')
    soup = BeautifulSoup(page_source)
    base_element = soup.find('p', { 'id': 'pipotot' })
    return element_contents(base_element)

def eddy_malou():
    page_source = load_page_source('http://eddy-malou.com')
    soup = BeautifulSoup(page_source)
    base_element = soup.find('p', { 'id': 'maloutot' })
    return element_contents(base_element)
