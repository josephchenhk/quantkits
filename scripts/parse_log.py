# -*- coding: utf-8 -*-
# @Time    : 9/19/2019 2:48 PM
# @Author  : Joseph Chen
# @Email   : joseph.chen@magnumwm.com
# @FileName: parse_log.py
# @Software: PyCharm
import json
import re
import pandas as pd

def timestr_to_milliseconds(timestr:str)->int:
    hour_min_sec, millisec = timestr.split(",")
    hour, min, sec = hour_min_sec.split(":")
    hour, min, sec, millisec = int(hour), int(min), int(sec), int(millisec)
    return hour*3600*1000 + min*60*1000 + sec*1000 + millisec

def extract_milliseconds_from_line(line:str)->int:
    time_search = re.search("\d{2}:\d{2}:\d{2},\d{3}", line, re.IGNORECASE)
    if time_search:
        time_str = time_search.group()
        milliseconds = timestr_to_milliseconds(time_str)
        return milliseconds
    return None

def generate_analysis_report(time_record:dict)->pd.DataFrame:
    df = pd.DataFrame(time_record)
    df = df.T
    df1 = df.shift(1)
    diff = df - df1
    diff.loc['Total', :] = diff.sum(axis=0)
    return diff.T


def parse(file_path:str):
    with open(file_path, "r") as f:
        lns = f.readlines()
        for i,ln in enumerate(lns):
            # print(i,ln)
            time_search = re.search("\d{2}:\d{2}:\d{2},\d{3}", ln, re.IGNORECASE)
            if time_search:
                time_str = time_search.group()
                # print(time_str)
                milliseconds = timestr_to_milliseconds(time_str)
                # print(milliseconds)
                if i%2==0:
                    start = milliseconds
                else:
                    end = milliseconds
                    # print(f"{start} --> {end}: {end-start}")
                    print(end-start)

def parse(file_path:str):
    contains = {1: 'inputBatchOrder-inputOrderStarts',
                2: 'InputOrder-SaveOrderStart',
                3: 'InputOrder-SaveOrderEnd',
                4: 'InputOrder-ibBrokerAdapterGetNextOrderIdStarts',
                5: 'InputOrder-ibBrokerAdapterGetNextOrderIdEnds',
                6: 'InputOrder-ibConnectorPlaceOrderRaiseOrderStarts',
                7: 'InputOrder-ibConnectorPlaceOrderRaiseOrderEnds',
                8: 'inputBatchOrder-inputOrderEnds'}
    occurances = [0] * 8
    time_record = {1: [],
                   2: [],
                   3: [],
                   4: [],
                   5: [],
                   6: [],
                   7: [],
                   8: []}
    with open(file_path, "r") as f:
        lns = f.readlines()
        for i,ln in enumerate(lns):
            # print(i,ln)
            for j in range(8):
                if contains[j+1] in ln:
                    occurances[j] += 1
                    millisec = extract_milliseconds_from_line(ln)
                    time_record[j+1].append(millisec)

    print(occurances)
    print(json.dumps(time_record, indent=4, sort_keys=True))

    result = generate_analysis_report(time_record)
    result.to_csv("result.csv")


if __name__=="__main__":
    file_path = "order.txt"
    parse(file_path)