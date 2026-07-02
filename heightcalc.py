import random
import math
import threading

def generate_random_heights(n: int, m: int):
    arr = [[] for i in range(n)]
    def fill_row(x):
        arr[x] = [random.randint(1, 100) for j in range(m)]
    t_poll = []
    for i in range(n):
        t_poll.append(threading.Thread(target=fill_row, args=(i,)))
        t_poll[i].start()
    for i in range(n):
        t_poll[i].join()
    return arr

def generate_random_heights_single(n: int, m: int):
    arr = [[random.randint(1, 100) for j in range(m)] for i in range(n)]
    return arr

def process_ray(n, m, x_, y_, alpha, a, a_):
    r = 1
    check_list = []
    while True:
        x = x_ + int(r * math.cos(alpha))
        y = y_ + int(r * math.sin(alpha))
        if x >= n or y >= m or x < 0 or y < 0:
            break
        check_list.append((x, y))
        a[x][y] = 1
        r += 1
    h2 = a_[x_][y_]['height']

    for i in range(2, len(check_list)):
        x, y = check_list[i]
        h0 = a_[x][y]['height']
        r02 = math.dist((x, y), (x_, y_))
        for j in range(0, i):
            x__, y__ = check_list[j]
            h1 = a_[x__][y__]['height']
            r01 = math.dist((x, y), (x__, y__))
            deg1 = math.degrees(math.atan2(h1-h0, r01))
            deg2 = math.degrees(math.atan2(h2-h0, r02))
            if deg1 > deg2:
                a[x][y] = 0
                break

def process_matrix(n: int, m:int, start_x: int, start_y:int, a:list[list], scale=360) -> list[list[int]]:
    results = [[] for i in range(n)]
    def fill_row(x):
        results[x] = [random.randint(1, 100) for j in range(m)]
    t_poll = []
    for i in range(n):
        t_poll.append(threading.Thread(target=fill_row, args=(i,)))
        t_poll[i].start()
    for i in range(n):
        t_poll[i].join()
    t_poll = []
    for alpha in range(scale):
        t_poll.append(threading.Thread(target=process_ray, args=(n, m, start_x, start_y, 2*math.pi*alpha/scale, results, a,)))
        # process_ray(n, m, start_x, start_y, 2*math.pi*alpha/scale, results, a)
        t_poll[alpha].start()
    for i in range(scale):
        t_poll[i].join()
    return results

def process_matrix_single(n: int, m:int, start_x: int, start_y:int, a:list[list], scale=360) -> list[list[int]]:
    results = [[0 for j in range(m)] for i in range(n)]
    t_poll = []
    for alpha in range(scale):
        # t_poll.append(threading.Thread(target=process_ray, args=(n, m, start_x, start_y, 2*math.pi*alpha/scale, results, a,)))
        process_ray(n, m, start_x, start_y, 2*math.pi*alpha/scale, results, a)
        # t_poll[alpha].start()
    # for i in range(scale):
        # t_poll[i].join()
    return results