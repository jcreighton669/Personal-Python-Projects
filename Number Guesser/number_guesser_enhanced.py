import random
import sys

print("""Let's play a guessing game.
Make a selection of the difficulty
Enter 'e' for easy, 5 attempts range 1 - 20.
Enter 'm' for medium, 10 attempts range 1 - 100.
Enter 'h' for hard, 5 attempts range 1 - 100.
""")
attempts = 0
upper_limit = 0
number = 0
difficulty = input()
if difficulty.lower().startswith('e'):
    attempts = 5
    upper_limit = 20
    number = random.randint(1, upper_limit)
elif difficulty.lower().startswith('m'):
    attempts = 10
    upper_limit = 100
    number = random.randint(1, upper_limit)
elif difficulty.lower().startswith('h'):
    attempts = 5
    upper_limit = 100
    number = random.randint(1, upper_limit)

print("""
Guess a number between 1 and {}.
You have {} chances to guess the number.
You will be instructed if your guess is too high or too low. 
Only valid guesses will be counted""".format(upper_limit, attempts))

guess_count = 1

while guess_count <= attempts:
    guess = input()
    if guess.isdigit():
        guess = int(guess)
        if 1 <= guess <= upper_limit:
            if guess == number:
                print("That is correct!\n")
                break
            elif guess < number:
                guess_count += 1
                print('Your guess was too LOW. Please try again!')
            elif guess > number:
                guess_count += 1
                print("Your guess was too HIGH. Please try again")
        else:
            print("Invalid input. Please try again!")
    else:
        print("Invalid input. Please try again!")

print()
if guess_count == 1:
    print("Congratulations it only took {} guess".format(guess_count), file=sys.stderr)
elif guess_count <= upper_limit:
    print("Congratulations it only took {} guesses".format(guess_count), file=sys.stderr)
else:
    print("The correct number was {}".format(number), file=sys.stderr)

input('Press Enter to exit')
