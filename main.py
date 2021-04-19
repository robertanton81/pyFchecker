import json
import os
import pathlib
import re


def readReportRef():
    rpath = 'C:\\Farms\\2021-03-30\\2021-03-30\\processListSimple.txt'
    with open(rpath, 'r') as fr:
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


def fromReportsToProcess(checkProcess):
    reports = readReportRef()
    inReports = []
    for key, value in reports.items():
        for v in value:
            if v == checkProcess and key not in inReports:
                inReports.append(key)
    return inReports


def iterAllFiles(rootPath, checkFile=''):
    if checkFile != '':
        res = {checkFile: {}}
        reports = fromReportsToProcess(checkFile)
        res[checkFile]['reports'] = reports
        callstack = lookforusages(checkFile, rootPath)
        sub = []
        for el in callstack:
            expandedCallStack = [el]
            lookforusagesRecursive(el, rootPath, expandedCallStack)
            processSearchPrint(expandedCallStack, checkFile, sub)
            print(f'{checkFile};{";".join([el for el in expandedCallStack])}')

    else:
        for r, d, fls in os.walk(rootPath):
            processed = []
            for f in fls:
                if f not in processed:
                    fExt = pathlib.Path(f).suffix
                    if fExt == '.bs':
                        processed.append(f)
                        callstack = []
                        lookforusagesRecursive(f, rootPath, callstack)
                        processSearchPrint(callstack, f)


def processSearchPrint(callstack, f, subd):
    for caller in callstack:
        idx = callstack.index(caller)
        reports = fromReportsToProcess(caller)
        if len(reports) > 0:
            tmp = f'{caller} => reports;{";".join([e for e in reports])}'
            callstack.remove(caller)
            callstack.append(tmp)


def lookforusages(file, rootpath):
    callstack = []
    for r, d, fls in os.walk(rootpath):
        procDir = r.split('\\')[-2]
        if procDir not in ['DEPMWorkforceAddIn', 'Allocation Addon', 'B&P Add in', 'DEPMCapitalPlanning', 'Deprecated',
                           'OlapAPIExtension', 'DEPMDynamicAttributesAddin', 'DEPMDateTimeAddIn',
                           'DEPMGenericAllocationAddin',
                           'WDDataUploadAddIn', 'DEPMWorkflowAddin', 'DEPMWorkforceDesignAddIn']:
            for f in fls:
                if f != file and f not in callstack:
                    fExt = pathlib.Path(f).suffix
                    if fExt == '.bs':
                        fPath = os.path.join(r, f)
                        with open(fPath, 'r', encoding='UTF-8') as fr:
                            content = fr.readlines()
                            for ln in [li.strip('\n\r\t') for li in content]:
                                if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include', ln,
                                                                                                  re.IGNORECASE):
                                    callstack.append(f)
    return callstack


def lookforusagesRecursive(file, rootpath, callstack):
    for r, d, fls in os.walk(rootpath):
        procDir = r.split('\\')[-2]
        if procDir not in ['DEPMWorkforceAddIn', 'Allocation Addon', 'B&P Add in', 'DEPMCapitalPlanning', 'Deprecated',
                           'OlapAPIExtension', 'DEPMDynamicAttributesAddin', 'DEPMDateTimeAddIn',
                           'DEPMGenericAllocationAddin',
                           'WDDataUploadAddIn', 'DEPMWorkflowAddin', 'DEPMWorkforceDesignAddIn']:
            for f in fls:
                if f != file and f not in callstack:
                    fExt = pathlib.Path(f).suffix
                    if fExt == '.bs':
                        fPath = os.path.join(r, f)
                        with open(fPath, 'r', encoding='UTF-8') as fr:
                            content = fr.readlines()
                            for ln in [li.strip('\n\r\t') for li in content]:
                                if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include', ln,
                                                                                                  re.IGNORECASE):
                                    callstack.append(f)
                                    lookforusagesRecursive(f, rootpath, callstack)


if __name__ == '__main__':
    # checkRemaining(
    #     'C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\result.json')
    # iterateDirectories('C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\', ['WB_CalculateAllActionsForEmployee.bs','WB_CalculateAllAssignmentsForEmployee.bs','WB_CalculateAllForOrg_Internal.bs','WB_CalculateFixedAmountBenefit.bs','WB_CalculatePremiumBenefit.bs','WB_CalculateSalaryAndDependenciesForEmployee.bs','WB_DeleteFixedAmountAction.bs','WB_DeletePremiumAction.bs','WB_PctBCActionCalculateAllAssigned.bs','WB_BCDefinitionDelete_Internal.bs','WB_PctBCActionDelete2.bs','WB_DeletePositionAssignment.bs','WB_ModifyAction.bs'])
    # fromReportsToProcess('C:\\Farms\\2021-03-30\\2021-03-30\\processListSimple.txt', 'WB_PctBCCalculatePercentBCs.bs')
    iterAllFiles(
        'C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\', 'WB_CalculateAllActionsForEmployee.bs')
