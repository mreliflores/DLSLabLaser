from src.root import root
from src.serialC import serialCtrl
from src.dataMaster import DataMaster
from src.contin import CONTIN


data = DataMaster()
serial = serialCtrl()
app = root(serial, data)
app.mainloop()