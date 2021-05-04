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


def pprint_reverseTree(node, file=None, _prefix="", _last=True):
    printKey = "\u0332".join(node.key) if isinstance(node, Report) else node.key
    print(_prefix, "`- " if _last else "|- ", printKey, sep="", file=file)
    _prefix += "   " if _last else "|  "
    if not isinstance(node, Report):
        child_count = len(node.callers)
        for i, child in enumerate(node.callers):
            _last = i == (child_count - 1)
            pprint_reverseTree(child, file, _prefix, _last)
    else:
        pass


def pprint_tree(node, r, f, file=None, _prefix="", _last=True):
    print(r.key, _prefix, "`- " if _last else "|- ", "\u0332".join(node.key) if f == node.key else node.key, sep="",
          file=file)
    _prefix += "   " if _last else "|  "
    child_count = len(node.calling)
    for i, child in enumerate(node.calling):
        _last = i == (child_count - 1)
        pprint_tree(child, r, f, file, _prefix, _last)


def apply(file):
    reportsNodes = []
    processNodes = []
    processNodesStr = []
    createNodes(processNodes, processNodesStr)
    createReportNodes(processNodes, reportsNodes)
    for node in processNodes:
        for subNode in processNodes:
            for call in subNode.calling:
                if node.key.lower() == call.key.lower():
                    node.callers.append(subNode)
    for n in processNodes:
        if n.key.lower() == file.lower():
            pprint_reverseTree(n)


def createReportNodes(processNodes, reportNodes):
    processNodes.sort(key=lambda n: n.key, reverse=False)
    for reportKey, calledProcesses in readReportRef().items():
        curr = Report(reportKey)
        reportNodes.append(curr)
        processed = []
        for process in calledProcesses:
            if process not in processed:
                processed.append(process)
                procNode = None
                for n in processNodes:
                    if n.key.lower() == process.lower():
                        procNode = n
                        continue
                if procNode is not None:
                    curr.setNode(procNode)
                    procNode.setCaller(curr)


def createNodes(processNodes, processNodesStr):
    for r, d, fls in os.walk(
            'C:\\Farms\\DEPM-35267-WFB-Perf-Model-1204\\Projects\\AppEngine\\Sources\\Depm\\Processes\\'):
        for f in fls:
            fExt = pathlib.Path(f).suffix
            if fExt == '.bs' and f not in processNodesStr:
                node = ProcessNode(f)
                if node is None:
                    print('is None!')
                processNodes.append(node)
                processNodesStr.append(f)
                fPath = os.path.join(r, f)
                with open(fPath, 'r', encoding='UTF-8') as fr:
                    content = fr.readlines()
                    for ln in [li.strip('\n\r\t') for li in content]:
                        if re.search('#include', ln, re.IGNORECASE):
                            txt = re.split('\"', ln)
                            subNodeName = txt[1] + '.bs'
                            subNode = None
                            for n in processNodes:
                                if n.key.lower() == subNodeName.lower():
                                    subNode = n
                                    continue
                            if subNode is None:
                                subNode = ProcessNode(subNodeName)
                            if subNode is not None:
                                node.calling.append(subNode)


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


if __name__ == '__main__':
    apply('WB_ComputeAnnualFTE.bs')
