import socket

HOST = '10.10.249.119' 
PORT = 7896

def run_client():
    ''' 
        AF_INET - IPv4
        AF_INET6 - IPv6
        AF_UNIX - UnixSockets

        SOCK_STREAM - TCP
        SOCK_DGRAM - UDP RAW_SOCKET - criar protocolo
    '''
    try:  
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        cliente.connect((HOST, PORT))
    
        while True:
            msg = input("Enter message: ")
            cliente.sendall(msg.encode("utf-8")[:1024])
    
            response = cliente.recv(1024).decode("utf-8")
    
            if response.lower() == "closed":
                break

            if not response:
                print("Esse server danadinho não respondeu")
                break
    
            print(f"recived: {response}")
        
        cliente.close()
        print("Closed connection")
    except socket.gaierror as e:
        print(f"Socket error:{e}")
    except ConnectionRefusedError:
        print("Connexão recusada, servidor está ligado?")
    except Exception as e:
        print("Error", e)
run_client()
