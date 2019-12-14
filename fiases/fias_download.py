import re
import os
from urllib import request
from tqdm import trange, tqdm
from rarfile import RarFile
from hurry.filesize import size, si
from fiases.init_db import IS_DEBUG
import fiases.fias_data


class TqdmUpTo(tqdm):
    """ Прогресс загрузки в консоли """

    def update_full(self, b=6_500_000, bsize=1, tsize=6_500_000):
        if tsize is not None:
            self.total = tsize
            # will also set self.n = b * bsize
            self.update(b * bsize - self.n)

    def update_delta(self, b=100_000, bsize=1, tsize=100_000):
        if tsize is not None:
            self.total = tsize
            # will also set self.n = b * bsize
            self.update(b * bsize - self.n)


def downloadUpdate():
    """ Загрузка обновления ФИАС """
    # if IS_DEBUG:
        # print('Начинаем загрузку ...')
        # print(fias_data.URL_DELTA)
    file_name = fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_DELTA_XML_RAR

    with TqdmUpTo(unit='B',
                  unit_scale=True,
                  miniters=1,
                  desc=fiases.fias_data.URL_DELTA.split('/')[-1]) as t:  # all optional kwargs
        request.urlretrieve(fiases.fias_data.URL_DELTA,
                            filename=file_name,
                            reporthook=t.update_delta,
                            data=None)
    # if IS_DEBUG:
        # print('Загрузка завершена.')


def downloadFull():
    """ Загрузка полной базы ФИАС """
    # if IS_DEBUG:
        # print('Начинаем загрузку ...')
        # print(fias_data.URL_FULL)
    file_name = fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_XML_RAR

    with TqdmUpTo(unit='B',
                  unit_scale=True,
                  miniters=1,
                  desc=fiases.fias_data.URL_FULL.split('/')[-1]) as t:  # all optional kwargs
        request.urlretrieve(fiases.fias_data.URL_FULL,
                            filename=file_name,
                            reporthook=t.update_full,
                            data=None)
    if IS_DEBUG:
        print('Загрузка завершена.')


def uprarUpdateAdddr(address):
    """Распаковка обновления """
    rf = RarFile(fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_DELTA_XML_RAR)

    addressMatcher = re.compile(fiases.fias_data.AS_ADDR_FILE)
    # if IS_DEBUG:
        # print('unrar address...')
    for f in rf.infolist():
        if addressMatcher.match(f.filename):
            # if IS_DEBUG:
                # print('FOUND: ' + f.filename)
            address.addressDeltaFile = f.filename
            address.addressDeltaSize = f.file_size
            # if IS_DEBUG:
                # print(
                    # 'size: ' + str(size(address.addressDeltaSize, system=si)))

    if (address.addressDeltaSize > 0):
        if IS_DEBUG:
            print('extracting: ' + address.addressDeltaFile)

        rf.extract(address.addressDeltaFile, fiases.fias_data.WORK_DIR)
        if IS_DEBUG:
            print('finished')
    else:
        if IS_DEBUG:
            print('files NOT FOUND!')


def uprarUpdateHouses(houses):
    """Распаковка обновления """
    rf = RarFile(fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_DELTA_XML_RAR)

    housesMatcher = re.compile(fiases.fias_data.AS_HOUSES_FILE)
    if IS_DEBUG:
        print('unrar houses...')
    for f in rf.infolist():
        if housesMatcher.match(f.filename):
            if IS_DEBUG:
                print('FOUND: ' + f.filename)
            houses.housesDeltaFile = f.filename
            houses.housesDeltaSize = f.file_size
            if IS_DEBUG:
                print(
                    'size: ' + str(size(houses.housesDeltaSize, system=si)))

    if (houses.housesDeltaSize > 0):
        if IS_DEBUG:
            print('2.extracting: ' + houses.housesDeltaFile)

        rf.extract(houses.housesDeltaFile, fiases.fias_data.WORK_DIR)
        if IS_DEBUG:
            print('finished')
    else:
        if IS_DEBUG:
            print('files NOT FOUND!')


def uprarDelFullAdddr(address):
    """3.Распаковываем архив с удаленными записями"""
    rf = RarFile(fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_XML_RAR)
    # rf = RarFile(fle)

    addressMatcher = re.compile(fiases.fias_data.AS_ADDR_FILE)
    addressDelMatcher = re.compile(fiases.fias_data.AS_DEL_ADDR_FILE)
    if IS_DEBUG:
        print('unrar address...')
    for f in rf.infolist():
        if addressDelMatcher.match(f.filename):
            if IS_DEBUG:
                print('FOUND: ' + f.filename)
            address.addressDELFullXMLFile = f.filename
            address.addressDELFullXmlSize = f.file_size
            if IS_DEBUG:
                print(
                    'size: ' + str(size(address.addressFullXmlSize, system=si)))

    if (address.addressDELFullXmlSize > 0):
        if IS_DEBUG:
            print('2.extracting: ' + address.addressDELFullXMLFile)

        rf.extract(address.addressDELFullXMLFile, fiases.fias_data.WORK_DIR)
        if IS_DEBUG:
            print('finished')
    else:
        if IS_DEBUG:
            print('files NOT FOUND!')


def unRarFullAdddr(address):
    """Распаковка адресов из полной базы ФИАС"""
    rf = RarFile(fiases.fias_data.WORK_DIR + fiases.fias_data.FIAS_XML_RAR)

    addressMatcher = re.compile(fiases.fias_data.AS_ADDR_FILE)
    print('')
    for f in rf.infolist():
        if addressMatcher.match(f.filename):
            if IS_DEBUG:
                print('Найден: ' + f.filename)
            address.addressFullXmlFile = f.filename
            address.addressFullXmlSize = f.file_size
            if IS_DEBUG:
                print(
                    'Размер: ' + str(size(f.file_size, system=si)))
    if (address.addressFullXmlSize > 0):
        if IS_DEBUG:
            print('Распаковка: ',  address.addressFullXmlFile)

        rf.extract(address.addressFullXmlFile, fiases.fias_data.WORK_DIR)

        if IS_DEBUG:
            print('Ok')
    else:
        if IS_DEBUG:
            print('Файлы не найдены')


def clearWorkDir():
    """Очистка рабочей директории от ранее загруженных файлов"""
    for the_file in os.listdir(fiases.fias_data.WORK_DIR):
        file_path = os.path.join(fiases.fias_data.WORK_DIR, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            if IS_DEBUG:
                print(e)
