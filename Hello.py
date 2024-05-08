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

from streamlit.logger import get_logger
from dateutil import parser 
from google.cloud import firestore
from google.oauth2 import service_account

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="T7 Journal",
        page_icon="👋",
    )

    st.title("T7 Journal")

    # st.sidebar.success("Select a demo above.")

    st.markdown(
        """
        A tool to display trading profit and loss automatically based on user settings.
        The tool is integrated with Dhan statement API only. So only Dhan users can use this tool. 
    """
    )

    def get_open_trades(trade):
        
        buylist = dict()
        selllist = dict()
        openpos = dict()
        index = 0
        
        # for item in trade:
        #     if "BUY" in item["transactionType"]: 
        #         buylist = item
        #         os_silver_netbuy = os_silver_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
        #         overnight_silver_fut_qty = overnight_silver_fut_qty + int(item["tradedQuantity"])
        #     if "SELL" in item["transactionType"]:
        #         selllist = item
        #         os_silver_netsell = os_silver_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
        #         overnight_silver_fut_qty = overnight_silver_fut_qty - int(item["tradedQuantity"])
        
        # if(buylist):            
        #     for buytrade in buylist:                            
        #         for selltrade in selllist :
        #             if(buytrade["customSymbol"] != selltrade["customSymbol"]):
        #                 continue
        #             else :
        #                 openpos[index] ={'contract': buytrade["customSymbol"], 'tradeval': str(selltrade["tradedPrice"] - buytrade["tradedPrice"]), 'tradeqty': str(selltrade["tradedQuantity"] - buytrade["tradedQuantity"])}
            
            
        # else:
            


    def mtsm_pnl():
        mtsm_starttime = datetime.time(9, 16, 0)
        mtsm_endtime = datetime.time(9, 45, 0)
        dts_starttime = datetime.time(9, 45, 0)
        dts_endtime = datetime.time(15, 20, 0)
        
        mtsm_netbuy =  mtsm_netsell =  mtsm_charges = mtsm_brokerage = mtsm_numtrades = 0
        os_bankex_netbuy = os_bankex_netsell = os_bankex_charges = os_bankex_brokerage = os_bankex_numtrades = 0
        os_sensex_netbuy = os_sensex_netsell = os_sensex_charges = os_sensex_brokerage = os_sensex_numtrades = 0
        os_banknifty_netbuy = os_banknifty_netsell = os_banknifty_charges = os_banknifty_brokerage = os_banknifty_numtrades = 0
        os_finnifty_netbuy = os_finnifty_netsell = os_finnifty_charges = os_finnifty_brokerage = os_finnifty_numtrades = 0
        os_nifty_netbuy = os_nifty_netsell = os_nifty_charges = os_nifty_brokerage = os_nifty_numtrades = 0
        dts_nifty_netbuy = dts_nifty_netsell = dts_nifty_charges = dts_nifty_brokerage = dts_nifty_numtrades = 0
        dts_banknifty_netbuy = dts_banknifty_netsell = dts_banknifty_charges = dts_banknifty_brokerage = dts_banknifty_numtrades = 0
        dts_finnifty_netbuy = dts_finnifty_netsell = dts_finnifty_charges = dts_finnifty_brokerage = dts_finnifty_numtrades = 0
        cts_silverfut_netbuy = cts_silverfut_netsell = cts_silverfut_charges = cts_silverfut_brokerage = cts_silverfut_numtrades = 0 
        os_silver_netbuy = os_silver_netsell = os_silver_charges = os_silver_brokerage = os_silver_numtrades = 0
        overnight_silver_fut_pos = dict()
        overnight_silver_fut_qty = 0
        silver_margin_count = 0 
        
        pagecount = 0
        current_date = start_date
        
        while current_date <= end_date:
            urllink = "https://api.dhan.co/tradeHistory/"+ current_date.strftime("%Y-%m-%d") + "/" + current_date.strftime("%Y-%m-%d") + "/" + str(pagecount) + ""
            myobj = {"Content-Type": "application/json", "access-token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzE3NDgxMzUxLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTAwMDU4MTQ2MCJ9.KIM6BqdHMgYpB8VVxm9KUEnxGd9rMV5Wn8ZLK2KQPgRTsX1Uo50u4TOuLtfKrFapUFgoUooelF7oOq940YD8jQ"}
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
                            if int(item["tradedQuantity"]) == 75:
                                if "BUY" in item["transactionType"]: 
                                    mtsm_netbuy = mtsm_netbuy +  float(item["tradedPrice"])
                                if "SELL" in item["transactionType"]:
                                    mtsm_netsell = mtsm_netsell +  float(item["tradedPrice"])
                                mtsm_brokerage = mtsm_brokerage + float(item["brokerageCharges"])
                                mtsm_numtrades = mtsm_numtrades + 1
                                mtsm_charges = mtsm_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "BANKNIFTY" not in item["customSymbol"] and "FINNIFTY" not in item["customSymbol"] and "NIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_nifty_netbuy = dts_nifty_netbuy +  float(item["tradedPrice"])
                            if "SELL" in item["transactionType"]:
                                dts_nifty_netsell = dts_nifty_netsell +  float(item["tradedPrice"])
                            dts_nifty_brokerage = dts_nifty_brokerage + float(item["brokerageCharges"])
                            dts_nifty_numtrades = dts_nifty_numtrades + 1
                            dts_nifty_charges = dts_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "BANKNIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_banknifty_netbuy = dts_banknifty_netbuy +  float(item["tradedPrice"])
                            if "SELL" in item["transactionType"]:
                                dts_banknifty_netsell = dts_banknifty_netsell +  float(item["tradedPrice"])
                            dts_banknifty_brokerage = dts_banknifty_brokerage + float(item["brokerageCharges"])
                            dts_banknifty_numtrades = dts_banknifty_numtrades + 1
                            dts_banknifty_charges = dts_banknifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "FINNIFTY" in item["customSymbol"] and "INTRADAY" in item["productType"] :
                        d = parser.parse(item["exchangeTime"]).time()
                        if dts_endtime >= d >= dts_starttime: 
                            if "BUY" in item["transactionType"]: 
                                dts_finnifty_netbuy = dts_finnifty_netbuy +  float(item["tradedPrice"])
                            if "SELL" in item["transactionType"]:
                                dts_finnifty_netsell = dts_finnifty_netsell +  float(item["tradedPrice"])
                            dts_finnifty_brokerage = dts_finnifty_brokerage + float(item["brokerageCharges"])
                            dts_finnifty_numtrades = dts_finnifty_numtrades + 1
                            dts_finnifty_charges = dts_finnifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                
                    if "BANKEX" in item["customSymbol"] :
                        if "BUY" in item["transactionType"]: 
                            os_bankex_netbuy = os_bankex_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        if "SELL" in item["transactionType"]:
                            os_bankex_netsell = os_bankex_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        os_bankex_brokerage = os_bankex_brokerage + float(item["brokerageCharges"])
                        os_bankex_numtrades =  os_bankex_numtrades + 1
                        os_bankex_charges = os_bankex_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "FINNIFTY" in item["customSymbol"] :
                        if "BUY" in item["transactionType"]: 
                            os_finnifty_netbuy = os_finnifty_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        if "SELL" in item["transactionType"]:
                            os_finnifty_netsell = os_finnifty_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        os_finnifty_brokerage = os_finnifty_brokerage + float(item["brokerageCharges"])
                        os_finnifty_numtrades = os_finnifty_numtrades + 1
                        os_finnifty_charges = os_finnifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                
                    if "SENSEX" in item["customSymbol"] :
                        if "BUY" in item["transactionType"]: 
                            os_sensex_netbuy = os_sensex_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        if "SELL" in item["transactionType"]:
                            os_sensex_netsell = os_sensex_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        os_sensex_brokerage = os_sensex_brokerage + float(item["brokerageCharges"])
                        os_sensex_numtrades = os_sensex_numtrades + 1
                        os_sensex_charges = os_sensex_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "BANKNIFTY" in item["customSymbol"] and "MARGIN" in item["productType"] :
                        if "BUY" in item["transactionType"]: 
                            os_banknifty_netbuy = os_banknifty_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        if "SELL" in item["transactionType"]:
                            os_banknifty_netsell = os_banknifty_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        os_banknifty_brokerage = os_banknifty_brokerage + float(item["brokerageCharges"])
                        os_banknifty_numtrades = os_banknifty_numtrades + 1
                        os_banknifty_charges = os_banknifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                
                    if "NIFTY" in item["customSymbol"] and "MARGIN" in item["productType"] :
                        if "BUY" in item["transactionType"]: 
                            os_nifty_netbuy = os_nifty_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        if "SELL" in item["transactionType"]:
                            os_nifty_netsell = os_nifty_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                        os_nifty_brokerage = os_nifty_brokerage + float(item["brokerageCharges"])
                        os_nifty_numtrades = os_nifty_numtrades + 1
                        os_nifty_charges = os_nifty_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                
                    if "SILVER" in item["customSymbol"] and "FUTCOM" in item["instrument"]:                        
                        if "INTRADAY" in item["productType"] :
                            if "BUY" in item["transactionType"]: 
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                            if "SELL" in item["transactionType"]:
                                cts_silverfut_netsell = cts_silverfut_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))                        
                        if "MARGIN" in item["productType"] :
                            if "BUY" in item["transactionType"]: 
                                cts_silverfut_netbuy = cts_silverfut_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                            if "SELL" in item["transactionType"]:
                                cts_silverfut_netsell = cts_silverfut_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))           
                        cts_silverfut_brokerage = cts_silverfut_brokerage + float(item["brokerageCharges"])
                        cts_silverfut_numtrades = cts_silverfut_numtrades + 1
                        cts_silverfut_charges = cts_silverfut_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                    
                    if "SILVER" in item["customSymbol"] and "OPTFUT" in item["instrument"]:
                        
                        if "BUY" in item["transactionType"]: 
                            os_silver_netbuy = os_silver_netbuy +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                            overnight_silver_fut_qty = overnight_silver_fut_qty + int(item["tradedQuantity"])
                        if "SELL" in item["transactionType"]:
                            os_silver_netsell = os_silver_netsell +  (float(item["tradedPrice"]) * int(item["tradedQuantity"]))
                            overnight_silver_fut_qty = overnight_silver_fut_qty - int(item["tradedQuantity"])
                        overnight_silver_fut_pos[silver_margin_count] = item                      
                        os_silver_brokerage = os_silver_brokerage + float(item["brokerageCharges"])
                        os_silver_numtrades = os_silver_numtrades + 1
                        os_silver_charges = os_silver_charges + float(item["sebiTax"]) + float(item["stt"]) + float(item["brokerageCharges"]) + float(item["serviceTax"]) + float(item["exchangeTransactionCharges"]) + float(item["stampDuty"])
                
                
                pagecount = pagecount + 1            
       
        Openpos_silver_fut = get_open_trades(overnight_silver_fut_pos)
               
        mtsm_Grosspnl = round((mtsm_netsell - mtsm_netbuy)*75,2)
        mtsm_Chg = round(mtsm_charges,2)
        mtsm_netpnl = round(mtsm_Grosspnl - mtsm_Chg,2)
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
        cts_silverfut_Grosspnl = round((cts_silverfut_netsell - cts_silverfut_netbuy),2)
        cts_silverfut_Chg = round(cts_silverfut_charges,2)
        cts_silverfut_netpnl = round(cts_silverfut_Grosspnl - cts_silverfut_Chg,2)
        os_silver_Grosspnl = round((os_silver_netsell - os_silver_netbuy),2)
        os_silver_Chg = round(os_silver_charges,2)
        os_silver_netpnl = round(os_silver_Grosspnl - os_silver_Chg,2)
        
        output = dict()
        output["mtsm_grosspnl"] = mtsm_Grosspnl
        output["mtsm_charges"] =  mtsm_Chg 
        output["mtsm_netpnl"] =  mtsm_netpnl
        output["mtsm_netpnl%"] = round((( mtsm_netpnl / capital)*100),4)
        output["mtsm_brokerage"] = mtsm_brokerage
        output["mtsm_numtrades"] = mtsm_numtrades
        output["os_bankex_grosspnl"] = os_bankex_Grosspnl
        output["os_bankex_charges"] =  os_bankex_Chg 
        output["os_bankex_netpnl"] = os_bankex_netpnl
        output["os_bankex_netpnl%"] = round(((os_bankex_netpnl / capital)*100),4)
        output["os_bankex_brokerage"] = os_bankex_brokerage
        output["os_bankex_numtrades"] = os_bankex_numtrades
        output["os_finnifty_grosspnl"] = os_finnifty_Grosspnl
        output["os_finnifty_charges"] =  os_finnifty_Chg 
        output["os_finnifty_netpnl"] = os_finnifty_netpnl
        output["os_finnifty_netpnlp"] = round(((os_finnifty_netpnl / capital)*100),4)
        output["os_finnifty_brokerage"] = os_finnifty_brokerage
        output["os_finnifty_numtrades"] = os_finnifty_numtrades
        output["os_sensex_grosspnl"] = os_sensex_Grosspnl
        output["os_sensex_charges"] =  os_sensex_Chg 
        output["os_sensex_netpnl"] = os_sensex_netpnl
        output["os_sensex_netpnl%"] = round(((os_sensex_netpnl / capital)*100),4)
        output["os_sensex_brokerage"] = os_sensex_brokerage
        output["os_sensex_numtrades"] = os_sensex_numtrades        
        output["os_banknifty_grosspnl"] = os_banknifty_Grosspnl
        output["os_banknifty_charges"] =  os_banknifty_Chg 
        output["os_banknifty_netpnl"] = os_banknifty_netpnl
        output["os_banknifty_netpnl%"] = round(((os_banknifty_netpnl / capital)*100),4)
        output["os_banknifty_brokerage"] = os_banknifty_brokerage
        output["os_banknifty_numtrades"] = os_banknifty_numtrades  
        output["os_nifty_grosspnl"] = os_nifty_Grosspnl
        output["os_nifty_charges"] =  os_nifty_Chg 
        output["os_nifty_netpnl"] = os_nifty_netpnl
        output["os_nifty_netpnl%"] = round(((os_nifty_netpnl / capital)*100),4)
        output["os_nifty_brokerage"] = os_nifty_brokerage
        output["os_nifty_numtrades"] = os_nifty_numtrades  
        output["dts_nifty_grosspnl"] = dts_nifty_Grosspnl
        output["dts_nifty_charges"] =  dts_nifty_Chg 
        output["dts_nifty_netpnl"] = dts_nifty_netpnl
        output["dts_nifty_netpnl%"] = round(((dts_nifty_netpnl / capital)*100),4)
        output["dts_nifty_brokerage"] = dts_nifty_brokerage
        output["dts_nifty_numtrades"] = dts_nifty_numtrades  
        output["dts_banknifty_grosspnl"] = dts_banknifty_Grosspnl
        output["dts_banknifty_charges"] = dts_banknifty_Chg
        output["dts_banknifty_netpnl"] = dts_banknifty_netpnl 
        output["dts_banknifty_netpnl%"] = round(((dts_banknifty_netpnl / capital)*100),4)
        output["dts_banknifty_brokerage"] = dts_banknifty_brokerage
        output["dts_banknifty_numtrades"] = dts_banknifty_numtrades  
        output["dts_finnifty_grosspnl"] = dts_finnifty_Grosspnl
        output["dts_finnifty_charges"] =  dts_finnifty_Chg 
        output["dts_finnifty_netpnl"] = dts_finnifty_netpnl 
        output["dts_finnifty_netpnl%"] = round(((dts_finnifty_netpnl / capital)*100),4)
        output["dts_finnifty_brokerage"] = dts_finnifty_brokerage
        output["dts_finnifty_numtrades"] = dts_finnifty_numtrades  
        output["cts_silverfut_grosspnl"] = cts_silverfut_Grosspnl
        output["cts_silverfut_charges"] =  cts_silverfut_Chg
        output["cts_silverfut_netpnl"] = cts_silverfut_netpnl 
        output["cts_silverfut_netpnl%"] = round(((cts_silverfut_netpnl / capital)*100),4)
        output["cts_silverfut_brokerage"] = cts_silverfut_brokerage
        output["cts_silverfut_numtrades"] = cts_silverfut_numtrades
        output["os_silver_grosspnl"] = os_silver_Grosspnl
        output["os_silver_charges"] =  os_silver_Chg 
        output["os_silver_netpnl"] = os_silver_netpnl
        output["os_silver_netpnl%"] = round(((os_silver_netpnl / capital)*100),4)
        output["os_silver_brokerage"] = os_silver_brokerage
        output["os_silver_numtrades"] = os_silver_numtrades        
        
        return(output)
       
    
    def click_button():
        data = mtsm_pnl()    
        st.write(":blue[Morning Blaster (BankNifty) --> Gross PnL -] :green[" + str(data["mtsm_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["mtsm_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["mtsm_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["mtsm_netpnl%"])+ "]")  
        st.write(":blue[OS (Bankex) --> Gross PnL -] :green[" + str(data["os_bankex_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_bankex_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_bankex_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_bankex_netpnl%"])+ "]")  
        st.write(":blue[OS (finnifty) --> Gross PnL -] :green[" + str(data["os_finnifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_finnifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_finnifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_finnifty_netpnlp"])+ "]")  
        st.write(":blue[OS (BankNifty) --> Gross PnL -] :green[" + str(data["os_banknifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_banknifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_banknifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_banknifty_netpnl%"])+ "]")  
        st.write(":blue[OS (Sensex) --> Gross PnL -] :green[" + str(data["os_sensex_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_sensex_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_sensex_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_sensex_netpnl%"])+ "]")  
        st.write(":blue[OS (Nifty) --> Gross PnL -] :green[" + str(data["os_nifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_nifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_nifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_nifty_netpnl%"])+ "]")  
        st.write(":blue[DTS (Nifty) --> Gross PnL -] :green[" + str(data["dts_nifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["dts_nifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["dts_nifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["dts_nifty_netpnl%"])+ "]")  
        st.write(":blue[DTS (BankNifty) --> Gross PnL -] :green[" + str(data["dts_banknifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["dts_banknifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["dts_banknifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["dts_banknifty_netpnl%"])+ "]")  
        st.write(":blue[DTS (FinNifty) --> Gross PnL -] :green[" + str(data["dts_finnifty_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["dts_finnifty_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["dts_finnifty_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["dts_finnifty_netpnl%"])+ "]")  
        st.write(":blue[CTS (Silver) --> Gross PnL -] :green[" + str(data["cts_silverfut_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["cts_silverfut_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["cts_silverfut_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["cts_silverfut_netpnl%"])+ "]")  
        st.write(":blue[OS (Silver) --> Gross PnL -] :green[" + str(data["os_silver_grosspnl"]) + "]    :blue[Charges -] :red[" + str(data["os_silver_charges"]) + "  "+  "]    :blue[Net PnL - ] :green[" + str(data["os_silver_netpnl"])+"]    :blue[Net PnL % - ] :green[" + str(data["os_silver_netpnl%"])+ "]")  
        
        gross_pnl = data["mtsm_grosspnl"] + data["os_bankex_grosspnl"] + data["os_finnifty_grosspnl"]+ data["os_banknifty_grosspnl"]+ data["os_sensex_grosspnl"] + data["os_nifty_grosspnl"] + data["dts_nifty_grosspnl"] + data["dts_banknifty_grosspnl"] + data["dts_finnifty_grosspnl"] + data["cts_silverfut_grosspnl"] + data["os_silver_grosspnl"]
        brokerage = data["mtsm_brokerage"] + data["os_bankex_brokerage"] + data["os_finnifty_brokerage"] + data["os_banknifty_brokerage"] + data["os_nifty_brokerage"] + data["os_sensex_brokerage"] + data["dts_nifty_brokerage"] + data["dts_banknifty_brokerage"] + data["dts_finnifty_brokerage"] + data["cts_silverfut_brokerage"] + data["os_silver_brokerage"]
        charges = data["mtsm_charges"] + data["os_bankex_charges"] + data["os_finnifty_charges"] + data["os_banknifty_charges"] + data["os_nifty_charges"] + data["os_sensex_charges"] + data["dts_nifty_charges"] + data["dts_banknifty_charges"] + data["dts_finnifty_charges"] + data["cts_silverfut_charges"] + data["os_silver_charges"]
        net_pnl = data["mtsm_netpnl"] + data["os_bankex_netpnl"] + data["os_finnifty_netpnl"]+ data["os_banknifty_netpnl"]+ data["os_sensex_netpnl"] + data["os_nifty_netpnl"] + data["dts_nifty_netpnl"] + data["dts_banknifty_netpnl"] + data["dts_finnifty_netpnl"] + data["cts_silverfut_netpnl"] + data["os_silver_netpnl"]
        charges_less_brokerage = round(charges - brokerage,2)

        st.write(":blue[Total Trades -->] :blue[" + str(data["os_banknifty_numtrades"] + data["os_bankex_numtrades"] + data["os_sensex_numtrades"] +  data["os_finnifty_numtrades"] + data["mtsm_numtrades"] + data["os_nifty_numtrades"] + data["dts_nifty_numtrades"] + data["dts_banknifty_numtrades"] + data["dts_finnifty_numtrades"] + data["cts_silverfut_numtrades"] + data["os_silver_numtrades"])+"]")
        st.write(":blue[Charges -->] :red[" + str(charges_less_brokerage)+"]")
        st.write(":blue[Brokerage -->] :red[" + str(round(brokerage,4))+"]")
        st.write(":blue[Net PnL -->] :green[" + str(net_pnl)+"]")
        st.write(":blue[Net PnL (%) -->] :green[" + str(round(((net_pnl / capital)*100),4))+"]")
       

    def save_setting():
        
        db = firestore.Client.from_service_account_json("t7member-a7b8a-firebase-adminsdk-4j03p-6795a99ba1.json")
        doc_ref = db.collection('journal').document('WuaSwUfW0Ggbmzs2iSTW')
        doc_ref.set({
            'userid': 't7support',
            'capital': str(capital),
            'startdate': str(start_date),
            'enddate': str(end_date),
            'api_token': token
        })


    
    #main

    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="t7member-a7b8a")   
    #db = firestore.Client.from_service_account_json("t7member-a7b8a-firebase-adminsdk-4j03p-6795a99ba1.json")
    doc_ref = db.collection('journal').document('WuaSwUfW0Ggbmzs2iSTW')
    doc = doc_ref.get().to_dict()
    

    token = st.text_input("API Token")
    clientid = st.text_input("Client ID")
    capital = st.number_input("Capital", min_value=0, max_value=None, value=int(doc["capital"]), step=1, help="Enter trading capital", disabled=False, label_visibility="visible")
    start_date = st.date_input("Start Date", value = datetime.datetime.strptime(doc["startdate"], '%Y-%m-%d').date())
    end_date = st.date_input("End Date", value = datetime.datetime.strptime(doc["enddate"], '%Y-%m-%d').date())
    st.button("Save", type="primary", on_click=save_setting) 
    st.button("Compute", type="primary", on_click=click_button)    


   



if __name__ == "__main__":
    run()