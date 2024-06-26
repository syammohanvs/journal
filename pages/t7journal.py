# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import requests
import json
import streamlit as st
from st_pages import Page, show_pages, add_page_title
import auth_functions
import time
import pandas as pd
import re

from streamlit.logger import get_logger
from dateutil import parser 
from google.cloud import firestore
from google.oauth2 import service_account
from st_pages import Page, show_pages, add_page_title, hide_pages
from collections import defaultdict
from operator import itemgetter
from dhanhq import dhanhq




LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="T7 Journal",
        page_icon="📘",
        # layout="wide",
    )

    show_pages(
        [
            Page("pages/t7journal.py", "T7 Journal", "📘"),
            Page("Home.py", "Home","🏠"),
        ]
    )

    st.markdown("<h1 style='text-align: center; color: #1D9AE2;'>T7 Journal</h1>", unsafe_allow_html=True)
    if 'user_info' not in st.session_state:
        st.warning("Please login to use the application")
        st.stop()

    # st.sidebar.success("Select a demo above.")
    
    st.markdown("<p style='text-align: center; color: black;'>A tool to display trading profit and loss automatically based on user settings.<br>The tool is integrated with Dhan statement API only. So only Dhan users can use this tool.</p>",unsafe_allow_html=True)
    
    def w_div(n, d):
        return n / d if d else 0

    def get_open_trades(trade):        
        
        nettradelist = dict()
        open_unrealised_pnl = open_realised_pnl = 0
        index = j = 0
        contract_in_list = False
        adj_amount = 0         
        
        month_dict = {
            "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
            "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
            "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
         }
        
        length = len(trade)
        while(index < length): 
            
            contract_in_list = False
            len_net = len(nettradelist)
            
            if "BUY" in trade[index].get("transactionType"): 
                
                j = 0
                while(j < len_net):                    
                    if(nettradelist[j].get("contract") == trade[index].get("customSymbol")):                                    
                        qty = nettradelist[j]['tradeqty'] + trade[index].get("tradedQuantity")
                        nettradelist[j]['tradeqty'] = qty
                        nettradelist[j]['ltp'] =  trade[index].get("tradedPrice") 
                        nettradelist[j]['ltt'] =  trade[index].get("exchangeTime")    
                        nettradelist[j]['val'] = nettradelist[j]['val']+ (trade[index].get("tradedQuantity") * trade[index].get("tradedPrice"))
                        contract_in_list = True
                        break
                    else:
                        j = j + 1
                if(contract_in_list == False):                             
                    
                    nettradelist[j] = {'contract':trade[index].get("customSymbol"),'tradeqty':trade[index].get("tradedQuantity"),'ltp':trade[index].get("tradedPrice"),'ltt':trade[index].get("exchangeTime"),'val':trade[index].get("tradedQuantity") * trade[index].get("tradedPrice")}
                     
            if "SELL" in trade[index].get("transactionType"):
                
                j = 0
                while(j < len_net):
                    if(nettradelist[j].get("contract") == trade[index].get("customSymbol")):                                    
                        qty = nettradelist[j]['tradeqty'] - trade[index].get("tradedQuantity")
                        nettradelist[j]['tradeqty'] = qty
                        nettradelist[j]['ltp'] =  trade[index].get("tradedPrice") 
                        nettradelist[j]['ltt'] =  trade[index].get("exchangeTime")    
                        nettradelist[j]['val'] = nettradelist[j]['val'] - (trade[index].get("tradedQuantity") * trade[index].get("tradedPrice"))
                        contract_in_list = True
                        break
                    else:
                        j = j + 1
                if(contract_in_list == False):     
                    
                    nettradelist[j] = {'contract':trade[index].get("customSymbol"),'tradeqty':0 - trade[index].get("tradedQuantity"),'ltp':trade[index].get("tradedPrice"),'ltt':trade[index].get("exchangeTime"),'val':0 - (trade[index].get("tradedQuantity") * trade[index].get("tradedPrice"))}
                                
            index = index + 1 
        
        index = 0
        pagecount = 0     
      
        length = len(nettradelist)  
        # st.write(nettradelist)
        while(index < length): 
            
            if(nettradelist[index]['tradeqty'] != 0):                              
                
                current_date = start_date - datetime.timedelta(days=1) 
                prev_end_date = start_date - datetime.timedelta(days=10)  
                
                while current_date >= prev_end_date:    
                    
                    prev_data = dhan.get_trade_history(current_date.strftime("%Y-%m-%d"),current_date.strftime("%Y-%m-%d"),page_number=pagecount).get("data")
                
                    if(not prev_data):
                        pagecount = 0
                        current_date = current_date - datetime.timedelta(days=1)                              
                    else:
                        for item in prev_data:                         
                            if (nettradelist[index].get("contract") == item.get("customSymbol")) and (abs(nettradelist[index].get("tradeqty")) == item.get("tradedQuantity")):
                                if nettradelist[index].get("tradeqty") < 0 and "BUY" in item["transactionType"]:
                                    open_realised_pnl = open_realised_pnl + 0 - (item.get("tradedPrice")*item.get("tradedQuantity"))
                                    nettradelist[index]['tradeqty'] = 0
                                    # st.write("buyopen" + open_realised_pnl)
                                    break
                                if nettradelist[index].get("tradeqty") > 0 and "SELL" in item["transactionType"]:
                                    open_realised_pnl = open_realised_pnl + item.get("tradedPrice")*item.get("tradedQuantity")
                                    nettradelist[index]['tradeqty'] = 0
                                    # st.write("sellopen" + open_realised_pnl) 
                                    break
                    pagecount = pagecount + 1
            else:
                del nettradelist[index]
            index = index + 1     
         
        for item in nettradelist:
                        
            if("BANKNIFTY" not in nettradelist[item].get("contract") and "FINNIFTY" not in nettradelist[item].get("contract") and "NIFTY" in nettradelist[item].get("contract")):
                                  
                    match = re.search(r"NIFTY (\d{2}) (\w{3}) (\d{5})", nettradelist[item].get("contract"))                     
                    
                    expiry_date = datetime.datetime(parser.parse(nettradelist[item]["ltt"]).year,month_dict.get(match.group(2).upper()),int(match.group(1)))                                     
                                    
                    if expiry_date.date() > end_date :                  
                        
                        open_unrealised_pnl =  open_unrealised_pnl + (0 - nettradelist[item]['tradeqty'] * nettradelist[item]['ltp'])
            
            if "SILVER" in nettradelist[item].get("contract") and "SILVERM" not in nettradelist[item].get("contract") : 
                
                if("FUT" in nettradelist[item].get("contract")):
                    match = re.search(r"SILVER (\w{3}) (\w{3})", nettradelist[item].get("contract"))  
                    if(month_dict.get(match.group(1)) > end_date.month):
                        open_unrealised_pnl =  open_unrealised_pnl + nettradelist[item]['tradeqty'] * nettradelist[item]['ltp']
                else:
                    match = re.search(r"SILVER (\d{2}) (\w{3})", nettradelist[item].get("contract"))  
                    if(month_dict.get(match.group(2)) > end_date.month):
                        open_unrealised_pnl =  open_unrealised_pnl + nettradelist[item]['tradeqty'] * nettradelist[item]['ltp']
                              
            if "SILVERM" in nettradelist[item].get("contract"): 

                if("FUT" in nettradelist[item].get("contract")):
                    match = re.search(r"SILVERM (\w{3}) (\w{3})", nettradelist[item].get("contract"))  
                    if(month_dict.get(match.group(1)) > end_date.month):
                        open_unrealised_pnl =  open_unrealised_pnl + nettradelist[item]['tradeqty'] * nettradelist[item]['ltp']
                else:
                    match = re.search(r"SILVERM (\d{2}) (\w{3})", nettradelist[item].get("contract"))  
                    if(month_dict.get(match.group(2)) > end_date.month):
                        open_unrealised_pnl =  open_unrealised_pnl + nettradelist[item]['tradeqty'] * nettradelist[item]['ltp']    
               
        # st.write(open_realised_pnl + open_unrealised_pnl)
        
        return(open_realised_pnl + open_unrealised_pnl)

    def mtsm_pnl():
        mtsm_starttime = datetime.time(9, 16, 0)
        mtsm_endtime = datetime.time(9, 45, 0)
        dts_starttime = datetime.time(9, 45, 0)
        dts_endtime = datetime.time(15, 22, 0)
        
        mtsm_netbuy =  mtsm_netsell =  mtsm_charges = mtsm_brokerage = mtsm_numtrades = mtsm_netqty = 0
        nts_nifty_netbuy =  nts_nifty_netsell =  nts_nifty_charges = nts_nifty_brokerage = nts_nifty_numtrades = nts_nifty_netqty = 0
        os_bankex_netbuy = os_bankex_netsell = os_bankex_charges = os_bankex_brokerage = os_bankex_numtrades = os_bankex_netqty = os_bankex_buytrades = 0
        os_sensex_netbuy = os_sensex_netsell = os_sensex_charges = os_sensex_brokerage = os_sensex_numtrades = os_sensex_netqty = os_sensex_buytrades = 0
        os_banknifty_netbuy = os_banknifty_netsell = os_banknifty_charges = os_banknifty_brokerage = os_banknifty_numtrades = os_banknifty_netqty = os_banknifty_buytrades = 0
        os_finnifty_netbuy = os_finnifty_netsell = os_finnifty_charges = os_finnifty_brokerage = os_finnifty_numtrades = os_finnifty_netqty = os_finnifty_buytrades = 0
        os_nifty_netbuy = os_nifty_netsell = os_nifty_charges = os_nifty_brokerage = os_nifty_numtrades = os_nifty_netqty = os_nifty_buytrades = 0
        dts_nifty_netbuy = dts_nifty_netsell = dts_nifty_charges = dts_nifty_brokerage = dts_nifty_numtrades = dts_nifty_netqty = 0
        dts_banknifty_netbuy = dts_banknifty_netsell = dts_banknifty_charges = dts_banknifty_brokerage = dts_banknifty_numtrades = dts_banknifty_netqty = 0
        dts_finnifty_netbuy = dts_finnifty_netsell = dts_finnifty_charges = dts_finnifty_brokerage = dts_finnifty_numtrades = dts_finnifty_netqty = 0
        cts_silverfut_netbuy = cts_silverfut_netsell = cts_silverfut_charges = cts_silverfut_brokerage = cts_silverfut_numtrades = cts_silverfut_netqty = 0 
        os_silver_netbuy = os_silver_netsell = os_silver_charges = os_silver_brokerage = os_silver_numtrades = os_silver_netqty = os_silver_buytrades = 0 
        
        mtsm_Grosspnl = mtsm_Chg = mtsm_netpnl = 0
        nts_nifty_Grosspnl = nts_nifty_Chg = nts_nifty_netpnl = 0
        os_bankex_Grosspnl = os_bankex_Chg = os_bankex_netpnl = 0
        os_sensex_Grosspnl = os_sensex_Chg = os_sensex_netpnl = 0
        os_banknifty_Grosspnl = os_banknifty_Chg = os_banknifty_netpnl = 0
        os_finnifty_Grosspnl = os_finnifty_Chg = os_finnifty_netpnl = 0
        dts_nifty_Grosspnl = dts_nifty_Chg = dts_nifty_netpnl = 0
        dts_banknifty_Grosspnl = dts_banknifty_Chg = dts_banknifty_netpnl = 0
        dts_finnifty_Grosspnl = dts_finnifty_Chg = dts_finnifty_netpnl = 0
        cts_silverfut_Grosspnl = cts_silverfut_Chg = cts_silverfut_netpnl = 0
        os_silver_Grosspnl = os_silver_Chg = os_silver_netpnl = 0

        overnight_silver_fut_pos = dict()
        overnight_silver_fut_qty = 0
        overnight_silver_intrafut_pos = dict()
        silver_intra_count = 0 
        overnight_silver_opt_pos = dict()
        silver_opt_count = 0
        silver_margin_count = 0 
        overnight_nts_pos = dict()                 
        nifty_nts_count= 0
        
        pagecount = 0
        current_date = start_date
        
        # Create an empty dictionary to store data
        data_dict = {}

        # Create a placeholder for the dataframe
        dataframe_placeholder = st.empty()        
        nt = 0
        fg = False
        while current_date <= end_date:
                       
            data = dhan.get_trade_history(current_date.strftime("%Y-%m-%d"),current_date.strftime("%Y-%m-%d"),page_number=pagecount).get("data")            
            
            if(not data):
                pagecount = 0
                current_date = current_date + datetime.timedelta(days=1)                              
            else:
                for item in data: 
                   
                    nt = nt + 1 
                                    
                    # for key, value in item.items():
                    #     if key not in data_dict:
                    #         data_dict[key] = []  # Create a new list for the column
                    #     data_dict[key].append(value) 
                    # df = pd.DataFrame(data_dict)                    
                    # dataframe_placeholder.dataframe(df)
                    
                    if "BANKNIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if mtsm_endtime >= d >= mtsm_starttime:                             
                            if "BUY" in item["transactionType"]: 
                                mtsm_netbuy = mtsm_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                mtsm_netsell = mtsm_netsell +  item["tradedPrice"] * item["tradedQuantity"]                                
                            mtsm_netqty = mtsm_netqty + item["tradedQuantity"]
                            mtsm_brokerage = mtsm_brokerage + float(item["brokerageCharges"])
                            mtsm_numtrades = mtsm_numtrades + 1
                            mtsm_charges = mtsm_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True
                    if "BANKNIFTY" not in item["customSymbol"] and "FINNIFTY" not in item["customSymbol"] and "NIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()                        
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_nifty_netbuy = dts_nifty_netbuy + item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                dts_nifty_netsell = dts_nifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            dts_nifty_netqty = dts_nifty_netqty + item["tradedQuantity"]
                            dts_nifty_brokerage = dts_nifty_brokerage + float(item["brokerageCharges"])
                            dts_nifty_numtrades = dts_nifty_numtrades + 1
                            dts_nifty_charges = dts_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True
                    if "BANKNIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_banknifty_netbuy = dts_banknifty_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                dts_banknifty_netsell = dts_banknifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            dts_banknifty_netqty = dts_banknifty_netqty + item["tradedQuantity"]
                            dts_banknifty_brokerage = dts_banknifty_brokerage + float(item["brokerageCharges"])
                            dts_banknifty_numtrades = dts_banknifty_numtrades + 1
                            dts_banknifty_charges = dts_banknifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True
                    if "FINNIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_finnifty_netbuy = dts_finnifty_netbuy + item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                dts_finnifty_netsell = dts_finnifty_netsell + item["tradedPrice"] * item["tradedQuantity"]
                            dts_finnifty_netqty = dts_finnifty_netqty + item["tradedQuantity"]
                            dts_finnifty_brokerage = dts_finnifty_brokerage + float(item["brokerageCharges"])
                            dts_finnifty_numtrades = dts_finnifty_numtrades + 1
                            dts_finnifty_charges = dts_finnifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True
                    if "BANKEX" in item["customSymbol"] :
                        if "BUY" in item["transactionType"]: 
                            os_bankex_netbuy = os_bankex_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            os_bankex_buytrades =  os_bankex_buytrades + 1
                        if "SELL" in item["transactionType"]:
                            os_bankex_netsell = os_bankex_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            os_bankex_numtrades =  os_bankex_numtrades + 1
                            os_bankex_netqty = os_bankex_netqty + item["tradedQuantity"]
                        os_bankex_brokerage = os_bankex_brokerage + float(item["brokerageCharges"])                        
                        os_bankex_charges = os_bankex_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        fg = True
                    if "FINNIFTY" in item["customSymbol"] and "MARGIN" in item["productType"]:
                        if "BUY" in item["transactionType"]: 
                            os_finnifty_netbuy = os_finnifty_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            os_finnifty_buytrades = os_finnifty_buytrades + 1
                        if "SELL" in item["transactionType"]:
                            os_finnifty_netsell = os_finnifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            os_finnifty_netqty = os_finnifty_netqty + item["tradedQuantity"]
                            os_finnifty_numtrades =  os_finnifty_numtrades + 1
                        os_finnifty_brokerage = os_finnifty_brokerage + float(item["brokerageCharges"])                        
                        os_finnifty_charges = os_finnifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        fg = True
                    if "SENSEX" in item["customSymbol"] :
                        if "BUY" in item["transactionType"]: 
                            os_sensex_netbuy = os_sensex_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            os_sensex_buytrades = os_sensex_buytrades + 1
                        if "SELL" in item["transactionType"]:
                            os_sensex_netsell = os_sensex_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            os_sensex_netqty = os_sensex_netqty + item["tradedQuantity"]
                            os_sensex_numtrades = os_sensex_numtrades + 1
                        os_sensex_brokerage = os_sensex_brokerage + float(item["brokerageCharges"])                        
                        os_sensex_charges = os_sensex_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        fg = True
                    if "BANKNIFTY" in item["customSymbol"] and "MARGIN" in item["productType"] :
                        if "BUY" in item["transactionType"]: 
                            os_banknifty_netbuy = os_banknifty_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            os_banknifty_buytrades = os_banknifty_buytrades + 1
                        if "SELL" in item["transactionType"]:
                            os_banknifty_netsell = os_banknifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                            os_banknifty_netqty = os_banknifty_netqty + item["tradedQuantity"]
                            os_banknifty_numtrades = os_banknifty_numtrades + 1
                        os_banknifty_brokerage = os_banknifty_brokerage + float(item["brokerageCharges"])                        
                        os_banknifty_charges = os_banknifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        fg = True
                    if "BANKNIFTY" not in item["customSymbol"] and "FINNIFTY" not in item["customSymbol"] and "NIFTY" in item["customSymbol"] and "MARGIN" in item["productType"] :
                        strike = int(item["customSymbol"].split()[3])                        
                        if (strike % 50 == 0 and strike % 100 != 0) :
                            if "BUY" in item["transactionType"]: 
                                os_nifty_netbuy = os_nifty_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                                os_nifty_buytrades = os_nifty_buytrades + 1
                            if "SELL" in item["transactionType"]:
                                os_nifty_netsell = os_nifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                                os_nifty_netqty = os_nifty_netqty + item["tradedQuantity"]
                                os_nifty_numtrades = os_nifty_numtrades + 1
                            os_nifty_brokerage = os_nifty_brokerage + float(item["brokerageCharges"])                            
                            os_nifty_charges = os_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True  
                        else:
                            if "BUY" in item["transactionType"]: 
                                nts_nifty_netbuy =  nts_nifty_netbuy + item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                nts_nifty_netsell =  nts_nifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                                nts_nifty_netqty = nts_nifty_netqty + item["tradedQuantity"]
                            nts_nifty_numtrades = nts_nifty_numtrades + 1
                            overnight_nts_pos[nifty_nts_count] = item                    
                            nifty_nts_count= nifty_nts_count + 1                            
                            
                            nts_nifty_brokerage = nts_nifty_brokerage + float(item["brokerageCharges"])                            
                            nts_nifty_charges = nts_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                            fg = True                 
                    if "SILVER" in item["customSymbol"] and "FUTCOM" in item["instrument"]:                        
                        
                        if "INTRADAY" in item["productType"] :                           
                            if "BUY" in item["transactionType"]:                                
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:                                
                                cts_silverfut_netsell = cts_silverfut_netsell +  item["tradedPrice"] * item["tradedQuantity"] 
                            overnight_silver_intrafut_pos[silver_intra_count] = item 
                            silver_intra_count = silver_intra_count + 1
                            fg = True                         
                        if "MARGIN" in item["productType"] :
                            if "BUY" in item["transactionType"]: 
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                cts_silverfut_netsell = cts_silverfut_netsell +  item["tradedPrice"] * item["tradedQuantity"]           
                            overnight_silver_fut_pos[silver_margin_count] = item 
                            silver_margin_count = silver_margin_count + 1
                            fg = True
                        cts_silverfut_netqty = cts_silverfut_netqty + item["tradedQuantity"]
                        cts_silverfut_brokerage = cts_silverfut_brokerage + float(item["brokerageCharges"])
                        cts_silverfut_numtrades = cts_silverfut_numtrades + 1
                        cts_silverfut_charges = cts_silverfut_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        
                    if "SILVER" in item["customSymbol"] and "OPTFUT" in item["instrument"]:                       
                        if "BUY" in item["transactionType"]: 
                            os_silver_netbuy = os_silver_netbuy +  item["tradedPrice"] * item["tradedQuantity"]                                             
                            os_silver_buytrades = os_silver_buytrades + 1
                        if "SELL" in item["transactionType"]:
                            os_silver_netsell = os_silver_netsell +  item["tradedPrice"] * item["tradedQuantity"]   
                            os_silver_numtrades = os_silver_numtrades + 1  
                            os_silver_netqty = os_silver_netqty + item["tradedQuantity"]                          
                        overnight_silver_opt_pos[silver_opt_count] = item                  
                        silver_opt_count = silver_opt_count + 1
                        os_silver_brokerage = os_silver_brokerage + float(item["brokerageCharges"])                        
                        os_silver_charges = os_silver_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                        fg = True
                    if(fg==False):
                        if "BANKNIFTY" not in item["customSymbol"] and "FINNIFTY" not in item["customSymbol"] and "NIFTY" in item["customSymbol"]:
                            nts_nifty_numtrades = nts_nifty_numtrades + 1
                            overnight_nts_pos[nifty_nts_count] = item                    
                            nifty_nts_count= nifty_nts_count + 1
                        if "SILVER" in item["customSymbol"] and "FUTCOM" in item["instrument"]:   
                            if "INTRADAY" in item["productType"] :
                                overnight_silver_intrafut_pos[silver_intra_count] = item 
                                silver_intra_count = silver_intra_count + 1   
                            if "MARGIN" in item["productType"] :
                                overnight_silver_fut_pos[silver_margin_count] = item 
                                silver_margin_count = silver_margin_count + 1
                            cts_silverfut_numtrades = cts_silverfut_numtrades + 1
                        if "SILVER" in item["customSymbol"] and "OPTFUT" in item["instrument"]:
                            overnight_silver_opt_pos[silver_opt_count] = item                  
                            silver_opt_count = silver_opt_count + 1          
                       
                    fg = False                
                pagecount = pagecount + 1            
        
        mtsm_Grosspnl = round((mtsm_netsell - mtsm_netbuy),2)
        mtsm_Chg = round(mtsm_charges,2)
        mtsm_netpnl = round(mtsm_Grosspnl - mtsm_Chg,2)

        nts_nifty_Grosspnl = round(nts_nifty_netsell - nts_nifty_netbuy + get_open_trades(overnight_nts_pos),2)
        nts_nifty_Chg = round(nts_nifty_charges,2)
        nts_nifty_netpnl = round(nts_nifty_Grosspnl - nts_nifty_Chg,2)
        
        os_bankex_Grosspnl = round((os_bankex_netsell - os_bankex_netbuy),2)
        os_bankex_Chg = round(os_bankex_charges,2)
        os_bankex_netpnl = round(os_bankex_Grosspnl - os_bankex_Chg,2)
        
        os_finnifty_Grosspnl = round((os_finnifty_netsell - os_finnifty_netbuy),2)
        os_finnifty_Chg = round(os_finnifty_charges,2)
        os_finnifty_netpnl = round(os_finnifty_Grosspnl - os_finnifty_Chg,2)
        
        os_sensex_Grosspnl = round((os_sensex_netsell - os_sensex_netbuy),2)
        os_sensex_Chg = round(os_sensex_charges,2)
        os_sensex_netpnl = round(os_sensex_Grosspnl - os_sensex_Chg,2)
        
        os_banknifty_Grosspnl = round((os_banknifty_netsell - os_banknifty_netbuy),2)
        os_banknifty_Chg = round(os_banknifty_charges,2)
        os_banknifty_netpnl = round(os_banknifty_Grosspnl - os_banknifty_Chg,2)
        
        os_nifty_Grosspnl = round((os_nifty_netsell - os_nifty_netbuy),2)
        os_nifty_Chg = round(os_nifty_charges,2)
        os_nifty_netpnl = round(os_nifty_Grosspnl - os_nifty_Chg,2)
       
        dts_nifty_Grosspnl = round((dts_nifty_netsell - dts_nifty_netbuy),2)
        dts_nifty_Chg = round(dts_nifty_charges,2)
        dts_nifty_netpnl = round(dts_nifty_Grosspnl - dts_nifty_Chg,2)
        
        dts_finnifty_Grosspnl = round((dts_finnifty_netsell - dts_finnifty_netbuy),2)
        dts_finnifty_Chg = round(dts_finnifty_charges,2)
        dts_finnifty_netpnl = round(dts_finnifty_Grosspnl - dts_finnifty_Chg,2)
        
        dts_banknifty_Grosspnl = round((dts_banknifty_netsell - dts_banknifty_netbuy),2)
        dts_banknifty_Chg = round(dts_banknifty_charges,2)
        dts_banknifty_netpnl = round(dts_banknifty_Grosspnl - dts_banknifty_Chg,2)
        
        cts_silverfut_Grosspnl = round((cts_silverfut_netsell - cts_silverfut_netbuy + get_open_trades(overnight_silver_fut_pos) + get_open_trades(overnight_silver_intrafut_pos)),2)
        cts_silverfut_Chg = round(cts_silverfut_charges,2)
        cts_silverfut_netpnl = round(cts_silverfut_Grosspnl - cts_silverfut_Chg,2)        
        
        os_silver_Grosspnl = round((os_silver_netsell - os_silver_netbuy + get_open_trades(overnight_silver_opt_pos)),2)
        os_silver_Chg = round(os_silver_charges,2)
        os_silver_netpnl = round(os_silver_Grosspnl - os_silver_Chg,2)
       
        output = dict()
        output["mtsm_grosspnl"] = mtsm_Grosspnl
        output["mtsm_charges"] =  mtsm_Chg 
        output["mtsm_netpnl"] =  mtsm_netpnl
        output["mtsm_netpnl%"] = round(w_div(mtsm_netpnl,capital)*100,4)        
        output["mtsm_brokerage"] = mtsm_brokerage
        output["mtsm_numtrades"] = mtsm_numtrades
        output["mtsm_netqty"] = mtsm_netqty        
        
        output["nts_nifty_grosspnl"] = nts_nifty_Grosspnl
        output["nts_nifty_charges"] =  nts_nifty_Chg 
        output["nts_nifty_netpnl"] =  nts_nifty_netpnl        
        output["nts_nifty_netpnl%"] = round(w_div(nts_nifty_netpnl,capital)*100,4)                            
        output["nts_nifty_brokerage"] = nts_nifty_brokerage
        output["nts_nifty_numtrades"] = nts_nifty_numtrades
        output["nts_nifty_netqty"] = nts_nifty_netqty
        
        output["os_bankex_grosspnl"] = os_bankex_Grosspnl
        output["os_bankex_charges"] =  os_bankex_Chg 
        output["os_bankex_netpnl"] = os_bankex_netpnl       
        output["os_bankex_netpnl%"] = round(w_div(os_bankex_netpnl,capital)*100,4)                 
        output["os_bankex_brokerage"] = os_bankex_brokerage
        output["os_bankex_numtrades"] = os_bankex_numtrades
        output["os_bankex_netqty"] = os_bankex_netqty
        output["os_bankex_buytrades"] = os_bankex_buytrades
        
        output["os_finnifty_grosspnl"] = os_finnifty_Grosspnl
        output["os_finnifty_charges"] =  os_finnifty_Chg 
        output["os_finnifty_netpnl"] = os_finnifty_netpnl
        output["os_finnifty_netpnl%"] = round(w_div(os_finnifty_netpnl,capital)*100,4)                        
        output["os_finnifty_brokerage"] = os_finnifty_brokerage
        output["os_finnifty_numtrades"] = os_finnifty_numtrades
        output["os_finnifty_netqty"] = os_finnifty_netqty
        output["os_finnifty_buytrades"] = os_finnifty_buytrades
        
        output["os_sensex_grosspnl"] = os_sensex_Grosspnl
        output["os_sensex_charges"] =  os_sensex_Chg 
        output["os_sensex_netpnl"] = os_sensex_netpnl        
        output["os_sensex_netpnl%"] = round(w_div(os_sensex_netpnl,capital)*100,4)              
        output["os_sensex_brokerage"] = os_sensex_brokerage
        output["os_sensex_numtrades"] = os_sensex_numtrades 
        output["os_sensex_netqty"] = os_sensex_netqty
        output["os_sensex_buytrades"] = os_sensex_buytrades
        
        output["os_banknifty_grosspnl"] = os_banknifty_Grosspnl
        output["os_banknifty_charges"] =  os_banknifty_Chg 
        output["os_banknifty_netpnl"] = os_banknifty_netpnl
        output["os_banknifty_netpnl%"] = round(w_div(os_banknifty_netpnl,capital)*100,4)             
        output["os_banknifty_brokerage"] = os_banknifty_brokerage
        output["os_banknifty_numtrades"] = os_banknifty_numtrades 
        output["os_banknifty_netqty"] = os_banknifty_netqty
        output["os_banknifty_buytrades"] = os_banknifty_buytrades
        
        output["os_nifty_grosspnl"] = os_nifty_Grosspnl
        output["os_nifty_charges"] =  os_nifty_Chg 
        output["os_nifty_netpnl"] = os_nifty_netpnl
        output["os_nifty_netpnl%"] = round(w_div(os_nifty_netpnl,capital)*100,4)               
        output["os_nifty_brokerage"] = os_nifty_brokerage
        output["os_nifty_numtrades"] = os_nifty_numtrades 
        output["os_nifty_netqty"] = os_nifty_netqty
        output["os_nifty_buytrades"] = os_nifty_buytrades
        
        output["dts_nifty_grosspnl"] = dts_nifty_Grosspnl
        output["dts_nifty_charges"] =  dts_nifty_Chg 
        output["dts_nifty_netpnl"] = dts_nifty_netpnl
        output["dts_nifty_netpnl%"] = round(w_div(dts_nifty_netpnl,capital)*100,4)        
        output["dts_nifty_brokerage"] = dts_nifty_brokerage
        output["dts_nifty_numtrades"] = dts_nifty_numtrades  
        output["dts_nifty_netqty"] = dts_nifty_netqty
       
        output["dts_banknifty_grosspnl"] = dts_banknifty_Grosspnl
        output["dts_banknifty_charges"] = dts_banknifty_Chg
        output["dts_banknifty_netpnl"] = dts_banknifty_netpnl 
        output["dts_banknifty_netpnl%"] = round(w_div(dts_banknifty_netpnl,capital)*100,4)        
        output["dts_banknifty_brokerage"] = dts_banknifty_brokerage
        output["dts_banknifty_numtrades"] = dts_banknifty_numtrades  
        output["dts_banknifty_netqty"] = dts_banknifty_netqty
        
        output["dts_finnifty_grosspnl"] = dts_finnifty_Grosspnl
        output["dts_finnifty_charges"] =  dts_finnifty_Chg 
        output["dts_finnifty_netpnl"] = dts_finnifty_netpnl         
        output["dts_finnifty_netpnl%"] = round(w_div(dts_finnifty_netpnl,capital)*100,4)            
        output["dts_finnifty_brokerage"] = dts_finnifty_brokerage
        output["dts_finnifty_numtrades"] = dts_finnifty_numtrades 
        output["dts_finnifty_netqty"] = dts_finnifty_netqty
        
        output["cts_silverfut_grosspnl"] = cts_silverfut_Grosspnl
        output["cts_silverfut_charges"] =  cts_silverfut_Chg
        output["cts_silverfut_netpnl"] = cts_silverfut_netpnl 
        output["cts_silverfut_netpnl%"] = round(w_div(cts_silverfut_netpnl,capital)*100,4)             
        output["cts_silverfut_brokerage"] = cts_silverfut_brokerage
        output["cts_silverfut_numtrades"] = cts_silverfut_numtrades
        output["cts_silverfut_netqty"] = cts_silverfut_netqty
        
        output["os_silver_grosspnl"] = os_silver_Grosspnl
        output["os_silver_charges"] =  os_silver_Chg 
        output["os_silver_netpnl"] = os_silver_netpnl
        output["os_silver_netpnl%"] = round(w_div(os_silver_netpnl,capital)*100,4)                
        output["os_silver_brokerage"] = os_silver_brokerage
        output["os_silver_numtrades"] = os_silver_numtrades 
        output["os_silver_netqty"] = os_silver_netqty 
        output["os_silver_buytrades"] = os_silver_buytrades             
        # st.write(nt)
        return(output)       
    
    def plot_title(title, size, color):
        if size == 1:
            st.markdown("<h1 style='text-align: center; color:"+ color +";'>"+title+"</h1>", unsafe_allow_html=True)
        if size == 2:
            st.markdown("<h2 style='text-align: center; color:"+ color +";'>"+title+"</h1>", unsafe_allow_html=True)
        if size == 3:
            st.markdown("<h3 style='text-align: center; color:"+ color +";'>"+title+"</h1>", unsafe_allow_html=True)
    
    def pnl_row(val):
        if(val >= 0) :
            st.write(":green[" + str(round(val,2))+"]") 
        else :
            st.write(":red[" + str(round(val,2))+"]")
    
    def pnl_block(title,name1,name2,name3,name4,name5,name6,l1,l2,l3,l4,l5,l6,t1,t2,t3,t4,t5,t6,gp1,gp2,gp3,gp4,gp5,gp6,chg1,chg2,chg3,chg4,chg5,chg6,np1,np2,np3,np4,np5,np6,npp1,npp2,npp3,npp4,npp5,npp6):
        if title:
            
            plot_title(title, size = 3, color = "#1D9AE2")
                        
            with st.container(border=True):        
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                with col1:
                    st.markdown("<b>Index</b>", unsafe_allow_html=True)                    
                    if name1 != "NA": 
                        st.write(":blue["+name1+"]")
                    if name2 != "NA": 
                        st.write(":blue["+name2+"]")
                    if name3 != "NA": 
                        st.write(":blue["+name3+"]")
                    if name4 != "NA": 
                        st.write(":blue["+name4+"]")
                    if name5 != "NA": 
                        st.write(":blue["+name5+"]")
                    if name6 != "NA": 
                        st.write(":blue["+name6+"]")                  
                    st.header("",divider="rainbow")
                    st.write(":black[Total]")

                with col2:
                    sum = 0                    
                    st.markdown("<b>Avg Qty</b>", unsafe_allow_html=True)
                    if 11 !="NA":
                        st.write(":blue[" + str(l1)+"]")
                        sum = sum + l1
                    if l2 !="NA":
                        st.write(":blue[" + str(l2)+"]")
                        sum = sum + l2
                    if l3 !="NA":
                        st.write(":blue[" + str(l3)+"]")
                        sum = sum + l3
                    if l4 !="NA": 
                        st.write(":blue[" + str(l4)+"]")
                        sum = sum + l4 
                    if l5 !="NA": 
                        st.write(":blue[" + str(l5)+"]")
                        sum = sum + l5   
                    if l6 !="NA": 
                        st.write(":blue[" + str(l6)+"]")
                        sum = sum + l6
                    st.header("",divider="rainbow") 
                    st.write(":black[" + str(sum) +"]")     
                with col3:
                    sum = 0
                    st.markdown("<b>Trades</b>", unsafe_allow_html=True)                    
                    if t1 !="NA":
                        st.write(":blue[" + str(t1)+"]")
                        sum = sum + t1
                    if t2 !="NA":
                        st.write(":blue[" + str(t2)+"]")
                        sum = sum + t2
                    if t3 !="NA":
                        st.write(":blue[" + str(t3)+"]")
                        sum = sum + t3
                    if t4 !="NA": 
                        st.write(":blue[" + str(t4)+"]") 
                        sum = sum + t4
                    if t5 !="NA": 
                        st.write(":blue[" + str(t5)+"]") 
                        sum = sum + t5  
                    if t6 !="NA": 
                        st.write(":blue[" + str(t6)+"]") 
                        sum = sum + t6
                    st.header("",divider="rainbow")
                    st.write(":black[" + str(sum) +"]")            
                with col4:                    
                    sum = 0
                    st.markdown("<b>Gross Profit</b>", unsafe_allow_html=True)                    
                    if gp1 !="NA":
                        pnl_row(gp1)
                        sum = sum + gp1
                    if gp2 !="NA":
                        pnl_row(gp2)
                        sum = sum + gp2
                    if gp3 !="NA":
                        pnl_row(gp3)
                        sum = sum + gp3                    
                    if gp4 !="NA": 
                        pnl_row(gp4)
                        sum = sum + gp4 
                    if gp5 !="NA": 
                        pnl_row(gp5)
                        sum = sum + gp5   
                    if gp6 !="NA": 
                        pnl_row(gp6)
                        sum = sum + gp6
                    st.header("",divider="rainbow")
                    pnl_row(sum)             
                with col5:
                    sum = 0
                    st.markdown("<b>Charges</b>", unsafe_allow_html=True)                    
                    if chg1 !="NA":
                        st.write(":red[" + str(chg1)+"]")
                        sum = sum + chg1
                    if chg2 !="NA":
                        st.write(":red[" + str(chg2)+"]")
                        sum = sum + chg2
                    if chg3 !="NA":
                        st.write(":red[" + str(chg3)+"]")
                        sum = sum + chg3
                    if chg4 !="NA": 
                        st.write(":red[" + str(chg4)+"]") 
                        sum = sum + chg4
                    if chg5 !="NA": 
                        st.write(":red[" + str(chg5)+"]") 
                        sum = sum + chg5  
                    if chg6 !="NA": 
                        st.write(":red[" + str(chg6)+"]") 
                        sum = sum + chg6
                    st.header("",divider="rainbow")
                    st.write(":red[" + str(round(sum,2))+"]")                         
                   
                with col6:
                    sum = 0
                    st.markdown("<b>Net Profit</b>", unsafe_allow_html=True)                       
                    if np1 !="NA":
                        pnl_row(np1)
                        sum = sum + np1
                    if np2 !="NA":
                        pnl_row(np2)
                        sum = sum + np2
                    if np3 !="NA":
                        pnl_row(np3)
                        sum = sum + np3
                    if np4 !="NA": 
                        pnl_row(np4)
                        sum = sum + np4
                    if np5 !="NA": 
                        pnl_row(np5)
                        sum = sum + np5  
                    if np6 !="NA": 
                        pnl_row(np6)
                        sum = sum + np6
                    st.header("",divider="rainbow")
                    pnl_row(sum)                   
                with col7:
                    sum = 0
                    st.markdown("<b>Net Profit %</b>", unsafe_allow_html=True)                       
                    if npp1 !="NA":
                        pnl_row(npp1)
                        sum = sum + npp1
                    if npp2 !="NA":
                        pnl_row(npp2)
                        sum = sum + npp2
                    if npp3 !="NA":
                        pnl_row(npp3)
                        sum = sum + npp3
                    if npp4 !="NA": 
                        pnl_row(npp4) 
                        sum = sum + npp4
                    if npp5 !="NA": 
                        pnl_row(npp5) 
                        sum = sum + npp5  
                    if npp6 !="NA": 
                        pnl_row(npp6)
                        sum = sum + npp6
                    st.header("",divider="rainbow")
                    pnl_row(sum)                       
            
    def click_button():

        data = mtsm_pnl()         
        
        tot_trades = data["nts_nifty_numtrades"] + data["os_banknifty_numtrades"] + data["os_banknifty_buytrades"] + data["os_bankex_numtrades"] +  data["os_bankex_buytrades"] + data["os_sensex_numtrades"] +  data["os_sensex_buytrades"] + data["os_finnifty_numtrades"] + data["os_finnifty_buytrades"] + data["mtsm_numtrades"] + data["os_nifty_numtrades"] + data["os_nifty_buytrades"] + data["dts_nifty_numtrades"] + data["dts_banknifty_numtrades"] + data["dts_finnifty_numtrades"] + data["cts_silverfut_numtrades"] + data["os_silver_numtrades"] + data["os_silver_buytrades"]
        gross_pnl = data["mtsm_grosspnl"] + data["nts_nifty_grosspnl"] + data["os_bankex_grosspnl"] + data["os_finnifty_grosspnl"]+ data["os_banknifty_grosspnl"]+ data["os_sensex_grosspnl"] + data["os_nifty_grosspnl"] + data["dts_nifty_grosspnl"] + data["dts_banknifty_grosspnl"] + data["dts_finnifty_grosspnl"] + data["cts_silverfut_grosspnl"] + data["os_silver_grosspnl"]
        gross_pnl = data["mtsm_grosspnl"] + data["nts_nifty_grosspnl"] + data["os_bankex_grosspnl"] + data["os_finnifty_grosspnl"]+ data["os_banknifty_grosspnl"]+ data["os_sensex_grosspnl"] + data["os_nifty_grosspnl"] + data["dts_nifty_grosspnl"] + data["dts_banknifty_grosspnl"] + data["dts_finnifty_grosspnl"] + data["cts_silverfut_grosspnl"] + data["os_silver_grosspnl"]
        brokerage = data["mtsm_brokerage"] + data["nts_nifty_brokerage"] + data["os_bankex_brokerage"] + data["os_finnifty_brokerage"] + data["os_banknifty_brokerage"] + data["os_nifty_brokerage"] + data["os_sensex_brokerage"] + data["dts_nifty_brokerage"] + data["dts_banknifty_brokerage"] + data["dts_finnifty_brokerage"] + data["cts_silverfut_brokerage"] + data["os_silver_brokerage"]
        charges = data["mtsm_charges"] + data["nts_nifty_charges"] + data["os_bankex_charges"] + data["os_finnifty_charges"] + data["os_banknifty_charges"] + data["os_nifty_charges"] + data["os_sensex_charges"] + data["dts_nifty_charges"] + data["dts_banknifty_charges"] + data["dts_finnifty_charges"] + data["cts_silverfut_charges"] + data["os_silver_charges"]
        net_pnl = data["mtsm_netpnl"] + data["nts_nifty_netpnl"] + data["os_bankex_netpnl"] + data["os_finnifty_netpnl"]+ data["os_banknifty_netpnl"]+ data["os_sensex_netpnl"] + data["os_nifty_netpnl"] + data["dts_nifty_netpnl"] + data["dts_banknifty_netpnl"] + data["dts_finnifty_netpnl"] + data["cts_silverfut_netpnl"] + data["os_silver_netpnl"]
        charges_less_brokerage = round(charges - brokerage,2)
        
        plot_title("PnL Report - " + str(start_date) + " to " + str(end_date) + "",size = 2, color = "#1D9AE2")
        
        plot_title("Total",size = 2, color = "#1D9AE2")

        with st.container(border=True):        
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.markdown("<b>Total Trades</b>", unsafe_allow_html=True)                
                st.write(":blue[" + str(tot_trades)+"]")
            with col2:
                st.markdown("<b>Gross Profit</b>", unsafe_allow_html=True)
                pnl_row(round(gross_pnl,2))
            with col3:
                st.markdown("<b>Charges</b>", unsafe_allow_html=True)
                st.write(":red[" + str(charges_less_brokerage)+"]")
            with col4:
                st.markdown("<b>Brokerage</b>", unsafe_allow_html=True)
                st.write(":red[" + str(round(brokerage,4)) +"]")                
            with col5:
                st.markdown("<b>Net Profit</b>", unsafe_allow_html=True)
                pnl_row(round(net_pnl,2))
            with col6:
                st.markdown("<b>Net Profit %</b>", unsafe_allow_html=True)
                if(capital > 0):
                    pnl_row(round(((net_pnl / capital)*100),2))  
                else:
                    pnl_row(0)
        
        pnl_block(title="Positional", name1="Nifty NTS",name2="NA",name3="NA",name4="NA",name5="NA",name6="NA",\
        l1 = round(w_div(data["nts_nifty_netqty"],data["nts_nifty_numtrades"])),l2="NA",l3="NA",l4="NA",l5="NA",l6="NA",\
        t1=data["nts_nifty_numtrades"],t2="NA",t3="NA",t4="NA",t5="NA",t6="NA",\
        gp1=data["nts_nifty_grosspnl"],gp2="NA",gp3="NA",gp4="NA",gp5="NA",gp6="NA",\
        chg1=data["nts_nifty_charges"],chg2="NA",chg3="NA",chg4="NA",chg5="NA",chg6="NA",\
        np1= data["nts_nifty_netpnl"], np2 = "NA", np3 ="NA", np4 = "NA",np5="NA",np6="NA", \
        npp1= data["nts_nifty_netpnl%"], npp2 = "NA", npp3 = "NA", npp4 = "NA",npp5="NA",npp6="NA")         
        
        pnl_block(title="Intraday", name1="BankNifty MTS",name2="Nifty DTS",name3="BankNifty DTS",name4="FinNifty DTS",name5="NA",name6="NA",\
        l1 = round(w_div(data["mtsm_netqty"],data["mtsm_numtrades"])),l2 = round(w_div(data["dts_nifty_netqty"],data["dts_nifty_numtrades"])),l3=round(w_div(data["dts_banknifty_netqty"],data["dts_banknifty_numtrades"])),l4=round(w_div(data["dts_finnifty_netqty"],data["dts_finnifty_numtrades"])),l5="NA",l6="NA",\
        t1=data["mtsm_numtrades"],t2=data["dts_nifty_numtrades"],t3=data["dts_banknifty_numtrades"],t4=data["dts_finnifty_numtrades"],t5="NA",t6="NA",\
        gp1=data["mtsm_grosspnl"],gp2=data["dts_nifty_grosspnl"],gp3=data["dts_banknifty_grosspnl"],gp4=data["dts_finnifty_grosspnl"],gp5="NA",gp6="NA",\
        chg1=data["mtsm_charges"],chg2=data["dts_nifty_charges"],chg3=data["dts_banknifty_charges"],chg4=data["dts_finnifty_charges"],chg5="NA",chg6="NA",\
        np1= data["mtsm_netpnl"], np2 = data["dts_nifty_netpnl"], np3 = data["dts_banknifty_netpnl"], np4 = data["dts_finnifty_netpnl"],np5="NA",np6="NA", \
        npp1= data["mtsm_netpnl%"], npp2 = data["dts_nifty_netpnl%"], npp3 = data["dts_banknifty_netpnl%"], npp4 = data["dts_finnifty_netpnl%"],npp5="NA",npp6="NA")
        
        pnl_block(title="Option Selling", name1="Bankex",name2="FinNifty",name3="BankNifty",name4="Nifty",name5="Sensex",name6="NA",\
        l1 = round(w_div(data["os_bankex_netqty"],data["os_bankex_numtrades"])),l2 = round(w_div(data["os_finnifty_netqty"],data["os_finnifty_numtrades"])),l3=round(w_div(data["os_banknifty_netqty"],data["os_banknifty_numtrades"])),l4=round(w_div(data["os_nifty_netqty"],data["os_nifty_numtrades"])),l5=round(w_div(data["os_sensex_netqty"],data["os_sensex_numtrades"])),l6="NA",\
        t1=data["os_bankex_numtrades"]+data["os_bankex_buytrades"],t2=data["os_finnifty_numtrades"]+data["os_finnifty_buytrades"],t3=data["os_banknifty_numtrades"]+data["os_banknifty_buytrades"],t4=data["os_nifty_numtrades"]+data["os_nifty_buytrades"],t5=data["os_sensex_numtrades"]+data["os_sensex_buytrades"],t6="NA",\
        gp1=data["os_bankex_grosspnl"],gp2=data["os_finnifty_grosspnl"],gp3=data["os_banknifty_grosspnl"],gp4=data["os_nifty_grosspnl"],gp5=data["os_sensex_grosspnl"],gp6="NA",\
        chg1=data["os_bankex_charges"],chg2=data["os_finnifty_charges"],chg3=data["os_banknifty_charges"],chg4=data["os_nifty_charges"],chg5=data["os_sensex_charges"],chg6="NA",\
        np1= data["os_bankex_netpnl"], np2 = data["os_finnifty_netpnl"], np3 = data["os_banknifty_netpnl"], np4 = data["os_nifty_netpnl"],np5=data["os_sensex_netpnl"],np6="NA", \
        npp1= data["os_bankex_netpnl%"], npp2 = data["os_finnifty_netpnl%"], npp3 = data["os_banknifty_netpnl%"], npp4 = data["os_nifty_netpnl%"],npp5=data["os_sensex_netpnl%"],npp6="NA")
        
        pnl_block(title="Commodity", name1="Silver CTS",name2="Silver OS",name3="NA",name4="NA",name5="NA",name6="NA",\
        l1 = round(w_div(data["cts_silverfut_netqty"],data["cts_silverfut_numtrades"])),l2 = round(w_div(data["os_silver_netqty"],data["os_silver_numtrades"])),l3="NA",l4="NA",l5="NA",l6="NA",\
        t1=data["cts_silverfut_numtrades"],t2 = data["os_silver_numtrades"]+data["os_silver_buytrades"],t3="NA",t4="NA",t5="NA",t6="NA",\
        gp1=data["cts_silverfut_grosspnl"],gp2=data["os_silver_grosspnl"],gp3="NA",gp4="NA",gp5="NA",gp6="NA",\
        chg1=data["cts_silverfut_charges"],chg2=data["os_silver_charges"],chg3="NA",chg4="NA",chg5="NA",chg6="NA",\
        np1= data["cts_silverfut_netpnl"], np2 = data["os_silver_netpnl"], np3="NA", np4="NA",np5="NA",np6="NA", \
        npp1= data["cts_silverfut_netpnl%"], npp2 = data["os_silver_netpnl%"], npp3="NA", npp4="NA",npp5="NA",npp6="NA")              
              
    def save_setting():          
    
        msg = st.toast(":green[Updating Database]",icon='⌛')       
        
        doc_ref.set({
            'userid': st.session_state["clientid_val"],
            'capital': st.session_state["capital_val"],
            'startdate': str(st.session_state["sd_val"]),
            'enddate': str(st.session_state["ed_val"]),
            'api_token': st.session_state["token_val"]            
        })
        time.sleep(1)
        msg.toast(":green[Settings Saved]",icon='🎉')              
          
    def logout():
        auth_functions.sign_out()
    
    def check_cred():
        if st.session_state["token_val"] and st.session_state["clientid_val"]:
            dhan = dhanhq(st.session_state["clientid_val"],st.session_state["token_val"],)
            out = dhan.get_fund_limits()            
            if(out["status"] != "success"):
                st.error(":red[API Token is not correct]",icon = "🚨")               
            else:
                if(out["data"]["dhanClientId"] != st.session_state["clientid_val"]):
                    st.error(":red[Client ID is not correct]", icon = "🚨")                    
    
    #main 
    
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="t7member-a7b8a")   
    doc_ref = db.collection('journal').document(st.session_state.user_info.get("email"))
   
    doc = doc_ref.get().to_dict()   
   
    token_val = ""
    clientid_val=""
    capital_val = 100000
    sd_val = datetime.date.today() - datetime.timedelta(days=30)
    ed_val = datetime.date.today()
    
    if not doc:         
        doc_ref.set({
            'userid': clientid_val,
            'capital': capital_val,
            'startdate': str(sd_val),
            'enddate': str(ed_val),
            'api_token': token_val           
        }) 
    else:
        token_val = doc["api_token"]
        clientid_val = doc["userid"]
        capital_val = doc["capital"]
        sd_val = datetime.datetime.strptime(doc["startdate"], '%Y-%m-%d').date()
        ed_val = datetime.datetime.strptime(doc["enddate"], '%Y-%m-%d').date()
    
    token = st.text_input("API Token",value = token_val,key = "token_val",on_change = check_cred)
    clientid = st.text_input("Client ID",value= clientid_val,key = "clientid_val",on_change = check_cred)
    capital = st.number_input("Capital", min_value= 0, max_value=None, value=capital_val, step=1, help="Enter trading capital", disabled=False, label_visibility="visible",key="capital_val")
    start_date = st.date_input("Start Date", value = sd_val,key = "sd_val")
    end_date = st.date_input("End Date", value = ed_val,key = "ed_val")    
          
    [col1,col2,col3,col4] = st.columns(4)
    with col2:
        st.button("Save Settings", type="primary", on_click=save_setting,use_container_width=False) 
    with col3:
        st.button("Compute PnL", type="primary", on_click=click_button,use_container_width=False)   
    st.button("Logout", type="primary", on_click=logout,use_container_width=True) 

    dhan = dhanhq(clientid,token)   
        
 
if __name__ == "__main__":
    run()