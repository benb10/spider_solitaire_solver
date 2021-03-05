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

    expected_card_values = [['10', '8', 'J', 'K', 'K', '7'],
 ['7', 'A', 'Q', 'J', 'Q', 'Q'],
 ['10', '5', '5', '6', '10', '5'],
 ['3', '2', 'A', '4', '3', '9', '6', 'J'],
 ['5', '6', '4', 'K', '3', '8'],
 ['3', 'J', '10', '6', '2', '6'],
 ['K', '9', '4', '7', 'Q', '4'],
 ['8', 'K', '6', 'J', '8', '9'],
 ['3', '8', '7', '4', '8', 'J'],
 ['10', 'Q', 'A', '4', '2', 'J']]

    assert card_values == expected_card_values


@pytest.mark.parametrize(
    ("range_1", "range_2", "is_overlap"),
    [((0, 1), (3, 4), False), ((31, 123), (99, 400), True)],
)
def test_ranges_overap(range_1, range_2, is_overlap):
    assert ranges_overlap(range_1, range_2) == is_overlap
