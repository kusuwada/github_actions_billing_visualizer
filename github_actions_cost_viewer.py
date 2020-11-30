#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Visualize github actions billing and calc billing distribution for each repository.
# Usage: python github_actions_cost_viewer.py {csv_filename} {target month YYYY/M}
# Notes:
#   * there could be an error of $0.01 between total cost and distribution
#   * the csv format is as of November 2020

import os
import argparse
import csv
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

FREE_TIER = {'shared storage': 50,  # GB
             'actions': 50000}      # min/month

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

def create_pileup_figure(dataframe, subject, vertical=False, transpose=False):
    fig, ax = plt.subplots(figsize=(10, 8))
    dataframe = dataframe.sort_index()
    if transpose:
        dataframe = dataframe.transpose()
    for i in range(len(dataframe)):
        if vertical:
            ax.barh(dataframe.columns, dataframe.iloc[i], left=dataframe.iloc[:i].sum(), label=dataframe.index[i])
            plt.ylabel(subject)
            plt.xlabel('Cost($)')
        else:
            ax.bar(dataframe.columns, dataframe.iloc[i], bottom=dataframe.iloc[:i].sum(), label=dataframe.index[i])
            plt.ylabel('Cost($)')
            plt.xlabel(subject)
    ax.set_title(subject)
    ax.tick_params(labelsize=min(500//len(dataframe.columns),10))
    plt.legend(loc='best')
    plt.tight_layout()
    plt.grid(b=True, which='major', color='#999999', linestyle='--', alpha=0.2)
    #plt.show()
    plt.savefig('output' + os.sep + subject.lower() + '.png')

def get_cost_bar_graph_pile(data, colmn_name, pile_index, subject, vertical=False, transpose=False):
    dataset = {}
    pile_columns = []
    for d in data:
        dataset.setdefault(d[colmn_name], {})
        if d[pile_index] in dataset[d[colmn_name]]:
            dataset[d[colmn_name]][d[pile_index]] += float(d['Quantity'])*float(d['Price Per Unit'][1:])
        else:
            dataset[d[colmn_name]][d[pile_index]] = float(d['Quantity'])*float(d['Price Per Unit'][1:])
            if d[pile_index] not in pile_columns:
                pile_columns.append(d[pile_index])
    df = pd.DataFrame(index=dataset.keys(), columns=pile_columns)
    for d in dataset:
        df.loc[d] = dataset[d]
    create_pileup_figure(df, subject, vertical=vertical, transpose=transpose)
    return dataset

def get_cost_bar_braph_for_repo(data, colmn_name, pile_index, subject, vertical=False, transpose=False):
    repositories = {}
    for d in data:
        if d['Repository Slug'] not in repositories:
            repositories[d['Repository Slug']] = [d]
        else:
            repositories[d['Repository Slug']].append(d)
    for r in repositories:
        os.makedirs('output' + os.sep + r, exist_ok=True)
        repo_subject = r + os.sep + subject
        get_cost_bar_graph_pile(repositories[r], colmn_name, pile_index, repo_subject, vertical=vertical, transpose=transpose)

def get_tier(data, products):
    # only for ubuntu
    dataset = {}
    unit_price = {}
    for p in products:
        dataset[p] = 0
    for d in data:
        dataset[d['Product']] += float(d['Quantity'])
        if d['Product'] not in unit_price:
            unit_price[d['Product']] = float(d['Price Per Unit'][1:])
    return dataset, unit_price

def my_round(float_num):
    d = Decimal(str(float_num)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return d

def show_payment(tier, unit_price, repo_cost):
    # free tier usage rate
    print('[FREE TIER USEGE RATE]')
    for t in tier:
        if FREE_TIER[t] != 0:
            print('  ' + t + ': ' + str(tier[t]*100 // FREE_TIER[t]) + '%')
        else:
            print('  ' + t + ': no free tier')
    # calc distribution
    distribution = {}
    total_payment = {}
    for t in tier:
        if tier[t] > FREE_TIER[t]:
            total_payment.setdefault(t, (tier[t] - FREE_TIER[t]) * unit_price[t])
            for rc in repo_cost:
                distribution.setdefault(rc, {})
                if t in repo_cost[rc]:
                    distribution[rc].setdefault(t, repo_cost[rc][t] * total_payment[t] / (tier[t] * unit_price[t]))
                else:
                    distribution[rc].setdefault(t, 0)
    print('[TOTAL PAYMENT]: $' + str(my_round(sum(total_payment.values()))))
    for p in total_payment:
        print('  [' + p + ']: $' + str(my_round(total_payment[p])))
    if my_round(sum(total_payment.values())) > 0:
        print('[Details]: ')
        for r in distribution:
            print('  [' + r + ']: $' + str(my_round(sum(distribution[r].values()))))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='target csv filename')
    parser.add_argument('month', help='target month YYYY/M')
    args = parser.parse_args()
    
    with open(args.filename) as f:
        reader = csv.reader(f)
        raw_data = [row for row in reader]

    titles = raw_data.pop(0)
    data = []
    for row in raw_data:
        is_target = True
        row_dict = {}
        for i,item in enumerate(row):
            if titles[i] == 'Date':  # for sort
                if item.startswith(args.month):
                    item = str(datetime.strptime(item, '%Y/%m/%d'))[5:10]
                else:
                    is_target = False
            if titles[i] == 'Repository Slug':  # for shorten
                item = item.split('/')[1]
            row_dict[titles[i]] = item
        if is_target:
            data.append(row_dict)
    
    os.makedirs('output', exist_ok=True)
    get_cost_bar_graph_pile(data, 'Product', 'Repository Slug', 'Product', True, True)
    repo_cost = get_cost_bar_graph_pile(data, 'Repository Slug', 'Product', 'Repository', True, True)
    get_cost_bar_braph_for_repo(data, 'Actions Workflow', 'Product', 'Workflow', True, True)
    get_cost_bar_braph_for_repo(data, 'Date', 'Product', 'Date', True, True)
    tier, unit_price = get_tier(data, FREE_TIER.keys())
    show_payment(tier, unit_price, repo_cost)