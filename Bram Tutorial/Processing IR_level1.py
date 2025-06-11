import numpy as np
import collections
import os
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import scipy as scp
import tkinter as tk
import jcamp as j
from tkinter import filedialog

def to_float(x):
    try:
        return float(x)
    except:
        return x

FolderName = 'Raw Data/20230912_BK053_C_550Red'
filelist = []
#Find all .dx files in the folder specified and add them to the list of files
for root, dirs, files in os.walk(FolderName, topdown=True):
        for name in files:
            if '.dx' in name:
                filelist.append(os.path.join(root, name))


#Load .dx files into dataframe
firsttime = True
for files in filelist:

    if firsttime:
        #For the first time, I want to read the wavenumbers and recalculate them since their is/was a bug in that.
        FirstSpectrum = j.jcamp_readfile(files)
        WavenumbersTemp = FirstSpectrum['x']
        AmountOfWavenumbers = len(WavenumbersTemp)
        HighestWaveNumber = WavenumbersTemp[0]
        LowestWavenumber = WavenumbersTemp[-1]
        CorrectWavenumbers = np.linspace(HighestWaveNumber, LowestWavenumber, num=AmountOfWavenumbers)

        #defining a dataframe with those wavenumbers to then add the spectra in later
        DF = pd.DataFrame({'Wavenumber': CorrectWavenumbers})
        firsttime = False

    #reading .dx file
    try:
        CurrentSpectrum = j.jcamp_readfile(files)
    except:
        print(str(CurrentNumber) + ' failed!!')

    # adding Y values of spectrum to DF
    DF = pd.concat([DF, pd.Series(CurrentSpectrum['y'])], axis=1)

    # some code to print the progress
    FilesKort = files.replace('.dx', '')
    CurrentNumber = FilesKort[-4:]
    if CurrentNumber[-2:] == '00':
        print(CurrentNumber)



#making the DF the way I want it- with the wavenumbers as columns and the spectra being the rows.
DF = DF.set_index(('Wavenumber'))
DF = DF.transpose()
DF.columns = DF.columns.map(to_float)
DF = DF.reset_index(drop=True)


#Plotting all spectra
AllSpectraFig = plt.figure()
AllSpectraFigAx = AllSpectraFig.add_subplot()
for i in DF.index:
    AllSpectraFigAx.plot(DF.columns,DF.iloc[i,:])

#Integrating CO2 peak
#First finding some parameters for cutting the range
Wavenumbers = DF.columns
LowWaveNumberIndex = min(range(len(Wavenumbers)), key=lambda i: abs(Wavenumbers[i]-2200))
HighWaveNumberIndex = min(range(len(Wavenumbers)), key=lambda i: abs(Wavenumbers[i] - 2400))
integrated_list = []
#then iterating over all spectra and integrating them
for i in DF.index:
    #cut data to relevant area
    SpectrumToIntegrate = DF.iloc[i,HighWaveNumberIndex:LowWaveNumberIndex]
    CO2_area = scp.integrate.trapezoid(y=SpectrumToIntegrate, x=SpectrumToIntegrate.index)
    #saving negative since the data is saved from high to low wavenumbers which makes the integration negative.
    integrated_list.append(-CO2_area)

#Plot CO2 band over time
CO2Fig = plt.figure()
CO2FigAx = CO2Fig.add_subplot()
CO2FigAx.plot(integrated_list)

plt.show()






