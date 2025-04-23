import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Base:
    def __init__(self, session_token=None, config:dict=None):
        self.session_token = session_token
        self.config = config

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.session_token['token']}"
        }
        return headers

    def get_pcc_url(self):
        return self.config['pcc']['url']

