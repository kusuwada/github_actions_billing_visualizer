#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Generate sample github actions billing csv for 1 month.
# Usage: python generate_sample.py {output_filename} {target month YYYY/M}

import csv
import argparse
import yaml
import random
from datetime import datetime

class ActionsRecord():
    def __init__(self, date, product, repo, quantity, unittype, ppu, workflow):
        self.date = date
        self.product = product
        self.repo = repo
        self.quantity = quantity
        self.unittype = unittype
        self.ppu = ppu  # price per unit
        self.workflow = workflow
        
def generate_day(month, date):
    return month + str(date)

def generate_random_quantity(q_min, q_max):
    return random.uniform(q_min, q_max)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='output csv filename')
    parser.add_argument('month', help='target month YYYY/M')
    args = parser.parse_args()
    
    with open('repo_sample.yaml', 'r') as f:
        repos = yaml.safe_load(f)
    
    records = []
    records.append(['Date', 'Product', 'Repository Slug', 'Quantity', 'Unit Type', 'Price Per Unit', 'Actions Workflow'])
    
    for repo, workflows in repos.items():
        for wf, coeff in workflows.items():
            storage_total = 0.0000
            for date in range(30):
                # actions
                r_actions = ActionsRecord(
                                generate_day(args.month + '/', date+1),
                                'actions',
                                'MyCorporation/repo-' + repo,
                                int(generate_random_quantity(0, coeff[0]*100)),
                                'UBUNTU',
                                '$0.01',
                                '.github/workflows/' + wf)
                if r_actions.quantity != 0:
                    records.append(r_actions.__dict__.values())
                # shared storage
                r_storage = ActionsRecord(
                                generate_day(args.month+ '/', date+1),
                                'shared storage',
                                'MyCorporation/repo-' + repo,
                                round(storage_total + generate_random_quantity(0, coeff[1]*0.01),4),
                                'gb',
                                '$0.25',
                                '')
                if r_storage.quantity != 0:
                    records.append(r_storage.__dict__.values())
                storage_total = r_storage.quantity

    
    with open(args.filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(records)