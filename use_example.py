#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import AppleLocalizedStringsFileParser

localizationTableName = u"MyApp"
projectCodePath = u"../MyApp";

( baseLocalizationFolderPath, localizationFiles, localizationFolders ) = AppleLocalizedStringsFileParser.prepareLocalizationPaths(projectCodePath)
print( baseLocalizationFolderPath, localizationFiles, localizationFolders )

AppleLocalizedStringsFileParser.writeLocalizationFiles(projectCodePath, baseLocalizationFolderPath)

filesCreated = AppleLocalizedStringsFileParser.exportLocalizationFromFolderToCsv(projectCodePath)
print( filesCreated )

AppleLocalizedStringsFileParser.saveLocalizationFromCsvToProjectFolder( localizationTableName + u".strings.csv", projectCodePath, localizationTableName + u".strings")

exit(0)
