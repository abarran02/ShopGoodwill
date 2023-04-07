import requests
import json
from .ShopGoodwillItem import ShopGoodwillItem
from .ShopGoodwillPost import ShopGoodwillPost
from bs4 import BeautifulSoup
from re import sub
from time import sleep
from datetime import date

class ShopGoodwill(object):

    # load request template and update current date
    with open('search_request.json', 'r') as template:
        request_template = json.load(template)
    request_template['closedAuctionEndingDate'] = date.today().strftime("%m/%d/%Y")

    # to be set later with __update_gw_ids()
    categories = None
    sellers = None

    def __init__(self, filters: dict = {}, category: int = 0, 
                 include_details: bool = False, sleeps: int = 0, max_results: int = float('inf')):
        self.items = []

        # make API request for item listings
        api_url = 'https://buyerapi.shopgoodwill.com/api/Search/ItemListing'
        json_request = self.__generate_request(filters, category)
        post_response = ShopGoodwillPost.post(api_url, json_request)

        # pull results from POST response 
        json_response = json.loads(post_response.content)
        search_results = json_response['searchResults']['items']
        self.result_count = json_response['searchResults']['itemCount']

        # add each item to ShopGoodwill item list
        for item in search_results:
            new_item = ShopGoodwillItem(item['itemId'], item_details=item)
            self.items.append(new_item)

            # stop if max_results reached, important if include_details = True
            if len(self.items) == max_results:
                break

        # append additional details from item listing page, if requested
        if include_details:
            for item in self.items:
                item.get_item_details()
                # sleep the specified time to avoid rate limiting
                # no need to sleep after the last item
                if item != self.items[-1]:
                    sleep(sleeps)
                    
    def __generate_request(self, filters: dict, category: int) -> dict:
        # ensure all user filters are valid
        for key in filters.keys():
            if key not in self.request_template.keys():
                raise KeyError(f'Invalid ShopGoodwill filter: {key}')

        request = self.request_template | filters
        # if category is the default, no need to change anything else
        if category == 0:
            return request

        # fetch categories to check against
        if self.categories == None:
            self.__update_gw_ids()

        # ensure category is valid and find parent category, if applicable
        for elem in self.categories:
            # user category is a parent category
            if category == elem['categoryId']:
                parent = 0
                level = 1
                break
            
            # category has children
            if len(elem['children']) != 0:
                # check each child id for a match
                try:
                    for child in elem['children'][1:]:
                        # user category is a child category
                        if category == child['categoryId']:
                            parent = elem['categoryId']
                            level = 2
                            raise StopIteration
                except StopIteration:
                    # only way I could find to break a nested for-loop
                    break
        else:
            # no matching category is found
            raise KeyError(f'Invalid ShopGoodwill category: {category}')

        # generate category updates for request
        cat_values = {
            'categoryId': category,
            'categoryLevel': level,
            'categoryLevelNo': str(level),
            'catIds': f'-1,{parent},{category}',
            'selectedCategoryIds': f'{category}'
            }

        return request | cat_values

    def __update_gw_ids(cls) -> bool:
        # not ideal using a cateogry page for this, but couldn't find anything else static
        page = requests.get('https://shopgoodwill.com/categories/antiques')
        soup = BeautifulSoup(page.text, 'html.parser')

        # seek to last script in the page, containing category info
        script = soup.find(id='serverApp-state').get_text()
        # replace quotes so json loads correctly
        script = sub(r'(&q;)', '"', script)
        data = json.loads(script)

        # update both categories and sellers, and get success
        s1 = cls.__update_categories(data)
        s2 = cls.__update_sellers(data)

        # return success
        return s1 and s2

    @classmethod
    def __update_categories(cls, data) -> bool:
        # iterate over json to find key with categories
        cls.categories = None
        for val in data.items():
            try:
                # if this doesn't throw errors, then found!
                categories = val[1]['body']['categoryListModel']['categoryModel']
                cls.categories = categories
                break
            except (KeyError, TypeError):
                pass

        return cls.categories != None

    @classmethod
    def __update_sellers(cls, data) -> bool:
        # iterate over json to find key with sellers
        cls.sellers = None
        for val in data.items():
            try:
                # if this doesn't throw errors, then found!
                sellers = val[1]['body']
                sellers[0]['sellerId']
                cls.sellers = sellers
                break
            except (KeyError, TypeError, IndexError):
                pass

        return cls.sellers != None

    @classmethod
    def show_categories(cls, show_children=False) -> None:
        # check whether categories have been found yet this session
        if cls.categories == None:
            cls.__update_gw_ids(cls)
        
        # iterate over cateogires for printing
        for elem in cls.categories:
            print(elem['categoryId'], elem['shortName'])
            
            # print subcategories
            if show_children and len(elem['children']) > 0:
                for child in elem['children'][1:]:
                    print('*', child['categoryId'], child['shortName'])
    
    @classmethod
    def show_locations(cls):
        # check whether sellers have been found yet this session
        if cls.sellers == None:
            cls.__update_gw_ids()

        for elem in cls.sellers:
            print(elem['sellerId'], elem['searchFilterName'])

    @classmethod
    def show_filters(cls):
        print("Search filters and default value:")
        for item in cls.request_template.items():
            if type(item[1]) is str:
                print('%s = "%s"' % item)
            else:
                print('%s = %s' % item)
