import pyautogui as pag
from time import time, sleep
from itertools import permutations
from copy import deepcopy

from screen_reader import get_card_locations


card_to_num = {str(i): i for i in range(2, 11)}
card_to_num["J"] = 11
card_to_num["Q"] = 12
card_to_num["K"] = 13
card_to_num["A"] = 1

pag.PAUSE = 0.3
pag.FAILSAFE = True


def get_run(column):

    col_bottom_up = column[::-1]

    run = [col_bottom_up[0]]

    for card, card_above in zip(col_bottom_up, col_bottom_up[1:]):
        cards_consecutive = card_to_num[card.val] + 1 == card_to_num[card_above.val]
        if not cards_consecutive:
            break
        # keep going up
        run.insert(0, card_above)
        continue
    return run


def get_cards_to_click_full_runs(runs):
    cards_to_click = []
    for run, other_run in permutations(runs, 2):
        # we can make a move on the 'run' if the top card of it is one below the bottom
        # card of the other run

        top_run_val = run[0].val
        bottom_other_run_val = other_run[-1].val

        can_make_move = (
            card_to_num[top_run_val] + 1 == card_to_num[bottom_other_run_val]
        )

        if can_make_move:
            cards_to_click.append(run[0])
    return cards_to_click


def get_cards_to_click_partial_runs_multiple(runs, table):
    all_cards_to_click = []

    # Keep new copy so we don't mutate these
    runs = deepcopy(runs)
    table = deepcopy(table)

    print("")
    print("running get_cards_to_click_partial_runs_multiple")
    count = 0

    while True:
        if count > 8:
            print(f"Issue in get_cards_to_click_partial_runs_multiple.  Breaking loop")
            # TODO investigate and fix this
            return all_cards_to_click

        cards_to_click = get_cards_to_click_partial_runs(runs, table)

        count += 1
        print(
            f"    Run number {count} of get_cards_to_click_partial_runs, clicking {[c.val for c in cards_to_click]}"
        )
        all_cards_to_click.extend(cards_to_click)

        # Now modify runs and table to reflect the moves that have been made.  THis may not be 100% accurate.
        for card_to_click in cards_to_click:
            card_positions = [
                (i, j)
                for i, col in enumerate(table)
                for j, card in enumerate(col)
                if card == card_to_click
            ]
            assert len(card_positions) == 1
            card_col, card_num = card_positions[0]

            cards_being_moved = table[card_col][card_num:]
            # remove from this row:
            table[card_col] = table[card_col][:card_num]

            # remove any columns from table if they no longer have any cards:
            table = [col for col in table if col]

            cols_it_could_be_placed_on = [
                col
                for col_num, col in enumerate(table)
                if card_to_num[col[-1].val] == card_to_num[card_to_click.val] + 1
                and col_num != card_col  # card will move onto a different column
            ]

            if not cols_it_could_be_placed_on:
                print(f"Issue at col_it_could_be_placed_on.  Exiting function")
                # TODO investigate and fix this
                return all_cards_to_click

            # Not sure which one because we are just clicking.  The website chooses which one it goes on
            # Just pick one:
            col_it_could_be_placed_on = cols_it_could_be_placed_on[0]
            col_it_could_be_placed_on.extend(cards_being_moved)

        # now just update the runs:
        runs = [get_run(col) for col in table]

        if not cards_to_click:
            break

    print("")

    return all_cards_to_click


def get_cards_to_click_partial_runs(runs, table):
    # TODO preference moves which open up empty rows
    # eg if there are two 6s to move to a 7, choose the one which is higher up on the screen?

    def _run_pair_sorter(run_pair):
        """Return a tuple to define the order that run pairs are considered for moves.
        Bigger tuple comes first (i.e. sorting with reverse=True)
        """
        run, other_run = run_pair

        return (len(run) + len(other_run), len(other_run))

    cards_to_click = []
    run_pairs = sorted(permutations(runs, 2), key=_run_pair_sorter, reverse=True)
    for run, other_run in run_pairs:

        bottom_other_run_val = other_run[-1].val
        for i, card in enumerate(run):

            this_card_val = card.val
            # we can make a move on the 'run' a card is one lower than the bottom of other_run
            # and also check that the resulting run will be longer.  THis should prevent useless
            # moves back and forth (and counterproductive moves)
            num_cards_moved = len(run) - i
            destination_run_size = len(other_run)
            resulting_run_size = num_cards_moved + destination_run_size

            can_make_move = card_to_num[this_card_val] + 1 == card_to_num[
                bottom_other_run_val
            ] and resulting_run_size > len(run)

            if can_make_move:
                # We don't want a card entered twice
                # We also don't want the same value entered twice because the second one is usually invalid
                # i.e. if there is a 7 and two 6s, we can only move one of the 6s.  Clicking both
                # sometimes makes no difference, and othertimes is an annoyance with the second 6
                # going down to a blank row
                cards_to_click_vals = {card.val for card in cards_to_click}
                if card.val not in cards_to_click_vals:
                    cards_to_click.append(card)
                break
    return cards_to_click


def run():
    start_time = time()

    NUM_COLUMNS = 10

    new_row_count = 0
    new_row_locs = [
        (360, 202),
        (339, 202),
        (321, 202),
        (302, 202),
        (281, 202),
    ]

    consecutive_blank_fill_count = 0

    while True:
        print("reading table...")
        table = get_card_locations()

        if table:
            print(f"Found {sum(len(col) for col in table)} cards on the screen")
        else:
            raise ValueError("Unable to identify any cards on the screen")
        print("finished reading table.")

        runs = [get_run(col) for col in table]
        vals = [[card.val for card in column] for column in table]
        run_vals = [[card.val for card in column] for column in runs]
        print("columns:")
        for col in vals:
            print(col)
        print("runs:")
        for col in run_vals:
            print(col)

        # cards_to_click = get_cards_to_click_partial_runs(runs, table)
        cards_to_click = get_cards_to_click_partial_runs_multiple(runs, table)
        ######

        cards_to_click_vals = [card.val for card in cards_to_click]
        print(f"Found these cards to click: {cards_to_click_vals}")

        # Avoid infinite loop where there are 2 runs on the top row:
        ok_to_fill_blank = consecutive_blank_fill_count < 5

        if not cards_to_click and len(table) < NUM_COLUMNS and ok_to_fill_blank:
            consecutive_blank_fill_count += 1

            # click one of the runs to fill the blank space
            top_of_runs = [run[0] for run in runs]
            # We want to avoid an infinite loop when trying to fill a blank column.  kept
            # clicking a card that was already down
            # A basic solution: just avoid clicking the highest card
            highest_card = min(top_of_runs, key=lambda card: card.box.top)

            card_to_click = max(
                top_of_runs,
                key=lambda card: (card != highest_card, card_to_num[card.val]),
                # card.box.top to avoid an infinite loop when trying to fill a blank column.  kept
                # clicking a card that was already down
            )
            print(f"filling blank space, clicking {card_to_click.val}")
            card_centre = pag.center(card_to_click.box)
            pag.moveTo(card_centre[0], card_centre[1], duration=0.5)
            pag.click(card_centre)
            continue

        consecutive_blank_fill_count = 0

        if not cards_to_click:
            # click for new row to come down:
            print("clicking the next row down")
            new_row_loc = new_row_locs[new_row_count]
            new_row_count += 1
            pag.moveTo(new_row_loc[0], new_row_loc[1], duration=0.5)
            pag.click(new_row_loc)
            sleep(
                2
            )  # wait for a moment while the cards all move into place, before we read the screen
            continue

        for card in cards_to_click:
            card_centre = pag.center(card.box)
            pag.moveTo(card_centre[0], card_centre[1], duration=0.5)
            pag.click(card_centre)

        print(f"Runtime: {time() - start_time} s")


if __name__ == "__main__":
    run()
