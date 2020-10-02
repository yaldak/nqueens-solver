#!/usr/bin/env python3

import argparse
import math
import pprint
import random
import requests
import requests.exceptions
import sys
import time

def main():
    parser = argparse.ArgumentParser(
        description="""
    Generate a large number of 8-puzzle instances and
    solve them (where possible) by hill climbing (steepest-ascent and
    first-choice variants), hill climbing with random restart, and
    simulated annealing.  Measure the search cost and percentage of
    solved problems.
        """,
    )

    parser.add_argument('BOARDFILE', help='path to the boards file')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    boardfile_path = args.BOARDFILE.strip()
    boardfile_file = open(boardfile_path, 'r')
    boardfile_lines = boardfile_file.readlines()
    boards = parse_boardfile_lines(boardfile_lines)

    # ARTIFICIAL LIMIT
    boards = boards[:100]

    print('name,board,solution,success,duration')

    evaluate_csv('RandomRestart', boards, npuzzle_hillclimb_random_step, 500000)
    evaluate_csv('SimulatedAnnealing', boards, npuzzle_hillclimb_simulatedannealing_step, 500000)
    evaluate_csv('SteepestAscent', boards, npuzzle_hillclimb_steepestascent_step, 200)
    evaluate_csv('FirstChoice', boards, npuzzle_hillclimb_firstchoice_step, 200)

def evaluate_csv(name, boards, function, max_steps):
    total_time_start = time.perf_counter()

    for board in boards:
        time_start = time.perf_counter()
        solution = npuzzle_hillclimb(board, function, max_steps)
        time_end = time.perf_counter()

        duration = str(time_end - time_start)

        success = 'true' if solution is not None else 'false'

        print(f""{name}","{board}","{solution}",{success},{duration}")

    total_time_end = time.perf_counter()

def parse_boardfile_lines(lines):
    result = []

    for line in lines:
        # TODO: validation
        cols_str = line.strip().split()
        cols_int = list(map(lambda y: int(y), cols_str))

        result.append(cols_int)

    return result

def npuzzle_hillclimb(board, function, max_steps):
    for x in range(max_steps):
        fitness = manhattan_distance(board)

        if fitness == 0:
            return board

        board = function(board)

        # XXX: Do I need this?
        if board is None:
            return None

    return None

def manhattan_distance(board):
    distance = 0

    for i in range(len(board)):
        distance += abs(i / 3 - board[i] / 3) + abs(i % 3 - board[i] % 3)

    return distance

def npuzzle_hillclimb_random_step(board):
    for i in range(len(board)):
        if board[i] == 0:
            break

    while True:
        rand = random.randint(0, 4)

        if rand == 0:
            if i >= 3:
                board_new = list(board)
                board_new[i] = board[i - 3]
                board_new[i - 3] = 0
                return board_new
        elif rand == 1:
            if i < 6:
                board_new = list(board)
                board_new[i] = board[i + 3]
                board_new[i + 3] = 0
                return board_new
        elif rand == 2:
            if i % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i - 1]
                board_new[i - 1] = 0
                return board_new
        else:
            if (i + 1) % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i + 1]
                board_new[i + 1] = 0
                return board_new

    return board

def npuzzle_hillclimb_firstchoice_step(board):
    for i in range(len(board)):
        if board[i] == 0:
            break
    distance = manhattan_distance(board)

    while True:
        rand = random.randint(0, 4)

        if rand == 0:
            if i >= 3:
                board_new = list(board)
                board_new[i] = board[i - 3]
                board_new[i - 3] = 0

                if manhattan_distance(board_new) <= distance:
                    return board_new
                else:
                    return board
        elif rand == 1:
            if i < 6:
                board_new = list(board)
                board_new[i] = board[i + 3]
                board_new[i + 3] = 0

                if manhattan_distance(board_new) <= distance:
                    return board_new
                else:
                    return board
        elif rand == 2:
            if i % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i - 1]
                board_new[i - 1] = 0

                if manhattan_distance(board_new) <= distance:
                    return board_new
                else:
                    return board
        else:
            if (i + 1) % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i + 1]
                board_new[i + 1] = 0

                if manhattan_distance(board_new) <= distance:
                    return board_new
                else:
                    return board
    return board

def npuzzle_hillclimb_simulatedannealing_step(board):
    for i in range(len(board)):
        if board[i] == 0:
            break

    annealing_rate = 0.95
    distance = manhattan_distance(board)
    temperature = max(len(board) * annealing_rate, 0.02)

    while True:
        rand = random.randint(0, 4)

        if rand == 0:
            if i >= 3:
                board_new = list(board)
                board_new[i] = board[i - 3]
                board_new[i - 3] = 0

                if manhattan_distance(board_new) < distance:
                    return board_new
                else:
                    delta = manhattan_distance(board_new) - distance
                    probability = min(math.exp(delta / temperature), 1)

                    if random.random() <= probability:
                        return board_new
        elif rand == 1:
            if i < 6:
                board_new = list(board)
                board_new[i] = board[i + 3]
                board_new[i + 3] = 0

                if manhattan_distance(board_new) < distance:
                    return board_new
                else:
                    delta = manhattan_distance(board_new) - distance
                    probability = min(math.exp(delta / temperature), 1)

                    if random.random() <= probability:
                        return board_new
        elif rand == 2:
            if i % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i - 1]
                board_new[i - 1] = 0

                if manhattan_distance(board_new) < distance:
                    return board_new
                else:
                    delta = manhattan_distance(board_new) - distance
                    probability = min(math.exp(delta / temperature), 1)

                    if random.random() <= probability:
                        return board_new
        else:
            if (i + 1) % 3 != 0:
                board_new = list(board)
                board_new[i] = board[i + 1]
                board_new[i + 1] = 0

                if manhattan_distance(board_new) < distance:
                    return board_new
                else:
                    delta = manhattan_distance(board_new) - distance
                    probability = min(math.exp(delta / temperature), 1)

                    if random.random() <= probability:
                        return board_new

    return board

def npuzzle_hillclimb_steepestascent_step(board):
    for i in range(len(board)):
        if board[i] == 0:
            break

    board_distance = {}

    if i >= 3:
        board_new = list(board)
        board_new[i] = board[i - 3]
        board_new[i - 3] = 0

        board_distance[i - 3] = manhattan_distance(board_new)
    if i < 6:
        board_new = list(board)
        board_new[i] = board[i + 3]
        board_new[i + 3] = 0

        board_distance[i + 3] = manhattan_distance(board_new)
    if i % 3 != 0:
        board_new = list(board)
        board_new[i] = board[i - 1]
        board_new[i - 1] = 0

        board_distance[i - 1] = manhattan_distance(board_new)
    if (i + 1) % 3 != 0:
        board_new = list(board)
        board_new[i] = board[i + 1]
        board_new[i + 1] = 0

        board_distance[i + 1] = manhattan_distance(board_new)

    shortestDistance = manhattan_distance(board)
    for point, value in board_distance.items():
        # "<=" means "not worse than" situation
        # plain
        if value <= shortestDistance:
            shortestDistance = value

    shortestDistancePoints = []
    for point, value in board_distance.items():
        if value == shortestDistance:
            shortestDistancePoints.append(point)

    # can not find a steeper move
    # we have come to the peek(local optimization)
    if len(shortestDistancePoints) == 0:
        return None

    random.shuffle(shortestDistancePoints)
    board[i] = board[shortestDistancePoints[0]]
    board[shortestDistancePoints[0]]= 0

    return board

if __name__ == '__main__':
    main()
