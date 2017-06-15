import ntpath
import pickle


def deserialize(serialized):
    msg = None
    try:
        msg = pickle.loads(serialized)
    except EOFError:
        print('error')
    return msg


def serialize(msg):
    if msg is None:
        return None
    else:
        return pickle.dumps(msg)


def split_path(user_home, path):
    ntpath.basename("a/b/c")
    server_path = user_home + path
    folder, file = ntpath.split(server_path)
    return folder, file

