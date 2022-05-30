from ctypes import util
from black import get_cache_info
from brownie import Lottery, accounts
import pytest
from scripts.deploy_lotr import deploy_lotr
from scripts import utils
from web3 import Web3
from brownie import network, exceptions ##this one 

def test_get_entrae_fee():
    if network.show_active() not in utils.LOCAL_BC_ENV:
        pytest.skip()
    account = accounts[0]
    lottery = deploy_lotr()

    #inint 2000usd / eth
    #entry fee 50
    # so 0.025
    entrance_fee =lottery.getEntranceFee()
    exp_ent_fee = Web3.toWei(0.025, 'ether')
    assert exp_ent_fee == entrance_fee

## exception.VirtualMachineError

def test_can_pick_winner():

    if network.show_active() not in utils.LOCAL_BC_ENV:
        pytest.skip()
    account = utils.get_account(index=0)
    lottery = deploy_lotr()
    lottery.startLotr({'from': account})

    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': utils.get_account(index=1), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': utils.get_account(index=2), 'value': lottery.getEntranceFee()})
    
    utils.fund_with_link(lottery)

    txn = lottery.endLotr({'from':account})
    req_id = txn.events['RequestRandomness']['requestId']
    STATIC_RNG = 777
    starting_bal = account.balance()
    bal_lotr = lottery.balance()
    utils.get_contract('vrf_coordinator').callBackWithRandomness(req_id, STATIC_RNG, lottery.address, {'from':account})
    # print(lottery.recentWinner)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

    assert account.balance() == starting_bal + bal_lotr
