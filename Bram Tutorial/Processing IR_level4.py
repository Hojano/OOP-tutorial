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


class IR_dataset:
    def __init__(self,FolderName):
        self.Name = FolderName
        self.filelist = []
        # Find all .dx files in the folder specified and add them to the list of files
        for root, dirs, files in os.walk(FolderName, topdown=True):
            for name in files:
                if '.dx' in name:
                    self.filelist.append(os.path.join(root, name))

        # Load .dx files into dataframe
        self.firsttime = True

        for files in self.filelist:
            if self.firsttime:
                # For the first time, I want to read the wavenumbers and recalculate them since their is/was a bug in that.
                self.FirstSpectrum = j.jcamp_readfile(files)
                self.WavenumbersTemp = self.FirstSpectrum['x']
                self.AmountOfWavenumbers = len(self.WavenumbersTemp)
                self.HighestWaveNumber = self.WavenumbersTemp[0]
                self.LowestWavenumber = self.WavenumbersTemp[-1]
                self.CorrectWavenumbers = np.linspace(self.HighestWaveNumber, self.LowestWavenumber, num=self.AmountOfWavenumbers)

                # defining a dataframe with those wavenumbers to then add the spectra in later
                self.DF = pd.DataFrame({'Wavenumber': self.CorrectWavenumbers})
                self.firsttime = False

            # reading .dx file
            try:
                self.CurrentSpectrum = j.jcamp_readfile(files)
            except:
                print(str(self.CurrentNumber) + ' failed!!')

            # adding Y values of spectrum to DF
            self.DF = pd.concat([self.DF, pd.Series(self.CurrentSpectrum['y'])], axis=1)

            # some code to print the progress
            self.FilesKort = files.replace('.dx', '')
            self.CurrentNumber = self.FilesKort[-4:]
            if self.CurrentNumber[-2:] == '00':
                print(self.CurrentNumber)

        # making the DF the way I want it- with the wavenumbers as columns and the spectra being the rows.
        self.DF = self.DF.set_index(('Wavenumber'))
        self.DF = self.DF.transpose()
        self.DF.columns = self.DF.columns.map(to_float)
        self.DF = self.DF.reset_index(drop=True)


    def plot_allspectra(self):
        # Plotting all spectra
        self.AllSpectraFig = plt.figure()
        self.AllSpectraFigAx = self.AllSpectraFig.add_subplot()
        for i in self.DF.index:
            self.AllSpectraFigAx.plot(self.DF.columns, self.DF.iloc[i, :])
        self.AllSpectraFigAx.title.set_text(self.Name)

    def integrate_and_plot_CO2(self,plot=False):
        # Integrating CO2 peak
        # First finding some parameters for cutting the range
        self.Wavenumbers = self.DF.columns
        self.LowWaveNumberIndex = min(range(len(self.Wavenumbers)), key=lambda i: abs(self.Wavenumbers[i] - 2200))
        self.HighWaveNumberIndex = min(range(len(self.Wavenumbers)), key=lambda i: abs(self.Wavenumbers[i] - 2400))

        self.integrated_list = []
        # then iterating over all spectra and integrating them
        for i in self.DF.index:
            # cut data to relevant area
            self.SpectrumToIntegrate = self.DF.iloc[i, self.HighWaveNumberIndex:self.LowWaveNumberIndex]
            self.CO2_area = scp.integrate.trapezoid(y=self.SpectrumToIntegrate, x=self.SpectrumToIntegrate.index)
            # saving negative since the data is saved from high to low wavenumbers which makes the integration negative.
            self.integrated_list.append(-self.CO2_area)
        if plot:
            # Plot CO2 band over time
            self.CO2Fig = plt.figure()
            self.CO2FigAx = self.CO2Fig.add_subplot()
            self.CO2FigAx.plot(self.integrated_list)

DataSets = {}

FoldersLocation = 'Raw Data'
Folders = os.listdir(FoldersLocation)
print(Folders)
for i in Folders:
    if os.path.isdir((FoldersLocation + '/' + i)):
        print(i)
        DataSets[i] = IR_dataset(FoldersLocation + '/' + i)

CO2CompareFig = plt.figure()
CO2CompareFigAx = CO2CompareFig.add_subplot()
for key, value in DataSets.items():
    value.plot_allspectra()
    value.integrate_and_plot_CO2()
    CO2CompareFigAx.plot(value.integrated_list,label=key)

CO2CompareFigAx.legend()
plt.show()









#Delete at end!
"""

"""