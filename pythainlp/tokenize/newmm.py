# -*- coding: utf-8 -*-
from __future__ import absolute_import,division,unicode_literals,print_function
from builtins import *
'''
โปรแกรม multi-cut
ตัดคำภาษาไทยโดยใช้ Maximum Matching algorithm
เดติดโค้ดต้นฉบับ คุณ Korakot Chaovavanich
จาก https://www.facebook.com/groups/408004796247683/permalink/431283740586455/
และ https://gist.github.com/korakot/fe26c65dc9eed467f4497f784a805716
'''
import re
import copy
from pythainlp.tools import file_trie
from marisa_trie import Trie
from collections import defaultdict
from pythainlp.tokenize import tcc
class LatticeString(str):
    ''' String subclass เพื่อเก็บวิธีตัดหลายๆ วิธี
    '''
    def __new__(cls, value, multi=None, in_dict=True):
        return str.__new__(cls, value)

    def __init__(self, value, multi=None, in_dict=True):
        self.unique = True
        if multi:
            self.multi = list(multi)
            if len(self.multi) > 1:
                self.unique = False
        else:
            self.multi = [value]
        self.in_dict = in_dict   # บอกว่าเป็นคำมีในดิกหรือเปล่า
spat_eng = r'''(?x)
([\d,\.]\#)+|   # number
([๑๒๓๔๕๖๗๘๙๐,\.]\#)+|   # thai number
([a-zA-Z]\#)+|  # english
[ \t]+|       # space
\r?\n         # newline
'''
pat_eng = re.compile(spat_eng)

def multicut(text,data):
    ''' ส่งคืน LatticeString คืนมาเป็นก้อนๆ
    '''
    words_at = defaultdict(list)  # main data structure
    if data=="":
        trie = file_trie(data="newmm")
    else:
        i=0
        data2=copy.copy(data)
        while i<len(data2):
            data2[i]=tcc.tcc(data2[i],sep='#')
            if(data2[len(data2[i])-1]!="#"):
               data2[i]+="#"
            i+=1
        trie = Trie(data2)
    def serialize(p, p2):    # helper function
        for w in words_at[p]:
            p_ = p + len(w)
            if p_== p2:
                yield w
            elif p_ < p2:
                for path in serialize(p_, p2):
                    yield w+'/'+path

    q = {0}
    last_p = 0   # last position for yield
    while min(q) < len(text):
        p = min(q)
        q -= {p}  # q.pop, but for set

        for w in trie.prefixes(text[p:]):
            words_at[p].append(w)
            q.add(p+len(w))

        if len(q)==1:
            q0 = min(q)
            yield LatticeString(text[last_p:q0], serialize(last_p, q0))
            last_p = q0

        # กรณี len(q) == 0  คือ ไม่มีใน dict
        elif len(q)==0:
            m = pat_eng.match(text[p:])
            if m!=None: # อังกฤษ, เลข, ว่าง
                i = p + m.span()[1]
            else: # skip น้อยที่สุด ที่เป็นไปได้
                for i in range(p, len(text)):
                    ww = trie.prefixes(text[i:])
                    m = pat_eng.match(text[i:])
                    if ww or m:
                        break
                else:
                    i = len(text)
            w = text[p:i]
            words_at[p].append(w)
            yield LatticeString(w, in_dict=False)
            last_p = i
            q.add(i)

def mmcut(text,data=''):
    res = []
    text=tcc.tcc(text,sep='#')
    if(text[len(text)-1]!='#'):
        text+='#'
    for w in multicut(text,data=data):
        mm = min(w.multi, key=lambda x: x.count('/'))
        res.extend(mm.split('/'))
    listdata=res
    i=0
    num=len(listdata)
    while i<len(listdata):
        if(re.search('\A[ก-ฮ]#\Z',listdata[i]) and i-1>=0):
            listdata[i-1]+=listdata[i]
            listdata[i]='#'
            num-=1
        i+=1
    return [x.replace('#','') for x in res if x!='#']
def combine(ww):
    if ww == []:
        yield ""
    else:
        w = ww[0]
        for tail in combine(ww[1:]):
            if w.unique:
                yield w+"|"+tail
            else:
                for m in w.multi:
                    yield m.replace("/","|")+"|"+tail

def listcut(text,data=''):
    '''
	ใช้ในการหา list ที่สามารถตัดคำได้ทั้งหมด
	'''
    ww = list(multicut(text,data))
    return list(combine(ww))
if __name__ == "__main__":
	text='ผมรักคุณนะครับโอเคบ่พวกเราเป็นคนไทยรักภาษาไทยภาษาบ้านเกิด'
	print(mmcut(text))
	#print(listcut(text))