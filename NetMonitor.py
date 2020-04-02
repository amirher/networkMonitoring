##author: Simone Porcu
# pyinstaller --onefile --noupx --windowed NetMonitor.py
import os
from tkinter import *
import psutil
import datetime
import pingparsing
import threading

root = Tk()
flag = True

old_value_sent = 0
old_value_recv = 0
variable = StringVar()


def convert_to_megabit(value):
    return 8 * (value / (2 ** 20))


def send_stat(value):
    return convert_to_megabit(value)


def recv_stat(value):
    return convert_to_megabit(value)


def initialization():
    start_button.config(state='disabled')
    start_button.update()

    filename1 = datetime.datetime.now().strftime("%Y-%m-%d")
    name = str(filename1) + ".csv"
    if os.path.exists(name):
        file2write = open(name, 'a')  # append if already exists
    else:
        file2write = open(name, 'w')  # make a new file if not
        file2write.write('date,upload,download,ping,packet-loss\n')

    def run():
        global old_value_sent, old_value_recv
        while flag:
            new_value_sent = psutil.net_io_counters().bytes_sent
            new_value_recv = psutil.net_io_counters().bytes_recv
            row = ""
            transmitter = pingparsing.PingTransmitter()
            transmitter.destination = "emea2cps.adobeconnect.com"
            transmitter.count = 4
            result = transmitter.ping()
            strings = result.stdout.split("\r\n")
            if old_value_sent and old_value_recv:
                up = round(send_stat(new_value_sent - old_value_sent), 4)
                dw = round(recv_stat(new_value_recv - old_value_recv), 4)
                row = str(datetime.datetime.now()) + ", upload: " + str(up) + " Mbit" + ", download: " + str(
                    dw) + " Mbit" + ", ping: " + strings[12].split(",")[2] + " Packet Loss:" + strings[10] + "\n"
                fileRow = (str(datetime.datetime.now()) + "," + str(up) + "," + str(dw) + "," +
                           strings[12].split(",")[2].split("=  ")[1].split("ms")[0] + "," +
                           strings[10].split("(")[1].split("%")[0] + "\n")
                file2write.write(fileRow)
            if not flag:
                file2write.close()
                break

            old_value_sent = new_value_sent
            old_value_recv = new_value_recv

            variable.set(str(row))

    thread = threading.Thread(target=run)
    thread.start()


def kill():
    root.destroy()


def flagon():
    global flag
    flag = True
    initialization()


def flagoff():
    global flag
    flag = False
    kill()


canvas = Canvas(root, width=650, height=80)
canvas.pack()
your_label = Label(root, textvariable=variable)
your_label.pack()
start_button = Button(root, text="start", command=flagon)
start_button.pack()
close_button = Button(root, text="stop", command=flagoff)
close_button.pack()
root.mainloop()
