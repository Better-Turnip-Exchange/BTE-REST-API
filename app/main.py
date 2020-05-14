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


@app.post("/turnip-items/")
async def create_item(turnip_item: TurnipItem):
    turnip_item_dict = turnip_item.dict()
    turnip_kvs[turnip_item_dict["turnip_id"]] = turnip_item_dict
    return turnip_item_dict


@app.get(
    "/turnip-items/{turnip_id}/name",
    response_model=TurnipItem,
    response_model_include={"turnip_id"},
)
async def read_turnip_kvs_id(turnip_id: str):
    return turnip_kvs[turnip_id]


@app.get(
    "/turnip-items/{turnip_id}/visited",
    response_model=TurnipItem,
    response_model_include={"turnip_id", "islands_visited"},
)
async def read_item_islands(turnip_id: str):
    return turnip_kvs[turnip_id]


@app.post("/run")
def main_driver(turnip_id: str):
    """
    Main Logic wrapper for turnip price scraping
    """
    if turnip_id not in turnip_kvs.keys():
        turnip_kvs[turnip_id] = {
            "turnip_id": turnip_id,
            "keywords": [],
            "islands_visited": {},
            "price_threshold": 0,
        }
    turnip_obj = Turnip()
    turnip_obj.build_requests(headers=headers, data=data, url=url)

    # Setup filter
    turnip_obj.build_filter(keywords=turnip_kvs[turnip_id]["keywords"])

    # Start main logic
    response = turnip_obj.scrape_turnip_data()
    response = json.loads(response.text)
    visited = turnip_kvs[turnip_id]["islands_visited"]
    print("Visited islands ", visited)
    for island in response["islands"]:
        if (
            island["turnipPrice"] > turnip_kvs[turnip_id]["price_threshold"]
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
