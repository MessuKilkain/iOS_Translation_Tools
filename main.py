#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from future.utils import iteritems

import csv
import codecs

import AppleLocalizedStringsFileParser

(keysValues, keysComments) = AppleLocalizedStringsFileParser.parseAppleLocalizedStringsFile(u'example.strings')

print(u"Values")
for (key, value) in iteritems(keysValues):
	print( '- ', key )
	print( '\t- ', value )
print(u"Comments")
for (key, comment) in iteritems(keysComments):
	print( '- ', key )
	print( '\t- ', comment )

fieldnames = ['Value','Comment']
values = {'Value':keysValues,'Comment':keysComments}
keys = keysValues.keys()
print( u'Start writing csv file' )

# with codecs.open( u'example.csv', u"w", u"utf-8" ) as fileTo:
# 	fileTo.write( u"Keys;Comments;Values\n" )
# 	for key in keys:
# 		fileTo.write( u'"' + key + u'";"' + keysComments[key] + u'";"' + keysValues[key] + u'"\n' )

with codecs.open( u'example.csv', u"w", u"utf-8" ) as fileTo:
	csvFieldnames = list(fieldnames)
	csvFieldnames.insert(0,'Key')
	writer = csv.DictWriter(fileTo, fieldnames=csvFieldnames)
	writer.writeheader()
	for key in keys:
		rowToWrite = {'Key':key}
		for fieldname in fieldnames:
			rowToWrite[fieldname] = values[fieldname][key]
		writer.writerow(rowToWrite)

print( u'Finnish sriting csv file' )
