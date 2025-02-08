walk = "n,s,n,s,n,s,n,s,n,s"

def is_valid_walk(walk):
    # Разделяем строку на список направлений
    gps = walk.split(",")

    # Проверяем, что длина пути равна 10
    if len(gps) != 10:
        print('nonono')
        return

    # Подсчитываем шаги в каждом направлении
    north = gps.count('n')
    south = gps.count('s')
    east = gps.count('e')
    west = gps.count('w')

    # Проверяем, возвращает ли путь в исходную точку
    if north == south and east == west:
        print("da right")
    else:
        print("no no no")

# Вызов функции
is_valid_walk(walk)
