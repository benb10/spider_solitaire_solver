from screen_reader import get_table, ranges_overlap
import cv2
import os
import pytest


def test_get_table():
    current_dir = os.path.dirname(__file__)
    input_screenshot = cv2.imread(
        os.path.join(current_dir, "test_images", "screen.png")
    )
    table = get_table(input_screenshot)

    card_values = [[card.val for card in column] for column in table]

    expected_card_values = [
        ["6", "7"],
        ["A", "10", "J"],
        ["3", "9", "6"],
        ["A", "9", "8"],
        ["7", "6", "5", "2", "8"],
        ["K", "Q", "J", "3", "2"],
        ["Q", "J", "8", "7"],
        ["7", "6", "10", "4"],
        ["3", "J", "10", "A"],
        ["7", "6", "5", "4", "3", "2", "A", "Q", "4"],
    ]

    assert card_values == expected_card_values


@pytest.mark.parametrize(
    ("range_1", "range_2", "is_overlap"),
    [((0, 1), (3, 4), False), ((31, 123), (99, 400), True)],
)
def test_ranges_overap(range_1, range_2, is_overlap):
    assert ranges_overlap(range_1, range_2) == is_overlap
