from AgentBasedModel import *
from AgentBasedModel.extra import *
import AgentBasedModel.settings as settings
from AgentBasedModel.visualization import (
    plot_price,
    plot_price_fundamental,
    plot_liquidity,
    plot_orderbook_imbalance,
    plot_trade_imbalance,
    plot_spread,
    plot_gain
)
from random import randint
from pathlib import Path

import random

datasets_quantity = 1

stocks_quantity = 2

simulator_iterations = 1000

risk_free_rate = 5e-4
        
price = 100
        
dividend = price * risk_free_rate


assets = [
    Stock(dividend) for _ in range(stocks_quantity)
]

    # Exchange agent (intermediary between market and customer)
exchanges = [
    ExchangeAgent(assets[i], risk_free_rate) for i in range(stocks_quantity) #for x in range(10)   # single asset
]

    # Market customers
traders = [
    *[Random(exchanges[randint(0, stocks_quantity - 1)])         for _ in range(100)],
    *[Fundamentalist(exchanges[randint(0, stocks_quantity - 1)]) for _ in range(100)],
    *[Chartist1D(exchanges[randint(0, stocks_quantity - 1)])         for _ in range(100)],
    *[Chartist2D(exchanges)                    for _ in range(20)],
    *[MarketMaker2D(exchanges)                 for _ in range(4)]
]

    # Run simulation
simulator = Simulator(**{
    'assets': assets,
    'exchanges': exchanges,
    'traders': traders,
    #'events': [MarketPriceShock(0, 200, -10)]
})


def simulate() -> SimulatorInfo:
    # Initialization of stocks

    info = simulator.info

    simulator.simulate(simulator_iterations, silent=False)

    return info
      

def collect_save_dataset(info: SimulatorInfo, iteration: int):
    metrics = {
        #"gain": lambda:plot_gain(info, idx = 1, left_iter=1, right_iter=simulator_iterations, show = True),
        #"spread":lambda:plot_spread(info, idx = 1, left_iter=1, right_iter=simulator_iterations, show = True),
        #"obi":lambda:plot_orderbook_imbalance(info,idx = 1, show=True),
        #"timb":lambda:plot_trade_imbalance(info, idx = 1, delta = 1, show = True),
        "price":lambda:plot_price(info, idx = 1, show = True, spread=False)
    }

    for metric, func in metrics.items():
        dataset = func()
        dataset.to_csv(f'dataset/{metric}_{iteration}.csv')         

if __name__ == "__main__":
    for i in range(datasets_quantity):
            
        # changing seed to generate various datasets with same parameters
        # settings.random = randint(1, 10000) 

        info = simulate()
            
        collect_save_dataset(info, i)
        # Save generated synthetic datasets           
            