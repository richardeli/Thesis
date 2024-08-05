from systembook import SystemBook

def test_book():
    sys = SystemBook(num_init_agents=25, initial_market_correction_dir=1, num_trade_cycles=50, chg_num_agent_pcycle=1,fundamentalist_dilution=1)
    sys.trade_cycle()
    
if __name__ == '__main__':
    test_book()