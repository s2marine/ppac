import os
from subprocess import run, PIPE

import ymlutils
from logger import prompt


def add(group, pkgs):
    assert_add(group, pkgs)
    install_pkgs(pkgs)
    add_config(group, pkgs)


def assert_add(group, pkgs):
    pkg_in_conf = ymlutils.get_pkg_by_group(group)
    for pkg in pkgs:
        assert pkg not in pkg_in_conf, '备份配置已存在'


def add_config(group, pkgs):
    conf = ymlutils.get_config_by_group(group)
    conf['package'].extend(pkgs)
    ymlutils.update_config(group, conf)


def remove(group, pkgs):
    assert_remove(group, pkgs)
    uninstall_pkgs(pkgs)
    remove_config(group, pkgs)


def assert_remove(group, pkgs):
    pkg_in_conf = ymlutils.get_pkg_by_group(group)
    for pkg in pkgs:
        assert pkg in pkg_in_conf, '备份配置不存在'


def remove_config(group, pkgs):
    conf = ymlutils.get_config_by_group(group)
    for pkg in pkgs:
        conf['package'].remove(pkg)
    ymlutils.update_config(group, conf)


def restore(group, pkgs):
    assert_restore(group, pkgs)
    install_pkgs(pkgs)


def assert_restore(group, pkgs):
    pass


def install_pkgs(pkgs):
    os.system(' '.join(['yaourt', '-S', *pkgs]))


def uninstall_pkgs(pkgs):
    os.system(' '.join(['yaourt', '-Rs', *pkgs]))


def pkgs_to_pure_pkgs(pkgs):
    pkg_groups = get_all_group()
    pure_pkgs = []
    for pkg in pkgs:
        if pkg in pkg_groups:
            pure_pkgs.extend(get_group_s_pkg(pkg))
        else:
            pure_pkgs.append(pkg)
    return set(pure_pkgs)


def get_all_installed_pkg():
    """
    获取所有已安装的包
    """
    return run_get_set(run(['yaourt', '-Qeq'], stdout=PIPE))


def get_all_group():
    """
    获取所有组
    """
    return run_get_set(run(['yaourt', '-Sgq'], stdout=PIPE))


def get_group_s_pkg(group):
    """
    获取某组下的所有包
    """
    return run_get_set(run(['yaourt', '-Sgq', group], stdout=PIPE))


def run_get_set(process):
    l = process.stdout.decode('utf-8').split('\n')
    l.remove('')
    return set(l)
