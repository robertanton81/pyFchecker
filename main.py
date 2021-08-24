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


def pprint_reverseTree(node, level, file=None, _prefix="", _last=True, _counter=-1):
    printKey = "\u0332".join(node.key) if isinstance(
        node, Report) else node.key
    print(_prefix, "`- " if _last else "|- ", printKey, sep="", file=file)
    _prefix += "   " if _last else "|  "
    if not isinstance(node, Report):
        _counter += 1
        child_count = len(node.callers)
        for i, child in enumerate(node.callers):
            if _counter == level:
                break
            _last = i == (child_count - 1)
            pprint_reverseTree(child,
                               level,
                               file,
                               _prefix,
                               _last,
                               _counter,)
    else:
        pass


def apply(file, path, level=99999999):
    reportsNodes = []
    processNodes = []
    processNodesStr = []
    createNodes(processNodes, processNodesStr, path)
    createReportNodes(processNodes, reportsNodes)
    for node in processNodes:
        for subNode in processNodes:
            for call in subNode.calling:
                if node.key.lower() == call.key.lower():
                    node.callers.append(subNode)
    for n in processNodes:
        if n.key.lower() == file.lower():
            pprint_reverseTree(n, level)


def get_obsolete(path):
    reportsNodes = []
    processNodes = []
    processNodesStr = []
    createNodes(processNodes, processNodesStr, path)
    createReportNodes(processNodes, reportsNodes)
    for node in processNodes:
        for subNode in processNodes:
            for call in subNode.calling:
                if node.key.lower() == call.key.lower():
                    node.callers.append(subNode)
    for n in processNodes:
        if len(n.callers) == 0:
            pprint_reverseTree(n, 999999999999)


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


def createNodes(processNodes, processNodesStr, path):
    for r, d, fls in os.walk(path):
        for f in fls:
            fExt = pathlib.Path(f).suffix
            if fExt == ".bs" and f not in processNodesStr:
                node = ProcessNode(f)
                if node is None:
                    print("is None!")
                processNodes.append(node)
                processNodesStr.append(f)
                fPath = os.path.join(r, f)
                with open(fPath, "r", encoding="UTF-8") as fr:
                    content = fr.readlines()
                    for ln in [li.strip("\n\r\t") for li in content]:
                        if re.search("#include", ln, re.IGNORECASE):
                            txt = re.split('"', ln)
                            subNodeName = txt[1] + ".bs"
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
    rpath = ".\\sources\\processListSimple.txt"
    with open(rpath, "r") as fr:
        content = fr.readlines()
        curr = ""
        repsDict = {}
        for ln in [li.strip("\n\r") for li in content]:
            if not ln.startswith("\t"):
                if ln not in repsDict and ln != "":
                    repsDict[ln] = []
                    curr = ln
            elif ln.startswith("\t") and curr != "":
                repsDict[curr].append(ln.strip("\t")[1:-1] + ".bs")
        return repsDict


if __name__ == "__main__":
    # TODO: needs to match correct path to bs files
    path = "C:\\Farms\\WFB_0207_model\\Projects\\AppEngine\\Sources\\Depm\\Processes\\"

    # this finds all calls to the bs process (.bs file)
    # TODO: to limit number of levels, add third argument (int)
    apply("WB_AttributeChangedAssignment_Internal.bs", path)

    # TODO: this should print all unreferenced bs files
    # get_obsolete(path)
