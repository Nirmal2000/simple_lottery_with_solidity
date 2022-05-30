from operator import ne
import time
from pkg_resources import load_entry_point
from scripts.utils import get_account, get_contract, fund_with_link
from dotenv import load_dotenv
load_dotenv()

from brownie import Lottery, network, config


def deploy_lotr():
    account = get_account(index=0)
    lottery = Lottery.deploy(
        get_contract("eth_usd_pf").address,
        get_contract('vrf_coordinator').address,
        get_contract('link_token').address,
        config['networks'][network.show_active()]['fee'],
        config['networks'][network.show_active()]['keyhash'],
        {'from': account},
        publish_source = config['networks'][network.show_active()].get('verify', False),
    )
    print("Deployed lottery")
    return lottery
    
def start_lotter():
    account = get_account(index=0)
    lottery = Lottery[-1]
    lottery.startLotr({'from':account}).wait(1)
    print("lotr started")

def enter_lotr():
    account = get_account(index=0) 
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({'from':account, "value":value})
    tx.wait(1)
    print("entered !!")

def endLotr():
    account = get_account(index=0) 
    lottery = Lottery[-1]
    fund_with_link(lottery.address)

    end_txn = lottery.endLotr({'from':account})
    end_txn.wait(1)
    time.sleep(30)
    print(F"{lottery.recentWinner()} is the winner")



def main():
    deploy_lotr()
    start_lotter()
    enter_lotr()
    endLotr()