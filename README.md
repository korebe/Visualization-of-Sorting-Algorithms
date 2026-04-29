# 排序算法可视化工具 - 核心说明

## 项目概述
- **C 语言**实现四种排序算法（冒泡、选择、快速、插入），增加回调机制。
- 编译为动态链接库（`.so` / `.dll`），由 **Python (tkinter)** 调用并显示排序动画。
- 排序过程中，每次元素交换/移动都会触发回调，将数组快照传回界面，实时绘制条形图并高亮变化的元素。

## 核心文件
| 文件 | 作用 |
|------|------|
| `sort_visual.c` | 改造后的 C 排序代码（含回调函数指针） |
| `libsort.so` (或 .dll) | 编译生成的共享库 |
| `visualizer.py` | Python 图形界面主程序 |

## 快速开始

### 1. 编译动态库
```bash
# Linux/macOS
gcc -shared -fPIC -o libsort.so sort_visual.c

# Windows (MinGW)
gcc -shared -o libsort.dll sort_visual.c
```

### 2. 运行 Python 程序
```bash
python visualizer.py
```
*(Windows 用户需将代码中的 `./libsort.so` 改为 `./libsort.dll`)*

### 3. 界面操作
- 选择排序算法（冒泡 / 选择 / 快速 / 插入）
- 设置数组大小（10~150），点击 **生成新数组**
- 调整动画速度（滑块）
- 点击 **开始排序** 观看排序过程
- 红色柱子为当前被交换/移动的两个元素

## 核心设计
- **线程分离**：排序在子线程执行，主线程负责 UI 重绘，界面不卡顿。
- **队列通信**：C 回调将数组快照和下标放入 `queue.Queue`，主线程定时取出并更新画布。
- **动画机制**：通过 `time.sleep(speed)` 控制绘制间隔，形成连续动画。
- **回调机制**：C 代码定义函数指针 `step_callback`，每次元素变化时调用它，将数组内容传递到 Python。

## 自定义扩展
- 修改随机数范围：编辑 `visualizer.py` 中的 `self.range_min` / `self.range_max`。
- 添加新算法：在 C 中实现并导出，在 Python 的 `_run_sorting` 和控制栏菜单中增加对应选项。
- 调整界面配色：修改 `self.canvas` 的矩形颜色、字体等。

## 注意事项
- 确保 Python、gcc 和 tkinter 已正确安装。
- 动态库的位数需与 Python 解释器一致（32/64 位）。
- 快速排序在小数据量下动画可能过快，可将速度滑块向左拖动。
- 我已经编译了so文件，windows需要的请自行编译并更改python文件的路径。
---
*适合算法教学与可视化演示。*
