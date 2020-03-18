#!/usr/bin/env python3
from os import mkdir
from os.path import exists

from numpy import array, empty, vstack
from requests import get

from nujo.utils.data.nujo_dir import HOME_DIR


class DatasetLoader:
    '''

    Parameters:
    -----------
    name : will be downloaded from the UCI ML repo
    override : if this file exists, does it get downloaded again
    '''
    _UCI_REPO_URL = '''
    https://archive.ics.uci.edu/ml/machine-learning-databases/{}/{}
    '''

    def __init__(self, name, override=False):
        self.name = name  # with .data
        self._file = HOME_DIR + self.name
        if exists(HOME_DIR + name) and not override:
            return
        self._link = self._UCI_REPO_URL.format(
            self.name.split('.')[0], self.name).strip()
        self.download()

    def install(self, dataset):
        with open(self._file, 'r+') as data:
            lines = data.readlines()

        dataset.X = empty((0, len(lines[0].split(','))))
        # number of columns
        for line in lines[:-1]:  # last row is \n
            x = array(line.strip().split(','))
            dataset.X = vstack((dataset.X, x))

    def download(self) -> None:
        r = get(self._link)
        if not exists(HOME_DIR):
            mkdir(HOME_DIR)
            print('Directory "~/.nujo" created')
        else:
            print('Directory "~/.nujo" already exists')
        print(f'File {self.name} has been created.')
        with open(self._file, 'wb') as f:
            f.write(r.content)
