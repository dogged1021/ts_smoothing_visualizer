# LOWESS / LOESS：局部加权回归

[算法索引与时间约定](overview.md)

## 原理

在目标时刻 t 附近选邻域，按距离给样本加权，再拟合局部直线：

$$\min_{a,b}\sum_{i\in N(t)}w_i[x_i-a-b(t_i-t)]^2,\qquad \hat x(t)=a.$$

本项目使用的 LOWESS 以三立方距离权重 `(1−|u|³)³` 加权（|u|≤1，u 为归一化距离）；再依据拟合残差进行稳健重加权，降低大残差点影响。

与 SG 的区别：两者都做局部回归；这里使用距离权重、按数据比例选邻域并进行残差重加权，不能简单化为所有位置共用一组固定卷积系数。LOESS 是更广的局部多项式方法名称，本项目具体实现是局部线性 LOWESS。

## 优缺点、变体与时延

- 优点：适合平滑的非线性趋势；稳健迭代有助于减少孤立异常点影响，但不保证消除所有异常。
- 缺点：计算量通常高于固定核卷积；大邻域抹掉局部结构，小邻域容易保留噪声；边界只有不对称邻域，误差可能增大。
- 当前离线实现会使用未来观测。因全段邻域与稳健迭代的依赖，不能将 `frac×N/2` 直接宣称为确定的固定等待帧数。
- 可设计只用历史窗口的局部回归，但邻域和稳健规则需重新定义；项目尚未接入此类模拟。

## 本项目实现与注意事项

[algorithms.py](../tslab/algorithms.py) 调用：

```python
lowess(x, np.arange(len(x)), frac=fraction, it=3, return_sorted=False)
```

库为 `statsmodels.nonparametric.smoothers_lowess`。默认 frac=0.05，界面对短序列提高下限，使邻域至少有两点；保留 3 次残差稳健重加权。

自变量是样本序号，当前仅适用于已验证的均匀采样。相同 frac 下，改变数据截取长度会改变实际邻域点数；比较前应关注 `frac×N`，不仅是 frac 数值。

接口依据：[statsmodels LOWESS](https://www.statsmodels.org/stable/generated/statsmodels.nonparametric.smoothers_lowess.lowess.html)。
