#!/usr/bin/python  
#-*- coding:utf-8 -*-  

# https://console.developers.google.com/apis/
# Google API Doc: https://cloud.google.com/translate/docs/translating-text

import httplib
import md5
import urllib
import random
import re
import json
import os
import sys

kGGAPIKey = 'YOUR_GOOGLE_API_KEY'


gStringsFileName = ''
gStringsKeyList = []
gStringsValueList = []
gAllSupportedLangList = ['auto', 'zh', 'en', 'yue', 'wyw', 'jp', 'kor', 'fra', 'spa', 'th', 'ara', 'ru', 'pt', 'de', 'it', 'el', 'nl', 'pl', 'bul', 'est', 'dan', 'fin', 'cs', 'rom', 'slo', 'swe', 'hu', 'cht', 'vie']


reload(sys)
sys.setdefaultencoding( "utf-8" )


def initStringsKeyValueFromFile(fileName):
	global gStringsFileName
	global gStringsKeyList
	global gStringsValueList

	gStringsFileName = fileName

	try:
		f = open(fileName, 'r')  
		lines = f.readlines()  
	except IOError as e:  
		print e  
	else:
		for line in lines:  
			match = re.search(r'^"(?P<key>.*?)"(\s*)=(\s*)"(?P<value>.*?)"', line)
			if match:
				gStringsKeyList.append(match.group('key'))
				gStringsValueList.append(match.group('value'))
			else:
				# 为了保存注释或空行到新的翻译文件
				gStringsKeyList.append(line)
				gStringsValueList.append('')
	finally:  
		f.close()


def translateToLanguageList(fromLang, toLangs):
	if fromLang not in gAllSupportedLangList:
		print fromLang + 'is not supported'
		return

	for toLang in toLangs:
		if toLang not in gAllSupportedLangList:
			print toLang + 'is not supported'
			break
		translateToLang(fromLang, toLang)


def translateToLang(fromLang, toLang):
	httpsClient = None
	
	httpsClient = httplib.HTTPSConnection('translation.googleapis.com')

	extension = os.path.splitext(gStringsFileName)[1]
	toFileName = gStringsFileName.replace(extension, '_' + toLang + extension)
	toFile = open(toFileName, 'w');

	print 'Translating ' + toLang + ' to fileName: ' + toFileName

	for index,val in enumerate(gStringsValueList):
		q = val

		myurl = '/language/translate/v2'
		if q:

			myurl = myurl + '?key=' + kGGAPIKey + '&q=' + urllib.quote(q) + '&source=' + fromLang + '&target=' + toLang
			#print myurl
			try:
				httpsClient.request('GET', myurl)
			 
				#response is HTTPResponse object
				response = httpsClient.getresponse()

				jsonData = json.loads(response.read())
				dst = jsonData['data']['translations'][0]['translatedText']
				print dst

				result = '"' + gStringsKeyList[index] + '" = "' + dst + '";\n'
				toFile.write(result)

			except Exception, e:
				print e

		else:
			# skip & save original key
			toFile.write(gStringsKeyList[index])

	if httpsClient:
		httpsClient.close()

	if toFile:
		toFile.close()

	print 'Finished translating to ' + toLang 


fileName = raw_input('Enter a fileName: ')
initStringsKeyValueFromFile(fileName)
print 'Supports languages:'
print gAllSupportedLangList
fromLang = raw_input('Enter from language: ')
toLangs = raw_input('Enter to language list, split by space: ')
print 'Start'
translateToLanguageList(fromLang, toLangs.split())
print 'All done!'
