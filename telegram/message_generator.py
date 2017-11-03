import sys


def prepare_message(s: str):
    res = ' '.join(s.split()[1:])
    url = ''
    if res.endswith('.md'):
        name = res.split('/')[-1]
        name = name.replace('.md', '.html')
        url = 'https://xamgore.github.io/au-conspectus/{}'.format(name)
    return res, url


def print_message(message: str, info: str, removed: bool = False):
    res, url = prepare_message(message)
    print('"{}" {}'.format(res, info))
    if url and not removed:
        print('take a look: {}'.format(url))
    print()


if __name__ == '__main__':
    ms = sys.stdin.readlines()
    for message in reversed(ms):
        if message.startswith('A'):
            print_message(message, 'added')
        elif message.startswith('M'):
            print_message(message, 'modified')
        elif message.startswith('D'):
            print_message(message, 'removed', True)
        else:
            break
