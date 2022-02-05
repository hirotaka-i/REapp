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
    priceK = st.sidebar.number_input('Property price in K', value=300, step=1)
    price = priceK * 1000
    rehab_cost = st.sidebar.slider("Rehab cost", 0, 100000, step=1000)
    closing_cost_pct = st.sidebar.slider("Closing cost ratio to the property price", 0, 100)
    b = Property('test', price=price, rehab_cost=rehab_cost, closing_cost_ratio=closing_cost_pct/100)
    st.text(f'{b.name}')

# git add app.py;git commit -m "debug";git push -u origin main

if __name__ == '__main__':
	main()

