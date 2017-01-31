from os import path

current_path = path.dirname(path.abspath(path.realpath(__file__)))

pc_conf = {
    'bak_path': path.join(current_path, 'backup'),
    'conf_path': path.join(current_path, 'config'),
}
