import sys


def parse(s: str):
    path = ' '.join(s.split()[1:])
    name = path.split('/')[-1][:-3]
    url = 'https://xamgore.github.io/au-conspectus/{}'.format(name + '.html')
    return name, url


if __name__ == '__main__':
    lines = [l.strip() for l in sys.stdin.readlines()]
    lectures = [l for l in reversed(lines) if l[:1] == 'A' and l[-3:] == '.md']

    if len(lectures) == 1:
        _, url = parse(lectures[0])
        print(':boom: Новая лекция! [глянуть]({})'.format(url))
    if len(lectures) > 1:
        print(':boom: Пачка новых лекций!')
        print(*(' · [%s](%s)' % parse(l) for l in lectures), sep='\n')
