
# adapted from Dropbox/SelfAdministration/Analysis/Analysis102.py
from tkinter import *
from tkinter.ttk import Notebook
from tkinter import filedialog
from datetime import datetime
import stream01
import math
import os
import GraphLib
import model
import Examples
import numpy as np
import ListLib

"""
Models, Views and Controllers (MCV) design: keep the representation of the data separate
from the parts of the program that the user interacts with.
Models: store and retrieve data from import osdatabases and files. 
View: displays information to the user (eg. a graph)
Controllers: convert user input into calls on functions that manipulate data
"""

def main(argv=None):
    if argv is None:
        argv = sys.argv
    gui = myGUI()
    gui.go()
    return 0

# ********************* The Model **********************


class DataRecord:
    def __init__(self, datalist, fileName):
        self.fileName = fileName
        self.datalist = datalist
        self.numberOfL1Responses = 0
        self.numberOfL2Responses = 0
        self.numberOfInfusions = 0
        self.totalPumpDuration = 0        
        self.cocConc = 0.0
        self.pumpSpeed = 0.0
        self.averagePumpTime = 0.0
        self.TH_PumpTimes = []
        self.priceList = []
        self.consumptionList = []
        self.responseList = []
        self.deltaList = []
        self.notes = "test"

    def __str__(self):
        """
            Returns a string of values inside object that is used when the print command is called
        """
        consumptionStr = ""
        for i in range(0,len(self.consumptionList)):
            consumptionStr = consumptionStr + "{:.3f}, ".format(self.consumptionList[i])

        priceStr = ""
        for i in range(0,len(self.priceList)):
            priceStr = priceStr + "{:.2f}, ".format(self.priceList[i])

        responseStr = ""
        for i in range(0,len(self.responseList)):
            responseStr = responseStr + "{}, ".format(self.responseList[i])
        
        
        s = "Filename: "+self.fileName+ \
        "\nNotes: "+self.notes+ \
        "\nLever 1 Responses: "+str(self.numberOfL1Responses)+ \
        "\nLever 2 Responses: "+str(self.numberOfL2Responses)+ \
        "\nInfusions: "+str(self.numberOfInfusions)+ \
        "\nTotal Pump Time (mSec): "+str(self.totalPumpDuration)+ \
        "\nAverage Pump Time (mSec): "+str(round(self.averagePumpTime,4))+ \
        "\nDrug Concentration (mg/ml): "+str(self.cocConc)+ \
        "\nPump Speed (ml/sec): "+str(self.pumpSpeed)+" ml/Sec"+ \
        "\nPumpTimes = "+str(self.TH_PumpTimes) + \
        "\nPriceList = " + priceStr + \
        "\nConsumptionList = " + consumptionStr + \
        "\nResponseList = " + responseStr +"\n"
        #"\nDelta List: "+str(self.deltaList)+ 
        #"\n============================\n"
        
        return s

    def extractStatsFromList(self):
        self.numberOfL1Responses = 0
        self.numberOfL2Responses = 0
        self.numberOfInfusions = 0
        self.totalPumpDuration = 0
        leverOut = True
        pumpOn = False
        lastTime = 0
        self.deltaList = []
        delta = 0
        for pairs in self.datalist:                   
            if pairs[1] == 'L':
                self.numberOfL1Responses = self.numberOfL1Responses + 1
            if pairs[1] == 'J':
                self.numberOfL2Responses = self.numberOfL2Responses + 1               
            if ((pairs[1] == 'P') and (leverOut == True)) :
                self.numberOfInfusions = self.numberOfInfusions + 1
                pumpStartTime = pairs[0]
                delta = pumpStartTime - lastTime
                self.deltaList.append(round(delta/(1000*60)))
                lastTime = pumpStartTime
                pumpOn = True
            if pairs[1] == 'p':
                if pumpOn:
                    duration = pairs[0]-pumpStartTime
                    pumpOn = False
                    self.totalPumpDuration = self.totalPumpDuration + duration
            if self.numberOfInfusions > 0:
                self.averagePumpTime = round(self.totalPumpDuration / self.numberOfInfusions,2)


class myGUI(object):
    def __init__(self):
        """
        This object controls all aspects of the Graphical User Interface:
        It uses the Tk tookkit imported from tkinter.
        "root" is the base level; all other frames and widgets are in relation to "root".

        """
        self.version = "Analysis200.02"
        self.root = Tk()
        self.root.title(self.version)
        canvas_width = 800
        canvas_height = 600

        #Construct ten empty dataRecords
        self.record0 = DataRecord([],"empty")         
        self.record1 = DataRecord([],"empty")
        self.record2 = DataRecord([],"empty")
        self.record3 = DataRecord([],"empty")
        self.record4 = DataRecord([],"empty")
        self.record5 = DataRecord([],"empty")
        self.record6 = DataRecord([],"empty")
        self.record7 = DataRecord([],"empty")
        self.record8 = DataRecord([],"empty")
        self.record9 = DataRecord([],"empty")
        
        # Create a list of dataRecords so that it can be "selected" with self.fileChoice.get()
        self.recordList = [self.record0,self.record1,self.record2,self.record3,self.record4, \
                           self.record5,self.record6,self.record7,self.record8,self.record9]

        # *************   The Model - vaiables, lists and files *********
        self.clockTimeStringVar = StringVar(value="0:00:00")
        self.max_x_scale = IntVar(value=360)
        self.max_y_scale = IntVar(value=250)
        self.neumaierDose = IntVar(value=2)
        # self.max_x_scale.set(120)
        
        self.fileChoice = IntVar(value=0)
        self.fileName0 = StringVar(value = self.recordList[0].fileName)
        self.fileName1 = StringVar(value = self.recordList[1].fileName)
        self.fileName2 = StringVar(value = self.recordList[2].fileName)
        self.fileName3 = StringVar(value = self.recordList[3].fileName)
        self.fileName4 = StringVar(value = self.recordList[4].fileName)
        self.fileName5 = StringVar(value = self.recordList[5].fileName)
        self.fileName6 = StringVar(value = self.recordList[6].fileName)
        self.fileName7 = StringVar(value = self.recordList[7].fileName)
        self.fileName8 = StringVar(value = self.recordList[8].fileName)
        self.fileName9 = StringVar(value = self.recordList[9].fileName)
        
        self.fileNameList = [self.fileName0,self.fileName1,self.fileName2,self.fileName3,self.fileName4,\
                             self.fileName5,self.fileName6,self.fileName7,self.fileName8,self.fileName9]

        # Threshold tab
        self.respMax = IntVar()
        self.respMax.set(200)
        self.rangeEnd = IntVar()
        self.rangeEnd.set(10)
        self.rangeBegin = IntVar()
        self.rangeBegin.set(0)


        #*************  The View ************       

        #************* Root Frame
        self.rootFrame = Frame(self.root, borderwidth=2, relief="sunken")
        self.rootFrame.grid(column = 0, row = 0)
        headerFrame= Frame(self.root,borderwidth=2, relief="sunken")
        headerFrame.grid(row=0,column=0,sticky=EW)
        fileSelectorFrame = Frame(self.root, borderwidth=2, relief="sunken")
        fileSelectorFrame.grid(row=1,column=0,sticky=NSEW)        
        noteBookFrame = Frame(self.root, borderwidth=2, relief="sunken")
        noteBookFrame.grid(row=2,column=0)
        myNotebook = Notebook(noteBookFrame)
        self.graphTab = Frame(myNotebook)
        self.thresholdTab = Frame(myNotebook)
        self.textTab = Frame(myNotebook)
        myNotebook.add(self.thresholdTab,text = "Threshold")
        myNotebook.add(self.graphTab,text = "Graphs")      
        myNotebook.add(self.textTab,text = "Text")
        myNotebook.grid(row=0,column=0)

        #**************Header Row ******************
        openFileButton = Button(headerFrame, text="Open File", command= lambda: self.openWakeFile("")).grid(row=0,column=0, sticky=W)
        spacer1Label = Label(headerFrame, text="               ").grid(row=0,column=1)
        clockTimeLabel = Label(headerFrame, textvariable = self.clockTimeStringVar).grid(row = 0, column=2)
        spacer2Label = Label(headerFrame, text="               ").grid(row=0,column=3)
        loadTestButton = Button(headerFrame, text="3_I164_Oct_4.str", command= lambda: \
                              self.openWakeFile("3_I164_Oct_4.str")).grid(row=0,column=4,sticky=N)

        #************** Graph Tab ******************
        self.columnFrame = Frame(self.graphTab, borderwidth=2, relief="sunken")
        self.columnFrame.grid(column = 0, row = 0, columnspan= 1, sticky=NS)
        
        self.graphButtonFrame = Frame(self.columnFrame, borderwidth=2, relief="sunken")
        self.graphButtonFrame.grid(column = 0, row = 0, sticky=N)
        clearCanvasButton = Button(self.graphButtonFrame, text="Clear", command= lambda: \
                              self.clearCanvas()).grid(row=0,column=0,sticky=N)
        cumRecButton = Button(self.graphButtonFrame, text="Cum Rec", command= lambda: \
                              self.drawCumulativeRecord(self.recordList[self.fileChoice.get()])).grid(row=2,column=0,sticky=N)
        self.showBPVar = BooleanVar(value = True)      
        showBPButton = Checkbutton(self.graphButtonFrame, text = "show BP", variable = self.showBPVar, onvalue = True, offvalue = False, \
                                   command= lambda: self.drawCumulativeRecord(self.recordList[self.fileChoice.get()]))
        showBPButton.grid(row = 3,column=0)      
        eventRecButton = Button(self.graphButtonFrame, text="Event Rec", command= lambda: \
                              self.drawEventRecords()).grid(row=4,column=0,sticky=N)
        timeStampButton = Button(self.graphButtonFrame, text="Timestamps", command= lambda: \
                              self.timeStamps(self.recordList[self.fileChoice.get()])).grid(row=5,column=0,sticky=N)
        modelButton = Button(self.graphButtonFrame, text="Model Coc", command= lambda: \
                              self.showModel(self.recordList[self.fileChoice.get()])).grid(row=6,column=0,sticky=N)
        histogramButton = Button(self.graphButtonFrame, text="Histogram", command= lambda: \
                              self.showHistogram(self.recordList[self.fileChoice.get()])).grid(row=7,column=0,sticky=N)

        self.graph_YaxisRadioButtonFrame = Frame(self.columnFrame, borderwidth=2, relief="sunken")
        self.graph_YaxisRadioButtonFrame.grid(column = 0, row = 1)
        y_axisButtonLabel = Label(self.graph_YaxisRadioButtonFrame, text = "Y axis").grid(row = 0, column=0)
        y_scaleRadiobutton250 = Radiobutton(self.graph_YaxisRadioButtonFrame, text="250", variable=self.max_y_scale, value=250)
        y_scaleRadiobutton250.grid(column = 0, row = 1)
        y_scaleRadiobutton500 = Radiobutton(self.graph_YaxisRadioButtonFrame, text="500", variable=self.max_y_scale, value=500)
        y_scaleRadiobutton500.grid(column = 0, row = 2)
        y_scaleRadiobutton1000 = Radiobutton(self.graph_YaxisRadioButtonFrame, text="1000", variable=self.max_y_scale, value=1000)
        y_scaleRadiobutton1000.grid(column = 0, row = 3)
        y_scaleRadiobutton1500 = Radiobutton(self.graph_YaxisRadioButtonFrame, text="1500", variable=self.max_y_scale, value=1500)
        y_scaleRadiobutton1500.grid(column = 0, row = 4)

        # ******  IntA Frame ************

        self.graph_IntA_frame = Frame(self.columnFrame, borderwidth=2, relief="sunken")
        self.graph_IntA_frame.grid(column = 0, row = 2)
        IntA_frame_lable = Label(self.graph_IntA_frame, text = "IntA").grid(row = 0, column=0)
        IntA_event_button = Button(self.graph_IntA_frame, text="Event records", command= lambda: \
            self.IntA_event_records()).grid(row=1,column=0,sticky=N)
        IntA_durations_button = Button(self.graph_IntA_frame, text="Pump durations", command= lambda: \
            self.IntA_durations()).grid(row=2,column=0,sticky=N)        
        IntA_histogram_block_Button = Button(self.graph_IntA_frame, text="Histogram (blocks)", command= lambda: \
            self.IntAHistogram_blocks()).grid(row=3,column=0,sticky=N)
        IntA_histogram_all_Button = Button(self.graph_IntA_frame, text="Histogram (All)", command= lambda: \
            self.IntAHistogram_all()).grid(row=4,column=0,sticky=N)


        # ******  Example Frame *********

        self.graph_example_frame = Frame(self.columnFrame, borderwidth=2, relief="sunken")
        self.graph_example_frame.grid(column = 0, row = 3)
        example_frame_lable = Label(self.graph_example_frame, text = "Examples").grid(row = 0, column=0)
        model_example_button = Button(self.graph_example_frame, text="Test Model", command= lambda: \
                self.testModel()).grid(row=1,column=0,sticky=N)
        axes_example_button = Button(self.graph_example_frame, text="Axes", command= lambda: \
                              self.test()).grid(row=2,column=0,sticky=N)
        


        # *************************************
        
        self.graph_XaxisRadioButtonFrame = Frame(self.graphTab, borderwidth=2, relief="sunken")
        self.graph_XaxisRadioButtonFrame.grid(column = 1, row = 1, sticky=EW)
        x_axisButtonLabel = Label(self.graph_XaxisRadioButtonFrame, text = "X axis").grid(row = 0, column=0)

        x_scaleRadiobutton10 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="10", variable=self.max_x_scale, value=10)
        x_scaleRadiobutton10.grid(column = 1, row = 0)
        x_scaleRadiobutton30 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="30", variable=self.max_x_scale, value=30)
        x_scaleRadiobutton30.grid(column = 2, row = 0)
        x_scaleRadiobutton60 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="60", variable=self.max_x_scale, value=60)
        x_scaleRadiobutton60.grid(column = 3, row = 0)
        x_scaleRadiobutton120 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="120", variable=self.max_x_scale, value=120)
        x_scaleRadiobutton120.grid(column = 4, row = 0)
        x_scaleRadiobutton180 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="180", variable=self.max_x_scale, value=180)
        x_scaleRadiobutton180.grid(column = 5, row = 0)
        x_scaleRadiobutton360 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="360", variable=self.max_x_scale, value=360)
        x_scaleRadiobutton360.grid(column = 6, row = 0)
        x_scaleRadiobutton720 = Radiobutton(self.graph_XaxisRadioButtonFrame, text="720", variable=self.max_x_scale, value=720)
        x_scaleRadiobutton720.grid(column = 7, row = 0)
        
        self.graphCanvasFrame = Frame(self.graphTab, borderwidth=2, relief="sunken")
        self.graphCanvasFrame.grid(column = 1, row = 0)
        self.graphCanvas = Canvas(self.graphCanvasFrame, width = canvas_width, height = canvas_height)
        self.graphCanvas.grid(row=0,column=0)
        self.graphCanvas.create_text(100,10,text = "Graph Canvas")
                

        #************** Threshold Tab **************
        self.thresholdButtonFrame = Frame(self.thresholdTab, borderwidth=2, relief="sunken")
        self.thresholdButtonFrame.grid(column = 0, row = 0, sticky=N)
        clearTHCanvasButton = Button(self.thresholdButtonFrame, text="Clear Canvas", \
                                     command = lambda: self.thresholdCanvas.delete('all')).grid(row=0,column=0,sticky=N)


        #************* Draw Threshold Frame ********
        self.drawThresholdFrame = Frame(self.thresholdButtonFrame, borderwidth=2, relief="sunken")
        self.drawThresholdFrame.grid(row = 1, column = 0, sticky = EW)

        thresholdButton = Button(self.drawThresholdFrame, text="Draw Threshold", command= lambda: \
                                 self.drawThreshold(self.recordList[self.fileChoice.get()])).grid(row=0,column=0, sticky = N)

        self.curveFitVar = BooleanVar(value = True)
        self.curveFitCheckButton = Checkbutton(self.drawThresholdFrame, text = "Auto Curve Fit", variable = self.curveFitVar, \
                                        onvalue = True, offvalue = False).grid(row = 1, column = 0, columnspan = 2)
        
        self.logXVar = BooleanVar(value = True)      
        logLogCheckButton = Checkbutton(self.drawThresholdFrame, text = "Log X", variable = self.logXVar, \
                                        onvalue = True, offvalue = False).grid(row = 2, column = 0)
        self.logYVar = BooleanVar(value = True)      
        logLogCheckButton = Checkbutton(self.drawThresholdFrame, text = "Log Y", variable = self.logYVar, \
                                        onvalue = True, offvalue = False).grid(row = 2, column = 1)
        self.showPmaxLine = BooleanVar(value = True)      
        showPmaxCheckButton = Checkbutton(self.drawThresholdFrame, text = "Pmax line", variable = self.showPmaxLine, \
                                        onvalue = True, offvalue = False).grid(row = 3, column = 0)
        self.showOmaxLine = BooleanVar(value = True)
        showOmaxCheckButton = Checkbutton(self.drawThresholdFrame, text = "Omax line", variable = self.showOmaxLine, \
                                        onvalue = True, offvalue = False).grid(row = 3, column = 1)
        self.AssignQzeroVar = DoubleVar()
        
        self.QzeroVar = DoubleVar()
        self.QzeroLabel = Label(self.drawThresholdFrame, text = "Qzero").grid(row=4,column=0,columnspan = 2,sticky=EW) 
        self.scale_Q_zero = Scale(self.drawThresholdFrame, orient=HORIZONTAL, length=200, resolution = 0.05, \
                                  from_=0.25, to=5.0, variable = self.QzeroVar)
        self.scale_Q_zero.set(1.0)
        self.scale_Q_zero.grid(row=5,column=0, columnspan = 2)

        self.alphaVar = DoubleVar()
        self.alphaLabel = Label(self.drawThresholdFrame, text = "alpha").grid(row=6,column=0,columnspan = 2,sticky=EW)        
        self.scale_alpha = Scale(self.drawThresholdFrame, orient=HORIZONTAL, length=200, resolution = 0.00025, \
                                 from_= 0.0005, to = 0.02, variable = self.alphaVar)
        self.scale_alpha.set(0.005)
        self.scale_alpha.grid(row=7,column=0, columnspan = 2)

        self.kVar = DoubleVar(value = 2.0)
        self.kLabel = Label(self.drawThresholdFrame, text = "k").grid(row=8,column=0,columnspan = 2,sticky=EW)
        self.scale_k = Scale(self.drawThresholdFrame, orient=HORIZONTAL, length=200, resolution = 0.2, \
                             from_=2.0, to=8.0, variable = self.kVar)
        self.scale_k.set(4.0)
        self.scale_k.grid(row=9,column=0, columnspan = 2)

    
        self.startStopFrame = Frame(self.thresholdButtonFrame, borderwidth=2, relief="sunken")
        self.startStopFrame.grid(columnspan=2, row = 9, column = 0)
        
        self.firstPointFrame = Frame(self.startStopFrame, borderwidth=2, relief="sunken")
        self.firstPointFrame.grid(row = 0, column = 0, sticky=W)
        
        rangeBeginLable = Label(self.firstPointFrame, text="First Point").grid(row=0,column=0, sticky=N)
        cumRecButton1 = Radiobutton(self.firstPointFrame, text = "1   ", variable= self.rangeBegin, value = 0).grid(row=1,column=0)
        cumRecButton2 = Radiobutton(self.firstPointFrame, text = "2  ", variable=  self.rangeBegin, value = 1).grid(row=2,column=0)
        cumRecButton3 = Radiobutton(self.firstPointFrame, text = "3  ", variable=  self.rangeBegin, value = 2).grid(row=3,column=0)
        cumRecButton4 = Radiobutton(self.firstPointFrame, text = "4  ", variable=  self.rangeBegin, value = 3).grid(row=4,column=0)

        self.lastPointFrame = Frame(self.startStopFrame, borderwidth=2, relief="sunken")
        self.lastPointFrame.grid(row = 0, column = 1, sticky=E)
        
        rangeEndLable = Label(self.lastPointFrame, text="Last Point").grid(row=0,column=0, sticky=N)
        cumRecButton1 = Radiobutton(self.lastPointFrame, text = "9   ", variable= self.rangeEnd, value = 8).grid(row=1,column=0)
        cumRecButton2 = Radiobutton(self.lastPointFrame, text = "10  ", variable= self.rangeEnd, value = 9).grid(row=2,column=0)
        cumRecButton3 = Radiobutton(self.lastPointFrame, text = "11  ", variable= self.rangeEnd, value = 10).grid(row=3,column=0)
        cumRecButton4 = Radiobutton(self.lastPointFrame, text = "12  ", variable= self.rangeEnd, value = 11).grid(row=4,column=0)

        self.responseButtonFrame = Frame(self.thresholdButtonFrame, borderwidth=2, relief="sunken")
        self.responseButtonFrame.grid(row = 50, column = 0, sticky = EW)

        self.responseCurveVar = BooleanVar(value = True)
        self.responseCurveCheckButton = Checkbutton(self.responseButtonFrame, text = "Show Response Curve", variable = self.responseCurveVar, \
                                        onvalue = True, offvalue = False).grid(row = 0, column = 0, columnspan = 2)
        
        respMaxLable = Label(self.responseButtonFrame, text="Response Max").grid(row=1,column = 0, sticky=(N))
        respMaxButton1 = Radiobutton(self.responseButtonFrame, text = "25   ", variable=self.respMax, value = 25).grid(row=2,column=0)
        respMaxButton2 = Radiobutton(self.responseButtonFrame, text = "50   ", variable=self.respMax, value = 50).grid(row=3,column=0)
        respMaxButton3 = Radiobutton(self.responseButtonFrame, text = "100   ", variable=self.respMax, value = 100).grid(row=2,column=1)
        respMaxButton4 = Radiobutton(self.responseButtonFrame, text = "200   ", variable=self.respMax, value = 200).grid(row=3,column=1)


        test1Button = Button(self.thresholdButtonFrame, text="Axes examples", command= lambda: \
                              self.testTHGraphicsDisplay_1()).grid(row=19,column=0,sticky=S)
        test2Button = Button(self.thresholdButtonFrame, text="Test Pmax calc", command= lambda: \
                              self.testTHGraphicsDisplay_2()).grid(row=20,column=0,sticky=S)
        test3Button = Button(self.thresholdButtonFrame, text="Test Button 3", command= lambda: \
                              self.testTHGraphicsDisplay_3()).grid(row=21,column=0,sticky=S)

        self.thresholdCanvas = Canvas(self.thresholdTab, width = canvas_width, height = canvas_height)
        self.thresholdCanvas.grid(row=0,column=1)
        self.thresholdCanvas.create_text(100,10,text = "Threshold Canvas")


        #*************** Text Tab ******************
        # self.columnFrame = Frame(self.graphTab, borderwidth=2, relief="sunken")
        # self.columnFrame.grid(column = 0, row = 0, columnspan= 1)
        
        self.textButtonFrame = Frame(self.textTab, borderwidth=5, relief="sunken")
        self.textButtonFrame.grid(column = 0, row = 0, sticky=N)
        cleartextButton = Button(self.textButtonFrame, text="Clear", command= lambda: \
                              self.clearText()).grid(row=0,column=0,sticky=N)
        self.textBox = Text(self.textTab, width=100, height=43)
        self.textBox.grid(column = 1, row = 0)
        summarytextButton = Button(self.textButtonFrame, text="Summary", command= lambda: \
                              self.summaryText()).grid(row=1,column=0,sticky=N)
        testText1Button = Button(self.textButtonFrame, text="Text Formatting Examples", command= lambda: \
                              self.testText1()).grid(row=2,column=0,sticky=N)
        testText2Button = Button(self.textButtonFrame, text="Test Button", command= lambda: \
                              self.testText2()).grid(row=3,column=0,sticky=N)
        intA_text_button = Button(self.textButtonFrame, text="IntA", command= lambda: \
                              self.intA_text()).grid(row=4,column=0,sticky=N)
        TH_text_button = Button(self.textButtonFrame, text="Threshold (TH)", command= lambda: \
                              self.threshold_text()).grid(row=4,column=0,sticky=N)

        #*************** bottom row ****************
        padding = 20
        radiobutton1 = Radiobutton(fileSelectorFrame, textvariable = self.fileName0, variable = self.fileChoice, \
                                   value = 0, command =lambda: self.selectList()).grid(column=0, row=2, padx=padding)
        radiobutton2 = Radiobutton(fileSelectorFrame, textvariable = self.fileName1, variable = self.fileChoice, \
                                   value = 1, command =lambda: self.selectList()).grid(column=1, row=2,padx=padding)
        radiobutton3 = Radiobutton(fileSelectorFrame, textvariable = self.fileName2, variable = self.fileChoice, \
                                   value = 2, command =lambda: self.selectList()).grid(column=2, row=2,padx=padding)
        radiobutton4 = Radiobutton(fileSelectorFrame, textvariable = self.fileName3, variable = self.fileChoice, \
                                   value = 3, command =lambda: self.selectList()).grid(column=3, row=2,padx=padding)
        radiobutton5 = Radiobutton(fileSelectorFrame, textvariable = self.fileName4, variable = self.fileChoice, \
                                   value = 4, command =lambda: self.selectList()).grid(column=4, row=2,padx=padding)
        radiobutton6 = Radiobutton(fileSelectorFrame, textvariable = self.fileName5, variable = self.fileChoice, \
                                   value = 5, command =lambda: self.selectList()).grid(column=0, row=3,padx=padding)
        radiobutton7 = Radiobutton(fileSelectorFrame, textvariable = self.fileName6, variable = self.fileChoice, \
                                   value = 6, command =lambda: self.selectList()).grid(column=1, row=3,padx=padding)
        radiobutton8 = Radiobutton(fileSelectorFrame, textvariable = self.fileName7, variable = self.fileChoice, \
                                   value = 7, command =lambda: self.selectList()).grid(column=2, row=3,padx=padding)
        radiobutton9 = Radiobutton(fileSelectorFrame, textvariable = self.fileName8, variable = self.fileChoice, \
                                   value = 8, command =lambda: self.selectList()).grid(column=3, row=3,padx=padding)
        radiobutton10 = Radiobutton(fileSelectorFrame, textvariable = self.fileName9, variable = self.fileChoice, \
                                   value = 9, command =lambda: self.selectList()).grid(column=4, row=3,padx=padding)

        #testRadiobutton1 = Radiobutton(self.rootFrame, text = "test1").grid(column=0, row=3)
        #testRadiobutton2 = Radiobutton(self.rootFrame, text = "test2").grid(column=1, row=4)
        


        # *************  The Controllers  **********
  

    def testText1(self):
        Examples.showTextFormatExamples(self.textBox)

    """
    def demandFunction(self, x, alpha, Qzero, k):
            y = np.e**(np.log(Qzero)+k*(np.exp(-alpha*Qzero*x)-1))
            return y
    """ 
    def demandFunction(self, x, alpha, Qzero):
            k = 4
            y = np.e**(np.log(Qzero)+k*(np.exp(-alpha*Qzero*x)-1))
            return y

    def testFunction(self, x, alpha):
            k = 4
            Qzero = self.scale_Q_zero.get()
            y = np.exp(np.log(Qzero)+k*(np.exp(-alpha*Qzero*x)-1))
            return y       
        
  
    def drawThreshold(self,aDataRecord):

        # price = 2.53, 4.49, 8.00, 14.23, 25.32, 42.55, 80.00, 142.86, 258.06, 444.44, 800.00, 1428.57
        # k
        # >>> math.log10(1428.57-4.49) = 3.15
        """
        Definitions from Hursch spreadsheet
        alpha: Essential value is the rate of change in log consumption with price
        Q0: Level of demand is indicated by the predicted consumption at a price of 0
        k: The range of the exponential demand curve from Q0 to minimum
        Pmax: The price at unit elasticity and at the peak of the response output function.
        Normalized price = (FR x Q0)/100 = Responses per 1 percent of Q0
        Normalized consumption = (Reinforcers/Q0) x 100 = Reinforcers as Percent of Q0


        Fletcher Cox pegged k at 4.18967505739766 - don't know why.
        Is this log or log10?
        0.001 is substituted for a zero - so our range (k) is probably 1 to 0.001 or four log units.


        """
        from scipy.optimize import curve_fit
        from scipy.stats.stats import pearsonr

        priceList = aDataRecord.priceList
        consumptionList = aDataRecord.consumptionList          

        x_zero = 100
        y_zero = 500
        x_pixel_width = 600
        y_pixel_height = 400
        xLogScaler = 3.0
        yLogScaler = 2.0
        max_x_scale = 1000         # price 
        response_max_x_scale = 120 # minutes
        x_divisions = 10
        max_y_scale = 2
        response_max_y_scale = self.respMax.get()
        y_divisions = 5
        leftLabel = True
        drawSymbol = True
        drawLine = False
        startRange = self.rangeBegin.get()
        endRange = self.rangeEnd.get()
        aCanvas = self.thresholdCanvas
        color = "black"
        logX = self.logXVar.get()
        logY = self.logYVar.get()
        x_startValue = 1            # used for Log scale; non-log defaults to 0
        y_startValue = 0.01 
        x_logRange = 3              # 3 Orders of magnitude: 1-1000
        y_logRange = 3              # 3 Orders of magnitude: 0.01-10

        x_caption = "Price (responses/mg cocaine)"
        y_caption = "Y"
        self.thresholdCanvas.delete('all')
        if logX : GraphLib.drawLog_X_Axis(aCanvas,x_zero,y_zero,x_pixel_width,x_startValue,x_logRange,x_caption)           
        else:     GraphLib.drawXaxis(aCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions, color)
        
        if logY:  GraphLib.drawLog_Y_Axis(aCanvas,x_zero,y_zero,y_pixel_height,y_startValue,y_logRange,y_caption)
        else:     GraphLib.drawYaxis(self.thresholdCanvas, x_zero,y_zero, y_pixel_height, max_y_scale, y_divisions,leftLabel)


        GraphLib.betaTestCurve(aCanvas,x_zero,y_zero,x_pixel_width,y_pixel_height, \
                               x_startValue, y_startValue, x_logRange, y_logRange, max_x_scale, max_y_scale, \
                               priceList, consumptionList, logX, logY, drawLine = False, color = "red")
        truncX = []
        truncY = []

        for t in range(startRange,endRange+1):    
            truncX.append(priceList[t])
            truncY.append(consumptionList[t])

        # Do this stuff if len(truncX) is > 0)
        # Else print message saying no file loaded
        """
            if self.curveFitVar.get():
            numpy_x_list = np.array(truncX)
            numpy_y_list = np.array(truncY)
            popt, pcov = curve_fit(self.demandFunction, numpy_x_list, numpy_y_list)
            alpha = popt[0]
            Qzero = popt[1]
            #k_value = popt[2]
            k_value = 4
            self.scale_alpha.set(alpha)
            self.scale_Q_zero.set(Qzero)
            self.scale_k.set(k_value)
            
        else:            
            alpha = self.scale_alpha.get()
            Qzero = self.scale_Q_zero.get()
            k_value = self.scale_k.get()
        """
        numpy_x_list = np.array(truncX)
        numpy_y_list = np.array(truncY)
        # setting k = 4 for everything

        if self.curveFitVar.get():
            popt, pcov = curve_fit(self.demandFunction, numpy_x_list, numpy_y_list)
            alpha = popt[0]
            Qzero = popt[1]
            k_value = 4
            self.scale_alpha.set(alpha)
            self.scale_Q_zero.set(Qzero)
            self.scale_k.set(k_value)
            
        else:            
            alpha = self.scale_alpha.get()
            Qzero = self.scale_Q_zero.get()
            # k_value = self.scale_k.get()
            # popt, pcov = curve_fit(self.demandFunction, numpy_x_list, numpy_y_list)
            k_value = 4


        # Calculate the correlation using only the points in the truncated list
        fitLine = []
        for i in range(0,len(truncX)):
            #y = self.demandFunction(truncX[i],alpha,Qzero,k_value)
            y = self.demandFunction(truncX[i],alpha,Qzero)
            fitLine.append(y)
        r = pearsonr(truncY,fitLine)
        label = "r = {:.3f}, N = {}".format(r[0],len(truncX))
        self.thresholdCanvas.create_text(300, 100, text=label)
        GraphLib.betaTestCurve(aCanvas, x_zero, y_zero, x_pixel_width, y_pixel_height, \
                               x_startValue, y_startValue, x_logRange, y_logRange, max_x_scale, max_y_scale, \
                               truncX, fitLine, logX, logY, drawSymbol = False, color = "blue")
                               # priceList, consumptionList, logX, logY, drawLine = False, color = "red")
        
        """
        Look for Pmax
        Bentzley et al. (2013) offers a formula for 1st derivative of the demand curve
        This formula is used to iterate through the line looking for a slope = 1.  
            slope = -alpha*Qzero*x*k*np.exp(-alpha*Qzero*x)
        same as:
            slope = -alpha*Qzero*x*k*np.e**(-alpha*Qzero*x)
        """
        verbose = False
        PmaxFound = False
        for x in range(10,500):
            if (PmaxFound != True):
                slope = -alpha*Qzero*x*k_value*np.exp(-alpha*Qzero*x)
                if verbose: 
                    if (slope < -0.9): print("slope at ",x," = ", slope)                
                if slope < -1.0:
                    Pmax = x 
                    Omax = self.demandFunction(x,alpha,Qzero)
                    PmaxFound = True
        if (PmaxFound):
            if logX:
                x_scaler = x_pixel_width / x_logRange
                PmaxX = GraphLib.get_logX_PixelValue(x_zero, Pmax, x_scaler, x_startValue)
                #PmaxX = (x_zero + (math.log(Pmax,10)*x_scaler)) // 1
            else:
                x_scaler = (x_pixel_width / max_x_scale)
                PmaxX = (x_zero + (Pmax * x_scaler)) // 1
            if logY:
                y_scaler = y_pixel_height / y_logRange
                OmaxY = GraphLib.get_logY_PixelValue(y_zero, Omax, y_scaler, y_startValue)
            else:
                y_scaler = (y_pixel_height / max_y_scale)
                OmaxY = (y_zero - (Omax * y_scaler)) // 1
             
            if self.showPmaxLine.get():
                aCanvas.create_line(PmaxX,y_zero,PmaxX,OmaxY,fill="red")
            if self.showOmaxLine.get():
                aCanvas.create_line(x_zero,OmaxY,PmaxX,OmaxY,fill="blue")
                
            alphaStr = "{:.6f}".format(alpha)
            QzeroStr = "{:.3f}".format(Qzero)
            OmaxStr  = "{:.3f}".format(Omax)
            # startRange and endRange anjusted from array index (0..11) to a [1..12]
            aCanvas.create_text(500, 80, fill="blue", text="Analysis of points "+str(startRange+1)+" to "+str(endRange+1))
            aCanvas.create_text(500, 100, fill="blue", text="Pmax = "+str(Pmax))
            aCanvas.create_text(500, 120, fill="blue", text="Qzero = "+QzeroStr)
            aCanvas.create_text(500, 140, fill="blue", text="Omax = "+OmaxStr)
            aCanvas.create_text(500, 160, fill="blue", text="Alpha = "+alphaStr)
            aCanvas.create_text(500, 180, fill="blue", text="k = "+str(k_value))
        
        GraphLib.eventRecord(self.thresholdCanvas, x_zero+50, y_zero-450, x_pixel_width-50, 120, aDataRecord.datalist, ["P"], "")
        
        if self.responseCurveVar.get():
            GraphLib.drawYaxis(self.thresholdCanvas, x_zero+x_pixel_width, y_zero, y_pixel_height, response_max_y_scale, y_divisions, False)
            GraphLib.betaTestCurve(aCanvas,x_zero,y_zero,x_pixel_width,y_pixel_height, \
                                   x_startValue, y_startValue, x_logRange, y_logRange, max_x_scale, response_max_y_scale, \
                                   aDataRecord.priceList,aDataRecord.responseList, logX, False, drawLine = True, color = "black")

    def testTHGraphicsDisplay_1(self):
        """
         Test the drawLogYAxis() function with various parameters
        """ 
        aCanvas = self.thresholdCanvas
        x_zero = 100
        y_zero = 550
        x_pixel_width = 600
        y_pixel_height = 500
        x_startValue = 0.001
        y_startValue = 0.001
        x_logRange = 5
        y_logRange = 5
        x_caption = "Price (responses/mg cocaine)"
        y_caption = "Y"
        #leftLabel = True
        GraphLib.drawLog_X_Axis(aCanvas,x_zero,y_zero,x_pixel_width,x_startValue,x_logRange,x_caption, test = True)
        GraphLib.drawLog_Y_Axis(aCanvas,x_zero,y_zero,y_pixel_height,y_startValue,y_logRange,y_caption, test = True)       
        x_zero = 200
        y_zero = 450
        x_pixel_width = 500
        y_pixel_height = 400
        x_startValue = 0.01
        y_startValue = 0.01
        x_logRange = 5
        logRange = 5
        GraphLib.drawLog_X_Axis(aCanvas,x_zero,y_zero,x_pixel_width,x_startValue,x_logRange,x_caption, test = True)
        GraphLib.drawLog_Y_Axis(aCanvas, x_zero,y_zero,y_pixel_height,y_startValue,y_logRange, y_caption, test = True)
        x_zero = 300
        y_zero = 350
        x_pixel_width = 400
        y_pixel_height = 300
        x_startValue = 0.1
        y_startValue = 0.1
        x_logRange = 2
        y_logRange = 2
        GraphLib.drawLog_X_Axis(aCanvas,x_zero,y_zero,x_pixel_width,x_startValue,x_logRange,x_caption)
        GraphLib.drawLog_Y_Axis(aCanvas,x_zero+x_pixel_width,y_zero,y_pixel_height,y_startValue,y_logRange,y_caption, test = True, leftLabel=False)
       

    def testTHGraphicsDisplay_2(self):
        """
        Bentxley et al. (2013) offers the following formula for 1st derivative so presumably:

        slope = -alpha*Qzero*x*k*np.exp(-alpha*Qzero*x)

        same as:

        slope = -alpha*Qzero*x*k*np.e**(-alpha*Qzero*x)

        """
        # these values from autofit of TH_BAZ15-033.txt
        alpha = 0.006474
        Qzero = 1.535
        k  =  4
        for x in range(30,40):
            print(x, -alpha*Qzero*x*k*np.exp(-alpha*Qzero*x))
        

    def testTHGraphicsDisplay_3(self):
        aCanvas = self.thresholdCanvas
        x_zero = 100
        y_zero = 550
        x_pixel_width = 600
        y_pixel_height = 500
        x_startValue = 1
        y_startValue = 0.01
        x_logRange = 3
        y_logRange = 3
        x_caption = "Price (responses/mg cocaine)"
        y_caption = "Y"
        #leftLabel = True
        GraphLib.drawLog_X_Axis(aCanvas,x_zero,y_zero,x_pixel_width,x_startValue,x_logRange,x_caption, test = True)
        GraphLib.drawLog_Y_Axis(aCanvas,x_zero,y_zero,y_pixel_height,y_startValue,y_logRange,y_caption, test = True)

        max_x_scale = 1000  # used if not log
        max_y_scale = 10    # used if not log
        xList = [3,10,30,100,300,1000]
        yList = [1,1,1,1,1,1]
        logX = True
        logY = True

        GraphLib.betaTestCurve(aCanvas, x_zero, y_zero, x_pixel_width, y_pixel_height, \
                               x_startValue, y_startValue, x_logRange, y_logRange, max_x_scale, max_y_scale, \
                               xList, yList, logX, logY, drawLine = False, color = "black")

        GraphLib.betaTestCurve(aCanvas, x_zero, y_zero, x_pixel_width, y_pixel_height, \
                               x_startValue, y_startValue, x_logRange, y_logRange, max_x_scale, max_y_scale, \
                               xList, yList, logX, logY, drawLine = True, color = "blue")


    def testText2(self):
        num = 0
        for pairs in self.recordList[self.fileChoice.get()].datalist:
            num = num + 1
            if num < 50:
                tempString = str(pairs[0])+" : "+pairs[1]
                self.textBox.insert(END,tempString+"\n")
        self.textBox.insert(END,"Number of data pairs = "+str(num)+"\n")


    def selectList(self):
        """
        Dummy function associated with radiobuttons that selects the filename textvariable.
        """
        # print("fileChoice: ", self.fileChoice.get())
        pass



    def openWakeFile(self, fileName):      
        global path
        if fileName == '':
            fileName = filedialog.askopenfilename()
        # print(fileName)
        if len(fileName) > 0:
            selected = self.fileChoice.get()
            self.recordList[selected].datalist = []
            name = fileName[fileName.rfind('/')+1:]
            path = fileName[0:fileName.rfind('/')+1]
            # print('path =',path)
            self.recordList[selected].fileName = name
            self.fileNameList[selected].set(name)
            self.recordList[selected].TH_PumpTimes = [3.162,1.780,1.000,0.562,0.316,0.188, \
                                                      0.100,0.056,0.031,0.018,0.010,0.0056]
            self.recordList[selected].cocConc = 5.0
            self.recordList[selected].pumpSpeed = 0.025 # Wake default 0.1 mls/4 sec = 0.025 / sec 
            # textBox.insert('1.0', name+" opened \n\n")
            if fileName.find(".str") > 0:
                self.recordList[selected].datalist = stream01.read_str_file(fileName)               
            elif fileName.find(".dat") > 0:
                aFile = open(fileName,'r')
                for line in  aFile:
                    pair = line.split()
                    pair[0] = int(pair[0])
                    self.recordList[selected].datalist.append(pair)
                aFile.close()
            self.recordList[selected].extractStatsFromList()

        # ------------  fillLists ---------
        verbose = True
        pumpStarttime = 0
        blockNum = -1 
        pumpOn = False
        leverTotal = 0       
        pumpTimeList = [0,0,0,0,0,0,0,0,0,0,0,0]     #Temp list of 12 pairs: price and total pump time
        responseList = [0,0,0,0,0,0,0,0,0,0,0,0]
        for pairs in self.recordList[selected].datalist:
            if pairs[1] == 'B':
                blockNum = blockNum + 1
            elif pairs[1] == 'P':
                pumpStartTime = pairs[0]
                pumpOn = True
                responseList[blockNum] = responseList[blockNum] + 1  # inc Bin_responses
                leverTotal = leverTotal + 1                        # using pump for responses
            elif pairs[1] == 'p':
                if pumpOn:
                    duration = pairs[0]-pumpStartTime
                    if blockNum <= 12:
                        pumpTimeList[blockNum] = pumpTimeList[blockNum] + duration
                    pumpOn = False
            # else no nothing
        # print("responseList = ", responseList)
        consumptionList = [0,0,0,0,0,0,0,0,0,0,0,0]
        mgPerSec = self.recordList[selected].cocConc * (self.recordList[selected].pumpSpeed * 0.001)
        if verbose:
            print("Cocaine Conc (mg/ml):", self.recordList[selected].cocConc)
            print("Pump Speed ( mls/msec):", self.recordList[selected].pumpSpeed)
            print("cocaine mg/sec:", mgPerSec)
        for i in range(12):
            consumptionList[i] = pumpTimeList[i] * mgPerSec
            if consumptionList[i] == 0:
                consumptionList[i] = 0.001  #so as not to have a zero value that would crash in a log function
        totalResp = 0
        totalIntake = 0
        for i in range(12):
            totalResp = totalResp + responseList[i]
            totalIntake = totalIntake + consumptionList[i]
        print('Total Intake = ',totalIntake,';  Total Responses = ',totalResp)
        priceList = []      
        for i in range(12):
            # dosePerResponse = pumptime(mSec) * mg/ml * ml/sec)
            dosePerResponse = self.recordList[selected].TH_PumpTimes[i] * \
                              self.recordList[selected].cocConc * \
                              (self.recordList[selected].pumpSpeed)
            price = round(1/dosePerResponse,2)
            priceList.append(price)
        self.recordList[selected].priceList = priceList
        self.recordList[selected].consumptionList = consumptionList
        self.recordList[selected].responseList = responseList

        # ------------- end fillLists -----------------
        print(self.recordList[selected])
    

    def clearCanvas(self):
        self.graphCanvas.delete('all')
                                   
    def drawCumulativeRecord(self,aRecord):
        self.clearCanvas()
        # print(aRecord)
        # canvas is 800 x 600
        x_zero = 50
        y_zero = 550
        x_pixel_width = 700                               
        y_pixel_height = 500
        x_divisions = 12
        max_x_scale = self.max_x_scale.get()
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        max_y_scale = self.max_y_scale.get()
        y_divisions = 10
        aTitle = aRecord.fileName
        # def cumRecord(aCanvas, x_zero, y_zero, x_pixel_width, y_pixel_height, max_x_scale, max_y_scale, datalist, aTitle)
        GraphLib.drawXaxis(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions)
        GraphLib.drawYaxis(self.graphCanvas, x_zero, y_zero, y_pixel_height, max_y_scale, y_divisions, True)
        GraphLib.cumRecord(self.graphCanvas, x_zero, y_zero, x_pixel_width, y_pixel_height, max_x_scale, max_y_scale, \
                           aRecord.datalist, self.showBPVar.get(), aTitle)

    def drawEventRecords(self):
        # canvas is 800 x 600
        self.clearCanvas()
        x_zero = 50
        x_pixel_width = 700
        x_divisions = 12
        max_x_scale = self.max_x_scale.get()
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        GraphLib.drawXaxis(self.graphCanvas, x_zero, 550, x_pixel_width, max_x_scale, x_divisions)
        y_zero = 30
        box = 0
        # eventRecord(aCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, datalist, charList, aLabel)
        # aTitle = aRecord.fileName
        for record in self.recordList:
            y_zero = y_zero + 40
            box = box + 1
            aTitle = "Box "+str(box)
            GraphLib.eventRecord(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, record.datalist, ["P"], aTitle)
        # print("event Records")

    def timeStamps(self,aRecord):
        self.clearCanvas()
        aCanvas = self.graphCanvas
        x_zero = 100
        y_zero = 400
        x_pixel_width = 650
        x_divisions = 12
        max_x_scale = self.max_x_scale.get()
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        GraphLib.drawXaxis(aCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions, color = "black")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-360, x_pixel_width, max_x_scale, aRecord.datalist, ["L"], "L1 active")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-340, x_pixel_width, max_x_scale, aRecord.datalist, [">"], "L1 inactive")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-310, x_pixel_width, max_x_scale, aRecord.datalist, ["J"], "L2 active")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-290, x_pixel_width, max_x_scale, aRecord.datalist, ["<"], "L2 inactive") 
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-260, x_pixel_width, max_x_scale, aRecord.datalist, ["P","p"], "Pump")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-230, x_pixel_width, max_x_scale, aRecord.datalist, ["S","s"], "Stim 1")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-210, x_pixel_width, max_x_scale, aRecord.datalist, ["C","c"], "Stim 2")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-180, x_pixel_width, max_x_scale, aRecord.datalist, ["=","."], "Lever 1")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-160, x_pixel_width, max_x_scale, aRecord.datalist, ["-",","], "Lever 2")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-130,  x_pixel_width, max_x_scale, aRecord.datalist, ["t","T"], "Timeout")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-100,  x_pixel_width, max_x_scale, aRecord.datalist, ["F"], "Food Tray")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-70,  x_pixel_width, max_x_scale, aRecord.datalist, ["B","b"], "Access")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-50,  x_pixel_width, max_x_scale, aRecord.datalist, ["H","h"], "Houselight")
        GraphLib.eventRecord(aCanvas, x_zero, y_zero-30,  x_pixel_width, max_x_scale, aRecord.datalist, ["G","E"], "Session")
        

    def threshold_text(self):
        aRecord = self.recordList[self.fileChoice.get()]
        aList = aRecord.datalist
        count = ListLib.count_char('L',aList)
        aString = 'Nunber of responses: '+str(count)
        self.textBox.insert(END,aString+"\n")
        
        count = ListLib.count_char('P',aList)
        aString = 'Nunber of injections: '+str(count)
        self.textBox.insert(END,aString+"\n")

        count = ListLib.count_char('B',aList)
        aString = 'Nunber of blocks: '+str(count)
        self.textBox.insert(END,aString+"\n")

        pump_count_list = ListLib.get_pump_count_per_block(aList)
        aString = 'Injections per block: '
        for item in pump_count_list:
            aString = aString + str(item) + ' '
        self.textBox.insert(END,aString+"\n")

        for b in range (12):    
            pump_duration_list = ListLib.get_pump_duration_list(aList, b)
            aString = 'Block '+str(b)+': '
            for i in range (len(pump_duration_list)):
                list_item = pump_duration_list[i]
                aString = aString + str(list_item[2]) + ' '
            self.textBox.insert(END,aString+"\n")
        #print("Block "+str(b), pump_duration_list)
        

    def intA_text(self):

        aRecord = self.recordList[self.fileChoice.get()]
        self.textBox.insert(END,aRecord.fileName+"\n")
        aList = aRecord.datalist

        count = ListLib.count_char('L',aList)
        aString = 'Number of Responses: '+str(count)
        self.textBox.insert(END,aString+"\n")

        count = ListLib.count_char('P',aList)
        aString = 'Number of Injections: '+str(count)
        self.textBox.insert(END,aString+"\n")

        count = ListLib.count_char('B',aList)
        aString = 'Number of Blocks: '+str(count)
        self.textBox.insert(END,aString+"\n")

        durations_list = ListLib.pump_durations_per_block(aList)
        print("Total durations per block:", durations_list)

        pump_duration_list = ListLib.get_pump_duration_list(aRecord.datalist, block = -1)
        print(pump_duration_list)     # prints a list of [pump_start_time, duration]  in mSec
        # pumptimes_per_bin = ListLib.get_pumptimes_per_bin(pump_timelist, bin_size = 5000)

        """
        # ***********************************************
        self.textBox.insert(END,"Total Pump Time (mSec): "+str(aRecord.totalPumpDuration)+"\n")
        self.textBox.insert(END,"Cummulative pump time per 5 second bin\n")
        aString = ""
        for t in range(len(pumptimes_per_bin)):
            aString = aString+str(pumptimes_per_bin[t])+' '
            #aString = aString + '{0:6d}'.format(pumptimes_per_bin[t])     
        self.textBox.insert(END,aString+"\n")
        total_pump_time = 0
        for t in range(len(pumptimes_per_bin)):
            total_pump_time = total_pump_time + pumptimes_per_bin[t]
        self.textBox.insert(END,"Total Pump Time (sum of bins): "+str(total_pump_time)+"\n")
        dose = (total_pump_time * 5 * 0.000025) / 0.33
        aString = "Total dose (mg/kg): {0:6.2f} mg/kg".format(dose)     # Format float to 2 decimal points in 6 character field
        self.textBox.insert(END, aString)
        """

    def IntA_event_records(self):
        # canvas is 800 x 600
        self.clearCanvas()
        aRecord = self.recordList[self.fileChoice.get()]
        x_zero = 75
        x_pixel_width = 600
        x_divisions = 12
        max_x_scale = 5
        x_divisions = 5
        GraphLib.drawXaxis(self.graphCanvas, x_zero, 550, x_pixel_width, max_x_scale, x_divisions)
        y_zero = 50
        for block in range(12):
            aTitle = str(block+1)
            pump_timestamps = ListLib.get_pump_timestamps(aRecord.datalist,block)
            GraphLib.eventRecord(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, pump_timestamps, ["P","p"], aTitle)
            y_zero = y_zero + 45

    def IntA_durations(self):
        '''

        '''
        aCanvas = self.graphCanvas
        self.clearCanvas()
        aRecord = self.recordList[self.fileChoice.get()]
        pump_timelist = ListLib.get_pump_duration_list(aRecord.datalist, -1)
        duration_list = []
        for data in pump_timelist:
            duration_list.append(data[2])
        x_zero = 75
        y_zero = 50
        x_pixel_width = 600
        x_divisions = 12
        max_x_scale = 5
        x_divisions = 5
        GraphLib.drawXaxis(aCanvas, x_zero, 550, x_pixel_width, max_x_scale, x_divisions)
        x_scaler = x_pixel_width / (max_x_scale*60*1000)
        y_zero = 50
        block = 0
        for block in range(12):
            x = x_zero
            y = y_zero
            aLabel = str(block+1)
            pump_timelist = ListLib.get_pump_duration_list(aRecord.datalist,block)
            aCanvas.create_text(x_zero-30, y_zero-5, fill="blue", text = aLabel) 
            for data in pump_timelist:
                newX = (x_zero + data[1] * x_scaler // 1)
                aCanvas.create_line(x, y, newX, y)
                height = int(data[2]/40)
                aCanvas.create_line(newX, y, newX, y-height)                        
                x = newX
            y_zero = y_zero + 45
            
        
    def IntAHistogram_blocks(self):
        '''

        '''
        self.clearCanvas()
        aRecord = self.recordList[self.fileChoice.get()]
        pump_total = 0
        for b in range (12):
            total_pump_time = 0
            pump_timelist = ListLib.get_pump_duration_list(aRecord.datalist, block = b)
            pumptimes_per_bin = ListLib.get_pumptimes_per_bin(pump_timelist, bin_size = 5000)
            for t in range(len(pumptimes_per_bin)):
                total_pump_time = total_pump_time + pumptimes_per_bin[t]
            pump_total = pump_total + total_pump_time
            y = (b*45)+50
            GraphLib.histogram(self.graphCanvas,pumptimes_per_bin, y_zero = y, y_pixel_height = 35, clear = False)
            self.graphCanvas.create_text(750, y, fill="blue", text = "Sum = "+str(total_pump_time))
            dose = (total_pump_time * 5 * 0.000025) / 0.33
            aString = "{0:6.2f} mg/kg".format(dose)     #eg. 4000 mSec * 5 mg/ml *0.000025 mls/mSec / 0.330 kg = 1.5 mg/kg
            self.graphCanvas.create_text(750, y + 12, fill="blue", text = aString)
        self.graphCanvas.create_text(750, y + 45, fill="blue", text = "Total "+str(pump_total))

    def IntAHistogram_all(self):
        self.clearCanvas()
        aRecord = self.recordList[self.fileChoice.get()]
        pump_total = 0
        x_zero = 75
        y_zero = 550
        x_pixel_width = 600
        y_pixel_height = 400
        max_x_scale = 300
        max_y_scale = 20000
        x_divisions = 5
        y_divisions = 10
        labelLeft = True
        GraphLib.drawYaxis(self.graphCanvas, x_zero, y_zero, y_pixel_height, max_y_scale, y_divisions, labelLeft, \
                  format_int = True, color = "black")
        pump_duration_list = ListLib.get_pump_duration_list(aRecord.datalist, block = -1)
        pumptimes_per_bin = ListLib.get_pumptimes_per_bin(pump_duration_list, bin_size = 5000)
        for t in range(len(pumptimes_per_bin)):
                pump_total = pump_total + pumptimes_per_bin[t]
        GraphLib.histogram(self.graphCanvas,pumptimes_per_bin, y_zero = 550, y_pixel_height = 400, clear = False, \
                           max_y_scale = 20000, y_divisions = 4)

        self.graphCanvas.create_text(300, 100, fill="blue", text = "Total Pump Time: "+str(pump_total))
        dose = (pump_total * 5 * 0.000025) / 0.33
        aString = "Total: {0:6.2f} mg/kg".format(dose)     # Format float to 2 decimal points in 6 character field
        self.graphCanvas.create_text(300, 130, fill="blue", text = aString)
        

    def showHistogram(self,aRecord, clear = True):
        """
        Draws a histogram using the datalist from aRecord.

        To Do: There is another histogram procedure in GraphLib. Should be merged. 

        """
        def drawBar(aCanvas,x,y, pixelHeight, width, color = "black"):
            aCanvas.create_line(x, y, x, y-pixelHeight, fill=color)
            aCanvas.create_line(x, y-pixelHeight, x+width, y-pixelHeight, fill=color)
            aCanvas.create_line(x+width, y-pixelHeight, x+width, y, fill=color)
        
        if clear:
            self.clearCanvas()          
        # Draw Event Record
        x_zero = 75
        y_zero = 100
        x_pixel_width = 700
        y_pixel_height = 200
        x_divisions = 12
        y_divisions = 5
        max_x_scale = self.max_x_scale.get()
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        self.graphCanvas.create_text(200, y_zero-50 , fill = "blue", text = aRecord.fileName)
        GraphLib.eventRecord(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, aRecord.datalist, ["P"], "")
        # Populate bin array
        binSize = 1   # in minutes
        intervals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        T1 = 0
        numInj = 0
        numIntervals = 0
        outOfRange = 0
        for pairs in aRecord.datalist:
            if pairs[1] == "P":
                numInj = numInj + 1
                T2 = pairs[0]
                if T1 > 0:
                    numIntervals = numIntervals + 1
                    interval = round((T2-T1)/(binSize*60000),1)   # rounded to a minute with one decimal point
                    index = int(interval)
                    if index < len(intervals)-1:
                        intervals[index] = intervals[index]+1
                    else:
                        outOfRange = outOfRange+1
                T1 = T2
        tempStr = "Number of Injections = "+str(numInj)
        self.graphCanvas.create_text(450, y_zero-50, fill = "blue", text = tempStr)
        # print("Number of Inter-injection Intervals =",numIntervals)
        print("Inter-injection Intervals = ",intervals)
        x_zero = 75
        y_zero = 450
        x_pixel_width = 400
        y_pixel_height = 300 
        max_x_scale = 20
        max_y_scale = 20
        x_divisions = 20
        y_divisions = max_y_scale
        labelLeft = True
        GraphLib.drawXaxis(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions, color = "black")
        GraphLib.drawYaxis(self.graphCanvas, x_zero, y_zero, y_pixel_height, max_y_scale, y_divisions, labelLeft, color = "black")
        # intervals = [0,1,2,3,4,5,6,5,4,3,2,1,0,0,0,0,0,0,0,1]  #Used for test without loading a file
        unitPixelHeight = int(y_pixel_height/y_divisions)
        width = int(x_pixel_width/len(intervals))
        for i in range(len(intervals)):           
            x = x_zero + (i*width)
            drawBar(self.graphCanvas,x,y_zero,intervals[i]*unitPixelHeight,width)
        #Draw OutOfRange Bar
        x = x_zero + (len(intervals)*width) + 20
        drawBar(self.graphCanvas,x,y_zero,outOfRange*unitPixelHeight,width)
        tempStr = "Each Bin = "+str(binSize)+" minute"
        self.graphCanvas.create_text(250, y_zero+50, fill = "blue", text = tempStr)
        

    def showModel(self,aRecord, resolution = 60, aColor = "blue", clear = True, max_y_scale = 25):
        if clear:
            self.clearCanvas()
        x_zero = 75
        y_zero = 350
        x_pixel_width = 700
        y_pixel_height = 200
        x_divisions = 12
        y_divisions = 5
        max_x_scale = self.max_x_scale.get()
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        # max_y_scale = self.max_y_scale.get()
        # max_y_scale = 25
        GraphLib.eventRecord(self.graphCanvas, x_zero, 100, x_pixel_width, max_x_scale, aRecord.datalist, ["P"], "Test")
        GraphLib.drawXaxis(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions, color = "red")
        GraphLib.drawYaxis(self.graphCanvas, x_zero, y_zero, y_pixel_height, max_y_scale, y_divisions, True, color = "blue")
        x_scaler = x_pixel_width / (max_x_scale*60*1000)
        y_scaler = y_pixel_height / max_y_scale
        cocConcXYList = model.calculateCocConc(aRecord.datalist,aRecord.cocConc, aRecord.pumpSpeed, resolution)
        # print(modelList)
        x = x_zero
        y = y_zero
        totalConc = 0
        totalRecords = 0
        startAverageTime = 10 * 60000    # 10 min
        endAverageTime = 120 * 60000     # 120 min
        for pairs in cocConcXYList:
            if pairs[0] >= startAverageTime:
                if pairs[0] < endAverageTime:
                    totalRecords = totalRecords + 1
                    totalConc = totalConc + pairs[1]
            concentration = round(pairs[1],2)
            newX = x_zero + pairs[0] * x_scaler // 1
            newY = y_zero - concentration * y_scaler // 1
            self.graphCanvas.create_line(x, y, newX, newY, fill= aColor)
            # self.graphCanvas.create_oval(newX-2, newY-2, newX+2, newY+2, fill=aColor)
            x = newX
            y = newY
        self.graphCanvas.create_text(300, 400, fill = "blue", text = aRecord.fileName)
        """
        dose = 2.8*aRecord.cocConc * aRecord.pumpSpeed
        tempStr = "Duration (2.8 sec) * Pump Speed ("+str(aRecord.pumpSpeed)+" ml/sec) * cocConc ("+str(aRecord.cocConc)+" mg/ml) = Unit Dose "+ str(round(dose,3))+" mg/inj"
        self.graphCanvas.create_text(300, 450, fill = "blue", text = tempStr)
        """
        averageConc = round((totalConc/totalRecords),3)
        # draw average line
        X1 = x_zero + (startAverageTime * x_scaler) // 1
        Y  = y_zero-((averageConc) * y_scaler) // 1
        X2 = x_zero + (endAverageTime * x_scaler) // 1
        self.graphCanvas.create_line(X1, Y, X2, Y, fill= "red")
        tempStr = "Average Conc (10-120 min): "+str(averageConc)
        self.graphCanvas.create_text(500, Y, fill = "red", text = tempStr)
        

    def testModel(self):
        WakePumpTimes = [3.162,1.780,1.000,0.562,0.316,0.188,0.100,0.056,0.031,0.018,0.010,0.0056]
        """
        This compares the same dose over 3 different time periods 5,25 and 50 sec
        It does this by changing the concentration, but perhpas it would be
        better to change the pump speed.

        eg. 5000 mSec * 4 mg/ml *0.000025 mls/mSec / 0.330 kg = 1.5 mg/kg
        # model.calculateCocConc defaults to bodyweight 0.330 

        """        
        # testRecord1  5 sec infusion
        testRecord1 = DataRecord([],"5 sec") 
        testRecord1.datalist = [[10000, 'P'],[15000, 'p']]
        testRecord1.pumpSpeed = 0.025   # Wake default 0.1 mls/4 sec = 0.025 / sec
        testRecord1.cocConc = 4.0
        testRecord1.TH_PumpTimes = WakePumpTimes
        testRecord1.extractStatsFromList()
        duration = testRecord1.totalPumpDuration
        dose = (testRecord1.totalPumpDuration * testRecord1.cocConc * (testRecord1.pumpSpeed/1000)/0.330)
        print("testRecord1 Duration = {0}; Total Dose = {1:2.1f}".format(duration,dose))
        # testRecord2  50 sec infusion
        duration = 50
        testRecord2 = DataRecord([],"50 sec") 
        testRecord2.datalist = [[10000, 'P'],[15000, 'p'], [15000, 'P'],[20000, 'p'], \
                                [20000, 'P'],[25000, 'p'], [25000, 'P'],[30000, 'p'], \
                                [30000, 'P'],[35000, 'p'], [35000, 'P'],[40000, 'p'], \
                                [40000, 'P'],[45000, 'p'], [45000, 'P'],[50000, 'p'], \
                                [50000, 'P'],[55000, 'p'], [55000, 'P'],[60000, 'p']]                          
        testRecord2.pumpSpeed = 0.025   # Wake default 0.1 mls/4 sec = 0.025 / sec
        testRecord2.cocConc = 4.0 / (duration / 5.0)
        testRecord2.TH_PumpTimes = WakePumpTimes
        testRecord2.extractStatsFromList()
        duration = testRecord2.totalPumpDuration
        dose = (testRecord2.totalPumpDuration * testRecord2.cocConc * (testRecord2.pumpSpeed/1000)/0.330)
        print("testRecord2 Duration = {0}; Total Dose = {1:2.1f}".format(duration,dose))
        # testRecord3  90 sec infusion
        duration = 90
        testRecord3 = DataRecord([],"90 sec") 
        testRecord3.datalist = [[10000, 'P'],[15000, 'p'], [15000, 'P'],[20000, 'p'], \
                                [20000, 'P'],[25000, 'p'], [25000, 'P'],[30000, 'p'], \
                                [30000, 'P'],[35000, 'p'], [35000, 'P'],[40000, 'p'], \
                                [40000, 'P'],[45000, 'p'], [45000, 'P'],[50000, 'p'], \
                                [50000, 'P'],[55000, 'p'], [55000, 'P'],[60000, 'p'], \
                                [60000, 'P'],[65000, 'p'], [65000, 'P'],[70000, 'p'], \
                                [70000, 'P'],[75000, 'p'], [75000, 'P'],[80000, 'p'], \
                                [80000, 'P'],[85000, 'p'], [85000, 'P'],[90000, 'p'], \
                                [90000, 'P'],[95000, 'p'], [95000, 'P'],[100000, 'p']]
        testRecord3.pumpSpeed = 0.025   # Wake default 0.1 mls/4 sec = 0.025 / sec
        testRecord3.cocConc = 4.0 / (duration / 5.0)
        testRecord3.TH_PumpTimes = WakePumpTimes
        testRecord3.extractStatsFromList()
        duration = testRecord3.totalPumpDuration
        dose = (testRecord3.totalPumpDuration * testRecord3.cocConc * (testRecord3.pumpSpeed/1000)/0.330)
        print("testRecord3 Duration = {0}; Total Dose = {1:2.1f}".format(duration,dose))

        self.showModel(testRecord1, resolution = 5, aColor = "black", max_y_scale = 10)
        self.showModel(testRecord2, resolution = 5, aColor = "red", clear = False, max_y_scale = 10)
        self.showModel(testRecord3, resolution = 5, aColor = "blue", clear = False, max_y_scale = 10)

    def test(self):
        self.clearCanvas()
        x_zero = 50
        y_zero = 550
        x_pixel_width = 700                               
        y_pixel_height = 500
        max_x_scale = self.max_x_scale.get()
        x_divisions = 12
        if (max_x_scale == 10) or (max_x_scale == 30): x_divisions = 10
        max_y_scale = self.max_y_scale.get()        
        y_divisions = 10
        GraphLib.drawXaxis(self.graphCanvas, x_zero, y_zero, x_pixel_width, max_x_scale, x_divisions, color = "red")
        offset = 0      
        GraphLib.drawYaxis(self.graphCanvas, x_zero, y_zero, y_pixel_height, max_y_scale, y_divisions, True, color = "blue")
        GraphLib.drawYaxis(self.graphCanvas, x_zero+x_pixel_width +10, y_zero, y_pixel_height, max_y_scale, y_divisions, False)

    def loadZimmerFile(self):
        selected = self.fileChoice.get()    
        aFileName = "/Users/daveroberts/Dropbox/Programming/Python/Analysis101/TH_ BAZ15-033.txt"
        #             /Users/daveroberts/Dropbox/Programming/Python/Analysis101/TH_BAZ15-033.txt  
        aFileName = filedialog.askopenfilename()
        print(aFileName)
        self.recordList[selected] = self.getZimmerFile(self.recordList[selected],aFileName)
        self.recordList[selected].extractStatsFromList()
        print(self.recordList[selected])
        self.fileNameList[selected].set(self.recordList[selected].fileName)
        
        
    def getZimmerFile(self,aDataRecord,aFileName):
    
        """
        A data record is passed in (which may or may not be empty). It is reset
        then filled with data from a chosen file and returned.
 
        Notes: 
        Uses the D: field to discriminate an FR1 file from a TH file.
        If it is an FR1 file it substitutes a pump time of 5 sec - probably wrong...
        If it is a TH file it uses the array of pumptimes.
        The pump times are preassigned and NOT read from the datafile

        To Do: Because values of zero throw errors in log functions, every log function needs
           to check and handle such data, or (perhaps in the interim) the data file should substitute
           0.00001 for any zero value (as often happens in the last consumption bin)
        
        Parsing the injections listed in Q: into bins matches the totals listed in H: 

        Codes for Zimmer files
    
        A = Active responses
        B = Infusions
        C = Inactive responses
      * D = List for pump times   
      * H = Number of infusions per 10 minute bin
      * I = Number of ResponsconsumptionListes per 10 minute bin
      * J = Number of Inactive responses per 10 minute bin

        M = Session duration (minutes)
      * N = 10 min counter
      * P = Time that pump, cue lights, and tone are on  
        Q = Time (in seconds) of each infusion
        R = Time (in seconds) of each response
        S = Each infusion duration (in centiseconds)
        U = Time out (seconds)
        W = Weight of animal - ignore
        X = Subscript for Q array - ignore
        Y = Subscript for R array - ignore
 
       * = used in TH file
    
       """
        # empty dataRecord
        aDataRecord.fileName = "Zimmer test"
        aDataRecord.numberOfL1Responses = 0
        aDataRecord.numberOfL2Responses = 0
        aDataRecord.numberOfInfusions = 0
        aDataRecord.totalPumpDuration = 0
        #   Check these assumptions
        #   These are values provided by Brandon (I think)
        #   MUSC: 2.73 mg/ml * 0.0000176 mls/mSec = 0.000048048 mg/mSec
        #   WAKE: 5 mg/ml * 0.000025 = 0.000125 mg/mSec 
        aDataRecord.cocConc = 2.73
        aDataRecord.pumpSpeed = 0.0176
        aDataRecord.averagePumpTime = 0.0
        # For comparison:
        # WakePumpTimes = [3.162,1.780,1.000,0.562,0.316,0.188,0.100,0.056,0.031,0.018,0.010,0.0056]
        aDataRecord.TH_PumpTimes = [8.175,4.597,2.585,1.454,0.818,0.460,0.259,0.145,0.082,0.046,0.026,0.0146]
        aDataRecord.priceList = []
        aDataRecord.consumptionList = []
        aDataRecord.deltaList = []
        aDataRecord.notes = "Zimmer file"
        """
          A: and B: contain the number of active responses and infusions respectively. These should be
          the same, but they are not. So, as a first pass, this analysis uses the injection data only.
          That is, the program uses the timestamps for the infusions and counts it as a pump time and
          a response time. 
        """
        sectionStartIdentfier = "Q:"
        sectionEndIdentifier = "R:"
        directory = os.path.split(aFileName)[0]
        fileName = os.path.split(aFileName)[1]
        # print(fileName)
        aDataRecord.fileName = fileName
        tempList = []
        # print("Looking for section preceded by "+sectionStartIdentfier+" in "+fileName+"\n")
        dataPoints = 0
        lineNumber = 0
        sectionIdentified = False
        FR1_File = False
        with open(aFileName) as myOpenFile:    # aFileName is complete string passed to procedure
            for line in myOpenFile:            # This runs through the file one line at a time
                lineNumber = lineNumber + 1            # count the lines
                if "D:       0.000" in line:   # This is used to descriminate between FR1 and TH files.
                    FR1_File = True            
                elif sectionStartIdentfier in line:  # if it finds "Q:" then it knows that it is in the right section of the datafile
                    sectionIdentified = True           
                    # print("Infusion data ('Q:') begins at line ", lineNumber)
                elif (sectionIdentified):   # If True, it should be in the right section and trying to parse the data 
                    if line[0] == " ":      # Looks for an indented section of text by checking that the first character is a space. 
                        numberList = line.split()               # splits the line up into a "list" of text values (turned into numbers later)
                        for dataNumber in numberList:           # goes through each "number" in the list (they are actually strings)
                            if dataNumber.find(".") > 0:        # It ignores "numbers" that doesn't have a decimal point - i.e. the 1st number
                                data = float(dataNumber)        # Convert the text value into a float (number with a decimal value)
                                time = int(data*1000)           # time in mSec
                                pair = [time, "P"]              # Cteate a timestamp pair: "Pump On" timestamp
                                tempList.append(pair)           # Add to list
                                pair = [time, "L"]              # Lever response timestamp
                                tempList.append(pair)
                                blockNum = int(time/600000)
                                if FR1_File:
                                    time = time+5000            # Pump Off time stamp. 
                                else:
                                    time = time+(aDataRecord.TH_PumpTimes[blockNum]*1000)   # Get pump duration from pump time array
                                pair = [time, "p"]
                                tempList.append(pair)
                                dataPoints = dataPoints + 1     # Count number of data points                     
                    elif sectionEndIdentifier in line:          # Look for end of section i.e. "R:"
                        sectionIdentified = False
            myOpenFile.close()
            print("Found", dataPoints,"dataPoints in Zimmer file:", fileName)
            aDataRecord.datalist = tempList

    
            """
            There are two ways to calculate cocaine consumption during the bins.
      
            Option 1 assumes that timestamp data stream contained all the information,
            such as the beginning and end of each Block ("B","b") and pump interval ("P","p").
            This would tie the analysis directly to the data and would be able to handle situations in
            which the interval length was changed (eg. 10 to 5 or 12 min) or the pumptimes were altered.

            Option 2. Unfortunately, not all datastreams contain this information. The "work around" is to calculate
            everything using only the pump start times. The duration of each infusion is calculated from the
            pumptime list which is assigned when the datastream is loaded. This option assumes that the pumptime list
            is accurate and that the bin length is always 10 min.

            """

            pumpStarttime = 0
            blockNum = -1 
            pumpOn = False
            leverTotal = 0       
            pumpTimeList = [0,0,0,0,0,0,0,0,0,0,0,0]     #Temp list of 12 pairs: price and total pump time
            aDataRecord.responseList = [0,0,0,0,0,0,0,0,0,0,0,0]
            aDataRecord.consumptionList = [0,0,0,0,0,0,0,0,0,0,0,0]
            aDataRecord.priceList = [0,0,0,0,0,0,0,0,0,0,0,0]
            for pairs in aDataRecord.datalist:              # Fill pumpTimeList and responseList
                if pairs[1] == 'P':
                    time = pairs[0]
                    blockNum = int(time/600000)
                    aDataRecord.responseList[blockNum] = aDataRecord.responseList[blockNum] + 1  # inc Bin_responses
                    leverTotal = leverTotal + 1                          # using pump for responses
                    duration = aDataRecord.TH_PumpTimes[blockNum]
                    pumpTimeList[blockNum] = pumpTimeList[blockNum] + duration                     
            mgPerSec = aDataRecord.cocConc * aDataRecord.pumpSpeed
            for i in range(12):
                aDataRecord.consumptionList[i] = pumpTimeList[i] * mgPerSec
            
            for i in range(12):
                # dosePerResponse = pumptime(mSec) * mg/ml * ml/sec)
                dosePerResponse = aDataRecord.TH_PumpTimes[i] * aDataRecord.cocConc * aDataRecord.pumpSpeed
                price = round(1/dosePerResponse,2)
                aDataRecord.priceList[i] = price

            return aDataRecord         

    

    # ******************** End Draw Threshold ***********

    def clearText(self):
        self.textBox.delete("1.0",END)

    def summaryText(self):
        # print(dataRecordList[self.fileChoice.get()])    # This will print to the Python Shell 
        self.textBox.insert("1.0",self.recordList[self.fileChoice.get()])
        #self.textBox.insert("1.0","summary text")

    def periodic_check(self):
        thisTime = datetime.now()
        self.clockTimeStringVar.set(thisTime.strftime("%H:%M:%S"))        
        self.root.after(100, self.periodic_check)               

    def go(self):
        self.root.after(100, self.periodic_check)
        self.root.mainloop()
        

if __name__ == "__main__":
    sys.exit(main())  

