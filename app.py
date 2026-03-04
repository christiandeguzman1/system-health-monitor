"""
System Health Monitor
Real-time system monitoring dashboard built with Streamlit + psutil
Author: Christian Deguzman
"""

import streamlit as st
import psutil
import time
import pandas as pd

#initializing session state history
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["time", "cpu", "memory"])

st.set_page_config(page_title="System Health Monitor", layout="wide")

st.title("Real-Time System Health Dashboard")

#create 3 columns
col1, col2, col3 = st.columns(3)

#get system stats
cpu_percent = psutil.cpu_percent(interval=1)
memory_percent = psutil.virtual_memory().percent
disk = psutil.disk_usage('/')

current_time = time.strftime("%H:%M:%S")

#display metrics
with col1:
    st.metric(label="CPU Usage", value=f"{cpu_percent}%")

with col2:
    st.metric(label="Memory Usage", value=f"{memory_percent}%")

with col3:
    st.metric(label="Disk Usage", value=f"{disk.percent}%")

#system health logic
st.subheader("System Status")

if cpu_percent > 85 or memory_percent > 85:
    st.error("Critical Usage Detected")
elif cpu_percent > 65 or memory_percent > 65:
    st.warning("High Usage Warning")
else:
    st.success("System Running Normally")

#alert logging
if "alerts" not in st.session_state:
    st.session_state.alerts = []

if cpu_percent > 85 or memory_percent > 85:
    st.session_state.alerts.append(
        f"{current_time} - Critical usage detected"
    )
elif cpu_percent > 65 or memory_percent > 65:
    st.session_state.alerts.append(
        f"{current_time} - High usage warning"
    )

#live charts
st.subheader("Live CPU Usage")
st.line_chart(st.session_state.data.set_index("time")["cpu"])

st.subheader("Live Memory Usage")
st.line_chart(st.session_state.data.set_index("time")["memory"])


#capturing metrics into dataframe

new_row = {
    "time": current_time,
    "cpu": cpu_percent,
    "memory": memory_percent
}

st.session_state.data = pd.concat(
    [st.session_state.data, pd.DataFrame([new_row])],
    ignore_index=True
)

#keep only last 50 records for MVP
st.session_state.data = st.session_state.data.tail(50)

#refresh button
if st.button("Refresh"):
    st.rerun()


#table of top CPU and meory processes
st.subheader("Top Running Processes")

processes = []

for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
    try:
        processes.append(proc.info)
    except:
        pass

df = pd.DataFrame(processes)

if not df.empty:
    top_cpu = df.sort_values(by="cpu_percent", ascending=False).head(5)
    top_memory = df.sort_values(by="memory_percent", ascending=False).head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.write("Top CPU Usage")
        st.dataframe(top_cpu)

    with col2:
        st.write("Top Memory Usage")
        st.dataframe(top_memory)

#export system history
st.subheader("Export Data")

csv = st.session_state.data.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download System Metrics as CSV",
    data=csv,
    file_name="system_metrics.csv",
    mime="text/csv",
)

#alert logging logic
st.subheader("Alert History")

if st.session_state.alerts:
    for alert in st.session_state.alerts[-5:]:
        st.write(alert)
else:
    st.write("No alerts triggered.")

#auto refresh
time.sleep(2)
st.rerun()