import sys


def prepare_string(s: str):
    res = ' '.join(s.split()[1:])
    return res


if __name__ == '__main__':
    ms = sys.stdin.readlines()
    for message in reversed(ms):
        if message.startswith('M'):
            print('"{}" modified '.format(prepare_string(message)))
        elif message.startswith('A'):
            print('"{}" added'.format(prepare_string(message)))
        elif message.startswith('D'):
            print('"{}" removed'.format(prepare_string(message)))
        else:
            break
