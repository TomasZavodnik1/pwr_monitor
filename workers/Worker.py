import threading
import time
import queue

class MSG:
   def __init__( self, msg ):
      self.created = time.time()
      self.msg = msg
      self.done = 0
      self.response = 0
      
   def isDone( self ):
      return self.done

   def hasBeenDone( self ):
      self.done = 1
   
   def pushResponse( self, reponse ):
      self.response = response

class Worker(threading.Thread):

   def __init__( self, name, owner ):
      threading.Thread.__init__( self )
      self.name = name
      self.queue = queue.Queue()
      self.go = 1
      self.owner = owner
   def pushMSG( self, msg ):
      if self.queue.qsize() > 20:
          return 0
      self.queue.put( msg )
      return 1

   def isEmpty( self ):
      if self.queue.empty() == False:
          return 0
      else:
          return 1
   def getNextMsg( self ):
      return self.queue.get()
   def run( self ):
     while ( self.go == 1 and self.owner.stop_all == 0 ):
         if ( self.step() == -1 ):
             self.go = False
             self.owner.stop_all = 1
             return -1
         time.sleep( 0.001 )
 
