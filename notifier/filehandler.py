# pylint: disable=C0111
# pylint: disable=W1203

import logging
import os
import shutil

import yaml

LOGGER = logging.getLogger(__name__)


def to_file_path(file_name: str) -> str:
    """ :returns an existing absolute file path based on the project root directory + file_name"""
    package_directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(package_directory, '..', file_name)
    return path


def create_dir(dir_name: str) -> str:
    """
    creates a directory if it is not already exiting
    :param dir_name: directory name
    :return: the absolute path to the directory
    """
    dir_path: str = to_file_path(dir_name)
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)
        LOGGER.info(f'created {dir_name} directory')

    return dir_path


def delete_dir(dir_name: str) -> bool:
    """
    deletes a directory if it exists
    :param dir_name: directory name
    :return: whether it exists or not
    """
    dir_path: str = to_file_path(dir_name)
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        LOGGER.info(f'Removed directory "{dir_name}"')
        return True
    if not os.path.exists(dir_path):
        LOGGER.warning(f'"{dir_name}" does not exists')
    else:
        LOGGER.warning(f'"{dir_name}" is not a directory')
    return False


def check_if_file_exists(filename: str) -> bool:
    """
    checks if a file exists
    :param filename: the filename of the file to check
    :return: whether it exists
    """
    filepath: str = to_file_path(filename)
    if not os.path.exists(filepath):
        LOGGER.warning(f'{filepath} does not exist')
        return False
    if not os.path.isfile(filepath):
        LOGGER.warning(f'{filepath} is not a file')
        return False
    return True


def save_file(file_name: str, data: any) -> None:
    """
     writes a file, if a file with file_name already exists its content gets overwritten
    :param file_name: the filename to save the file. If the ending is 'yaml' it will parse the data to yaml
    :param data: the data to write into the file
    :return:
    """
    file_path: str = to_file_path(file_name)
    if not os.path.isfile(file_path):
        LOGGER.info(f'{file_path} created')
    with open(file_path, 'w') as file:
        if get_file_ending(file_path) == 'yaml':
            yaml.dump(data, file, allow_unicode=True)
        else:
            file.write(data)
    LOGGER.info(f'saved {file_name}')


def load_file(filename: str) -> any:
    """
    Loads the content of a file. If it ends with 'yaml' it will try to parse the yaml file to a python object
    :param filename: the filename to load
    :return: the contents of the file
    """
    file_path: str = to_file_path(filename)
    if not check_if_file_exists(file_path):
        return None
    with open(file_path, 'r') as stream:
        if get_file_ending(file_path) == 'yaml':
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                LOGGER.error(f'YAML parsing error: {exc}')
                return None
        else:
            return stream.read()


def get_file_ending(filepath: str) -> str:
    """
    :param filepath: the path to a file
    :return: the ending of a file
    """
    return filepath.split(".")[-1]
