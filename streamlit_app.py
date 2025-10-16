"""
Streamlit app for eTalonu validation data visualization.

Loads CSV data from data.gov.lv and displays charts.
"""

import streamlit as st

from database import db
from state_manager import StateKeys, init_state
from utils import format_month_repr_long, last_day_of_month
from widgets.charts import render_charts
from widgets.metrics import render_metrics
from widgets.sidebar import render_sidebar

init_state(db, st.session_state)
min_month = st.session_state[StateKeys.AVAILABLE_MONTHS][0]
max_month = st.session_state[StateKeys.AVAILABLE_MONTHS][-1]

st.set_page_config(
    page_title='eTalonu validācijas',
    page_icon='🚋',
    layout='centered',
    initial_sidebar_state='auto',
)

st.title('🚋 eTalonu validācijas')

st.markdown(
    body=f"""
### Par datiem

Dati pieejami par šādu laika periodu: **{format_month_repr_long(min_month)}** līdz
**{format_month_repr_long(last_day_of_month(max_month))}**.

Dati ietver validācijas no autobusiem, tramvajiem un
trolejbusiem visā Rīgas sabiedriskā transporta tīklā.

Grafikos iespējams apskatīt:

- Kopējo braucienu skaitu izvēlētajā mēnesī un braucienu skaita izmaiņas laika gaitā
- Vidējo braucienu skaitu vienā dienā
- Visaktīvāko stundu braucieniem izvēlētajā mēnesī
- Braucienu sadalījumu pa transporta veidiem
- Braucienu sadalījumu pa nedēļas dienām
- 15 populārākos maršrutus
- Populārāko maršrutu viena transporta līdzekļa vidējo noslogojumu

**Izmantojiet filtrus kreisajā pusē**, lai izvēlētos konkrētu mēnesi un
transporta veidu.
"""
)

render_sidebar(st.session_state)

render_metrics(st.session_state)

render_charts(st.session_state)
