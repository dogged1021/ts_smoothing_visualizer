"""Small controls shared by the implemented application pages."""

import streamlit as st


def odd_window(label: str, size: int, key: str) -> int:
    """Keep an odd window within the current data length, including after resizing."""
    options = list(range(3, min(51, size) + 1, 2))
    if key in st.session_state and st.session_state[key] not in options:
        st.session_state[key] = options[-1]
    default = None if key in st.session_state else min(15, options[-1])
    return st.select_slider(label, options=options, value=default, key=key)
