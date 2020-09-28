# portfolio-viewer
A small python program to analyze and compare an arbitrary number of user-defined stock portfolios over time. Fetches stock data from the `Yahoo! Finance` website (and therefore requires an internet connection to run). Uses the [click](https://click.palletsprojects.com/en/7.x/) library to implement the command-line interface, and [matplotlib](https://matplotlib.org/) for plotting data.

![Plot comparing example portfolios over time](https://user-images.githubusercontent.com/8965354/94437178-64d8f280-016b-11eb-9f13-ed244dbd95d2.jpg)

Written and tested in python 3.6.4.

# Capabilities
- Nice command-line interface
- Scrapes and uses stock data from `Yahoo! Finance` (shhhh... don't tell anyone)
- Calculates and plots value-over-time for each portfolio
- Calculates return-per-stock data for each portfolio
- Conveniently saves data for each portfolio into its own directory 
- Can handle and compare an arbitrary number of portfolios
- Code is documented and fully type-hinted

# Running the Example
I've provided a couple portfolio files in the `example` folder. From the root of this repository, do the following:

## Setup Virtual Environment
Use the [python venv tool](https://docs.python.org/3/library/venv.html) to set up a new virtual environment:
```
python3 -m venv portfolio-env
```

Activate the environment:
```
portfolio-env\Scripts\activate.bat (Windows)
source portfolio-env/scripts/activate.sh (Linux)
```

Install the requirements:
```
pip install -r requirements.txt
```

Run the program on one example portfolio. Set start- and end-dates `March 10, 2020` to `August 31, 2020`. Save all created files to the `results-one` directory:
```
python main.py 4500 example/portfolio-1.json -s 2020-3-10 -e 2020-8-31 --save_dir results-one
```

Run the program on all example portfolios. Set start- and end-dates `March 10, 2020` to `August 31, 2020`. Save all created files to the `results-all` directory:
```
python main.py 4500 example/portfolio-1.json example/portfolio-2.json example/portfolio-3.json example/portfolio-4.json example/portfolio-5.json example/portfolio-6.json -s 2020-3-10 -e 2020-8-31 --save_dir results-all
```
