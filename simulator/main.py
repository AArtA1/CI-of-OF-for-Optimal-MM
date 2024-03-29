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

stocks_quantity = 4

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
    *[Random(exchanges[randint(0, stocks_quantity - 1)])         for _ in range(700)],
    *[Fundamentalist(exchanges[randint(0, stocks_quantity - 1)]) for _ in range(700)],
    *[Chartist1D(exchanges[randint(0, stocks_quantity - 1)])         for _ in range(700)],
    *[Chartist2D(exchanges)                    for _ in range(200)],
    *[MarketMaker2D(exchanges)                 for _ in range(100)]
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
        #"obi":lambda:plot_orderbook_imbalance(info, show=True,level = 10),
        "timb":lambda:plot_trade_imbalance(info, delta = 3, show = True),
        "obi_1":lambda:plot_orderbook_imbalance(info,show = True, level = 3),
        #"obi_2":lambda:plot_orderbook_imbalance(info,show = True, level = 2),    
        "price":lambda:plot_price(info, show = True, spread=False)
    }


    # for i in range(10):
    #    metrics[f'obi_level_{i+1}'] = lambda i = i:plot_orderbook_imbalance(info,show = True, level = i+1)

    # for i in range(10):
    #     metrics[f'tfi_delta_{i}'] = lambda i = i:plot_trade_imbalance(info,delta = i+1,show = True)

    #metrics.update(obi_levels)

    for metric, func in metrics.items():
        dataset = func()
        #dataset.to_csv(f'dataset/{metric}_{iteration}.csv')         
        dataset.to_csv(f'dataset/{metric}.csv')         

if __name__ == "__main__":
    for i in range(datasets_quantity):
            
        # changing seed to generate various datasets with same parameters
        # settings.random = randint(1, 10000) 

        info = simulate()
            
        collect_save_dataset(info, i)
        # Save generated synthetic datasets           
            