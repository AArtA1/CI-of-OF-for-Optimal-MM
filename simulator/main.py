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

import random


random.seed(settings.seed) 

# Some Useful Definitions 

# I hope I will add them later

# Exchange agent - 

# Define parameters
risk_free_rate = 5e-4
price = 100
dividend = price * risk_free_rate

# Initialize objects

# Initialization of stocks
assets = [
    Stock(dividend) for _ in range(10)
]

# Exchange agent (intermediary between market and customer)
exchanges = [
    ExchangeAgent(assets[i], risk_free_rate) for i in range(10) #for x in range(10)   # single asset
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
simulator.simulate(500, silent=False)

#plot_liquidity(info,None, rolling = 1)


# print(len(info.orders[0]))

# print(type(info.exchanges[0]))

# print(len(info.exchanges))

#print(info.orders[0][0])

#plot_orderbook_imbalance(info, 0, rolling = 1)

#plot_trade_imbalance(info,idx=0,left_iter=1,right_iter=100)

#plot_orderbook_imbalance(info, idx=0)

#plot_gain(info,idx=0,left_iter=1,right_iter=500)

#plot_spread(info,idx = 0, left_iter=1,right_iter=10)

#plot_spread(info,idx = 0, left_iter=1, right_iter=10)

#plot_price(info, idx = 0, rolling=1)

plot_gain(info, left_iter=1, right_iter=500)

res = plot_spread(info, idx = 1 , left_iter=1 , right_iter=500)

res.to_csv('output.csv')