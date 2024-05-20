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


from streamlit.logger import get_logger
from dateutil import parser 
from google.cloud import firestore
from google.oauth2 import service_account
from st_pages import Page, show_pages, add_page_title, hide_pages
from collections import defaultdict
from operator import itemgetter



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
            Page("Home.py", "Home","🛋️"),
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
        
        index = j = 0
        contract_in_list = False     
        
        length = len(trade)           
        
        while(index < length):           
            
            j = 0
            contract_in_list = False
            len_net = len(nettradelist)
            
            if "BUY" in trade[index].get("transactionType"): 
                
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

        # st.write("tradelist***************************************")
        # st.write(trade)
        # st.write("nettradelist***************************************")
        # st.write(nettradelist) 
        
        
        # test = sorted(nettradelist.items(), key = lambda x: x[1]['ltt'])
        # st.write(test)  
        # out = test.pop(len(test)-1)
        # st.write(out)
        # st.write(out[1])    

        i = 0
        sum = 0
        while(i < len(nettradelist)):
            if(nettradelist[i]['tradeqty'] != 0):
                sum = sum + nettradelist[i]['val']
            i = i + 1 

        #st.write(sum)
        return(sum)
        

    def mtsm_pnl():
        mtsm_starttime = datetime.time(9, 16, 0)
        mtsm_endtime = datetime.time(9, 45, 0)
        dts_starttime = datetime.time(9, 45, 0)
        dts_endtime = datetime.time(15, 20, 0)
        
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
        
        while current_date <= end_date:
            urllink = "https://api.dhan.co/tradeHistory/"+ current_date.strftime("%Y-%m-%d") + "/" + current_date.strftime("%Y-%m-%d") + "/" + str(pagecount) + ""
            myobj = {"Content-Type": "application/json", "access-token": token}
            x = requests.get(url = urllink, headers = myobj)
            data = json.loads(x.text)
        
            if(not data):
                pagecount = 0
                current_date = current_date + datetime.timedelta(days=1)                
            else:
                for item in data:                     
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
                
                    if "BANKNIFTY" not in item["customSymbol"] and "FINNIFTY" not in item["customSymbol"] and "NIFTY" in item["customSymbol"] and "MARGIN" in item["productType"] :
                        strike = int(item["customSymbol"].split()[3])                        
                        if (strike % 50 == 0 and strike % 100 != 0) and (item["tradedPrice"] < 100):
                            if "BUY" in item["transactionType"]: 
                                os_nifty_netbuy = os_nifty_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                                os_nifty_buytrades = os_nifty_buytrades + 1
                            if "SELL" in item["transactionType"]:
                                os_nifty_netsell = os_nifty_netsell +  item["tradedPrice"] * item["tradedQuantity"]
                                os_nifty_netqty = os_nifty_netqty + item["tradedQuantity"]
                                os_nifty_numtrades = os_nifty_numtrades + 1
                            os_nifty_brokerage = os_nifty_brokerage + float(item["brokerageCharges"])                            
                            os_nifty_charges = os_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
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
                                         
                    if "SILVER" in item["customSymbol"] and "FUTCOM" in item["instrument"]:                        
                        
                        if "INTRADAY" in item["productType"] :                           
                            if "BUY" in item["transactionType"]:                                
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:                                
                                cts_silverfut_netsell = cts_silverfut_netsell +  item["tradedPrice"] * item["tradedQuantity"] 
                            overnight_silver_intrafut_pos[silver_intra_count] = item 
                            silver_intra_count = silver_intra_count + 1                       
                        if "MARGIN" in item["productType"] :
                            if "BUY" in item["transactionType"]: 
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  item["tradedPrice"] * item["tradedQuantity"]
                            if "SELL" in item["transactionType"]:
                                cts_silverfut_netsell = cts_silverfut_netsell +  item["tradedPrice"] * item["tradedQuantity"]           
                            overnight_silver_fut_pos[silver_margin_count] = item 
                            silver_margin_count = silver_margin_count + 1
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
            st.write(":green[" + str(val)+"]") 
        else :
            st.write(":red[" + str(val)+"]")
    
    def pnl_block(title,name1,name2,name3,name4,name5,name6,l1,l2,l3,l4,l5,l6,t1,t2,t3,t4,t5,t6,gp1,gp2,gp3,gp4,gp5,gp6,chg1,chg2,chg3,chg4,chg5,chg6,np1,np2,np3,np4,np5,np6,npp1,npp2,npp3,npp4,npp5,npp6):
        if title:
            
            plot_title(title, size = 3, color = "#1D9AE2")
                        
            with st.container(border=True):        
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                with col1:
                    st.markdown("Index")
                    if name1: 
                        st.write(":blue["+name1+"]")
                    if name2: 
                        st.write(":blue["+name2+"]")
                    if name3: 
                        st.write(":blue["+name3+"]")
                    if name4: 
                        st.write(":blue["+name4+"]")
                    if name5: 
                        st.write(":blue["+name5+"]")
                    if name6: 
                        st.write(":blue["+name6+"]")
                with col2:
                    st.markdown("Avg Qty")
                    if 11:
                        st.write(":blue[" + str(l1)+"]")
                    if l2:
                        st.write(":blue[" + str(l2)+"]")
                    if l3:
                        st.write(":blue[" + str(l3)+"]")
                    if l4: 
                        st.write(":blue[" + str(l4)+"]") 
                    if l5: 
                        st.write(":blue[" + str(l5)+"]")   
                    if l6: 
                        st.write(":blue[" + str(l6)+"]") 
                          
                with col3:
                    st.markdown("Trades")
                    if 11:
                        st.write(":blue[" + str(t1)+"]")
                    if l2:
                        st.write(":blue[" + str(t2)+"]")
                    if l3:
                        st.write(":blue[" + str(t3)+"]")
                    if l4: 
                        st.write(":blue[" + str(t4)+"]") 
                    if l5: 
                        st.write(":blue[" + str(t5)+"]")   
                    if l6: 
                        st.write(":blue[" + str(t6)+"]")        
                with col4:
                    st.markdown("Gross Profit")
                    if gp1:
                        pnl_row(gp1)
                    if gp2:
                        pnl_row(gp2)
                    if gp3:
                        pnl_row(gp3)
                    if gp4: 
                        pnl_row(gp4) 
                    if gp5: 
                        pnl_row(gp5)   
                    if gp6: 
                        pnl_row(gp6)       
                with col5:
                    st.markdown("Charges")
                    if chg1:
                        st.write(":red[" + str(chg1)+"]")
                    if chg2:
                        st.write(":red[" + str(chg2)+"]")
                    if chg3:
                        st.write(":red[" + str(chg3)+"]")
                    if chg4: 
                        st.write(":red[" + str(chg4)+"]") 
                    if chg5: 
                        st.write(":red[" + str(chg5)+"]")   
                    if chg6: 
                        st.write(":red[" + str(chg6)+"]")                  
                   
                with col6:
                    st.markdown("Net Profit")
                    if np1:
                        pnl_row(np1)
                    if np2:
                        pnl_row(np2)
                    if np3:
                        pnl_row(np3)
                    if np4: 
                        pnl_row(np4) 
                    if np5: 
                        pnl_row(np5)   
                    if np6: 
                        pnl_row(np6)             
                with col7:
                    st.markdown("Net Profit %") 
                    if npp1:
                        pnl_row(npp1)
                    if npp2:
                        pnl_row(npp2)
                    if npp3:
                        pnl_row(npp3)
                    if npp4: 
                        pnl_row(npp4) 
                    if npp5: 
                        pnl_row(npp5)   
                    if npp6: 
                        pnl_row(npp6) 
            
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
                st.markdown("Total Trades")
                st.write(":blue[" + str(tot_trades)+"]")
            with col2:
                st.markdown("Gross Profit")
                pnl_row(round(gross_pnl,2))
            with col3:
                st.markdown("Charges")
                st.write(":red[" + str(charges_less_brokerage)+"]")
            with col4:
                st.markdown("Brokerage")
                st.write(":red[" + str(round(brokerage,4)) +"]")                
            with col5:
                st.markdown("Net Profit")
                pnl_row(round(net_pnl,2))
            with col6:
                st.markdown("Net Profit %")
                if(capital > 0):
                    pnl_row(round(((net_pnl / capital)*100),2))  
                else:
                    pnl_row(0)
        
        pnl_block(title="Positional", name1="Nifty NTS",name2="",name3="",name4="",name5="",name6="",\
        l1 = round(w_div(data["nts_nifty_netqty"],data["nts_nifty_numtrades"])),l2 = 0,l3=0,l4=0,l5=0,l6=0,\
        t1=data["nts_nifty_numtrades"],t2=0,t3=0,t4=0,t5=0,t6=0,\
        gp1=data["nts_nifty_grosspnl"],gp2=0,gp3=0,gp4=0,gp5=0,gp6=0,\
        chg1=data["nts_nifty_charges"],chg2=0,chg3=0,chg4=0,chg5=0,chg6=0,\
        np1= data["nts_nifty_netpnl"], np2 = 0, np3 = 0, np4 = 0,np5=0,np6=0, \
        npp1= data["nts_nifty_netpnl%"], npp2 = 0, npp3 = 0, npp4 = 0,npp5=0,npp6=0)         
        
        pnl_block(title="Intraday", name1="BankNifty MTS",name2="Nifty DTS",name3="BankNifty DTS",name4="FinNifty DTS",name5="",name6="",\
        l1 = round(w_div(data["mtsm_netqty"],data["mtsm_numtrades"])),l2 = round(w_div(data["dts_nifty_netqty"],data["dts_nifty_numtrades"])),l3=round(w_div(data["dts_banknifty_netqty"],data["dts_banknifty_numtrades"])),l4=round(w_div(data["dts_finnifty_netqty"],data["dts_finnifty_numtrades"])),l5=0,l6=0,\
        t1=data["mtsm_numtrades"],t2=data["dts_nifty_numtrades"],t3=data["dts_banknifty_numtrades"],t4=data["dts_finnifty_numtrades"],t5=0,t6=0,\
        gp1=data["mtsm_grosspnl"],gp2=data["dts_nifty_grosspnl"],gp3=data["dts_banknifty_grosspnl"],gp4=data["dts_finnifty_grosspnl"],gp5=0,gp6=0,\
        chg1=data["mtsm_charges"],chg2=data["dts_nifty_charges"],chg3=data["dts_banknifty_charges"],chg4=data["dts_finnifty_charges"],chg5=0,chg6=0,\
        np1= data["mtsm_netpnl"], np2 = data["dts_nifty_netpnl"], np3 = data["dts_banknifty_netpnl"], np4 = data["dts_finnifty_netpnl"],np5=0,np6=0, \
        npp1= data["mtsm_netpnl%"], npp2 = data["dts_nifty_netpnl%"], npp3 = data["dts_banknifty_netpnl%"], npp4 = data["dts_finnifty_netpnl%"],npp5=0,npp6=0)
        
        pnl_block(title="Option Selling", name1="Bankex",name2="FinNifty",name3="BankNifty",name4="Nifty",name5="Sensex",name6="",\
        l1 = round(w_div(data["os_bankex_netqty"],data["os_bankex_numtrades"])),l2 = round(w_div(data["os_finnifty_netqty"],data["os_finnifty_numtrades"])),l3=round(w_div(data["os_banknifty_netqty"],data["os_banknifty_numtrades"])),l4=round(w_div(data["os_nifty_netqty"],data["os_nifty_numtrades"])),l5=round(w_div(data["os_sensex_netqty"],data["os_sensex_numtrades"])),l6=0,\
        t1=data["os_bankex_numtrades"]+data["os_bankex_buytrades"],t2=data["os_finnifty_numtrades"]+data["os_finnifty_buytrades"],t3=data["os_banknifty_numtrades"]+data["os_banknifty_buytrades"],t4=data["os_nifty_numtrades"]+data["os_nifty_buytrades"],t5=data["os_sensex_numtrades"]+data["os_sensex_buytrades"],t6=0,\
        gp1=data["os_bankex_grosspnl"],gp2=data["os_finnifty_grosspnl"],gp3=data["os_banknifty_grosspnl"],gp4=data["os_nifty_grosspnl"],gp5=data["os_sensex_grosspnl"],gp6=0,\
        chg1=data["os_bankex_charges"],chg2=data["os_finnifty_charges"],chg3=data["os_banknifty_charges"],chg4=data["os_nifty_charges"],chg5=data["os_sensex_charges"],chg6=0,\
        np1= data["os_bankex_netpnl"], np2 = data["os_finnifty_netpnl"], np3 = data["os_banknifty_netpnl"], np4 = data["os_nifty_netpnl"],np5=data["os_sensex_netpnl"],np6=0, \
        npp1= data["os_bankex_netpnl%"], npp2 = data["os_finnifty_netpnl%"], npp3 = data["os_banknifty_netpnl%"], npp4 = data["os_nifty_netpnl%"],npp5=data["os_sensex_netpnl%"],npp6=0)
        
        pnl_block(title="Commodity", name1="Silver CTS",name2="Silver OS",name3="",name4="",name5="",name6="",\
        l1 = round(w_div(data["cts_silverfut_netqty"],data["cts_silverfut_numtrades"])),l2 = round(w_div(data["os_silver_netqty"],data["os_silver_numtrades"])),l3=0,l4=0,l5=0,l6=0,\
        t1=data["cts_silverfut_numtrades"],t2 = data["os_silver_numtrades"]+data["os_silver_buytrades"],t3=0,t4=0,t5=0,t6=0,\
        gp1=data["cts_silverfut_grosspnl"],gp2=data["os_silver_grosspnl"],gp3=0,gp4=0,gp5=0,gp6=0,\
        chg1=data["cts_silverfut_charges"],chg2=data["os_silver_charges"],chg3=0,chg4=0,chg5=0,chg6=0,\
        np1= data["cts_silverfut_netpnl"], np2 = data["os_silver_netpnl"], np3 = 0, np4 = 0,np5=0,np6=0, \
        npp1= data["cts_silverfut_netpnl%"], npp2 = data["os_silver_netpnl%"], npp3 = 0, npp4 = 0,npp5=0,npp6=0)              
              
    def save_setting():          
    
        msg = st.toast(":green[Updating Database with your new settings]")       
        
        doc_ref.set({
            'userid': st.session_state["clientid_val"],
            'capital': st.session_state["capital_val"],
            'startdate': str(st.session_state["sd_val"]),
            'enddate': str(st.session_state["ed_val"]),
            'api_token': st.session_state["token_val"]            
        })
        time.sleep(1)
        msg.toast(":green[Settings Updated]")
        # msg = st.success('Setting Updated!', icon="✅")        
        # time.sleep(1) # Wait for 3 seconds
        # msg.empty() # Clear the alert
        
          
    def logout():
        auth_functions.sign_out()
    
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
    
    token = st.text_input("API Token",value = token_val,key = "token_val")
    clientid = st.text_input("Client ID",value= clientid_val,key = "clientid_val")
    capital = st.number_input("Capital", min_value= 0, max_value=None, value=capital_val, step=1, help="Enter trading capital", disabled=False, label_visibility="visible",key="capital_val")
    start_date = st.date_input("Start Date", value = sd_val,key = "sd_val")
    end_date = st.date_input("End Date", value = ed_val,key = "ed_val")        
       
    
    [col1,col2,col3,col4] = st.columns(4)
    with col2:
        st.button("Save Settings", type="primary", on_click=save_setting,use_container_width=False) 
    with col3:
        st.button("Compute PnL", type="primary", on_click=click_button,use_container_width=False)   
    st.button("Logout", type="primary", on_click=logout,use_container_width=True)    
        
 
if __name__ == "__main__":
    run()