import json
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
from functools import lru_cache
import argparse


def to_string_with_leading_zeros(number,digits):
    result = str(number)
    while len(result) < digits:
        result = '0' + result
    return result

def filter_traffic(files,directory,IP_CLIENT):
    for i in tqdm(range(len(files)-1)):
        #print(files[i])
        df = pd.read_csv(
            files[i], sep=";",
            infer_datetime_format=True,
            parse_dates=["frame.time_epoch"])
        df_out = df[(df["ip.src"] == IP_CLIENT) & (df["dns.flags.response"] == 0)]
        df_in = df[(df["ip.dst"] == IP_CLIENT) & (df["dns.flags.response"] == 1)]
        df_in = df_in.dropna(subset=["dns.resp.ttl", "dns.a"])
        df_out = df_out.rename(columns={"udp.srcport": "udp.port"})
        df_out = df_out.set_index(["dns.id", "udp.port"])
        df_in = df_in.rename(columns={"udp.dstport": "udp.port"})
        df_in = df_in.set_index(["dns.id", "udp.port"])
        df_out = df_out.rename(columns={"ip.dst": "ip.dst.out", "frame.time_epoch": "ts.out"})
        df_out = df_out[["ts.out", "ip.dst.out"]]

        try:
            df_2 = pd.read_csv(
                files[i+1], sep=";",
                infer_datetime_format=True,
                parse_dates=["frame.time_epoch"])
            df_in2 = df_2[(df_2["ip.dst"] == IP_CLIENT) & (df_2["dns.flags.response"] == 1)]

            df_in2 = df_in2.rename(columns={"udp.dstport": "udp.port"})
            df_in2 = df_in2.set_index(["dns.id", "udp.port"])

            second_file = True
        except:
            second_file = False

        df_in = df_in.rename(
            columns={"frame.time_epoch": "ts.in", "ip.src": "ip.src.in", "dns.resp.ttl": "dns.resp.ttl.in",
                     "dns.a": "dns.a.in"})
        df_in = df_in[["ts.in", "ip.src.in", "dns.resp.ttl.in", "dns.a.in","ip.ttl"]]
        df_in2 = df_in2.rename(
            columns={"frame.time_epoch": "ts.in", "ip.src": "ip.src.in", "dns.resp.ttl": "dns.resp.ttl.in",
                     "dns.a": "dns.a.in"})
        df_in2 = df_in2[["ts.in", "ip.src.in", "dns.resp.ttl.in", "dns.a.in","ip.ttl"]]
        if second_file:
            df_in = pd.concat([df_in, df_in2])

        df_sanitized = df_out.join(df_in, how="left")
        df_sanitized = df_sanitized[~pd.isnull(df_sanitized["ip.src.in"])]
        df_sanitized = df_sanitized.drop_duplicates("ip.dst.out")
        df_sanitized = df_sanitized[df_sanitized["ts.in"] > df_sanitized["ts.out"]]

        df_sanitized.to_csv(f"{directory}/filtered_{to_string_with_leading_zeros(i,5)}.csv.gz",sep=";")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_dir", help="absolute path to directory, where csv files are located")
    parser.add_argument("ip_client", help="IP address of the client")
    args = parser.parse_args()
    
    logs_csv_scanner = glob.glob(f"{args.csv_dir}/dns_complete_*.csv.gz")
    logs_csv_scanner.sort()
    #print(logs_csv_scanner)
    filter_traffic(logs_csv_scanner,args.csv_dir,args.ip_client)
