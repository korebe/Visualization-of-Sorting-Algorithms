import ctypes
import tkinter as tk
from tkinter import ttk
import random
import threading
import queue
import time

# ========== 1. 加载 C 库 ==========
lib = ctypes.CDLL('/home/zwj/c+python/排序/libsort.so')  

# 定义函数原型
lib.ACM_maopao.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
lib.ACM_xuanze.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
lib.ACM_kuaisu.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int]
lib.ACM_insert.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]

# 回调函数类型：void (*callback)(int* arr, int n, int i, int j)
CALLBACK = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.c_int)

lib.set_callback.argtypes = [CALLBACK]
lib.set_random_seed.argtypes = [ctypes.c_uint]

# ========== 2. 全局状态与队列 ==========
event_queue = queue.Queue()        # 用于线程间传递快照数据
running = False                    # 排序是否正在运行

# ========== 3. UI 类 ==========
class SortVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("排序算法可视化")
        self.root.geometry("900x650")
        self.root.configure(bg='#f0f4f7')

        # 数据参数
        self.n = 50                 # 数组大小
        self.range_min = 10
        self.range_max = 100
        self.arr = []               # 当前数组
        self.speed = 0.05           # 动画间隔（秒）

        # 回调锁（避免同时写入队列）
        self.lock = threading.Lock()

        # 设置回调函数（C 调用时触发）
        self.callback_func = CALLBACK(self._step_callback)
        lib.set_callback(self.callback_func)
        lib.set_random_seed(random.randint(0, 10000))

        # 构建界面
        self._build_ui()

        # 初始化数组并绘制
        self.generate_array()

    def _build_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ----- 控制栏 -----
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 算法选择
        ttk.Label(control_frame, text="算法:").pack(side=tk.LEFT, padx=5)
        self.algo_var = tk.StringVar(value="冒泡排序")
        algo_menu = ttk.Combobox(control_frame, textvariable=self.algo_var,
                                 values=["冒泡排序", "选择排序", "快速排序", "插入排序"],
                                 state="readonly", width=12)
        algo_menu.pack(side=tk.LEFT, padx=5)

        # 数组大小
        ttk.Label(control_frame, text="数量:").pack(side=tk.LEFT, padx=(20,5))
        self.size_var = tk.IntVar(value=50)
        size_spin = ttk.Spinbox(control_frame, from_=10, to=150, textvariable=self.size_var, width=5)
        size_spin.pack(side=tk.LEFT, padx=5)

        # 生成按钮
        gen_btn = ttk.Button(control_frame, text="生成新数组", command=self.generate_array)
        gen_btn.pack(side=tk.LEFT, padx=20)

        # 开始排序按钮
        self.start_btn = ttk.Button(control_frame, text="开始排序", command=self.start_sorting)
        self.start_btn.pack(side=tk.LEFT, padx=10)

        # 速度滑块
        ttk.Label(control_frame, text="速度:").pack(side=tk.LEFT, padx=(20,5))
        self.speed_var = tk.DoubleVar(value=0.05)
        speed_scale = ttk.Scale(control_frame, from_=0.01, to=0.5, variable=self.speed_var,
                                orient=tk.HORIZONTAL, length=120)
        speed_scale.pack(side=tk.LEFT, padx=5)

        # ----- 画布 -----
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # ----- 状态栏 -----
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10,0))

    def generate_array(self):
        """生成随机数组并绘制"""
        if running:
            return
        self.n = self.size_var.get()
        self.arr = [random.randint(self.range_min, self.range_max) for _ in range(self.n)]
        self.status_var.set(f"已生成 {self.n} 个随机数")
        self._draw_array(highlight=(-1, -1))

    def _draw_array(self, highlight=(-1, -1)):
        """绘制条形图，highlight 为高亮的两个下标 (-1,-1) 表示不高亮"""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:  # 画布尚未就绪
            return
        if self.n == 0:
            return

        bar_width = max(1, (w - 20) // self.n)
        max_val = max(self.arr) if self.arr else 1

        for i, val in enumerate(self.arr):
            x0 = 10 + i * bar_width
            y0 = h - 20 - (val / max_val) * (h - 40)
            x1 = x0 + bar_width - 1
            y1 = h - 20

            # 默认颜色
            color = '#4a90d9'
            if i == highlight[0] or i == highlight[1]:
                color = '#e74c3c'  # 红色高亮

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='')

            # 如果条形够宽，显示数值
            if bar_width > 15:
                self.canvas.create_text((x0+x1)/2, y0-10, text=str(val), font=('Arial', 7))

    def start_sorting(self):
        """在新线程中启动排序，避免阻塞 UI"""
        global running
        if running:
            return
        if not self.arr:
            return

        algo = self.algo_var.get()
        self.speed = self.speed_var.get()
        running = True
        self.start_btn.config(state=tk.DISABLED)
        self.status_var.set(f"正在执行 {algo} ...")

        # 清空事件队列
        while not event_queue.empty():
            event_queue.get()

        # 创建 C 格式数组
        self.c_arr = (ctypes.c_int * self.n)(*self.arr)

        # 启动排序线程
        t = threading.Thread(target=self._run_sorting, args=(algo,))
        t.daemon = True
        t.start()

        # 启动 UI 更新循环
        self._update_canvas()

    def _run_sorting(self, algo):
        """在子线程中调用 C 排序函数"""
        if algo == "冒泡排序":
            lib.ACM_maopao(self.c_arr, self.n)
        elif algo == "选择排序":
            lib.ACM_xuanze(self.c_arr, self.n)
        elif algo == "快速排序":
            lib.ACM_kuaisu(self.c_arr, 0, self.n - 1)
        elif algo == "插入排序":
            lib.ACM_insert(self.c_arr, self.n)

        # 排序完成，放入结束信号
        event_queue.put(("done", None, None))

    def _step_callback(self, arr_ptr, n, i, j):
        """C 回调：将当前数组快照和下标放入队列"""
        if not running:
            return
        # 从 C 指针复制数组内容
        snapshot = [arr_ptr[k] for k in range(self.n)]
        event_queue.put(("step", snapshot, (i, j)))
        # 简单限速：回调过于频繁时会减慢 UI 更新，此处通过 speed 在 UI 端控制

    def _update_canvas(self):
        """主线程定时检查队列，更新画布"""
        global running
        try:
            while True:
                event = event_queue.get_nowait()
                msg = event[0]
                if msg == "step":
                    snapshot, idx = event[1], event[2]
                    self.arr = snapshot
                    self._draw_array(highlight=idx)
                    # 控制动画速度
                    time.sleep(self.speed)
                    self.root.update()
                elif msg == "done":
                    # 排序结束
                    running = False
                    self.start_btn.config(state=tk.NORMAL)
                    self.status_var.set("排序完成")
                    self._draw_array()  # 清除高亮
                    return
        except queue.Empty:
            pass

        if running:
            self.root.after(10, self._update_canvas)

# ========== 4. 启动 ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = SortVisualizer(root)
    root.mainloop()