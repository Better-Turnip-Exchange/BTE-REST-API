import os
import json
import webbrowser
import time
from turnip import Turnip
from dotenv import load_dotenv  # for python-dotenv method
from fastapi import FastAPI
from typing import Dict, List
from pydantic import BaseModel


class TurnipItem(BaseModel):
    name: str
    keywords: List[str] = None
    islands_visited: Dict[str, bool] = None
    price_threshold = 0


app = FastAPI()

items = {
    "foo": {
        "name": "Foo",
        "keywords": [
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
        ],
        "price_threshold": 520,
        "islands_visited": {},
    },
}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/items/")
async def create_item(turnip_item: TurnipItem):
    item_dict = turnip_item.dict()
    return item_dict


@app.get(
    "/items/{item_id}/name",
    response_model=TurnipItem,
    response_model_include={"name", "keywords"},
)
async def read_item_name(turnip_id: str):
    return items[turnip_id]


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/run")
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
    # while True:
    response = turnip_obj.scrape_turnip_data()
    out = json.loads(response.text)
    print("Visited islands ", turnip_obj.islands_visited)
    # turnip_obj.fbclient_interface(
    #     username=os.environ.get("FB_USER"), pwd=os.environ.get("FB_PASS"), choice="Login",
    # )
    users = []
    for island in out["islands"]:
        if (
            island["turnipPrice"] > 550
            and not island["turnipCode"] in turnip_obj.islands_visited.keys()
            and not turnip_obj.keyword_processor.extract_keywords(island["description"])
        ):
            msg_url = "https://turnip.exchange/island/{}".format(island["turnipCode"])
            print("\n", island["description"])
            turnip_obj.islands_visited[island["turnipCode"]] = True
            if debug:
                webbrowser.get("chrome").open_new_tab(msg_url)
                # users.append(turnip_obj.fbclient.uid)
            else:
                users_requested = ["Alex Messick", "Chris Callan"]
                for user in users_requested:
                    users.append((turnip_obj.fbclient.searchForUsers(user)[0]).uid)
            print("ISLAND FOUND!")
            # turnip_obj.fbclient_interface(
            #     username=None, pwd=None, msg=msg_url, recipients=users, choice="Msg"
            # )
    items["bar"] = {
        "name": "bar",
        "keywords": keywords,
        "islands_visited": turnip_obj.islands_visited,
        "price_threshold": 600,
    }
    return items["bar"]
    # turnip_obj.fbclient_interface(choice="Logout")
