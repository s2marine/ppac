#!/usr/bin/env python3
import sys
from os import path

import futils
import putils
import ymlutils
import logger
from result import ActionType, Result


def analyze_args(argv):
    if len(argv) <= 1:
        return 'help', None, None
    cmd = argv[1]

    group = None
    args = []
    i = 2
    while i < len(argv):
        if argv[i] == '-g':
            group = argv[i + 1]
            i += 1
        else:
            args.append(argv[i])
        i += 1
    return cmd, group, args


def show_help():
    print('ac', 'rc', 'ap', 'rp', 'csync', 'pstate')


def check_add_config(group, file_paths):
    group = group or 'tmp'
    return [Result(ActionType.ADD_CONFIG, group, path.realpath(file_path)) for file_path in file_paths]


def check_remove_config(group, file_paths):
    group = group or 'tmp'
    abs_paths = [path.abspath(file_path) for file_path in file_paths]
    return [Result(ActionType.REMOVE_CONFIG, group, abs_path) for abs_path in abs_paths]


def check_add_pkg(group, pkgs):
    group = group or 'tmp'
    return [Result(ActionType.ADD_PKG, group, pkg) for pkg in pkgs]


def check_remove_pkg(group, pkgs):
    group = group or 'tmp'
    return [Result(ActionType.REMOVE_PKG, group, pkg) for pkg in pkgs]


def check_config_sync(group):
    if group is None:
        file_paths = futils.get_all_file()
    else:
        file_paths = futils.get_file_by_group(group)

    return [Result(ActionType.RESTORE_CONFIG, group, file_path)
            for file_path in file_paths if not futils.is_managed(file_path)]


def check_pkg_state(group):
    if group is None:
        pkgs = ymlutils.get_all_pkg()
    else:
        pkgs = ymlutils.get_pkg_by_group(group)
    installed = putils.get_all_installed_pkg()
    uninstalled = pkgs - installed
    unmanaged = installed - pkgs
    print('unmanaged: %s' % unmanaged)
    return [Result(ActionType.RESTORE_PKG, group, pkg) for pkg in uninstalled]


def action_route(cmd, group, args):
    if cmd == 'help':
        return show_help()
    elif cmd == 'ac':
        return check_add_config(group, args)
    elif cmd == 'rc':
        return check_remove_config(group, args)
    elif cmd == 'ap':
        return check_add_pkg(group, args)
    elif cmd == 'rp':
        return check_remove_pkg(group, args)
    elif cmd == 'csync':
        return check_config_sync(group)
    elif cmd == 'pstate':
        return check_pkg_state(group)
    else:
        return []


def do_add_config(results):
    if not logger.prompt('是否添加配置', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        futils.add(group, args)


def do_remove_config(results):
    if not logger.prompt('是否移除配置', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        futils.remove(group, args)


def do_add_pkg(results):
    if not logger.prompt('是否添加包', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        putils.add(group, args)


def do_remove_pkg(results):
    if not logger.prompt('是否移除包', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        putils.remove(group, args)


def do_restore_config(results):
    if not logger.prompt('是否恢复配置', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        futils.restore(group, args)


def do_restore_pkg(results):
    if not logger.prompt('是否安装缺失包', results):
        return
    groups = list_group_by(results)
    for group, args in groups.items():
        putils.restore(group, args)


def route_result(results):
    add_config_results = [result for result in results if result.action_type == ActionType.ADD_CONFIG]
    remove_config_results = [result for result in results if result.action_type == ActionType.REMOVE_CONFIG]
    restore_config_results = [result for result in results if result.action_type == ActionType.RESTORE_CONFIG]
    add_pkg_results = [result for result in results if result.action_type == ActionType.ADD_PKG]
    remove_pkg_results = [result for result in results if result.action_type == ActionType.REMOVE_PKG]
    restore_pkg_results = [result for result in results if result.action_type == ActionType.RESTORE_PKG]

    add_config_results and do_add_config(add_config_results)
    remove_config_results and do_remove_config(remove_config_results)
    restore_config_results and do_restore_config(restore_config_results)

    add_pkg_results and do_add_pkg(add_pkg_results)
    remove_pkg_results and do_remove_pkg(remove_pkg_results)
    restore_pkg_results and do_restore_pkg(restore_pkg_results)


def list_group_by(results):
    ret = {}
    for result in results:
        if result.group not in ret:
            ret[result.group] = []
        ret[result.group].append(result.arg)
    return ret


def main():
    cmd, group, arg = analyze_args(sys.argv)
    results = action_route(cmd, group, arg)
    results and route_result(results)


if __name__ == '__main__':
    main()
