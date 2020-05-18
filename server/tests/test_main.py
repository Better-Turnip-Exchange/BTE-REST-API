from fastapi.testclient import TestClient

from server import main

client = TestClient(main.app)


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


if __name__ == "__main__":
    test_read_root()
    test_create_villager()
