from twisted.internet import protocol, reactor, endpoints, task
from twisted.protocols.policies import TimeoutMixin
from datetime import datetime
from datetime import datetime
from workers.Worker import *
from aux.COMLink import *

import threading
import time
import queue
import base64
import json
import struct
import traceback


STATUS_REPORT = 1
CRADLE_RESULT_REPORT = 2


class Client(protocol.Protocol, TimeoutMixin):
    def __init__(self, task_man, data_man, fac, data_packet):
        protocol.Protocol.__init__( self )
        TimeoutMixin.__init__( self )
        self.buffer = ""
        self.mTaskHandler = task_man
        #print( 'Creating' )
        self.names = "Client"
        self.found_par = 0
        self.factory = fac
        self.com_link = task_man
        self.data_man = data_man
        self.active_tasks = []
        self.command_packet = data_packet
        self.dispatch = { 0: self.processBasic,
                          2: self.processLogChunk,
                          4: self.processFwChunk,
                          8: self.processFwAuxChunk,
                          10: self.ProcessCreateNewId,
                          12: self.processCommandDone,
                          30: self.processNewCoinData,
                          31: self.processBTSReport,
                          32: self.processBTSMemoryState,
                          34: self.processErrorData,
                          6: self.processDataChunk}
        
        self.t = ""
        self.found_arr = 0
        self.sent = 0
        self.task_man.registerNewClient( self )
        #self.tcp_man.registerNewSocket( self )

    
    def decodeError(self, desc):
        self.desc = desc
    
    def ProcessCreateNewId(self, data):
        type_fw = data[ "unique_data" ]
        self.createActiveTask( "ProcessCreateNewId", data )
    
    def processErrorData( self, data ):
        self.createActiveTask( "ProcessBTSError", data )
    
    def processCommandDone(self, data):
        command_id = data[ "command_id" ]
        timestamp = data[ "timestamp" ]
        print( "Command done" ) 
        self.createActiveTask( "ProcessCommandDone", data )
    
    def processBTSMemoryState(self, data):
        self.createActiveTask( "ProcessBTSMemoryState", data )
        
    def processFwAuxChunk(self, data):
        type_fw = data[ "type_fw" ]
        self.createActiveTask( "ProcessFwAuxPacket", data )
        
    def processErrorLog(self, data):
        ##print( "Error log" )
        type = data["e_type"]
        desc = data["desc"]
        
        self.decodeError( desc )
    
    def processLogChunk(self, data):
        dev_c = data[ "dev_c" ]
        data = data[ "data" ]
    
    def createActiveTask(self, func_name, data):
        task = self.task_man.createTask( func_name, data )
        task.callback = self.write
        self.task_man.pushTasks( task )
        
        self.active_tasks.append( task )
        
    def createActiveTaskWithoutReturn(self, func_name, data):
        task = self.task_man.createTask( func_name, data )
        task.callback = self.conditionalWrite
        self.task_man.pushTasks( task )
        self.active_tasks.append( task )    
        
    def processBasic(self, data):
        #print( data )
        fw_v = data["fw_v"]
        b_fw_v = data["b_fw_v"]
        
        self.createActiveTask( "CheckVersionTask", data )
        
    def processFwChunk(self, data):
        self.createActiveTask( "ProcessNewFWTask", data )
    
    def processNewCoinData(self, data):
        ##print( data )
        ##print( "Data chunk" )
        self.createActiveTaskWithoutReturn( "ProcessNewCoinData", data )
        
    def processBTSReport(self, data):
        self.createActiveTask( "ProcessBTSReport", data )
                
    def processDataChunk(self, data):
        ##print( data )
        ##print( "Data chunk" )

       

        #self.createActiveTask( "ProcessDataPacket", data )
        return
        
    def connectionMade(self):
        self.factory.clientConnectionMade(self)
        self.setTimeout(15)

    def logError(self):
        var = traceback.format_exc()
        self.log( "Error: {0}".format( var ), 3 )

    def log(self, txt, priority=3):

        msg = {}
        msg[ "txt" ] = txt
        msg[ "module" ] = self.names

        self.logger.sendMsg( msg )

    def timeoutConnection(self):
        self.data_man.removeClient( self )
        self.transport.abortConnection()
    
    def conditionalWrite( self, dat ):
        if dat == 0:
            return
        self.transport.write( dat.encode() )
        
    
    def write(self, dat):
        #print( "-->{0}".format( dat ) )
        self.transport.write( dat.encode() )
       
        #print( "I lived for {0} s".format( time.time() - self.start_t ) )
    
    def performFunction(self, res):
        i_type = int( res["type"] )
        id = int( res["id"] )
        tracker_id = -1
        if "tracker_id" in res:
            tracker_id = int(res["tracker_id"])
        #if id == 5:
        #    return
        if i_type not in self.dispatch:
            #print( "{0} not in dispatch {1}".format( i_type, self.buffer ) )
            return 0
        #print( tracker_id )
        #print( "asdasdgrtergdfhrth51" )
       
        try:
            self.dispatch[ i_type ]( res )
        except Exception as e:
            traceback.print_exc()
            print( e )
    
    
    def parseData(self, datas, type):
           
        try:
            res = json.loads( datas )
           
            if type == 0:
                if "type" not in res:
                    return 0 
                self.performFunction( res)     

            if type == 1:
                
                for i in res:
                     if "type" in i:
                         self.performFunction( i )
                         
                if "id" in datas:
                    tracker_id = int(res[0]["id"])
                    for i in self.command_packet:
                        if tracker_id not in self.command_packet[i]["sentBTS"] and self.command_packet[i]["commandType"] != 999:
                            if self.command_packet[ i ]["status"] < 2:
                                resp_arr = {}
                                resp_arr["command_data"] = self.command_packet[ i ]["data"]
                                resp_arr["command_coin_id"] =  self.command_packet[ i ]["coinId"]
                                resp_arr["command_id"] =  self.command_packet[ i ]["id"]
                                resp_arr["command"] =  1
                                resp_arr["command_type"] =  self.command_packet[ i ]["commandType"]
                                print( json.dumps( resp_arr ) )
                                
                                params = {}
                                params["model_id"] = "CommandStorage"
                                params["function"] = "addBTS"
                                params["data"] = { "bts": tracker_id, "command_id": self.command_packet[ i ]["id"] }
                                
                                self.t_procedure_mag3 = createProcedure( "runCustomFunction", params )
                                self.data_man.pushProcedure( self.t_procedure_mag3 )
                                self.write( json.dumps( resp_arr ) )
                                self.sent = 1
                                break
                            
                if self.sent == 0: 
                    self.write( "{ 'id': 1 }" )
                    
        except Exception as e:
            print( e )
            print( datas )
            return 0
        
        return 1
        
    def dataReceived(self, data):
        #if self.found_par == 1:
        self.buffer = "{0}{1}".format( self.buffer, data.decode(encoding='utf-8', errors="ignore") )

        try:
            dat = self.buffer
            for i in dat:
                if i == '[':
                    self.found_arr  = 1

                if i == '{' and self.found_arr == 0:
                    self.found_par = 1

                if self.found_par == 1 or self.found_arr == 1:
                    self.t = "{0}{1}".format( self.t, i )
                    
                if ( self.found_par == 1 and i == '}' ) or ( self.found_arr == 1 and i == ']' ):
                    self.com_link.sendMSG( self.buffer, WorkerEnum.SENDER )
                    self.buffer = ""
                    self.found_par = 0
                    self.found_arr = 0
                    break
               
            #print(  data.decode('utf-8')  )
            return
        except Exception as e:
            ip, port = self.transport.client
            print( ip )
            print( "JSON decode error" )
            print( e )
            return


    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)
        self.data_man.removeClient( self )
        #self.log( "Disc" )
        
    def step(self):
        remove_list = []
        
        for task in self.active_tasks:
            if task.done == 1:
                ##pr int( json.dumps( task.result ) )
                try:
                    if task.callback != 0:
                        task.callback( json.dumps( task.result ) )
                    remove_list.append( task )
                    
                except Exception as e:
                    #print( e )
                    #print( data )
                    #print( traceback.#print_exc() )
                    return
        
        for i in remove_list:
            try:
                self.active_tasks.remove( i )
            except:
                #print( "Client removeing active task from system that doesnt exist" )
                return
class EchoFactory(protocol.Factory):
    def __init__(self, task_manager, data_man, parent):
        protocol.Factory.__init__( self )
        self.task_manager = task_manager
        self.clients = []
        self.parent = parent
        self.lc = task.LoopingCall(self.steps)
        self.lc.start(0.002)
        self.command_packet = 0
        self.data_man = data_man
        
    def stringToBytes(self, arr):
        r = int( arr[0] )
        g = int( arr[1] )
        b = int( arr[2] )
        
        
        h = bytearray()
        h.append( 0xAA )
        h.append( ( r ) & 0xFF )
        h.append( ( g ) & 0xFF )
        h.append( ( b ) & 0xFF )
        
        xor = 0
        
        for i in h:
            xor = xor ^ i
            
        h.append( xor & 0xFF )
        #print( arr )
        return h
    
    def pushDataPacket(self, data):
        self.command_packet = data
    
    
    def steps(self):
        try:
              for client in self.clients:
                  client.step()
                  
        except Exception as e:
            #print( e )
            return
        return 1
        
    
    def pushUpdate(self, json_data):
        #print( "asdadsda" )
        for i in self.clients:
            ff = self.stringToBytes( json_data.decode().split(',') )
            i.pushUpdate( ff )
            
    def clientConnectionMade(self, client):
        self.clients.append(client)

    def clientConnectionLost(self, client):
        self.clients.remove(client)

    def buildProtocol(self, addr):
        return Client( self.task_manager, self.parent, self, self.command_packet )

class TCPServerThread(Worker):
     def __init__( self, com_link, semaphore ):
         Worker.__init__( self, "TCPServerThread", semaphore )
         self.com_link = com_link
         self.owner = semaphore
         self.clients = []
         
     def registerNewClient( self, client ):
        self.clients.append( client )
     
     def removeClient( self, client ):
        if client in self.clients:
            self.clients.remove( client )
        
     
     def step( self ):
         self.instance =  EchoFactory( self.com_link, 0, self )
         endpoints.serverFromString(reactor, "tcp:{0}".format( 9994 )).listen( self.instance )
         reactor.run()
