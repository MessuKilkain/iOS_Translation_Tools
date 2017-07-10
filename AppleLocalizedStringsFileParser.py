#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import csv
import subprocess
# python2 open method does not have encoding parameter with open method, workarround is to use codecs.open instead
from codecs import open

FIELDNAME_KEY = u'Key'
FIELDNAME_COMMENT = u'Comment'
BASE_LPROJ_FOLDER_NAME = u"Base.lproj"

class AppleLocalizedStringsFileSyntaxError(Exception):
	'''Exception raised when the parser can not extract every part of the localized entry'''

class ResourcesError(Exception):
	'''Exception raised when files are unexpected or in unexpected state'''

class UnmatchingComment(Exception):
	'''Exception raised when comments are different for the same localization key'''

def guessEncoding(filePath,encodingsToTry=[u"utf-16",u"utf-16-le",u"utf-8"]):
	'''
	Try to open and read the file with encodings until the right one is found or all encodings have been tested

	:param str filePath: The path to file which encoding is unknown
	:param list encodingsToTry: List of encodings to try on the file. (optional)
	:return: Correct encoding found or None
	:rtype: str
	:raises EncodingError: if the last encoding to try has failed to open the file.
	'''
	encodingFound = None
	encodingsToTry = list(encodingsToTry)
	while 0 < len(encodingsToTry) and not encodingFound:
		encoding = encodingsToTry[0]
		try:
			with open(filePath, u"r", encoding=encoding) as stringsFile:
				lines = stringsFile.readline()
				encodingFound = encoding
			pass
		except UnicodeError as e:
			encodingsToTry.pop(0)
			if 0 >= len(encodingsToTry):
				raise
	return encodingFound

def mergeCommentsDictionaries(d1,d2):
	'''
	Combine two dictionaries without conflicts

	:param d1: First dictionary
	:param d2: Second dictionary
	:return: A dictionary with keys and values from both d1 and d2
	:rtype: dict
	:raises UnmatchingComment: if there is any conflict between the two dictionaries.
	'''
	res = d1.copy()
	for k in d2:
		v = d2[k]
		if v:
			if k in d1 and d1[k] and d1[k] != d2[k]:
				raise UnmatchingComment(u"Comments are differents for key " + k, [d1[k] ,d2[k]])
			else:
				res[k] = v
	return res

def parseAppleLocalizedStringsFile(filePath,encodingsToTry=[u"utf-16",u"utf-16-le",u"utf-8"]):
	'''
	Parse and return localization from an Apple '.strings' file.

	:param str filePath: The path to Apple '.strings' file to import from
	:param list encodingsToTry: List of encodings to try on the file. (optional)
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

	encoding = guessEncoding(filePath,encodingsToTry=encodingsToTry)

	with open(filePath, u"r", encoding=encoding) as stringsFile:
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
								raise AppleLocalizedStringsFileSyntaxError('Invalid comment format',{'cComment':cComment, 'hasComment':hasComment, 'hasCommentStarted':hasCommentStarted, 'lineCount':lineCount, 'rawLine':lRaw, 'filePath':filePath})
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

def writeAppleLocalizedStringsFile(filePath,keys,comments,localizedTexts,encoding=u"utf-16"):
	'''
	Write a localization Apple '.strings' file.

	:param str filePath: The path to Apple '.strings' file to export to
	:param list keys: Localization keys
	:param dict comments: dictionary with localization keys as keys and comments as values
	:param dict localizedTexts: dictionary with localization keys as keys and localized texts as values
	:param str encoding: Encoding used for writing files (optional)
	:return: void
	:rtype: None
	:raises ValueError: if 'Key' is not present in the csv fieldnames
	'''
	with open( filePath, u"w", encoding=encoding ) as fileTo:
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
	:param str encoding: Encoding used for open (optional)
	:return: The list of localization keys and the dictionary of dictionries of localized texts, first level key being the language or 'Comment', second level key being the localization key for the translated text or the comment
	:rtype: (list,dict)
	:raises ValueError: if 'Key' is not present in the csv fieldnames
	'''
	extractedValues = dict()
	extractedKeys = list()

	with open( inputFileName, u"r", encoding=encoding ) as csvfile:
		reader = csv.DictReader(csvfile)
		csvFieldnames = list(reader.fieldnames)
		if not FIELDNAME_KEY in csvFieldnames:
			raise ValueError(FIELDNAME_KEY + u" is not present as a fieldname in csv.")
		else:
			csvFieldnames.remove(FIELDNAME_KEY)
			for fieldname in csvFieldnames:
				extractedValues[fieldname] = dict()
			for row in reader:
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
	:param str encoding: Encoding used for open (optional)
	:return: void
	:rtype: None
	:raises ValueError: if 'Key' is present in the csv fieldnames
	'''
	fieldnames = list(localization)
	if FIELDNAME_KEY in fieldnames:
		raise ValueError(FIELDNAME_KEY + u" is expected to be absent from fieldnames")
	with open( outputFileName, u"w", encoding=encoding ) as fileTo:
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

def exportLocalizationFromFolderToCsv(folderPath,outputFolder = u'.'):
	'''
	Export localization to csv from Apple '.strings' files found and sorted in folderPath

	:param str folderPath: The path to the folder containing Apple '.strings' files in its hierarchy to convert into .csv
	:param str outputFolder: The path to the folder to write csv files. (optional)
	:return: The list of paths to created csv files
	:rtype: list
	'''
	( baseLocalizationFolderPath, localizationFiles, localizationFolders ) = prepareLocalizationPaths(folderPath)

	localizedFolders = list(localizationFolders)
	localizedFolders.append(baseLocalizationFolderPath)

	filesCreated = list()
	for lFileName in localizationFiles:
		keys = set()
		comments = dict()
		translatedTexts = dict()
		for lFolderPath in localizedFolders:
			lFolderName = os.path.basename( lFolderPath )
			lFileLangPath = os.path.join( lFolderPath, lFileName )
			if os.path.exists( lFileLangPath ) and os.path.isfile( lFileLangPath ):
				(keysValues, keysComments) = parseAppleLocalizedStringsFile(lFileLangPath)
				keys.update(list(keysValues))
				comments = mergeCommentsDictionaries(comments, keysComments)
				translatedTexts[lFolderName] = keysValues
		translatedTexts[FIELDNAME_COMMENT] = comments
		outputFileName = os.path.join(outputFolder, lFileName + os.extsep + u"csv")
		exportLocalizationToCsvFile( outputFileName, sorted(list(keys), key=lambda s:s.lower()), translatedTexts )
		filesCreated.append(outputFileName)
	return filesCreated

def saveLocalizationFromCsvToProjectFolder(csvFilePath, projectFolderPath, localizationTableName, csvFileEncoding=u"utf-8", stringsFileEncoding=u"utf-16"):
	'''
	Import localization from csv to Apple '.strings' files in the localization folders founds in projectFolderPath

	:param str csvFilePath: The path to csv file to import.
	:param str projectFolderPath: The path to the folder containing Apple '.strings' files in its hierarchy
	:param str localizationTableName: The name of '.strings' files to create
	:param str csvFileEncoding: Encoding used for open csv file (optional)
	:param str stringsFileEncoding: Encoding used for writing '.strings' files (optional)
	:return: void
	:rtype: None
	'''
	( baseLocalizationFolderPath, localizationFiles, localizationFolders ) = prepareLocalizationPaths(projectFolderPath)

	localizedFolders = list(localizationFolders)
	localizedFolders.append(baseLocalizationFolderPath)

	(extractedKeys, extractedValues) = importLocalizationFromCsvFile(csvFilePath, encoding=csvFileEncoding)

	for lFolderPath in localizedFolders:
		lFolderName = os.path.basename( lFolderPath )
		lFileLangPath = os.path.join( lFolderPath, localizationTableName )
		writeAppleLocalizedStringsFile( lFileLangPath, extractedKeys, extractedValues[FIELDNAME_COMMENT], extractedValues[lFolderName], encoding=stringsFileEncoding)

def prepareLocalizationPaths(folderPath,baseLprojFolderName=BASE_LPROJ_FOLDER_NAME):
	'''
	Get the paths necessary to process externally Apple '.strings' localization files from Project folder

	:param str folderPath: The path to the project folder to scan.
	:param str baseLprojFolderName: The name of the folder for Base localization (aka untranslated)
	:return: Three values: the path to the 'Base.lproj' folder found, the list of localization files name (table name with extension '.strings') found, the list of path to language folders found (like 'Base.lproj')
	:rtype: (str,list,list)
	:raises ResourcesError: if there is no or more than only one 'Base.lproj' found
	'''
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
	'''
	Generate '.strings' files from source code files '.m' in outputLocalizationFolderPath folder

	:param str sourceFilesProjectRootFolderPath: The path to the folder containing source code files '.m' in its hierarchy
	:param str outputLocalizationFolderPath: Path to the folder where '.strings' files should be generated.
	:return: void
	:rtype: None
	:raises RuntimeWarning: if there is some data printed by command line used (in stdout or stderr)
	'''
	# NOTE : the final solution was to use find with -print0 and xargs with -0 to force the use of other separator
	findFilesCommand = subprocess.Popen( ["find",sourceFilesProjectRootFolderPath,"-name","*.m","-print0"], stdout = subprocess.PIPE, stderr = subprocess.PIPE )

	# "stdin = findFilesCommand.stdout" is necessary to link subprocesses
	genstringsCommand = subprocess.Popen( ["xargs","-0","genstrings","-o",outputLocalizationFolderPath], stdin = findFilesCommand.stdout, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
	findFilesCommand.stdout.close()
	(stdoutdata, stderrdata) = genstringsCommand.communicate()
	if stdoutdata or stderrdata:
		raise RuntimeWarning( u"The genstrings command line exit with data on stdout or stderr", {'stdoutdata':stdoutdata, 'stderrdata':stderrdata} )
	return
