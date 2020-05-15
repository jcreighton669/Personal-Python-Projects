import random
import sys

number = random.randint(1, 100)
guess_count = 1
print("""Let's play a guessing game. 
Guess a number between 1 and 100.
You have 10 chances to guess the number.
You will be instructed if your guess is too high or too low. 
Only valid guesses will be counted""")
while guess_count <= 10:
    guess = input()
    if guess.isdigit():
        guess = int(guess)
        if 1 <= guess <= 100:
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
elif guess_count <= 10:
    print("Congratulations it only took {} guesses".format(guess_count), file=sys.stderr)
else:
    print("The correct number was {}".format(number), file=sys.stderr)

print()
input('Press Enter to exit')
