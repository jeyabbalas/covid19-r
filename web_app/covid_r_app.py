import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
import covid_backend as covid
from datetime import datetime as dt

import plotly.graph_objs as go


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# allow exceptions from adding callbacks to elements that don't exist yet on layout
app.config.suppress_callback_exceptions = True

confirmed_data, epicurves, rcurves, countries_list, data_dates = covid.get_covid_data()
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')


website_navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("COVID-19 Control", href="/"),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("What is this?", href="/about")),
                ],
                className="ml-auto", navbar=True
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)


choropleth_map = dbc.Card(dbc.CardBody(
                    [
                    html.Div([html.H1("COVID-19 dynamics by country")],
                                style={'textAlign': "center", "padding-bottom": "30"}),
                       html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "40%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected", value='lifeExp',
                                              options=[{'label': "Population ", 'value': 'pop'},
                                                       {'label': "GDP Per Capita ", 'value': 'gdpPercap'},
                                                       {'label': "Life Expectancy ", 'value': 'lifeExp'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "70%"},
                                              className="six columns")], className="row"),
                       dcc.Graph(id="choropleth_map")
                    ],
                    ),
                    className="mt-1",
                )


def get_cases_graphs(countries, confirmed_data, countries_list, data_dates):
    cases_graphs = []

    idxs = [countries_list.index(country) for country in countries]

    data = []
    for idx in idxs:
        data.append(go.Scatter(
            x=list(data_dates),
            y=np.array(confirmed_data[idx]),
            mode='lines+markers',
            name=countries_list[idx]))

    max_cases = max([max(vals) for vals in confirmed_data[idxs]])
    max_cases = max_cases + max_cases*0.1

    cases_graphs.append(html.Div(dcc.Graph(
        id='cases_graphs',
        figure={'data': data,
                'layout': go.Layout(xaxis=dict(range=[min(data_dates), max(data_dates)]),
                                    yaxis=dict(range=[0, max_cases]),
                                    margin={'l': 50, 'r': 1,
                                            't': 45, 'b': 40},
                                    xaxis_title='Day',
                                    yaxis_title='Number of people',
                                    title='Total confirmed COVID-19 cases',
                                    showlegend=True)})))

    return cases_graphs


def get_epicurve_graphs(countries, epicurves, countries_list, data_dates):
    epicurve_graphs = []

    idxs = [countries_list.index(country) for country in countries]

    data = []
    for idx in idxs:
        data.append(go.Bar(x=list(data_dates[1:]),
                           y=np.array(epicurves[idx]),
                           name=countries_list[idx]))

    max_cases = max([max(vals) for vals in epicurves[idxs]])
    max_cases = max_cases + max_cases*0.1

    epicurve_graphs.append(html.Div(dcc.Graph(
        id='epi_graphs',
        figure={'data': data,
                'layout': go.Layout(xaxis=dict(range=[min(data_dates[1:]), max(data_dates[1:])]),
                                    yaxis=dict(range=[0, max_cases]),
                                    margin={'l': 50, 'r': 1,
                                            't': 45, 'b': 40},
                                    xaxis_title='Day',
                                    yaxis_title='Number of people',
                                    title='Epidemiological curves (total new COVID-19 cases per day)',
                                    barmode='group',
                                    showlegend=True)})))

    return epicurve_graphs


def get_rcurve_graphs(countries, rcurves):
    rcurve_graphs = []

    min_date = np.min(rcurves[countries[0]]['dates'])
    max_date = np.max(rcurves[countries[0]]['dates'])
    max_value = 0.0

    data = []
    for country in countries:
        if np.min(rcurves[country]['dates']) < min_date:
            min_date = np.min(rcurves[country]['dates'])
        if np.max(rcurves[country]['dates']) < max_date:
            max_date = np.max(rcurves[country]['dates'])
        if np.max(rcurves[country]['mean_r']) > max_value:
            max_value = np.max(rcurves[country]['mean_r'])
        data.append(go.Scatter(
            x=list(rcurves[country]['dates']),
            y=np.array(rcurves[country]['mean_r']),
            mode='lines+markers',
            name=country))

    # Rt=1 line for reference
    data.append(go.Scatter(
            x=[min_date, max_date],
            y=[1.0,1.0],
            mode='lines',
            name="R<sub>t</sub> = 1"))

    rcurve_graphs.append(html.Div(dcc.Graph(
        id='r_graphs',
        figure={'data': data,
                'layout': go.Layout(xaxis=dict(range=[min_date, max_date]),
                                    yaxis=dict(range=[0, max_value+2.0]),
                                    margin={'l': 50, 'r': 1,
                                            't': 45, 'b': 40},
                                    xaxis_title='Day',
                                    yaxis_title='R<sub>t</sub>',
                                    title='Change in effective Reproduction Number (R<sub>t</sub>)',
                                    barmode='group',
                                    showlegend=True)})))

    return rcurve_graphs


countries_dropdown = html.Div([
            dcc.Dropdown(id='country-name',
                         options=[{'label': country, 'value': country}
                                  for country in countries_list],
                         value=['US'],
                         multi=True
                         ), ])


national_tab_content = dbc.Card(
    dbc.CardBody(
        [
            choropleth_map,
            html.Hr(),
            html.H1('Visualizing COVID-19 dynamics'),
            countries_dropdown,
            dbc.Card(dbc.CardBody([dbc.Row(id="graph-content",),]), className="mt-3"),
            html.Hr(),
            html.H1('Evaluating control measures'),
        ]
    ),
    className="mt-3",
)


regional_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]
    ),
    className="mt-3",
)


tabs = dbc.Tabs(
    [
        dbc.Tab(national_tab_content, label="National data"),
        dbc.Tab(regional_tab_content, label="Regional data"),
    ]
)


date_picker = dcc.DatePickerSingle(
    id='my-date-picker-single',
    min_date_allowed=dt(1995, 8, 5),
    max_date_allowed=dt(2017, 9, 19),
    initial_visible_month=dt(2017, 8, 5),
    date=str(dt(2017, 8, 25, 23, 59, 59))
)



# home page layout
home_layout = dbc.Container([
    tabs,
])


# about page layout
about_page_layout = dbc.Container([
    html.H1('What is this?'),
])


# main layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    website_navbar,
    html.Div(id='page-content'),
    html.P(),
    html.Hr(),
    html.P(),
])


@app.callback(Output("choropleth_map", "figure"),
    [Input("value-selected", "value")])
def update_figure(selected):
    dff = df.groupby(['iso_alpha', 'country']).mean().reset_index()
    def title(text):
        if text == "pop":
            return "Poplulation (million)"
        elif text == "gdpPercap":
            return "GDP Per Capita (USD)"
        else:
            return "Life Expectancy (Years)"
    trace = go.Choropleth(locations=dff['iso_alpha'],z=dff[selected],text=dff['country'],autocolorscale=False,
                          colorscale="YlGnBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": title(selected), "side": "bottom"}})
    return {"data": [trace],
            "layout": go.Layout(title=title(selected),height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}


@app.callback(Output("graph-content", "children"),
             [Input('country-name', 'value')],)
def render_graph_content(countries):
    cases_graph = dbc.Col(dbc.Card(
        dbc.CardBody(
             get_cases_graphs(countries, confirmed_data, countries_list, data_dates)
            ), className="ml-2",
        ), width="auto")


    epi_graph = dbc.Col(dbc.Card(
        dbc.CardBody(
             get_epicurve_graphs(countries, epicurves, countries_list, data_dates)
            ), className="ml-2",
        ), width="auto")


    r_graph = dbc.Col(dbc.Card(
        dbc.CardBody(
             get_rcurve_graphs(countries, rcurves)
            ), className="ml-2",
        ), width="auto")

    return [cases_graph, epi_graph, r_graph,]


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')],)
def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/about':
        return about_page_layout
    else:
        return home_layout


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
