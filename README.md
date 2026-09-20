<p align="center">
  <img src="app_preview.gif" width="600" alt="App Preview">
</p>


# Time Series Smoothing: an Interactive Visualizer

[![Try the App](https://img.shields.io/badge/TRY%20THE%20APP-FF4B4B)](https://timeseriessmoothing.streamlit.app/)


This repository contains the code for a Streamlit app that visualizes time series smoothing techniques. It includes both real and synthetic datasets and lets you compare how different methods behave with adjustable parameters.

*Note: The app was developed while writing this Medium article: [Six Approaches to Time Series Smoothing](https://medium.com/@dmitriy.bolotov/six-approaches-to-time-series-smoothing-cc3ea9d6b64f)*

**Features**
- Adjustable smoothing parameters
- Visual comparison across methods
- 5 datasets

**Supported methods**: Moving Average, Exponential Moving Average, Savitzky-Golay, LOESS, Gaussian Filter, Kalman Filter

当前开发版已完成 **A01 随机降噪与稳定读数**：保留六种原有算法，增加后向移动平均、有真值的合成实验、因果方法筛选及 RMSE/MAE。上方动图与在线体验链接属于原始项目，当前开发版请在本地启动。

**Extension roadmap (中文)**: [应用分类、代表性算法与分阶段扩展规划](docs/dev/extension_plan_zh.md)

**Development plan (中文)**: [开发顺序、简洁 UI 与模块划分](docs/dev/development_plan_zh.md)

**Stage 0 baseline (中文)**: [环境、启动方式、计算基线与已知问题](docs/baseline_stage0/README.md)

**Stage 1 review (中文)**: [本阶段实现、数值变化与检查步骤](docs/dev/stage1_review_zh.md)

**Language and appearance**: Switch 中文 / English in the sidebar. Use the top-right menu for Light / Dark / System themes. Application text and charts follow your selection; experiment parameters remain unchanged.

**基础体验补充**：[中英文、亮暗主题与后续常用功能建议](docs/dev/usability_plan_zh.md)。本轮未进入导数板块。

## Local development

在项目根目录使用已有环境启动：

```bash
conda activate ts_filter
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

浏览器访问 `http://127.0.0.1:8501`；远程开发需转发该端口。新环境使用 `python -m pip install -r requirements.txt` 安装依赖。

运行数值回归与页面交互测试（无需额外测试依赖）：

```bash
conda run -n ts_filter python -m unittest discover -s tests -v
```

`app.py` 负责导航；`tslab/` 中的数据、算法、指标和绘图相互分离；`tslab/applications/denoising.py` 组织 A01 实验。后续按应用逐步扩展。

## Datasets

This project uses a mix of real-world and synthetic datasets. Below are the sources and licensing information:

- **Sunspots**  
  Daily total sunspot numbers from [SILSO](https://www.sidc.be/SILSO/datafiles). Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

- **Humidity (RH)** and **Wind Speed (WV)**  
  Weather time series from [Weather Long-term Time Series Forecasting](https://www.kaggle.com/datasets/alistairking/weather-long-term-time-series-forecasting) on Kaggle. Licensed under the [MIT License](https://www.mit.edu/~amini/LICENSE.md).

- **Noisy Sine**  
  Synthetic noisy sine wave, created for this project.

- **Process Anomalies**  
  Synthetic dataset simulating different industrial operating modes and injected anomalies, created for this project.
