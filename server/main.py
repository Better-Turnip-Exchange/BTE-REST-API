import os
import string
import random
import json
import uvicorn
from server import turnip
from fastapi import FastAPI, HTTPException
from typing import Dict, List
from pydantic import BaseModel

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, \like Gecko) \
                Chrome/81.0.4044.138 Safari/537.36"


# Borrowed from https://stackoverflow.com/a/2257449
def villager_id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


# villager Data Model for requests
# From: https://fastapi.tiangolo.com/tutorial/body/
# A request body is data sent by the client to your API.
class villager(BaseModel):
    villager_id: str = villager_id_generator()  # Populate this with a random string
    keywords: List[str] = []  # List of words you wish not to see in island descriptions
    islands_visited: Dict[str, dict] = {}  # A dict of all the island ids a user "visits"
    price_threshold: int = 0  # The requested turnip price limit


debug = True if os.environ.get("DEBUG") else False


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
    "Foo": {
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

app = FastAPI(
    title="Better Turnip Exchange",
    description="A turnip.exchange companion that makes it easier to sell your turnips.",
    version="1.0.0",
)


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}


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
    if type(villager_item) != villager:
        raise HTTPException(status_code=400, detail="Incorrect request data model")
    else:
        try:
            villager_item_dict = villager_item.dict()
            villager_kvs[villager_item_dict["villager_id"]] = villager_item_dict
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))
    return villager_item_dict


@app.put("/villager/{villager_id}/update")
# Needs to expect the villager_id (str) and keywords (List[str])
async def update_keywords(villager_id: str, keywords: List[str]):
    """
    Checks to see if villager exists in villager_kvs and
    updates keywords.

    args: villager_id: str, keywords: List[str]
    return: villager specified by villager_id
    """
    # Check if villager_id exists in kvs
    # NOTE: You want to search and pull data from the villager_kvs
    if villager_id in villager_kvs.keys():
        # if villager_id exists in kvs, then update keywords
        villager_kvs[villager_id]["keywords"] = keywords
    else:
        # if villager_id is not in kvs, then give error msg
        raise HTTPException(status_code=404, detail="Villager not found!")
    return villager_kvs[villager_id]


@app.put("/villager/{villager_id}/append")
# Needs to expect the villager_id (str) and keywords (List[str])
async def append_keywords(villager_id: str, keywords: List[str]):
    """
    Checks to see if villager exists in villager_kvs and
    appends keywords to the keywords list.

    args: villager_id: str, keywords: List[str]
    return: villager specified by villager_id
    """
    # Check if villager_id exists in kvs
    # NOTE: You want to search and pull data from the villager_kvs
    if villager_id in villager_kvs.keys():
        # if villager_id exists in kvs, then appends keywords
        # Converts existing keywords list to set, then creates a new set from added keywords
        # Finds keywords that do not exist in the existing set, then combines the two sets
        # Converts combined set back to a list
        original_keywords_set = set(villager_kvs[villager_id]["keywords"])
        new_keywords_set = set(keywords)
        not_in_original = list(new_keywords_set - original_keywords_set)
        combined_keywords = villager_kvs[villager_id]["keywords"] + not_in_original
        combined_keywords.sort()
        villager_kvs[villager_id]["keywords"] = combined_keywords
    else:
        # if villager_id is not in kvs, then give error msg
        raise HTTPException(status_code=404, detail="Villager not found!")
    return villager_kvs[villager_id]


@app.get("/villager/",)
async def get_villiagers():
    """
    Get all villager information from villager_kvs

    return: villager_kvs
    """
    try:
        return villager_kvs
    except Exception as e:
        raise HTTPException(
            status_code=404, detail="villager_kvs is not found: {}".format(str(e))
        )


@app.get(
    "/villager/{villager_id}/public", response_model=villager,
)
async def read_villager_public_data(villager_id: str):
    """
    Return villager_id's villager information

    arg: villager_id: str
    return: villager_kvs
    """
    try:
        return villager_kvs[villager_id]
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="villager_id {} is not found: {}".format(villager_id, str(e)),
        )


@app.post(
    "/run", response_model=villager, response_model_include={"islands_visited"},
)
async def main_driver(villager_id: str):
    """
    Main Logic wrapper for turnip price scraping

    NOTE: This is subject to change heavily as development continues.

    1. Check if villager exists
      - 404 please create_villager before POST to main_driver
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

    returns:
    - islands_visited
    {
        {
        "islands_visited": {
            "str": {
            "name":""
            "link", "str",
            "description": "str"
            "turnipPrice": int,
            "creationTime": "str",
            "rating": int,
            "ratingCount": int,
            "islandScore": int,
            "queued": "str",
            "maxQueue": int
            }
        }
    }
    """
    if villager_id not in villager_kvs.keys():
        raise HTTPException(status_code=404, detail="Villager not found")
    try:
        turnip_obj = turnip.Turnip()
        turnip_obj.build_requests(headers=headers, data=data, url=url)
    except Exception as e:
        raise HTTPException(
            status_code=503, detail="turnip.exchange API is unreachable: {}".format(str(e))
        )
    try:
        # Setup filter
        turnip_obj.build_filter(keywords=villager_kvs[villager_id]["keywords"])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Keyword filter failed: {}".format(str(e)))
    try:
        # Start main logic
        response = turnip_obj.scrape_turnip_data()
        response = json.loads(response.text)
        visited = villager_kvs[villager_id]["islands_visited"]
        for island in response["islands"]:
            if (
                island["turnipPrice"] > villager_kvs[villager_id]["price_threshold"]
                and not island["fee"]
                and not island["turnipCode"] in visited
                and not turnip_obj.keyword_processor.extract_keywords(island["description"])
            ):
                turnip_code = island["turnipCode"]
                msg_url = "https://turnip.exchange/island/{}".format(turnip_code)
                name = island["name"]
                link = msg_url
                description = island["description"]
                turnipPrice = island["turnipPrice"]
                creationTime = island["creationTime"]
                rating = island["rating"]
                ratingCount = island["ratingCount"]
                islandScore = island["islandScore"]
                queued = island["queued"]
                maxQueue = island["maxQueue"]
                iv = {
                    "name": name,
                    "link": link,
                    "description": description,
                    "turnipPrice": turnipPrice,
                    "creationTime": creationTime,
                    "rating": rating,
                    "ratingCount": ratingCount,
                    "islandScore": islandScore,
                    "queued": queued,
                    "maxQueue": maxQueue,
                }
                visited[turnip_code] = iv
        villager_kvs[villager_id]["islands_visited"] = visited
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to populate islands_visited section: {}".format(str(e)),
        )
    return villager_kvs[villager_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
