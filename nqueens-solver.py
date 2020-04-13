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
    Generate a large number of 8-puzzle and 8-queens instances and
    solve them (where possible) by hill climbing (steepest-ascent and
    first-choice variants), hill climbing with random restart, and
    simulated annealing.  Measure the search cost and percentage of
    solved problems and graph these against the optimal solution cost.

    Comment your results.

    TODO: describe how to define the board
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
    boards = boards[:3]

    print('name,board,solution,success,duration')

    evaluate_csv('RandomRestart', boards, nqueens_hillclimb_random_step, 500000)
    evaluate_csv('SimulatedAnnealing', boards, nqueens_hillclimb_simulatedannealing_step, 500000)
    evaluate_csv('SteepestAscent', boards, nqueens_hillclimb_steepestascent_step, 200)

def evaluate_csv(name, boards, function, max_steps):
    total_time_start = time.perf_counter()

    for board in boards:
        time_start = time.perf_counter()
        solution = nqueens_hillclimb(board, function, max_steps)
        time_end = time.perf_counter()

        duration = str(time_end - time_start)

        success = 'true' if solution is not None else 'false'

        print(f"{name},{board},{solution},{success},{duration}")

    total_time_end = time.perf_counter()

def parse_boardfile_lines(lines):
    result = []

    for line in lines:
        # TODO: validation
        cols_str = line.strip().split()
        cols_int = list(map(lambda y: int(y), cols_str))

        result.append(cols_int)

    return result

def nqueens_hillclimb(board, function, max_steps):
    for x in range(max_steps):
        fitness = nqueens_fitness_max(board)

        if fitness == 0:
            return board

        board = function(board)

    return None

def nqueens_fitness_max(board):
    fitness = 0

    for col1 in range(len(board)):
        for col2 in range(col1 + 1, len(board)):
            if board[col1] == board[col2]:
                # Collision in same row
                fitness += 1
            elif abs(board[col1] - board[col2]) == (col2 - col1):
                # Collision diagonally
                fitness += 1

    # returns number of collisions
    return fitness

def nqueens_hillclimb_random_step(board):
    while True:
        rand_row = random.randint(0, len(board) - 1)
        rand_col = random.randint(0, len(board) - 1)

        if board[rand_col] != rand_row:
            board[rand_col] = rand_row

            return board

    # TODO: log error
    return board

# accept the random choice with certain probability
def nqueens_hillclimb_simulatedannealing_step(board):
    temperature = len(board) ** 2
    annealingRate = 0.95

    while True:
        rand_row = random.randint(0, len(board) - 1)
        rand_col = random.randint(0, len(board) - 1)

        originCollisionNum = nqueens_fitness_max(board)
        originRow = board[rand_col]

        board[rand_col] = rand_row

        newCollisionNum = nqueens_fitness_max(board)
        temperature = max(temperature * annealingRate, 0.02)

        if newCollisionNum < originCollisionNum:
            return board
        else:
            deltaE = newCollisionNum - originCollisionNum
            acceptProbability = min(math.exp(deltaE / temperature), 1)
            if random.random() <= acceptProbability:
                return board
            else:
                board[rand_col] = originRow

    return board

# for each column, calculate the collision number
# if the queen is moved to the other rows
# find the smallest one and move to it.
# steps = 200
def nqueens_hillclimb_steepestascent_step(board):
    collisionNumBoard = {}
    smallestCollisionNum = nqueens_fitness_max(board)
    for col in range(len(board)):
        for row in range(len(board)):
            if board[col] == row:
                continue
            originRow = board[col]
            board[col] = row
            collisionNumBoard[(row,col)] = nqueens_fitness_max(board)
            board[col] = originRow

    for point,value in collisionNumBoard.iteritems():
        if value < smallestCollisionNum:
            smallestCollisionNum = value

    smallestCollisionPoints = []
    for point,value in collisionNumBoard.iteritems():
        if value == smallestCollisionNum:
            smallestCollisionPoints.append(point)

    # can not find a steeper move
    # we have come to the peek(local optimization)
    if len(smallestCollisionPoints) == 0:
        return None

    random.shuffle(smallestCollisionPoints)
    board[smallestCollisionPoints[0][1]]=smallestCollisionPoints[0][0]
    return board

if __name__ == '__main__':
    main()
