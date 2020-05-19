import random
from collections import Counter
import matplotlib.pyplot as plt

six_sided_die = ["""
-----------
|         |
|    0    |
|         |
-----------""", """
-----------
| 0       |
|         |
|       0 |
-----------""", """
-----------
| 0       |
|    0    |
|       0 |
-----------""", """
-----------
| 0     0 |
|         |
| 0     0 |
-----------""", """
-----------
| 0     0 |
|    0    |
| 0     0 |
-----------""", """
-----------
| 0     0 |
| 0     0 |
| 0     0 |
-----------"""]


def calculate_mean(numbers):
    s = sum(numbers)
    N = len(numbers)
    # Calculate the mean
    mean = s / N

    return mean


def calculate_median(numbers):
    elements = len(numbers)
    numbers.sort()

    # Find the median
    if elements % 2 == 0:
        # if N is even
        m1 = elements / 2
        m2 = (elements / 2) + 1
        # Convert to integer, match position
        m1 = int(m1) - 1
        m2 = int(m2) - 1
        median = (numbers[m1] + numbers[m2]) / 2
    else:
        m = (elements + 1) / 2
        # Convert to integer, match position
        m = int(m) - 1
        median = numbers[m]

    return median


def calculate_mode(numbers):
    c = Counter(numbers)
    numbers_freq = c.most_common()
    max_count = numbers_freq[0][1]

    modes = []
    for num in numbers_freq:
        if num[1] == max_count:
            modes.append(num[0])
    return modes


def create_bar_chart(data, labels):
    # Number of bars
    num_bars = len(data)
    # This list is the point on the y-axis where each bar is centered. Here it will be [1, 2, 3...]
    positions = range(1, num_bars+1)
    plt.barh(positions, data, align='center')
    # Set the label of each bar
    plt.yticks(positions, labels)
    plt.xlabel('Rolls')
    plt.ylabel('Side')
    plt.title('Number of Rolls')
    # Turns on the which may assist in visual estimation
    plt.grid()
    plt.show()


num_rolls = int(input("Enter how many dice to roll: "))
track_rolls = [] * num_rolls
for i in range(num_rolls):
    roll = random.randint(0, 5)
    track_rolls.append(roll + 1)


ones = track_rolls.count(1)
twos = track_rolls.count(2)
threes = track_rolls.count(3)
fours = track_rolls.count(4)
fives = track_rolls.count(5)
sixes = track_rolls.count(6)
rolls = [ones, twos, threes, fours, fives, sixes]
labels = six_sided_die

print(ones, twos, threes, fours, fives, sixes)
print("The most common number was {}".format(calculate_mode(track_rolls)))
ones_odds = ones / num_rolls
twos_odd = twos / num_rolls
threes_odds = threes / num_rolls
fours_odd = fours / num_rolls
fives_odds = fives / num_rolls
sixes_odd = sixes / num_rolls

total_odds = [ones_odds, twos_odd, threes_odds, fours_odd, fives_odds, sixes_odd]
print(total_odds)
create_bar_chart(rolls, labels)

