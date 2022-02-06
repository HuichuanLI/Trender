# -*- coding:utf-8 -*-
# @Time : 2022/2/6 4:48 下午
# @Author : huichuan LI
# @File : bull_strategy.py
# @Software: PyCharm
# -*- coding:utf-8 -*-
# @Time : 2022/2/6 3:01 下午
# @Author : huichuan LI
# @File : ma_strategy.py
# @Software: PyCharm
import data.stock as st
import strategy.base as strat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def bull_strategy(code, start_date, end_date, window):
    """
    双均线策略
    :param data: dataframe, 投资标的行情数据（必须包含收盘价）
    :param short_window: 短期n日移动平均线，默认5
    :param long_window: 长期n日移动平均线，默认20
    :return:
    """
    # 获取股票代码在指定时间段的价格数据
    data = st.get_csv_price(code, start_date, end_date)
    # 计算上(upper)、中(mid)、下(lower)轨线值
    data['std'] = data['close'].rolling(window).std()
    data['mid'] = data['close'].rolling(window).mean()
    data['upper'] = data['mid'] + 2 * data['std']
    data['lower'] = data['mid'] - 2 * data['std']
    # 生成交易信号：买入open>lower>close;卖出open<upper<close
    data['buy_signal'] = np.where((data['open'] > data['lower']) & (data['lower'] > data['close']), 1, 0)
    data['sell_signal'] = np.where((data['open'] < data['upper']) & (data['upper'] < data['close']), -1, 0)
    # 整理信号，计算收益率
    data_adj = data[
        (data['buy_signal'] != 0) |
        (data['sell_signal'] != 0)].copy()  # 去除无买卖日期的信号（compose_signl处理连续买卖信号时，要求连续的买卖信号中间不能有间隔）
    data_adj = strat.compose_signal(data_adj)  # 整理信号
    data_adj = strat.calculate_prof_pct(data_adj)  # 计算单次收益率
    data_adj = strat.calculate_cum_prof(data_adj)  # 计算累计收益率
    # 存储收益率数据，可视化bull线
    print(data_adj)
    # data_adj.to_csv('/Users/zhongbo/Desktop/data_adj.csv')
    data['upper'].plot(label='upper')
    data['mid'].plot(label='mid')
    data['lower'].plot(label='loser')
    data['close'].plot(label='close')
    plt.legend()
    plt.show()

    return data_adj


if __name__ == '__main__':
    # 股票列表
    stocks = ['000001.XSHE', '000858.XSHE', '002594.XSHE']

    # 存放累计收益率
    # cum_profits = pd.DataFrame()
    # 循环获取数据
    cum_profits = pd.DataFrame()

    for code in stocks:
        df = bull_strategy(code, '2017-01-01', '2021-08-08', 20)
        cum_profits[code] = df['cum_profit'].reset_index(drop=True)
        # 折线图
        df['cum_profit'].plot(label=code)
        # 筛选有信号点
        df = df[df['signal'] != 0]
        # 预览数据
        print("开仓次数：", int(len(df)))
        print(df[['close', 'signal', 'profit_pct', 'cum_profit']])

    print(cum_profits)
    # 可视化
    cum_profits.plot()
    plt.legend()
    plt.title('Comparison of Bull Strategy Profits')
    plt.show()
