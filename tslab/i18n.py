"""Presentation-only translations; stored selections and numerical results stay unchanged."""

ENGLISH = {
    "时间序列实验室": "Time Series Lab",
    "随机降噪与稳定读数": "Noise reduction & stable readings",
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
