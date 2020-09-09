# portfolio-viewer
Simple python script to visualize stock portfolio performance over time and to plot hypothetical trades.

# Required Packages
matplotlib
dataclasses
click

# Capabilities


# Running the Example
I've provided a couple transaction files in the `example` folder. From the root of this repository, try running the following command (once you've installed the required packages):

Single portfolio:
```
python main.py 4500 example/transactions.txt -s 2020-3-10 -e 2020-8-31
```

Multiple portfolios:
```
python main.py 4500 example/transactions.txt example -h example/hypothetical-transactions-1.txt -h example/hypothetical-transactions-2.txt -h example/hypothetical-transactions-3.txt -h example/hypothetical-transactions-4.txt -h example/hypothetical-transactions-5.txt -h example/hypothetical-transactions-6.txt -s 2020-3-10 -e 2020-8-31
```