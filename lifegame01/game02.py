import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# 変数宣言
N=9      # 9 x 9のグリッドを構築
ON = 255 # 生物
OFF = 0  # 何もなし
vals = [ON, OFF]
# N x Nの配列を作成。ON:OFFの割合を2:8で初期化
grid = np.random.choice(vals, N*N, p=[0.2, 0.8]).reshape(N, N)
def update(frameNum, img, grid, N):
    # https://stackoverflow.com/questions/1692388/python-list-of-dict-if-exists-increment-a-dict-value-if-not-append-a-new-dic
    from collections import defaultdict
    newGrid = grid.copy()
    # 各セルの情報を取得し、gridを更新
    for i in range(N):
        for j in range(N):
            cell_info = defaultdict(int)
            # 今後の拡張性を考えて、各要素の出現回数を保存
            cell_info[grid[i, (j-1)%N]] += 1 # (0,8) 左のセル
            cell_info[grid[i, (j+1)%N]] += 1 # (0,1) 右のセル
            cell_info[grid[(i-1)%N, j]] += 1 # (8,0) 上のセル
            cell_info[grid[(i+1)%N, j]] += 1 # (1,0) 下のセル
            cell_info[grid[(i-1)%N, (j-1)%N]] += 1 # (8,8) 左上のセル
            cell_info[grid[(i-1)%N, (j+1)%N]] += 1 # (8,1) 右上のセル
            cell_info[grid[(i+1)%N, (j-1)%N]] += 1 # (1,8) 左下のセル
            cell_info[grid[(i+1)%N, (j+1)%N]] += 1 # (1,1) 右下のセル
            #print("(%d,%d)のセルの値は%d: 周辺の%sの数は%d" % (i, j,grid[i,j],ON,cell_info[ON]))
            # refer to https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
            # 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            # 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
            # 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
            if grid[i, j] == ON:
                # 1. underpopulation and 3. overpopulation
                if (cell_info[ON] < 2) or (cell_info[ON] > 3):
                    newGrid[i, j] = OFF
                else:
                    # two or three live neighbours
                    # do nothing and remains on (to the 2. next generation)
                    continue
            else:
                # 4. reproduction
                if cell_info[ON] == 3:
                    newGrid[i, j] = ON
    # update data
    img.set_data(newGrid)
    # Shallow copies refer to below link
    # https://stackoverflow.com/questions/6167238/what-does-mean
    grid[:] = newGrid[:]
    return img
%matplotlib notebook
# set up animation
fig, ax = plt.subplots()
img = ax.imshow(grid)
ani = animation.FuncAnimation(fig, update, fargs=(img, grid, N),frames = 10,interval=500,save_count=50)
plt.show()