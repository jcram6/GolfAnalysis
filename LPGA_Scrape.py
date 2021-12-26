#Libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl

#Functions
def scrapeUrl(url, year):
    
    baseString = 'https://www.lpga.com/statistics/'
    yearString = '?year='
    
    #send request
    url = baseString + url + yearString + str(year)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    #parse data from response
    table = soup.find("table", attrs={"class" : "table"})
    
    headers = []
    for th in table.findAll("th", attrs={"class" : "table-coltitle"}):
        header = th.text.strip()
        headers.append(header)
        
    data = []
    for tr in table.findAll("tr", attrs={"class" : "body"}):
        row = []
        for td in tr.findAll("td", attrs={"class" : "table-content"}):
            stat = td.text.strip()  
            row.append(stat)
        data.append(row)
    
    #format data into df
    df = pd.DataFrame(data, columns = headers)
    df['Year'] = year
    
    return df

def multiMerge(dfs):
    
    dfMerged = dfs[0]
    
    for df in dfs[1:]:
        dfMerged = pd.merge(dfMerged, df, on = ['Name', 'Year'], how = 'inner')
        
    return dfMerged
    

def main():
    
    outputPath = '/Users/john/Documents/Python/Validere/Data.xlsx'
    
    urls = {
        'drive_acc' : 'driving/driving-accuracy',
        'drive_avg' : 'driving/average-driving-distance',
        'gir_pct' : 'short-game/greens-in-reg',
        'putt_avg' : 'short-game/putting-average',
        'scoring_avg' : 'scoring/scoring-average'
        }
    
    yearStart = 2016
    yearEnd = 2021
    
    dfsMetric = {}
    for metric, url in urls.items():
        dfsYear=[]
        for year in range(yearStart, yearEnd):
            dfsYear.append(scrapeUrl(url, year))
        dfsMetric[metric] = pd.concat(dfsYear)
        
    #join, filter, and clean up dataframes
    dfMaster_LPGA = multiMerge(list(dfsMetric.values()))
    dfMaster_LPGA['Gender'] = 'Female'

    cols = {'Name' : 'Player',
            'Gender' : 'Gender',
            'Year' : 'Year',
            'Average Driving Distance' : 'drive_avg',
            'Percentage' : 'drive_acc',
            'Greens' : 'gir_pct',
            'Putts Average' : 'putt_avg',
            'Average' : 'scoring_avg'
            }
    dfMaster_LPGA = dfMaster_LPGA[list(cols.keys())]
    dfMaster_LPGA.rename(columns = cols, inplace=True)

    dfMaster_LPGA.dropna(axis = 0,inplace = True)
    
    #format data types and divide putt average by 18
    dfMaster_LPGA['drive_avg'] = dfMaster_LPGA['drive_avg'].astype(float)
    dfMaster_LPGA['drive_acc'] = dfMaster_LPGA['drive_acc'].apply(lambda x: x[:-1]).astype(float)
    dfMaster_LPGA['gir_pct'] = dfMaster_LPGA['gir_pct'].apply(lambda x: x[:-1]).astype(float)
    dfMaster_LPGA['putt_avg'] = dfMaster_LPGA['putt_avg'].astype(float)/18
    dfMaster_LPGA['scoring_avg'] = dfMaster_LPGA['scoring_avg'].astype(float)
    
    #export to excel for others to view and to be used in analysis script
    with pd.ExcelWriter(outputPath, engine = "openpyxl", mode= "a", on_sheet_exists="replace") as writer:
        dfMaster_LPGA.to_excel(writer, sheet_name = 'LPGA', index = False)

#Run main command
if __name__ == '__main__':
    main()
    