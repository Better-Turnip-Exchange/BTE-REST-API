import json
import webbrowser
from app.turnip import Turnip
from fastapi import FastAPI
from typing import Dict, List
from pydantic import BaseModel

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, \like Gecko) \
                Chrome/81.0.4044.138 Safari/537.36"


# villager Data Model for requests
# From: https://fastapi.tiangolo.com/tutorial/body/
# A request body is data sent by the client to your API.
class villager(BaseModel):
    villager_id: str  # Populate this with some variant of the username
    keywords: List[str] = None  # List of words you wish not to see in island descriptions
    islands_visited: Dict[str, str] = None  # A dict of all the island ids a user "visits"
    price_threshold: int  # The requested turnip price limit


app = FastAPI()

# All the parameters needed to interact with turnip.exchange API
# headers: The headers params may be overkill however this is what worked when
# curling the turnip.exchange API
headers = {
    "authority": "api.turnip.exchange",
    "accept": "application/json",
    "content-type": "application/json",
    "user-agent": USER_AGENT,
    "x-island-id": "",
    "origin": "https://turnip.exchange",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://turnip.exchange/islands",
    "accept-language": "en-US,en;q=0.9",
}
# data: api.turnip.exchange request body needed
# NOTE: We may want to make this request body configurable by the user
data = '{"islander":"neither","category":"turnips"}'
# turnip.exchange API URL
url = "https://api.turnip.exchange/islands/"

# villager_kvs: in-memory kvs for class villager(BaseModel)
# This is mostly for POC in the future we should convert this to use a RDS
# This implementation has the following faults
# 1. Memory blow out
# 2. Villiagers overwritten via id collisions
# 3. kvs wiped during server reset

# The foo villager is a runnable example of a user for the POC
villager_kvs = {
    "foo": {
        "villager_id": "Foo",
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
        "islands_visited": {},
        "price_threshold": 520,
    },
}


@app.post(
    "/villager/", response_model=villager,
)
async def create_villager(villager_item: villager):
    """
    Create and add a villager to villager_kvs

    villager Request Body attributes required
    villager_id: str
    price_threshold: int

    arg: villager_item - villager Data Model detailed above

    return: villager_item_dict
    """
    villager_item_dict = villager_item.dict()
    villager_kvs[villager_item_dict["villager_id"]] = villager_item_dict
    return villager_item_dict


@app.get("/villager/",)
async def get_villiagers():
    """
    Get all villager information from villager_kvs

    return: villager_kvs
    """
    return villager_kvs


@app.get(
    "/villager/{villager_id}/public", response_model=villager,
)
async def read_villager_public_data(villager_id: str):
    """
    Return villager_id's villager information

    arg: villager_id: str
    return: villager_kvs
    """
    return villager_kvs[villager_id]


@app.post(
    "/run",
    response_model=villager,
    response_model_include={"villager_id", "islands_visited", "price_threshold"},
)
async def main_driver(villager_id: str):
    """
    Main Logic wrapper for turnip price scraping

    NOTE: This is subject to change heavily as development continues.

    1. Check if villager exists
      - If not create them.
      - NOTE: Probably best to return a status code instead of populating the kvs
              implicitly/
    2. Create Turnip object
      - This obj has a lot of the same attributes as the villager
        however it also acts as an interface for some of the main logic
      - Build turnip filter
      - Scrape the turnip page
    3. Traverse all the islands scrapped and populate the villager's
       islands_visited attribute with the url
       - update the villager kvs information
       - In the past part of the logic also opened new chrome tabs and sent fb
         messages, we want to control and throttle this more to not create spam.

    arg:
    - villager_id
    - NOTE: Potential optional arg; price threshold if they want to override value

    returns:
    - villager data model
        - the villager_id, visited islands (urls) and and price threshold they set
    """
    if villager_id not in villager_kvs.keys():
        villager_kvs[villager_id] = {
            "turnip_id": villager_id,
            "keywords": [],
            "islands_visited": {},
            "price_threshold": 0,
        }
    turnip_obj = Turnip()
    turnip_obj.build_requests(headers=headers, data=data, url=url)

    # Setup filter
    turnip_obj.build_filter(keywords=villager_kvs[villager_id]["keywords"])

    # Start main logic
    response = turnip_obj.scrape_turnip_data()
    response = json.loads(response.text)
    visited = villager_kvs[villager_id]["islands_visited"]
    for island in response["islands"]:
        if (
            island["turnipPrice"] > villager_kvs[villager_id]["price_threshold"]
            and not island["turnipCode"] in visited
            and not turnip_obj.keyword_processor.extract_keywords(island["description"])
        ):
            msg_url = "https://turnip.exchange/island/{}".format(island["turnipCode"])
            # print("\n", island["description"])
            visited[island["turnipCode"]] = True
            webbrowser.get("chrome").open_new_tab(msg_url)
            print("ISLAND FOUND!")
    turnip_kvs[turnip_id]["islands_visited"] = visited
    return turnip_kvs[turnip_id]
