"""El mapa del mundo debe coincidir exactamente con el grafo de zonas del GDD (sección 2.1)."""

import json

from engine import resources

# Conexiones del juego base según el GDD. Todas son bidireccionales.
GDD_CONNECTIONS = {
    frozenset(pair)
    for pair in [
        ("cartuja", "alamillo_park"),
        ("cartuja", "river"),
        ("cartuja", "macarena"),
        ("triana", "river"),
        ("triana", "los_remedios"),
        ("triana", "heliopolis"),
        ("los_remedios", "heliopolis"),
        ("river", "old_town"),
        ("river", "plaza_de_espana"),
        ("plaza_de_espana", "heliopolis"),
        ("plaza_de_espana", "nervion"),
        ("old_town", "macarena"),
        ("old_town", "nervion"),
        ("macarena", "nervion"),
        ("macarena", "noble_zone"),
    ]
}


def load():
    with open(resources.path("data", "world_map.json"), encoding="utf-8") as f:
        return json.load(f)


def test_eleven_zones_and_the_gdd_connections():
    data = load()
    assert len(data["zones"]) == 11
    connections = {frozenset((c["a"], c["b"])) for c in data["connections"]}
    assert connections == GDD_CONNECTIONS
    assert len(data["connections"]) == 15


def test_dead_ends():
    data = load()
    for zone, neighbour in (("alamillo_park", "cartuja"), ("noble_zone", "macarena")):
        links = [c for c in data["connections"] if zone in (c["a"], c["b"])]
        assert len(links) == 1 and neighbour in (links[0]["a"], links[0]["b"])


def test_expansion_only_connects_to_cartuja_and_triana():
    data = load()
    targets = {c["b"] for c in data["expansion_connections"]}
    assert targets == {"cartuja", "triana"}


def test_geography_rules():
    data = load()
    river_x_at_cartuja = 39  # el río pasa por x≈39-42 % a la altura de la Cartuja
    crater = data["points_of_interest"]["crater"]["at"]
    assert crater[0] < river_x_at_cartuja  # el cráter, al oeste del río
    for zone in ("cartuja", "triana", "los_remedios", "alamillo_park"):
        assert data["zones"][zone]["box"][2] < 40  # orilla oeste
    giralda = data["points_of_interest"]["giralda"]["at"]
    assert data["points_of_interest"]["alcazar"]["at"][1] > giralda[1]  # Alcázar al sur
    assert data["points_of_interest"]["setas"]["at"][1] < giralda[1]  # Setas al norte


def test_south_route_is_locked_by_the_first_boss():
    data = load()
    by_pair = {frozenset((c["a"], c["b"])): c for c in data["connections"]}
    for pair in (("triana", "heliopolis"), ("los_remedios", "heliopolis")):
        assert by_pair[frozenset(pair)]["requires"] == "torre_del_oro_boss_defeated"
    assert by_pair[frozenset(("cartuja", "alamillo_park"))]["requires"] == "alamillo_decontaminated"
