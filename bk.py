


import pyvisa
from time import sleep
#ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)



rm = pyvisa.ResourceManager()
d=list(rm.list_resources())
print(d)
x=int(input('inst number?' ))
ps=rm.open_resource(d[x])

#ps = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
print(ps.query("*IDN?"))

def i():
    return float(ps.query("meas:curr?"))


while 1:
    q=input('cmd?  ')
    if q=='sw':
        x=int(input('inst number?' ))
        ps=rm.open_resource(d[x])
        print(ps.query('*idn?'))
    if q=="":
        break
    elif '?' in q:
        print(ps.query(q))
    else:
        ps.write(q)


while 1:
    e =i()
    print(e)
    if e< 0.100:
        ps.write('output 0')

    sleep(60)
