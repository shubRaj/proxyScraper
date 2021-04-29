import socket
def port_checker(ip:str,port:int) -> bool:
    soc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    soc.settimeout(1)
    try:
        conn = soc.connect((ip,port))
        soc.settimeout(None)
        return True
    except:
        return False
if __name__ == "__main__":
    print(port_checker("103.232.155.233",80))