from serial import Serial
from serial.tools import list_ports
import time
import threading


class serialCtrl():
    def __init__(self):
        self.test_com = "?"
        self.sync_ok = "ok"
        self.threadingRTD = True

        for port in list_ports.comports():
            #print(port)
            if "Arduino " in port[1]:
                self.port = port[0]
                break
            pass
        pass
   
        self.SerialOpen()

    def SerialOpen(self):
        try:
            self.ser.is_open
            pass
        except Exception as e:
            #print(e) debugging
            PORT = self.port
            BAUD = 115200
            self.ser = Serial()
            self.ser.baudrate = BAUD
            self.ser.port = PORT
            self.ser.timeout = None
            pass

        try:
            if self.ser.is_open:
                self.ser.status = True
                pass
            else:
                PORT = self.port
                BAUD = 115200
                self.ser = Serial()
                self.ser.baudrate = BAUD
                self.ser.port = PORT
                self.ser.timeout = None
                self.ser.open()
                self.ser.status = True
                pass
            pass
        except Exception as e:
            #print(e)
            self.ser.status = False
            pass
        pass

    def SerialClose(self):
        try:
            self.ser.is_open
            self.ser.close()
            self.ser.status = False
            pass
        except Exception as e:
            #rint(e)
            self.ser.status = False
            pass
        pass

    def stream(self, queue, data):
        while self.threadingRTD:
            try:
                #t0 = time.perf_counter() #debug
                data.rowMsg = self.ser.readline()
                data.decodeMsg()
                self.ser.reset_input_buffer()
                queue.put(data.msg)
                #print(time.perf_counter()-t0) #debug
            except Exception as e:
                print(e)
                pass

if __name__=="__main__":
    serialCtrl()