import json
import os
import pathlib
import re


class Report:
    def __init__(self, key):
        self.key = key
        self.nodes = []

    def setNode(self, node):
        self.nodes.append(node)


class ProcessNode:
    def __init__(self, key):
        self.key = key
        self.callers = []
        self.calling = []

    def setCaller(self, caller):
        self.callers.append(caller)

    def set_calling(self, calling):
        self.calling.append(calling)

    # def __str__(self, level=0):
    #     ret = "\n"*level+repr(self.key)
    #     for node in self.calling:
    #         ret += node.__str__(level+1)
    #     return ret
    #
    # def __repr__(self):
    #     return '<tree rep>'


globalReportsNodes = []
globalProcessNodes = []
globalProcessNodesStr = []


def processAll(file):
    setNodes()
    setReports()
    for r in globalReportsNodes:
        for n in r.nodes:
            stack = []
            pprint_tree_v(n, r, stack)
            if file in stack:
                pprint_tree(n, r, file)


def pprint_tree_v(node, r, stack, file=None, _prefix="", _last=True):
    # print(_prefix, "`- " if _last else "|- ", node.key, sep="", file=file)
    # _prefix += "   " if _last else "|  "
    child_count = len(node.calling)
    for i, child in enumerate(node.calling):
        _last = i == (child_count - 1)
        stack.insert(0, child.key)
        pprint_tree_v(child, r, stack, file, _prefix, _last)


def pprint_tree(node, r, f, file=None, _prefix="", _last=True):
    print(r.key, _prefix, "`- " if _last else "|- ", "\u0332".join(node.key) if f == node.key else node.key, sep="", file=file)
    _prefix += "   " if _last else "|  "
    child_count = len(node.calling)
    for i, child in enumerate(node.calling):
        _last = i == (child_count - 1)
        pprint_tree(child, r, f, file, _prefix, _last)


def setReports():
    globalProcessNodes.sort(key=lambda n: n.key, reverse=False)
    for reportKey, calledProcesses in readReportRef().items():
        curr = Report(reportKey)
        globalReportsNodes.append(curr)
        processed = []
        for process in calledProcesses:
            if process not in processed:
                processed.append(process)
                procNode = None
                for n in globalProcessNodes:
                    if n.key.lower() == process.lower():
                        procNode = n
                        continue
                if procNode is not None:
                    curr.setNode(procNode)
                    procNode.setCaller(curr)


def setNodes():
    for r, d, fls in os.walk(
            'C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\'):
        procDir = r.split('\\')[-2]
        # if procDir not in ['DEPMWorkforceAddIn', 'Allocation Addon', 'B&P Add in', 'DEPMCapitalPlanning', 'Deprecated',
        #                    'OlapAPIExtension', 'DEPMDynamicAttributesAddin', 'DEPMDateTimeAddIn',
        #                    'DEPMGenericAllocationAddin',
        #                    'WDDataUploadAddIn', 'DEPMWorkflowAddin', 'DEPMWorkforceDesignAddIn']:
        for f in fls:
            fExt = pathlib.Path(f).suffix
            if fExt == '.bs' and f not in globalProcessNodesStr:
                fPath = os.path.join(r, f)
                node = ProcessNode(f)
                if node is None:
                    print('is None!')
                globalProcessNodes.append(node)
                globalProcessNodesStr.append(f)
                with open(fPath, 'r', encoding='UTF-8') as fr:
                    content = fr.readlines()
                    for ln in [li.strip('\n\r\t') for li in content]:
                        if re.search('#include', ln, re.IGNORECASE):
                            txt = re.split('\"', ln)
                            subNodeName = txt[1] + '.bs'
                            subNode = None
                            for n in globalProcessNodes:
                                if n.key.lower() == subNodeName.lower():
                                    subNode = n
                                    break
                            else:
                                subNode = ProcessNode(subNodeName)
                            if subNode is not None:
                                subNode.callers.append(node)
                                node.calling.append(subNode)



def reportCallStacksClasses():
    for reportKey, calledProcesses in readReportRef().items():
        curr = Report(reportKey)
        processed = []
        processNodes = []
        for process in calledProcesses:
            if process not in processed:
                processNode = ProcessNode(process, curr)
                curr.nodes.append(processNode)
        for node in processNodes:
            calls(node)


def calls(processNode):
    pass


def readReportRef():
    rpath = '.\\assets\\processListSimple.txt'
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


def reportCallStacks():
    res = {}
    for reportKey, calledProcesesses in readReportRef().items():
        processed = []
        res[reportKey] = []
        for process in calledProcesesses:
            if process not in processed:
                processed.append(process)
                calls = [process]
                lookforusages(
                    'C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\',
                    process, calls)
                # print(f'{reportKey};{";".join([el for el in calls])}')
                res[reportKey].append(calls)

    # with open('data.txt', 'w') as outfile:
    #     json.dump(res, outfile)


def lookforusages(rpath, file, callsTack):
    for r, d, fls in os.walk(rpath):
        procDir = r.split('\\')[-2]
        if procDir != 'DEPMWorkforceAddIn':
            for f in fls:
                if f != file and f not in callsTack:
                    fExt = pathlib.Path(f).suffix
                    if fExt == '.bs':
                        fPath = os.path.join(r, f)
                        with open(fPath, 'r', encoding='UTF-8') as fr:
                            content = fr.readlines()
                            for ln in [li.strip('\n\r\t') for li in content]:
                                if re.search(file.split('.')[0], ln, re.IGNORECASE) and re.search('#include', ln,
                                                                                                  re.IGNORECASE):
                                    callsTack.append(f)
                                    lookforusages(rpath, f, callsTack)


def checkProcess(process):
    with open('data.txt') as reportsDict:
        data = json.load(reportsDict)
        for report, callStacks in data.items():
            for calls in callStacks:
                if process in calls:
                    for call in calls:
                        print(report + ";" + call)


if __name__ == '__main__':
    # reportCallStacks()
    # checkProcess('WB_ComputeAnnualFTE.bs')
    # reportCallStacksClasses()
    processAll('WB_ComputeAnnualFTE.bs')
