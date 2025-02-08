import random

number_to_guess = random.randint(1,10)

attemps_left = 3

print('угадай число от 1 до 10. у тебя 3 попытки: ')

while attemps_left > 0:
    guess = int(input('твоя попытка: '))

    if guess == number_to_guess:
        print('да! ты угадал число! оно было ', number_to_guess)
        break
    elif guess < number_to_guess:
        print('больше')
    else:
        print('меньше')
    attemps_left -= 1

    print(f"у тебя осталось {attemps_left} попыток")

if attemps_left == 0:
    print(f"ты проиграл... загаданное число было: {number_to_guess} ")
