import numpy as np

class DataMaster():
    def __init__(self):
        self.tSSData = []
        self.aSSData = []
        self.msg = []
        #print("Dataa")
        pass

    def decodeMsg(self):
        temporal = self.rowMsg.decode('utf8')
        if (len(temporal)>0):
            try:
                self.msg = temporal.split(",")
                del self.msg[-1]
                self.msg = list(map(self.stringToFloat, self.msg))
                #print(self.msg)
                #print(len(self.msg)) #debugg
                #if len(self.msg)==2500:
                    #print(True)
                    #pass
                #else:
                    #print(len(self.msg))
            except Exception as e:
                print(e)
            pass
        pass

    def stringToFloat(self, n):
        if len(n)>0:
            return int(n)


if __name__=="__main__":
    DataMaster()