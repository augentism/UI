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
import serial.tools.list_ports


serialPorts = [comport.device for comport in serial.tools.list_ports.comports()]
serialInfo = [comport.description for comport in serial.tools.list_ports.comports()]
#serialPorts = [0,1,2,3,4,5]

check = os.path.exists('data.csv')
if not check:
    f = open('data.csv','w')
    f.close()
dataGlobal = [0] * 1002
array = []
with open('data.csv','r') as f: #loading previously saved data
        array = []
        for line in f:
            array.append(line.split(','))


def scanSerial():
    global serialPorts
    global serialBox
    global serialInfo
    serialPorts = [comport.device for comport in serial.tools.list_ports.comports()]
    serialInfo = [comport.description for comport in serial.tools.list_ports.comports()]
    #print(serialPorts)
    serialBox.delete(0,serialBox.size())
    count=0
    for obj in serialPorts:
        serialBox.insert(count, obj + " : " + serialInfo[count])
        count+=1

#button command function
def measure():

    data = importFromUART()
    
    #print sample and speed to console
    print("Sample detected and speed:")
    sampleNum = data[0]
    speedNum = data[1]
    print("Sample: " + str(sampleNum))
    print("Speed: " + str(speedNum))
    displayData(sampleNum, speedNum)

    global dataGlobal 
    dataGlobal = data.copy()
    graphData = data.copy()
    graphData.pop(0)
    graphData.pop(0)
    #print("First point on graph: " + str(graphData[0]))
    plot(graphData, sampleNum)




#get data from UART
def importFromUART():
    global dataGlobal
    global woodLength
    #print("importing CSV data")
    #dummy data to test graphing
    startTime = time.perf_counter()
    global serialBox
    #print(serialBox.curselection())
    if(len(serialBox.curselection())):
        error = Toplevel(root)
        errormsg = Label(error, text="Please Select a Serial Input")
        acceptButton = ttk.Button(error, text="Ok", command=error.destroy)
        errormsg.pack()
        acceptButton.pack()
        return dataGlobal
    serialName = serialPorts[serialBox.curselection()[0]]
    print(serialName[1])
    if(len(serialName) == 0):
        error = Toplevel(root)
        errormsg = Label(error, text="Please Select a Serial Input")
        acceptButton = ttk.Button(error, text="Ok", command=error.destroy)
        errormsg.pack()
        acceptButton.pack()
        return dataGlobal

    ser = serial.Serial(serialName, 115200, timeout=None)
    #x = ser.read()          # read one byte
    #s = ser.read(10)        # read up to ten bytes (timeout)
    
    lenstr = woodLength.get()
    if(re.match(r'[0-9]+\.?[0-9]*',lenstr) == None or len(lenstr) == 0):
        error = Toplevel(root)
        errormsg = Label(error, text="invalid length input")
        acceptButton = ttk.Button(error, text="Ok", command=error.destroy)
        errormsg.pack()
        acceptButton.pack()
        return dataGlobal
    lev = float(lenstr)
    s2 = str(lev)
    if len(s2) < 13:
        while len(s2) <13:
            s2 = s2 + '0'
    if len(s2) > 13:
        s2 = s2[:13]
        
        
    #global threshVal
    global powerVal
    
    
    thresh = "50" #threshVal.get() deprecated with current STM code implementation, still send over UART to keep packet size/shape
    power = powerVal.get()
    
    if len(thresh) < 4:
        while len(thresh) <4:
            thresh =  '0' + thresh
    if len(thresh) > 4:
        thresh = thresh[:4]
    
    if len(power) < 4:
        while len(power) <4:
            power = power + '0'
    if len(power) > 4:
        power = power[:4]
    
    out = "S[" + s2 +','+ thresh + ',' + power + ']'
    print(out)

    #S[######.######,####,#.###]

    ser.write(bytes(out,'utf-8'))
    ser.reset_input_buffer()

    serialString = ""
    count = 0
    bufferLength = 1002
    dataBuffer = [0] * bufferLength
    foundData = False

    while 1:
        currentTime = time.perf_counter()

        try:
            
            serialString = ser.readline()   # read a '\n' terminated line
        except:
            if(foundData == True):
                break

        try:
            newString = serialString.decode('utf-8')
            #print(newString)
            try:
                intVal = float(newString)
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
                    time.sleep(1)
                    if (ser.in_waiting == 0):
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

    return dataBuffer

#display speed to button
def displayData(sampleNum, speedNum):
    sample.set("Sample: " + str(sampleNum) + " = " + str(sampleNum*0.78125) + " us")
    speed.set(str(speedNum) + " m/s")

#plot data
def plot(plotData, sampleNum): 
    #plot data
    numbltime = [];
    for x in range(len(plotData)):
        numbltime.append(x * .78125)
    plot1.clear()
    #print(numbltime)
    plot1.plot(numbltime,plotData)
    
    trimmedarray = plotData[30:len(plotData)-60]
    
    ymax = max(trimmedarray) + 500
    ymin = min(trimmedarray) - 500
    
    sampleTime = sampleNum * .78125
    plot1.set_xlim(0* .78125,940 * .78125)
    plot1.set_ylim(ymin, ymax)
    plot1.set_xlabel("Time (us)")
    plot1.set_ylabel("Amplitude")
    plot1.set_title("Received Signal")
    plot1.axvline(x=(sampleTime), ymin=0, ymax = 65000, linewidth=2, color='k')

  
    #update canvas in UI
    canvas.draw()

# save a measurement to data.txt
def saveMeasure():
    #print(dataGlobal)
    print(str(len(dataGlobal)))
    if(len(dataGlobal) > 100):
        print("saving data")
        with open('data.csv','a') as f:
            global woodName
            stri = woodName.get()
            stri = stri + ',' + woodLength.get()
            for i in dataGlobal:
                stri = stri + ',' + str(i)
            line = stri + '\n'
            f.write(line)
            arrLine = line.split(',')
            array.append(arrLine)
            lsBox.insert(len(arrLine),arrLine[0])

# load data from a stored value
def loadData():
    #print("dummy")
    tuple = lsBox.curselection()
    index = tuple[0]
    work = array[index].copy()
    global woodName
    woodName.delete(0,len(woodName.get()))
    woodName.insert(0,work[0])
    work.pop(0)
    #print(work)
    global woodLength
    woodLength.delete(0,len(woodLength.get()))
    woodLength.insert(0,work[0])
    work.pop(0)


    worklen = len(work)
    work[worklen-1] = work[worklen-1].strip()
    workNum = []
    for string in work:
        try:
            workNum.append(float(string))
        except ValueError:
            workNum.append(string)
    #print(workNum)
    global dataGlobal
    dataGlobal = workNum.copy()

    
    speedNum = workNum[1]
    sampleNum = workNum[0]
    displayData(sampleNum,speedNum)

    dataGlobal = workNum.copy()
    graphData = workNum.copy()
    graphData.pop(0)
    graphData.pop(0)
    plot(graphData, sampleNum)
def deleteData():
    tuple = lsBox.curselection()
    index = tuple[0]
    lsBox.delete(index)
    array.pop(index)
    tempTXT = []
    with open('data.csv','r') as f:
        tempTXT = f.readlines
        tempTXT.pop(index)
    with open('data.csv','w') as f:
        f.writelines(tempTXT)
    
#define root
root = Tk()
root.title("test app")
root.geometry("1200x900") 

#create figure for plot
fig = Figure(figsize = (7, 4), 
                 dpi = 100) 
plot1 = fig.add_subplot(111) 
plot1.set_xlim(0,950)
plot1.set_ylim(29000,32000)
plot1.set_xlabel("Time (us)")
plot1.set_ylabel("Amplitude")
plot1.set_title("Received Signal")

#Set up graph canvas
canvas = FigureCanvasTkAgg(fig, master = root)
canvas.draw() 
canvas.get_tk_widget().grid(row=0,column=0) 

woodLabel = ttk.Label(text="Wood Name")
woodName = ttk.Entry(width=50)
woodName.insert(0,"Wood")
lengthLabel = ttk.Label(text="Wood Length (cm)")
woodLength = ttk.Entry(width=50)


woodLabel.grid(row=1,column=1)
woodName.grid(row=2,column=1)
lengthLabel.grid(row=3,column=1)
woodLength.grid(row=4,column=1)

# woodLabel.pack(side = LEFT)
# woodName.pack(side = LEFT)
# lengthLabel.pack(side = RIGHT)
# woodLength.pack(side = RIGHT)

# threshlabel/threshVal deprecated for now
#threshLabel = ttk.Label(text="Threshold")
#threshVal = ttk.Entry(width=50)
#threshVal.insert(0,"50")
powerLabel = ttk.Label(text="Power")
powerVal = ttk.Entry(width=50)
powerVal.insert(0,"2.0")

#threshLabel.pack()
#threshVal.pack()
powerLabel.grid(row=5,column=1)
powerVal.grid(row=6,column=1)




#button to take measurement
plot_Button = ttk.Button(root, text="Measure", command=measure)
plot_Button.grid(row=7,column=1)

#speed output label
speed = StringVar()
speed.set("No Speed Yet")
speedLabel = ttk.Label(root, textvariable=speed)
speedLabel.grid(row=8,column=1)

#sample triggered output label
sample = StringVar()
sample.set("No Samples Yet")
sampleLabel = ttk.Label(root, textvariable=sample)
sampleLabel.grid(row=9,column=1)

save_Button = ttk.Button(root, text="Save data", command=saveMeasure)
save_Button.grid(row=10,column=1)

#list data
lsBox = Listbox(selectmode=SINGLE, width=40)
count = 0
for arr in array:
    lsBox.insert(count, str(arr[0]))
    count+=1
lsBox.grid(row=11,column=1)


load_Button = ttk.Button(root, text="Load data", command=loadData)
load_Button.grid(row=12,column=1)



rescan_serial = ttk.Button(root, text="Rescan Serial Ports", command=scanSerial)
serialBox = Listbox(selectmode=SINGLE,width = 40)
count=0
for obj in serialPorts:
    serialBox.insert(count, obj + " : " + serialInfo[count])
    count+=1

deleteButton = ttk.Button(root,text="Delete Measurement", command=deleteData)

deleteButton.grid(row=13,column=1)



rescan_serial.grid(row=9,column=0)
serialBox.grid(row=11,column=0)


#begin application loop
root.mainloop()



