import numpy as np
from math import pow
from linked_list import Node

SIZE = 5

# proba[x, y][v] = probability of having the value v at spot (x, y)
proba = np.zeros((SIZE, SIZE, 4))
known = np.zeros((SIZE, SIZE)) - 1


############################################################
###     STEP 0 - Set the board
############################################################

vertical_data   = [(2, 3), (4, 2), (5, 1), (3, 3), (7, 1)]
horizontal_data = [(7, 0), (4, 1), (7, 1), (5, 2), (1, 4)]

print("Ok, tell me what the board is.")
print("First, let's do vertical readings")
for i in range(SIZE):
    print(f" > number of points in the {i + 1}th row ? ", end='')
    p = int(input())
    print(f" > number of bombs in the {i + 1}th row ? ", end='')
    b = int(input())

    vertical_data[i] = (p, b)
print("Now, let's do horizontal readings")
for i in range(SIZE):
    print(f" > number of points in the {i + 1}th column ? ", end='')
    p = int(input())
    print(f" > number of bombs in the {i + 1}th column ? ", end='')
    b = int(input())

    horizontal_data[i] = (p, b)

############################################################
###     STEP 1 - Initial requests
############################################################

total_points = 0
for i in range(SIZE):
    total_points += vertical_data[i][0]
collected = 0

def ask(x, y, tell=True):
    global proba, collected

    if known[x, y] >= 0:
        return x, y, known[x, y]

    if tell:
        if proba[x, y, 0] >= 0.3:
            print(f"It is a gamble ! ", end='')
        print(f"{round(proba[x, y, 0] * 100)}% chances of loosing. ", end='')

    print(f"What is at ({x + 1}, {y + 1}) ? ", end='')
    inp = input()
    if inp == 's':
        print("x: ", end='')
        x = int(input()) - 1
        print("y: ", end='')
        y = int(input()) - 1
        print("value: ", end='')
        inp = input()
    val = int(inp)
    proba[x, y] = np.zeros(4)
    proba[x, y, val] = 1
    known[x, y] = val
    collected += val

    return x, y, val

def ask_safe():
    global collected
    
    # Vertical swipe
    for y in range(SIZE):
        if vertical_data[y][1] == 0:
            if vertical_data[y][0] == 5:
                for x in range(SIZE):
                    proba[x, y] = np.zeros(4)
                    proba[x, y, 1] = 1
                    known[x, y] = 1
                    collected += 1
            else:
                for x in range(SIZE):
                    ask(x, y, tell=False)

    # Horizontal swipe
    for x in range(SIZE):
        if horizontal_data[x][1] == 0:
            if horizontal_data[x][0] == 5:
                for y in range(SIZE):
                    proba[x, y] = np.zeros(4)
                    proba[x, y, 1] = 1
                    known[x, y] = 1
                    collected += 1
            else:
                for y in range(SIZE):
                    ask(x, y, tell=False)

ask_safe()


############################################################
###     STEP 2 - Generate possible scenarios
############################################################
head = None
count = 0

def get_board():
    board = np.zeros((SIZE, SIZE), dtype=np.int8) - 1
    for x in range(SIZE):
        for y in range(SIZE):
            if known[x, y] >= 0:
                board[x, y] = known[x, y]

    return board

def get_next_spot(board):
    for x in range(SIZE):
        for y in range(SIZE):
            if board[x, y] < 0:
                return (x, y)

    return None

# Generate all possible scenarios
def try_scenario(board):
    spot = get_next_spot(board)

    if spot is None:
        global head

        # The senario is plausible
        if head is None:
            head = Node(board)
        else:
            new = Node(board)
            new.next = head
            head = new
        return

    # Found an empty spot
    x, y = spot
    for val in range(4):
        copy = board.copy()
        copy[x, y] = val

        # Already exceeded
        if np.sum(copy[x, :(y+1)]) > horizontal_data[x][0]:
            continue
        if np.sum(copy[:(x+1), y]) > vertical_data[y][0]:
            continue

        # Finished a column
        if len(np.where(copy[x, :] == -1)[0]) == 0:
            if np.sum(copy[x]) != horizontal_data[x][0] or len(np.where(copy[x, :] == 0)[0]) != horizontal_data[x][1]:
                # The scenario is not possible
                continue

        # Finished a row
        if len(np.where(copy[:, y] == -1)[0]) == 0:
            if np.sum(copy[:, y]) != vertical_data[y][0] or len(np.where(copy[:, y] == 0)[0]) != vertical_data[y][1]:
                # The scenario is not possible
                continue

        # The senario is still possible
        try_scenario(copy)

def set_count():
    global count

    count = 0
    node = head
    while node is not None:
        count += 1
        node = node.next

print("Give me some time to think...")
try_scenario(get_board())
set_count()
print(f"Found {count} possible scenarios")


############################################################
###     STEP 3 - Game and gamble
############################################################

def set_probabilities():
    global proba
    proba = np.zeros((SIZE, SIZE, 4))

    node = head
    while node is not None:
        for x in range(SIZE):
            for y in range(SIZE):
                proba[x, y, node.val[x, y]] += 1
        node = node.next

    for x in range(SIZE):
        for y in range(SIZE):
            proba[x, y] /= count

def get_expected_value(prob):
    return prob[2] * 2 + prob[3] * 3 - 50 * prob[0]

def get_request():
    max_x = max_y = 0
    max = -100000.0

    for x in range(SIZE):
        for y in range(SIZE):
            if known[x, y] < 0:
                if get_expected_value(proba[x, y]) > max or \
                    (get_expected_value(proba[x, y]) == max and proba[x, y, 0] < proba[max_x, max_y, 0]):
                    max = get_expected_value(proba[x, y])
                    max_x = x
                    max_y = y

    x, y, val = ask(max_x, max_y)
    return x, y, val

def update(x, y, val):
    global head
    node = head
    prev = None
    while node is not None:
        if node.val[x, y] != val:
            if prev is not None:
                prev.remove_next()
                node = prev.next
            else:
                head = node.next
                node = head
        else:
            prev = node
            node = node.next

try:
    print()
    print("Let's start the fun part now")

    while True:
        if collected == total_points:
            print('Congratulations !')
            break

        set_probabilities()
        x, y, val = get_request()
        if val == 0:
            print("Oops. Unlucky you")
            print("Continue nonetheless ? [y/N]", end='')
            if input() != 'y':
                break
        update(x, y, val)
        set_count()
        if count == 0:
            print("A problem occurred: no scenarios left...")
            break
        print(f" > Only {count} possible scenarios left")

except KeyboardInterrupt:
    print('')
    print("Bye")
