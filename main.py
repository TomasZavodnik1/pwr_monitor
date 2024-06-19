import time

from workers.TCPServerThread import *
from workers.ReaderThread import *
#from workers.SerialThread import *
#from aux.COMLink import *

class Semaphore:
    def __init__( self ):
       self.stop_all = 0

com_link = COMLink()

#com_thread = COMThread( com_link )
semaphore = Semaphore()
#create threads
tcp_server_thread = TCPServerThread( com_link, semaphore )
reader_thread = ReaderThread( com_link, semaphore ) 

#data_thread = DATAThread( com_link )
#set communications links 
com_link.set( tcp_server_thread, reader_thread )
print( "Launching threads" )

#launch threads
reader_thread.start()
tcp_server_thread.start()
#data_thread.start()

print( "Threads Launched" )
while semaphore.stop_all == 1:
  time.sleep( 0.1 )

print("Exiting")


