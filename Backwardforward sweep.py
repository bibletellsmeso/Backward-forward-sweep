# Developed by Hyun-Su Shin Nov. 2022
# This Code is developed and tested on Python 3.8

#%% Library
import numpy as np
import pandas as pd
import cmath, math
import timeit
import matplotlib.pyplot as plt

DEBUG = False

# Constants
MAX_ITERS = 200
MAX_ERROR = 1e-6

S_BASE_MVA = 1 # 100MVA?
V_BASE_KV = 12.66

S_base = S_BASE_MVA
V_base = V_BASE_KV
Z_base = (V_base**2)/S_base

#%%
def getPolar(var):
    PRECISION = 5
    USE_DEGREES = True
    magnitude = abs(var)
    angle = cmath.phase(var)

    if (magnitude < 0.1 or magnitude > 1e3): # display in exponential form
        magnitude = '{num:.{prec}e}'.format(num=magnitude, prec=PRECISION)
    else:
        magnitude = round(magnitude, PRECISION)

    if USE_DEGREES: # True
        return f"{magnitude}∠{round(np.degrees(angle), PRECISION)}°"
    else:
        return f"{magnitude}∠{round(angle, PRECISION)} rad"

def getPower(current:complex, impedance:complex) -> complex:
    return np.abs(current)**2 * impedance

# matrix 구조의 data의 연산을 일괄적으로 처리할 수 있도록 시퀀스형 자료를 함수의 매개변수로 포함(?)
getPolar = np.vectorize(getPolar)
getPower = np.vectorize(getPower)

#%% Data read
print("Fetching data...")
startTime = timeit.default_timer()
BusData = pd.read_csv('33Bus.txt', sep = "\t", names=['BusNum', 'BusType', 'PG', 'QG', 'PL', 'QL', 'Voltage', 'Angle'], encoding="cp949")
BusData.QL = BusData.QL.apply(lambda x : complex(1j*x))
# BusData.QL = BusData.QL.apply(lambda s : s/S_base/1000) # p.u.
if DEBUG:
    print("Bus Data")
    print(BusData)
    
LineData = pd.read_csv('33Line.txt', sep = "\t", names=['FromNode', 'ToNode', 'Resistance', 'Reactance', 'Suceptance'], encoding="cp949")
LineData.Reactance = LineData.Reactance.apply(lambda x : complex(1j*x))
LineData.insert(5, 'Impedance', LineData.Resistance + LineData.Reactance)
# LineData.Impedance = LineData.Impedance.apply(lambda r : r/Z_base)
if DEBUG:
    print("Line Data")
    print(LineData)
    
#%% The voltage at firts node is already 1 p.u.
# Assume all other values are also 1 p.u.
V = np.ones(BusData.__len__(), dtype=np.complex64)
VOld = V.copy()
if DEBUG:
    print(f"{V=}")

# The load current draw at first node is already 0 p.u.
# Assume all other values are also 0 p.u.   
iLoad = np.zeros(BusData.__len__(), dtype=np.complex64) # in p.u.
iLine = np.zeros(LineData.__len__(), dtype=np.complex64) # fill it with zeros too

stopTime = timeit.default_timer()
print(f"-> Data fetched successfully in {stopTime-startTime} seconds.")
#%% Backward/Forward Sweep

startTime = timeit.default_timer()
for iter in range(MAX_ITERS):
    print(f"iteration: {iter+1}")
    
    # BACKWARD
    # enumerate: 리스트의 순서와 값(0부터)을 전달, 자료형(list, set, tuple, dictionary, string)을 입력으로 받아 인덱스 값을 포함하는 객체를 리턴
    for i, (vBus, sBus) in enumerate(zip(V, (BusData.PL + BusData.QL))):
        iLoad[i] = np.conj(sBus/vBus)
    if DEBUG:
        print(f"{list(iLoad)=}")
    
    # reversed: 거꾸로 루프 돌리기 (리스트 형태)
    for i, EndNode in reversed(list(enumerate(LineData.ToNode))): # enumerate() -> tuple, to upstream transpose list
        if EndNode not in set(LineData.FromNode):
            iLine[i] = iLoad[i+1]
        else:
            boolSelector = LineData.FromNode == EndNode
            if DEBUG:
                print(EndNode)
                print(boolSelector)
                print(iLine[boolSelector])
                print(iLoad[EndNode-1])
            iLine[i] = np.sum(iLine[boolSelector]) + iLoad[i+1]
            
        if DEBUG:
            print(f"{list(iLine)=}")
            
    # FORWARD
    for i, (I, Z) in enumerate(zip(iLine, LineData.Impedance)):
        V[LineData.ToNode[i]-1] = V[LineData.FromNode[i]-1] - I * Z
        
    if np.max(np.abs(np.subtract(V, VOld))) < MAX_ERROR:
        print(f"--> Error requirement statisfied in {iter+1} iters.")
        break
    VOld = np.copy(V)
    if DEBUG:
        print(f"{list(V)=}")

stopTime = timeit.default_timer()
print(f"-> Calculation done in {stopTime-startTime} seconds.")
print("#"*70)
print("Bus voltages: ")
[print(f"{str(i).zfill(2)}-> {line}") for i, line in enumerate(list(getPolar(V)))]
# print("Line currents: ")
# [print(f"{str(i).zfill(2)}-> {line}") for i, line in enumerate(list(iLine))]
print("Line currents: ")
[print(f"{str(i).zfill(2)}-> {line}") for i, line in enumerate(list(getPolar(iLine)))]

print("#"*70)
sIn = getPolar(V[0]*np.conj(iLine[0])*S_base*1e3)
ploss = np.real(np.sum(getPower(iLine, LineData.Impedance)))
sOut= getPolar((np.sum(BusData.PL + BusData.QL) + np.sum(getPower(iLine, LineData.Impedance)) )*S_base*1e3)
print(f"Line losses: {ploss*S_base*1e3} kW")
print(f"#S_in = {sIn} kVA  #S_out = {sOut} kVA")

# plot(xData=BusData.BusNum, xLabel="Bus Number", yData1=abs(V), yLabel1="v (p.u.)", yData2=None, yLabel2='', legend =['voltage'], title="Bus voltages plot")

def plot(xData:np.array, xLabel:str, yData1:np.array, yLabel1:str, yData2:np.array, yLabel2:str, legend:list, title="plotName", savePath="fig.png" ):
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    fig, ax1 = plt.subplots(figsize=(12,9))
    ax1.minorticks_on() # display minor ticks
    ax2 = ax1.twinx() # share x axis and seprate y axis
    # set x-axis label
    ax1.set_xlabel(xLabel, fontsize = 28)
    # set y-axis label
    ax1.set_ylabel(yLabel1, fontsize=28)
    ax2.set_ylabel(yLabel2, fontsize=28)

    ax1.plot(xData, yData1, '-', lw=2, color='mediumblue')
    ax2.plot(xData, yData2, '--', lw=2, color="#FA7268") # Angle

    ax1.grid(which='major', alpha=0.7, linestyle = '--', linewidth = 0.5)
    # ax.grid(color='black',  which='minor', linestyle = '--', linewidth = 0.5)
    # ax1.set_title(title, fontsize=28)
    fig.legend(legend, fontsize=18)
    plt.savefig(savePath, dpi=300, bbox_inches='tight')
    plt.show()


plot(xData=BusData.BusNum, xLabel="Bus Number", yData1=abs(V), yLabel1="v (p.u.)", yData2=[cmath.phase(v) for v in V], yLabel2="∠°", legend =['voltage', 'Angle'], title="Bus voltages plot")