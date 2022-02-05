import streamlit as st
import streamlit.components.v1 as stc

# File Processing Pkgs
import pandas as pd
import numpy as np
import base64
import datetime as dt
from property_module import Property
from myfunc2 import get_table
import pandas as pd

# import matplotlib.pyplot as plt # don't work...
today = dt.datetime.today()
version = f'{today.year}{today.month}{today.day}'

def read_file(data_file):
    if data_file.type == "text/csv":
        df = pd.read_csv(data_file)
    elif data_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(data_file, sheet_name=0)
    return (df)

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    study_code = df.study.unique()[0]
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}"  download="{study_code}_sample_manifest_selfQC_{version}.csv">Download csv file</a>'
    return href
    
# @st.cache
# def load_image(image_file):
#     img = Image.open(image_file)
#     return img 


def main():
    def analyze(b):
        b.sim_loan(down_payment_ratio=down_payment_ratio, years=years, 
                   interest_rate=interest_rate)
        b.sim_equity(appreciation_year=appreciation_year)
        b.sim_ex(hoa=hoa, tax_rate=tax_rate, insurance_rate=insurance_rate, 
                 maintenance_rate=maintenance_rate, inflation_year=inflation_year)
        b.sim_rent(extra_rehab=extra_rehab, rent=rent, vacancy_rate=vacancy_rate, 
                   op_rate=op_rate)
        b.sim_invest(return_year=return_year)
        return(b)
    
    price = 1000 * st.sidebar.number_input('Price (K)', value=400, step=1)
    rehab_cost = st.sidebar.slider("Rehab Cost", 0, 80000, step=1000, value=10000)
    closing_cost_pct = st.sidebar.slider("Closing Cost (% to the property price)", 0.0, 10.0, value=2.5, step=0.05)
    b = Property('test', price=price, rehab_cost=rehab_cost, closing_cost_ratio=closing_cost_pct/100)
    down_payment_ratio = 1/100 * st.sidebar.slider("Down Payment (% to the property price)", 0, 100, value=20)
    years = st.sidebar.slider("Morgage Length (years)", 0, 30, value=30)
    interest_rate= 1/100 * st.sidebar.slider('Morgage Interest (%)', 2.50, 6.00, step=0.01, value=4.00)
    appreciation_year = 1/100 * st.sidebar.slider("Appreciation (%)", 0.0, 10.0, value=3.0, step=0.1)
    inflation_year = 1/100 * st.sidebar.slider("Inflation (%) ", 0.0, 10.0, value=2.0)
    hoa = st.sidebar.slider('HOA (monthly)', 0,1000, step=10, value=0)
    
    tax_value = round(0.01 * price / 12)
    tax = st.sidebar.slider("Tax (monthly) ", 0, 5*tax_value, value=tax_value)
    tax_rate = tax * 12 / price
    
    insurance_value = round(0.004 * price / 12)
    insurance = st.sidebar.slider("Insurance (monthly)", 0, insurance_value*3, value=insurance_value)
    insurance_rate = insurance * 12 / price
    
    maintenance_value = round(0.005 * price / 12)
    maintenance = st.sidebar.slider("Maintenance (monthly)", 0, maintenance_value*3, value=maintenance_value)
    maintenance_rate = maintenance * 12 / price
    
    extra_rehab=0
    rent = st.sidebar.slider("Rent (monthly)", 0, 8000, step=10, value=2000)
    vacancy_rate = 1/100 * st.sidebar.slider("Vacancy Rate (%)", 0, 100, step=5, value=10)
    op_value = round(0.015 * rent / 12)
    op = 1/100 * st.sidebar.slider("Operating Expenses (monthly)", 0, op_value*3, value=op_value)
    op_rate = op / rent
    
    return_year= 1/100 * st.sidebar.slider("Invest Return to compare (%, annual)", 0, 20, value=8)
    
    analyze(b)
    
    st.text(f'Monthly morgage payment: {b.pay:.2f}')
    st.text(f'Total initial payment: {b.initial_total:.0f}')
    
    t = get_table(b)
    st.text(f'Total Gain (monthly) [tg] vs gain if invested [invested_change]')
    st.line_chart(t[['tg','invest_change']])
    
    st.text('Snapshot for selected periods')
    st.text('* morgage payment = interest_paid + balance_change\n* ex = hoa + tax + insurance\n* opex = ex + montly operation expense')
    periods = [i-1 for i in [1,12,24,36,48,60,96,120,180,240,300,360] if i <= b.n_pay]
    d = t.loc[periods,:].copy()
    st.table(d[['period', 'interest_paid', 'balance_change', 'pmi',
                'pvalue_change', 'hoa', 'tax', 'insurance',
                'maintenance', 'ex', 'rent', 'income', 'opex', 'noi', 'cf', 'tg',
                'invest_change']])
    
    st.text('All numbers')
    st.table(t)
    

# git add app.py;git commit -m "debug";git push -u origin main

if __name__ == '__main__':
    main()