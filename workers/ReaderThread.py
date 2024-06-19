from twisted.internet import protocol, reactor, endpoints, task
from twisted.protocols.policies import TimeoutMixin
from datetime import datetime
from datetime import datetime
from workers.Worker import *
from aux.COMLink import *
from aux.HWDetector import *

import threading
import time
import queue
import base64
import json
import struct
import traceback
import sys
import os


class ReaderThread(Worker):
     def __init__( self, com_link, owner ):
         Worker.__init__( self, "ReaderThread", owner )
         self.owner = owner
         self.com_link = com_link
         self.spooled_up = 0
         self.hw_version = 0
         self.first_line = 1
         self.output_file = 0
         
     def getHWVersion( self ):
         return HWDetector.detectVersion()
         
     def getDeviceIDandPCB( self ):
         return HWDetector.getCurrentDeviceID(), HWDetector.getCurrentPCBVersion()
         
     def openOutputFile( self ):
         self.id, self.pcb_ver = self.getDeviceIDandPCB()
         
         if self.id == -1 or self.pcb == -1:
             print( "Failed to get ID" )
             return -1
         storage_folder = "/var/log/pwr_monitor"
         
         if ( os.path.exists( storage_folder ) == False ):
             os.path.mkdir( storage_folder )
             
         file_name = "{0}_{1}_{2}.csv".format( self.id, self.pcb_ver, int( time.time() ) )
         self.output_file = open( "{0}/{1}".format( storage_folder, file_name ), 'w' )
         
         if ( self.first_line == 1 ):
             if ( self.logLineToFile( self.csv_header ) == -1 ):
                 return -1
             self.first_line = 0
            
         return 1
     def logLineToFile( self, line ):
        try:
           self.output_file.write( line )
        except Exception as e:
            print( e )
          
     def readLine( self ):
       values = []
       for file in self.files:
          fil = open(file, 'r')
          res = fil.read()
          values.append( res )
          if row != "":
              row = "{0},{1}".format( row, res )
          else:
              row = "{0},{1},{2}".format(time.time(), current_id, res )
          row = row.replace( '\n', '' )
          fil.close()
          print( row )
       return values, row
      

          
     def spool( self ):
         self.hw_version = self.getHWVersion()
         if self.hw_version == 0:
             print( "Failed to get hw version" )
             return -1
         self.files, self.csv_header = HWDetector.createCSVHeader( self.hw_version )
         if ( self.files == 0 or self.csv_header == 0 ):
             return -1
         if ( self.openOutputFile() == -1 ):
              return -1
         return 1
         
     def sendLine( self, line ):
         self.com_link.sendMSG( line, WorkerEnum.SENDER )
         
     def calculateValues( files, line ):
        if ( self.hw_version  == HWVersions.CM1_5 ):

        elif ( self.hw_version  == HWVersions.CM1_5_SLEEVE ):
            main_power_without_mpcie_nrf = files[ 2 ] - files[ 1 ] - files[ 0 ]
            line = "{0},{1}".format( line, main_power_without_mpcie_nrf ) 
        elif ( self.hw_version  == HWVersions.CM2_0 ):
            pwr_without_pcie_nrf = files[ 0 ] - files[ 1 ] - files[ 2 ] - files[ 3 ] - files[ 4 ]
            mPcie_total = files[ 1 ] + files[ 2 ] + files[ 3 ]
            line = "{0},{1},{2}".format( line, mPcie_total, pwr_without_pcie_nrf )
        #elif ( self.hw_version  == HWVersions.CCB3_0 ):
            
            
        return line
     def step( self ):
         #check if running for the first time if yes prepare
         if self.spooled_up == 0:
              if ( self.spool() == -1 ):
                   print( "Spool failed" )
                   return -1
              self.spooled_up = 1

         #read currents from file
         files, line = self.readLine()
         if line == -1:
             return -1
         line = self.calculateValues( files, line )
         #try to write line to file, if failed return error
         if ( self.logLineToFile( readLine ) == -1 ):
             return -1
             
         #send line to TCP and Serial line
         self.sendLine( readLine )
         
         
         
         return 1
