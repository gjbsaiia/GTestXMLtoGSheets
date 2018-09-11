#!/usr/bin/python

# Griffin Saiia
# XML to GSheets, Test document formatting

import os
import sys
import json
import gspread
import xml.etree.ElementTree as xmlReader
from oauth2client.client import SignedJwtAssertionCredentials

# Nested data structures to extract test data into
class testDoc:
	def __init__(self):
		self.name = ""
		self.runtime = 0
		self.tests = 0
		self.failures = 0
		self.errors = 0
		self.time = ""
		self.date = ""
		self.testsuite = []
class testSuite:
	def __init__(self):
		self.name = ""
		self.tests = 0
		self.failures = 0
		self.errors = 0
		self.runtime = 0
		self.testcase = []
class testCase:
	def __init__(self):
		self.name = ""
		self.success = False
		self.runtime = 0
		self.classtested = ""

# runs in command line
def main():
	credPath = "creds.json"
	sheetName = "Marturion Armstrong Tests"
	xmlDirectory = "XML_Logs/"
	line = ""
	print("Welcome to Griffin's GTest XML Converter!")
	print("*******************************************")
	line = raw_input("Enter GTest XML name: ")
	print("*******************************************")
	gpath = xmlDirectory+line
	print("converting...")
	xmlTree = xmlReader.parse(gpath)
	testResults = extractData(xmlTree)
	print("...done")
	print("*******************************************")
	print("writing results...")
	credentials = configCreds(credPath)
	writeData(credentials, sheetName, testResults)
	print("...sheet updated.")

# takes XML and populates data structures above
def extractData(xmlTree):
	root = xmlTree.getroot()
	test = testDoc()
	test = toStruct(test, root, 0)
	for child in root:
		suite = testSuite()
		suite = toStruct(suite, child, 1)
		test.testsuite.append(suite)
		for item in child:
			case = testCase()
			case = toStruct(case, item, 2)
			suite.testcase.append(case)
	return test

# generalized stripping xml into structs
# mode 0: testDoc, mode 1: testSuite, mode 2: testCase
def toStruct(struct, xmlObj, mode):
	struct.name = xmlObj.get("name")
	struct.runtime = xmlObj.get("time")
	# for testDoc (mode 0) and testSuite (mode 1)
	if( mode != 2):
		struct.tests = xmlObj.get("tests")
		struct.failures = xmlObj.get("failures")
		struct.errors = xmlObj.get("errors")
		# for testDoc only (mode 0)
		if(mode == 0):
			timestamp = xmlObj.get("timestamp")
			splitted = timestamp.split("T")
			struct.time = splitted[1]
			splitt = splitted[0].split("-")
			date = splitt[1]+"/"+splitt[2]+"/"+splitt[0]
			struct.date = date
	# for testCase (mode 2)
	else:
		struct.classname = xmlObj.get("classname")
		if(xmlObj.get("status") == "run"):
			struct.success = True
		else:
			struct.success = False
	return struct

# config credentials
def configCreds(credPath):
	json_key = json.load(open(credPath))
	scopeList = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scopeList)
	return credentials

# writes to sheet
def writeData(credentials, sheetName, testResults):
	# config destination
	file = gspread.authorize(credentials)
	sheet = file.open(sheetName).add_worksheet(testResults.name, 100, 100)
	i = setUpSheet(sheet, testResults)
	j = 0
	while( j < len(testResults.testsuite)):
		i = writeSuite(sheet, testResults.testsuite[j], i)
		j += 1

# initializes new sheet
def setUpSheet(sheet, testResults):
	i = 1
	sheet.update_cell(i, 1, testResults.date)
	sheet.update_cell(i, 2, testResults.time)
	i += 1
	sheet.update_cell(i, 1, "Suite Name")
	sheet.update_cell(i, 2, testResults.name)
	i += 1
	sheet.update_cell(i, 1, "No. of Tests")
	sheet.update_cell(i, 2, testResults.tests)
	i += 1
	sheet.update_cell(i, 1, "Total Failures")
	sheet.update_cell(i, 2, testResults.failures)
	i += 1
	sheet.update_cell(i, 1, "Error Count")
	sheet.update_cell(i, 2, testResults.errors)
	i += 1
	sheet.update_cell(i, 1, "Runtime")
	sheet.update_cell(i, 2, testResults.runtime)
	return i

# writes the frame for the testing suite
def writeSuite(sheet, suite, i):
	i += 2
	sheet.update_cell(i, 1, "Class Name")
	sheet.update_cell(i, 2, "No. Of Tests")
	sheet.update_cell(i, 3, "Test Name")
	sheet.update_cell(i, 4, "Passed")
	sheet.update_cell(i, 5, "Runtime")
	i += 1
	sheet.update_cell(i, 1, suite.name)
	sheet.update_cell(i, 2, suite.tests)
	j = 0
	while(j < len(suite.testcase)):
		i += 1
		i = writeCase(sheet, suite.testcase[j], i)
		j += 1
	return i

# writes the outcome and information for each test case
def writeCase(sheet, case, i):
	sheet.update_cell(i, 3, case.name)
	sheet.update_cell(i, 4, case.success)
	sheet.update_cell(i, 5, case.runtime)
	return i


# to run it from command line
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("")
		print('Interrupted')
        try:
			sys.exit(0)
	except SystemExit:
			os._exit(0)
