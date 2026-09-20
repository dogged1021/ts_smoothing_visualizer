"""Streamlit entry point: application navigation and page setup only."""

from functools import partial

import streamlit as st

from tslab.applications.denoising import render
from tslab.data import ROOT
from tslab.i18n import translate

language = st.session_state.get("language", "zh")
t = partial(translate, language=language)
st.set_page_config(page_title=t("时间序列实验室"), layout="wide")
st.markdown(f"<style>{(ROOT / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

APPLICATIONS = {"随机降噪与稳定读数": render}

with st.sidebar:
    st.radio(
        "语言 / Language", ["zh", "en"], format_func={"zh": "中文", "en": "English"}.get,
        horizontal=True, key="language",
    )
    st.title(t("时间序列实验室"))
    st.caption(t("右上角 ⋮ 菜单可切换 Light / Dark / System 主题。"))
    st.caption(t("信号恢复与结构保留"))
    application = st.radio(
        t("应用板块"), list(APPLICATIONS), format_func=t, label_visibility="collapsed", key="application"
    )

APPLICATIONS[application](language=language, theme=st.context.theme.type or "light")
