from fastapi.testclient import TestClient

from server import main

client = TestClient(main.app)

expected_get_villagers_out = {
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


def test_get_villagers():
    response = client.get("/villager/")
    assert response.status_code == 200
    assert response.json() == expected_get_villagers_out


def test_read_villager_public():
    response = client.get("/villager/foo/public")
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
    test_read_root()
    test_create_villager()
