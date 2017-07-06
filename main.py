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

fieldnames = ['Value',AppleLocalizedStringsFileParser.FIELDNAME_COMMENT]
values = {'Value':keysValues,AppleLocalizedStringsFileParser.FIELDNAME_COMMENT:keysComments}
keys = keysValues.keys()

csvFileName = u"example.csv"

print( u'Start writing csv file' )

# with codecs.open( csvFileName, u"w", u"utf-8" ) as fileTo:
# 	csvFieldnames = list(fieldnames)
# 	csvFieldnames.insert(0,AppleLocalizedStringsFileParser.FIELDNAME_KEY)
# 	writer = csv.DictWriter(fileTo, fieldnames=csvFieldnames)
# 	writer.writeheader()
# 	for key in keys:
# 		rowToWrite = {AppleLocalizedStringsFileParser.FIELDNAME_KEY:key}
# 		for fieldname in fieldnames:
# 			if key in values[fieldname]:
# 				rowToWrite[fieldname] = values[fieldname][key]
# 		writer.writerow(rowToWrite)
AppleLocalizedStringsFileParser.exportLocalizationToCsvFile( csvFileName, keys, values)

print( u'Finnish writing csv file' )

print( u'Start reading csv file' )

extractedValues = dict()
extractedKeys = list()

with codecs.open( csvFileName, u"r" ) as csvfile:
	reader = csv.DictReader(csvfile)
	csvFieldnames = list(reader.fieldnames)
	print(csvFieldnames)
	if not AppleLocalizedStringsFileParser.FIELDNAME_KEY in csvFieldnames:
		raise ValueError(AppleLocalizedStringsFileParser.FIELDNAME_KEY + u" is not present as a fieldname in csv.")
	else:
		csvFieldnames.remove(AppleLocalizedStringsFileParser.FIELDNAME_KEY)
		for fieldname in fieldnames:
			extractedValues[fieldname] = dict()
		for row in reader:
			# print(row)
			key = row[AppleLocalizedStringsFileParser.FIELDNAME_KEY]
			extractedKeys.append(key)
			for fieldname in fieldnames:
				extractedValues[fieldname][key] = row[fieldname]

print( u'Finnish reading csv file' )

extractedKeys = sorted( extractedKeys )

language = u'Value'

print( u'Start writing new strings file' )

with codecs.open( u"example_output.strings", "w", "utf-16-le" ) as fileTo:
	for key in extractedKeys:
		comment = extractedValues[AppleLocalizedStringsFileParser.FIELDNAME_COMMENT][key]
		value = extractedValues[language][key]
		fileTo.write( "/* " + comment + " */" + "\n" )
		fileTo.write( "\"" + key + "\" = \"" + value + "\";" + "\n" )
		fileTo.write( "\n" )

print( u'Finnish writing new strings file' )
