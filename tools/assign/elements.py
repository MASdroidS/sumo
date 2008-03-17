#!/usr/bin/env python
# This script is to define the required network geometric classes 
# and the functions for calculating link characteristics, such as capacity, travel time and link cost function.

import os, random, string, sys

# Vertex class which stores incoming and outgoing edges as well as
# auxiliary data for the flow computation. The members are accessed
# directly.

class Predecessor:

    def __init__(self, edge, pred, distance):
        self.edge = edge
        self.pred = pred
        self.distance = distance
        
class Vertex:

    def __init__(self, num):
        self.inEdges = set()
        self.outEdges = set()
        self.label = "temp_%s" % num
        self.preds = []
        self.wasUpdated = False
    
    def __repr__(self):
        return self.label
        
    def _addNewPredecessor(self, edge, updatePred, newPreds):
        for pred in newPreds:
            if pred.pred == updatePred:
                return
        newPreds.append(Predecessor(edge, updatePred,
                                    updatePred.distance + edge.actualtime))

    def update(self, KPaths, edge):
        updatePreds = edge.source.preds
        if len(self.preds) == KPaths\
           and updatePreds[0].distance + edge.actualtime >= self.preds[KPaths-1].distance:
            return False
        newPreds = []
        updateIndex = 0
        predIndex = 0
        while len(newPreds) < KPaths\
              and (updateIndex < len(updatePreds)\
                   or predIndex < len(self.preds)):
            if predIndex == len(self.preds):
                self._addNewPredecessor(edge, updatePreds[updateIndex], newPreds)
                updateIndex += 1
            elif updateIndex == len(updatePreds):
                newPreds.append(self.preds[predIndex])
                predIndex += 1
            elif updatePreds[updateIndex].distance + edge.actualtime < self.preds[predIndex].distance:
                self._addNewPredecessor(edge, updatePreds[updateIndex], newPreds)
                updateIndex += 1
            else:
                newPreds.append(self.preds[predIndex])
                predIndex += 1
        if predIndex == len(newPreds): # no new added
            return False
        self.preds = newPreds
        returnVal = not self.wasUpdated
        self.wasUpdated = True
        return returnVal


# Edge class which stores start and end vertex, type amd label of the edge
# as well as flow and capacity for the flow computation and some parameters
# read from the net. The members are accessed directly.
class Edge:
    def __init__(self, label, source, target, kind="junction"):
        self.label = label
        self.source = source
        self.target = target
        self.capacity = sys.maxint
        self.flow = 0.0
        self.kind = kind
        self.maxspeed = 1.0                                # default value : 14 m/s (50 kmh)
        self.length = 0.0
        self.numberlane = 0
        self.freeflowtime = 0.0                            
        self.estcapacity = 0.0                             # default value: 1500 vehicles per lane                             
        self.CRcurve = ''
        self.actualtime = 0.0
        self.weight = 0.0
        self.connection = 0
        self.edgetype = None
        self.helpflow = 0.0     
        
    def __repr__(self):
        cap = str(self.capacity)
        if self.capacity == sys.maxint or self.connection == 1:
            cap = "inf"
        return "%s_%s<%s|%s|%s|%s|%s|%s|%s|%s|%s>" % (self.kind, self.label, self.source, self.target,
                                                      self.flow, self.length, self.numberlane,
                                                      self.CRcurve, self.estcapacity, cap, self.weight)

    def getFFTT(self):
        if str(self.source) == str(self.target):
            self.freeflowtime = 0.0
        else:
            self.freeflowtime = self.length / self.maxspeed
        return self.freeflowtime
                
    def getDefaultESTCAP(self, parfile):
        f = file(parfile)
        for line in f:
            p = line.split()
            periods = int(p[len(p)-2])
        self.estcapacity = float(self.numberlane * 1500) * periods           # The respective rules will be developed accroding to the HBS. 

        return self.estcapacity

    # modified CR-curve database defined in the Validate files
    def getAppCapacity(self, parfile):
        f = file(parfile)
        for line in f:
            p = line.split()
            periods = int(p[(len(p)-2)])
        if self.numberlane > 0:
            if self.maxspeed > 38.0:
                self.estcapacity = float(self.numberlane * 1500) * periods     # 16 intervals in the test network in Magdeburg
                if self.numberlane <= 2:
                    self.edgetype = '14'
                elif self.numberlane == 3:
                    self.edgetype = '10'
                elif self.numberlane >= 4:
                    self.edgetype = '6'
            if self.maxspeed > 34.0 and self.maxspeed <= 38.0:
                self.estcapacity = float(self.numberlane * 1500) * periods
                if self.numberlane == 2:
                    self.edgetype = '15'
                elif self.numberlane == 3:
                    self.edgetype = '11'
                elif self.numberlane >= 4:
                    self.edgetype = '7'
            if self.maxspeed > 33.0 and self.maxspeed <= 34.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '26'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '23'
                elif self.numberlane >= 3:
                    self.estcapacity = float(self.numberlane * 1500) * periods
                    self.edgetype = '20'
            if self.maxspeed > 30.0 and self.maxspeed <= 33.0:
                self.estcapacity = float(self.numberlane * 1400) * periods
                if self.numberlane <= 2:        
                    self.edgetype = '16'
                if self.numberlane == 3:
                    self.edgetype = '12'
                elif self.numberlane >= 3:
                    self.edgetype = '8'
            if self.maxspeed > 29.0 and self.maxspeed <= 30.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1350) * periods       
                    self.edgetype = '18'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1500) * periods
                    self.edgetype = '24'
                elif self.numberlane >= 3:
                    self.estcapacity = float(self.numberlane * 1500) * periods
                    self.edgetype = '21'
            if self.maxspeed > 27.0 and self.maxspeed <= 29.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1350) * periods       
                    self.edgetype = '64'
                if self.numberlane >= 2:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '61'
            if self.maxspeed >= 25.0 and self.maxspeed <= 27.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1350) * periods       
                    self.edgetype = '19'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '17'
                if self.numberlane == 3:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '13'
                if self.numberlane >= 4:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '9'
            if self.maxspeed > 22.0 and self.maxspeed < 25.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1300) * periods
                    self.edgetype = '29'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1300) * periods
                    self.edgetype = '33'
                if self.numberlane >= 3:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '30'
            if self.maxspeed > 19.0 and self.maxspeed <= 22.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1200) * periods
                    self.edgetype = '37'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1350) * periods
                    self.edgetype = '34'
                if self.numberlane >= 3:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '31'
            if self.maxspeed > 18.0 and self.maxspeed <= 19.0:
                self.estcapacity = float(self.numberlane * 1300) * periods
                self.edgetype = '84'
            if self.maxspeed > 16.0 and self.maxspeed <= 18.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1200) * periods
                    self.edgetype = '38'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1300) * periods
                    self.edgetype = '35'
                if self.numberlane == 3:
                    self.estcapacity = float(self.numberlane * 1300) * periods
                    self.edgetype = '32'
                if self.numberlane >= 4:
                    self.estcapacity = float(self.numberlane * 1100) * periods
                    self.edgetype = '40'
            if self.maxspeed > 15.0 and self.maxspeed <= 16.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1000) * periods
                    self.edgetype = '47'
                if self.numberlane >= 2:
                    self.estcapacity = float(self.numberlane * 1100) * periods
                    self.edgetype = '44'
            if self.maxspeed > 13.0 and self.maxspeed <= 15.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 1200) * periods
                    self.edgetype = '39'
                if self.numberlane == 2:
                    self.estcapacity = float(self.numberlane * 1050) * periods
                    self.edgetype = '45'
                if self.numberlane >= 3:
                    self.estcapacity = float(self.numberlane * 1110) * periods
                    self.edgetype = '42'
            if self.maxspeed > 12.0 and self.maxspeed <= 13.0:
                self.estcapacity = float(self.numberlane * 800) * periods
                if self.numberlane == 1: 
                    self.edgetype = '49'
                if self.numberlane == 2:
                    self.edgetype = '86'
            if self.maxspeed > 11.0 and self.maxspeed <= 12.0:
                if self.numberlane == 1: 
                    self.estcapacity = float(self.numberlane * 800) * periods
                    self.edgetype = '83'
                if self.numberlane >= 2:
                    self.estcapacity = float(self.numberlane * 1000) * periods
                    self.edgetype = '75'
            if self.maxspeed > 9.0 and self.maxspeed <= 11.0:
                if self.numberlane == 1:
                    self.estcapacity = float(self.numberlane * 800) * periods
                    self.edgetype = '89'
                if self.numberlane >= 2:
                    self.estcapacity = float(self.numberlane * 1400) * periods
                    self.edgetype = '87'
            if self.maxspeed > 8.0 and self.maxspeed <= 9.0:
                self.estcapacity = float(self.numberlane * 800) * periods
                self.edgetype = '79'
            if self.maxspeed <= 8.0:
                self.estcapacity = float(self.numberlane * 200) * periods
                self.edgetype = '94'

    def getCRcurve(self):
        self.CRcurve =''
        if self.edgetype != None:
            if int(self.edgetype) <= 5:
                    self.CRcurve = 'CR12'
                    self.estcapacity = 0.                    
            elif int(self.edgetype) >= 6 and int(self.edgetype) <= 19:
                    self.CRcurve = 'CR1'
            elif int(self.edgetype) >= 20 and int(self.edgetype) <= 49:
                    self.CRcurve = 'CR2'
            elif int(self.edgetype) >= 50 and int(self.edgetype) <= 79:
                    self.CRcurve = 'CR3'
            elif int(self.edgetype) >= 80 and int(self.edgetype) <= 89:
                    self.CRcurve = 'CR4'
            elif int(self.edgetype) >= 90 and int(self.edgetype) <= 93:
                    self.CRcurve = 'CR5'
            elif int(self.edgetype) >= 94 and int(self.edgetype) <= 99:
                    self.CRcurve = 'CR6'
                    
# Function for calculating/updating link travel time
    def getACTTT(self, curvefile):        
        foutcheck = file('time_flow.txt', 'a')
        f = file(curvefile)
        for line in f:
            itemCR = line.split()
            if itemCR[0] == self.CRcurve:
                if self.flow == 0.0 or self.connection == 1 or self.numberlane == 0 or str(self.source) == str(self.target):         # self.flow = 0: at free-flow speed; self.numberlane =0: connection link
                    self.actualtime = self.freeflowtime
                else:
                    if self.estcapacity == 0.0:
                        foutcheck.write('edge.label=%s: estcapacity=0\n' %(self.label))
                    else:
                        self.actualtime = self.freeflowtime*(1+(float(itemCR[1])*(self.flow/(self.estcapacity*float(itemCR[3])))**float(itemCR[2])))
                if self.flow > self.estcapacity and self.connection != 1 and str(self.source) != str(self.target):
                    self.actualtime = self.actualtime*1.2           # travel time penalty (need to be modified)
                    foutcheck.write('************edge.label="%s": acutaltime is timed by 1.2.\n' %(self.label))
        f.close()
        foutcheck.close()        
        return self.actualtime
              
# Vehilce class: the origin, destination, links, path travel time, path length and path flow will be stored in the Path class.
class Vehicle:
    def __init__(self, label):
        self.label = label
        self.depart = 0.
        self.arrival = 0.       
        self.speed = 0.
        self.route = []
        self.traveltime = 0.
        self.travellength = 0.

    def __repr__(self):
        return "%s_%s_%s_%s_%s_%s<%s>" % (self.label, self.depart, self.arrival, self.speed, self.traveltime, self.travellength, self.route)
        
pathNum = 0
        
# Path class: the origin, destination, links, path travel time, path length and path flow will be stored in the Path class.
class Path:
    def __init__(self):
        self.source = None
        self.target = None
        self.label = "%s" % pathNum    #Pfad_
        global pathNum
        pathNum += 1
        self.Edges = []
        self.freepathtime = 0.0
        self.actpathtime = 0.0
        self.pathflow = 0.0
        self.helpflow = 0.0
        self.commfactor = 0.0
        self.choiceprob = 0.0
    
    def __repr__(self):
#        return "%s_%s<%s|%s|%s|%s|%s|%s>" % (self.label, self.source, self.target, self.pathflow, 
#                                             self.actpathtime, self.commfactor, self.choiceprob, self.Edges) 
        return "%s_%s_%s<%s|%s|%s|%s>" % (self.label, self.source, self.target, self.freepathtime, self.pathflow, self.actpathtime, self.Edges)

    def UpdatePathActTime(self, net):
        self.actpathtime = 0.
        for edge in self.Edges:
            self.actpathtime += edge.actualtime
