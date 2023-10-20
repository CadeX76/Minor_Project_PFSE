from math import sqrt, pi
from plotly import graph_objects as go
from shapely import LineString, intersection
import streamlit as st
from eng_module import seismic_analysis as sa

st.set_page_config(
    page_title='Seismic Design: Eurocode 1998-1-1',
    layout='wide',
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.subheader('Response Spectrum Data:')
    st.subheader('Eurocode 1998-1-1')
    spectra_type = st.selectbox('Spectra Type', [1, 2])
    pga = 9.81 * st.number_input('Peak Ground Acceleration [ag/g]', value= 0.2)
    soil_type = st.selectbox('Soil Type', ['A', 'B', 'C', 'D', 'E'])
    damping = st.number_input('Damping [%]', value= 5)
    st.divider()
    st.subheader('System Parameters:')
    m_sys = st.number_input('Mass [ton]', value= 4000.0)
    k_type = st.selectbox('Type of Stiffness', ['Linear', 'Multi-linear'])
    if k_type == 'Linear':
        k1_sys = st.number_input('Stiffness [kN/m]', value= 350000.0)
    elif k_type == 'Multi-linear':
        k1_sys = st.number_input('Stiffness of first branch [kN/m]', value= 350000.0)
        k2_sys = st.number_input('Stiffness of second branch [kN/m]', value= 35000.0)
        F1_sys = st.number_input('Maximum force of first branch [kN]', value= 10000.0)
    
spectrum = sa.Ec_response_spectrum(ag= pga, spectra_type= spectra_type, soil_type= soil_type, damping= damping)

xy_demand = sa.system_demand(m_sys, spectrum)
x_demand, y_demand = zip(*xy_demand)

if k_type == 'Linear':
    xy_capacity = sa.system_capacity(k_type, x_demand, k1_sys)
elif k_type == 'Multi-linear':
    xy_capacity = sa.system_capacity(k_type, x_demand, k1_sys, k2_sys, F1_sys)

x_capacity, y_capacity = zip(*xy_capacity)

F_sys = intersection(LineString(xy_demand), LineString(xy_capacity))

fig = go.Figure()
fig.layout.title.text = 'Seismic demand vs capacity'
fig.add_trace(go.Scatter(y= y_demand, x= x_demand, name = 'Demand'))
fig.add_trace(go.Scatter(y= y_capacity, x= x_capacity, name = 'Capacity'))
fig.layout.width = 700
fig.layout.height = 700
fig.update_xaxes(range = [0, max(x_demand) * 1.1])
fig.update_yaxes(range = [0, max(y_demand) * 1.1])
fig.layout.xaxis.title = 'Displacement [m]'
fig.layout.yaxis.title = 'Force [kN]'
st.plotly_chart(fig)

col1, col2, col3, col4 = st.columns(4)

col1.metric(label='System Force', value=f'{round(F_sys.y, 1)} kN')
col2.metric(label='System Displacement', value=f'{round(F_sys.x * 1000, 1)} mm')
col3.metric(label='System Period', value=f'{round(2 * pi * sqrt(m_sys / (F_sys.y / F_sys.x)), 2)} s')
col4.metric(label='System Acceleration', value=f'{round(F_sys.y / m_sys, 2)} m/s2')

