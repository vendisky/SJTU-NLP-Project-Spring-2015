from stat_parser import Parser, display_tree
from pprint import pprint
import Tkinter
from time import time
import sys
import config



""" Some data """
VBList = [u'MD', u'VB', u'VBD', u'VBG', u'VBN', u'VBP', u'VBZ']
NNList = [u'PRP', u'PRP$', u'NN', u'NNS', u'NNP', u'NNPS']   # what about u'PRP$' ?
MDList = ['can', 'could', 'may', 'might', 'must', 'need', 'dare', 'dared', 'shall', 'should', 'will', 'would', "'ll", "'d"]
NotFollowVBZList = ['am', 'are', 'is', "'m", "'re", "'s", 'was', 'were', 'to', 'please', 'has', 'have', 'been', 'had', 'not', "n't", "already"]
CCRBList = [u'CC', u'RB', u'RBR', u'RBS', u'RP']
WHList = [u'WHADJP', u'WHADVP', u'WHNP', u'WHPP']

PRPThirdList = ['he', 'she', 'it', 'this', 'that']
PRPSecondList = ['we','you','they','these', 'those']

BEList = ['am', 'are', 'is', "'m", "'re", "'s", 'was', 'were']



""" global variables """
code = 0
nodeNum = 0
errorCode = []
nodeList = []
firstVBNN = []
firstNNVB = []
found = 0
sqFlag = 0
gqFlag = 0
NNNode = []
VBNode = []



""" TreeNode data structure """
class node:   
    def __init__(self, data):
        self._data = data
        self._children = []
        self._parent = None
        self._childNum = 0
        self._code = 0
        self._visited = 0
        self._desNum = 0
 
    def getData(self):
        return self._data
 
    def getChildren(self):
        return self._children
    
    def getParent(self):
        return self._parent
    
    def getChildNum(self):
        return self._childNum

    def getLeftChild(self):
        return self._children[0]

    def getRightChild(self):
        return self._children[self._childNum-1]

    def getLeftMostChild(self):
        if self.isLeaf():
            return self
        else:
            leftMostNode = self
            while not leftMostNode.isLeaf():
                leftMostNode = leftMostNode.getLeftChild()
            return leftMostNode

    def getRightMostChild(self):
        if self.isLeaf():
            return self
        else:
            rightMostNode = self
            while not rightMostNode.isLeaf():
                rightMostNode = rightMostNode.getRightChild()
            return rightMostNode

    def getCode(self):
        return self._code

    def getVisited(self):
        return self._visited

    def getDesNum(self):
        return self._desNum
 
    def addChild(self, node):
        self._children.append(node)
        self._childNum += 1

    def setParent(self, node):
        self._parent = node

    def setData(self, data):
        self._data = data

    def setCode(self, num):
        self._code = num

    def setVisited(self):
        self._visited = 1

    def addDesNum(self, num):
        self._desNum += num

    def isLeaf(self):
        return type(self._data)==str



""" transform list to "tree of node" """
def trans(arr):
    root = node(arr[0])

    if not isinstance(arr[1], list):                # different type
        tmp = node(arr[1])
        tmp.setParent(root)
        root.addChild(tmp)

    else:
        for subArr in arr[1:]:
            tmp = trans(subArr)
            tmp.setParent(root)
            root.addChild(tmp)

    return root



""" assign code & create nodeList & change VB & changeNNS"""
def assignCode(root):
    if root.isLeaf():
        global code, nodeList
        root.setCode(code)
        code += 1
        nodeList.append(root)

        last = len(root.getData())-1
        if root.getData()[last]=='s' and root.getParent().getData() in [u'VB', u'VBP']:
            root.getParent().setData(u'VBZ')

        if root.getParent().getData()==u'VBN' and root.getCode()>0 and nodeList[root.getCode()-1].getData() not in ['have', 'has', 'had', 'been', 'already']:
            if root.getData()[last]=='d':
                root.getParent().setData(u'VBD')
            else:
                root.getParent().setData(u'VB')

        if root.getData()[last]=='s' and root.getParent().getData() in [u'NN', u'NNP']:
            root.getParent().setData(u'NNS')
        return

    for node in root.getChildren():
        assignCode(node)



""" assign descendant num for each node """
def assignDesNum(root):
    if root.isLeaf():
        root.addDesNum(1)
        return 1

    for node in root.getChildren():
        tmpNum = assignDesNum(node)
        root.addDesNum(tmpNum)

    return root.getDesNum()
        


""" print the tree label with indentation """
def dfsIndent(root,depth):
    print ' '*depth + root.getData()
    for node in root.getChildren():
        dfsIndent(node,depth+1)



""" print all verb and MD """
def printVB(root):
    if root.isLeaf():
        if root.getParent().getData() in VBList:
            print root.getParent().getData(), ': ', root.getData(), root.getCode()+1, '\t',
        return

    else:
        for node in root.getChildren():
            printVB(node)



""" Pre-Check the node List """
def preCheck():
    global nodeNum
    nodeNum = len(nodeList)
    
    for i in range(nodeNum-1):
        node1 = nodeList[i]
        node2 = nodeList[i+1]
        if node2.getParent().getData()==u'RB' and i+2<nodeNum:
            node2 = nodeList[i+2]
        if (node1.getData().lower() in (MDList + NotFollowVBZList)) and (node2.getParent().getData()==u'VBZ'):
            errorCode.append(node2.getCode())



""" Skip CC and RB """
def skipCCRB():
    index = 0
    while nodeList[index].getParent().getData() in CCRBList:
        index += 1
    return index
            


""" Check if the sentence is subject clause """
def isSubjectClause():
    index = skipCCRB()
    node = nodeList[index]
    if (node.getParent().getParent().getData() in WHList) and nodeList[nodeNum-1].getData()=='.':
        tmpList = ['need', 'to']
        global errorCode
        for code in errorCode:
            if nodeList[code-1].getData() in tmpList:
                errorCode.remove(code)                      # "What we need is..." conflicts, "what we belongs to is..." conflicts
        if config.print_sentence_type:
            print 'Subject Clause'
        return 1
    return 0



""" Check if the sentence is there-be """
def isThereBe():
    index = skipCCRB()
    node = nodeList[index]
    if node.getParent().getData() == u'EX':
        if config.print_sentence_type:
            print 'There-be Pattern'
        return 1
    return 0



""" Find the first VB & NP """
def findFirstVBNN(root):
    if root.isLeaf():
        return

    for i in range(root.getChildNum()-1):
        node1 = root.getChildren()[i]
        node2 = root.getChildren()[i+1]

        if node2.getData() == u'RB' and root.getChildNum()>i+2:                                      # skip "not", "why isn't him?", "why don't you save me?", "don't you think so?"
            node2 = root.getChildren()[i+2]
            
        if (node1.getData() in VBList or node1.getData()==u'S+VP') and (node2.getData()==u'NP'):
            global found, firstVBNN
            if not found:                                                       # give up on case "You and I" or "You, he and I", too complicated
                found = 1
                firstVBNN.append(node1.getLeftMostChild())
                firstVBNN.append(node2.getRightMostChild())

    for node in root.getChildren():
        if not found:
            findFirstVBNN(node)



""" Find the first NP & VP """
def findFirstNNVB(root):                                                        # can not deal with case "Could the teacher in classroom say that again?"
    if root.isLeaf():
        return

    for i in range(root.getChildNum()-1):
        node1 = root.getChildren()[i]
        node2 = root.getChildren()[i+1]
        if node2.getData()==u'ADVP' and i+2<root.getChildNum():
            node2 = root.getChildren()[i+2]
        if node1.getData()==u'NP' and (node2.getData()==u'VP' or node2.getData() in VBList):
            # node1.setVisited()
            # node2.setVisited()
            global found, firstNNVB
            if not found:
                found = 1
                firstNNVB.append(node1.getRightMostChild())
                firstNNVB.append(node2.getLeftMostChild())
    
    for node in root.getChildren():
        if not found:
            findFirstNNVB(node)



""" Check if the sentence is special question """
def specialQuestion(root):
    index = skipCCRB()
    node = nodeList[index]
    
    if node.getParent().getParent().getData() in WHList:
        if config.print_sentence_type:
            print 'Special Question'
            global sqFlag
            sqFlag = 1
    else:
        return

    global found
    found = 0
    findFirstVBNN(root)

    found = 0
    findFirstNNVB(root)

    global firstVBNN, firstNNVB
    if firstVBNN and firstNNVB and (not firstVBNN[1]==firstNNVB[0]):
        firstNNVB = []
    

    
""" Check if the sentence is special question """
def generalQuestion(root):
    index = skipCCRB()
    node = nodeList[index]

    if (node.getParent().getData() in VBList) and nodeList[nodeNum-1].getData()=='?':
        if config.print_sentence_type:
            print 'General Question'
            global gqFlag
            gqFlag = 1
    else:
        return

    global found
    found = 0
    findFirstVBNN(root)

    found = 0
    findFirstNNVB(root)

    global firstVBNN, firstNNVB
    if firstVBNN and firstNNVB and (not firstVBNN[1]==firstNNVB[0]):
        firstNNVB = []



""" Find NP + SBAR """
def findNPSBAR(root):
    if root.isLeaf():
        return

    for i in range(root.getChildNum()-1):
        node1 = root.getChildren()[i]
        node2 = root.getChildren()[i+1]
        if (node1.getData() in [u'NP', u'PP'] or node1.getData() in NNList) and node2.getData()==u'SBAR':                     # PP, "in that factory that"
            # node1.setVisited()
            # node2.setVisited()
            if (node2.getChildren()[0].getData() in WHList or node2.getChildren()[0].getData() == 'IN') and (node2.getChildren()[1].getData()[0]==u'S'):    # IN means that
                sNode = node2.getChildren()[1]
                if sNode.getChildren()[0].getData() in VBList or sNode.getChildren()[0].getData()==u'VP':       # VP, had never seen before
                    if config.print_sentence_type:
                        print 'Attributive Clause II'

                    NNNode.append(node1.getRightMostChild())
                    VBNode.append(sNode.getChildren()[0].getLeftMostChild())

    for node in root.getChildren():
        findNPSBAR(node)

                    
                    
""" Check if the sentence is attributive clause """
def attributiveClause(root):
    """ case 1: root -> NP + SBAR + VP """
    if root.getChildNum()>=3 and root.getChildren()[0].getData()==u'NP' and root.getChildren()[1].getData()==u'SBAR' and root.getChildren()[2].getData()==u'VP':
        if config.print_sentence_type:
            print 'Attributive Clause I'

        # root.getChildren()[0].setVisited()
        # root.getChildren()[2].setVisited()
        NNNode.append(root.getChildren()[0].getRightMostChild())
        VBNode.append(root.getChildren()[2].getLeftMostChild())

    """ case 2, NP + SBAR """
    findNPSBAR(root)



""" Find noun and verb """
def findNPVP(root):
    if root.isLeaf():
        return

    for i in range(root.getChildNum()-1):
        node1 = root.getChildren()[i]
        node2 = root.getChildren()[i+1]
        if node2.getData()==u'ADVP' and i+2<root.getChildNum():
            node2 = root.getChildren()[i+2]
        if node1.getData()==u'NP' and (node2.getData()==u'VP' or node2.getData() in VBList):
            # if node1.getVisited() or node2.getVisited():
                # continue
            NNNode.append(node1.getRightMostChild())
            VBNode.append(node2.getLeftMostChild())

    for node in root.getChildren():
        findNPVP(node)

        
             
""" Total Check """
def totalCheck(root):
    """ Cannot deal with these 2 cases, so just give up """
    if isSubjectClause():
        return

    if isThereBe():
        return

    specialQuestion(root)

    generalQuestion(root)
    
    attributiveClause(root)

    findNPVP(root)



""" main function """
def main():
    time1 = time()
    parser = Parser()

    inFile = sys.argv[1]
    outFile = sys.argv[2]
    f = open(outFile,'w+')
    
    for line in open(inFile):
        if config.print_line: 
            print line

        global code, errorCode, nodeList, nodeNum, firstVBNN, firstNNVB, found, sqFlag, gqFlag, NNNode, VBNode
        code = 0
        nodeNum = 0
        errorCode = []
        nodeList = []
        firstVBNN = []
        firstNNVB = []
        found = 0
        sqFlag = 0
        gpFlag = 0
        NNNode = []
        VBNode = []
            
        wordNum = len(line.split())
        if config.print_word_num:
            print 'Word Num: ', wordNum

        if config.ignore_long_sentence and wordNum>config.max_word_num:
            # print 'Long Sentence'
            # print '\n'*2
            # print -1, line,
            f.write(str(-1) + ' ' + line)
            continue 

        try:
            start = time()
            indentTree = parser.raw_parse(line)     # raw parse for indent tree list
            end = time()
        except:
            # print 'Parsing Error'
            # print '\n'*2
            # print -1, line,
            f.write(str(-1) + ' ' + line)
            continue

        if config.print_parse_time:
            print 'Raw Parse Time: ', end-start, 's'
        
        if config.print_indent_tree:
            pprint(indentTree)                      # unit test

        root = trans(indentTree)                    # recursively transform list to "tree of node"
        assignCode(root)
        assignDesNum(root)
        
        if config.dfs_indent:
            dfsIndent(root,0)                       # unit test

        if config.print_node_list:                  # unit test
            for node in nodeList:
                print node.getData(), '\t',
            print
        
        if config.show_nltk_tree:
            start = time()
            nlktTree = parser.parse(line)           # nlktTree, could be drawn into graph
            end = time()
            print 'NLKT Tree Parse Time: ', end-start, 's'
            display_tree(nlktTree)                  # unit test

        """ Now the check begins! """
        preCheck()
        totalCheck(root)

        """ If there is some NP+VP left """
        for i in range(len(nodeList)-1):
            node1 = nodeList[i]
            node2 = nodeList[i+1]
            if node2.getParent().getData() == u'RB' and i+2<len(nodeList):
                node2 = nodeList[i+2]
            if node1.getParent().getData() in NNList and node2.getParent().getData() in VBList:
                if (node1 in NNNode and node2 in VBNode) or (firstNNVB and (node1==firstNNVB[0] and node2==firstNNVB[1])):
                    pass
                else:
                    NNNode.append(node1)
                    VBNode.append(node2)

        """ Be Check """
        for i in range(len(nodeList)-1):
            node1 = nodeList[i]
            node2 = nodeList[i+1]
            if node2.getParent().getData() == u'RB' and i+2<len(nodeList):
                node2 = nodeList[i+2]
            if node1.getData().lower() == 'i':
                if node2.getData() in BEList and node2.getData() not in ['am', 'was',"'m"]:
                    errorCode.append(node2.getCode())
            elif node1.getData().lower() in PRPSecondList:
                if node2.getData() in BEList and node2.getData() not in ['are', 'were',"'re"]:
                    errorCode.append(node2.getCode())
            elif node1.getData().lower() in PRPThirdList:
                if node1.getData().lower()=='that':
                    if i>0 and nodeList[i-1].getParent().getData() in NNList:
                        continue
                if node2.getData() in BEList and node2.getData() not in ['is', 'was',"'s"]:
                    errorCode.append(node2.getCode())
            else:
                pass

        """ del duplicates """
        if firstNNVB:
            n = firstNNVB[0]
            v = firstNNVB[1]
            if n in NNNode and v in VBNode:
                NNNode.remove(n)
                VBNode.remove(v)
                

        """ replace RB with the word after (Maybe VB) """
        if firstNNVB:
            v = firstNNVB[1]
            if v.getParent().getData()==u'RB':
                code = v.getCode()
                new = nodeList[code+1]
                if new.getParent().getData() in VBList:
                    firstNNVB[1] = new
                else:
                    pass

        for v in VBNode:
            if v.getParent().getData()==u'RB':
                code = v.getCode()
                new = nodeList[code+1]
                if new.getParent().getData() in VBList:
                    VBNode[VBNode.index(v)] = new
                else:
                    pass

        """ print dependencies """
        if config.print_npvp:
            print 'FROM ERRORCODE:'
            for i in errorCode:
                print nodeList[i].getData(), '\t',
            print

            print 'FROM QUESTION:'
            for node in firstVBNN:
                print node.getData()
            for node in firstNNVB:
                print node.getData()
            print

            print 'FROM NPVP & OTHERS:'
            for i in range(len(NNNode)):
                print NNNode[i].getParent().getData(), NNNode[i].getData(), '\t', VBNode[i].getParent().getData(), VBNode[i].getData()
            print

        """ canonicalize """
        if firstVBNN:
            if not (firstVBNN[0].getParent().getData() in VBList and firstVBNN[1].getParent().getData() in NNList):
                firstVBNN = []

        if firstNNVB:
            if not (firstNNVB[1].getParent().getData() in VBList and firstNNVB[0].getParent().getData() in NNList):
                firstNNVB = []

        for v in VBNode:
            i = VBNode.index(v)
            if not (NNNode[i].getParent().getData() in NNList and VBNode[i].getParent().getData() in VBList):
                del NNNode[i]
                del VBNode[i]
        

        """ Finally! We add codes! """
        if config.print_standard_answer:
            """ FROM QUESTION """
            if sqFlag or gqFlag:
                if firstVBNN:
                    v = firstVBNN[0]
                    n = firstVBNN[1]
                    if n.getData().lower() in PRPThirdList or n.getParent().getData() in [u'NN', u'NNP']:       # single noun
                        if v.getParent().getData() in [u'VB', u'VBP']:
                            errorCode.append(v.getCode())
                    else:
                        if v.getParent().getData()==u'VBZ':
                            errorCode.append(v.getCode())

                    if firstNNVB:
                            v = firstNNVB[1]
                            if v.getParent().getData()==u'VBZ':
                                errorCode.append(v.getCode())

                else:
                    if firstNNVB:
                        if not (firstNNVB[0] in NNNode and firstNNVB[1] in VBNode):
                            NNNode.append(firstNNVB[0])
                            VBNode.append(firstNNVB[1])

            """ FROM NPVP & OTHERS """
            for i in range(len(NNNode)):
                n = NNNode[i]
                v = VBNode[i]
                if n.getData().lower() in PRPThirdList or n.getParent().getData() in [u'NN', u'NNP']:       # single noun
                    if v.getParent().getData() in [u'VB', u'VBP']:
                        errorCode.append(v.getCode())
                else:
                    if v.getParent().getData()==u'VBZ':
                        errorCode.append(v.getCode())

            errorCode = list(set(errorCode))
            errorCode.sort()
            if errorCode:
                for i in errorCode:
                    # print i+1,
                    f.write(str(i+1) + ' ')
            else:
                # print -1,
                f.write(str(-1) + ' ')
            # print line,
            f.write(line)


        if config.print_vb:
            printVB(root)                           # print all verb and MD in tree
            print

        if config.print_empty_line:
            print '\n'*2

    time2 = time()
    if config.print_total_time:
        print 'Total Execution Time: ', time2-time1, 's'
        
    if config.show_nltk_tree:
        Tkinter._test()                             # show the nlktTree graph

main()
