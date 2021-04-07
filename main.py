import os
import json
import pathlib
import re


def iterateDirectories(rpath, sfn=''):
    reportlistpath = 'C:\\Users\\ranton\\Downloads\\2021-03-30\\2021-03-30\\processListSimple.txt'
    reportsDict = readReportRef(reportlistpath)
    if sfn == '':
        for root, dirs, files in os.walk(rpath):
            procDir = root.split('\\')[-2]
            if procDir == 'Workforce Budgeting':
                for file in files:
                    fileExt = pathlib.Path(file).suffix
                    if fileExt == '.bs':
                        reports = []
                        calledin = []
                        processed = []
                        lookinreports(file, reports, reportsDict)
                        lookforusages(calledin, file, processed, reports, rpath)
    else:
        reports = []
        lookinreports(sfn, reports, reportsDict)
        lookforusages([], sfn, [], reports, rpath)


def lookinreports(file, reports, reportsDict):
    for k, v in reportsDict.items():
        if len(v) > 0:
            strinlist = ','.join([str(el) for el in v])
            if re.search(file, strinlist, re.IGNORECASE):
                reports.append(k)


def lookforusages(calledin, file, processed, reports, rpath):
    for r, d, fls in os.walk(rpath):
        for f in fls:
            if f != file:
                fExt = pathlib.Path(f).suffix
                if f not in processed and fExt == '.bs':
                    processed.append(f)
                    fPath = os.path.join(r, f)
                    with open(fPath, 'r', encoding='UTF-8') as fr:
                        content = fr.readlines()
                        for ln in [li.strip('\n\r\t') for li in content]:
                            if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include',ln, re.IGNORECASE):
                                calledin.append(f)
    print(f'{file};{calledin};{reports}')


def readReportRef(fpath):
    with open(fpath, 'r') as fr:
        content = fr.readlines()
        curr = ''
        repsDict = {}
        for ln in [li.strip('\n\r') for li in content]:
            if not ln.startswith('\t'):
                if ln not in repsDict and ln != '':
                    repsDict[ln] = []
                    curr = ln
            elif ln.startswith('\t') and curr != '':
                repsDict[curr].append(ln.strip('\t')[1:-1] + '.bs')
        return repsDict


def checkObsolete(rpath):
    obsolete = []
    with open(rpath) as fr:
        data = json.load(fr)
        for checkedProcess, checkedProcData in data.items():
            isUsed = False
            if len(checkedProcData['reports']) > 0:
                isUsed = True
            if not isUsed:
                for key, value in data.items():
                    if checkedProcess != key:
                        if checkedProcess in value['callsTo']:
                            isUsed = True
            if not isUsed:
                obsolete.append(checkedProcess)

    for o in obsolete:
        print(o)


def checkRemaining(rpath):
    obsolete = []
    usedReports = []
    usedProcesesses = []
    with open(rpath) as fr:
        data = json.load(fr)
        for checkedProcess, checkedProcData in data.items():
            isUsed = False
            if len(checkedProcData['reports']) > 0:
                isUsed = True
                usedReports.append(f'{checkedProcess}; {checkedProcData["reports"]}')
            if not isUsed:
                for key, value in data.items():
                    if checkedProcess != key:
                        if checkedProcess in value['callsTo']:
                            isUsed = True
                            usedProcesesses.append(f'{checkedProcess};{key}')
            if not isUsed:
                obsolete.append(checkedProcess)

    print('obsolete')
    for o in obsolete:
        print(o)

    print('inReports')
    for u in usedReports:
        print(f'{u}')

    print('inProcess')
    for up in usedProcesesses:
        print(up)


if __name__ == '__main__':
    # checkRemaining(
    #     'C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\result.json')
    iterateDirectories('C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\Projects\\AppEngine\\Sources\\Depm\\Processes\\', 'WB_GetPositionSliceXML.BS')
