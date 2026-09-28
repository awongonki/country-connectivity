import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from connectivity import check_connection, classify, load_graph  # noqa: E402

G = load_graph()


def test_single_country():
    assert check_connection(G, ["KEN"]) == 0


def test_neighbours_form_one_block():
    # Kenya borders Tanzania and Uganda, and they border each other
    assert classify(G, ["KEN", "TZA", "UGA"]) == "StrongRegional"


def test_within_two_steps():
    # Kenya and Rwanda do not share a border, but Uganda sits between them
    assert classify(G, ["KEN", "RWA"]) == "WeakRegional"


def test_far_apart():
    assert classify(G, ["KEN", "BRA"]) == "MultiRegional"


def test_unknown_country_is_not_strong():
    # a code missing from the graph must not be silently dropped
    assert check_connection(G, ["KEN", "XXX"]) == 999


def test_duplicates_ignored():
    assert check_connection(G, ["KEN", "KEN"]) == 0
