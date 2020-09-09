# portfolio-viewer
Simple python script to visualize stock portfolio performance over time and to plot hypothetical trades.

# Required Packages
matplotlib
dataclasses
click

# Capabilities


# Running the Example
I've provided a couple portfolio files in the `example` folder. From the root of this repository, try running the following command (once you've installed the required packages):

```
python main.py 4500 example/portfolio-1.json example/portfolio-2.json example/portfolio-3.json example/portfolio-4.json example/portfolio-5.json example/portfolio-6.json -s 2020-3-10 -e 2020-8-31 --save_dir example
```