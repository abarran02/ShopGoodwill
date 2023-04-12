import json
from re import sub

from bs4 import BeautifulSoup
from requests_html import HTMLSession

from .ShopGoodwillPost import ShopGoodwillPost


class ShopGoodwillItem(object):
    """
    Item object which expands on the basic listing information provided by a ShopGoodwill search query by pulling the item's listing page.
    
    The initialized object will have the following data members:
    * itemid `str`
    * shipping `dict`: stores shipping prices with keys `shipping`, `handling`, and `total`. Updated by `calculate_shipping()`.
    * item_details `dict`: contains item listing information. Updated with `get_item_details()`.
    """
    def __init__(self, itemid: str, item_details: dict = None):
        """
        itemid `str`: item listing unique identifier, string as it may start with 0

        item_details `dict`: provided by a ShopGoodwill object query
        """
        self.itemid = itemid
        self.shipping = { 'shipping': -1, 'handling': -1, 'total': -1 }
        self.item_details = item_details

    def __checkId(self):
        # ensure itemid is set and url will actually return
        if self.itemid == None:
            raise AttributeError("ShopGoodwillItem object has no itemid set")

    def get_item_details(self) -> None:
        """Retrieve more detailed item listing information from the item's page and update the `item_details` data member"""
        self.__checkId()

        # get item listing page
        with HTMLSession() as s:
            response = s.get(f'https://shopgoodwill.com/item/{self.itemid}')
            response.html.render()

        # seek to script element with complete listing data
        soup = BeautifulSoup(response.html.html, 'html.parser')
        script = soup.find(id='serverApp-state').get_text()
        script = sub(r'(&q;)', '"', script)
        data = json.loads(script)

        for val in data.items():
            try:
                item_details = val[1]['body']
                # if this doesn't throw errors, then found!
                item_details['buyerCountry']
                break
            except (KeyError, TypeError):
                pass

        # set item details, or update if pulled already
        if self.item_details == None:
            self.item_details = item_details
        else:
            self.item_details = self.item_details | item_details

        # can calculate total shipping cost if One Cent Shipping is enabled
        if self.item_details['shippingPrice'] == 0.01:
            self.shipping['shipping'] = 0.01
            self.shipping['handling'] = self.item_details['handlingPrice']

            self.shipping['total'] = 0.01 + self.shipping['handling']

    def calculate_shipping(self, zip_code: str) -> float:
        """Calculate cost of shipping item to the given zip code"""
        self.__checkId()

        # send a POST request to ShopGoodwill for shipping cost
        api_url = 'https://buyerapi.shopgoodwill.com/api/ItemDetail/CalculateShipping'
        json_request = {
            "itemId":self.itemid,
            "country":"US",
            "province":None,
            "zipCode":str(zip_code),
            "quantity":1,
            "clientIP":"0.0.0.3"
            }
        
        post_response = ShopGoodwillPost.post(api_url, json_request)
        
        # parse shipping, handling, and total
        soup = BeautifulSoup(post_response.content, 'html.parser')
        shipping = soup.find(id='shipping-span').get_text()
        self.shipping['shipping'] = strip_price(shipping)
        handling = soup.find_all('p')[-2].get_text()
        self.shipping['handling'] = strip_price(handling)

        # should be faster to calculate this than scrape the HTML
        self.shipping['total'] = self.shipping['shipping'] + self.shipping['handling']

        return self.shipping['total']

    def place_bid(itemid: int, sellerid: int, bid_amount: float, quantity: int = 1) -> bool:
        api_url = 'https://buyerapi.shopgoodwill.com/api/ItemBid/PlaceBid'
        json_request = {
            "itemId":itemid,
            "quantity":quantity,
            "sellerId":sellerid,
            "bidAmount":str(bid_amount)
            }

        post_response = ShopGoodwillPost.post(api_url, json_request, cookies=None)

        # True if status_code < 400, else False
        return post_response.ok

def strip_price(price: str) -> float:
    return float(sub(r'[^\d.]', '', price))
