from os import link
from brownie import network, accounts, config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract, interface
from web3 import Web3

LOCAL_BC_ENV = ['development', 'ganache-local']

def get_account(index=None, id=None):
    if index is not None:        
        return accounts[index]
    if network.show_active() in LOCAL_BC_ENV:
        account = accounts[0]
    return accounts.add(config['wallets']['from_key'])
    
contract_to_mock = {
    "eth_usd_pf": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}

def get_contract(contract_name):
    "get cont add if in config else deploy mocks"
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BC_ENV:
        if len(contract_type) == 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config['networks'][network.show_active()][contract_name]
        
        #this is how to get contract
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

def deploy_mocks():
    account = get_account()
    print("deploying mocks...")    
    MockV3Aggregator.deploy(18, Web3.toWei(2000, 'ether'), {'from':account})
    lk = LinkToken.deploy({'from':account})
    VRFCoordinatorMock.deploy(lk.address, {'from':account})
    print("deployed mocks...") 

def fund_with_link(contract_addr, account=None, link_token=None, amount=100000000000000000): #0.1 link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract('link_token')
    tx = link_token.transfer(contract_addr, amount, {'from': account})
    # link_tkn_crt = interface.LinkTokenInterface(link_token.address)
    # link_tkn_crt.transfer(contract_addr, amount, {'from': account})
    tx.wait(1)



    
        