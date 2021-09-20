#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mpc
import seaborn as sns
import argparse
plt.rcParams.update({'font.size': 12})


# In[2]:

parser = argparse.ArgumentParser()
parser.add_argument("dataframe_file", help="dataframe file with postprocessed scan data")
args = parser.parse_args()

dataframe_file = args.dataframe_file


# In[3]:


df = pd.read_csv(dataframe_file,sep = ";")#,na_filter=False) # <- problem with continent code NA for North America, if continent code is needed set na_filter=False


# In[4]:


df["count"] = 1


# In[5]:


df_by_country_total = df.groupby(["country_request","response_type"]).sum().reset_index()[["country_request","response_type","count"]]


# In[6]:


def get_freq(country,df,mode):
    if mode=="trans_rel":
        try:
            return (df[(df["country_request"]==country) & (df["response_type"]=="Transparent Forwarder")]["count"].tolist()[0] / df[(df["country_request"]==country)]["count"].sum())*100
        except:
            return 0
    elif mode=="trans_abs":
        try:
            return df[(df["country_request"]==country) & (df["response_type"]=="Transparent Forwarder")]["count"].tolist()[0]
        except:
            return 0
    elif mode=="fwd":
        try:
            return (df[(df["country_request"]==country) & (df["response_type"]=="Forwarder")]["count"].tolist()[0] / df[(df["country_request"]==country)]["count"].sum())*100
        except:
            return 0
    elif mode=="res":
        try:
            return (df[(df["country_request"]==country) & (df["response_type"]=="Resolver")]["count"].tolist()[0] / df[(df["country_request"]==country)]["count"].sum())*100
        except:
            return 0
    else:
        return 0


# In[7]:


df_country_index = df_by_country_total.groupby("country_request").count()
df_country_index = df_country_index.reset_index()
df_country_index["% Transparent Forwarder"] = df_country_index["country_request"].apply(get_freq,args=(df_by_country_total,"trans_rel"))
df_country_index["% Recursive Forwarder"] = df_country_index["country_request"].apply(get_freq,args=(df_by_country_total,"fwd"))
df_country_index["% Recursive Resolver"] = df_country_index["country_request"].apply(get_freq,args=(df_by_country_total,"res"))
df_country_index["# Transparent Forwarder"] = df_country_index["country_request"].apply(get_freq,args=(df_by_country_total,"trans_abs"))
df_country_index = df_country_index.set_index("country_request")[["% Transparent Forwarder","% Recursive Resolver","% Recursive Forwarder","# Transparent Forwarder"]]


# In[8]:


df_sorted = df_country_index.sort_values("# Transparent Forwarder",ascending=False).head(50)
share_cols = ["% Transparent Forwarder", "% Recursive Forwarder","% Recursive Resolver",]

ax = df_sorted[share_cols].plot.bar(stacked=True, figsize=(14*0.9,4*0.9), #figsize=(8*0.9,3*0.9),
                                 color=["#D9514E", "#2DA8D8","#74d82d"])
# plot count as line
ax2 = df_sorted["# Transparent Forwarder"].plot(marker=".", c="black", ax=ax,
                               secondary_y=True, rot=90, alpha=0.7)
ax.set_ylabel("ODNS Share [%]")
ax.set_xlabel("Top 50 Countries, Descending by Total Transparent Forwarder Count")
ax.set_ylim((0,100))
ax2.set_ylabel("Transparent Forwarder [#]")
ax2.set_yscale("symlog")
ax2.set_ylim((10**2,10**6))
ax2.grid(alpha=0.7, zorder=-1000)
handles, labels = ax.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax.legend().remove()
# insert -1 for reverse sort orter
ax2.legend(handles[::-1] + handles2,
          labels[::-1] + [ l+" (Left)" for l in labels2],
          loc="best", bbox_to_anchor=(0.5, 0.4, 0.5, 0.5),fancybox=True, shadow=True)
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
ax2.yaxis.set_label_position("left")
ax2.yaxis.tick_left()

# save and clean up
fig = ax.get_figure()
fig.tight_layout(pad=0.5)
fig.savefig("./figures/bars_topxcc_odns_shares.pdf")
#plt.show()
plt.close(fig)


# In[9]:


def get_trans_fwd_count(index, df):
    r_type = df[df.index==index]["response_type"].tolist()[0]
    if r_type == "Transparent Forwarder":
        return df[df.index==index]["count"].tolist()[0]
    else:
        return 0


# In[10]:


df_tmp = df_by_country_total.copy().reset_index()
df_tmp["transp fwd count"]=df_tmp["index"].apply(get_trans_fwd_count,args=(df_by_country_total,))
df_tmp = df_tmp.groupby("country_request").sum("transp fwd count").reset_index()
df_cdf_plot = df_tmp.set_index("country_request")["transp fwd count"]
cdf = df_cdf_plot.value_counts(normalize=False).sort_index().cumsum()

ax = cdf.plot(logx=True, figsize=(8*0.9,3*0.9))#(8*0.7,3*0.7))

ax.set_ylabel("Countries [#]")
ax.set_ylim(0)

ax.set_xscale("symlog")
ax.set_xlim(0)
ax.set_xlabel("Transparent Forwarder [#]")
ax.text(10**4.1, 150, "TOP 10", size=12, color='dimgrey')#, rotation=90)

fig = ax.get_figure()
plt.axvspan(df_cdf_plot.sort_values(ascending=False).tolist()[9], df_by_country_total[df_by_country_total["response_type"]=="Transparent Forwarder"]["count"].max(), facecolor='lightgrey', alpha=0.5)
fig.savefig("./figures/cdf_transp_fwd_per_cc.pdf", bbox_inches='tight')

#plt.show()
plt.close(fig)

# In[12]:


def get_company(asn):
    if asn in [139190, 139070, 45566, 16591, 15169, 19527, 36040, 43515, 16550]:
        return "google"
    elif asn == 13335:
        return "cloudflare"
    elif asn == 19281:
        return "quad9"
    elif asn == 36692:
        return "opendns"
    else:
        return "other"


# In[13]:


df_heatmap_raw = df.copy()

df_heatmap_raw["company"] = df_heatmap_raw["asn_response"].apply(get_company)


# In[14]:


df_others = df_heatmap_raw[(df_heatmap_raw["country_request"].isin(["BRA","IND","TUR","ARG","POL","USA","IDN","BGD","CHN","MUS"]))                & (df_heatmap_raw["response_type"]=="Transparent Forwarder")                & (df_heatmap_raw["company"]=="other")].groupby(["country_request","asn_response"]).count().reset_index()[["country_request","asn_response","count"]]


# In[15]:


def get_freq_others(index, df):
    asn = df[df.index==index]["asn_response"].tolist()[0]
    country = df[df.index==index]["country_request"].tolist()[0]
    return df[df.index==index]["count"].tolist()[0]/df[(df["country_request"]==country)]["count"].sum()


# In[16]:


df_tmp = df_others.copy().reset_index()
df_tmp["relative frequency"] = df_tmp["index"].apply(get_freq_others,args=(df_others,))
df_tmp = df_tmp[["country_request","asn_response","count","relative frequency"]]


# In[17]:


df_heatmap_raw = df_heatmap_raw.groupby(["country_request","response_type","company"]).count().reset_index()[["country_request","response_type","company","count"]]
df_heatmap_raw = df_heatmap_raw[df_heatmap_raw["response_type"]=="Transparent Forwarder"]


# In[18]:


def get_rel_for_company(country,df,mode):
    if mode=="total":
        return df[(df["country_request"]==country)]["count"].sum()
    else:
        try:
            return (df[(df["country_request"]==country) & (df["company"]==mode)]["count"].sum() / df[(df["country_request"]==country)]["count"].sum())*100
        except:
            return 0


# In[19]:


df_heatmap = df_heatmap_raw.copy()
df_heatmap["Google"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"google"))
df_heatmap["Cloudflare"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"cloudflare"))
df_heatmap["Quad9"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"quad9"))
df_heatmap["OpenDNS"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"opendns"))
df_heatmap["Other"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"other"))
df_heatmap["TOTAL"] = df_heatmap["country_request"].apply(get_rel_for_company,args=(df_heatmap_raw,"total"))
df_heatmap = df_heatmap.drop_duplicates("country_request")
df_heatmap = df_heatmap.set_index("country_request")[["Google","Cloudflare","Quad9","OpenDNS","Other","TOTAL"]]


# In[20]:


import matplotlib
plt.rcParams.update({'font.size': 24})
plot_map = df_heatmap.sort_values("TOTAL",ascending=False)[["Google","Cloudflare","Quad9","OpenDNS","Other"]].head(50).transpose()

plt.figure(figsize=(30,6))
my_colormap = matplotlib.cm.get_cmap("rocket_r").copy()
my_colormap.set_under("w")
ax = sns.heatmap(plot_map, linewidth=1,linecolor="black",cmap=my_colormap,cbar_kws={"label":"Share of Transparent\nForwarders [%]","pad":0.01},                 square=False,vmin=0.01,vmax=100)
cbar = ax.collections[0].colorbar
cbar.set_ticks([0.01, 20, 40, 60, 80, 100])
cbar.set_ticklabels(['0', '20', '40', '60','80', '100'])
plt.xlabel("Top 50 Countries, Descending by Total Transparent Forwarder Count")
plt.ylabel("Source of DNS Response")
plt.xticks(rotation=90)
fig = ax.get_figure()
fig.savefig("./figures/heatmap_dominance_pub_rr.pdf", bbox_inches='tight', pad_inches=0)
plt.rcParams.update({'font.size': 12})






