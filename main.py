#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.utils import iteritems

import AppleLocalizedStringsFileParser

language = u'Value'

(keysValues, keysComments) = AppleLocalizedStringsFileParser.parseAppleLocalizedStringsFile(u'example.strings')

print(u"Values")
for (key, value) in iteritems(keysValues):
	print( '- ', key )
	print( '\t- ', value )
print(u"Comments")
for (key, comment) in iteritems(keysComments):
	print( '- ', key )
	print( '\t- ', comment )

fieldnames = [language,AppleLocalizedStringsFileParser.FIELDNAME_COMMENT]
values = {language:keysValues,AppleLocalizedStringsFileParser.FIELDNAME_COMMENT:keysComments}
keys = list(keysValues)

csvFileName = u"example.csv"

print( u'Start writing csv file' )

AppleLocalizedStringsFileParser.exportLocalizationToCsvFile( csvFileName, keys, values)

print( u'Finnish writing csv file' )

print( u'Start reading csv file' )

(extractedKeys, extractedValues) = AppleLocalizedStringsFileParser.importLocalizationFromCsvFile(csvFileName)

print( u'Finnish reading csv file' )

extractedKeys = sorted( extractedKeys )

print( u'Start writing new strings file' )

AppleLocalizedStringsFileParser.writeAppleLocalizedStringsFile(u"example_output.strings",keys=extractedKeys,comments=extractedValues[AppleLocalizedStringsFileParser.FIELDNAME_COMMENT],localizedTexts=extractedValues[language])

print( u'Finnish writing new strings file' )
