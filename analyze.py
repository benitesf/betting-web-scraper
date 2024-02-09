# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 16:27:34 2023

@author: edzon
"""
import json

abspath = "./data/raw/"
filename = "Salernitana_vs_Empoli.json"

with open(abspath + filename, "r") as openfile:
    json_object = json.load(openfile)

threshold_tail = 1.65
threshold_head = 1.95
res = {}

for market_name, market_dict in json_object.items():
    a = {}
    for item_name, item_dict in market_dict.items():
        b = {}
        for odd_name, odd_value in item_dict.items():
            try:                
                if threshold_tail <= float(odd_value) and threshold_head >= float(odd_value):
                    b[odd_name] = odd_value
            except Exception:
                break
        if len(b) > 0:
            a[item_name] = b
    if len(a) > 0:
        res[market_name] = a

# Serialize json
json_object = json.dumps(res, indent=4, ensure_ascii=False)

# Save to json file
filename_ = filename.split(".")[0] + "_threshold.json"
with open("./data/raw/" + filename_, "w") as outfile:
    outfile.write(json_object)