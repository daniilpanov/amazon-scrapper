data = []


def ttt(n: int):
    yield from data[:n]
    for i in range(len(data), n):
        data.append(i)
        print(f'append for [{n}]: {i}')
        yield i


print(list(ttt(10)))
print(list(ttt(20)))
print(list(ttt(10)))
