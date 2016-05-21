__author__ = 'col'

import os
import csv
import re
from os import listdir
from os.path import isfile, join


def getMatchData (filename):
    with open(filename, 'rb') as f:
        return [line.strip() for line in f]


def main():
    filedir = os.path.dirname(__file__)
    inputdir = 'rules'
    outputdir = 'output'
    inputfilelist = [f for f in listdir(inputdir) if isfile(join(inputdir, f))]
    # inputfilelist = ['P01ESQCP803.csv']
    outputfilename = 'test.csv'
    outputfilenamefull = os.path.join(filedir, outputdir + '/' + outputfilename)
    matchDataFile = 'search2_tko_net.txt'

    matchData = getMatchData(matchDataFile)
    outputHeader = [
        "device.id",
        "device.name",
    #    "policy.uid",
        "policy.name",
    #    "rule.uid",
        "rulen.number",
        "rule.name",
    #    "rule.disabled",
        "rule.source"
    #    "rule.destination",
    #    "rule.service",
    #    "rule.action"
    ]
    outputHeader.extend(matchData)

    # start writer
    with open(outputfilenamefull, 'wb') as outF:
        writer = csv.writer(outF)
        writer.writerow(outputHeader)
        count = 0

        for filename in inputfilelist:
            inputfilenamefull = os.path.join(filedir, inputdir + '/' + filename)
            # start reader
            with open(inputfilenamefull, 'rb') as inF:
                reader = csv.DictReader(open(inputfilenamefull, 'rb'))
                print 'searching file: %s' %filename

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

                    outputRow = []
                    outputRow.extend((deviceid, devicename, policyname, rulenumber,rulename, rulesource))
                    TorFResult = [False] * len(matchData)

                    reg = ".[^)]*"
                    result2 = []

                    rowMatched = False
                    i = 0
                    for data in matchData:
                        if re.findall(data, rulesource):
                            matched2 = re.findall(data+reg, rulesource)
                            rowMatched = True
                            TorFResult[i] = True
                            result2.append(matched2)

                        if re.findall(data, deviceid):
                            matched2 = re.findall(data+reg, deviceid)
                            rowMatched = True
                            TorFResult[i] = True
                            result2.append(matched2)

                        if rowMatched == True and i == len(matchData) - 1:
                            outputRow.extend(TorFResult)
                            #print result2
                            outputRow.extend(result2)
                            writer.writerow(outputRow)
                            count += 1
                        i += 1
                    # End For line
                # End For row
            # End reader
        # End For filename
        print 'Total output row: %s' %count
    #End writer

if __name__ == '__main__':
    main()
