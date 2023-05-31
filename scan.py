import socket
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from functools import partial
import ipaddress
import statistics

def get_ip_from_subnet(ip_subnet):

    ips= ipaddress.ip_network(ip_subnet)
    ip_list=[str(ip) for ip in ips]
    return ip_list


def wg_ping(ip,port,timeout=1):
	# print('Checking %s:%s' %(ip,port)) 
  
	# print("Sending request...")
	
	payload= "\x01\x00\x00\x00\xcb\x9c\xf0\xe7\x3b\x5c\xaa\xb2\x5b\x14\x62\x35" \
	"\x57\x90\x3c\xa1\x55\xa3\xb1\x55\x44\x66\x3f\x17\xc7\xf3\x93\x9e" \
	"\x6e\xfa\x95\x8d\xc9\xf2\x84\x57\x23\x88\xb6\x93\x1c\x0b\x74\xbb" \
	"\x11\x98\x37\x61\x2b\x54\xeb\xb9\x4e\x24\x5b\x90\xf7\xd0\x4c\xe8" \
	"\xcb\x50\xec\xda\x61\xa7\x3b\xc2\x77\xe6\x58\x76\x12\xaf\x2c\x0e" \
	"\x29\x0b\x01\x31\x6f\x75\x1f\x67\x3f\x33\x2b\x0b\xa5\x6e\x53\xf3" \
	"\x34\x82\x59\xec\xf7\x3c\xcb\x6e\x03\x1b\x6d\xa3\x12\x90\x34\xa3" \
	"\x4f\x89\x1f\x20\x1c\x3e\x7f\xe3\xd7\x21\x9f\xdc\x2f\x4d\xb0\xff" \
	"\x53\x13\xb3\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
	"\x00\x00\x00\x00"
	
	ping=0
	start_time = time.time_ns()
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(timeout) # in seconds
	sock.connect((ip, int(port)))
	sock.send(bytes(payload, 'latin1'))
	try:
		dta=sock.recv(100)
		ping=int((time.time_ns()-start_time)/1000000)
		# print("Server reply: %s" %(dta))
	except:
		# print("Server not responding")
		pass
		
	sock.close()
	# print("###########################################################")
	return ping


def do_ping(ip_port):
	(ip,port)=ip_port
	pings=[]
	ping=0 
	for i in range(1,3):
		px=wg_ping(ip,port,timeout=1)
		if px==0 :
			# px=9999
			return (ip,port,0)
		pings.append(px)
	
	ping=statistics.mean(pings)
	return (ip,port,ping)
	


# cidrs="188.114.99.0/24"
cidrs="162.159.192.0/24 162.159.193.0/24 162.159.195.0/24 188.114.96.0/24 188.114.97.0/24 188.114.98.0/24 188.114.99.0/24"

# ports="500 854 859 864 878 880 890 891 894 903 908 928 934 939 942 943 945 946 955 968 987 988 1002 1010 1014 1018 1070 1074 1180 1387 1701 1843 2371 2408 2506 3138 3476 3581 3854 4177 4198 4233 4500 5279 5956 7103 7152 7156 7281 7559 8319 8742 8854 8886"
ports="2408 1701 4500 988"
# ports="2408"


print("Building ip list...")
ip_port_list=[]


for cidr in cidrs.split(" "):
	for ip in get_ip_from_subnet(cidr):
		ip_port_list.extend([(ip,port) for port in ports.split(" ")]);
	
print(f"{len(ip_port_list)} target has been generated.")
progress=0
print("Scaning...")
sorted_result=[]
with ThreadPoolExecutor(64) as executor:
	results_gen = executor.map(do_ping, ip_port_list)
	for p in results_gen :
			(ip,port,ping)=p
			
			progress+=1
			if(ping>0):
				print(f'{ip}:{port}\t-> {ping}ms \t ({progress/len(ip_port_list)*100:#05.2f}%)')
				sorted_result.append(p)

	sorted_result.sort(key=lambda tup: tup[2], reverse=False)
	print("\n--------------------------\n")
	print("Sorted results:\n")
	for p in sorted_result:
		(ip,port,ping)=p
		print(f'{ip}:{port}\t-> {ping}ms')
