import pandas as pd
from sklearn import preprocessing
scaler = preprocessing.MinMaxScaler()

text = pd.read_csv('./data/text_clusters.csv')
geo = pd.read_csv('./data/GeoData.csv')
fin = pd.read_csv('./data/fin_clusters.csv')
sample = pd.read_csv('./data/SampleData_v3.csv')
topics = pd.read_csv('./data/lda_topics.csv')

for col in range(5):
    fin.drop(str(col), inplace = True, axis =1)

df = text.merge(geo[['EIN', 'County', 'Lat', 'Lon']], how = 'inner', on = 'EIN')
df = df.merge(fin, how = 'inner', on = 'EIN')


df = df.merge(sample[['EIN', '/IRS990/GrossReceiptsAmt', '/IRS990/RevenueAmt', '/IRS990/TotalNetAssetsFundBalanceGrp/EOYAmt', 
                      '/IRS990/TotalLiabilitiesGrp/EOYAmt']])

df = df.drop_duplicates()

df = df.rename(index=str, columns={'/IRS990/GrossReceiptsAmt': 'gross_receipts', 
           '/IRS990/RevenueAmt': 'revenue',
           '/IRS990/TotalNetAssetsFundBalanceGrp/EOYAmt': 'fund_balance',
           '/IRS990/TotalLiabilitiesGrp/EOYAmt': 'liabilities',
           'County': 'county',
#            'GeoDistance(km)': 'geo_dist_1',
           'labels': 'fin_labels',
           'Lat': 'latitude',
           'Lon': 'longitude'})

df = df.merge(topics, how = 'inner', on = 'text_labels')


df.to_csv('./data/data_for_viz.csv', index=False)

print('Done.')