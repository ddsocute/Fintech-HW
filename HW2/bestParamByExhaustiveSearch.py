import pandas as pd
import numpy as np

# 讀取價格資料
df = pd.read_csv('Price 3000 Open.csv', skiprows=1, names=['Date', 'Adj Close'], parse_dates=['Date'])
df.set_index('Date', inplace=True)
priceVec = df['Adj Close'].values  # 價格向量，用於測試

# 定義策略函數
def myStrategy(pastPriceVec, currentPrice, rsiPeriod, overboughtThreshold, oversoldThreshold):
    import numpy as np

    action = 0  # 預設動作為保持不動

    # 確保有足夠的歷史數據
    if len(pastPriceVec) < rsiPeriod + 1:
        return action

    # 計算 RSI
    deltas = np.diff(pastPriceVec[-(rsiPeriod + 1):])
    gains = deltas[deltas >= 0]
    losses = -deltas[deltas < 0]
    avg_gain = gains.sum() / rsiPeriod if len(gains) > 0 else 0
    avg_loss = losses.sum() / rsiPeriod if len(losses) > 0 else 0

    if avg_loss == 0:
        RSI = 100
    else:
        rs = avg_gain / avg_loss
        RSI = 100 - (100 / (1 + rs))

    # 判斷買賣信號
    if RSI < oversoldThreshold:
        action = 1  # 建議買入
    elif RSI > overboughtThreshold:
        action = -1  # 建議賣出

    return action

# 定義回報率評估函數
def rrEstimate(priceVec, rsiPeriod, overboughtThreshold, oversoldThreshold):
    capital = 1000  # 初始資金
    capitalOrig = capital
    dataCount = len(priceVec)
    stockHolding = 0  # 初始持股數量
    totalAsset = np.zeros(dataCount)

    for ic in range(dataCount):
        currentPrice = priceVec[ic]
        pastPriceVec = priceVec[0:ic]

        # 呼叫策略函數
        action = myStrategy(pastPriceVec, currentPrice, rsiPeriod, overboughtThreshold, oversoldThreshold)

        # 模擬交易行為
        if action == 1 and stockHolding == 0:
            # 買入
            stockHolding = capital / currentPrice
            capital = 0
        elif action == -1 and stockHolding > 0:
            # 賣出
            capital = stockHolding * currentPrice
            stockHolding = 0

        # 更新總資產
        totalAsset[ic] = capital + stockHolding * currentPrice

    returnRate = (totalAsset[-1] - capitalOrig) / capitalOrig
    return returnRate

# 參數最佳化
bestReturn = -np.inf
bestRsiPeriod = None
bestOverboughtThreshold = None
bestOversoldThreshold = None

# 定義要測試的參數範圍
rsiPeriodRange = range(6, 25, 2)            # RSI 計算週期：6、8、10、...、24
overboughtThresholdRange = range(65, 86, 5) # 超買閾值：65、70、75、80、85
oversoldThresholdRange = range(15, 36, 5)   # 超賣閾值：15、20、25、30、35

print("開始測試不同的 RSI 策略參數組合...\n")
for rsiPeriod in rsiPeriodRange:
    for overboughtThreshold in overboughtThresholdRange:
        for oversoldThreshold in oversoldThresholdRange:
            if overboughtThreshold <= oversoldThreshold:
                continue  # 確保超買閾值大於超賣閾值

            rr = rrEstimate(priceVec, rsiPeriod, overboughtThreshold, oversoldThreshold)
            print(f"RSI 週期: {rsiPeriod}, 超買閾值: {overboughtThreshold}, 超賣閾值: {oversoldThreshold}, 回報率: {rr * 100:.2f}%")

            if rr > bestReturn:
                bestReturn = rr
                bestRsiPeriod = rsiPeriod
                bestOverboughtThreshold = overboughtThreshold
                bestOversoldThreshold = oversoldThreshold

print(f"\n最佳 RSI 週期: {bestRsiPeriod}, 最佳超買閾值: {bestOverboughtThreshold}, 最佳超賣閾值: {bestOversoldThreshold}, 最高回報率: {bestReturn * 100:.2f}%")
