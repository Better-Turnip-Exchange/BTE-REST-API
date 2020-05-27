import json
import requests
from flashtext import KeywordProcessor


class Turnip(object):
    def __init__(self):
        self.req_params = None
        self.keywords = []
        self.islands_visited = {}
        self.keyword_processor = KeywordProcessor()
        self.price_threshold = 0
        self.response = None

    def build_requests(self, headers: dict, data: str, url: str):
        """
        Gather and organize the requests parameters
        """
        self.req_params = {}
        self.req_params["headers"] = headers
        self.req_params["data"] = data
        self.req_params["url"] = url

    def build_filter(self, keywords: list):
        """
        Setup keywords to filter from what we scrape
        """
        for word in keywords:
            self.keyword_processor.add_keyword(word)

    def scrape_turnip_data(self):
        """
        Request data from https://turnip.exchange

        Typically we'll be sending a POST request to Turnip Exchange
        to gather information about it's islands
        However this could be utilized for other requests as well

        NOTE: Will hardcode request type as POST for now
        """
        response = None
        if self.req_params is not None:
            response = requests.post(
                self.req_params["url"],
                headers=self.req_params["headers"],
                data=self.req_params["data"],
            )
        return response


def main_driver(debug=True):
    """
    Main Logic wrapper for turnip price scraping
    """
    turnip_obj = Turnip()
    headers = {
        "authority": "api.turnip.exchange",
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "x-island-id": "",
        "origin": "https://turnip.exchange",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://turnip.exchange/islands",
        "accept-language": "en-US,en;q=0.9",
    }
    data = '{"islander":"neither","category":"turnips"}'
    url = "https://api.turnip.exchange/islands/"
    turnip_obj.build_requests(headers=headers, data=data, url=url)

    # Setup filter
    keywords = [
        "ENTRY",
        "entry",
        "NMT",
        "NMTs",
        "nmts",
        "GOLD",
        "gold",
        "MILES",
        "miles",
        "TIP",
        "tip",
    ]
    turnip_obj.build_filter(keywords=keywords)

    # Start main logic
    while True:
        response = turnip_obj.scrape_turnip_data()
        out = json.loads(response.text)
        print("Visited islands ", turnip_obj.islands_visited)
        for island in out["islands"]:
            if (
                island["turnipPrice"] > 550
                and not island["turnipCode"] in turnip_obj.islands_visited.keys()
                and not turnip_obj.keyword_processor.extract_keywords(island["description"])
            ):
                msg_url = "https://turnip.exchange/island/{}".format(island["turnipCode"])
                print("\n", island["description"])
                turnip_obj.islands_visited[island["turnipCode"]] = msg_url


if __name__ == "__main__":
    main_driver()
