#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class PluginObject:

    def getHomepage(self):
        return "https://www.becmd.com"

    def isAlive(self):
        pass

    def getPhoneNumbers(self, country):
        pass

    def receiveCode(self, phoneNumber):
        assert False
        return None

    def receiveCodeByKeywords(self, phoneNumber, keywordList):
        assert False
        return None

    def receiveCodeByRegexPattern(self, phoneNumber, regexPattern):
        assert False
        return None

