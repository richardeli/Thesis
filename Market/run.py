from systembook import SystemBook

def test_book():
    for num_sims in range(1):
        for num_runs in range(1000):
            sys = SystemBook(num_init_fundamentalists=100, num_init_speculators=100, init_upward_market_dir=False, 
                            num_trade_cycles=10, chg_num_agent_pcycle=10, cycle_cool_off_per_dilution=1, 
                            fund_dilute_rm=False, change_dilution_dir_cycle_num=None)
            sys.trade_cycle()
            # sys.output_graph()
            # sys.save_to_excel(num_sims+1, num_runs+1)
            sys.save_per_simulation_excel(num_sims+1, num_runs+1)
        
if __name__ == '__main__':
    test_book()