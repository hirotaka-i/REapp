# This is active
import streamlit as st

# File Processing Pkgs
import pandas as pd
import numpy as np
import base64
import datetime as dt
from property_module import Property
from myfunc2 import get_table

today = dt.datetime.today()
version = f'{today.year}{today.month}{today.day}'

def read_file(data_file):
    if data_file.type == "text/csv":
        df = pd.read_csv(data_file)
    elif data_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(data_file, sheet_name=0)
    return (df)


def main():    
    property_name = st.sidebar.text_input("Property Name", value='12-ABCstreet-NY')
    price = 1000 * st.sidebar.number_input('Price (K)', value=350, step=1)
    # price_q = round(price/100/1000)
    rehab_cost = 1000* st.sidebar.slider("Rehab Cost (K)", 0, 200, step=10, value=10)
    rehab_add = 1000* st.sidebar.slider("Added Value by Rehab", 0, 500, step=10, value=0)
    down_payment_ratio = 1/100 * st.sidebar.slider("Down Payment (% to the price, If <20% PMI 1%)", 0, 100, value=20)
    years = st.sidebar.slider("Morgage Length (years)", 0, 30, value=30)
    closing_cost_pct = st.sidebar.slider("Closing Cost (% to the property price)", 0.0, 10.0, value=2.5, step=0.05)
    interest_rate= 1/100 * st.sidebar.slider('Morgage Interest (%)', 2.5, 10.0, step=0.1, value=4.00)
    appreciation_year = 1/100 * st.sidebar.slider("Appreciation (%)", 0.0, 10.0, value=3.0, step=0.1)
    inflation_year = 1/100 * st.sidebar.slider("Inflation (%, affects rental income/cost)", 0.0, 10.0, value=2.5, step=0.1)

    hoa = st.sidebar.slider('HOA (monthly)', 0,1000, step=10, value=0)
    
    tax_value = round(0.01 * price / 12)
    tax = st.sidebar.slider("Tax (preset=ProperyPrice*1%/12)", 0, 5*tax_value, value=tax_value)
    tax_rate = tax * 12 / price
    
    insurance_value = round(0.004 * price / 12)
    insurance = st.sidebar.slider("Insurance (preset=ProperyPrice*0.4%/12)", 0, insurance_value*3, value=insurance_value)
    insurance_rate = insurance * 12 / price
    
    maintenance_value = round(0.005 * price / 12)
    maintenance = st.sidebar.slider("Maintenance (preset=ProperyPrice*0.5%/12)", 0, maintenance_value*3, value=maintenance_value)
    maintenance_rate = maintenance * 12 / price
    
    extra_rehab=0
    rent = st.sidebar.slider("Rent (monthly)", 0, 6000, step=20, value=2000)
    vacancy_rate = 1/100 * st.sidebar.slider("Vacancy Rate (%)", 0, 100, step=5, value=10)
    op_value = round(0.2 * rent)
    op = st.sidebar.slider("Renting Expenses (management etc. preset=rent*0.2)", 0, max(op_value*3,1200), value=op_value, step=10)
    if rent==0:
        op_rate=0
    else:
        op_rate = op / rent
    
    b = Property('test', price=price, rehab_cost=rehab_cost, rehab_add=rehab_add, closing_cost_ratio=closing_cost_pct/100)
    b.sim_loan(down_payment_ratio=down_payment_ratio, years=years, 
               interest_rate=interest_rate)
    b.sim_equity(appreciation_year=appreciation_year)
    b.sim_ex(hoa=hoa, tax_rate=tax_rate, insurance_rate=insurance_rate, 
             maintenance_rate=maintenance_rate, inflation_year=inflation_year)
    b.sim_rent(extra_rehab=extra_rehab, rent=rent, vacancy_rate=vacancy_rate, 
               op_rate=op_rate)
    
    # period of interest including cf turning month
    period_list = [1,11,23,35,47,59,95,119,179,239,299,359]
    cf_plus = [p for p,cf in zip(b.period, b.cf) if cf>0]
    if len(cf_plus)>0:
        period_i = min(cf_plus)
        period_list = period_list + [period_i]
        period_list.sort()
    else:
        period_i = 'None'
    
    st.subheader('Number Breakdowns at Start')
    st.markdown(f"""
* Total Initial Payment: **${b.initial_total:,.0f}**
    * Down Payment: ${b.down_payment_ratio*b.price:,.0f}
    * Closing Cost: ${b.closing_cost_ratio*b.price:,.0f}
    * Rehab Cost: ${b.rehab_cost:,.0f}
    * ARV: ${b.rehab_add + b.price:,.0f}
* Monthly Morgage Payment: **${b.pay:,.0f}**
* PMI: **${b.pmi[0]:,.0f}**
* Net Operating Income: **${b.noi[0]:,.0f}**
    * Income (Rent * (1 - vancancy rate)): **${b.income[0]:.0f}**
    * Operating Expense: **${b.opex[0]:,.0f}**
        * Possessing: ${b.ex[0]:,.0f} (hoa + tax + insurance + maintenance)
        * Renting: ${(b.opex[0]-b.ex[0]):,.0f} (Property management, additional maintenance etc.)
* Cash Flow After Loan: **${b.cf[0]:,.0f}** (NOI - morgage - pmi)
    * Positive Cash Flow at period (month) = {period_i}

                """)

    st.subheader(f'''Comparison: RE vs Stock Market''')
    st.markdown(f"""\
* RE: tg = cash flow + equity gain[property apreciation + paid balance]
* Stock Market: invest_change = monthly capital gain of the initial payment if invested""")
    
    return_year= 1/100 * st.slider("Stock Market Annual Return to compare (%) ", 0.0, 15.0, value=7.5, step=0.1)
    b.sim_invest(return_year=return_year)    
    t = get_table(b)
    st.line_chart(t[['tg','invest_change']])
    
    st.markdown(f"""\
    ##### Cap position (- Initial Capital)
    * RE: Equity at the month + cumsum Cash Flow up to the month
    * Stock Market: Capital at the month""")
    t['RE-Cap'] = t.equity + t.cf.cumsum()
    tt = t.copy()
    tt['Initial Pay'] = b.initial_total
    st.line_chart(tt[['RE-Cap','invest', 'Initial Pay']])
    st.text('Snapshot for capital gain/loss at selected periods (month)')
    
    periods = [i for i in period_list if i <= b.n_pay]
    d = t.loc[periods,:].copy()
    st.dataframe(d[['interest_paid', 'balance_change', 'pmi',
                'pvalue_change', 'hoa', 'tax', 'insurance',
                'maintenance', 'ex', 'rent', 'income', 'opex', 'noi', 'cf', 'tg',
                'invest_change', 'invest', 'RE-Cap']].T)
    st.markdown('* pvalue_change = property appreciatioon (at the month)')
    
    st.subheader('All numbers')
    st.dataframe(t.T, height=8000)
    

    # data download
    def get_table_download_link(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}"  download="{property_name}_{(price/1000):.0f}K_{version}.csv">Download spreadsheet</a>'
        return href
    
    st.subheader("Spreadsheet download  (Transposed format - rows are the periods)")
    st.markdown(get_table_download_link(t), unsafe_allow_html=True)

# git add app.py;git commit -m "debug";git push -u origin main

if __name__ == '__main__':
    main()