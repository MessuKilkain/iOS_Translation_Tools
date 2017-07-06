#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import csv
import codecs

FIELDNAME_KEY = u'Key'
FIELDNAME_COMMENT = u'Comment'

class AppleLocalizedStringsFileSyntaxError(Exception):
	'''Exception raised when the parser can not extract every part of the localized entry'''

def parseAppleLocalizedStringsFile(filePath):
	'''
	Parse and return localization from an Apple '.strings' file.

	:param str filePath: The path to csv file to import from
	:return: Two dictionaries: both using localization keys as keys, the first using localized texts as values, the second using comments as values
	:rtype: (dict,dict)
	:raises AppleLocalizedStringsFileSyntaxError: if the parsing failed at some point
	'''
	rComment = '^ */\*(.*)\*/ *$'
	pComment = re.compile(rComment)
	rCommentStart = '^ */\*(.*)$'
	pCommentStart = re.compile(rCommentStart)
	rCommentEnd = '(.*)\*/ *$'
	pCommentEnd = re.compile(rCommentEnd)
	rKeyValue = '^ *"(.*)" *= *"(.*)" *; *$'
	pKeyValue = re.compile(rKeyValue)

	hasError = False
	keysValues = {}
	keysComments = {}

	with codecs.open(filePath, "r", "utf-16-le") as stringsFile:
		lines = stringsFile.readlines()
		lineCount = 0
		hasComment = False
		hasCommentStarted = False
		cComment = ""
		for lRaw in lines:
			lineCount += 1
			l = lRaw.strip()
			if l != "":
				if not hasComment:
					if not hasCommentStarted:
						result = pComment.search(l)
						if result != None :
							cComment = result.groups()[0]
							hasComment = True
						else:
							result = pCommentStart.search(l)
							if result != None :
								cComment = result.groups()[0]
								hasCommentStarted = True
							else:
								hasError = True
								raise AppleLocalizedStringsFileSyntaxError('Invalid comment format',{'cComment':cComment, 'hasComment':hasComment, 'hasCommentStarted':hasCommentStarted, 'lineCount':lineCount, 'rawLine':lRaw})
					else:
						result = pCommentEnd.search(l)
						if result != None :
							cComment += "\n" + result.groups()[0]
							hasComment = True
						else:
							cComment += "\n" + l
				else:
					result = pKeyValue.search(l)
					if (result != None):
						key = result.groups()[0]
						value = result.groups()[1]
						keysValues[key] = value
						keysComments[key] = cComment.strip()
						key = ""
						value = ""
						cComment = ""
					else:
						hasError = True
						raise AppleLocalizedStringsFileSyntaxError('Invalid pair key/value format',{'lineCount':lineCount, 'rawLine':lRaw})
					hasComment = False
					hasCommentStarted = False
	if hasError:
		return None
	else:
		return (keysValues, keysComments)

def exportLocalizationToCsvFile(outputFileName,keys,localization,encoding=u"utf-8"):
	'''
	Write localization to a CSV file.

	:param str outputFileName: The path to csv file to export to
	:param list keys: The list of localization key
	:param dict localization: The dictionary of dictionries of localized texts, first level key being the language or 'Comment', second level key being the localization key for the translated text or the comment
	:param str encoding: Encoding used for codecs.open (optional)
	:return: void
	:rtype: None
	:raises ValueError: if 'Key' is present in the csv fieldnames
	'''
	fieldnames = list(localization)
	if FIELDNAME_KEY in fieldnames:
		raise ValueError(FIELDNAME_KEY + u" is expected to be absent from fieldnames")
	with codecs.open( outputFileName, u"w", encoding=encoding ) as fileTo:
		csvFieldnames = list(fieldnames)
		csvFieldnames.insert(0,FIELDNAME_KEY)
		writer = csv.DictWriter(fileTo, fieldnames=csvFieldnames)
		writer.writeheader()
		for key in keys:
			rowToWrite = {FIELDNAME_KEY:key}
			for fieldname in fieldnames:
				if key in localization[fieldname]:
					rowToWrite[fieldname] = localization[fieldname][key]
			writer.writerow(rowToWrite)
	return

def importLocalizationFromCsvFile(inputFileName,encoding=u"utf-8"):
	'''
	Parse and return localization from a CSV file.

	:param str inputFileName: The path to csv file to import from
	:param str encoding: Encoding used for codecs.open (optional)
	:return: The list of localization keys and the dictionary of dictionries of localized texts, first level key being the language or 'Comment', second level key being the localization key for the translated text or the comment
	:rtype: (list,dict)
	:raises ValueError: if 'Key' is not present in the csv fieldnames
	'''
	extractedValues = dict()
	extractedKeys = list()

	with codecs.open( inputFileName, u"r", encoding=encoding ) as csvfile:
		reader = csv.DictReader(csvfile)
		csvFieldnames = list(reader.fieldnames)
		if not FIELDNAME_KEY in csvFieldnames:
			raise ValueError(FIELDNAME_KEY + u" is not present as a fieldname in csv.")
		else:
			csvFieldnames.remove(FIELDNAME_KEY)
			for fieldname in fieldnames:
				extractedValues[fieldname] = dict()
			for row in reader:
				# print(row)
				key = row[FIELDNAME_KEY]
				extractedKeys.append(key)
				for fieldname in fieldnames:
					extractedValues[fieldname][key] = row[fieldname]
	return (extractedKeys, extractedValues)
