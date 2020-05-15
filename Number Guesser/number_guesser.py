import random
import sys

number = random.randint(1, 100)
guess_count = 1
print("""Let's play a guessing game. 
Guess a number between 1 and 100 (inclusively).
You have 10 chances to guess the number and 
you will be instructed if your guess is too high or too low. """)
while guess_count <= 10:
    guess = input()
    if guess.isdigit():
        guess = int(guess)
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
if guess_count == 1:
    print("Congratulations it only took {} guess\n".format(guess_count), file=sys.stderr)
elif guess_count <= 10:
    print("Congratulations it only took {} guesses\n".format(guess_count), file=sys.stderr)
else:
    print("The correct number was {}".format(number), file=sys.stderr)

input('Press Enter to exit')
