import pytest

from funtions import load_file


HEROES = {
    "0": {
        "name": "A-Bomb",
        "gender": "Male",
        "eye_color": "yellow",
        "race": "Human",
        "hair_color": "No Hair",
        "height": "203",
        "publisher": "Marvel Comics",
        "skin_color": "-",
        "alignment": "good",
        "weight": "441",
    }
}


@pytest.fixture
def client(monkeypatch):
    import application as app_module

    monkeypatch.setattr(app_module, "data", HEROES)
    app_module.application.config.update(TESTING=True)
    return app_module.application.test_client()


def test_load_file_parses_hero_csv(tmp_path):
    csv_file = tmp_path / "heroes.csv"
    csv_file.write_text(
        "id;Name;Gender;Eye color;Race;Hair color;Height;Publisher;Skin color;Alignment;Weight\n"
        "42;Nova;Male;blue;Human;Black;190;Marvel Comics;light;good;85\n",
        encoding="utf-8",
    )

    heroes = load_file(str(csv_file))

    assert heroes["42"]["name"] == "Nova"
    assert heroes["42"]["weight"] == "85"


def test_home_route_returns_all_heroes(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == HEROES


def test_hero_route_returns_requested_hero(client):
    response = client.get("/0")

    assert response.status_code == 200
    assert response.get_json() == HEROES["0"]
