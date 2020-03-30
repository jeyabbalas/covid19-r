import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from scipy.stats import sem
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
                                style={'textAlign': "left", "padding-bottom": "30"}),
                       html.Div([html.Span("Statistic to display : ", className="six columns",
                                           style={"text-align": "left", "padding-top": 10, "padding-left": 25}),
                                 dcc.Dropdown(id="value-selected", value='lifeExp',
                                              options=[{'label': "Population ", 'value': 'pop'},
                                                       {'label': "GDP Per Capita ", 'value': 'gdpPercap'},
                                                       {'label': "Life Expectancy ", 'value': 'lifeExp'}],
                                              style={"display": "block", "margin-left": 10, "margin-right": 10,
                                                     "margin-bottom":10, "width": "100%"},
                                              className="six columns")], className="row"),
                       dcc.Graph(id="choropleth_map"),
                    ],
                    ),
                    className="mt-1",
                )


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
                                    margin={'l': 40, 'r': 1,
                                            't': 45, 'b': 40},
                                    xaxis_title='Day',
                                    yaxis_title='Number of people',
                                    title='Epidemiological curves (new cases/day)',
                                    barmode='group',
                                    showlegend=True,
                                    legend=dict(orientation='h',xanchor='left',yanchor='bottom',y=-0.25),
                                    )})))

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
                                    margin={'l': 40, 'r': 1,
                                            't': 45, 'b': 40},
                                    xaxis_title='Day',
                                    yaxis_title='R<sub>t</sub>',
                                    title='Effective Reproduction Number (R<sub>t</sub>)',
                                    barmode='group',
                                    showlegend=True,
                                    legend=dict(orientation='h',xanchor='left',yanchor='bottom',y=-0.25),
                                    )})))

    return rcurve_graphs, [min_date, max_date]


countries_dropdown = html.Div([
            dcc.Dropdown(id='country-name',
                         options=[{'label': country, 'value': country}
                                  for country in countries_list],
                         value=['US'],
                         multi=True
                         ), ])


graphs_and_control = dbc.Card(dbc.CardBody(
                    [
                    html.H1('Visualizing COVID-19 dynamics'),
                    countries_dropdown,
                    dbc.Container(id="graph-content"),
                    ]
                    ), className="mt-3",
                    )

national_tab_content = dbc.Card(
    dbc.CardBody(
        [
            choropleth_map,
            html.Hr(),
            graphs_and_control,
        ]
    ),
    className="mt-3",
)


regional_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Under construction."),
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
    epi_graph = dbc.Col(dbc.Card(
        dbc.CardBody(
             get_epicurve_graphs(countries, epicurves, countries_list, data_dates)
            ), className="ml-0",
        ))

    r_curve_graphs, date_range = get_rcurve_graphs(countries, rcurves)

    r_graph = dbc.Col(dbc.Card(
        dbc.CardBody(
             r_curve_graphs
            ), className="ml-1",
        ))

    date_picker = dcc.DatePickerSingle(
                        id='r-date-picker',
                        min_date_allowed=date_range[0],
                        max_date_allowed=date_range[1],
                        initial_visible_month=dt.today(),
                        date=str(dt(2020,3,11)),
                        display_format="MMM Do, YY"
                    )

    description = html.P("""Pick a date of reference. This date can be the day
        some control measures were implemented in your region of interest.
        Example— On March 11th 2020, WHO declared COVID-19 as a pandemic; on March 18th,
        2020, US and Canada closed its borders for non-essential traffic; on March 9th,
        2020 the government of Italy imposed a national quarantine; on January 23rd, 2020,
        the government of China issued a lockdown on Wuhan and other cities in Hubei.""")

    eval_control = dbc.Col(dbc.Card(dbc.CardBody(
                    [
                    html.H2('Evaluating effectiveness of control measures'),
                    html.Br(),
                    description,
                    html.H6("Enter a date of reference: "),
                    date_picker,
                    html.P(),
                    html.H4("Comparing average R before/after date of reference"),
                    dbc.Container(id='r-evaluation'),
                    ])))

    graph_content = [
                    dbc.Row([epi_graph,r_graph], className="mt-3"),
                    dbc.Row([eval_control], className="mt-3",),
                    ]

    return graph_content


@app.callback(Output('r-evaluation', 'children'),
             [Input('r-date-picker', 'date'),
             Input('country-name', 'value')],)
def update_r_evaluation(ref_date, countries):
    ref_date_dt = dt.strptime(ref_date, "%Y-%m-%d %H:%M:%S")
    before_list = list([html.H6("Average R before "+ref_date_dt.strftime("%d %B, %Y"), className="card-title")])
    after_list = list([html.H6("Average R after "+ref_date_dt.strftime("%d %B, %Y"), className="card-title")])

    for country in countries:
        ref = np.argwhere((rcurves[country]['dates'] > ref_date_dt) == True)[0][0]
        before_mean = np.around(np.mean(rcurves[country]['mean_r'][:ref]), decimals=2)
        before_sem = np.around(sem(rcurves[country]['mean_r'][:ref]), decimals=2)
        after_mean = np.around(np.mean(rcurves[country]['mean_r'][ref:]), decimals=2)
        after_sem = np.around(sem(rcurves[country]['mean_r'][ref:]), decimals=2)
        before_list.append(html.P(country+": "+str(before_mean)+" \u00B1 "+str(before_sem)))
        after_list.append(html.P(country+": "+str(after_mean)+" \u00B1 "+str(after_sem)))


    evaluation_output = dbc.Row([
        dbc.Col(dbc.Card(dbc.CardBody(before_list))),
        dbc.Col(dbc.Card(dbc.CardBody(after_list))),
        ], className="mt-3")

    return [evaluation_output]


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
