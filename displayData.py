# import numpy

from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 

import serial
import time
import os
import re
import sys

#Btech 135 at 9:45

check = os.path.exists('data.txt')
if not check:
    f = open('data.txt','w')
    f.close()
dataGlobal = [0] * 1002

with open('data.txt','r') as f: #loading previously saved data
        array = []
        for line in f:
            array.append(line.split(','))


#button command function
def measure():

    data = importFromUART()

    speedNum = data[len(data) - 1]
    sampleNum = data[len(data) - 2]
    displaySpeed(speedNum)

    global dataGlobal 
    dataGlobal = data.copy()
    graphData = data.copy()
    graphData.pop(len(data)-1)
    plot(graphData)




#get data from UART
def importFromUART():
    #print("importing CSV data")
    #dummy data to test graphing
    startTime = time.perf_counter()

    ser = serial.Serial('COM4', 115200, timeout=None)
    #x = ser.read()          # read one byte
    #s = ser.read(10)        # read up to ten bytes (timeout)
    global dataGlobal
    global woodLength
    lenstr = woodLength.get()
    if(re.match(r'[0-9]+\.?[0-9]*',lenstr) == None or len(lenstr) == 0):
        error = Toplevel(root)
        errormsg = Label(error, text="invalid length input")
        acceptButton = ttk.Button(error, text="Ok", command=error.destroy)
        errormsg.pack()
        acceptButton.pack()
        return dataGlobal


    ser.write(bytes("S[123.456789123]",'utf-8'))
    ser.reset_input_buffer()

    serialString = ""
    count = 0
    bufferLength = 1002
    dataBuffer = [0] * bufferLength
    foundData = False

    while 1:
        currentTime = time.perf_counter()

        if((currentTime - startTime) > 5.0):
            break

        try:
            serialString = ser.readline()   # read a '\n' terminated line
        except:
            if(foundData == True):
                break

        try:
            newString = serialString.decode('utf-8')
            #print(newString)
            try:
                intVal = int(newString)
            except ValueError:
                print("could not get integerVal\n")
                print(newString)
                intVal = newString

            #print(serialString.decode("Ascii"))
            if (foundData == False):
                if (newString != ""):
                    foundData = True
                    time.sleep(1)
                    dataBuffer[count] = intVal
                    count += 1
            else:
                dataBuffer[count] = intVal
                count += 1
                if (ser.in_waiting == 0):
                    print("end of data")
                    break
                if(count >= bufferLength):
                    break

        except:
            print("no data\n")
            if (foundData == True):
                if (count >= bufferLength):
                    break
                else:
                    dataBuffer[count] = 0
                    count += 1
            pass

    ser.reset_input_buffer()
    ser.close()

    # testData = [1000] * 1002
    # testData[1000] = 176
    # testData[1001] = 3296
    #print(dataBuffer)
    return dataBuffer

#display speed to button
def displaySpeed(speedNum):
    speed.set(speedNum)

#plot data
def plot(plotData): 
    #plot data
    plot1.clear()
    plot1.plot(plotData) 
  
    #update canvas in UI
    canvas.draw()

def saveMeasure():
    #print(dataGlobal)
    print(str(len(dataGlobal)))
    if(len(dataGlobal) > 100):
        print("saving data")
        with open('data.txt','a') as f:
            global woodName
            stri = woodName.get()
            for i in dataGlobal:
                stri = stri + ',' + str(i)
            line = stri + '\n'
            f.write(line)
            arrLine = line.split(',')
            array.append(arrLine)
            lsBox.insert(len(arr),arrLine[0])

def loadData():
    #print("dummy")
    tuple = lsBox.curselection()
    index = tuple[0]
    work = array[index]
    work.pop(0)
    work[len(work)-1] = work[len(work)-1].strip()
    workNum = []
    for string in work:
        try:
            workNum.append(int(string))
        except ValueError:
            workNum.append(string)
    #print(workNum)
    global dataGlobal
    dataGlobal = workNum.copy()

    speedNum = workNum[len(workNum) - 1]
    sampleNum = workNum[len(workNum) - 2]
    displaySpeed(speedNum)

    dataGlobal = workNum.copy()
    graphData = workNum.copy()
    graphData.pop(len(workNum)-1)
    plot(graphData)

    
    
    
    
    
    # with open('data.txt','r') as f:
    #     array = []
    #     for line in f:
    #         array.append(line.split(','))
    #     print(array)
    #     # win = Toplevel(root)
    #     # win.transient(root)
    #     # win.title("Load Data")
    #     # root.geometry("500x700")
    #     lsBox = Listbox()
    #     count = 0
    #     for arr in array:
    #         lsBox.insert(count, str(arr[0]))
    #         count+=1
    #     lsBox.pack()
    #     loadData
        



              

#define root
root = Tk()
root.title("test app")
root.geometry("500x900") 

#create figure for plot
fig = Figure(figsize = (5, 5), 
                 dpi = 100) 
plot1 = fig.add_subplot(111) 

#Set up graph canvas
canvas = FigureCanvasTkAgg(fig, master = root)
canvas.draw() 
canvas.get_tk_widget().pack() 

woodLabel = ttk.Label(text="Wood Name")
woodName = ttk.Entry(width=50)
woodName.insert(0,"Wood")
lengthLabel = ttk.Label(text="Wood Length (cm)")
woodLength = ttk.Entry(width=50)

woodLabel.pack()
woodName.pack()
lengthLabel.pack()
woodLength.pack()


#button to take measurement
plot_Button = ttk.Button(root, text="Prime for Measurement", command=measure)
plot_Button.pack()

#speed output label
speed = StringVar()
speed.set(0)
speedLabel = ttk.Label(root, textvariable=speed)
speedLabel.pack()

save_Button = ttk.Button(root, text="Save data", command=saveMeasure)
save_Button.pack()

#list data
lsBox = Listbox(selectmode=SINGLE)
count = 0
for arr in array:
    lsBox.insert(count, str(arr[0]))
    count+=1
lsBox.pack()


load_Button = ttk.Button(root, text="Load data", command=loadData)
load_Button.pack()

#begin application loop
root.mainloop()



