# coding:utf-8
from numpy import *
import sys
sys.setrecursionlimit(10000)
import time

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode  # needs to be updated
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind=1):
        print ' ' * ind, self.name, ' ', self.count
        for child in self.children.values():
            child.disp(ind +1 )


#test

def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        if frozenset(trans) in retDict.keys():
            retDict[frozenset(trans)] += 1
        else:
            retDict[frozenset(trans)]=1
    return retDict



####统计个元素出现的次数
def createTree(dataSet,minSup = 1):
    headerTable = {}
    for trans in dataSet:
        # print trans
        for item in trans:
            headerTable[item] = headerTable.get(item,0) + dataSet[trans]#记录每个元素项出现的频度
####删除小于minSup的元素
    # print headerTable
    for k in headerTable.keys():
        if headerTable[k] < minSup:
            del(headerTable[k])
    # freqItemSet = set(headerTable.keys())
    freqItemSet = frozenset(headerTable.keys())
    # print freqItemSet
    if len(freqItemSet) == 0:#不满足最小值支持度要求的除去
        return None,None
    for k in headerTable:
        headerTable[k] = [headerTable[k],None]
    # print headerTable
    retTree = treeNode('Null Set', 1, None)
    for tranSet,count in dataSet.items():
        localD={}
        # print tranSet,count
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            ###按照localD中项集次数p:p[1]的降序reverse=True来排列
            orderedItems = [v[0] for v in sorted(localD.items(),key = lambda p:p[1],reverse = True)]
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable
def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


def ascendTree(leafNode, prefixPath):  # ascends from leaf node to root
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

####根据headtable生成 【a,b,c,d】到e的各个子集及次数 次数是headtable的元素count
def findPrefixPath(basePat, treeNode):  # treeNode comes from header table
    condPats = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats
def mineTree(inTree, headerTable, minSup, preFix, freqItemList,maxlength):
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1])]#(sort header table)
    # print "bigl %s" % bigL
    for basePat in bigL:
        newFreqSet = preFix.copy()
        # newFreqSet = preFix
        newFreqSet.add(basePat)
        # newFreqSet=frozenset(newFreqSet)
        freqItemList.append(frozenset(newFreqSet))
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(condPattBases, minSup)
        if myHead != None:
            if len(freqItemList)<=maxlength:
                mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemList,maxlength)

def get_support_data(data_set, Ck, min_support, support_data):
    '''

    :param data_set: the whole data
    :param Ck: the fluenqucy itemset
    :param min_support: min support %
    :param support_data: value to return
    :return:
    '''
    # Lk = set()
    item_count = {}
    for t in data_set:
        for item in Ck:
            # print item
            if item.issubset(t):
                if item not in item_count:
                    item_count[item] = 1
                else:
                    item_count[item] += 1
    t_num = float(len(data_set))
    for item in item_count:
        if (item_count[item] / t_num) >= min_support:
            # Lk.add(item)
            support_data[item] = item_count[item] / t_num
    print support_data
    return support_data


def generate_big_rules(L, support_data, min_conf):
    """
    Generate big rules from frequent itemsets.
    Args:
        L: The list of Lk.
        support_data: A dictionary. The key is frequent itemset and the value is support.
        min_conf: Minimal confidence.
    Returns:
        big_rule_list: A list which contains all big rules. Each big rule is represented
                       as a 3-tuple.
    """
    big_rule_list = []
    sub_set_list = []
    for i in L:
        # for freq_set in L[i]:
        for sub_set in sub_set_list:
            if sub_set.issubset(i):
                # print i
                # # print sub_set
                # print i - sub_set
                # print '######'
                conf = support_data[i] / support_data[i - sub_set]
                conf_opp = support_data[i] / support_data[sub_set]
                kulc = (conf + conf_opp) / 2
                lift = conf / support_data[i - sub_set]
                ir = abs(support_data[i - sub_set]-support_data[sub_set])/(support_data[i - sub_set]+support_data[sub_set]-support_data[i])
                big_rule = (i - sub_set, sub_set, conf, kulc, lift, ir)
                if conf >= min_conf and big_rule not in big_rule_list:
                    # print freq_set-sub_set, " => ", sub_set, "conf: ", conf
                    big_rule_list.append(big_rule)
        sub_set_list.append(i)
    # print sub_set_list
    return big_rule_list
if __name__=='__main__':
    print int(time.time())
    ##输入 数据文件
    infile=sys.argv[1]
    # infile='D:\\fp-data.csv'
    ###存储频繁项集
    # out1='d:\\1.txt'
    out1=sys.argv[2]
    ###存储满足条件的结果
    out2='d:\\2.txt'
    # minsupp=2
    ##最小支持度 int 挖掘频繁项集时使用的，下面还有一个apriori算法打印最小置信度使用的百分比
    minsupp=sys.argv[3]
    ###频繁项集的最大长度
    maxlength=sys.argv[4]
    # maxlength=3
    datas=[]
    output=open(out1,'w')
    outputresult=open(out2,'w')
    with open(infile,'r') as f:
        for line in f.readlines():
            line=line.strip()
            line=line.split(',')
            line = list(filter(None, line))
            datas.append(line)
    dataset = createInitSet(datas)
    myFPtree, myHeaderTab = createTree(dataset, minsupp)
    freqItems = []
    mineTree(myFPtree, myHeaderTab, minsupp, set(), freqItems,maxlength)
    print  >> output,freqItems
    # datasets = load_data_set()
    a=get_support_data(dataset,freqItems,min_support=0.01299,support_data={},)
    # print >> output,a
    # print freqItems
    L=list(set(freqItems))
    # print L
    # L = sorted(L,key=lambda p:len(p))
    # print L
    big_rules_list = generate_big_rules(L, a, min_conf=0.0)
    # print big_rules_list
    for item in big_rules_list:
        print >>outputresult,item[0], "=>", item[1], "conf: ", item[2], "kulc:", item[3], "lift:", item[4], "ir:", item[5]
    output.close()
    # outputresult.close()
    print int(time.time())