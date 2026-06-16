from deriv_organismo.workers.market_loop import MarketLoop


if __name__ == "__main__":
    loop = MarketLoop()
    result = loop.run_cycle()
    print(result)
