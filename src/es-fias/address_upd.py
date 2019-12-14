#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tqdm import trange, tqdm
from xml.dom import pulldom
from lxml import etree
from xml.dom.pulldom import parse
from elasticsearch.helpers import parallel_bulk
from elasticsearch_dsl import Search

# Local modules:
import fias_data
from fias_download import downloadUpdate, uprarUpdateAdddr, clearWorkDir
from fias_info import getUpdateVersion
from snapshot import createSnapshot
from update_info import findInfoDoc
from fias_data import ES


def addressUpdate(isDebug, address):

    IS_DEBUG = isDebug

    # 3. распаковка
    uprarUpdateAdddr(address)

    # 4. обновление
    rootDeltaXML = etree.parse(fias_data.WORK_DIR
                               + address.addressDeltaFile).getroot()
    address.addressDeltaRecSize = len(rootDeltaXML.getchildren())

    doc = parse(fias_data.WORK_DIR + address.addressDeltaFile)

    def updateIndex():
        """Обновление индекса"""
        for event, node in doc:
            if event == pulldom.START_ELEMENT and node.tagName == fias_data.ADDR_OBJECT_TAG:
                yield {
                    "_index": fias_data.ADDRESS_INDEX,
                    "_type": "_doc",
                    "_op_type": fias_data.INDEX_OPER,
                    'pipeline': fias_data.ADDR_PIPELINE_ID,
                    "_id": node.getAttribute("AOID"),
                    "ao_guid": node.getAttribute("AOGUID"),
                    "parent_guid": node.getAttribute("PARENTGUID"),
                    "formal_name": node.getAttribute("FORMALNAME"),
                    "off_name": node.getAttribute("OFFNAME"),
                    "short_name": node.getAttribute("SHORTNAME"),
                    "ao_level": node.getAttribute("AOLEVEL"),
                    "area_code": node.getAttribute("AREACODE"),
                    "city_code": node.getAttribute("CITYCODE"),
                    "place_code": node.getAttribute("PLACECODE"),
                    "auto_code": node.getAttribute("AUTOCODE"),
                    "plan_code": node.getAttribute("PLANCODE"),
                    "street_code": node.getAttribute("STREETCODE"),
                    "city_ar_code": node.getAttribute("CTARCODE"),
                    "extr_code": node.getAttribute("EXTRCODE"),
                    "sub_ext_code": node.getAttribute("SEXTCODE"),
                    "code": node.getAttribute("CODE"),
                    "region_code": node.getAttribute("REGIONCODE"),
                    "plain_code": node.getAttribute("PLAINCODE"),
                    "postal_code": node.getAttribute("POSTALCODE"),
                    "okato": node.getAttribute("OKATO"),
                    "oktmo": node.getAttribute("OKTMO"),
                    "ifns_fl": node.getAttribute("IFNSFL"),
                    "ifns_ul": node.getAttribute("IFNSUL"),
                    "terr_ifns_fl": node.getAttribute("TERRIFNSFL"),
                    "terr_ifns_ul": node.getAttribute("TERRIFNSUL"),
                    "norm_doc": node.getAttribute("NORMDOC"),
                    "act_status": node.getAttribute("ACTSTATUS"),
                    "live_status": node.getAttribute("LIVESTATUS"),
                    "curr_status": node.getAttribute("CURRSTATUS"),
                    "oper_status": node.getAttribute("OPERSTATUS"),
                    "start_date": node.getAttribute("STARTDATE"),
                    "end_date": node.getAttribute("ENDDATE"),
                    "bazis_create_date": fias_data.CREATE_DATE_ZERO,
                    "bazis_update_date": fias_data.VERSION_DATE,
                    "update_date": node.getAttribute("UPDATEDATE"),
                    "bazis_finish_date": node.getAttribute("ENDDATE")
                }

    ADDR_CNT = 0
    if IS_DEBUG:
        for ok, info in tqdm(parallel_bulk(ES, updateIndex(),
                                           raise_on_error=False,
                                           raise_on_exception=False),
                             unit=' адрес',
                             desc='обновлено',
                             total=address.addressDeltaRecSize):
            ADDR_CNT = ADDR_CNT + 1
            if (not ok):
                if IS_DEBUG:
                    print(ok, info)

    else:
        for ok, info in parallel_bulk(ES, updateIndex(),
                                      raise_on_error=False,
                                      raise_on_exception=False):
            ADDR_CNT = ADDR_CNT + 1
            if (not ok):
                print(ok, info)

    # return address.addressDeltaRecSize
    return ADDR_CNT


# addressUpdate(isDebug=True)