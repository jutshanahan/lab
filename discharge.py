


import pyvisa
from time import sleep, time, strftime
from sys import exit
#ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,timeout=1)


import requests

def msg(m):
	print('sending telegram')
	token = "5524996951:AAHi1R26cyzT-c-7lm8fcLrdBX4POdqgWxw"
	url = f"https://api.telegram.org/bot{token}"
	# https://api.telegram.org/bot=5524996951:AAHi1R26cyzT-c-7lm8fcLrdBX4POdqgWxw
	params = {"chat_id": "5553458128", "text": m}
	r = requests.get(url + "/sendMessage", params=params)





rm = pyvisa.ResourceManager()
d=list(rm.list_resources())
print(d)

#ps = rm.open_resource('ASRL/dev/ttyUSB0::INSTR')

def pq(inst,q):
	r=inst.query(q).strip()
	print(q,':',r)
	return r

def qf(inst,q):
	r=inst.query(q).strip()
	return float(r)


try:
	ps=rm.open_resource('ASRL/dev/ttyUSB0::INSTR')
	pq(ps,"*IDN?")
	pq(ps,'volt?')
	pq(ps,'curr?')
	pq(ps,'meas:volt?')
	pq(ps,'meas:curr?')
except Exception as e:
	print(e)
	exit()
	

try:
	load=rm.open_resource('USB0::11975::34816::802199036737610032::0::INSTR')
	pq(load,"*IDN?")
	# load.write('remote:sense ON')
	
	rs=input('enable remote sense  [0|1]? ')
	load.write('remote:sense ' + rs)
	sleep(0.5)
	ans = pq(load,'remote:sense?')
	if ans != rs: raise Exception("unable to set remote sense",ans)
	
	
	load.write('func current')
	sleep(0.2)
	ans = pq(load,'func?')
	if ans != "CURRENT": raise Exception("unable to set current mode",ans)
	pq(load,'input?')
	pq(load,'meas:volt?')
	pq(load,'meas:curr?')
	
except Exception as e:
	print(e)
	exit()
		
def meas_dcr(inst):
	try:
		load=rm.open_resource('USB0::11975::34816::802199036737610032::0::INSTR')
		pq(load,"*IDN?")
		# load.write('remote:sense ON')
		rs='0'
		load.write('remote:sense ' + rs)
		sleep(0.5)
		ans = pq(load,'remote:sense?')
		if ans != rs: raise Exception("unable to set remote sense",ans)
		
		
		load.write('func current')
		sleep(0.2)
		ans = pq(load,'func?')
		if ans != "CURRENT": raise Exception("unable to set current mode",ans)
		pq(load,'input?')
		
		# pq(load,'curr:range?')
		# pq(load,'curr:slew?')
		i=1
		load.write('curr ' + str(i))
		pq(load,'curr?')
		pq(load,'input?')
		print('off...')
		v1=float(pq(load,'meas:volt?'))
		pq(load,'meas:volt?')
		pq(load,'meas:curr?')
		load.write('input ON')
		print('on...')
		sleep(1)
		v2=float(pq(load,'meas:volt?'))
		pq(load,'meas:curr?')
		print('internal resistance',round((v1-v2)/i*1000,1),'mΩ')
		load.write('input OFF')
		print('off...')
		sleep(1)
		pq(load,'meas:volt?')
		pq(load,'meas:curr?')
		pq(load,'input?')


	except Exception as e:
		print(e)
		exit()
		

def i():
    return float(ps.query("meas:curr?"))
	
project=input('project name?  ')
	
ch=input('power supply output channel [1|2|3]?  ')
if ch=="":
	print("charging disabled")
else:
	ps.write('inst:nsel ' + ch)
	pq(ps,'inst:nselect?')
	sleep(0.5)
	pq(load,"meas:volt?")
	pq(load,"meas:curr?")
	
cv=input('charge voltage?  ')
if cv=="":
	print("charging disabled")
else:
	ps.write('volt ' + cv)
	sleep(0.5)
	pq(ps,'volt?')
	
	
cv=input('charge current?  ')
ps.write('current ' + cv)
sleep(0.5)
pq(ps,'current?')
	

if cv!="":
	coc=input('cutoff current [0.1A]?  ')
	if coc=="": coc = 0.1

	
dv=float(input('discharge cutoff voltage?  '))

di=float(input('discharge current?  '))

r=(input('wire resistance?  '))
if r=="":
	r=0
	# print("")
else:
	r=float(r)

logdt=(input('log data every [1] ?  '))
if logdt=="": logdt = 1
else: logdt = float(logdt)



ps.write('outp on')
t=time()
t0=time()
sleep(logdt)
wh=0
ah=0
while 1:
	try:
		fv=qf(ps,"meas:volt?")
		i=qf(ps,"meas:curr?")
		
		r=0
		
		v = i*r + fv
		now=time()
		dt=now-t
		t=now
		
		p=v*i
		ah+=i*dt/3600
		wh+=p*dt/3600
		te=round(now-t0,0)
		
		ts=strftime("%b %d %Y  %l:%M:%S")
		s = "%s	%.3fV(meas)	%.3fV (calcd)	%.1fA	%.1fW	%.3fs	%.3fAh	%.3fWh	" % (ts,fv,v,i,p,te,ah,wh)
		print(s)
		sleep(logdt)
		if i< float(coc):
			ps.write('output off')
			sleep(0.5)
			pq(load,"output?")
			v=float(pq(load,"meas:volt?"))
			i=float(pq(load,"meas:curr?"))
			msg(project + ' .charge finished. ' + s)
			break
	except Exception as e:
		print(e)
	
	except KeyboardInterrupt as e:
		print(e)
		sleep(0.5)
		load.write('input off')
		sleep(0.5)
		pq(load,'input?')
		v=float(pq(load,"meas:volt?"))
		i=float(pq(load,"meas:curr?"))
		msg('done by keyboard')
		exit()


v=float(pq(load,"meas:volt?"))
i=float(pq(load,"meas:curr?"))
load.write('curr ' + str(di))
load.write('input on')
t=time()
t0=time()
sleep(logdt)
wh=0
ah=0

while 1:
	try:
		fv=qf(load,"meas:volt?")
		i=qf(load,"meas:curr?")
		
		v = i*r + fv
		now=time()
		dt=now-t
		t=now
		
		p=v*i
		ah+=i*dt/3600
		wh+=p*dt/3600
		te=round(now-t0,0)
		
		ts=strftime("%b %d %Y  %l:%M:%S")
		s = "%s	%.3fV(meas)	%.3fV (calcd)	%.1fA	%.1fW	%.3fs	%.3fAh	%.3fWh	" % (ts,fv,v,i,p,te,ah,wh)
		print(s)
		sleep(logdt)
		if v< dv:
			load.write('input off')
			sleep(0.5)
			pq(load,"input?")
			v=float(pq(load,"meas:volt?"))
			i=float(pq(load,"meas:curr?"))
			print('done')
			msg('discharge finished. ' + s)
			break
	# except Exception as e:
		# print(e)
	
	except KeyboardInterrupt as e:
		print(e)
		sleep(0.5)
		load.write('input off')
		sleep(0.5)
		pq(load,'input?')
		v=float(pq(load,"meas:volt?"))
		i=float(pq(load,"meas:curr?"))
		msg('done by keyboard')
		break
		
exit()

e =i()
print(e)
if e< 0.100:
	ps.write('output 0')

sleep(60)

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
