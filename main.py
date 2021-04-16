import os
import json
import pathlib
import re


def iterateDirectories(rpath, sfn=[]):
    print('folder;procName;in process;in reports')
    reportlistpath = 'C:\\Farms\\2021-03-30\\2021-03-30\\processListSimple.txt'
    reportsDict = readReportRef(reportlistpath)
    if len(sfn) == 0:
        for root, dirs, files in os.walk(rpath):
            procDir = root.split('\\')[-2]
            par = root.split('\\')[-1]
            if procDir == 'Workforce Budgeting':
                for file in files:
                    fileExt = pathlib.Path(file).suffix
                    if fileExt == '.bs':
                        reports = []
                        calledin = []
                        processed = []
                        lookinreports(file, reports, reportsDict)
                        lookforusages(calledin, file, processed, reports, rpath, par)
    else:
        for ff in sfn:
            reports = []
            lookinreports(ff, reports, reportsDict)
            lookforusages([], ff, [], reports, rpath, '-')


def lookinreports(file, reports, reportsDict):
    for k, v in reportsDict.items():
        if len(v) > 0:
            strinlist = ','.join([str(el) for el in v])
            if re.search(file, strinlist, re.IGNORECASE):
                reports.append(k)


def lookforusages(calledin, file, processed, reports, rpath, procDir):
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
                            if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include', ln,
                                                                                              re.IGNORECASE):
                                calledin.append(f)
    inrepstr = ','.join([str(el) for el in reports])
    inprocstr = ','.join([str(el) for el in calledin])
    if len(inrepstr) == 0:
        inrepstr = 'NOT FOUND'
    if len(inprocstr) == 0:
        inprocstr = 'NOT FOUND'


    print(f'{procDir};{file};{inprocstr};{inrepstr}')


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


if __name__ == '__main__':
    # checkRemaining(
    #     'C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\result.json')
    iterateDirectories('C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\', ['WB_PctBCCalculatePercentBCs'])
