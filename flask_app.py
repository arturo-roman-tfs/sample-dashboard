
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies
import dash_table as dt
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def shared_filter(selected_date_filter):
    if selected_date_filter == 1:  # This Week
        start_date = pd.Timestamp("now").to_period("W").start_time
        end_date = pd.Timestamp("now").to_period("D").start_time
    elif selected_date_filter == 2:  # This Month
        start_date = pd.Timestamp("now").to_period("M").start_time
        end_date = pd.Timestamp("now").to_period("D").start_time
    elif selected_date_filter == 3:  # This Quarter
        start_date = pd.Timestamp("now").to_period("Q").start_time
        end_date = pd.Timestamp("now").to_period("D").start_time
    elif selected_date_filter == 4:  # This Year
        start_date = pd.Timestamp("now").to_period("Y").start_time
        end_date = pd.Timestamp("now").to_period("D").start_time
    elif selected_date_filter == 5:  # Last Week
        start_date = pd.Timestamp("now").to_period("W").start_time - pd.Timedelta(
            1, unit="W"
        )
        end_date = pd.Timestamp("now").to_period("W").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 6:  # Last Month
        start_date = pd.Timestamp("now").to_period("M").start_time - pd.Timedelta(
            1, unit="M"
        )
        end_date = pd.Timestamp("now").to_period("M").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 7:  # Last Quarter
        start_date = pd.Timestamp("now").to_period("Q").start_time - pd.Timedelta(
            92, unit="D"
        )
        end_date = pd.Timestamp("now").to_period("Q").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 8:  # Last Year
        start_date = pd.Timestamp("now").to_period("Y").start_time - pd.Timedelta(
            1, unit="Y"
        )
        end_date = pd.Timestamp("now").to_period("Y").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 9:  # Last 7 Days
        start_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            7, unit="D"
        )
        end_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 10:  # Last 30 Days
        start_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            30, unit="D"
        )
        end_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 11:  # Last 90 Days
        start_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            90, unit="D"
        )
        end_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            1, unit="D"
        )
    elif selected_date_filter == 12:  # Last 365 Days
        start_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            365, unit="D"
        )
        end_date = pd.Timestamp("now").to_period("D").start_time - pd.Timedelta(
            1, unit="D"
        )

    return start_date, end_date


def serve_layout():

    global daily_agg_df
    global revenue_df
    global master_df
    global active_inventory_df
    global turnover_df
    daily_agg_df = pd.read_csv("daili_agg_dataset.csv").sort_values("ref_date")
    daily_agg_df["ref_date"] = pd.to_datetime(daily_agg_df["ref_date"])
    revenue_df = daily_agg_df.loc[daily_agg_df["true_sale"] == "t"]
    daily_agg_df.loc[daily_agg_df.true_sale == "f", "revenue"] = 0
    master_df = (
        daily_agg_df.groupby("ref_date")
        .agg(
            {
                "revenue": "sum",
                "cogs": "sum",
                "sold_tickets_count": "sum",
                "purchased_tickets_count": "sum",
                "costs": "sum",
            }
        )
        .reset_index()
    )

    active_inventory_df = pd.read_csv("active_inventory_dataset.csv").sort_values(
        "ref_date"
    )

    active_inventory_df["ref_date"] = pd.to_datetime(active_inventory_df["ref_date"])
    master_df = master_df.merge(
        active_inventory_df, left_on="ref_date", right_on="ref_date", how="inner"
    )

    master_df["daily_gross_profit"] = master_df["revenue"] - master_df["cogs"]
    master_df["daily_gross_margin"] = (
        master_df["daily_gross_profit"] / master_df["revenue"]
    )
    master_df["avg_inventory"] = (
        2 * master_df["active_inventory_dollars"]
        + master_df["cogs"]
        - master_df["costs"]
    ) / 2
    #///// Daily turnover for datagrid
    master_df["turnover"] = master_df["cogs"] / master_df["avg_inventory"]
    #///// Weekly turnover for graph
    turnover_df = master_df.groupby(pd.Grouper(key='ref_date', freq='W-SAT')).agg({'cogs': 'sum','costs': 'sum', 'active_inventory_dollars': 'last'}).reset_index()
    turnover_df["avg_inventory"] = (
        2 * turnover_df["active_inventory_dollars"]
        + turnover_df["cogs"]
        - turnover_df["costs"]
    ) / 2
    turnover_df["turnover"] =turnover_df["cogs"] / turnover_df["avg_inventory"]
    # Is required to compute the turnover Sunday to Saturday but show it on Sunday
    turnover_df['ref_date'] = pd.to_datetime(turnover_df['ref_date']) + pd.DateOffset(days=1)
    filtered_master_df1 = master_df.head(1)
    filtered_master_df1["DOW_name"] = pd.to_datetime(
        filtered_master_df1["ref_date"]
    ).dt.day_name()
    filtered_master_df1 = filtered_master_df1[
        [
            "ref_date",
            "DOW_name",
            "active_inventory_dollars",
            "revenue",
            "cogs",
            "daily_gross_profit",
            "daily_gross_margin",
            "turnover",
            "costs",
        ]
    ].copy()
    filtered_master_df1.columns = [
        "Date",
        "Day of Week",
        "Active Inventory",
        "Revenue",
        "COGS",
        "Profit",
        "Margin",
        "Turnover",
        "Purchases($)",
    ]

    return html.Div(
        [
            # HEADER AND FILTER ROW
            html.Div(
                [
                    # HEADER CONTAINER
                    html.Div(
                        [html.Div([html.H2("Business Summary")])],
                        className="four columns",
                    ),
                    ##DESCRIPTION CONTAINER
                    html.Div(
                        [html.P("", className="row")],
                        id="right-column",
                        className="four columns",
                    ),
                    # FILTER CONTAINER
                    html.Div(
                        [
                            html.P("Filter by periods:", className="control_label"),
                            dcc.Dropdown(
                                id="purchase-dropdown",
                                options=[
                                    {"label": "This week", "value": 1},
                                    {"label": "This month", "value": 2},
                                    {"label": "This quarter", "value": 3},
                                    {"label": "This year", "value": 4},
                                    {"label": "Last week", "value": 5},
                                    {"label": "Last month", "value": 6},
                                    {"label": "Last quarter", "value": 7},
                                    {"label": "Last year", "value": 8},
                                    {"label": "Last 7 days", "value": 9},
                                    {"label": "Last 30 days", "value": 10},
                                    {"label": "Last 90 days", "value": 11},
                                    {"label": "Last 365 days", "value": 12},
                                ],
                                value=11,
                            ),
                        ],
                        className="four columns",
                    ),
                ],
                className="row flex-display",
            ),
            # TAB CONTAINER
            dcc.Tabs(
                id="tabs",
                children=[
                    # FIRST TAB
                    dcc.Tab(
                        label="Summary",
                        children=[
                            # FIRST ROW
                            html.Div(
                                [
                                    # FISRT GRAPH CONTAINER
                                    html.Div(
                                        [
                                            dcc.Loading(
                                                id="loading-revenue_graph",
                                                children=[
                                                    dcc.Graph(id="revenue_graph")
                                                ],
                                                type="default",
                                            )
                                        ],
                                        className="pretty_container six columns",
                                    ),
                                    # SECOND GRAPH CONTAINER
                                    html.Div(
                                        [
                                            dcc.Loading(
                                                id="loading-turnover_graph",
                                                children=[
                                                    dcc.Graph(id="turnover_graph")
                                                ],
                                                type="default",
                                            )
                                        ],
                                        className="pretty_container six columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),
                            # SECOND ROW
                            html.Div(
                                [
                                    # 3RD GRAPH CONTAINER
                                    html.Div(
                                        [
                                            dcc.Loading(
                                                id="loading-gross_profit_graph",
                                                children=[
                                                    dcc.Graph(id="gross_profit_graph")
                                                ],
                                                type="default",
                                            )
                                        ],
                                        className="pretty_container six columns",
                                    ),
                                    # 4TH GRPH CONTAINER
                                    html.Div(
                                        [
                                            dcc.Loading(
                                                id="loading-active_inventory_graph",
                                                children=[
                                                    dcc.Graph(
                                                        id="active_inventory_graph"
                                                    )
                                                ],
                                                type="default",
                                            )
                                        ],
                                        className="pretty_container six columns",
                                    ),
                                ],
                                className="row flex-display",
                            ),
                        ],
                    ),
                    # SECOND TAB
                    dcc.Tab(
                        label="Breakdown",
                        children=[
                            # FIRTS ROW
                            html.Div(
                                [
                                    # TABLE CONTAINER
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    dt.DataTable(
                                                        id="daily_data_table",
                                                        columns=[
                                                            {
                                                                "name": i,
                                                                "id": i,
                                                                "deletable": False,
                                                            }
                                                            for i in filtered_master_df1.columns
                                                        ],
                                                        data=filtered_master_df1.to_dict(
                                                            "records"
                                                        ),
                                                        style_data_conditional=[
                                                            {
                                                                "if": {
                                                                    "row_index": "odd"
                                                                },
                                                                "backgroundColor": "rgb(248, 248, 248)",
                                                            }
                                                        ],
                                                        style_header={
                                                            "backgroundColor": "rgb(230, 230, 230)",
                                                            "fontWeight": "bold",
                                                        },
                                                    ),
                                                    html.Div(
                                                        id="datatable-filter-container"
                                                    ),
                                                ]
                                            )
                                        ],
                                        className="pretty_container twelve columns",
                                    )
                                ],
                                className="row",
                            )
                        ],
                    ),
                ],
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column", "margin-top": "0px"},
    )


############################################################

# initialize app
app = dash.Dash(__name__)
server = app.server

############################################################

# create app layout
app.layout = serve_layout

############################################################

# callbacks


@app.callback(
    [
        dash.dependencies.Output("revenue_graph", "figure"),
        dash.dependencies.Output("turnover_graph", "figure"),
        dash.dependencies.Output("gross_profit_graph", "figure"),
        dash.dependencies.Output("active_inventory_graph", "figure"),
    ],
    [dash.dependencies.Input("purchase-dropdown", "value")],
)
def update_summary_figure(selected_date_filter):
    # date filter

    start_date, end_date = shared_filter(selected_date_filter)
    filtered_revenue_df = revenue_df.loc[
        (
            (pd.to_datetime(revenue_df["ref_date"]) >= start_date)
            & (pd.to_datetime(revenue_df["ref_date"]) <= end_date)
        )
    ].copy()
    filtered_revenue_df["cum_revenue"] = filtered_revenue_df["revenue"].cumsum()
    filtered_master_df = master_df.loc[
        (
            (pd.to_datetime(master_df["ref_date"]) >= start_date)
            & (pd.to_datetime(master_df["ref_date"]) <= end_date)
        )
    ].copy()
    filtered_turnover_df = turnover_df.loc[
        (
            (pd.to_datetime(turnover_df["ref_date"]) >= start_date)
            & (pd.to_datetime(turnover_df["ref_date"]) <= end_date)
        )
    ].copy()
    turnover_first_point = filtered_turnover_df["ref_date"].min()

    revenue_go = go.Bar(
        x=pd.to_datetime(filtered_revenue_df["ref_date"]),
        y=filtered_revenue_df["revenue"],
        name="Revenue",
    )
    cum_revenue_go = go.Scatter(
        x=pd.to_datetime(filtered_revenue_df["ref_date"]),
        y=filtered_revenue_df["cum_revenue"],
        mode="lines",
        name="Cumulative Revenue",
    )

    revenue_layout = go.Layout(
        template="plotly_white",
        autosize=True,
        title="Revenue",
        font=dict(family="Raleway", size=14),
        hovermode="closest",
        legend=dict(x=-0.0277108433735, y=-0.142606516291, orientation="h",),
        margin=dict(r=10, t=60, b=10, l=10,),
        showlegend=True,
        xaxis=dict(
            autorange=True,
            linecolor="rgb(0, 0, 0)",
            linewidth=1,
            showgrid=False,
            showline=True,
        ),
        yaxis=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=True,
            ticklen=10,
            ticks="outside",
            title="$",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
        ),
        yaxis2=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=False,
            ticklen=10,
            ticks="outside",
            title="$",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
        ),
    )

    revenue_graph = make_subplots(specs=[[{"secondary_y": True}]])
    revenue_graph.add_trace(
        revenue_go, secondary_y=False,
    )
    # revenue_graph.add_trace(
    #     cum_revenue_go, secondary_y=True,
    # )
    revenue_graph.update_layout(revenue_layout)

    turnover_go = go.Scatter(
        x=pd.to_datetime(filtered_turnover_df["ref_date"]),
        y=filtered_turnover_df["turnover"],
        name="Turnover",
        mode="lines+markers",
        marker=dict(size=8,
            line=dict(width=2,
                    color='DarkSlateGrey')
        )
    )
    turnover_layout = go.Layout(
        template="plotly_white",
        autosize=True,
        title="Turnover",
        font=dict(family="Raleway", size=14),
        hovermode="closest",
        legend=dict(x=-0.0277108433735, y=-0.142606516291, orientation="h",),
        margin=dict(r=10, t=60, b=10, l=10,),
        showlegend=True,
        xaxis=dict(
            autorange=True,
            linecolor="rgb(0, 0, 0)",
            linewidth=1,
            showgrid=False,
            showline=True,
            dtick=86400000.0*7,
            tickformat="%m/%d/%Y",
            tickangle=-30,
            tickfont=dict(family='Calibri', size=12),
            tick0=turnover_first_point,
        ),
        yaxis=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=True,
            ticklen=10,
            ticks="outside",
            title="%",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
            tickformat=",.1%",
        ),
    )
    turnover_graph = make_subplots(specs=[[{"secondary_y": True}]])
    turnover_graph.add_trace(
        turnover_go, secondary_y=False,
    )
    turnover_graph.update_layout(turnover_layout)
    gross_profit_go = go.Bar(
        x=pd.to_datetime(filtered_master_df["ref_date"]),
        y=filtered_master_df["daily_gross_profit"],
        name="Gross Profit",
    )
    gross_margin_go = go.Scatter(
        x=pd.to_datetime(filtered_master_df["ref_date"]),
        y=filtered_master_df["daily_gross_margin"],
        name="Gross Margin",
        mode="lines",
    )
    gross_profit_layout = go.Layout(
        template="plotly_white",
        autosize=True,
        title="Gross Profit/Gross Margin",
        font=dict(family="Raleway", size=14),
        hovermode="closest",
        legend=dict(x=-0.0277108433735, y=-0.142606516291, orientation="h",),
        margin=dict(r=10, t=60, b=10, l=10,),
        showlegend=True,
        xaxis=dict(
            autorange=True,
            linecolor="rgb(0, 0, 0)",
            linewidth=1,
            showgrid=False,
            showline=True,
        ),
        yaxis=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=True,
            ticklen=10,
            ticks="outside",
            title="$",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
        ),
        yaxis2=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=False,
            ticklen=10,
            ticks="outside",
            title="%",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
            tickformat="%",
        ),
    )
    gross_profit_graph = make_subplots(specs=[[{"secondary_y": True}]])
    gross_profit_graph.add_trace(
        gross_profit_go, secondary_y=False,
    )
    gross_profit_graph.add_trace(
        gross_margin_go, secondary_y=True,
    )
    gross_profit_graph.update_layout(gross_profit_layout)
    active_inventory_go = go.Scatter(
        x=pd.to_datetime(filtered_master_df["ref_date"]),
        y=filtered_master_df["active_inventory_dollars"],
        name="Active Inventory",
        mode="lines",
    )
    active_inventory_layout = go.Layout(
        template="plotly_white",
        autosize=True,
        title="Active Inventory",
        font=dict(family="Raleway", size=14),
        hovermode="closest",
        legend=dict(x=-0.0277108433735, y=-0.142606516291, orientation="h",),
        margin=dict(r=10, t=60, b=10, l=10,),
        showlegend=True,
        xaxis=dict(
            autorange=True,
            linecolor="rgb(0, 0, 0)",
            linewidth=1,
            showgrid=False,
            showline=True,
        ),
        yaxis=dict(
            gridcolor="rgba(127, 127, 127, 0.2)",
            mirror=False,
            showgrid=True,
            showline=True,
            ticklen=10,
            ticks="outside",
            title="$",
            zeroline=False,
            zerolinewidth=4,
            rangemode="tozero",
        ),
    )
    active_inventory_graph = make_subplots(specs=[[{"secondary_y": True}]])
    active_inventory_graph.add_trace(
        active_inventory_go, secondary_y=False,
    )
    active_inventory_graph.update_layout(active_inventory_layout)

    return (
        revenue_graph,
        turnover_graph,
        gross_profit_graph,
        active_inventory_graph,
    )


@app.callback(
    [dash.dependencies.Output("daily_data_table", "data")],
    [dash.dependencies.Input("purchase-dropdown", "value"),],
)
def update_breakdown_figure(selected_date_filter):

    start_date, end_date = shared_filter(selected_date_filter)

    filtered_master_df = master_df.loc[
        (
            (pd.to_datetime(master_df["ref_date"]) >= start_date)
            & (pd.to_datetime(master_df["ref_date"]) <= end_date)
        )
    ].copy()
    filtered_master_df["DOW_name"] = pd.to_datetime(
        filtered_master_df["ref_date"]
    ).dt.day_name()
    filtered_master_df["Active Inventory"] = filtered_master_df[
        "active_inventory_dollars"
    ].map("${:,}".format)
    filtered_master_df["revenuet"] = (
        filtered_master_df["revenue"].round(1).map("${:,}".format)
    )
    filtered_master_df["cogst"] = (
        filtered_master_df["cogs"].round(1).map("${:,}".format)
    )
    filtered_master_df["Profit"] = (
        filtered_master_df["daily_gross_profit"].round(1).map("${:,}".format)
    )
    filtered_master_df["Margin"] = filtered_master_df["daily_gross_margin"].map(
        "{:.2%}".format
    )
    filtered_master_df["turnovert"] = filtered_master_df["turnover"].map(
        "{:.3%}".format
    )
    filtered_master_df["Purchases($)"] = (
        filtered_master_df["costs"].round(1).map("${:,}".format)
    )
    filtered_master_df = filtered_master_df[
        [
            "ref_date",
            "DOW_name",
            "Active Inventory",
            "revenuet",
            "cogst",
            "Profit",
            "Margin",
            "turnovert",
            "Purchases($)",
        ]
    ].copy()
    filtered_master_df.columns = [
        "Date",
        "Day of Week",
        "Active Inventory",
        "Revenue",
        "COGS",
        "Profit",
        "Margin",
        "Turnover",
        "Purchases($)",
    ]

    dff = filtered_master_df.sort_values("Date", ascending=False)
    dff["Date"] = dff["Date"].dt.strftime("%m/%d/%Y")

    return [dff.to_dict("records")]


app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == "__main__":
    app.run_server(debug=True)
