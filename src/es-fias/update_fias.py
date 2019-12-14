#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import fias_data
from fias_data import Address
from fias_info import getUpdateVersion
from address_upd import addressUpdate
from house_upd import housesUpdate
from update_info import findInfoDoc
from init_db import createConnection, IS_DEBUG
from fias_download import downloadUpdate, clearWorkDir
from index_address import index
from snapshot import createSnapshot, createFullSnapshot
from fias_data import ES


def update(isDebug=False):
    print()
    print('обновление...')
    print()

    address = fias_data.Address()
    address.createPreprocessor(ES)
    # 1. версия
    getUpdateVersion()

    print('версия:')
    print(fias_data.VERSION_REPORT_DATE)
    print()

    infoDoc = findInfoDoc()

    now = datetime.datetime.now()
    infoDoc.update(update_date=now)
    
    # 2. загрузка
    downloadUpdate()

    print()
    print('дома...')
    print()
    houses = fias_data.Houses()
    houses.createPreprocessor(ES)
    HOUSE_CNT = housesUpdate(isDebug=True,houses=houses)
    infoDoc.update(rec_upd_houses=HOUSE_CNT)

    print()
    print('адреса...')
    print()
    ADDR_CNT = addressUpdate(isDebug=True,address=address)
    infoDoc.update(rec_upd_address=ADDR_CNT)

    print()
    print('индексация...')
    print()

    index(isUpdate=True)


    # снэпшот
    createFullSnapshot(repository=fias_data.REPOSITORY)

    #  очистка
    clearWorkDir()

    print("завершено")


update(isDebug=True)
# index(isUpdate=False)
# createFullSnapshot(repository=fias_data.REPOSITORY)