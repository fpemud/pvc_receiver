#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import re
import time
import fcntl
import errno
import shutil


class PgsFormatError(Exception):
    pass


class VerificationCodeReceiver:

    DEFAULT_TIMEOUT = 5 * 60            # 5 minutes

    SECURE_LEVEL_PUBLIC = 1             # the verification is not important, can be seen by the world
    SECURE_LEVEL_PRIVATE = 2            # the verification should not be see by others
    SECURE_LEVEL_SECERET = 3            # we only beleive our self

    VC_TYPE_SMS = 1
    VC_TYPE_VOICE = 2

    def __init__(self, country, secureLevel, vcType, timeout=None, dirPrefix="/"):
        assert country is not None   # FIXME
        assert secureLevel in [self.SECURE_LEVEL_PUBLIC, self.SECURE_LEVEL_PRIVATE, self.SECURE_LEVEL_SECERET]
        assert vcType in [self.VC_TYPE_SMS, self.VC_TYPE_VOICE]
        assert isinstance(private, bool)

        # we don't support voice verification code yet
        assert vcType == self.VC_TYPE_SMS

        self.country = country
        self.private = private
        self.secureLevel = secureLevel
        self.vcType = vcType
        self.timeout = self.DEFAULT_TIMEOUT if timeout is None else timeout
        self.dirPrefix = dirPrefix

    def refresh(self):
        pass

    def getPhoneNumber(self):
        assert False
        return None

    def receiveCode(self):
        assert False
        return None

    def receiveCodeByKeywords(self, keywordList):
        assert False
        return None

    def receiveCodeByRegexPattern(self, regexPattern):
        assert False
        return None

    def 






































from collections import OrderedDict
from urllib.parse import urlparse

from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from hello_spidery.utils.commons import seconds_2_str
from hello_spidery.utils.spiders.crawl_spider import HelloCrawlSpider
from hello_spidery.utils.selector_utils import xpath_extract_all_text_strip, \
    xpath_extract_all_text_no_spaces as xpath_text_no_spaces


class MobilePhoneSpider(HelloCrawlSpider):
    name = 'mobile_phone'

    custom_settings = {
        'USE_DEFAULT_ERROR_BACK': True,
        'DOWNLOAD_DELAY': 1,

        # DATABASE
        'SQLITE_DATABASE': '',
        'CREATE_TABLE_SQL_4_SQLITE': """CREATE TABLE IF NOT EXISTS spider_data
                                        (`mobile_phone_number`  char(11) NOT NULL primary key,
                                         `url`                  varchar(100) NOT NULL,
                                         `crawl_time`           varchar(19) NOT NULL,
                                         `timestamp`            integer   NOT NULL);""",
        'INSERT_SQL_4_SQLITE': """INSERT OR REPLACE INTO spider_data VALUES (?,?,?,?);"""
    }

    start_urls = [
        # 'https://www.pdflibr.com/?page=1',
        # 'https://yunduanxin.net/China-Phone-Number/',
        # 'http://www.smszk.com/',
        # 'http://www.z-sms.com/',
        'https://www.becmd.com/',
        # 'https://www.receivingsms.com/'
    ]

    url_and_phone_number_mapping = {}

    phone_num_match = re.compile(r'\d{11,}')

    list_page_xpaths = {
        'www.pdflibr.com': {
            'phone_number': '//div[contains(@class, "number-list-flag")]//h3',
            'a_tag': '//div[contains(@class, "sms-number-read")]//a/@href'
        },
        'yunduanxin.net': {
            'phone_number_and_url': '//a[text()="接收短信"]/@href'
        },
        'www.smszk.com': {
            'phone_number_and_url': '//a[text()="查看短信"]/@href'
        },
        'www.receivingsms.com': {
            'phone_number_and_url': '//a[text()="接收短信"]/@href'
        },
        'www.becmd.com': {
            'phone_number_and_url': '//a[text()="阅读短信"]/@href'
        }
    }

    database_column_list = ['mobile_phone_number', 'url', 'crawl_time', 'timestamp']

    rules = (
        Rule(LinkExtractor(allow=r'www\.pdflibr\.com/\?page=\d+', allow_domains='www.pdflibr.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'yunduanxin\.net/China-Phone-Number/?', allow_domains='yunduanxin.net'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.smszk\.com/?$', allow_domains='www.smszk.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.receivingsms\.com/?$', allow_domains='www.receivingsms.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.becmd\.com/?$', allow_domains='www.becmd.com'),
             callback='parse_list', follow=True),
    )

    def get_ph_num(self, ph_num_text):
        _ph_num = self.phone_num_match.search(ph_num_text)
        if not _ph_num:
            return
        _ph_num = _ph_num.group()[-11:]
        return _ph_num

    def parse_list(self, response):
        host_name = urlparse(response.url).hostname
        xpaths_dict = self.list_page_xpaths.get(host_name, {})
        if not xpaths_dict:
            return

        if 'phone_number_and_url' in xpaths_dict:
            href_list = [mbr for mbr in response.xpath(xpaths_dict['phone_number_and_url']).extract()]
            phone_number_list = href_list[:]
        else:
            phone_number_selectors = response.xpath(xpaths_dict['phone_number'])
            phone_number_list = [xpath_text_no_spaces(mbr) for mbr in phone_number_selectors]
            href_list = [mbr for mbr in response.xpath(xpaths_dict['a_tag']).extract()]

        for ph_num, href in zip(phone_number_list, href_list):
            _ph_num = self.get_ph_num(ph_num)
            if not _ph_num:
                continue
            if int(_ph_num[:2]) < 13 or int(_ph_num[:2]) >= 20:
                continue
            url = response.urljoin(href)
            if url not in self.url_and_phone_number_mapping:
                self.url_and_phone_number_mapping[url] = _ph_num
                item = self.assemble_parsed_item(response)
                a_dict = {
                    'mobile_phone_number': _ph_num,
                    'url': url,
                    'crawl_time': seconds_2_str(),
                    'timestamp': int(time.time()),
                }
                item['_parsed_data'] = self.assemble_result(a_dict)
                yield item

    def assemble_result(self, a_dict):
        result_dict = OrderedDict()
        for col in self.database_column_list:
            result_dict[col] = a_dict[col]
        return result_dict





