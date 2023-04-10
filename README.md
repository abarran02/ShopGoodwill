# ShopGoodwill Python

This project is for educational purposes only. ShopGoodwill.com is an online auction marketplace for Goodwill stores to expand their audience. While the site does not provide an official API, it uses a POST request system that allows imitating user interaction and capturing responses.

## Installation

Ensure you have the latest version of PyPA’s build installed:

```bash
python3 -m pip install --upgrade build
```

To build and install the package, run the following commands from the base directory:

```bash
python3 -m build
pip install dist/ShopGoodwill-1.0.0-py3-none-any.whl
```

## ShopGoodwill class

The ShopGoodwill class is your primary interface with the standard ShopGoodwill requests.
ShopGoodwill provides a numeric identifier for categories and store location that can be used to narrow your search. These can be viewed easily through the ShopGoodwill class:

```Python
import ShopGoodwill
ShopGoodwill.show_categories(show_children=True)
ShopGoodwill.show_locations()
```

Further filters are stored in ``source/search_request.json``, which is used for a POST request to ShopGoodwill. All of these filters can be viewed using:

```Python
ShopGoodwill.show_filters()
```

Initializing a ShopGoodwill object automatically makes a search query to ShopGoodwill, based on your configuration.

### Example usage

```Python
sg = ShopGoodwill(filters={'searchOneCentShippingOnly': True}, max_results=1, include_details=True)
```

The options for the ShopGoodwill object and request include:

* category (int)
* max_results (int)
* include_details (bool)
  * This makes an additional request using ShopGoodwillItem for more detailed information
* sleeps (int)
  * Time in seconds to wait between include_details requests to avoid rate limiting
* filters (dict)
  * Overrides any attribute of search_request.json
  * Search query text is controlled by this dict using the "searchText" key

After the initialization query, the ShopGoodwill object will have the following data members:

* items
  * A list of all ShopGoodwillItem objects returned by the search query
* result_count
  * A count of the total number of items matched to the search query. This may exceed max_results

## ShopGoodwillItem class

The ShopGoodwillItem object has two functions to expand on the basic information provided by the search query.

``get_item_details()`` can find full listing descriptions and metadata. Importantly, this will scrape the handling price of the item.
``calculate_shipping()`` allows the user to calculate the cost of the seller-selected shipping option using a POST request to ShopGoodwill

A ShopGoodwillItem object can be manually created with a valid item ID, and item_details dict if already available.

```Python
from ShopGoodwill import ShopGoodwillItem
itm = ShopGoodwillItem('1')
itm.get_item_details()
itm.calculate_shipping('20500')
```

A ShopGoodwillItem object has the following data members:

* itemid
* shipping
  * Dictionary containing ``shipping``, ``handling``, and ``total`` costs
* item_details

## ShopGoodwillPost class

This class is primarily for usage by the ShopGoodwill and ShopGoodwillItem classes, but provides some additional functionality to the user. One may supply cookies, or override the user agent used for the POST requests.
