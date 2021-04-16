import os
import pathlib
import re


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


def fromReportsToProcess(rpath, checkProcess):
    dpath = 'C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\Workforce Budgeting\\'
    reports = readReportRef(rpath)
    found = {}
    for key, value in reports.items():
        processed = []
        for v in value:
            calls = [v]
            if v not in processed:
                lookforusages(v, dpath, calls, key)
                processed.append(v)
            if checkProcess in calls:
                found[key] = calls


def lookforusages(file, rpath, callst, report):
    for r, d, fls in os.walk(rpath):
        procDir = r.split('\\')[-2]
        if procDir != 'DEPMWorkforceAddIn':
            for f in fls:
                if f != file:
                    fExt = pathlib.Path(f).suffix
                    if fExt == '.bs':
                        fPath = os.path.join(r, f)
                        with open(fPath, 'r', encoding='UTF-8') as fr:
                            content = fr.readlines()
                            for ln in [li.strip('\n\r\t') for li in content]:
                                if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include', ln, re.IGNORECASE):
                                    if f not in callst:
                                        callst.append(f)
                                        lookforusages(f, rpath, callst, report)


if __name__ == '__main__':
    # checkRemaining(
    #     'C:\\Farms\\DEPM-35267-WFB-Perf-Model-2403\\result.json')
    # iterateDirectories('C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\', ['WB_CalculateAllActionsForEmployee.bs','WB_CalculateAllAssignmentsForEmployee.bs','WB_CalculateAllForOrg_Internal.bs','WB_CalculateFixedAmountBenefit.bs','WB_CalculatePremiumBenefit.bs','WB_CalculateSalaryAndDependenciesForEmployee.bs','WB_DeleteFixedAmountAction.bs','WB_DeletePremiumAction.bs','WB_PctBCActionCalculateAllAssigned.bs','WB_BCDefinitionDelete_Internal.bs','WB_PctBCActionDelete2.bs','WB_DeletePositionAssignment.bs','WB_ModifyAction.bs'])
    fromReportsToProcess('C:\\Farms\\2021-03-30\\2021-03-30\\processListSimple.txt', 'WB_PctBCCalculatePercentBCs.bs')
