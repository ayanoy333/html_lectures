import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ライフゲームのルールを定義
def life_step(X):
    """
    セルの次の世代の状態を計算する関数
    """
    # 近傍の状態の合計を計算
    N = (X[0:-2,0:-2] + X[0:-2,1:-1] + X[0:-2,2:] +
         X[1:-1,0:-2]                + X[1:-1,2:] +
         X[2:  ,0:-2] + X[2:  ,1:-1] + X[2:  ,2:])

    # セルの次の状態を計算
    birth = (N==3) & (X[1:-1,1:-1]==0)
    survive = ((N==2) | (N==3)) & (X[1:-1,1:-1]==1)
    X[...] = 0
    X[1:-1,1:-1][birth | survive] = 1
    return X

# 初期状態をランダムに生成
def initial_state(N):
    """
    ランダムな初期状態を生成する関数
    """
    X = np.zeros((N, N))
    r = np.random.randint(0, 2, (N, N))
    X[1:-1, 1:-1] = r
    return X

# アニメーションを作成
def animate(frame):
    """
    アニメーションを作成する関数
    """
    global X
    X = life_step(X)
    mat.set_array(X)
    return [mat]

# メイン関数
if __name__ == '__main__':
    N = 100  # セルの数
    X = initial_state(N)

    fig, ax = plt.subplots()
    mat = ax.matshow(X, cmap='binary')
    ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, blit=True)
    plt.show()
