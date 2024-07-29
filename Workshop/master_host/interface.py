import numpy as np
import zmq
import pmt
import time
from threading import Lock, Thread

pub_lock = Lock()

ctx = zmq.Context()
pub = ctx.socket(zmq.REP)
pub.bind("tcp://*:8000")
#pub.connect("tcp://127.0.0.1:8000")
cmd = ctx.socket(zmq.PUB)
cmd.bind("tcp://*:8001")
morse_symb = {
    'a':['.','-'],
    'b':['-','.','.','.'],
    'c':['-','.','-','.'],
    'd':['-','.','.'],
    'e':['.'],
    'f':['.','.','-','.'],
    'g':['-','-','.'],
    'h':['.','.','.','.'],
    'i':['.','.'],
    'j':['.','-','-','-'],
    'k':['-','.','-'],
    'l':['.','-','.','.'],
    'm':['-','-'],
    'n':['-','.'],
    'o':['-','-','-'],
    'p':['.','-','-','.'],
    'q':['-','-','.','-'],
    'r':['.','-','.'],
    's':['.','.','.'],
    't':['-'],
    'u':['.','.','-'],
    'v':['.','.','.','-'],
    'w':['.','-','-'],
    'x':['-','.','.','-'],
    'y':['-','.','-','-'],
    'z':['-','-','.','.'],
    '1':['.','-','-','-','-'],
    '2':['.','.','-','-','-'],
    '3':['.','.','.','-','-'],
    '4':['.','.','.','.','-'],
    '5':['.','.','.','.','.'],
    '6':['-','.','.','.','.'],
    '7':['-','-','.','.','.'],
    '8':['-','-','-','.','.'],
    '9':['-','-','-','-','.'],
    '0':['-','-','-','-','-'],
}

dih = 1
dah = 3
intra_character_space = 1
inter_character_space = 3
word_space = 7

symtime = 0.24

def set_symbol_time(symboltime):
    global symtime
    symtime = symboltime
    val = float(symboltime) #Make sure it is typed correct
    val = pmt.to_pmt(val)
    message_pair = pmt.cons(pmt.to_pmt("unit_time"), val)
    cmd.send(pmt.serialize_str(message_pair))
    return

def set_wpm(wpm): 
    set_symbol_time(60/(50*wpm))
    return

def symbol_to_array(symbol: str):
    output = []
    symb = morse_symb[symbol.lower()]
    for i, char in enumerate(symb):
        if char == '.':
            output = np.append(output, np.ones(dih, dtype=np.uint8))
        elif char == '-':
            output = np.append(output, np.ones(dah,dtype=np.uint8))
        if i != len(symb) - 1:
            output = np.append(output, np.zeros(intra_character_space, dtype=np.uint8))
    return output 


def message_morse(msg: str):
    words = msg.strip().split() # Remove whitespace and split to Words
    morse_str = []
    for word in words:
        for i_symbol, symbol in enumerate(word):
            try:
                morse_str = np.append(morse_str, symbol_to_array(symbol))
                if i_symbol != len(word)-1:
                    morse_str = np.append(morse_str,np.zeros(inter_character_space, dtype=np.uint8))
            except:
                pass
        morse_str = np.append(morse_str,np.zeros(word_space,dtype=np.uint8))
    morse_str = np.array(morse_str, dtype=np.uint8)
    pub_lock.acquire()
    for i in morse_str:
        pub.recv()
        pub.send(i)
    pub_lock.release()
    return

def idle():
    while True:
        pub_lock.acquire(blocking=True)
        pub.recv()
        pub.send(np.uint8(0))
        pub_lock.release()
        time.sleep(symtime*0.95)

if __name__ == "__main__":
    def print_help():
        print("""
        Help:
              Unittime: #1 time_sec
              WPM:      #2 wpm
              Loop:     #3 msg
              Message:  #4
        """)
        return
    idle_tsk = Thread(target=idle)
    idle_tsk.start()
    def interface():
        print_help()
        while True:
            print("Ready for cmd:")
            stdin = input()
            if stdin.startswith("#"):
                try:
                    cmd, arg = stdin[1:].split()
                except:
                    cmd = stdin[1:].split()[0]
                if cmd == "help":
                    print_help()
                    #print(f"unittime: #1 time_sec \nWPM: #2 wpm\nLoop: #3 msg")
                elif cmd =="1":
                    try:
                        set_symbol_time(float(arg))
                    except:
                        print("Something went wrong")
                elif cmd =="2":
                    try:
                        set_wpm(float(arg))
                    except:
                        print("Something went wrong")
                elif cmd=="3":
                    msg = stdin[3:]
                    while True:
                        try:
                            message_morse(msg)
                            time.sleep(len(msg)*6*symtime)
                        except KeyboardInterrupt:
                            break
                elif cmd=="4":
                    msg = "OZ3JJ Welcomes the best participants to Aalborg"
                    while True:
                        try:
                            message_morse(msg)
                            time.sleep(len(msg)*6*symtime)
                        except KeyboardInterrupt:
                            break
            else:
                message_morse(stdin)
                   
    interface()


    # msg = "hej med"
    # message_morse(msg)






