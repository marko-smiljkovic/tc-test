import requests


class APICaller:
    api_server_url = None

    def __init__(self, api_server_url):
        if api_server_url is None:
            raise Exception("Error, missing api server url")
        self.api_server_url = api_server_url

    @staticmethod
    def _create_headers_from_token(token):
        return {'Authorization': 'Bearer {}'.format(token)} if token is not None else ""

    def _get_full_api_url(self, route):
        return "{api_server_url}/{route}".format(
            api_server_url=self.api_server_url,
            route=route,
        )

    def call_json_api(self, method, route, params, jwt_token=None):
        return requests.request(method,
                                self._get_full_api_url(route),
                                json=params,
                                headers=self._create_headers_from_token(jwt_token))

    def call_api(self, method, route, params, jwt_token=None):
        return requests.request(method,
                                self._get_full_api_url(route),
                                params=params,
                                headers=self._create_headers_from_token(jwt_token))


class BaconIpsumApiCaller(APICaller):

    def __init__(self):
        super().__init__("https://baconipsum.com/api")

    def get_bacon_ipsum(self):
        response = self.call_api('GET', '', {"type": "all-meat", "paras": 1})
        return response.json()[0]


class TCTestApiCaller(APICaller):

    def get_jwt_token_pair(self, email, password):
        response = self.call_json_api('POST', 'token/', {"username": email, "password": password})
        return response.json()

    def register_user(self, email, password):
        response = self.call_json_api('POST', 'signup/', {"email": email, "password": password})
        return response

    def create_post(self, text, jwt_token):
        response = self.call_json_api('POST', 'post/', {"text": text}, jwt_token)
        return response.json()

    def get_user_posts(self, user_id, jwt_token):
        response = self.call_json_api('GET', 'post/', {"user_id": user_id}, jwt_token)
        return response.json()

    def like_post(self, post_id, jwt_token):
        response = self.call_json_api('POST', 'like/', {"post_id": post_id}, jwt_token)
        return response.json()
