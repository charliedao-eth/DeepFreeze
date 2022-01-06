from attr import Factory
from brownie import DeepFreezeFactory, config, network
from scripts.helpful_scripts import get_account


def main():
    deploy_DeepFreeze()


def deploy_DeepFreeze():
    account = get_account()
    DeepFreezeFactory.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
