"""Streamlit entry point: application navigation and page setup only."""

import streamlit as st

from tslab.applications.denoising import render
from tslab.data import ROOT

st.set_page_config(page_title="时间序列实验室", layout="wide")
st.markdown(f"<style>{(ROOT / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

APPLICATIONS = {"随机降噪与稳定读数": render}

with st.sidebar:
    st.title("时间序列实验室")
    st.caption("信号恢复与结构保留")
    application = st.radio("应用板块", list(APPLICATIONS), label_visibility="collapsed")

APPLICATIONS[application]()
