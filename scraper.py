from typing import List
import requests
from bs4 import BeautifulSoup
import time


def load_soup(data_url: str) -> BeautifulSoup:
    """
    Utility function to request and parse player's website.

    Parameters:
        data_url (str): unique data url to identify player

    Returns:
        soup (BeautifulSoup): BeautifulSoup object parsed by html.parser
    """

    url = 'https://www.futbin.com{}'.format(data_url)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_price(data_url: str) -> dict:
    """
    Make request to futbin api to get player's price.

    Parameters:
        data_url (str): unique data url to identify player

    Returns:
        dict: dictionary with player's price
    """

    soup = load_soup(data_url)
    data_player_resource = soup.find(id='page-info').get('data-player-resource')
    url = 'https://www.futbin.com/21/playerGraph?type=daily_graph&year=21&player={}'.format(data_player_resource)
    r = requests.get(url)
    return r.json()


def get_stats(data_url: str) -> dict:
    """
    Scrape player's rating and in-game statistics and personal information.

    Parameters:
        data_url (str): unique data url to identify player

    Returns:
        dict: dictionary with player rating and statistic
    """

    soup = load_soup(data_url)
    game_attributes = soup.find_all('span', class_='ig-stat-name-tooltip')
    game_values = soup.find_all('div', class_='stat_val', style=False)
    personal_values = soup.find_all('td', class_='table-row-text', limit=7)
    personal_attributes = soup.find_all('th', limit=7)
    rating = soup.find('div', class_='pcdisplay-rat').get_text()
    game = {k.get_text(): v.get_text() for k, v in zip(game_attributes, game_values)}
    personal = {k.get_text(): v.get_text() for k, v in zip(personal_attributes, personal_values)}
    statistic = {**personal, **game, 'Rating': rating}
    time.sleep(0.5)
    return statistic


def get_links(pages: int) -> List:
    """
    Paginate trough futbin.com to scrape links to player's pages. Search has been limited to only gold players who
    are not goalkeepers.

    Parameters:
        pages (int): number of pages to scrape

    Returns:
        links: list of found links
    """

    links = []
    for i in range(1, pages + 1):
        try:
            r = requests.get('https://www.futbin.com/21/players?page={}&position=CB,LB,LWB,RB,RWB,CDM,CM,CAM,CF,ST,'
                             'LM,LW,LF,RM,RW,RF&version=gold'.format(i))
            soup = BeautifulSoup(r.text, 'html.parser')
            for link in soup.find_all('a', {'class': 'player_name_players_table'}):
                links.append(link.get('href'))
            time.sleep(2)
        except requests.exceptions.HTTPError:
            pass
    return links
