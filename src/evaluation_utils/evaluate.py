import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

class performEvaluation():
    def sigmoid(self, Z):
        return (1/(1+np.exp(-Z)))

    def calculate_accuracy(self, AL, y):
        #calculate accuracy, precision, recall and F1 value here too
        ALc = AL[:, 0]
        yc = y[:, 0]
        
        ALc = ALc > 0.5
        ALc = ALc.astype(int)
        
        total = ALc.shape[0]
        
        TP = np.sum(np.logical_and(ALc==1, yc==1))
        TN = np.sum(np.logical_and(ALc==0, yc==0))
        
        FP = np.sum(np.logical_and(ALc==1, yc==0))
        FN = np.sum(np.logical_and(ALc==0, yc==1))
        
        P = TP / (TP + FP)
        R = TP / (TP + TN)
        F1 = (2 * P * R) / (P + R)
        
        
        acc = np.sum(ALc == yc)/total
        
        
        print("\nAccuracy: {} \n".format(acc))
        print("True Positive: {} \nTrue Negative: {}\nFalse Positive: {} \nFalse Negative: {}\n".format(TP, TN, FP, FN))
        print("Precision: {} \nRecall: {} \nF1 Score: {}\n".format(P, R, F1))
        
        
        ALcr = AL[:, 1]
        ycr = y[:, 1]

        fig, axes = plt.subplots(figsize=(12,6))
        axes.plot(ALcr, label="Predicted Value")
        axes.plot(ycr, label="Actual Value")
        axes.set_ylabel("Percentage Change")
        axes.set_title("Regression Comparision")
        axes.legend(loc=4)
        
        slope, intercept, rval, pval, stderr = linregress(ycr, ALcr)
        print("R-Value: " + str(rval)) #rvalue is between -1 and 1 and can be used for single. Suitable for my purpose. R2 can be used for multiple, gives one and zero
        
        maximum = max(ycr.max(),AL.max())
        minimum = min(ycr.min(),ALcr.min())
        fig2, ax2 = plt.subplots(figsize=(12,6))
        ax2.scatter(ycr,ALcr)
        ax2.plot([minimum, maximum], [minimum, maximum], 'r-', lw=2)
        
        return AL