#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import codecs

class AppleLocalizedStringsFileSyntaxError(Exception):
	'''Exception raised when the parser can not extract every part of the localized entry'''

########################################################
# functions Keys extraction
########################################################

# Return (keysValues, keysComments), two dictionaries
def parseAppleLocalizedStringsFile(filePath):
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
