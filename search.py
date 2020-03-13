'''
@author: RMM
'''
import csv
import string
import os
import pandas as pd
import requests
import sys

base_url = "https://xxxx.firebaseio.com/.json"

class ResultObject():
    #store attributes of result for transparent code
    def __init__(self,loc,pkey=None,text=None):
        self.text = text
        self.score = 0
        self.loc = loc
        self.pkey = pkey
        self.table,self.ind,self.col = loc['node'], loc['index'], loc['column']
        self.links = []
        
def perform_search(cands):
    #base_url = "https://inf-551-be532.firebaseio.com/.json"
    cands = [c.lower().strip().replace("'","") for c in cands] #lower case 
    response = requests.get(base_url).json()
    search = False
    query2loc = {}
    for cand in cands: 
        if cand in response["inv"]:
            query2loc[cand] = response["inv"][cand]
            search = True
        else:
            continue
        
    if not query2loc:
        print("No Results for given query")
        
    table2pkey = {'country':'Code','city':'ID','countrylanguage':'CountryCode'}
    search_results = []
    for query,loclist in query2loc.items():
        for loc in loclist:
            table,index,col = loc['node'],loc['index'], loc['column']
            pkey_col = table2pkey[table]
            result = response[table][index][col]
            obj = ResultObject(loc)
            obj.text, obj.pkey = response[table][index][col].lower(),response[table][index][pkey_col]
            for word in obj.text.split():
                for q in cands:
                    if word == q:
                        obj.score += 1
            search_results.append(obj)
    
    table2result = {}
    for node in ['city','country','countrylanguage']:
        table2result[node] = sorted([r for r in search_results if r.table==node],key=lambda x:x.score,reverse=True)
    
    collector = {}
    filtered = {'city':[],'country':[],'countrylanguage':[]}
    
    for k,v in table2result.items():
        for item in v:
            idx = (item.table,item.ind,item.col)
            if idx in collector: 
                pass
            else:
                collector[idx] = None
                filtered[k].append(item)
        
    merged = {}
    for k,v in filtered.items():
        merged[k] = {}
        for item in v:
            if item.pkey not in merged[k]:
                merged[k][item.pkey] = [item]
            else:
                merged[k][item.pkey].append(item)
    
    final_result = {}
    for k,subdict in merged.items():
        final_result[k] = []
        for pkey, items in subdict.items():
            main = items[0]
            for i in range(1,len(items)):
                item = items[i]
                main.links.append(item)
                main.score+=item.score
            final_result[k].append(main)
        final_result[k] = sorted(final_result[k],key=lambda x:x.score,reverse=True)
    
    q = " ".join(i for i in cands) ; print(f"For: {q}")
    for table, result in final_result.items():
        result_stdout = ",".join(str(i.pkey) for i in result)
        print(table+":"+result_stdout)
    
    print("\n")
    '''
    for table, result in final_result.items():
        print(table)
        for r in result:
            print(r.pkey,r.score,r.text," ".join(g.text for g in r.links))
    '''

def main():
    args = sys.argv[1:]
    queries = []
    flag = False
    for arg in args:
        queries.append(arg.split())
    
    queries = {'main':[],'combo':[]}
    for arg in args:
        arg_split = arg.split()
        if len(arg_split) == 1:
            queries['main'].extend(arg_split)
            queries['combo'].extend(arg_split)
        else:
            queries[arg] = arg_split
            queries['combo'].extend(arg_split)
            flag = True
    '''
    if ((len(queries.keys()) ==2) and queries['main'] != []):
        print("HERE")
    if  (queries['main'] == [] and (len(queries.keys()) ==3)):
        print("HERE2")
    '''
    
    #comment the below two lines if they are raising bugs
    if queries and (((len(queries.keys()) ==2) and queries['main'] != []) or (queries['main'] == [] and (len(queries.keys()) ==3))):
        del queries['combo']
        
    for k, cands in queries.items():
        if cands:
            if k == "combo":
                print("ALL QUERIES TOGETHER")
            perform_search(cands)
    
if __name__ == "__main__":
    main()  