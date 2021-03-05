import os
from pathlib import Path
from collections import namedtuple
from time import time
import pyautogui as pag
import cv2
import numpy as np
from itertools import chain

Box = namedtuple("Box", ["left", "top", "width", "height"])
Card = namedtuple("Card", ["val", "box"])


def ranges_overlap(range_a, range_b):
    a_start, a_end = range_a
    b_start, b_end = range_b

    assert a_start <= a_end
    assert b_start <= b_end

    a_is_before_b = a_end < b_start
    b_is_before_a = b_end < a_start

    # The ranges are disjoint if and only if range_a is completely before b OR range_b is completely before a
    ranges_are_disjoint = a_is_before_b or b_is_before_a
    return not ranges_are_disjoint


def get_x_ranges(table):
    """
    table = [
        ['2', 'A'],
        ['K', 'J', '10' ...],
        ...,
    ]
    """
    ranges = []
    for column in table:
        lefts = [card.box.left for card in column]
        rights = [card.box.left + card.box.width for card in column]

        left = min(lefts)
        right = max(rights)

        ranges.append((left, right))

    return ranges


def get_y_ranges(column):
    ranges = []
    for card in column:
        top = card.box.top
        bottom = card.box.top + card.box.height

        ranges.append((top, bottom))

    return ranges


def get_image_matches(screenshot, target_image):
    img_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)

    height, width = target_gray.shape

    res = cv2.matchTemplate(img_gray, target_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.95
    loc = np.where(res >= threshold)

    boxes = []

    for pt in zip(*loc[::-1]):
        left, top = pt
        boxes.append(Box(left=left, top=top, width=width, height=height))

    return boxes


def card_overlaps_existing_card(card, table):
    existing_cards = chain(*table)

    for existing_card in existing_cards:
        card_x_range = (card.box.left, card.box.left + card.box.width)
        card_y_range = (card.box.top, card.box.top + card.box.height)

        existing_card_x_range = (existing_card.box.left, existing_card.box.left + existing_card.box.width)
        existing_card_y_range = (existing_card.box.top, existing_card.box.top + existing_card.box.height)
        card_boxes_overlap = ranges_overlap(card_x_range, existing_card_x_range) and ranges_overlap(card_y_range, existing_card_y_range)
        if card_boxes_overlap:
            return True
    return False


def get_table(screenshot):
    """This function reads the given screeshot and returns an object representing all the cards currently
    on the screen.

    the returned object is a list where each element is a list of cards in a column.
    """
    card_images = [
        "A.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "J.png",
        "Q.png",
        "K.png",
    ]
    card_images = ["images/" + i for i in card_images]
    current_dir = os.path.dirname(__file__)
    table = []

    for card_image_file in card_images:
        card_path = os.path.join(current_dir, card_image_file)
        card_image = cv2.imread(card_path)
        if card_image is None:
            raise ValueError(f"Could not read card image {card_path}.")
        boxes = get_image_matches(screenshot, target_image=card_image)

        for box in boxes:
            # which row is it in?
            # where in that row is it?
            card = Card(val=card_image_file.split("/")[-1].split(".")[0], box=box)

            if not table:
                table.append([card])
                continue

            if card_overlaps_existing_card(card, table):
                print(f"Skipping match for {card_image_file}.  It overlaps an existing card.")
                continue

            x_ranges = get_x_ranges(table)

            card_x_range = (card.box.left, card.box.left + card.box.width)

            matches = [
                i
                for i, range in enumerate(x_ranges)
                if ranges_overlap(card_x_range, range)
            ]

            if not matches:
                # make a new row:
                rows_to_left = [
                    i for i, range in enumerate(x_ranges) if card.box.left > range[1]
                ]
                if not rows_to_left:
                    table.insert(0, [card])
                    continue

                row_to_left = max(rows_to_left)
                insert_loc = row_to_left + 1
                table.insert(insert_loc, [card])
                continue

            assert len(matches) == 1
            match = matches[0]
            column = table[match]

            # where in that column does it go:
            y_ranges = get_y_ranges(column)
            cards_above = [
                i for i, range in enumerate(y_ranges) if card.box.top > range[1]
            ]
            if not cards_above:
                column.insert(0, card)
                continue

            card_index_above = max(cards_above)
            insert_loc = card_index_above + 1
            column.insert(insert_loc, card)

    return table


def get_card_locations():
    start_time = time()
    print(f"Reading the cards on screen... ", end="")
    screenshot = pag.screenshot()

    # debug step
    dir_name = os.path.split(__file__)[0]
    debug_dir = os.path.join(dir_name, "debug")
    Path(debug_dir).mkdir(exist_ok=True)
    screenshot.save(os.path.join(debug_dir, "screenshot.png"), "PNG")

    table = get_table(np.array(screenshot))
    print(f"Finished in {time() - start_time} seconds")

    return table
