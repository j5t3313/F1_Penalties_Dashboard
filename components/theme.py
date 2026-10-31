import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


CHART_TEMPLATE = "f1"
COLOR_SEQUENCE = px.colors.qualitative.Set2
BORDER_STYLE = dict(showline=True, linewidth=1.5, linecolor="#333333", mirror=True)

template = go.layout.Template(pio.templates["plotly_white"])
template.layout.dragmode = False
template.layout.xaxis.fixedrange = True
template.layout.yaxis.fixedrange = True
pio.templates[CHART_TEMPLATE] = template
pio.templates.default = CHART_TEMPLATE


def apply_border(fig, is_treemap=False):
    if is_treemap:
        fig.add_shape(
            type="rect", xref="paper", yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color="#333333", width=1.5),
        )
    else:
        fig.update_xaxes(**BORDER_STYLE)
        fig.update_yaxes(**BORDER_STYLE)
    return fig


def empty_figure(message="No data available"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color="gray"),
    )
    fig.update_layout(
        template=CHART_TEMPLATE,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig
