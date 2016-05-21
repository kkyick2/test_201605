__author__ = 'col'

import os
import csv
import re
from os import listdir
from os.path import isfile, join

FQDNLIST = []



def getMatchDataList(filename):
    with open(filename, 'rb') as f:
        return [line.strip() for line in f]


def writeRow(outF, row):
    writer = csv.writer(outF)
    writer.writerow(row)


def isMatchedinSearchRow(data, source):
    Matched = False
    if re.findall(data, source):
        Matched = True
    return Matched

def getRegexFull_withGroup (matchDataList):
    regex_Group = r"\w+ \(Group\)"
    regex_IP = "\.[^)]*"
    regex_Combine ="|"
    regex = regex_Group
    for data in matchDataList:
        regex = regex + regex_Combine + data + regex_IP
    #print regex
    return regex


def searchFile(inF, outF, matchDataList):
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

        #
        # construct the output row "Original row + True or False Result + Matched Result"
        #
        outputRow = []
        outputRow.extend((deviceid, devicename, policyname, rulenumber, rulename, rulesource))
        TorFResult = ["F"] * len(matchDataList)


        Regex_itemsToBeChanged_withGroup = getRegexFull_withGroup (matchDataList)
        regex_IP = "\.[^)]*"

        TorFrowMatched = False
        itemsToBeChanged = []
        itemsToBeChangedMatched = False
        i = 0
        for data in matchDataList:
            # Search for rulesource column
            if isMatchedinSearchRow(data, rulesource):
                matched_group = re.findall(Regex_itemsToBeChanged_withGroup, rulesource)
                TorFrowMatched = True
                TorFResult[i] = "T"
                # output itemsToBeChanged for one time only per row
                if matched_group and itemsToBeChangedMatched is False:
                    itemsToBeChangedMatched = True
                    itemsToBeChanged.append(matched_group)

            # Search for device id column for catering miss format case
            if isMatchedinSearchRow(data, deviceid):
                matched_ip = re.findall(data + regex_IP, deviceid)
                TorFrowMatched = True
                TorFResult[i] = "T"
                itemsToBeChanged.append(matched_ip)

            # Output matched result only for two condition
            # 1 There are row matched
            # 2 Output result for once only all matchDataList search
            if TorFrowMatched is True and i == len(matchDataList) - 1:
                outputRow.extend(TorFResult)
                print itemsToBeChanged
                outputRow.append(itemsToBeChanged)
                FQDNLIST.extend(itemsToBeChanged)
                writeRow(outF, outputRow)
                count += 1
            i += 1
    return count

def main():
    # file operation
    filedir = os.path.dirname(__file__)
    inputdir = 'rules'
    outputdir = 'output'
    inputfilelist = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]
    # inputfilelist = ['P01ESQCP803.csv']
    outputfilename = 'output3.csv'
    outputfilenamefull = os.path.join(filedir, outputdir + '/' + outputfilename)

    matchDataFile = 'matchdata_host_range.txt'
    matchDataList = getMatchDataList(matchDataFile)

    #
    # construct the output file header row
    #
    outputHeader = [
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
    outputHeader.extend(matchDataList)
    outputHeader.extend(newHeaderColmn)

    # Open output file, start writer
    with open(outputfilenamefull, 'wb') as outF:
        # pint header row to output file
        writeRow(outF, outputHeader)
        count = 0

        # Open raw data file one by one
        for filename in inputfilelist:
            inputfilenamefull = os.path.join(filedir, inputdir + '/' + filename)
            # Open raw data file, start reader
            with open(inputfilenamefull, 'rb') as inF:
                print 'searching file: %s' %inputfilenamefull
                # search the files with key word in matchDataList
                rowprintedcount = searchFile(inF, outF, matchDataList)
                count += rowprintedcount

        print 'Total output row: %s' %count


if __name__ == '__main__':

    main()

    # output second file

    FQDNLIST = sum(FQDNLIST, [])
    FQDNLIST = list(set(FQDNLIST))
    FQDNLIST2 = []
    reg = "(Group)"
    i = 0

    for item in FQDNLIST:
        if str(FQDNLIST[i]).endswith(reg) == False:
            FQDNLIST2.append(FQDNLIST[i])
        i+=1

    print FQDNLIST2

    # file operation
    filedir = os.path.dirname(__file__)
    inputdir = 'rules'
    outputdir = 'output'
    inputfilelist = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]
    outputfilename = 'output_fqdn1.csv'
    outputfilenamefull = os.path.join(filedir, outputdir + '/' + outputfilename)

    outputHeader = [
        "ip address",
        "fqdn"
    ]

    with open(outputfilenamefull, 'wb') as outF:
        # pint header row to output file
        writer = csv.writer(outF)
        writeRow(outF, outputHeader)
        for val in FQDNLIST2:
            writer.writerow([val])