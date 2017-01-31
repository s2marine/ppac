import os
from os import path
import shutil

from config import pc_conf
import ymlutils


def add(group, file_paths):
    assert_add(group, file_paths)
    for file_path in file_paths:
        add_file(file_path)
    add_config(group, file_paths)


def assert_add(group, file_paths):
    file_in_conf = ymlutils.get_file_by_group(group)
    for file_path in file_paths:
        assert path.exists(file_path), '文件不存在'
        assert file_path not in file_in_conf, '备份配置已存在'
        assert not path.exists(get_backup_path(file_path)), '备份文件已存在'


def add_file(file_path):
    bak_path = get_backup_path(file_path)
    mkpath(path.dirname(file_path), path.dirname(bak_path))
    move(file_path, bak_path)
    mklink(bak_path, file_path)


def add_config(group, file_paths):
    conf = ymlutils.get_config_by_group(group)
    for file_path in file_paths:
        conf['config'].append(file_path)
    ymlutils.update_config(group, conf)


def remove(group, file_paths):
    assert_remove(group, file_paths)
    for file_path in file_paths:
        remove_file(file_path)
    remove_config(group, file_paths)


def assert_remove(group, file_paths):
    file_in_conf = ymlutils.get_file_by_group(group)
    for file_path in file_paths:
        assert path.exists(file_path), '文件不存在'
        assert path.exists(get_backup_path(file_path)), '文件备份不存在'
        assert file_path in file_in_conf, '备份配置不存在'
        assert path.realpath(file_path) == get_backup_path(file_path), '该文件不是已备份文件'


def remove_file(file_path):
    bak_path = get_backup_path(file_path)
    mkpath(path.dirname(bak_path), path.dirname(file_path))
    os.remove(file_path)
    move(bak_path, file_path)


def remove_config(group, file_paths):
    conf = ymlutils.get_config_by_group(group)
    for file_path in file_paths:
        conf['config'].remove(file_path)
    ymlutils.update_config(group, conf)


def restore(group, file_paths):
    assert_restore(group, file_paths)
    for file_path in file_paths:
        restore_file(file_path)


def assert_restore(group, file_paths):
    for file_path in file_paths:
        assert not path.exists(file_path), '文件已存在'
        assert path.exists(get_backup_path(file_path)), '文件备份不存在'
        assert group is None or file_path in ymlutils.get_file_by_group(group), '备份配置不存在'


def restore_file(file_path):
    bak_path = get_backup_path(file_path)
    mkpath(path.dirname(bak_path), path.dirname(file_path))
    mklink(bak_path, file_path)


def get_backup_path(file_path):
    return join(pc_conf['bak_path'], file_path)


def get_before_path(file_path):
    return file_path[len(pc_conf['bak_path']):]


def get_conf_path(file_path):
    return join(pc_conf['conf_path'], file_path)


def get_all_file():
    configs = ymlutils.get_all_config()
    return [file_path for config in configs for file_path in config['config']]


def get_file_by_group(group):
    config = ymlutils.get_config_by_group(group)
    return [file_path for file_path in config['config']]


def is_managed(file_path):
    bak_path = get_backup_path(file_path)
    return path.islink(file_path) and path.realpath(file_path) == bak_path


def mkpath(frm, to):
    frm_paths = frm.split('/')[1:]
    to_paths = to.split('/')[1:]
    frm_len = len(frm_paths)
    to_len = len(to_paths)
    min_len = min(frm_len, to_len)
    for i in range(min_len, -1, -1):
        frm_path = path.join('/', *frm_paths[:frm_len - i])
        to_path = path.join('/', *to_paths[:to_len - i])
        assert not path.isfile(to_path)
        if not path.exists(to_path):
            os.mkdir(to_path)
            copy_stat(frm_path, to_path)


def copy_stat(frm, to):
    st = os.stat(frm)
    os.chown(to, st.st_uid, st.st_gid)
    shutil.copystat(frm, to)


def mklink(frm, to):
    os.symlink(frm, to)


def move(frm, to):
    if path.isfile(frm):
        shutil.copy(frm, to)
        copy_stat(frm, to)
        os.remove(frm)
    else:
        shutil.copytree(frm, to)
        copy_stat(frm, to)
        shutil.rmtree(frm)


def remove_empty_path(p):
    while not os.listdir(p):
        os.rmdir(p)
        p = path.dirname(p)


def join(a, b):
    b = b[1:] if b.startswith('/') else b
    return path.join(a, b)
