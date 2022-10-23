"""
Created on 23rd Sept 2022

@author: Rudraksh (Rudy) Mishra
"""

#%%
'''
Install pandasql to run sql commands on pandas dataframe
'''
#get_ipython().system('pip install -U pandasql')

#%%
'''Importing required libraries after installing'''

import pandas as pd
import numpy as np #for array computations
from pandasql import sqldf #Importing panda sql
import matplotlib.pyplot  as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore') #to remove warning pop-ups

#%%
'''1. Reading all provided dataframes'''

# To read the excel files please store the code and data in same directory OR change the file directory of files below
kw_performance = pd.read_excel('KW_Performance_L120D.XLSX') 
kw_performance.columns= kw_performance.columns.str.strip().str.lower() #Returning lowercased values of column names for easier calls
kw_performance.rename(columns={'kw id': 'kw_id'},inplace=True) #Renaming columns to replace space with underscore (easier for sql calls)
kw_performance['kw_id'] = kw_performance['kw_id'].apply(str) #changing kw_id to str for easier use in later functions
#print(kw_performance.head(10)) #calls the first 10 rows of dataframe

#%%

inventory_current_onsite = pd.read_excel('Inventory_Current_Onsite.XLSX')
inventory_current_onsite.columns= inventory_current_onsite.columns.str.strip().str.lower()
#print(inventory_current_onsite.tail(10)) #calls the last 10 rows of dataframe

#%%

inventory_historical = pd.read_excel('Inventory_Historical.XLSX')
inventory_historical.columns= inventory_historical.columns.str.strip().str.lower()
#print(inventory_historical)

#%%

kw_attributes = pd.read_excel('KW_Attributes.XLSX')
kw_attributes.columns= kw_attributes.columns.str.strip().str.lower()
kw_attributes.rename(columns={'kw id': 'kw_id','ad group': 'ad_group','match type': 'match_type','quality score': 'quality_score','est first pos. bid': 'est_first_pos_bid','est top of page bid': 'est_top_page_bid'},inplace=True)
kw_attributes['kw_id'] = kw_attributes['kw_id'].apply(str)
#print(kw_attributes)

#%%

make_model_ARS = pd.read_excel('Make_Model_ARS.XLSX')
make_model_ARS.columns= make_model_ARS.columns.str.strip().str.lower()
make_model_ARS.rename(columns={'make model': 'make_model'},inplace=True)
#print(make_model_ARS)

#%%
''' 2. Aggregate KW data to get CVR for AG, Mk/Mo/Yr, Mk/Mo and Mkt data'''

#%%
'''2.1 Extracting market, make, model, year from ad_group column in kw_attributes''' 

kw_attributes2 = kw_attributes[['ad_group','kw_id']]
kw_attributes2[['d','r','market','make','model','yr']] = kw_attributes2['ad_group'].str.split('-', expand=True)
kw_attributes2 = kw_attributes2[['kw_id','market','make','model','yr']]
kw_attributes2['kw_id'] = kw_attributes2['kw_id'].astype(str)
splits = [kw_attributes2[col].str.split(pat='_', expand=True).add_prefix(col) for col in kw_attributes2.columns]
clean_df = pd.concat(splits, axis=1)
clean_df = clean_df.drop(['make0','model0','yr0'], axis=1)
clean_df.rename(columns={'make1': 'make','model1': 'model','yr1': 'yr','kw_id0': 'kw_id','market0': 'market'},inplace=True)
#print(clean_df.head(5))

#%%
'''
The sqldfmethod is used to query the Dataframes and it requires 2 inputs:
            a) The SQL query string
            b) globals()or locals() function
'''
pysqldf = lambda q: sqldf(q, globals()) 
query='select market,keyword from clean_df c join kw_attributes kw_a on c.kw_id=kw_a.kw_id'
mkt_kw=pysqldf(query)
#print(mkt_kw.head(5))

#%%
'''Aggregate KW data to get AG_CVR'''

query='select * from kw_performance perf join ( select * from kw_attributes ) attr on perf.kw_id = attr.kw_id'
adg_cvr_t=pysqldf(query)
adg_cvr_t=adg_cvr_t.groupby(['ad_group'])['clicks','conversions'].sum().reset_index()
adg_cvr_t['cvr']=adg_cvr_t['conversions']/adg_cvr_t['clicks']
#print(adg_cvr_t.head(5))

#%%
'''2.3)   Aggregate KW data to get mk_mo_yr_CVR'''

query='select * from kw_performance perf join ( select * from clean_df ) attr on perf.kw_id = attr.kw_id'
mk_mo_yr_cvr_t=pysqldf(query)
mk_mo_yr_cvr_t=mk_mo_yr_cvr_t.groupby(['make','model','yr'])['clicks','conversions'].sum().reset_index()
mk_mo_yr_cvr_t['cvr']=mk_mo_yr_cvr_t['conversions']/mk_mo_yr_cvr_t['clicks']
#print(mk_mo_yr_cvr_t.head(5))

#%%
'''2.4)   Aggregate KW data to get mk_mo_CVR'''

query='select * from kw_performance perf join ( select * from clean_df ) attr on perf.kw_id = attr.kw_id'
mk_mo_cvr_t=pysqldf(query)
mk_mo_cvr_t=mk_mo_cvr_t.groupby(['make','model'])['clicks','conversions'].sum().reset_index()
mk_mo_cvr_t['cvr']=mk_mo_cvr_t['conversions']/mk_mo_cvr_t['clicks']
#print(mk_mo_cvr_t.head(5))

#%%
'''2.5)   Aggregate KW data to get mkt_CVR'''

query='select * from kw_performance perf join ( select * from clean_df ) attr on perf.kw_id = attr.kw_id'
mkt_cvr_t=pysqldf(query)
mkt_cvr_t=mkt_cvr_t.groupby(['market'])['clicks','conversions'].sum().reset_index()
mkt_cvr_t['cvr']=mkt_cvr_t['conversions']/mkt_cvr_t['clicks']
#print(mkt_cvr_t.head(5))

#%%
'''2.6)   Aggregate Kw_id data to get kw_CVR'''

query='select * from kw_performance perf join ( select * from kw_attributes ) attr on perf.kw_id = attr.kw_id'
kw_cvr_t=pysqldf(query)
kw_cvr_t=kw_cvr_t.groupby(['keyword'])['clicks','conversions'].sum().reset_index()
kw_cvr_t['cvr']=kw_cvr_t['conversions']/kw_cvr_t['clicks']
#print(kw_cvr_t.head(5))

#%%
''' 3. Building functions for each individual bidding logic'''

#%%
'''3.1) Returns make,model,year for the keyword'''

def get_makemodelyear(k):
    query = 'select keyword,make,model,yr from clean_df join kw_attributes kw_a on clean_df.kw_id=kw_a.kw_id group by 1,2,3'
    ans=pysqldf(query)
    ans1 = ans.loc[ans['keyword'] == k, 'make'].values[0]
    ans2 = ans.loc[ans['keyword'] == k, 'model'].values[0]
    ans3 = ans.loc[ans['keyword'] == k, 'yr'].values[0]
    return ans1,ans2,ans3

#%%
'''3.2) Returns make_model_ARS for the make+model'''
def get_mkmo_ARS(mkmo):
    query = "Select ars from make_model_ARS where LOWER(make_model) = LOWER(\'"+ mkmo+"\');" 
    return pysqldf(query)

#%%
'''3.3) Returns CVR for keyword,ad_group,mk_mo_yr,mk_mo,mkt depending on the input'''

def getConversionandRate(attribute, value):

    if attribute == 'keyword':
        query = 'select * from kw_cvr_t' 
        ans=pysqldf(query)
        ans1 = ans.loc[ans['keyword'] == value[0],'conversions'].values[0]
        ans2 = ans.loc[ans['keyword']==value[0],'cvr'].values[0]

    elif attribute == 'ad_group':
        query = 'select * from adg_cvr_t'
        ans=pysqldf(query)
        ans1 = ans.loc[ans['ad_group'] == value[0],'conversions'].values[0]
        ans2 = ans.loc[ans['ad_group']==value[0],'cvr'].values[0]
    elif attribute == 'mk_mo_yr':
        query = 'select * from mk_mo_yr_cvr_t'
        ans=pysqldf(query)
        ans1 = ans.loc[(ans.make == value[0]) & (ans.model == value[1]) & (ans.yr == value[2])].iloc[0]['conversions']
        ans2=ans.loc[(ans.make == value[0]) & (ans.model == value[1]) & (ans.yr == value[2])].iloc[0]['cvr']
    elif attribute == 'mkt':
        query33 = "select * from mkt_cvr_t"
        ans=pysqldf(query33)
        ans1 = ans.loc[ans['market'] == value[0],'conversions'].values[0]
        ans2 = ans.loc[ans['market']==value[0],'cvr'].values[0]
    elif attribute == 'mk_mo':
        query11 = 'select * from mk_mo_cvr_t'
        ans=pysqldf(query11)
        df = ans.loc[(ans['make'] == value[0]) & (ans['model'] == value[1])]
        ans1 = df.iloc[0]['conversions']
        ans2 = df.iloc[0]['cvr']
    return ans1,ans2


#%%
'''3.4) Calculates intial bid based on bidding logic from step-1'''

def new_bid_calc(kw_id):
    ''' calculated the new bid price '''
    query = "select kw_id,keyword from kw_attributes"
    t_k=pysqldf(query)
    keyword = t_k.loc[t_k['kw_id'] == kw_id,'keyword'].values[0]
    make, model, year = get_makemodelyear(keyword)
    mk_mo_ars = get_mkmo_ARS(make + " " + model)
    #print(mk_mo_ars)
    kw_conv, kw_cvr = getConversionandRate('keyword', [keyword])
    #print(kw_cvr)
    if kw_conv > 10:
        return [(kw_cvr * mk_mo_ars).to_numpy(), 0]

    query = "select ad_group from kw_attributes where LOWER(kw_id) = LOWER(\'" + kw_id + "\')"
    adg_kw = pysqldf(query).to_numpy()[0][0]
    #print(adg_kw)
    ad_conv, ad_cvr = getConversionandRate('ad_group', [adg_kw])
    #print(ad_conv, ad_cvr)
    if kw_conv < 11 and ad_conv > 10:
        return [(ad_cvr * mk_mo_ars).to_numpy(), 0]
 
    mk_mo_yr_conv, mk_mo_yr_cvr = getConversionandRate('mk_mo_yr', [make, model, year])
    if ad_conv < 11 and mk_mo_yr_conv > 10:
        return [(mk_mo_yr_cvr * mk_mo_ars).to_numpy(), 1]

    mk_mo_conv, mk_mo_cvr = getConversionandRate('mk_mo', [make, model])
    if mk_mo_yr_conv < 11 and mk_mo_conv > 10:
        return [(mk_mo_cvr * mk_mo_ars).to_numpy(), 1]

    if mk_mo_conv < 11:
        query = "select est_first_pos_bid from kw_attributes where LOWER(kw_id) = LOWER(\'" + kw_id + "\');"
        est_first_pos_bid = pysqldf(query)
        est_first_pos_bid=est_first_pos_bid.to_numpy()[0][0]
        return [est_first_pos_bid, 1]


#%%
'''3.5) Calculates the revised bid (step-2) based on intial bid'''


def revised_bid(kw_id, bid):
    query = "select kw_id,keyword from kw_attributes"
    t_k=pysqldf(query)
    keyword = t_k.loc[t_k['kw_id'] == kw_id,'keyword'].values[0]
    
    changed_bid = bid[0][0][0]
    #print('inti',bid[0][0][0])
    make, model, year = get_makemodelyear(keyword)

    cur_inv=inventory_current_onsite.loc[(inventory_current_onsite['make'] == make) & (inventory_current_onsite['model'] == model) & (inventory_current_onsite['year'] == 2000+int(year))].iloc[0]['currentonsiteinventory'].sum()
    hist_inv=inventory_historical.loc[(inventory_historical['make'] == make) & (inventory_historical['model'] == model) & (inventory_historical['year'] == 2000+int(year))].iloc[0]['histavginv'].sum()
    #print('inv',cur_inv,hist_inv)
    if cur_inv < hist_inv:
        percentage_reduce = ((hist_inv - cur_inv)/(hist_inv)) * 50/100
        #print(percentage_reduce)
        changed_bid = bid[0][0][0]-(percentage_reduce * bid[0][0][0])
        #print(changed_bid)
    if bid[1] == 1:
        query="select * from clean_df where LOWER(kw_id) = LOWER(\'" + kw_id + "\');"
        test=pysqldf(query)
        test=test['market'].to_numpy()[0]
        query="select * from mkt_cvr_t where LOWER(market) = LOWER(\'" + test + "\');"
        mkt_cvr_3=pysqldf(query)
        mkt_cvr_3=mkt_cvr_3['cvr'].to_numpy()[0]

        query = "select sum(conversions)/CAST(sum(clicks)as double precision) as cvr from kw_performance;"
        overall_cvr = pysqldf(query).to_numpy()
        changed_bid = changed_bid+(((mkt_cvr_3-overall_cvr[0][0] ) / 2) * changed_bid)

    query = "select quality_score from kw_attributes where LOWER(kw_id) = LOWER(\'" + kw_id + "\');"
    qs = pysqldf(query)
    qs=qs.to_numpy()[0][0]
    #print(qs)
    query = "select est_top_page_bid from kw_attributes where LOWER(kw_id) = LOWER(\'" + kw_id + "\');"
    est_top_page_bid = pysqldf(query)
    est_top_page_bid=est_top_page_bid.to_numpy()[0][0]
    #print(est_top_page_bid)
    query = "select est_first_pos_bid from kw_attributes where LOWER(kw_id) = LOWER(\'" + kw_id + "\');"
    est_first_pos_bid = pysqldf(query)
    est_first_pos_bid=est_first_pos_bid.to_numpy()[0][0]
    #print(est_first_pos_bid)
    #print('avg',(est_first_pos_bid+est_top_page_bid)/2)
    if qs > 7 and changed_bid > est_first_pos_bid:
        changed_bid = est_first_pos_bid
    
    elif qs < 8 and qs > 5:
    
        if changed_bid > ((est_first_pos_bid+est_top_page_bid)/2):
            changed_bid = min(changed_bid, (est_first_pos_bid+est_top_page_bid)/2)

    elif qs < 6:
        value = (est_top_page_bid * 0.9) + (est_first_pos_bid * 0.1)
        #print('val',value)
        if changed_bid > value:
            changed_bid = value

    if changed_bid > 12 or changed_bid > 12:
        changed_bid = 12.0
    return changed_bid 

#%%

'''3.6) Calculates intial final bid if kewyword match is Broad'''

def revise2_bid(bid, kw_id, final_bid):

    query = "select kw_id,keyword from kw_attributes"
    t_k=pysqldf(query)
    keyword = t_k.loc[t_k['kw_id'] == kw_id,'keyword'].values[0]
    
    query = "select distinct keyword from kw_attributes where ad_group in (select distinct ad_group from kw_attributes where LOWER(keyword) = LOWER(\'" + keyword + "\') )  and LOWER(match_type) = \'exact\'"
    rows = pysqldf(query).to_numpy()
    min_group_bid = 12.0
    for keyword in rows:
        min_group_bid = min(min_group_bid, final_bid[keyword[0]])
    for keyword in rows:
        if bid > final_bid[keyword[0]]:
            bid = min_group_bid
            break
    return bid

#%%
''' Main Function stores the final bid value in csv file and calls other fuctions sequentially ''' 

def main():
   
    query = "select distinct kw_id from kw_attributes;"
    kw_ids = pysqldf(query).to_numpy()
    query = "select distinct keyword from kw_attributes;"
    keywords = pysqldf(query).to_numpy()
    final_bid = dict()
    
    for ids in kw_ids:
        new_bid = new_bid_calc(ids[0])
        final_bid[ids[0]] = revised_bid(ids[0], new_bid)
    #print(final_bid)
        
    for ids in kw_ids:
        query = "select distinct match_type from kw_attributes where LOWER(keyword) = LOWER(\'" + ids[0] + "\');"
        match = pysqldf(query)
        match['match_type']=match['match_type'].str.lower()
        if (match['match_type'] == "broad").any():
            final_bid[ids[0]] = revise2_bid(final_bid[ids[0]], ids[0], final_bid)

    file = open('output.csv', 'w')
    file.write('{0},{1}\n'.format('keyword_id', 'bid'))
    for ids in kw_ids:
            file.write('{0},{1}\n'.format(ids[0], final_bid[ids[0]]))
    file.close()
    
if __name__ == '__main__':
    main()

#%%
''' 5. Data Exploration and Analysis (Not a required part of assignment) '''
print('---------------------------------DATA ANALYSIS--------------------------------------------')
output_bid = pd.read_csv('finall.csv')
query='select * from output_bid o left join kw_attributes kw_a on kw_a.kw_id=o.keyword_id join kw_performance perf on perf.kw_id=o.keyword_id'
merged=pysqldf(query)
query='select * from merged join ( select * from clean_df ) attr on merged.kw_id = attr.kw_id'
m2=pysqldf(query)

ma_mo_comp=m2.groupby(['make','model'])['clicks','conversions'].sum().reset_index()
ma_mo_comp['cvr']=ma_mo_comp['conversions']/ma_mo_comp['clicks']
ma_mo_comp['ma_mo']=ma_mo_comp['make']+'_'+ma_mo_comp['model']
ma_mo_comp=ma_mo_comp.sort_values(by=['cvr'], ascending=False)
print('---------------------------------Make_Model_CVR_Comparison--------------------------------------------')
print(ma_mo_comp)

make_model_g=ma_mo_comp.groupby(['make'])['clicks','conversions'].sum().reset_index()
plt.figure(figsize=(12,8))
sns.pairplot(make_model_g, hue = 'make')
plt.show()
'''
From the above table and graph we can see that Kia Soul Model has the highest cvr, as well as the
highest clicks and conversions followed by Toyota Camry and Carolla
'''
#%%
ma_mo = ma_mo_comp['ma_mo']
cvr= ma_mo_comp['cvr']
plt.figure(figsize=(40,8))
plt.bar(ma_mo[0:21], cvr[0:21])

mkt_comp=m2.groupby(['market'])['clicks','conversions'].sum().reset_index()
mkt_comp['cvr']=mkt_comp['conversions']/mkt_comp['clicks']
mkt_comp=mkt_comp.sort_values(by=['cvr'], ascending=False)
print('---------------------------------Market_CVR_Comparison--------------------------------------------')
print(mkt_comp)

market = mkt_comp['market']
cvr= mkt_comp['cvr']
plt.figure(figsize=(12,8))
plt.bar(market[0:4], cvr[0:4])
'''
From the above table and graph we can see that ATL and DAL have the highest cummulative cvr,
though DAL has highest clicks its CVR is lower than ATL due to lower conversion rates
'''
#%%

print('---------------------------------basic stats--------------------------------------------')
print(m2[['quality_score','est_first_pos_bid','est_top_page_bid']].describe().T)
#%%
plt.figure(figsize=(12,8))
corr_var = m2[['quality_score','est_first_pos_bid','est_top_page_bid']].corr()
sns.heatmap(corr_var, annot=True, square=True, fmt='.2f', cmap='RdYlGn', vmin=-1, mask=np.triu(corr_var, 1))
plt.xticks(fontsize=12, fontweight='bold')
plt.yticks(fontsize=12, fontweight='bold')
plt.title("Heatmap - Correlation among numerical variables", fontsize=20, fontweight='bold')
plt.show()
'''
The above graph is a heatmap of correlation between 'quality_score','est_first_pos_bid','est_top_page_bid'
As we can see none of the variables are highly correlated to each other,
est_first_pos_bid shows a slight correlation with est_top_page_bid, which makes sense as 
bid for top 4 position would be slightly correlated to top position bid. 
'''
#%%
plt.figure(figsize=(12,8))
sns.countplot(x='conversions', hue='make', data=m2[(m2.conversions <= 7)])
plt.show()
'''
From the above graph we can see the distribution of number of converstions w.r.t make
For example Honda has the highest number of count of converstions when converstions are equal to 7
'''
#%%
plt.figure(figsize=(12,8))
sns.countplot(x='campaign', hue='make', data=m2)
plt.show()
'''
From the above graph we can see different campaigns and their count distribution of make(car manufactures)
In each campagin we have Kia and Ford having the highest number of car counts of 120 and 
Cardillac being the lowest.
'''
#%%

