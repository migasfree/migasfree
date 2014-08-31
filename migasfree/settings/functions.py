import os
import random
import string


def secret_key(path):
    if not os.path.exists(path):
        os.makedirs(path)
    _file = os.path.join(path, 'secret_key.txt')
    if os.path.exists(_file):
        _key = open(_file).read().strip()
    else:
        _key = ''.join([random.SystemRandom().choice("%s%s%s" % (string.ascii_letters, string.digits, string.punctuation)) for i in range(50)])
        with file(_file, 'w') as outfile:
            outfile.write(_key)
    return _key
