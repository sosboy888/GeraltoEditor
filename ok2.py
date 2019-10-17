# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 21:40:18 2019

@author: Intal
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 22:08:59 2019

@author: Intal
"""

import wx
import wx.lib.dialogs
import wx.stc as stc
import os
import subprocess
import wx.py.shell
import keyword
import xml.dom.minidom
from xml.dom.minidom import parse
if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'size2': 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'size2': 10,
             }


class MainWindow(wx.Frame):
    def __init__(self,parent,title):
        self.dirname=''
        self.filename=''
        self.drivename=''
        self.path=""
        self.leftMarginWidth=25
        self.lineNumbersEnabled=True
        self.normalStylesFore = dict()
        self.normalStylesBack = dict()
        self.pythonStylesFore = dict()
        self.pythonStylesBack = dict()
        
        wx.Frame.__init__(self,parent,title=title,size=(800,600))
        self.SetIcon(wx.Icon("ImageKit/GeraltoIcon.ico"))
        self.control =stc.StyledTextCtrl(self,style=wx.TE_MULTILINE|wx.TE_WORDWRAP)
        self.control.CmdKeyAssign(ord('='),stc.STC_SCMOD_CTRL,stc.STC_CMD_ZOOMIN)#Ctrl+= to zoom in
        self.control.CmdKeyAssign(ord('-'),stc.STC_SCMOD_CTRL,stc.STC_CMD_ZOOMOUT)#Ctrl+- to zoom out
        self.control.SetViewWhiteSpace(False)
        self.control.SetLexer(stc.STC_LEX_PYTHON)
        self.control.SetKeyWords(0," ".join(keyword.kwlist))
		# Set some properties of the text control
        self.control.SetViewWhiteSpace(False)
        self.control.SetProperty("fold", "1")
        self.control.SetProperty("tab.timmy.whinge.level", "1")
        self.control.SetMargins(5,0)
        self.control.SetMarginType(1,stc.STC_MARGIN_NUMBER)
        self.control.SetMarginWidth(1,self.leftMarginWidth)
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_CIRCLEMINUS,          "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_CIRCLEPLUS,           "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,                "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNERCURVE,         "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040")
        self.control.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE,         "white", "#404040")
        self.CreateStatusBar()
        self.StatusBar.SetBackgroundColour((220,220,220))
        self.panel=ConsolePanel(self)
        self.splitter=wx.SplitterWindow(self,style=wx.SP_LIVE_UPDATE)
        self.panel1=self.control
        self.panel2=self.panel
        self.splitter.SplitVertically(self.panel1, self.panel2)
        w, h = self.GetSize()
        self.splitter.SetMinimumPaneSize(w/2)

        self.windowSizer = wx.BoxSizer(wx.VERTICAL)
        self.windowSizer.Add(self.splitter, 1, wx.ALL | wx.EXPAND)
        fileMenu=wx.Menu()
        menuNew=fileMenu.Append(wx.ID_NEW,"&New","Create a new file")
        menuOpen=fileMenu.Append(wx.ID_OPEN,"&Open","Open an existing file")
        menuSave=fileMenu.Append(wx.ID_SAVE,"&Save","Save the current file")
        menuSaveAs=fileMenu.Append(wx.ID_SAVEAS,"Save &As","Save the current file as a new file")
        fileMenu.AppendSeparator()
        menuClose=fileMenu.Append(wx.ID_EXIT,"&Close","Close Geralto")
        editMenu=wx.Menu()
        menuUndo=editMenu.Append(wx.ID_UNDO,"&Undo","Undo the last action")
        menuRedo=editMenu.Append(wx.ID_REDO,"&Redo","Redo the last action")
        editMenu.AppendSeparator()
        menuSelectAll=editMenu.Append(wx.ID_SELECTALL,"&Select All","Select the entire document")
        menuCopy=editMenu.Append(wx.ID_COPY,"&Copy","Copy selected text")
        menuCut=editMenu.Append(wx.ID_CUT,"C&ut","Cut selected text")
        menuPaste=editMenu.Append(wx.ID_PASTE,"&Paste","Paste text from clipboard")
        prefMenu=wx.Menu()
        menuLineNumbers=prefMenu.Append(wx.ID_ANY,"Toggle &Line Numbers","Show/Hide Line Numbers Column")
        helpMenu=wx.Menu()
        menuHowTo=helpMenu.Append(wx.ID_ANY,"&How To...","Get help using the editor")
        menuAbout=helpMenu.Append(wx.ID_ABOUT,"&About","Read about the editor and it's making!")
        
        
        menuBar=wx.MenuBar()
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(editMenu,"&Edit")
        menuBar.Append(prefMenu,"&Preferences")
        menuBar.Append(helpMenu,"&Help")
        
        self.SetMenuBar(menuBar)
        toolBar=self.CreateToolBar(style=wx.TB_HORIZONTAL)
        toolBarRunButton=toolBar.AddLabelTool(wx.ID_ANY,'Run',wx.Bitmap('ImageKit/run.png'))
        #toolBarCompileButton=toolBar.AddLabelTool(wx.ID_ANY,'Compile',wx.Bitmap('ImageKit/compile.png'))
        toolBar.Realize()
        toolBar.SetToolBitmapSize((24,24))
        
        #consolePanel=ConsolePanel(self)
        
        self.control.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)
        #File
        self.Bind(wx.EVT_MENU,self.onNew,menuNew)
        self.Bind(wx.EVT_MENU,self.onOpen,menuOpen)
        self.Bind(wx.EVT_MENU,self.onSave,menuSave)
        self.Bind(wx.EVT_MENU,self.onSaveAs,menuSaveAs)
        self.Bind(wx.EVT_MENU,self.onClose,menuClose)
        self.control.Bind(wx.EVT_KEY_UP,self.autoIndent)
        
        #Edit
        self.Bind(wx.EVT_MENU,self.onUndo,menuUndo)
        self.Bind(wx.EVT_MENU,self.onRedo,menuRedo)
        self.Bind(wx.EVT_MENU,self.onSelectAll,menuSelectAll)
        self.Bind(wx.EVT_MENU,self.onCopy,menuCopy)
        self.Bind(wx.EVT_MENU,self.onCut,menuCut)
        self.Bind(wx.EVT_MENU,self.onPaste,menuPaste)
        
        #preferences
        self.Bind(wx.EVT_MENU,self.onToggleLineNumbers,menuLineNumbers)
        #Help
        self.Bind(wx.EVT_MENU,self.onHowTo,menuHowTo)
        self.Bind(wx.EVT_MENU,self.onAbout,menuAbout)
        
        #ToolBar Bindings
        self.Bind(wx.EVT_TOOL,self.onRun,toolBarRunButton)
        #self.Bind(wx.EVT_TOOL,self.onCompile,toolBarCompileButton)
        
        self.Show()
        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleClearAll() # reset all to be like default

		# global default styles for all languages
        self.control.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,size:%(size2)d" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.control.StyleSetSpec(stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold")
        self.control.StyleSetSpec(stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold")

		# Set all the theme settings
        self.ParseSettings("settings.xml")
        self.setStyling()
        
    def setStyling(self):
		# Set the general foreground and background for normal and python styles
		pSFore = self.pythonStylesFore
		pSBack = self.pythonStylesBack
		nSFore = self.normalStylesFore
		nSBack = self.normalStylesBack

		# Python styles
		self.control.StyleSetBackground(stc.STC_STYLE_DEFAULT, nSBack["Main"])
		self.control.SetSelBackground(True, "#333333")

		# Default
		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "fore:%s,back:%s" % (pSFore["Default"], pSBack["Default"]))
		self.control.StyleSetSpec(stc.STC_P_DEFAULT, "face:%(helv)s,size:%(size)d" % faces)

		# Comments
		self.control.StyleSetSpec(stc.STC_P_COMMENTLINE, "fore:%s,back:%s" % (pSFore["Comment"], pSBack["Comment"]))
		self.control.StyleSetSpec(stc.STC_P_COMMENTLINE, "face:%(other)s,size:%(size)d" % faces)

		# Number
		self.control.StyleSetSpec(stc.STC_P_NUMBER, "fore:%s,back:%s" % (pSFore["Number"], pSBack["Number"]))
		self.control.StyleSetSpec(stc.STC_P_NUMBER, "size:%(size)d" % faces)

		# String
		self.control.StyleSetSpec(stc.STC_P_STRING, "fore:%s,back:%s" % (pSFore["String"], pSBack["Number"]))
		self.control.StyleSetSpec(stc.STC_P_STRING, "face:%(helv)s,size:%(size)d" % faces)

		# Single-quoted string
		self.control.StyleSetSpec(stc.STC_P_CHARACTER, "fore:%s,back:%s" % (pSFore["SingleQuoteString"], pSBack["SingleQuoteString"]))
		self.control.StyleSetSpec(stc.STC_P_CHARACTER, "face:%(helv)s,size:%(size)d" % faces)

		# Keyword
		self.control.StyleSetSpec(stc.STC_P_WORD, "fore:%s,back:%s" % (pSFore["Keyword"], pSBack["Keyword"]))
		self.control.StyleSetSpec(stc.STC_P_WORD, "bold,size:%(size)d" % faces)

		# Triple quotes
		self.control.StyleSetSpec(stc.STC_P_TRIPLE, "fore:%s,back:%s" % (pSFore["TripleQuote"], pSBack["TripleQuote"]))
		self.control.StyleSetSpec(stc.STC_P_TRIPLE, "size:%(size)d" % faces)

		# Triple double quotes
		self.control.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "fore:%s,back:%s" % (pSFore["TripleDoubleQuote"], pSBack["TripleDoubleQuote"]))
		self.control.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, "size:%(size)d" % faces)

		# Class name definition
		self.control.StyleSetSpec(stc.STC_P_CLASSNAME, "fore:%s,back:%s" % (pSFore["ClassName"], pSBack["ClassName"]))
		self.control.StyleSetSpec(stc.STC_P_CLASSNAME, "bold,underline,size:%(size)d" % faces)

		# Function name definition
		self.control.StyleSetSpec(stc.STC_P_DEFNAME, "fore:%s,back:%s" % (pSFore["FunctionName"], pSBack["FunctionName"]))
		self.control.StyleSetSpec(stc.STC_P_DEFNAME, "bold,size:%(size)d" % faces)

		# Operators
		self.control.StyleSetSpec(stc.STC_P_OPERATOR, "fore:%s,back:%s" % (pSFore["Operator"], pSBack["Operator"]))
		self.control.StyleSetSpec(stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces)

		# Identifiers
		self.control.StyleSetSpec(stc.STC_P_IDENTIFIER, "fore:%s,back:%s" % (pSFore["Identifier"], pSBack["Identifier"]))
		self.control.StyleSetSpec(stc.STC_P_IDENTIFIER, "face:%(helv)s,size:%(size)d" % faces)

		# Comment blocks
		self.control.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "fore:%s,back:%s" % (pSFore["CommentBlock"], pSBack["CommentBlock"]))
		self.control.StyleSetSpec(stc.STC_P_COMMENTBLOCK, "size:%(size)d" % faces)

		# End of line where string is not closed
		self.control.StyleSetSpec(stc.STC_P_STRINGEOL, "fore:%s,back:%s" % (pSFore["StringEOL"], pSBack["StringEOL"]))
		self.control.StyleSetSpec(stc.STC_P_STRINGEOL, "face:%(mono)s,eol,size:%(size)d" % faces)

		# Caret/Insertion Point
		self.control.SetCaretForeground(pSFore["Caret"])
		self.control.SetCaretLineBackground(pSBack["CaretLine"])
		self.control.SetCaretLineVisible(True)
        
        
    def onNew(self,event):
        self.filename=''
        self.control.SetValue("")
    def onOpen(self,event):
        try:
            dlg=wx.FileDialog(self,"Choose a File",self.dirname,"","*.*",wx.FD_OPEN)
            if(dlg.ShowModal()==wx.ID_OK):
                self.path=dlg.GetPath()
                f=open(self.path,'r')
                lines=f.read()
                self.control.SetValue(lines)
               
                f.close()
            dlg.Destroy()
        except:
            dlg=wx.MessageDialog(self,"Couldn't open the file","Error",wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    def onSave(self,event):
        try:
            f=open(self.path,'w')
            f.write(self.control.GetValue())
            f.close()
        except:
            try:
                dlg=wx.FileDialog(self,"Save file as",self.dirname,"Untitled","*.*",wx.FD_SAVE|wx.FD_OVERRIDE_PROMPT)
                if(dlg.ShowModal()==wx.ID_OK):
                    
                    f=open(dlg.GetPath(),'w')
                    f.close()
                dlg.Destroy()
            except:
                pass
    def onSaveAs(self,event):
        
        dlg=wx.FileDialog(self,"Save file as",self.dirname,"Untitled","*.*",wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        if(dlg.ShowModal()==wx.ID_OK):
            self.path=dlg.GetPath()
            f=open(self.path,'w')
            f.write(self.control.GetValue())
            f.close()
        dlg.Destroy()
       
    def onClose(self,event):
        self.Close(True)
    def onUndo(self,event):
        self.control.Undo()
    def onRedo(self,event):
        self.control.Redo()
    def onSelectAll(self,event):
        self.control.SelectAll()
    def onCopy(self,event):
        self.control.Copy()
    def onCut(self,event):
        self.control.Cut()
    def onPaste(self,event):
        self.control.Paste()
    def onToggleLineNumbers(self,event):
        if(self.lineNumbersEnabled):
            self.control.SetMarginWidth(1,0)
            self.lineNumbersEnabled=False
        else:
            self.control.SetMarginWidth(1,self.leftMarginWidth)
            self.lineNumbersEnabled=True
    def onHowTo(self,event):
        dlg=wx.lib.dialogs.ScrolledMessageDialog(self,"This is how to.",(400,400))
        dlg.ShowModal()
        dlg.Destroy()
    def onAbout(self,e):
        dlg=wx.MessageDialog(self,"Geralto- Created by sosboy888.")
        if(dlg.ShowModal==wx.ID_OK):
            dlg.Destroy()
    def onRun(self,e):
        print("The program will execute here")
        if(self.path==""):
            msg=wx.MessageDialog(self,"You will have to save the file first before running the python script.")
            if(msg.ShowModal()==wx.ID_OK):
                msg.Destroy()
                dlg=wx.FileDialog(self,"Save file as",self.dirname,"Untitled","*.py",wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                if(dlg.ShowModal()==wx.ID_OK):
                    self.path=dlg.GetPath()
                    f=open(self.path,'w')
                    f.write(self.control.GetValue())
                    f.close()
                dlg.Destroy()
        self.child.runScript(self.path)
        
        
    # Update the user interface 
    def onUpdateUI(self, e):
		# check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.control.GetCurrentPos()
        if (caretPos > 0):
            charBefore = self.control.GetCharAt(caretPos - 1)
            styleBefore = self.control.GetStyleAt(caretPos - 1)

		# check before
        if (charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR):
            braceAtCaret = caretPos - 1

		# check after
        if (braceAtCaret < 0):
            charAfter = self.control.GetCharAt(caretPos)
            styleAfter = self.control.GetStyleAt(caretPos)

            if (charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR):
                braceAtCaret = caretPos

        if (braceAtCaret >= 0):
            braceOpposite = self.control.BraceMatch(braceAtCaret)

        if (braceAtCaret != -1 and braceOpposite == -1):
            self.control.BraceBadLight(braceAtCaret)
        else:
            self.control.BraceHighlight(braceAtCaret,braceOpposite) 
    def ParseSettings(self, settings_file):
		# Open XML document using minidom parser
		DOMTree = xml.dom.minidom.parse(settings_file)
		collection = DOMTree.documentElement # Root element
		
		# Get all the styles in the collection
		styles = collection.getElementsByTagName("style")
		for s in styles:
			item = s.getElementsByTagName("item")[0].childNodes[0].data
			color = s.getElementsByTagName("color")[0].childNodes[0].data
			side = s.getElementsByTagName("side")[0].childNodes[0].data
			sType = s.getAttribute("type")
			if sType == "normal":
				if side == "Back": # background
					self.normalStylesBack[str(item)] = str(color)
				else:
					self.normalStylesFore[str(item)] = str(color)
			elif sType == "python":
				if side == "Back":
					self.pythonStylesBack[str(item)] = str(color)
				else:
					self.pythonStylesFore[str(item)] = str(color)
    def onCompile(self,e):
        print("The program will compile here")
        filename = "sos.java"
        args = "javac.exe " + filename
        subprocess.call(args, shell=False)
    def autoIndent(self,event):
        print self.control.GetCharAt((self.control.GetCurrentPos()))
        key = event.GetKeyCode()
        if key == wx.WXK_NUMPAD_ENTER or key == wx.WXK_RETURN:
            if self.control.GetCharAt((self.control.GetCurrentPos()-3)) == 58:
                
                line = self.control.GetCurrentLine()-1
                oldindent=self.control.GetLineIndentation(line)
                print(oldindent)
                if(((oldindent/8)>0)):
                    i=oldindent/8
                    while(i>=0):
                        self.control.AddText("\t")
                        i=i-1
                        print("indented")
                else:
                    self.control.AddText("\t")
                #self.control.SetLineIndentation(line, self.control.GetLineIndentation(line)+self.control.GetTabWidth())
                        
        event.Skip()
class ConsolePanel(wx.Panel):
    def __init__(self,parent):
        
        
        wx.Panel.__init__(self,parent)
        self.shell=wx.py.shell.Shell(self,-1)
        
    def runScript(self,path):
        self.shell.runfile(path)

app=wx.App(False)
frame=MainWindow(None,"Geralto")
app.MainLoop()