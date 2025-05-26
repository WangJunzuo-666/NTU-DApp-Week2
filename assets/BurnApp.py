from web3 import Web3
from web3.exceptions import BlockNotFound
import matplotlib.pyplot as plt
import json

# 配置参数
INFURA_URL = "https://mainnet.infura.io/v3/daaf957ba6a04ff392fed885d92cc3e3"
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# 检查连接
if not web3.is_connected():
    raise ConnectionError("无法连接到以太坊主网，请检查您的 Infura URL")

# Uniswap V3 池地址和 ABI
POOL_ADDRESS = "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"
POOL_ABI = '[...]'  # 请替换为 Uniswap V3 池的 ABI

# 加载合约
pool_contract = web3.eth.contract(address=POOL_ADDRESS, abi=POOL_ABI)

# 配置区块范围
START_BLOCK = 17618642
END_BLOCK = 17618742
TICK_LOWER = 200540
TICK_UPPER = 200560

# 获取区块数据
try:
    start_block = web3.eth.get_block(START_BLOCK)
    end_block = web3.eth.get_block(END_BLOCK)
except BlockNotFound as e:
    raise ValueError(f"无法找到指定的区块：{e}")

# 获取区块时的流动性
def get_liquidity_at_block(block_number):
    try:
        liquidity = pool_contract.functions.liquidity().call(block_identifier=block_number)
        return liquidity
    except Exception as e:
        raise ValueError(f"获取流动性失败：{e}")

# 获取 tick 的流动性分布
def get_liquidity_distribution():
    tick_data = {}
    for tick in range(200530, 200581):
        try:
            liquidity = pool_contract.functions.ticks(tick).call(block_identifier=START_BLOCK)
            tick_data[tick] = liquidity[0]  # 假设第一个返回值是流动性
        except Exception as e:
            tick_data[tick] = 0
    return tick_data

# 获取手续费分布
def get_fee_distribution():
    fee_data = {}
    for tick in range(200530, 200581):
        try:
            fee_growth = pool_contract.functions.ticks(tick).call(block_identifier=END_BLOCK)
            fee_data[tick] = fee_growth[1]  # 假设第二个返回值是手续费增长
        except Exception as e:
            fee_data[tick] = 0
    return fee_data

# 计算头寸的 USDC 和 WETH 余额
def calculate_position_balance(liquidity, tick_lower, tick_upper):
    usdc_balance = 0
    weth_balance = 0
    for tick in range(tick_lower, tick_upper + 1):
        weight = liquidity.get(tick, 0)
        usdc_balance += weight * 0.5  # 假设 50% 是 USDC
        weth_balance += weight * 0.5  # 假设 50% 是 WETH
    return usdc_balance, weth_balance

# 绘制流动性分布图
def plot_liquidity_distribution(liquidity_data):
    ticks = list(liquidity_data.keys())
    liquidity = list(liquidity_data.values())

    plt.figure(figsize=(10, 6))
    plt.bar(ticks, liquidity, color='blue', alpha=0.6, label='Total Liquidity')
    plt.xlabel("Tick Number")
    plt.ylabel("Liquidity")
    plt.title("Liquidity Distribution at Block 17618642")
    plt.legend()
    plt.show()

# 绘制手续费分布图
def plot_fee_distribution(fee_data):
    ticks = list(fee_data.keys())
    fees = list(fee_data.values())

    plt.figure(figsize=(10, 6))
    plt.bar(ticks, fees, color='green', alpha=0.6, label='Fee Distribution')
    plt.xlabel("Tick Number")
    plt.ylabel("Fees Accumulated")
    plt.title("Swap Fee Distribution from Block 17618642 to 17618742")
    plt.legend()
    plt.show()

# 主程序
if __name__ == "__main__":
    # 获取流动性分布
    liquidity_data = get_liquidity_distribution()
    plot_liquidity_distribution(liquidity_data)

    # 获取手续费分布
    fee_data = get_fee_distribution()
    plot_fee_distribution(fee_data)

    # 计算头寸余额
    usdc_balance, weth_balance = calculate_position_balance(liquidity_data, TICK_LOWER, TICK_UPPER)
    print(f"USDC Balance: {usdc_balance}, WETH Balance: {weth_balance}")
