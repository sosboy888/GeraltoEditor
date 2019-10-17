# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 11:22:56 2019

@author: Intal
"""

import wx
import  wx.py

app = wx.App(False)
frm = wx.Frame(None, -1, "Shell")
wx.py.shell.Shell(frm)
frm.Show()
app.MainLoop()