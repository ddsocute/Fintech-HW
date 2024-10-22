def myStrategy(pastPriceVec, currentPrice):
    import numpy as np

    action = 0  # 預設動作為保持不動

    # 最佳參數
    rsiPeriod = 24
    overboughtThreshold = 85
    oversoldThreshold = 20

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
