import os
import json


def iterateDirectories(rpath):
    reportlistpath = 'C:\\Users\\ranton\\Downloads\\2021-03-30\\2021-03-30\\processListSimple.txt'
    reportsDict = readReportRef(reportlistpath)

    processes = {}

   

    for folder in os.scandir(rpath):
        if folder.name not in ['DEPMWorkforceAddIn']:
            files = os.scandir(folder.path)
            for f in files:
                reports = []
                processes[f.name] = {'reports': reports, 'callsTo': {}}
                for k, v in reportsDict.items():
                    if f.name in v:
                        reports.append(k)
                with open(f.path, 'r') as fr:
                    content = fr.readlines()
                    for ln in [li.strip('\n\r\t') for li in content]:
                        if ln.startswith('#include'):
                            calledProcess = ln.split("\"")[1] + '.bs'
                            calls = findUsages(calledProcess, rpath)
                            processes[f.name]['callsTo'][calledProcess] = calls

    with open(os.path.join('C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\', 'result.json'), 'w') as outFile:
        json.dump(processes, outFile)


def findUsages(procFile, rpath):
    usedprocesses = [procFile]
    for folder in os.scandir(rpath):
        if folder.name != "DEPMWorkforceAddIn":
            files = os.scandir(folder.path)
            for file in files:
                if file.name == procFile:
                    with open(file.path, 'r') as fr:
                        content = fr.readlines()
                        for ln in [li.strip('\n\r\t') for li in content]:
                            if ln.startswith('#include'):
                                calledProcess = ln.split("\"")[1] + '.bs'
                                usedprocesses.append(calledProcess)
                                # usedprocesses = f'{usedprocesses} => {calledProcess}'
                                findUsages(calledProcess, rpath)
    return usedprocesses


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
    checkRemaining(
        'C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\result.json')
    # iterateDirectories('C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\Projects\\AppEngine\\Sources\\Depm\\Processes\\Workforce Budgeting\\')
