import pytest
from pycardgolf.utils.enums import Rank, Suit


def test_rank_comparison():
    assert Rank.QUEEN < Rank.KING
    assert Rank.QUEEN > Rank.JACK
    assert Rank.QUEEN == Rank.QUEEN


@pytest.mark.parametrize("lesser,greater", [
    (Suit.CLUBS, Suit.DIAMONDS),
    (Suit.DIAMONDS, Suit.HEARTS),
    (Suit.HEARTS, Suit.SPADES),
])
def test_suit_comparison_less_than(lesser, greater):
    # Test Suit.__lt__ method
    assert lesser < greater
    assert not greater < lesser


@pytest.mark.parametrize("rank", list(Rank))
def test_rank_in_enum(rank):
    # Test that all Rank values are in the Rank enum
    assert rank in Rank


@pytest.mark.parametrize("suit", list(Suit))
def test_suit_in_enum(suit):
    # Test that all Suit values are in the Suit enum
    assert suit in Suit


def test_rank_str():
    # Test Rank.__str__ method
    assert str(Rank.ACE) == "A"
    assert str(Rank.TWO) == "2"
    assert str(Rank.JACK) == "J"
    assert str(Rank.QUEEN) == "Q"
    assert str(Rank.KING) == "K"
