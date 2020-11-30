# GitHub Actions Billing Visualizer

Visualize github actions billing and calc billing distribution for each repository.

## Demo

Graph of Cost by Repository. 

<img src="https://github.com/kusuwada/github_actions_billing_visualizer/raw/image/image/repository.png" width="400">

Daily Cost graph for each repository

<img src="https://github.com/kusuwada/github_actions_billing_visualizer/raw/image/image/date.png" width="400">

Cost graph per repository/workflow

<img src="https://github.com/kusuwada/github_actions_billing_visualizer/raw/image/image/workflow.png" width="400">

## Usage

### Prepare Billing csv for GitHub Actions

See below and get your Organization or Enterprize Billing csv.  
[Viewing GitHub Actions usage for your organization](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-billing-and-payments-on-github/viewing-your-github-actions-usage#viewing-github-actions-usage-for-your-organization)

or, create sample csv.

```
$ git clone git@github.com:kusuwada/github_actions_billing_visualizer.git
$ cd github_actions_billing_visualizer
$ pip install -r requirements.txt
$ python generate_sample.py {output_filename.csv} {target month YYYY/M}
```

### Generate graphs and calculate Billing distribution

```
$ git clone git@github.com:kusuwada/github_actions_billing_visualizer.git
$ cd github_actions_billing_visualizer
$ pip install -r requirements.txt
$ python github_actions_cost_viewer.py {target_filename.csv} {target month YYYY/M}
```

Then, you can get charts and results as below.

```
output/
├── product.png
├── repo-camel
│   ├── date.png
│   └── workflow.png
├── repo-cat-dog
│   ├── date.png
│   └── workflow.png
...
└── repository.png
```

Execution sample:

```
$ python github_actions_cost_viewer.py sample_actions.csv 2020/12
[FREE TIER USEGE RATE]
  shared storage: 135.0%
  actions: 56.0%
[TOTAL PAYMENT]: $4.43
  [shared storage]: $4.43
[Details]: 
  [repo-rabbit]: $0.00
  [repo-panda]: $2.06
  [repo-cat-dog]: $0.32
  [repo-camel]: $0.00
  [repo-elephant]: $2.05
```

## Limitation

* There could be an error of $0.01 between billing cost and sum of thee distribution.
* The csv format is as of November 2020.
* You can use also [GitHub Actions API.](https://docs.github.com/en/free-pro-team@latest/rest/reference/actions)