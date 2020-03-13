# -*- coding: utf-8 -*-
"""
@author: RMM
"""
#Imports
import csv
import string
import os
import pandas as pd
import requests
import json
import sys
base_url = "https://inf-551-be532.firebaseio.com/.json"


def get_csv_data(filepath,encoding):
    data = pd.read_csv(filepath,encoding = encoding,quotechar="'",skipinitialspace=True)
    return data

def clean_dataframe(df):
    new_cols = []
    for val in df.columns:
        new_cols.append(("".join((text if text.isalnum() else " ") for text in val)).strip())
    df.columns = new_cols
    columns = df.columns
    
    for col in columns:
        for val in df[col]:
            try:
                dtype = str(type(val))
                if not pd.isna(val):
                    break
            except:
                continue
        if 'str' in dtype:
            df[col] = df[col].str.replace("'","").str.replace('"','').str.strip()#.str.replace("#","").str.strip().str.replace("-","")
            df[col] = df[col].str.encode('ascii', 'ignore').str.decode('ascii')
    return df

def get_json(df,orient):
    return df.to_json(orient=orient,force_ascii=False)

def getnode(filepath):
    if 'city.csv' in filepath:
        return 'city'
    elif 'country.csv' in filepath:
        return 'country'
    elif 'countrylanguage.csv' in filepath:
        return 'countrylanguage'
    else:
        raise TypeError ("PLEASE SPECIFY ONLY THE FOLLOWING FILE NAMES: city, country, countrylanguage")

def produce_inverted_index(response):
    inv_index = {}
    for node,items in response.json().items():
        for index, record in enumerate(items):
            for key, val in record.items():
                dtype = str(type(val))
                location = {'column': key,'index' : index, 'node' : node}
                if 'str' in dtype:
                    words = "".join((text if text.isalnum() else " ") for text in val).lower()
                    for word in words.split():
                            word = word.encode('ascii', 'ignore').decode('ascii').lower()
                            if word in inv_index:
                                inv_index[word].append(location)
                            else:
                                inv_index[word] = [location]
                elif 'int' in dtype or 'float' in dtype:
                    #key,index,node = validate()
                    pass    
    return inv_index

def main():
    args = sys.argv[1:]
    
    #base_url is global
    #can also add it here
    
    argsdict = {}
    for arg in args:
        if 'city' in os.path.basename(arg):
            argsdict[arg] = 'ansi'
        else:
            argsdict[arg] = 'utf-8'
    
    for filepath,encoding in argsdict.items():
        df = get_csv_data(filepath,encoding)
        df = clean_dataframe(df)
        json_data = get_json(df,'records')
        data = '{"' + getnode(filepath) + '": ' + json_data + '}'
        resp = requests.patch(base_url,data)
        sample = "Successful Upload" if '200' in str(resp)  else "Faulty upload"
        print(f"Response for {filepath} is {resp} " + sample)

    response = requests.get(base_url)
    print("Creating Inverted Index...")
    inv = produce_inverted_index(response)
    inv = {'inv':inv}
    inv = json.dumps(inv)
    p = requests.patch(base_url,inv)
    s = "Inverted Index: Successful Upload" if '200' in str(p)  else "Faulty upload"
    response = requests.get(base_url)
    print(s)
    #print(len(response.json()["inv"].keys()))
    
if __name__ == "__main__":
    main()  