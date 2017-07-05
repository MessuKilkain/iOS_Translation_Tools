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

csvFileName = u"example.csv"

print( u'Start writing csv file' )

with codecs.open( csvFileName, u"w", u"utf-8" ) as fileTo:
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

print( u'Start reading csv file' )

with codecs.open( csvFileName, u"r" ) as csvfile:
	reader = csv.DictReader(csvfile)
	csvFieldnames = reader.fieldnames
	print(csvFieldnames)
	if not u'Key' in csvFieldnames:
		raise ValueError("\'Key\' is not present as a fieldname in csv.")
	else:
		for row in reader:
			print(row)

print( u'Finnish reading csv file' )

# with codecs.open( lFilePathTo, "w", "utf-16" ) as fileTo:
# 	# fileTo.write( "\n" ) # Unnecessary
# 	for (comment, key, value) in keysInfosTo:
# 		fileTo.write( "/* " + comment + " */" + "\n" )
# 		fileTo.write( "\"" + key + "\" = \"" + value + "\";" + "\n" )
# 		fileTo.write( "\n" )
