import numpy as np

def myAction03(priceMat, transFeeRate, K):
    m, n = priceMat.shape  # 天數與股票數量
    initial_capital = 1000  # 初始資金

    # 初始化DP表
    dp = np.full((m, n + 1, K + 1), -np.inf)
    dp[0][n][1] = initial_capital

    prev = [[[None for _ in range(K + 1)] for _ in range(n + 1)] for _ in range(m)]

    # 第一天的狀態
    for j in range(n):
        dp[0][j][0] = (initial_capital * (1 - transFeeRate)) / priceMat[0][j]
        prev[0][j][0] = (n, 0, 'buy')
    prev[0][n][1] = (n, 0, 'hold')

    # 填充DP表
    for i in range(1, m):
        for j in range(n + 1):
            for k in range(K + 1):
                if j == n:
                    # 持有現金
                    if k < K:
                        if dp[i-1][j][k] > dp[i][j][k+1]:
                            dp[i][j][k+1] = dp[i-1][j][k]
                            prev[i][j][k+1] = (j, k, 'hold')
                    for l in range(n):
                        cash = dp[i-1][l][k] * priceMat[i][l] * (1 - transFeeRate)
                        if cash > dp[i][j][1]:
                            dp[i][j][1] = cash
                            prev[i][j][1] = (l, k, 'sell')
                else:
                    # 持有股票j
                    if dp[i-1][j][k] > dp[i][j][k]:
                        dp[i][j][k] = dp[i-1][j][k]
                        prev[i][j][k] = (j, k, 'hold')
                    buy_amt = dp[i-1][n][k] * (1 - transFeeRate) / priceMat[i][j]
                    if buy_amt > dp[i][j][0]:
                        dp[i][j][0] = buy_amt
                        prev[i][j][0] = (n, k, 'buy')

    # 找最大資產
    max_asset = -np.inf
    last_state = (n, K)
    for j in range(n + 1):
        for k in range(K + 1):
            asset = dp[m-1][j][k] if j == n else dp[m-1][j][k] * priceMat[m-1][j] * (1 - transFeeRate)
            if k >= K and asset > max_asset:
                max_asset = asset
                last_state = (j, k)

    # 回溯生成動作
    actions = []
    state_j, state_k = last_state
    for i in range(m-1, -1, -1):
        if state_j == n:
            prev_state, prev_k, action = prev[i][state_j][state_k]
        else:
            prev_state, prev_k, action = prev[i][state_j][state_k]
        
        if action == 'buy':
            z = dp[i-1][prev_state][prev_k] * (1 - transFeeRate)
            actions.append([i, -1, state_j, z])
        elif action == 'sell':
            z = dp[i-1][prev_state][prev_k] * priceMat[i][prev_state] * (1 - transFeeRate)
            actions.append([i, prev_state, -1, z])
        
        state_j, state_k = prev_state, prev_k
        if i == 0:
            break

    actions = actions[::-1]
    final_actions = {int(a[0]): a for a in actions}
    sorted_actions = [final_actions[day] for day in sorted(final_actions)]
    actionMat = np.array(sorted_actions, dtype=object)

    # 驗證動作有效性
    for action in actionMat:
        d, a, b, z = action
        assert isinstance(d, (int, np.integer)), "天數索引必須為整數"
        assert 0 <= d < m, "天數索引超出範圍"
        assert (a == -1 or (0 <= a < n)), "來源資產無效"
        assert (b == -1 or (0 <= b < n)), "目標資產無效"
        assert z > 0, "交易金額必須為正數"

    return actionMat

def myAction02(priceMat, transFeeRate, K):
    m, n = priceMat.shape
    initial_capital = 1000

    dp = np.full((m, n + 1, K + 1), -np.inf)
    dp[0][n][1] = initial_capital

    prev = [[[None for _ in range(K + 1)] for _ in range(n + 1)] for _ in range(m)]

    for j in range(n):
        dp[0][j][0] = (initial_capital * (1 - transFeeRate)) / priceMat[0][j]
        prev[0][j][0] = (n, 0, 'buy')
    prev[0][n][1] = (n, 0, 'hold')

    for i in range(1, m):
        for j in range(n + 1):
            for k in range(K + 1):
                if j == n:
                    if k < K:
                        if dp[i-1][j][k] > dp[i][j][k+1]:
                            dp[i][j][k+1] = dp[i-1][j][k]
                            prev[i][j][k+1] = (j, k, 'hold')
                    for l in range(n):
                        cash = dp[i-1][l][k] * priceMat[i][l] * (1 - transFeeRate)
                        if cash > dp[i][j][1]:
                            dp[i][j][1] = cash
                            prev[i][j][1] = (l, k, 'sell')
                else:
                    if dp[i-1][j][k] > dp[i][j][k]:
                        dp[i][j][k] = dp[i-1][j][k]
                        prev[i][j][k] = (j, k, 'hold')
                    buy_amt = dp[i-1][n][k] * (1 - transFeeRate) / priceMat[i][j]
                    if buy_amt > dp[i][j][0]:
                        dp[i][j][0] = buy_amt
                        prev[i][j][0] = (n, k, 'buy')

    max_asset = -np.inf
    last_state = (n, K)
    for j in range(n + 1):
        for k in range(K + 1):
            asset = dp[m-1][j][k] if j == n else dp[m-1][j][k] * priceMat[m-1][j] * (1 - transFeeRate)
            if k >= K and asset > max_asset:
                max_asset = asset
                last_state = (j, k)

    actions = []
    state_j, state_k = last_state
    for i in range(m-1, -1, -1):
        if state_j == n:
            prev_state, prev_k, action = prev[i][state_j][state_k]
        else:
            prev_state, prev_k, action = prev[i][state_j][state_k]
        
        if action == 'buy':
            z = dp[i-1][prev_state][prev_k] * (1 - transFeeRate)
            actions.append([i, -1, state_j, z])
        elif action == 'sell':
            z = dp[i-1][prev_state][prev_k] * priceMat[i][prev_state] * (1 - transFeeRate)
            actions.append([i, prev_state, -1, z])
        
        state_j, state_k = prev_state, prev_k
        if i == 0:
            break

    actions = actions[::-1]
    final_actions = {int(a[0]): a for a in actions}
    sorted_actions = [final_actions[day] for day in sorted(final_actions)]
    actionMat = np.array(sorted_actions, dtype=object)

    for action in actionMat:
        d, a, b, z = action
        assert isinstance(d, (int, np.integer)), "天數索引必須為整數"
        assert 0 <= d < m, "天數索引超出範圍"
        assert (a == -1 or (0 <= a < n)), "來源資產無效"
        assert (b == -1 or (0 <= b < n)), "目標資產無效"
        assert z > 0, "交易金額必須為正數"

    return actionMat

def myAction01(priceMat, transFeeRate):
    m, n = priceMat.shape
    initial_capital = 1000

    dp = np.full((m, n + 1), -np.inf)
    dp[0][n] = initial_capital

    prev = [[None for _ in range(n + 1)] for _ in range(m)]

    for j in range(n):
        dp[0][j] = (initial_capital * (1 - transFeeRate)) / priceMat[0][j]
        prev[0][j] = (n, 'buy')
    prev[0][n] = (n, 'hold')

    for i in range(1, m):
        for j in range(n + 1):
            if j == n:
                hold_cash = dp[i-1][n]
                action = 'hold'
                prev_state = (n, 'hold')
                for k in range(n):
                    cash = dp[i-1][k] * priceMat[i][k] * (1 - transFeeRate)
                    if cash > hold_cash:
                        hold_cash = cash
                        action = 'sell'
                        prev_state = (k, 'sell')
                dp[i][n] = hold_cash
                prev[i][n] = prev_state
            else:
                hold_stock = dp[i-1][j]
                action = 'hold'
                prev_state = (j, 'hold')
                buy_stock = dp[i-1][n] * (1 - transFeeRate) / priceMat[i][j]
                if buy_stock > hold_stock:
                    hold_stock = buy_stock
                    action = 'buy'
                    prev_state = (n, 'buy')
                dp[i][j] = hold_stock
                prev[i][j] = prev_state

    max_asset = dp[m-1][n]
    last_state = n
    for j in range(n):
        asset = dp[m-1][j] * priceMat[m-1][j] * (1 - transFeeRate)
        if asset > max_asset:
            max_asset = asset
            last_state = j

    actions = []
    state = last_state
    for i in range(m-1, -1, -1):
        if state == n:
            prev_state, action = prev[i][state]
        else:
            prev_state, action = prev[i][state]
        
        if action == 'buy':
            z = dp[i-1][n] * (1 - transFeeRate)
            actions.append([i, -1, state, z])
        elif action == 'sell':
            z = dp[i-1][prev_state] * priceMat[i][prev_state] * (1 - transFeeRate)
            actions.append([i, prev_state, -1, z])
        
        state = prev_state
        if i == 0:
            break

    actions = actions[::-1]
    final_actions = {int(a[0]): a for a in actions}
    sorted_actions = [final_actions[day] for day in sorted(final_actions)]
    actionMat = np.array(sorted_actions, dtype=object)

    for action in actionMat:
        d, a, b, z = action
        assert isinstance(d, (int, np.integer)), "天數索引必須為整數"
        assert 0 <= d < m, "天數索引超出範圍"
        assert (a == -1 or (0 <= a < n)), "來源資產無效"
        assert (b == -1 or (0 <= b < n)), "目標資產無效"
        assert z > 0, "交易金額必須為正數"

    return actionMat
