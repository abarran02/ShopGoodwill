import requests
from fake_useragent import UserAgent
from importlib_resources import open_text


class ShopGoodwillPost(object):

    with open_text('ShopGoodwill', 'fallback_ua.txt') as f:
        fallback = f.readline()
        ua = UserAgent(fallback=fallback)

    @classmethod
    def post(cls, api_url: str, json: dict, cookies: dict = None, user_agent: str = ua) -> requests.Response:
        """Interface for `reqeusts.post()` but including a default user agent"""
        if user_agent == cls.ua:
            headers = {'User-Agent': cls.ua.chrome}
        else:
            headers = {'User-Agent': user_agent}

        post_response = requests.post(api_url, json=json, headers=headers, cookies=cookies)

        return post_response
