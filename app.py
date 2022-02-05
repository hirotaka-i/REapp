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
# 	img = Image.open(image_file)
# 	return img 


def main():
    price = 1000 * st.sidebar.number_input('Property price in K', value=300, step=1)
    rehab_cost = st.sidebar.slider("Rehab cost", 0, 100000, step=1000, value=10000)
    closing_cost_pct = st.sidebar.slider("Closing cost % to the property price ", 0, 100, value=5)
    b = Property('test', price=price, rehab_cost=rehab_cost, closing_cost_ratio=closing_cost_pct/100)
    down_payment_ratio = 1/100 * st.sidebar.slider("Down payment % to the property price ", 0, 100, value=20)
    years = st.sidebar.slider("Morgage duration in years", 0, 30, value=30)
    interest_rate= 1/100 * st.sidebar.slider('Morgage interest in %', 2.50, 6.00, step=0.01, value=4.00)
    appreciation_year = 1/100 * st.sidebar.slider("Property appreciation - annual average (%) ", 0.0, 20.0, value=3.0)
    hoa = st.sidebar.slider('Monthly HOA', 0,1000, step=10, value=0)
    tax_value = round(0.01 * price / 12)
    tax = 1/100 * st.sidebar.slider("Property tax (monthly) ", 0, 5*tax_value, value=tax_value)
    tax_rate = tax * 12 / price
    insurance_value = round(0.004 * price / 12)
    insurance = 1/100 * st.sidebar.slider("Insurance (monthly)", 0, insurance_value*3, value=insurance_value)
    insurance_rate = insurance * 12 / price
    st.text(f'{b.name}')
# git add app.py;git commit -m "debug";git push -u origin main

if __name__ == '__main__':
	main()

