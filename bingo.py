#coding=utf-8
from colorama import init, Fore, Back, Style
import os
from time import sleep
from random import choice
import argparse, socket
BUFSIZE = 65535
tmp_port = 9989

def start():
    init(autoreset=True)
    os.system('clear')
    print('Welcome to '+Fore.RED+'Bingo Game!')
    print('Please input ', end='')
    print(Back.MAGENTA+Fore.BLACK+'name,your number', end='')
    print('to join this game')
    print('Your input = ', end='')
#    text = input()
#    name = text.split(',')[0]
#    num = text.split(',')[1:]
    text = input()
    name = text.split(';')[0]
    num = text.split(';')[1].split(',')
    os.system("clear")
    print('Welcome '+Fore.YELLOW+name, end='')
    print(" ! Let's wait for the game start!")
    print("This is your bingo card")
#    num = num.split(',')
    for i in range(0, len(num)):
        if (i+1)%5!=0:
            print('{:>4}'.format(num[i]), end='')
        else:
            print('{:>4}'.format(num[i]))
    return (name, num,text)

def check_bingo(bingo_card):
    board = [[0 for j in range(5)] for i in range(5)]
    for i in range(5):
        for j in range(5):
            board[i][j] = bingo_card[i*5+j]
    
    for row in board:
        if all(cell == 'X' for cell in row):
            return True
    
    for col in range(5):
        if all(board[row][col] == 'X' for row in range(5)):
            return True

    if all(board[i][i] == 'X' for i in range(5)) or all(board[i][4-i] == 'X' for i in range(5)):
        return True
    
    return False

def server(network, port, ser_addr):
    num = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]
    player = {} # record {address:[name,number]}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((ser_addr, port)) #flag
    delay = 10.0
    sock.settimeout(delay)
    try:
        i = 1
        while(1):
            data, address = sock.recvfrom(BUFSIZE)
#            text = data.decode('ascii').split(',')
#            who = text[0]
#            number = text[1:]
            text = data.decode('ascii').split(';')
            who = text[0]
            number = text[1].split(',')
            player[address] = [who,number]
            print(f'Player \033[33m{who}\033[0m join this game.')

            text = f'You are player \033[33m{i}\033[0m, Welcome! The game is expected to start in {delay} seconds'
            text = text.encode('UTF-8')
            sock.sendto(text,address)
            i += 1
    except:
        print('\033[92mGame Start!\033[0m')
    text = 'start'
    sock.sendto(text.encode('ascii'), (network, port))
    delay = 2.0 #flag

    nobody_win = 1
    while nobody_win:
        n = choice(num)
        if n=='X':
            continue
        print(f'Number : \033[36m{n}\033[0m') #flag
        num[num.index(n)] = 'X' # == ? #flag
        text = str(n)
        sock.sendto(text.encode('ascii'), (network, port))

        for x in player:
           player[x][1][player[x][1].index(str(n))] = 'X'

        sock.settimeout(delay)
        try:
            print('\033[90mReceving ...\033[0m')
            while True:
                data, address = sock.recvfrom(BUFSIZE)
                data = data.decode('ascii')
                che = 0
                if(data == 'Bingo'):
                    che = check_bingo(player[address][1])
                    if che : 
                        nobody_win = 0;
#                        text = 'You win!'
#                        sock.sendto(text.decode(),address)

                        print(f'Winner is \033[30;47m{player[address][0]}\033[0m')

                        text = f'Bingo, {player[address][0]} from {address[0]}'
                        sock.sendto(text.decode(),(network,address)) #broadcast
                        break;
                    else:
                        text = 'You don\'t win!:('
                        sock.sendto(text.decode(),address)
        except:
            if nobody_win:
                print('\033[90mNobody bingo\033[0m')
        if nobody_win == 0:
            sock.sendto(text.encode('ascii'), (network, port))
    print('\033[92mGame End!\033[0m')
    #indata, addr = sock.recvfrom(BUFSIZE)
    #print('recvfrom client({}):{} '.format(addr, indata.decode()))

def client(interface, port, ser_addr):
    In = start()
    flag = False
    name = In[0]
    nums = In[1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((interface, port))

    text = In[2].encode('UTF-8') #flag
    sock.sendto(text,(ser_addr, port))

    while True:
        indata, addr = sock.recvfrom(BUFSIZE)
        print('{}:"{}"'.format(addr,indata.decode()))
        #outdata = name
        #sock.sendto(outdata.encode(), (addr, port))
        #indata, addr = sock.recvfrom(BUFSIZE)
        #print('recvfrom server({}):{} '.format(addr, indata.decode()))
        if indata.decode()=='start':
            break
    os.system('clear')
    print("Let's start the game!")
    while flag==False:
        indata, addr = sock.recvfrom(BUFSIZE)
        if indata.decode('ascii')[:5] == 'Bingo':
            print(indata.decode('ascii'))
            return
#            break;

#        os.system('clear')
        print('recvfrom server({}):\033[36m{}\033[0m'.format(addr, indata.decode()))
        if nums[nums.index(indata.decode())] == 'X' or indata.decode() == 'start':
            continue;
        else:
            nums[nums.index(str(indata.decode()))]='X'
            for i in range(0, len(nums)):
                print_red = ''
                print_end = '' 
                if nums[i] == 'X': 
                    print_red = '\033[31m'
                    print_end = '\033[0m'
                if (i+1)%5!=0:	
                    print('{}{:>4}{}'.format(print_red,nums[i],print_end), end='')
                else:
                    print('{}{:>4}{}'.format(print_red,nums[i],print_end))
            print()
            print("=========================================")
            print()
            flag = check_bingo(nums)
    text = 'Bingo'
    print(Fore.YELLOW+"Bingo!")
    while 1:
        sock.sendto(text.encode(),(ser_addr, port))
        indata, addr = sock.recvfrom(BUFSIZE)
        if indata.decode()[:5] == 'Bingo':
            print('You Win!')
            break;

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send, receive UDP broadcast')
    parser.add_argument('role', choices=choices, help='which role to take')
    parser.add_argument('host', help='interface the server listens at;'
                        ' network the client sends to')
    parser.add_argument('-p', metavar='port', type=int, default=1060,
                        help='UDP port (default 1060)')
    parser.add_argument('-s', metavar='server_address', type=str, 
                        default='172.20.192.1', help='Server Address')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p, args.s)
