#Libraries
import pandas as pd
import seaborn as sns
import math
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy import stats
import numpy as np

#Inputs
path = r'Data.xlsx'

#Load Data, Merge and Label Genders
df_PGA = pd.read_excel(path, sheet_name = 'PGA')
df_LPGA = pd.read_excel(path, sheet_name = 'LPGA')

#leave df_PGA unmodifed as there are more features than df_LPGA we may return to
df = pd.concat([df_PGA.iloc[:,0:8], df_LPGA])
df.reset_index(drop = True, inplace = True)

#Explore Data

#Correlation, Distributions, and Modeling
selection = {'Male' : 'PGA', 'Female' : 'LPGA'}
models = {}

for gender in ['Male', 'Female']:
    
    data = df[df['Gender'] == gender]
    
    #Correlation
    correlation = data.iloc[:,2:].corr()
    fig = sns.heatmap(correlation).get_figure()
    fig.savefig(r'heatmap_'+gender+'.png')
    plt.close(fig)
    plt.clf()
    
    #Distributions
    for f in data.columns[3:]:
        for year in set(data['Year'].tolist()):
            X = data[data['Year'] == year]
            X = X[[f]]
            nbins = round(1 + 3.322*math.log(len(X), 10))
            plt.hist(X, nbins, alpha=0.4, label=year)
            plt.legend(loc='upper right')
            plt.xlabel(f)
            plt.ylabel('frequency')
            plt.title('Yearly Distribution of ' + f + ' in the ' + selection[gender])
        plt.savefig(r'hist_'+f+'_'+gender+'.png')
        plt.clf()
    
    #Modeling
    y = data['scoring_avg']
    x = data[['drive_avg', 'drive_acc']]
    LinReg = LinearRegression().fit(x, y)
    r2 = LinReg.score(x, y)
    coef = LinReg.coef_
    #get p values using statsmodels and a chance to compare outputs
    x = sm.add_constant(x)
    model=sm.OLS(y, x).fit()
    #print(model.pvalues)
    #print(model.summary())
    models[selection[gender]] = {'Gender' : gender,
                                 'R2' : r2,
                                 'Coefficients' : {key:val for key, val in zip(data.columns[3:-1], coef)},
                                 'P Values' : model.pvalues.tolist(),
                                 'Summary' : model.summary()}


    #Plot distance vs accuracy for both tours
    #color with average score and include linear fitted relation
    x, y, z = data['drive_avg'], data['drive_acc'], data['scoring_avg']
    fig = plt.scatter(x, y, s=5, c=z, cmap='RdYlGn_r')
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
    models[selection[gender]]['m'] = np.poly1d(np.polyfit(x, y, 1))[1]
    models[selection[gender]]['b'] = np.poly1d(np.polyfit(x, y, 1))[0]
    plt.colorbar(fig)
    plt.xlabel('drive_avg (yards)')
    plt.ylabel('drive_acc (%)')
    plt.title(selection[gender])
    plt.savefig(r'acc_vs_avg_'+gender+'.png')
    plt.clf()


#Experimental Modelling incorporating other features to understand impact
#Not used - comment out

#PGA Modelling Using Distance to Hole
# df_PGA['putt_avg'] = df_PGA['hole_proximity_avg'] / df['putt_avg'] #putt distance
# #df_PGA['putt_avg'] = df_PGA['putt_avg']*18
# y = df_PGA['scoring_avg']/18
# cols = ['strokes_gained_tee_green', 'strokes_gained']
# x = df_PGA[cols]
# LinReg = LinearRegression().fit(x, y)
# r2 = LinReg.score(x, y)
# coef = LinReg.coef_





