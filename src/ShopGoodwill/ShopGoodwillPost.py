import requests
from fake_useragent import UserAgent

class ShopGoodwillPost(object):
    with open('fallback_ua.txt', 'r') as f:
        fallback = f.readline()
        ua = UserAgent(fallback=fallback)

    @classmethod
    def post(cls, api_url: str, json: dict, cookies: dict = None, user_agent: str = ua) -> requests.Response:
        if user_agent == cls.ua:
            headers = {'User-Agent': cls.ua.chrome}
        else:
            headers = {'User-Agent': user_agent}

        post_response = requests.post(api_url, json=json, headers=headers, cookies=cookies)

        return post_response
