"""Presentation-only translations; stored selections and numerical results stay unchanged."""

ENGLISH = {
    "Gaussian（单边）": "Gaussian (one-sided)",
    "Gaussian（固定延迟）": "Gaussian (fixed delay)",
    "Gaussian 与 SG 共用窗口点数；两种 Gaussian 共用 σ。单边核在当前点权重最大，中心核对称；相同窗口不代表相同平滑强度。":
        "Gaussian and SG share the sample window; both Gaussian methods share σ. One-sided weights peak at the "
        "current sample; centered weights are symmetric. Equal windows do not imply equal smoothing strength.",
    "后向差分": "Backward differences",
    "EMA 后向差分": "EMA + backward differences",
    "后向差分与 EMA 后向差分从第 1 帧输出信号，从第 3 帧输出导数；SG 各阶均等待完整窗口。":
        "Backward differences and EMA + backward differences publish the signal from frame 1 and derivatives "
        "from frame 3. SG waits for a complete window for every order.",
    "处理方式": "Processing mode",
    "模拟实时": "Simulated real time",
    "仅使用当前及过去数据": "Current and past data only",
    "使用未来数据": "Uses future data",
    "无需等待未来帧": "No future-frame wait",
    "需要固定等待": "Fixed look-ahead",
    "SG-endpoint": "SG-endpoint",
    "SG（固定延迟）": "SG (fixed delay)",
    "逐帧回放已有数据，不接入实时设备。只计算已到达观测；曲线按被估计时刻对齐。":
        "Replay recorded data frame by frame, without a live device. Only arrived observations are processed;"
        " estimates align with their target times.",
    "窗口方法 · 参数": "Window methods · parameters",
    "窗口方法共用窗口长度；两种 SG 共用阶数，仅求值位置不同。完整窗口形成前不输出。":
        "Window methods share a window length; both SG methods share the degree and differ only in evaluation"
        " position. No output before a full window is available.",
    "修改数据、所选算法或参数会从第一帧重新开始；语言和主题切换保留进度。":
        "Changing data, methods or parameters restarts at the first frame. Language and theme changes "
        "preserve progress.",
    "回到第一帧": "Reset to first frame",
    "下一帧": "Next frame",
    "前进 10 帧": "Advance 10 frames",
    "已到达帧数": "Arrived frames",
    "等待帧数": "Look-ahead frames",
    "等待时间（秒）": "Look-ahead (s)",
    "启动所需帧数": "Startup samples",
    "最新估计对应时刻": "Latest estimated time",
    "尚未输出": "No output yet",
    "已到达 {count}/{total} 帧 · 当前时刻：{time}": "Arrived {count}/{total} frames · Current time: {time}",
    "竖线为当前到达时刻。等待帧数不含启动过程，也不等于响应滞后；末尾未发布估计保持空缺。":
        "The vertical line marks the current arrival time. Look-ahead excludes startup and is distinct from "
        "response lag; unpublished tail estimates remain missing.",
    "误差和 RPR 仅在已发布结果的共同目标时刻上计算；无共同有效点时留空，不代表零误差。":
        "Errors and RPR use common target times of published estimates only. Missing metrics mean no common "
        "valid samples, not zero error.",
    "等待更多数据形成共同有效点。": "Waiting for more data to obtain common valid samples.",
    "未知的模拟方法。": "Unknown simulation method.",
    "模拟窗口必须是至少为 3 的奇数。": "The simulation window must be an odd integer of at least three.",
    "时间序列实验室": "Time Series Lab",
    "随机降噪与稳定读数": "Noise reduction & stable readings",
    "导数与变化率估计": "Derivatives & rates of change",
    "变化、事件与状态": "Change, events & state",
    "二次多项式": "Quadratic polynomial",
    "直接差分": "Finite differences",
    "EMA 后差分": "EMA + differences",
    "Gaussian 后差分": "Gaussian + differences",
    "SavGol 直接求导": "SavGol derivatives",
    "信号": "Signal",
    "一阶导数": "First derivative",
    "二阶导数": "Second derivative",
    "输出": "Output",
    "信号 s(t)（u）": "Signal s(t) (u)",
    "一阶导数（u/s）": "First derivative (u/s)",
    "二阶导数（u/s²）": "Second derivative (u/s²)",
    "逐阶误差": "Errors by derivative order",
    "评价范围": "Evaluation region",
    "排除窗口边界": "Exclude window boundaries",
    "所有共同有效点": "All common valid samples",
    "导数估计至少需要 3 个样本。": "Derivative estimation needs at least three samples.",
    "采样间隔必须大于 0。": "The sample interval must be positive.",
    "同时估计一阶和二阶导数时，多项式阶数至少为 2。":
        "Estimating both first and second derivatives requires a polynomial degree of at least two.",
    "未知的导数实验场景。": "Unknown derivative scenario.",
    "评价掩码长度必须与真值一致。": "The evaluation mask must have the same length as the truth.",
    "输出长度必须与真值一致。": "Estimates must have the same length as the truth.",
    "EMA 使用固定系数递推；启动影响仍计入评价，没有人为指定稳定时间。":
        "EMA uses fixed-coefficient recursion. Initialization effects remain included; no settling time is assumed.",
    "多项式阶数至少为 2；直接估计各阶导数，按真实 Δt 换算单位。端点使用多项式拟合。":
        "Degree must be at least two. Derivatives use the actual Δt; endpoint estimates use polynomial fits.",
    "A07 · 比较信号、一阶导数和二阶导数。真值来自解析公式，不由带噪观测差分生成。":
        "A07 · Compare the signal and its first two derivatives against analytic truth, not differences of noisy data.",
    "时间单位为秒，幅值单位记为 u；一阶和二阶导数单位分别为 u/s、u/s²。":
        "Time is in seconds and amplitude in arbitrary units u; derivatives are in u/s and u/s².",
    "因果模式使用三点后向差分：前两点为空缺；一阶公式为二阶精度，二阶公式为一阶精度。":
        "Causal mode uses three-point backward stencils with two missing initial samples. "
        "Accuracy is second order for d1 and first order for d2.",
    "离线差分采用三点中心公式，两端各一点为空缺；SavGol 和 Gaussian 使用未来样本。":
        "Offline differences use centered three-point stencils, leaving endpoints missing. "
        "SavGol and Gaussian also use future samples.",
    "三行共享时间轴；点击图例可同时隐藏该方法的三条曲线。灰色区域标记所选方法的窗口边界或启动空缺。":
        "The panels share a time axis. A legend click toggles all three curves for a method. "
        "Shading marks the selected methods' window boundaries or missing startup samples.",
    "每一阶在相同的共同有效点上比较；不同阶量纲不同，不合并打分。EMA 初始化影响仍计入。":
        "Methods share valid samples within each order. Units differ across orders; no combined score is used. "
        "EMA initialization effects remain included.",
    "**直接差分**用于展示噪声放大；**平滑后差分**先对观测降噪；**SavGol**从局部多项式直接计算导数。信号平滑得好，不代表导数误差小。":
        "**Finite differences** expose noise amplification. **Smoothing + differences** first reduces observation noise. "
        "**SavGol** differentiates local polynomial fits directly. Good signal smoothing does not imply accurate derivatives.",
    "正弦真值为 s(t)=sin(2πt/5)；多项式真值为 s(t)=0.1t²−0.5t+1。当前只使用光滑合成场景，不在阶跃等不可导点上计算点值导数误差。":
        "The sine signal is s(t)=sin(2πt/5); the polynomial is s(t)=0.1t²−0.5t+1. "
        "Only smooth synthetic scenarios are used; pointwise derivative errors at discontinuities are not evaluated.",
    "边界范围取已选方法的并集：中心差分为两端各 1 点，后向差分为前 2 点，SavGol 为两端各半个窗口，Gaussian 后差分为核半径加 1 点。切换评价范围可查看包含边界估计时的误差变化。":
        "Boundary regions combine the selected methods: one endpoint sample for centered differences, "
        "two initial samples for backward differences, half a window at each end for SavGol, and the kernel radius "
        "plus one for Gaussian + differences. Switch evaluation regions to inspect boundary effects.",
    "信号恢复与结构保留": "Signal recovery & structure preservation",
    "应用板块": "Application",
    "右上角 ⋮ 菜单可切换 Light / Dark / System 主题。":
        "Use the top-right ⋮ menu to switch between Light, Dark and System themes.",
    "数据来源": "Data source",
    "合成信号（有真值）": "Synthetic signal (with ground truth)",
    "内置数据集": "Bundled dataset",
    "实验场景": "Scenario",
    "正弦信号": "Sine wave",
    "缓慢趋势": "Slow trend",
    "恒定读数": "Constant reading",
    "数据参数": "Data parameters",
    "样本数": "Samples",
    "采样间隔 Δt（秒）": "Sample interval Δt (s)",
    "噪声标准差": "Noise standard deviation",
    "随机种子": "Random seed",
    "数据集": "Dataset",
    "太阳黑子 · Sunspots": "Sunspots",
    "带噪正弦 · Noisy Sine": "Noisy Sine",
    "湿度 · Humidity": "Humidity",
    "风速 · Wind Speed": "Wind Speed",
    "过程异常 · Process Anomalies": "Process Anomalies",
    "从开头截取的点数（参与计算）": "Samples from the start (used for calculation)",
    "内置 CSV 未提供干净真值（包括 Noisy Sine），因此仅展示粗糙度等诊断，不计算恢复误差。":
        "Bundled CSVs, including Noisy Sine, contain no clean ground truth. Only diagnostics are available.",
    "MA（居中）": "MA (centered)",
    "MA（后向）": "MA (trailing)",
    "{name} · 参数": "{name} · Parameters",
    "窗口（样本）": "Window (samples)",
    "使用未来 {half} 点（{seconds:g} 秒）；两端各 {half} 点窗口不完整，保留空缺。":
        "Uses {half} future samples ({seconds:g} s). The first and last {half} samples remain missing.",
    "因果；前 {count} 点为启动空缺，不使用未来回填。":
        "Causal. The first {count} samples remain missing; no future values are used to fill them.",
    "平滑因子 α": "Smoothing factor α",
    "起始阶段归一化权重（adjust=True）": "Normalize initial weights (adjust=True)",
    "默认保持原项目行为；取消勾选后采用 y[t] = αx[t] + (1−α)y[t−1]。":
        "The default preserves the original behavior. Uncheck for y[t] = αx[t] + (1−α)y[t−1].",
    "因果；首值初始化，起始阶段受初始化影响。":
        "Causal; initialized with the first observation. Early estimates depend on initialization. ",
    "使用归一化指数权重。": "Uses normalized exponential weights.",
    "使用固定系数递推。": "Uses fixed-coefficient recursion.",
    "多项式阶数": "Polynomial degree",
    "非因果；内部点使用未来 {half} 点。两端各 {half} 点由首尾窗口多项式估计（interp）。":
        "Noncausal. Interior estimates use {half} future samples; endpoint regions use polynomial interpolation.",
    "邻域比例 frac": "Neighborhood fraction",
    "请输入邻域比例 frac。": "Enter a neighborhood fraction.",
    "非因果；邻域约 {count} 点，端点使用不对称邻域。保留 3 次稳健重加权，不能视为固定延迟滤波。":
        "Noncausal; about {count} neighbors, asymmetric at endpoints. Three robust reweightings; not fixed-lag filtering.",
    "σ（样本）": "σ (samples)",
    "非因果；核半径 {radius} 点（{seconds:g} 秒），边界使用反射延拓。":
        "Noncausal; kernel radius {radius} samples ({seconds:g} s), with reflective boundaries.",
    "过程方差 Q": "Process variance Q",
    "观测方差 R": "Observation variance R",
    "输入是方差，不是标准差。Q 是每个采样步的过程方差；更改采样间隔后应重新评估参数。":
        "Inputs are variances, not standard deviations. Q is per sample step; revisit it when changing Δt.",
    "因果；一维随机游走，初始均值取首个观测、初始方差为 1。没有速度或加速度状态。":
        "Causal scalar random walk, initialized at the first observation with variance 1; no velocity or acceleration state.",
    "未知算法：{name}": "Unknown algorithm: {name}",
    "减少随机抖动，同时观察真实信号的保留程度。A01 · 信号恢复与结构保留":
        "Reduce random fluctuations while preserving the underlying signal. A01 · Signal recovery",
    "{count} 个样本 · 采样间隔 {dt:g} 秒 · 等间隔采样":
        "{count} samples · Sample interval {dt:g} s · Uniform sampling",
    "使用模式": "Processing mode",
    "离线对比": "Offline comparison",
    "仅因果方法": "Causal methods only",
    "只使用当前与过去的样本；这是历史记录上的因果计算，并非实时设备接入。":
        "Uses current and past samples only. This processes recorded data, not a live device stream.",
    "可同时对比因果与非因果方法；使用未来信息及边界处理方式见下方说明。":
        "Compare causal and noncausal methods. See the notes for future-sample usage and boundary handling.",
    "对比算法": "Methods to compare",
    "显示设置": "Display settings",
    "原始观测透明度": "Observation opacity",
    "请选择至少一种算法进行比较。当前显示原始观测及可用真值。":
        "Select at least one method to compare. Observations and available ground truth are shown.",
    "任务指标": "Evaluation metrics",
    "方法": "Method",
    "有效点数": "Valid samples",
    "原始观测": "Observations",
    "原始观测以灰色线和前景采样点显示；直接差分的零阶信号就是原始观测，两者重合。":
        "Observations use a gray line with foreground sample markers. The zeroth-order output of direct "
        "differences is the original observation, so the two overlap.",
    "居中离线估计对齐窗口中心，不整体右移；若逐点获取数据，内部点需等待 {samples} 个未来样本（{delay:.3f} 秒）。端点另用多项式拟合。":
        "Centered offline estimates align with the window center without a global right shift. With streaming data, "
        "interior estimates require {samples} future samples ({delay:.3f} s). Endpoints use separate polynomial fits.",
    "干净真值": "Ground truth",
    "时间": "Time",
    "时间（s）": "Time (s)",
    "信号值": "Signal value",
    "估计 − 真值": "Estimate − truth",
    "所选方法没有共同有效点；请缩小窗口或增加样本数。指标中的空值不是零误差。":
        "No common valid samples. Reduce the windows or increase the sample count. Missing metrics are not zero errors.",
    "所有方法及原始观测在相同的 {count} 个有效点上比较。MA 的空缺点不计入指标；其他方法的边界拟合和初始化区域仍计入。RPR 越低仅表示更平滑；常数参考或没有有效相邻点时显示空值。":
        "All methods and observations use the same {count} valid samples. Missing MA values are excluded; other boundary "
        "and initialization regions remain included. Lower RPR only means smoother output. RPR is undefined for "
        "constant observations or when no valid adjacent pairs exist.",
    "误差与边界诊断": "Errors & boundary diagnostics",
    "没有真值，无法判断实际恢复误差。请结合曲线形状及应用目标判断效果。":
        "Without ground truth, recovery error is unknown. Assess the shape together with your application goals.",
    "算法原理与比较提示": "Methods & comparison notes",
    "算法说明正文":
        "- **MA / EMA / Gaussian** use uniform, exponential and Gaussian weights, respectively.\n"
        "- **SavGol** fits local polynomials to reduce noise while retaining local structure.\n"
        "- **LOWESS** fits local lines and reduces outlier influence through residual-based reweighting.\n"
        "- **Kalman** combines random-walk predictions with noisy observations to estimate the state.\n\n"
        "Stronger smoothing can suppress peaks and rapid changes. Causal methods can lag, while offline methods "
        "can use future data; compare them in the context of your intended use.",
    "输入必须是一维、非空且不含缺失值或无穷值的数列。":
        "Input must be a nonempty, finite, one-dimensional sequence.",
    "窗口必须是正整数，且不能超过数据长度。": "The window must be a positive integer no longer than the data.",
    "alpha 必须在 (0, 1] 内。": "Alpha must be in (0, 1].",
    "SavGol 窗口必须为奇数，且多项式阶数必须为非负整数并小于窗口。":
        "SavGol requires an odd window and a nonnegative integer degree smaller than the window.",
    "LOWESS 邻域至少需要 2 个样本，frac 应在 (0, 1] 内。":
        "LOWESS needs at least two neighbors and a fraction in (0, 1].",
    "sigma 必须大于 0。": "Sigma must be positive.",
    "过程方差 Q 必须非负，观测方差 R 必须大于 0。": "Q must be nonnegative and R must be positive.",
    "数据至少需要两行，并包含 value 列。": "Data needs at least two rows and a value column.",
    "观测包含缺失值或无穷值；当前阶段不自动插补。": "Observations contain missing or infinite values; automatic filling is not enabled.",
    "时间戳包含缺失值。": "Timestamps contain missing values.",
    "时间必须严格递增，且不含重复或无效时间戳。": "Time must be strictly increasing with no duplicate or invalid timestamps.",
    "当前板块要求等间隔采样；非均匀采样处理将在后续阶段提供。":
        "This application requires uniform sampling. Nonuniform sampling support is planned for a later stage.",
    "未知的内置数据集。": "Unknown bundled dataset.",
    "样本数必须是至少为 2 的整数。": "The sample count must be an integer of at least two.",
    "采样间隔必须大于 0，噪声标准差必须非负。": "The sample interval must be positive and noise standard deviation nonnegative.",
    "未知的合成场景。": "Unknown synthetic scenario.",
}

METHOD_NOTES_ZH = (
    "- **MA / EMA / Gaussian**：分别使用等权、指数权重、高斯权重进行平均。\n"
    "- **SavGol**：在局部窗口拟合多项式，兼顾降噪与局部形状。\n"
    "- **LOWESS**：局部线性回归，并根据残差降低异常值权重。\n"
    "- **Kalman**：结合随机游走模型预测与带噪观测，递推估计状态。\n\n"
    "窗口、σ 或平滑强度增大，可能同时损失峰值和快速变化。"
    "因果方法存在响应滞后的可能，离线方法借助未来数据，二者应结合实际使用方式比较。"
)


def translate(text: str, language: str = "zh", **values: object) -> str:
    """Translate a display string and fill named fields; keep algorithm names intact."""
    if language not in ("zh", "en"):
        raise ValueError(f"Unsupported language: {language}")
    if language == "en":
        text = ENGLISH.get(text, text)
    elif text == "算法说明正文":
        text = METHOD_NOTES_ZH
    return text.format(**values) if values else text
