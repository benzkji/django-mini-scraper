import datetime
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from .base import BaseParser


class HTMLParser(BaseParser):

    @classmethod
    def get_soup_text(self, soup, selector, all=False):
        if selector:
            if all:
                text = ''
                result_soup = soup.select(selector)
                for item in result_soup:
                    text += item.get_text(' ')
                return text
            else:
                result_soup = soup.select_one(selector)
                if result_soup:
                    return result_soup.get_text(' ')
        return ''

    def conf(self, key):
        return self.from_dict(self.node_config_html, key)

    def get_link(self, item_soup):
        return self.get_link_html(item_soup)

    def get_link_html(self, item_soup):
        if self.conf('link_node'):
            link = item_soup.select_one(self.conf('link_node'))
        elif item_soup.name == 'a':
            link = item_soup
        else:
            link = item_soup.select_one('a')
        if link:
            if self.conf('link_attribute'):
                attr = self.conf('link_attribute')
            else:
                attr = 'href'
            link_value = link.attrs.get(attr, '')
            if not link_value.startswith('http'):
                original_url = urlparse(self.source.url)
                link_value = '{}://{}{}'.format(
                    original_url.scheme,
                    original_url.netloc,
                    link_value,
                )
            if self.conf('link_strip_get'):
                split = link_value.split('?')
                link_value = split[0]
                link_value = link_value.replace('?', '')
            return link_value
        return ''

    def get_guid(self, item_soup):
        return self.get_guid_html(item_soup)

    def get_guid_html(self, item_soup):
        if self.conf('guid_node'):
            guid = item_soup.select_one(self.conf('guid_node'))
        else:
            guid = item_soup  # it's the wrapper node
        if guid:
            if self.conf('guid_attribute'):
                attr = self.conf('guid_attribute')
            else:
                attr = 'id'
            guid_value = guid.attrs.get(attr, '')
            return guid_value
        return ''

    def get_title(self, item_soup):
        return self.get_title_html(item_soup)

    def get_title_html(self, item_soup):
        return self.get_soup_text(item_soup, self.conf('title_node'))

    def get_price(self, item_soup):
        return self.get_price_html(item_soup)

    def get_price_html(self, item_soup):
        if self.conf('price_attribute'):
            price_node = item_soup.select_one(self.conf('price_node'))
            return price_node.attrs.get(self.conf('price_attribute'), '')
        else:
            return self.get_soup_text(item_soup, self.conf('price_node'))

    def get_contact(self, item_soup):
        return self.get_contact_html(item_soup)

    def get_contact_html(self, item_soup):
        return self.get_soup_text(item_soup, self.conf('contact_node'))

    def get_location(self, item_soup):
        return self.get_location_html(item_soup)

    def get_location_html(self, item_soup):
        return self.get_soup_text(item_soup, self.conf('location_node'))

    def get_lat_lng(self, item_soup):
        return self.get_lat_lng_html(item_soup)

    def get_lat_lng_html(self, item_soup):
        return self.get_soup_text(item_soup, self.conf('lat_lng_node'))

    def get_description(self, item_soup):
        return self.get_description_html(item_soup)

    def get_description_html(self, item_soup):
        description = ''
        for description_node in self.conf('description_node').split(','):
            description += '%s / ' % self.get_soup_text(item_soup, description_node)
        description = description[:-2]
        return description

    def get_author(self, item_soup):
        return self.get_author_html(item_soup)

    def get_author_html(self, item_soup):
        return self.get_soup_text(item_soup, self.conf('author_node'))

    def get_image(self, item_soup):
        return self.get_image_html(item_soup)

    def get_image_html(self, item_soup):
        if self.conf('image_node'):
            image = item_soup.select_one(self.conf('image_node'))
        else:
            image = item_soup.select_one('img')
        if image:
            if self.conf('image_attribute'):
                attrs = self.conf('image_attribute').split(',')
            else:
                attrs = ['src', ]
            for attr in attrs:
                image_value = image.attrs.get(attr, '')
                if image_value:
                    break
            if not (image_value.startswith('http') or image_value.startswith('//')):
                original_url = urlparse(self.source.url)
                image_value = '{}://{}{}'.format(
                    original_url.scheme,
                    original_url.netloc,
                    image_value,
                )
            return image_value
        return ''

    def get_items_for_link(self, link, page):
        return self.get_items_for_link_html(link, page)

    def get_items_for_link_html(self, link, page):
        if not link:
            return []
        content = self.fetch_link(link, page)
        self.current_soup = BeautifulSoup(content, 'html.parser')
        self.current_wrapper_soup = self.current_soup.select_one(self.conf('list_wrapper_node'))
        results = self.current_soup.select('{} {}'.format(self.conf('list_wrapper_node'), self.conf('item_node')))
        # print(self.current_wrapper_soup)
        # print(results)
        return results

    def get_next_page_link(self, current_link, page):
        return self.get_next_page_link_html(current_link, page)

    def get_next_page_link_html(self, current_link, page):
        link_node = self.get_next_page_link_node(current_link, page)
        if link_node:
            if self.conf('next_page_attribute'):
                attr = self.conf('link_attribute')
            else:
                attr = 'href'
            link_value = link_node.attrs.get(attr, None)
            if link_value and not (link_value.startswith('http') or link_value.startswith('//')):
                original_url = urlparse(self.source.url)
                slash = ''
                if not link_value.startswith('/'):
                    slash = '/'
                link_value = '{}://{}{}{}'.format(
                    original_url.scheme,
                    original_url.netloc,
                    slash,
                    link_value,
                )
            return link_value
        return None

    def get_next_page_link_node(self, current_link, page):
        return self.get_next_page_link_node_html(current_link, page)

    def get_next_page_link_node_html(self, current_link, page):
        if self.conf('next_page_node'):
            link = self.current_soup.select_one(self.conf('next_page_node'))
        else:
            return None
        return link
