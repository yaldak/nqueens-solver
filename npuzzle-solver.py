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
    boards = boards[:10]

    print('name,board,solution,success,duration')

    evaluate_csv('RandomRestart', boards, npuzzle_hillclimb_random_step, 500000)
    evaluate_csv('SimulatedAnnealing', boards, npuzzle_hillclimb_simulatedannealing_step, 500000)
    evaluate_csv('SteepestAscent', boards, npuzzle_hillclimb_steepestascent_step, 200)

def evaluate_csv(name, boards, function, max_steps):
    total_time_start = time.perf_counter()

    for board in boards:
        time_start = time.perf_counter()
        solution = npuzzle_hillclimb(board, function, max_steps)
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

def npuzzle_hillclimb(board, function, max_steps):
    for x in range(max_steps):
        fitness = manhattan_distance(board)

        if fitness == 0:
            return board

        board = function(board)

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
                upBoard = board
                upBoard[i] = board[i - 3]
                upBoard[i - 3] = 0
                return upBoard
        elif rand == 1:
            if i < 6:
                downBoard = board
                downBoard[i] = board[i + 3]
                downBoard[i + 3] = 0
                return downBoard
        elif rand == 2:
            if i % 3 != 0:
                leftBoard = board
                leftBoard[i] = board[i - 1]
                leftBoard[i - 1] = 0
                return leftBoard
        else:
            if (i + 1) % 3 != 0:
                rightBoard = board
                rightBoard[i] = board[i + 1]
                rightBoard[i + 1] = 0
                return rightBoard

    return board

# accept the random choice with certain probability
def npuzzle_hillclimb_simulatedannealing_step(board):
    temperature = len(board)
    annealingRate = 0.95

    for i in range(len(board)):
        if board[i] == 0:
            break
    distance = manhattan_distance(board)
    temperature = max(temperature * annealingRate, 0.02)
    while True:
        randCase = random.randint(0,4)
        if randCase == 0:
            if i >= 3:
                upBoard = list(board)
                upBoard[i] = board[i-3]
                upBoard[i-3] = 0
                if manhattan_distance(upBoard) < distance:
                    return upBoard
                else:
                    deltaE = manhattan_distance(upBoard) - distance
                    acceptProbability = min(math.exp(deltaE / temperature), 1)
                    if random.random() <= acceptProbability:
                        return upBoard
        elif randCase == 1:
            if i < 6:
                downBoard = list(board)
                downBoard[i] = board[i+3]
                downBoard[i+3] = 0
                if manhattan_distance(downBoard) < distance:
                    return downBoard
                else:
                    deltaE = manhattan_distance(downBoard) - distance
                    acceptProbability = min(math.exp(deltaE / temperature), 1)
                    if random.random() <= acceptProbability:
                        return downBoard
        elif randCase == 2:
            if i%3 != 0:
                leftBoard = list(board)
                leftBoard[i] = board[i-1]
                leftBoard[i-1] = 0
                if manhattan_distance(leftBoard) < distance:
                    return leftBoard
                else:
                    deltaE = manhattan_distance(leftBoard) - distance
                    acceptProbability = min(math.exp(deltaE / temperature), 1)
                    if random.random() <= acceptProbability:
                        return leftBoard
        else:
            if (i+1)%3 != 0:
                rightBoard = list(board)
                rightBoard[i] = board[i+1]
                rightBoard[i+1] = 0
                if manhattan_distance(rightBoard) < distance:
                    return rightBoard
                else:
                    deltaE = manhattan_distance(rightBoard) - distance
                    acceptProbability = min(math.exp(deltaE / temperature), 1)
                    if random.random() <= acceptProbability:
                        return rightBoard

    return board

# for each column, calculate the collision number
# if the queen is moved to the other rows
# find the smallest one and move to it.
def npuzzle_hillclimb_steepestascent_step(board):
    for i in range(len(board)):
        if board[i] == 0:
            break
    distanceBoard = {}
    if i >= 3:
        upBoard = list(board)
        upBoard[i] = board[i-3]
        upBoard[i-3] = 0
        distanceBoard[i-3] = manhattan_distance(upBoard)
    if i < 6:
        downBoard = list(board)
        downBoard[i] = board[i+3]
        downBoard[i+3] = 0
        distanceBoard[i+3] = manhattan_distance(downBoard)
    if i%3 != 0:
        leftBoard = list(board)
        leftBoard[i] = board[i-1]
        leftBoard[i-1] = 0
        distanceBoard[i-1] = manhattan_distance(leftBoard)
    if (i+1)%3 != 0:
        rightBoard = list(board)
        rightBoard[i] = board[i+1]
        rightBoard[i+1] = 0
        distanceBoard[i+1] = manhattan_distance(rightBoard)

    shortestDistance = manhattan_distance(board)
    for point,value in distanceBoard.iteritems():
        # "<=" means "not worse than" situation
        # plain
        if value <= shortestDistance:
            shortestDistance = value

    shortestDistancePoints = []
    for point,value in distanceBoard.iteritems():
        if value == shortestDistance:
            shortestDistancePoints.append(point)

    # can not find a steeper move
    # we have come to the peek(local optimization)
    if len(shortestDistancePoints) == 0:
        # print "local optimization"
        global FAILED
        FAILED = True
        return board

    random.shuffle(shortestDistancePoints)
    board[i] = board[shortestDistancePoints[0]]
    board[shortestDistancePoints[0]]= 0
    return board

if __name__ == '__main__':
    main()
