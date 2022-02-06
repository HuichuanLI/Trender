# -*- coding:utf-8 -*-
# @Time : 2022/2/5 10:04 下午
# @Author : huichuan LI
# @File : strategy.py
# @Software: PyCharm
import data.stock as st
import numpy as np
import datetime
import matplotlib.pyplot as plt
import pandas as pd


def compose_signal(data):
    """
    整合信号
    :param data:
    :return:
    """
    data['buy_signal'] = np.where((data['buy_signal'] == 1)
                                  & (data['buy_signal'].shift(1) == 1), 0, data['buy_signal'])
    data['sell_signal'] = np.where((data['sell_signal'] == -1)
                                   & (data['sell_signal'].shift(1) == -1), 0, data['sell_signal'])
    data['signal'] = data['buy_signal'] + data['sell_signal']
    return data


def calculate_prof_pct(data):
    """
    计算单次收益率：开仓、平仓（开仓的全部股数）
    :param data:
    :return:
    """
    data.loc[data['signal'] != 0, 'profit_pct'] = (data['close'] - data['close'].shift(1)) / data['close'].shift(1)
    data = data[data['signal'] == -1]
    return data


def calculate_cum_prof(data):
    """
    计算累计收益率
    :param data: dataframe
    :return:
    """
    data['cum_profit'] = pd.DataFrame(1 + data['profit_pct']).cumprod() - 1
    return data


def week_period_strategy(code, time_freq, start_date, end_date):
    """
    周期选股（周四买，周一卖）
    :param code:
    :param time_freq:
    :param start_date:
    :param end_date:
    :return:
    """
    data = st.get_single_price(code, time_freq, start_date, end_date)
    # 新建周期字段
    data['weekday'] = data.index.weekday
    # 周四买入
    data['buy_signal'] = np.where((data['weekday'] == 3), 1, 0)
    # 周一卖出
    data['sell_signal'] = np.where((data['weekday'] == 0), -1, 0)

    data = compose_signal(data)  # 整合信号
    data = calculate_prof_pct(data)  # 计算收益
    data = calculate_cum_prof(data)  # 计算累计收益率
    data = caculate_max_drawdown(data)  # 最大回撤
    return data


def caculate_max_drawdown(data):
    """
    计算最大回撤比
    :param data:
    :return:
    """
    # 选取时间周期（时间窗口）
    window = 252
    # 选取时间周期中的最大净值
    data['roll_max'] = data['close'].rolling(window=window, min_periods=1).max()
    # 计算当天的回撤比 = (谷值 — 峰值)/峰值 = 谷值/峰值 - 1
    data['daily_dd'] = data['close'] / data['roll_max'] - 1
    # 选取时间周期内最大的回撤比，即最大回撤
    data['max_dd'] = data['daily_dd'].rolling(window, min_periods=1).min()
    return data


def calculate_sharpe(data):
    """
    计算夏普比率，返回的是年化的夏普比率
    :param data: dataframe, stock
    :return: float
    """
    # 公式：sharpe = (回报率的均值 - 无风险利率) / 回报率的标准差
    daily_return = data['close'].pct_change()
    avg_return = daily_return.mean()
    sd_reutrn = daily_return.std()
    # 计算夏普：每日收益率 * 252 = 每年收益率
    sharpe = avg_return / sd_reutrn
    sharpe_year = sharpe * np.sqrt(252)
    return sharpe, sharpe_year


if __name__ == '__main__':
    # stocks = [
    #     {'name': '平安银行', 'code': '000001.XSHE'},
    #     {'name': '宏华数科', 'code': '688789.XSHG'},
    #     {'name': '苑东生物', 'code': '688513.XSHG'}
    # ]
    # df_cum_profit = pd.DataFrame()
    #
    # for stock in stocks:
    #     df = week_period_strategy(stock['code'], 'daily', '2021-07-12', datetime.date.today())
    #     df_cum_profit[stock['name']] = df['cum_profit']
    #
    # print(df_cum_profit)
    # print(df_cum_profit.describe())
    # df_cum_profit.plot()
    # # plt.rcParams['font.family'] = ['SimHei']  # 需要安装配置中文字体
    # # plt.rcParams['axes.unicode_minus'] = False
    # # plt.title('周期策略下(周四买入周一卖出)三支股票的累计收益率')
    # plt.show()

    # 查看平安银行最大回撤
    df = st.get_single_price('000001.XSHE', 'daily', '2006-01-01', '2022-01-01')
    df = caculate_max_drawdown(df)
    print(df[['close', 'roll_max', 'daily_dd', 'max_dd']])
    df[['daily_dd', 'max_dd']].plot()
    plt.show()


    #计算夏普比率
    df = st.get_single_price('000001.XSHE', 'daily', '2006-01-01', '2021-01-01')
    sharpe = calculate_sharpe(df)
    print(sharpe)
