#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np
from tqdm import tqdm
import pyasn as pyasn
from functools import lru_cache
import pycountry

import warnings
warnings.filterwarnings('ignore')

scan_dir = "./sanitized_csv_scan_data/"
asndb_file = "./pyasn_db/IPASN/ipasn-2021-09-20.gz"


# In[2]:


def load_and_join(file_list):
    #load all csv files into data frames
    #concat them to a single one for further processing
    df = pd.read_csv(file_list.pop(0), sep=";")
    for file_name in file_list:
        tmp_df = pd.read_csv(file_name, sep=";")
        df = pd.concat([df,tmp_df],ignore_index=True)
    return df


# In[3]:


logs_csv_scanner = glob.glob(scan_dir + "filtered_*csv.gz")
df_complete = pd.read_csv(logs_csv_scanner.pop(0), sep=";")
for i in tqdm(range(0,len(logs_csv_scanner),50)):
    tmp = load_and_join(logs_csv_scanner[i:i+50])
    df_complete = pd.concat([df,tmp],ignore_index=True)


# In[9]:


df_check_a_record = df_complete[df_complete["dns.a.in"].str.contains("91.216.216.216",na=False)]


# In[10]:


# Of the packets that contain our check A Record, we only want these packets who answered with exactly 2 A Records
df_two_arecords = df_check_a_record[df_check_a_record["dns.a.in"].str.contains("^[^,]*[,]{1}[^,]*$",regex=True,na=False)]


# In[11]:


# rename and reorder columns!
df_two_arecords = df_two_arecords.rename(columns={"ts.out":"timestamp_request","ts.in":"timestamp_response","ip.dst.out":"ip_request","ip.src.in":"ip_response","dns.resp.ttl.in":"dns_ttl","dns.a.in":"a_record","ip.ttl":"ip_ttl"})
df_two_arecords = df_two_arecords[["dns.id","udp.port","timestamp_request","ip_request","timestamp_response","ip_response","a_record","dns_ttl","ip_ttl"]]


# In[12]:


def filter_arecord(arecord):
    iplist = arecord.split(",")
    if iplist[0]=="91.216.216.216":
        return iplist[1]
    else:
        return iplist[0]


# In[13]:


def delete_second_ttl(ttl):
    ttllist = ttl.split(",")
    return ttllist[0]


# In[ ]:


def ip_to_asn_online(ip):
    url = f"https://bgpview.io/ip/{ip}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    asn = None
    try:
        table_data = soup.find("table").findChildren("tr")
    except:
        return None
    else:
        for row in table_data:
            columns = row.findChildren("td")
            for cell in columns:
                value = cell.string
                if value and value[:2]=="AS":
                    asn = value[2:]
        return asn  


# In[14]:


# define helper function with unlimitted cache of results
@lru_cache(maxsize=None)
def map_asn(my_ip, my_asndb):
    
    # its easier to ask for forgiveness, so use try-except
    # (instead of performing the "in" check and than "lookup")
    try:
        ip_asn, ip_prefix = my_asndb.lookup(my_ip)
        if not ip_asn:
            ip_asn = ip_to_asn_online(my_ip)
        return ip_asn
    except:
        return np.nan


# In[15]:


# load pyasn database only once, this is heavy
asndb = pyasn.pyasn(asndb_file)


# In[16]:


df_two_arecords["a_record"] = df_two_arecords["a_record"].apply(filter_arecord)
df_two_arecords["dns_ttl"] = df_two_arecords["dns_ttl"].apply(delete_second_ttl)


# In[17]:


df_two_arecords["asn_request"] = df_two_arecords["ip_request"].apply(map_asn,args=(asndb))
df_two_arecords["asn_response"] = df_two_arecords["ip_response"].apply(map_asn,args=(asndb))
df_two_arecords["asn_arecord"] = df_two_arecords["a_record"].apply(map_asn,args=(asndb))


# In[21]:


def country_to_iso_cc(country):
    # its easier to ask for forgiveness, so use try-except
    # (instead of performing the "in" check and than "lookup")
    try:
        if country=="South Korea":
            return "KOR"
        elif country=="Iran":
            return "IRN"
        elif country=="Macedonia":
            return "MKD"
        elif country=="Moldova":
            return "MDA"
        elif country=="Palestine":
            return "PSE"
        elif country=="Czech Republic":
            return "CZE"
        elif country=="Venezuela":
            return "VEN"
        elif country=="Bolivia" or country=="Bolivia, Plurinational State of":
            return "BOL"
        elif country=="Bonaire":
            return "BES"
        elif country=="British Virgin Islands":
            return "VGB"
        elif country=="Cote d'Ivoire":
            return "CIV"
        elif country=="Curacao":
            return "CUW"
        elif country=="European Union":
            return "EU"
        elif country=="Reunion":
            return "REU"
        elif country=="Taiwan":
            return "TWN"
        else:
            iso_cc = pycountry.countries.get(name=country)
            return iso_cc.alpha_3
    except:
        return np.nan


# In[22]:


def countrycode_to_iso_cc(country):
    # its easier to ask for forgiveness, so use try-except
    # (instead of performing the "in" check and than "lookup")
    try:
        iso_cc = pycountry.countries.get(alpha_2=country)
        return iso_cc.alpha_3
    except:
        return np.nan


# In[23]:


csv_cc = glob.glob("./AS_2_CountryCode/as_country_webcrawl-*.csv")
csv_cc2 = glob.glob("./AS_2_CountryCode/as_to_cc*.csv")
df_cc = load_and_join(csv_cc[:])
df_cc["cc"]=df_cc["country"].apply(country_to_iso_cc)
df_cc2 = pd.read_csv("./AS_2_CountryCode/as_country.csv",sep=";")
df_cc2["cc"] = df_cc2["country"].apply(countrycode_to_iso_cc)
df_cc3 = load_and_join(csv_cc2[:])
df_cc3["cc"] = df_cc3["country"].apply(country_to_iso_cc)


# In[24]:


# define helper function with unlimitted cache of results
@lru_cache(maxsize=None)
def map_asn_to_cc(asn):
    global df_cc, df_cc2, df_cc3
    # its easier to ask for forgiveness, so use try-except
    # (instead of performing the "in" check and than "lookup")
    try:
        cc = df_cc[df_cc["asn"]==asn]["cc"].tolist()[0]
        return cc
    except:
        try:
            cc = df_cc2[df_cc2["asn"]==asn]["cc"].tolist()[0]
            return cc
        except:
            try:
                cc = df_cc3[df_cc3["asn"]==asn]["cc"].tolist()[0]
                return cc
            except:
                return np.nan


# In[25]:


df_two_arecords["country_request"] = df_two_arecords["asn_request"].apply(map_asn_to_cc)
df_two_arecords["country_response"] = df_two_arecords["asn_response"].apply(map_asn_to_cc)


# In[26]:


df_two_arecords = df_two_arecords[["dns.id","udp.port","timestamp_request","ip_request","asn_request","country_request","timestamp_response","ip_response","asn_response","country_response","a_record","asn_arecord","dns_ttl","ip_ttl"]]


# In[27]:


df_resolver = df_two_arecords[(df_two_arecords["ip_request"]==df_two_arecords["ip_response"]) & (df_two_arecords["ip_request"] == df_two_arecords["a_record"])]

# Def. Public Forwarder := Requested IP-adr. matches source IP-adr. of response
#                        & Requested IP-adr. is not equal to IP-adr. of A-Record
df_forwarder = df_two_arecords[(df_two_arecords["ip_request"]==df_two_arecords["ip_response"]) & (df_two_arecords["ip_request"] != df_two_arecords["a_record"])]

# Def. Transp. Forwarder := Requested IP-adr. is not equal to source IP-adr. of response
df_transp_fwd = df_two_arecords[df_two_arecords["ip_request"]!=df_two_arecords["ip_response"]]

# Set response_type value
df_resolver["response_type"] = "Resolver"
df_forwarder["response_type"] = "Forwarder"
df_transp_fwd["response_type"] = "Transparent Forwarder"

# Join them into one frame and write result to csv
df_complete = pd.concat([df_resolver,df_forwarder,df_transp_fwd])
#df_complete.to_csv("dataframe_raw.csv",sep=";",index=False)


# In[28]:


df_complete


# In[29]:


df_complete.to_csv("./dataframes/dataframe_for_analysis.csv.gz",sep=";",index=False)


# In[ ]:




