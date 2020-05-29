from fastapi.testclient import TestClient

from server import main

client = TestClient(main.app)

expected_get_villagers_out = {
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
    "Bar": {
        "islands_visited": {},
        "keywords": ["Entry"],
        "price_threshold": 300,
        "villager_id": "Bar",
    },
}


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_create_villager():
    response = client.post(
        "/villager/",
        json={
            "villager_id": "Bar",
            "keywords": ["Entry"],
            "islands_visited": {},
            "price_threshold": 300,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "villager_id": "Bar",
        "keywords": ["Entry"],
        "islands_visited": {},
        "price_threshold": 300,
    }


def test_create_villager_fail_unprocessable():
    response = client.post(
        "/villager/", json={
            "villager_id": [],
            "keyword": ["Entry"],
            "islands": "",
            "price": 300
        },
    )
    assert response.status_code == 422


def test_create_villager_fail_empty():
    response = client.post("/villager/", data={"": ""})
    assert response.status_code == 400


def test_create_villager_fail_no_data():
    response = client.post("/villager/")
    assert response.status_code == 422


def test_update_keywords():
    # Creating a villager
    response = client.post(
        "/villager/",
        json={
            "villager_id": "Bar",
            "keywords": ["Entry"],
            "islands_visited": {},
            "price_threshold": 300,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "villager_id": "Bar",
        "keywords": ["Entry"],
        "islands_visited": {},
        "price_threshold": 300,
    }
    response = client.put(
        "/villager/Bar/update",
        json=["Entry2", "Entry3", "Entry4"]
    )
    assert response.status_code == 200
    assert response.json() == {
        "villager_id": "Bar",
        "keywords": ["Entry2", "Entry3", "Entry4"],
        "islands_visited": {},
        "price_threshold": 300,
    }


def test_append_keywords():
    # Creating a villager
    response = client.post(
        "/villager/",
        json={
            "villager_id": "Bar",
            "keywords": ["Entry"],
            "islands_visited": {},
            "price_threshold": 300,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "villager_id": "Bar",
        "keywords": ["Entry"],
        "islands_visited": {},
        "price_threshold": 300,
    }
    response = client.put(
        "/villager/Bar/append",
        json=["Entry2", "Entry3", "Entry4"]
    )
    assert response.status_code == 200
    assert response.json() == {
        "villager_id": "Bar",
        "keywords": ["Entry", "Entry2", "Entry3", "Entry4"],
        "islands_visited": {},
        "price_threshold": 300,
    }


def test_get_villagers():
    response = client.post(
        "/villager/",
        json={
            "villager_id": "Bar",
            "keywords": ["Entry"],
            "islands_visited": {},
            "price_threshold": 300,
        },
    )
    response = client.get("/villager/")
    assert response.status_code == 200
    assert response.json() == expected_get_villagers_out


def test_read_villager_public():
    response = client.get("/villager/Foo/public")
    assert response.status_code == 200
    assert response.json() == {
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
    }


if __name__ == "__main__":
    # test_read_root()
    test_create_villager()
    test_get_villagers()
    test_update_keywords()
    test_append_keywords()
    test_read_villager_public()
    test_create_villager_fail_empty()
    test_create_villager_fail_no_data()
