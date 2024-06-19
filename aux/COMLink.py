class WorkerEnum:
   SENDER = 0
   READER = 1

class COMLink:

    def __init__( self ):
      self.go = 0

    def set( self, server_link, reader_link ):
      self.server_link = server_link
      self.reader_link = reader_link

    def getWorkerByIndex( self, index ):
       if index == WorkerEnum.READER:
          return self.reader_link
       elif index == WorkerEnum.SENDER:
          return self.server_link
       return -1

    def sendMSG( self, msg, worker_index ):
       
       if worker_index > 1:
          print( "Requesting nonexistant worker: {0}" ).format( worker_index )
          return 0
       
       res_worker = self.getWorkerByIndex( worker_index )
       
       if res_worker == -1:
          print( "Something HORRIBLE has happened" )
          return 0

       res_worker.pushMSG( msg )
       return 1
 
