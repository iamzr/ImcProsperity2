# IMC Prosperity 2

This repository contains my work for the algorithmic trading segment of the IMC Prosperity 2 trading challenge.

## Table of Contents
1. [Useful Links](#useful-links)
2. [Installation](#installation)
3. [Usage](#usage)

## Useful Links
- [IMC Prosperity 2 Wiki](https://imc-prosperity.notion.site/Prosperity-2-Wiki-fe650c0292ae4cdb94714a3f5aa74c85) 

    Comprehensive resource for the competition, including details about the rounds, problems, and all necessary information to create a trader.

- [Backtester](https://github.com/jmerle/imc-prosperity-2-backtester)

    An unofficial backtester created by a fellow contestant. This tool is invaluable for testing your trading algorithms.

- [Visualizer](https://jmerle.github.io/imc-prosperity-2-visualizer/?/visualizer)

    A visualizer that, with minimal setup in your code, allows you to see how your algorithms perform during backtesting.

- [Leaderboard](https://github.com/jmerle/imc-prosperity-2-backtester)

    A leaderboard tracking the performance of individuals and teams in each round.

## Installation
To install the necessary dependencies, use the following command:

```commandline
pip install -r requirements.txt
```

This will install all packages listed in requirements.txt necessary for running the trader.

## Usage
To test your trader's performance, use the provided backtester:

```commandline
prosperity2bt trader.py <round_number>
```

### Visualizer Setup
After running a backtest, a log file will be generated in the `backtests/` directory. You can use this file with the visualizer:

1. Run the backtester using the command above.
2. Locate the generated log file in the backtests/ folder.
3. Upload the log file to the visualizer to access a detailed dashboard of your trading performance.