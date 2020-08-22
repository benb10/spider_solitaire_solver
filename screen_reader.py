import os
from collections import namedtuple
from PIL import Image
import numpy
from time import time
import pyautogui as pag

Box = namedtuple("Box", ["left", "top", "width", "height"])
Card = namedtuple("Card", ["val", "box"])

def to_list(array):
    lst = []
    for row in array:
        lst.append([])
        for element in row:
            lst[-1].append(tuple(element))
    return lst


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


def get_card_locations():
    """This function reads the screen and returns an object representing all the cards currently
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

    # im = pag.screenshot()

    x_min = 265
    x_max = 1301
    y_min = 259
    y_max = 636
    # left, top, width, height
    search_region = Box(x_min, y_min, x_max - x_min, y_max - y_min)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    table = []

    for card_image_file in card_images:
        card_image = Image.open(os.path.join(current_dir, card_image_file))
        card_image_list = to_list(numpy.asarray(card_image))
        # readin this way, we get 4 tuples instead of size 3 tuples.  Trim them down
        card_image_list = [[t[:3] for t in row] for row in card_image_list]

        # Ace is at [Box(left=590, top=337, width=60, height=9)]
        st = time()
        found_cards = list(
            pag.locateAllOnScreen(card_image, region=search_region, grayscale=True)
        )  # comment out later.  Just for testing
        print(f"locateAllOnScreen method took {time() - st} s")

        for found_card in found_cards:

            # which row is it in?
            # where in that row is it?
            card = Card(
                val=card_image_file.split("/")[-1].split(".")[0], box=found_card
            )

            if not table:
                table.append([card])
                continue

            x_ranges = get_x_ranges(table)

            card_x = pag.center(card.box).x
            card_y = pag.center(card.box).y

            matches = [
                i
                for i, range in enumerate(x_ranges)
                if card_x > range[0] and card_x < range[1]
            ]

            if not matches:
                # make a new row:
                rows_to_left = [
                    i for i, range in enumerate(x_ranges) if card_x > range[1]
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
            cards_above = [i for i, range in enumerate(y_ranges) if card_y > range[1]]
            if not cards_above:
                column.insert(0, card)
                continue

            card_index_above = max(cards_above)
            insert_loc = card_index_above + 1
            column.insert(insert_loc, card)

    return table
