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

datasets_quantity = 10

stocks_quantity = 10

simulator_iterations = 500

risk_free_rate = 5e-4
        
price = 100
        
dividend = price * risk_free_rate


def simulate() -> SimulatorInfo:
    # Initialization of stocks
    assets = [
        Stock(dividend) for _ in range(10)
    ]

    # Exchange agent (intermediary between market and customer)
    exchanges = [
        ExchangeAgent(assets[i], risk_free_rate) for i in range(stocks_quantity) #for x in range(10)   # single asset
    ]

    # Market customers
    traders = [
        *[Random(exchanges[randint(0, 2)])         for _ in range(20)],
        *[Fundamentalist(exchanges[randint(0, 2)]) for _ in range(20)],
        *[Chartist2D(exchanges)                    for _ in range(20)],
        *[MarketMaker2D(exchanges)                 for _ in range(4)]
    ]

    # Run simulation
    simulator = Simulator(**{
        'assets': assets,
        'exchanges': exchanges,
        'traders': traders,
        'events': [MarketPriceShock(0, 200, -10)]
    })

    info = simulator.info

    simulator.simulate(simulator_iterations, silent=False)

    return info
      

def collect_save_dataset(info: SimulatorInfo, iteration: int):
    metrics = {
        "gain": lambda:plot_gain(info, left_iter=1, right_iter=simulator_iterations),
        "spread":lambda:plot_spread(info, left_iter=1, right_iter=simulator_iterations),
        "obi":lambda:plot_orderbook_imbalance(info),
        "timb":lambda:plot_trade_imbalance(info, left_iter=1, right_iter=simulator_iterations)
    }

    filepath = Path('../dataset')
    filepath.mkdir()

    for metric, func in metrics.items():
        dataset = func()
        dataset.to_csv(f'../dataset/{metric}_{iteration}.csv')         

if __name__ == "__main__":
    for i in range(datasets_quantity):
            
        # changing seed to generate various datasets with same parameters 
        settings.random = randint(1, 10000)

        info = simulate()
            
        collect_save_dataset(info, i)
        # Save generated synthetic datasets           
            

plot_gain(info, left_iter=1, right_iter=500)

res = plot_spread(info, left_iter=1 , right_iter=500)

res.to_csv('output.csv')