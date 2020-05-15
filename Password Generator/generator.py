import random
import webbrowser
import pyperclip


lowercase = 'abcdefghijklmnopqrstuvwxyz'
uppercase = lowercase.upper()
digits = '0123456789'
spec_characters = '!@#$%^&*'


def gen_password(length):
    character_options = lowercase + uppercase + digits + spec_characters
    password = ''
    for i in range(length):
        password += random.choice(character_options)

    print(password)
    return password


def check_strength():
    webbrowser.open('https://howsecureismypassword.net/', new=2)
    copy_paste()


def copy_paste():
    pyperclip.copy(password)


if __name__ == '__main__':
    n = input('Enter the length of the password you want: ')
    if n.isdigit():
        password = gen_password(int(n))
        print('Would you like to check the passwords strength? (yes or no) ')
        test_strength = input()
        if test_strength == 'yes':
            print('Password added to clipboard, just use system command to paste into web page!')
            check_strength()
        x = input("Press any key to exit")
    else:
        print("Invalid Input")
