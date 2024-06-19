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


STATUS_REPORT = 1
CRADLE_RESULT_REPORT = 2

class ReaderThread(Worker):
     def __init__( self, com_link ):
         Worker.__init__( self, "ReaderThread" )
         self.com_link = com_link
         self.spooled_up = 0
     def getHWVersion( self ):
         return HWDetector.detectVersion()
     def readLine( self ):
     
     def spool( self ):
         self.hw_version = self.getHWVersion()
         if self.hw_version == 0:
             sys.exit( -1 )
         
         
     def step( self ):
         if self.spooled_up == 0:
              self.spool()
              self.spooled_up = 1
         
