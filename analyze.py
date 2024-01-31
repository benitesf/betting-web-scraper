# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 16:27:34 2023

@author: edzon
"""
import json

abspath = "./data/raw/"
filename = "Grêmio_vs_Goiás.json"

with open(abspath + filename, "r") as openfile:
    json_object = json.load(openfile)