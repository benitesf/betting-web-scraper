# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 19:52:34 2023

@author: edzon
"""
import abc

class Scraper(abc.ABC):
    @abc.abstractclassmethod()
    def extract( ):
        pass
    
    @abc.abstractclassmethod()
    def save( ):
        pass
    
    @abc.abstractclassmethod()
    def ():
        pass