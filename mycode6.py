__author__ = 'col'
import os
import csv
import re
from os import listdir
from os.path import isfile, join


class mainFilterHandler (object):

    def __init__(self, outfilename, searchfilename):
        # file operation
        self.filedir = os.path.dirname(__file__)
        self.inputdir = 'rules'
        self.outputdir = 'output'
        self.inputfilelist = [f for f in listdir(self.inputdir) if isfile(join(self.inputdir, f))]
        self.outputfilename = outfilename
        self.outputfilenamefull = os.path.join(self.filedir, self.outputdir + '/' + self.outputfilename)

        self.searchDataFilename = searchfilename
        self.searchDataList = self.getSearchDataList(self.searchDataFilename)
        print '###########################################################################################'
        print 'Outputfilename: %s' %self.outputfilename
        print 'Searchfilename: %s' %self.searchDataFilename
        print 'start searching %s in below raw files' %self.searchDataList

        self.IPtoFQDNLIST = []

        self.mainFilterCounter = 0

    def getSearchDataList(self, filename):
        with open(filename, 'rb') as f:
            return [line.strip() for line in f]

    def writeRow(self, outF, row):
        writer = csv.writer(outF)
        writer.writerow(row)

    def isMatchedinSearchRow(self, data, source):
        if re.findall(data, source):
            return True

    def getRegexFullwithGroup (self, matchDataList):
        regex_Group = r"\w+ \(Group\)"
        regex_IP = "\.[^)]*"
        regex_Combine ="|"
        regex = regex_Group
        for data in matchDataList:
            regex = regex + regex_Combine + data + regex_IP
        return regex

    def countMatchedPatternInList(self, pattern, orgList):
        matchedCount = 0
        for item in orgList:
            if re.findall(pattern, item):
                matchedCount +=1
        return matchedCount

    def isAllGroupObjectinList(self,orgList):
        #print orgList
        #print list(orgList).__len__()
        #print self.countMatchedPatternInList('\(Group\)', orgList)
        return list(orgList).__len__() == self.countMatchedPatternInList('\(Group\)', orgList)

    def searchFile(self, inF, outF, matchDataList):
        reader = csv.DictReader(inF)
        count = 0
        for row in reader:
            deviceid = str(row["device.id"])
            devicename = str(row["device.name"])
            policyuid = str(row["policy.uid"])
            policyname = str(row["policy.name"])
            ruleuid = str(row["rule.uid"])
            rulenumber = str(row["rule.number"])
            rulename = str(row["rule.name"])
            ruledisabled = str(row["rule.disabled"])
            rulesource = str(row["rule.source"])
            ruledestination = str(row["rule.destination"])
            ruleservice = str(row["rule.service"])
            ruleaction = str(row["rule.action"])

            # construct the output row "Original row + True or False Result + Matched Result"
            outputRow = []
            outputRow.extend((deviceid, devicename, policyname, rulenumber, rulename, rulesource))
            TorFResult = ["F"] * len(matchDataList)

            Regex_itemsToBeChangedwithGroup = self.getRegexFullwithGroup (matchDataList)
            regex_IP = "\.[^)]*"

            TorFrowMatched = False
            itemsToBeChanged = []
            itemsToBeChangedMatched = False
            i = 0
            for data in matchDataList:
                # Search for rulesource column
                if self.isMatchedinSearchRow(data, rulesource):
                    matched_group = re.findall(Regex_itemsToBeChangedwithGroup, rulesource)
                    matched_ip = re.findall(data + regex_IP, rulesource)
                    TorFrowMatched = True
                    TorFResult[i] = "T"
                    # output itemsToBeChanged for one time only per row
                    # if matched_group and itemsToBeChangedMatched is False:
                    if matched_group and itemsToBeChangedMatched is False:
                        itemsToBeChangedMatched = True
                        itemsToBeChanged.append(matched_group)

                # Search for device id column for catering miss format case
                if self.isMatchedinSearchRow(data, deviceid):
                    matched_ip = re.findall(data + regex_IP, deviceid)
                    TorFrowMatched = True
                    TorFResult[i] = "T"
                    itemsToBeChanged.append(matched_ip)

                # Output matched result only for two condition
                # 1 There are row matched
                # 2 Output result for once only all matchDataList search
                if TorFrowMatched is True and i == len(matchDataList) - 1:
                    outputRow.extend(TorFResult)

                    itemsToBeChanged = self.getFlattenList(itemsToBeChanged)
                    a = self.isAllGroupObjectinList(itemsToBeChanged)

                    outputRow.append(itemsToBeChanged)

                    self.IPtoFQDNLIST.extend(itemsToBeChanged)
                    # print outputrow to file
                    self.writeRow(outF, outputRow)
                    count += 1
                i += 1
        return count

    def setMainFilterHeader(self):
        # construct the output file header row
        header = [
            "device.id",
            "device.name",
            #    "policy.uid",
            "policy.name",
            #    "rule.uid",
            "rule.number",
            "rule.name",
            #    "rule.disabled",
            "rule.source"
            #    "rule.destination",
            #    "rule.service",
            #    "rule.action"
        ]
        newHeaderColmn = [
            "item to be changed",
            "action"
        ]
        header.extend(self.searchDataList)
        header.extend(newHeaderColmn)
        return header

    def mainFilter(self):

        outputHeader = self.setMainFilterHeader()
        # Open output file, start writer
        with open(self.outputfilenamefull, 'wb') as outF:
            # pint header row to output file
            self.writeRow(outF, outputHeader)

            # Open raw data file one by one
            for filename in self.inputfilelist:
                inputfilenamefull = os.path.join(self.filedir, self.inputdir + '/' + filename)
                # Open raw data file, start reader
                with open(inputfilenamefull, 'rb') as inF:

                    #print 'searching file: %s' %inputfilenamefull

                    # search the files with key word in matchDataList
                    rowprintedcount = self.searchFile(inF, outF, self.searchDataList)
                    self.mainFilterCounter += rowprintedcount

            print 'Total output main filter row: %s' %self.mainFilterCounter

    def setfqdnlistFilterHeader(self):
        header = [
            "ip address",
            "fqdn"
        ]
        return header

    def getFlattenList(self, oldlist):
        flattenedList = []
        for sublist in oldlist:
            for val in sublist:
                flattenedList.append(val)
        return flattenedList

    def removeDuplicates(self,orglist):
        return list(set(orglist))

    def fqdnlistFilter(self, outFilename):
        # file operation
        filedir = self.filedir
        outputdir = self.outputdir
        outputfilename = outFilename
        outputfilenamefull = os.path.join(filedir, outputdir + '/' + outputfilename)

        outputHeader = self.setfqdnlistFilterHeader()

        FQDNLIST2 = []
        i = 0
        for item in self.IPtoFQDNLIST:
            if not str(self.IPtoFQDNLIST[i]).endswith("(Group)"):
                FQDNLIST2.append(self.IPtoFQDNLIST[i])
            i += 1
        FQDNLIST2 = self.removeDuplicates(FQDNLIST2)

        with open(outputfilenamefull, 'wb') as outF:
            # pint header row to output file
            writer = csv.writer(outF)
            self.writeRow(outF, outputHeader)
            for val in FQDNLIST2:
                writer.writerow([val])
            print 'Total output fqdnlist row: %s' %FQDNLIST2.__len__()

if __name__ == '__main__':

    s1a = 'search1_wwh_net.txt'
    s1b = 'search1_wwh_host.txt'
    o1a = 'output1_wwh_net.csv'
    o1b = 'output1_wwh_host.csv'
    o1c = 'output1_wwh_fqdn.csv'

    s2a = 'search2_tko_net.txt'
    s2b = 'search2_tko_host.txt'
    o2a = 'output2_tko_net.csv'
    o2b = 'output2_tko_host.csv'
    o2c = 'output2_tko_fqdn.csv'

    s3a = 'search3_es_net.txt'
    s3b = 'search3_es_host.txt'
    o3a = 'output3_es_net.csv'
    o3b = 'output3_es_host.csv'
    o3c = 'output3_es_fqdn.csv'

    s4a = 'search4_ifc_net.txt'
    s4b = 'search4_ifc_host.txt'
    o4a = 'output4_ifc_net.csv'
    o4b = 'output4_ifc_host.csv'
    o4c = 'output4_ifc_fqdn.csv'

    s5a = 'search5_ip_net.txt'
    s5b = 'search5_ip_host.txt'
    o5a = 'output5_ip_net.csv'
    o5b = 'output5_ip_host.csv'
    o5c = 'output5_ip_fqdn.csv'

    s6a = 'search6_ces_net.txt'
    s6b = 'search6_ces_host.txt'
    o6a = 'output6_ces_net.csv'
    o6b = 'output6_ces_host.csv'
    o6c = 'output6_ces_fqdn.csv'

    s7a = 'search7_pccwt_net.txt'
    s7b = 'search7_pccwt_host.txt'
    o7a = 'output7_pccwt_net.csv'
    o7b = 'output7_pccwt_host.csv'
    o7c = 'output7_pccwt_fqdn.csv'


    #outputfilename, searchfilename
    net = mainFilterHandler(o1a, s1a)
    net.mainFilter()
    host = mainFilterHandler(o1b, s1b)
    host.mainFilter()
    host.fqdnlistFilter(o1c)

    net = mainFilterHandler(o2a, s2a)
    net.mainFilter()
    host = mainFilterHandler(o2b, s2b)
    host.mainFilter()
    host.fqdnlistFilter(o2c)

    net = mainFilterHandler(o3a, s3a)
    net.mainFilter()
    host = mainFilterHandler(o3b, s3b)
    host.mainFilter()
    host.fqdnlistFilter(o3c)

    net = mainFilterHandler(o4a, s4a)
    net.mainFilter()
    host = mainFilterHandler(o4b, s4b)
    host.mainFilter()
    host.fqdnlistFilter(o4c)

    net = mainFilterHandler(o5a, s5a)
    net.mainFilter()
    host = mainFilterHandler(o5b, s5b)
    host.mainFilter()
    host.fqdnlistFilter(o5c)

    net = mainFilterHandler(o6a, s6a)
    net.mainFilter()
    host = mainFilterHandler(o6b, s6b)
    host.mainFilter()
    host.fqdnlistFilter(o6c)