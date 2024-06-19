import time

from workers.TCPServerThread import *
from workers.ReaderThread import *
from workers.SerialThread import *
#from aux.COMLink import *

class Semaphore:
    def __init__( self ):
       self.stop_all = 0

com_link = COMLink()

#com_thread = COMThread( com_link )
semaphore = Semaphore()

tcp_server_thread = TCPServerThread( com_link, semaphore )
reader_thread = TCPClientThread( com_link, semaphore ) 

#data_thread = DATAThread( com_link )
 
com_link.set( tcp_server_thread, tcp_client_thread )
print( "Launching threads" )

reader_thread.start()
tcp_server_thread.step()
#data_thread.start()

print( "Threads Launched" )
while semaphore.stop_all == 0:
  time.sleep( 0.1 )

print("Exiting")
