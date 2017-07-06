#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import csv
import codecs
import subprocess

FIELDNAME_KEY = u'Key'
FIELDNAME_COMMENT = u'Comment'

class AppleLocalizedStringsFileSyntaxError(Exception):
	'''Exception raised when the parser can not extract every part of the localized entry'''

class ResourcesError(Exception):
	'''Exception raised when files are unexpected or in unexpected state'''

def parseAppleLocalizedStringsFile(filePath):
	'''
	Parse and return localization from an Apple '.strings' file.

	:param str filePath: The path to Apple '.strings' file to import from
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

def writeAppleLocalizedStringsFile(filePath,keys,comments,localizedTexts):
	'''
	Write a localization Apple '.strings' file.

	:param str filePath: The path to Apple '.strings' file to export to
	:param list keys: Localization keys
	:param dict comments: dictionary with localization keys as keys and comments as values
	:param dict localizedTexts: dictionary with localization keys as keys and localized texts as values
	:return: void
	:rtype: None
	:raises ValueError: if 'Key' is not present in the csv fieldnames
	'''
	with codecs.open( filePath, u"w", u"utf-16-le" ) as fileTo:
		for key in keys:
			comment = comments.get(key, u"")
			value = localizedTexts.get(key, u"")
			fileTo.write( u"/* " + comment + u" */" + u"\n" )
			fileTo.write( u"\"" + key + u"\" = \"" + value + u"\";" + u"\n" )
			fileTo.write( u"\n" )
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
			for fieldname in csvFieldnames:
				extractedValues[fieldname] = dict()
			for row in reader:
				# print(row)
				key = row[FIELDNAME_KEY]
				extractedKeys.append(key)
				for fieldname in csvFieldnames:
					extractedValues[fieldname][key] = row[fieldname]
	return (extractedKeys, extractedValues)

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


# return a strings file keys: list
def prepareLocalizationPaths(folderPath):
	baseLprojFolderName = u"Base.lproj"
	baseLocalizationFolderPathList = list()
	localizationFiles = []
	localizationFolders = []
	for (dirpath, dirnames, filenames) in os.walk(folderPath):
		if dirpath.endswith(baseLprojFolderName) :
			baseLocalizationFolderPathList.append(dirpath)
	if 1 != len(baseLocalizationFolderPathList) :
		raise ResourcesError( str(numberOfFolderBaseLprojFound) + u" Base.lproj folder found, expected 1.", baseLocalizationFolderPathList)

	baseLocalizationFolderPath = baseLocalizationFolderPathList[0]

	localizationFiles = [
		lFile
		for lFile
		in os.listdir(baseLocalizationFolderPath)
		if lFile.endswith(u".strings")
			and os.path.isfile(os.path.join(baseLocalizationFolderPath,lFile))
		]
	(head,tail) = os.path.split(baseLocalizationFolderPath)
	localizationFolders = [
		os.path.join(head,lFile)
		for lFile
		in os.listdir(head)
		if lFile.endswith(u".lproj")
			and not os.path.isfile(os.path.join(head,lFile))
			and not lFile == baseLprojFolderName
		]

	return ( baseLocalizationFolderPath, localizationFiles, localizationFolders )

def writeLocalizationFiles( sourceFilesProjectRootFolderPath, outputLocalizationFolderPath ):
	# NOTE : the final solution was to use find with -print0 and xargs with -0 to force the use of other separator
	findFilesCommand = subprocess.Popen( ["find",sourceFilesProjectRootFolderPath,"-name","*.m","-print0"], stdout = subprocess.PIPE, stderr = subprocess.PIPE )

	# "stdin = findFilesCommand.stdout" is necessary to link subprocesses
	genstringsCommand = subprocess.Popen( ["xargs","-0","genstrings","-o",outputLocalizationFolderPath], stdin = findFilesCommand.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
	findFilesCommand.stdout.close()
	(stdoutdata, stderrdata) = genstringsCommand.communicate()
	if stdoutdata:
		raise RuntimeWarning( u"stdoutdata : " + stdoutdata )
	if stderrdata:
		raise RuntimeWarning( u"stderrdata : " + stderrdata )
	return
