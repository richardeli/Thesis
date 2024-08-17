from systembook import SystemBook

def test_book():
    sys = SystemBook(num_init_fundamentalists=25, num_init_speculators=25, init_upward_market_dir=False, num_trade_cycles=50, chg_num_agent_pcycle=5, cycle_cool_off_per_dilution=1, fund_dilute_rm=False, change_dilution_dir_cycle_num=None)
    sys.trade_cycle()
    
if __name__ == '__main__':
    test_book()