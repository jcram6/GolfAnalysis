#Libraries
import pandas as pd
import requests
import openpyxl

#Functions
def convertDistance(d):
    ft, inch = d.split(" ")
    ft = ft.strip('\'')
    inch = inch.strip("\"")
    total = float(ft) + float(inch)/12
    return total

def returnData(year):
    
        baseUrl = 'https://api.sportradar.us/golf/trial/pga/v3/en/'
        endUrl = '/players/statistics.json?api_key='
        key = 'aw5zr5nky8xcvtxxyfev4ksg'
        url = baseUrl+str(year)+endUrl+key
        response = requests.get(url)
        
        try:
            data = response.json()
        except ValueError:
            print('Error in server response for request from ' + str(year))
            pass
        else:
            df = pd.json_normalize(data, record_path='players')
            #strip verbose naming of columns
            for col in df.columns:
                if 'statistics' in col:
                    newCol = col.split('.')[-1]
                    df.rename(columns = {col : newCol}, inplace = True)
            df['Year'] = year #label year of data
            df['Player'] = df['first_name'] + ' ' + df['last_name'] #concat fullname
            df['hole_proximity_avg'] = df['hole_proximity_avg'].astype(str).apply(convertDistance)
            return df

#Main
def main():

    outputPath = r'/Users/john/Documents/Python/Validere/Data.xlsx'
    
    #gather the data (data before 2016 does not have all statistics desired)
    yearStart = 2016
    yearEnd = 2021
    
    dfs = []
    for year in range(yearStart, yearEnd):
        df = returnData(year)
        dfs.append(df)
        
    dfMaster_PGA = pd.concat(dfs)
    
    #reindex and drop nulls (20/1526 or 1.3% of values) - imputation not feasible/worth it for this
    dfMaster_PGA.reset_index(drop = True, inplace = True)
    dfMaster_PGA.dropna(axis = 0, inplace = True)
    dfMaster_PGA['Gender'] = 'Male'
    
    #filter columns to metadata, driving, putting, and results
    cols = ['Player',
            'Gender',
            'Year',
            'drive_avg',
            'drive_acc',
            'gir_pct',
            'putt_avg',
            'scoring_avg',
            'hole_proximity_avg',
            'scrambling_pct',
            'strokes_gained',
            'strokes_gained_tee_green',
            'strokes_gained_total'
            ]
    dfMaster_PGA = dfMaster_PGA[cols]

    #export to excel for others to view and to be used in analysis script
    with pd.ExcelWriter(outputPath, engine="openpyxl", mode="a", on_sheet_exists="replace") as writer:
        dfMaster_PGA.to_excel(writer, sheet_name = 'PGA', index = False)
    
    
#Run main command
if __name__ == '__main__':
    main()
        
    

