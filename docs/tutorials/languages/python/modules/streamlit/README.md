# Streamlit Tutorial

**Level**: Beginner to Advanced
**Category**: Web Apps / Dashboarding

Streamlit turns data scripts into shareable web apps in minutes. No front-end experience required.

## 📦 Installation

```bash
pip install streamlit
```

## 🚀 Beginner: "Hello World" App

Create equal `app.py`:

```python
import streamlit as st
import pandas as pd
import numpy as np

st.title("My First Streamlit App")

st.write("Here's our first attempt at using data to create a table:")
df = pd.DataFrame(np.random.randn(10, 2), columns=['x', 'y'])
st.line_chart(df)

if st.button('Say hello'):
    st.write('Why hello there!')
```

Run it locally:
```bash
streamlit run app.py
```

## 🏃 Intermediate: Interactivity & Layout

Use sidebar widgets to filter data dynamically.

```python
import streamlit as st

st.sidebar.title("Controls")
name = st.sidebar.text_input("Enter your name")
age = st.sidebar.slider("Select your age", 0, 100, 25)

col1, col2 = st.columns(2)

with col1:
    st.header("Profile")
    st.write(f"Name: {name}")
    st.write(f"Age: {age}")

with col2:
    st.header("Analytics")
    st.metric(label="Score", value=age * 10, delta="1.2%")
```

## 🧠 Advanced: Session State & Caching

Streamlit reruns the *entire* script on every interaction. Use `@st.cache_data` for expensive computations and `st.session_state` to remember variables between reruns.

```python
import streamlit as st
import time

# 1. Caching: This function only runs if 'seconds' changes
@st.cache_data
def expensive_computation(seconds):
    time.sleep(seconds)
    return "Done!"

if st.button("Run Expensive Task"):
    result = expensive_computation(2)
    st.success(result)

# 2. Session State: Counter example
if 'count' not in st.session_state:
    st.session_state.count = 0

increment = st.button('Click me')
if increment:
    st.session_state.count += 1

st.write(f"Button clicked {st.session_state.count} times")
```

## 💡 Use Cases

1.  **Model Demos**: Allow non-technical users to input text/images and see your AI model's output.
2.  **Internal Dashboards**: Replace Excel sheets with interactive web dashboards for KPIs.
3.  **Data Labeling**: Build simple tools for humans to categorize data manually.
