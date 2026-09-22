"""Small controls shared by the implemented application pages."""

from functools import partial

import pandas as pd
import streamlit as st

from tslab.i18n import translate


def odd_window(label: str, size: int, key: str) -> int:
    """Keep an odd window within the current data length, including after resizing."""
    options = list(range(3, min(51, size) + 1, 2))
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = options[-1]
    default = None if key in st.session_state else min(15, options[-1])
    return st.select_slider(label, options=options, value=default, key=key)


def _advance_replay(key: str, amount: int, size: int) -> None:
    st.session_state[key] = min(size, max(1, st.session_state.get(key, 1) + amount))


def replay_controls(frame: pd.DataFrame, selected: list[str], settings: dict, prefix: str, language: str) -> int:
    """Render shared manual replay controls with isolated state and safe navigation resets."""
    t = partial(translate, language=language)
    count_key, signature_key = f"{prefix}_count", f"{prefix}_signature"
    signature = (pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes(), tuple(selected), tuple(settings.items()))
    if st.session_state.get(signature_key) != signature or count_key not in st.session_state:
        st.session_state[signature_key] = signature
        st.session_state[count_key] = 1
    st.caption(t("修改数据、所选算法或参数会从第一帧重新开始；语言和主题切换保留进度。"))
    reset, step, jump = st.columns(3)
    reset.button(t("回到第一帧"), on_click=_advance_replay,
                 args=(count_key, -len(frame), len(frame)), key=f"{prefix}_reset")
    step.button(t("下一帧"), on_click=_advance_replay, args=(count_key, 1, len(frame)),
                disabled=st.session_state[count_key] == len(frame), key=f"{prefix}_step")
    jump.button(t("前进 10 帧"), on_click=_advance_replay, args=(count_key, 10, len(frame)),
                disabled=st.session_state[count_key] == len(frame), key=f"{prefix}_jump")
    return st.slider(t("已到达帧数"), 1, len(frame), key=count_key)
