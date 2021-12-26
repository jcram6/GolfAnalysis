#Libraries
import pandas as pd
import seaborn as sns
import math
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
import statsmodels.api as sm

#Inputs
pathAdv = r'ASA All PGA Raw Data - Tourn Level.csv'

#Load data, select strokes gained features and meta data, remove NA
df_PGA = pd.read_csv(pathAdv)
df_PGA['year'] = df_PGA['date'].apply(lambda x: int(x[0:4]))
df_PGA['strokes_minus_par_per_hole'] = (df_PGA['strokes'] - df_PGA['hole_par']) / (df_PGA['n_rounds']*18)
cols = ['player',
        'year',
        'strokes_minus_par_per_hole',
        'sg_ott',
        'sg_app',
        'sg_arg',
        'sg_putt']
df_PGA = df_PGA[cols]
df_PGA.dropna(axis = 0, inplace = True)

#Explore Data: feature correlation, distributions, and modeling

models = {}

#Correlation
correlation = df_PGA[cols[2:]].corr()
fig = sns.heatmap(correlation).get_figure()
plt.tight_layout()
fig.savefig(r'heatmap_SG_'+'.png')
plt.close(fig)
plt.clf()

#Distributions
for f in df_PGA.columns[2:]:
    for year in sorted(set(df_PGA['year'].tolist())):
        X = df_PGA[df_PGA['year'] == year]
        X = X[[f]]
        nbins = round(1 + 3.322*math.log(len(X), 10))
        plt.hist(X, nbins, alpha=0.4, label=year)
        plt.legend(loc='upper right')
        plt.xlabel(f)
        plt.ylabel('frequency')
        plt.title('Yearly Distribution of ' + f + ' in the PGA')
    plt.savefig(r'hist_'+f+'_PGA.png')
    plt.clf()

#Modeling (sklearn)
y = df_PGA['strokes_minus_par_per_hole']
x = df_PGA[df_PGA.columns[3:]]
LinReg = LinearRegression().fit(x, y)
r2 = LinReg.score(x, y)
coef = LinReg.coef_

#Modeling (statsmodels) - for p values and as a comparison
x = sm.add_constant(x)
model=sm.OLS(y, x).fit()
#print(model.pvalues)
#print(model.summary())
models['PGA_SG'] = {'Gender' : 'Male',
                 'R2' : r2,
                 'Coefficients' : {key:val for key, val in zip(df_PGA.columns[3:], coef)},
                 'P Values' : model.pvalues.tolist(),
                 'Summary' : model.summary()}
       




