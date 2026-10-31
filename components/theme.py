import plotly.graph_objects as go
import plotly.io as pio


CHART_TEMPLATE = "f1"

template = go.layout.Template(pio.templates["plotly_white"])
template.layout.dragmode = False
template.layout.xaxis.fixedrange = True
template.layout.yaxis.fixedrange = True
pio.templates[CHART_TEMPLATE] = template
pio.templates.default = CHART_TEMPLATE
