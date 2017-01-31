from os import path
import glob

from ruamel import yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
import futils
from config import pc_conf
import putils


def update_config(group, config):
    content = yaml.dump(config, Dumper=yaml.RoundTripDumper, indent=4, block_seq_indent=4)
    file_path = futils.join(pc_conf['conf_path'], group + '.yml')
    with open(file_path, 'w') as conf:
        conf.write(content)


def get_config_by_group(group):
    file_path = futils.join(pc_conf['conf_path'], group + '.yml')
    if path.exists(file_path):
        config = get_config_by_path(file_path)
    else:
        config = get_default_config()
    return create_default_seq(config)


def get_all_config():
    file_paths = glob.glob(path.join(pc_conf['conf_path'], '*.yml'))
    configs = [get_config_by_path(file_path) for file_path in file_paths]
    return [create_default_seq(config) for config in configs]


def get_default_config():
    return CommentedMap()


def create_default_seq(config):
    if not config.get('config'):
        config['config'] = CommentedSeq()
    if not config.get('package'):
        config['package'] = CommentedSeq()
    if not config.get('ignore'):
        config['ignore'] = CommentedSeq()
    if not isinstance(config['config'], list):
        config['config'] = list_to_seq(config['config'])
    if not isinstance(config['package'], list):
        config['package'] = list_to_seq(config['package'])
    if not isinstance(config['ignore'], list):
        config['ignore'] = list_to_seq(config['ignore'])
    return config


def get_config_by_path(conf_path):
    with open(conf_path) as conf:
        content = conf.read()
        return yaml.load(content, Loader=yaml.SafeLoader)


def get_all_pkg():
    configs = get_all_config()
    pkgs = [pkg for config in configs for pkg in config['package']]
    pure_pkgs = putils.pkgs_to_pure_pkgs(pkgs)
    ignores = set([ignore for config in configs for ignore in config['ignore']])
    return pure_pkgs - ignores


def get_pkg_by_group(group):
    config = get_config_by_group(group)
    pkgs = [pkg for pkg in config['package']]
    pure_pkgs = putils.pkgs_to_pure_pkgs(pkgs)
    ignores = set([ignore for ignore in config['ignore']])
    return pure_pkgs - ignores


def get_all_file():
    configs = get_all_config()
    return [file_path for config in configs for file_path in config['config']]


def get_file_by_group(group):
    config = get_config_by_group(group)
    return [file_path for file_path in config['config']]


def list_to_seq(l):
    ret = CommentedSeq()
    [ret.append(e) for e in l]
    return ret
