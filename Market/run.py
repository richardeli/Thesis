from systembook import SystemBook

def test_book():
    sys = SystemBook(num_init_agents=25, init_upward_market_dir=False, num_trade_cycles=75, chg_num_agent_pcycle=1,fund_dilute_rm=True, change_dilution_dir_cycle_num=25)
    sys.trade_cycle()
    
if __name__ == '__main__':
    test_book()