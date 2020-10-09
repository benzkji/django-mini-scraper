import time

import requests
from django.conf import settings


class BaseParser():
    """
    subclasses must implement most of "Not Implemented" methods!
    most important:
    - get_results_for_link(link):
    """

    allow_same_links = False

    def __init__(self, source):
        self.source = source
        self.url = source.url
        self.user_input = source.user_input
        self.preflight_url = source.preflight_url

    @classmethod
    def from_dict(self, dict, key):
        if dict.get(key, ''):
            return dict.get(key)
        return ''

    def input(self, key):
        return self.from_dict(self.user_input, key)

    def get_link(self, item):
        raise(Exception('Not Implemented!'))

    def get_guid(self, item):
        raise(Exception('Not Implemented!'))

    def get_image(self, item):
        raise(Exception('Not Implemented!'))

    def get_title(self, item):
        raise(Exception('Not Implemented!'))

    def get_price(self, item):
        raise(Exception('Not Implemented!'))

    def get_contact(self, item):
        raise(Exception('Not Implemented!'))

    def get_location(self, item):
        raise(Exception('Not Implemented!'))

    def get_lat_lng(self, item):
        raise(Exception('Not Implemented!'))

    def get_description(self, item):
        raise(Exception('Not Implemented!'))

    def get_items_for_link(self, link, page):
        raise (Exception('Not Implemented'))

    def get_next_page_link(self, current_link, page):
        raise (Exception('Not Implemented'))

    def do_preflight(self):
        if (self.preflight_url):
            self.session.get(self.preflight_url)

    def fetch_link(self, link, page):
        return self.session.get(link).content

    def get_url(self, url=None):
        """
        override to allow url modification
        inject session id, whatever
        """
        if not url:
            return self.url
        else:
            return url

    def transform_item(self, item):
        """
        item can be a beautifulsoup4 dom element, as well as a json object.
        :param item:
        :return: dict
        """
        guid = self.get_guid(item)
        if not guid:
            guid = self.get_link(item)
        result = {}
        result['link'] = self.get_link(item)
        result['guid'] = guid
        result['image'] = self.get_image(item)
        result['title'] = self.get_title(item)
        result['contact'] = self.get_contact(item)
        result['price'] = self.get_price(item)
        result['location'] = self.get_location(item)
        result['lat_lng'] = self.get_lat_lng(item)
        result['description'] = self.get_description(item)
        # result['lat_lng'] = self.get_location(item)
        return result

    def session_config(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Upgrade-Insecure-Requests': '1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        self.session.headers.update(headers)

    def fetch_results(self):
        search_url = self.get_url()
        self.session = requests.Session()
        self.session_config()
        self.do_preflight()
        current_link = search_url
        all_links = []
        results = range(1, 2, )
        counter = 0
        guids = []
        page = 0
        print("---- fetch_results for {}".format(self.url))
        while len(results):
            # measure fetch
            start = time.process_time()
            # yield results
            old_counter = counter
            for item in self.get_items_for_link(current_link, page):
                result = self.transform_item(item)
                if result['guid'] and not result['guid'] in guids:
                    guids.append(result['guid'])
                    counter +=1
                    # print(result['link'])
                    if counter - 1 >= self.source.max_results:
                        return
                    yield result
            print("----")
            end = time.process_time()
            # get next link, sleep a bit before fetching that one
            current_link = self.get_next_page_link(current_link, page)
            # prevent double fetching of pages
            if not current_link in all_links or self.allow_same_links:
                all_links.append(current_link)
            else:
                current_link = None
            if current_link and counter > old_counter:
                # has we still a new link for next page?
                # has we found any valid values?
                duration = end - start
                if not settings.DEBUG:
                    time.sleep(duration * 10)
            else:
                results = []
            page += 1
        return
