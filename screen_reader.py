import os
from pathlib import Path
from collections import namedtuple
from time import time
import pyautogui as pag
import cv2
import numpy as np
from itertools import chain
from copy import deepcopy

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

        existing_card_x_range = (
            existing_card.box.left,
            existing_card.box.left + existing_card.box.width,
        )
        existing_card_y_range = (
            existing_card.box.top,
            existing_card.box.top + existing_card.box.height,
        )
        card_boxes_overlap = ranges_overlap(
            card_x_range, existing_card_x_range
        ) and ranges_overlap(card_y_range, existing_card_y_range)
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
        card_image = read_image(os.path.join(current_dir, card_image_file))
        boxes = get_image_matches(screenshot, target_image=card_image)

        for box in boxes:
            # which row is it in?
            # where in that row is it?
            card = Card(val=card_image_file.split("/")[-1].split(".")[0], box=box)

            if not table:
                table.append([card])
                continue

            if card_overlaps_existing_card(card, table):
                print(
                    f"Skipping match for {card_image_file}.  It overlaps an existing card."
                )
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

    table = removes_aces_at_top(table)

    return table


def removes_aces_at_top(table):
    """Remove aces which are in the top row, showing the completed runs.

    This is a post processing step which is run after the screen is read.

    The rule of thumb is to iterate through each column and remove an
    ace at the top if it is more than x pixels higher than the highest
    non ace card in on the table.
    """
    # Code used to check avg distances:

    # for col in table:
    #     for (a, b) in zip(col, col[1:]):
    #         a_bottom = a.box.top + a.box.height
    #         print(f"aaaaaa {b.box.top - a_bottom}")

    # avg_distance_between_stacked_cards = 30  # pixels
    # avg_distance_to_top_aces = 180  # pixels

    ACE_CEILING_BUFFER = 100  # rough estimate based on investigation

    all_cards = chain(*table)
    non_ace_cards = [c for c in all_cards if c.val != "A"]
    highest_non_ace_card = min(non_ace_cards, key=lambda c: c.box.top)
    ace_ceiling = highest_non_ace_card.box.top - ACE_CEILING_BUFFER

    new_table = deepcopy(table)

    for column in new_table:
        top_card = column[0]
        if top_card.val != "A":
            continue

        # remember that lower "top" values are higher on the screen
        ace_is_too_high = top_card.box.top < ace_ceiling

        if ace_is_too_high:
            print(f"Removing card identified as top ro ace: {top_card}.")
            column.pop(0)

    # we may have reduced a column ot an empty list.  Remove them:
    new_table = [col for col in new_table if col]

    return new_table


def read_image(filepath):
    image = cv2.imread(filepath)
    if image is None:
        # If the file path does not exist, image will just be None.
        # Let's raise an error here
        raise ValueError(f"Could not read card image {filepath}.")
    return image


def get_new_rew_loc():
    new_row_card_image = read_image(
        os.path.join(os.path.dirname(__file__), "images/new_row.png")
    )

    screenshot = get_screenshot()

    boxes = get_image_matches(screenshot, target_image=new_row_card_image)

    # Hopefully the first one is correct:
    return pag.center(boxes[0])


def get_screenshot():
    screenshot = pag.screenshot()

    # debug step
    dir_name = os.path.split(__file__)[0]
    debug_dir = os.path.join(dir_name, "debug")
    Path(debug_dir).mkdir(exist_ok=True)
    screenshot.save(os.path.join(debug_dir, "screenshot.png"), "PNG")

    return np.array(screenshot)


def get_card_locations():
    start_time = time()
    print(f"Reading the cards on screen... ", end="")
    screenshot = get_screenshot()
    table = get_table(screenshot)
    print(f"Finished in {time() - start_time} seconds")

    return table
