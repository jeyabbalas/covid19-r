import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from scipy.stats import sem
from datetime import datetime as dt
import pycountry

import covid_backend as covid

import plotly.graph_objs as go


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# allow exceptions from adding callbacks to elements that don't exist yet on layout
app.config.suppress_callback_exceptions = True

confirmed_data, epicurves, rcurves, countries_list, data_dates = covid.get_covid_data()


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
                                 dcc.Dropdown(id="value-selected", value='Total Cases',
                                              options=[{'label': "Log10 of Total Cases ", 'value': 'Total Cases'},
                                                       {'label': "Log10 of New Cases (on last reported day) ", 'value': 'New Cases'},
                                                       {'label': "Average Reproduction Number ", 'value': 'Average R'}],
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
        #dbc.Tab(regional_tab_content, label="Regional data"),
    ]
)

# home page layout
home_layout = dbc.Container([
    tabs,
    dcc.Interval(
        id='data-auto-update',
        interval=2160000,
        n_intervals=0),
    html.P(id='placeholder')
])


# about page layout
about_page_layout = dbc.Container([
    html.H1("What is this?"),
    html.Br(),
    html.H4("Who developed this website and why?"),
    html.P("""
        My name is Jeya Balaji Balasubramanian. I developed this website mainly
        to learn concepts surrounding web application development.
        """),
    html.P("""
        Functionally, the purpose of this website is to help monitor the extent
        of the current COVID-19 pandemic. It extracts global COVID-19 transmission dynamics
        data from Johns Hopkins University.
        """),
    html.P("""
        The contents of this website should be used with discretion as I do not have an
        epidemiological background.
        """),
    html.H4("What is the data source?"),
    html.P("From Johns Hopkins University, linked below—"),
    html.A("https://github.com/CSSEGISandData/COVID-19", href="https://github.com/CSSEGISandData/COVID-19"),
    html.P(),
    html.H4("What is Reproduction Number?"),
    html.P("""
        Reproduction number is a statistic that helps quantify the transmissibility of a disease.
        It is defined as the average number of secondary cases that an individual with the
        infection is likely to infect. This statistic depends upon the virality of the pathogen
        and the social conditions around the susceptible population. Therefore, this statistic
        can help in disease surveillence and to check if interventions like social distancing,
        quarantine, travel ban, vaccines, etc. have been effective.
        """),
    html.H4("How do you calculate the daily Reproduction Number?"),
    html.P("""
        I implemented the Wallinga-Teunis method (see References 1 and 2 below). I get the case
        incidence data from Johns Hopkins University (see above). I get the serial interval
        distribution from the gamma distribution parameters from reference 3 below.
        """),
    html.P("""
        Since the time-step is small here (daily), the estimates of R varies considerably increasing
        the risk of negative autocorrelation. To mitigate that, I calculate the estimates over a window
        of 3 days. For details of this method, see reference 1.
        """),
    html.H4("Contact me"),
    html.P("You can approach me on my LinkedIn page—"),
    html.A("https://www.linkedin.com/in/jbbalas", href="https://www.linkedin.com/in/jbbalas"),
    html.P(),
    html.H4("References"),
    html.P("""[1]\tCori A, Ferguson NM, Fraser C, Cauchemez S. A new framework and
        software to estimate time-varying reproduction numbers during epidemics. American
        journal of epidemiology. 2013 Nov 1;178(9):1505-12."""),
    html.P("""[2]\tWallinga J, Teunis P. Different epidemic curves for severe acute
        respiratory syndrome reveal similar impacts of control measures. American Journal
        of epidemiology. 2004 Sep 15;160(6):509-16.
        """),
    html.P("""
        [3]\tDu Z, Xu X, Wu Y, Wang L, Cowling BJ, Meyers LA. The serial interval of
        COVID-19 from publicly reported confirmed cases. medRxiv. 2020 Jan 1.
        """),

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
    country_iso_codes = covid.get_country_iso_codes()
    encoded_countries = list(countries_list)

    avg_r = np.zeros(len(countries_list), np.float32)
    for country in rcurves.keys():
        idx = countries_list.index(country)
        encoded_countries[idx] = country_iso_codes[countries_list[idx]]
        if len(rcurves[country]['mean_r'])==0:
            avg_r[idx] = 0.0
        avg_r[idx] = np.mean(rcurves[country]['mean_r'])

    map_data = np.vstack((np.array(encoded_countries), np.log10(np.max(confirmed_data, axis=1)), np.log10(epicurves[:,-1]), avg_r))
    map_df = pd.DataFrame(map_data.T, columns = ['Country', 'Total Cases', 'New Cases', 'Average R'])

    def title(text):
        if text == 'Total Cases':
            return "Log10 of Total Cases"
        elif text == 'New Cases':
            return "Log10 of Total New Cases (on last reported day)"
        else:
            return "Average R<sub>t</sub> over Time"
    trace = go.Choropleth(locations=map_df['Country'],z=map_df[selected],text=map_df['Country'],autocolorscale=False,
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
        Example— On March 11th, 2020, WHO declared COVID-19 as a pandemic; on March 18th,
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
    ref_date_dt = dt.strptime(ref_date[:10], "%Y-%m-%d")
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


@app.callback(Output('placeholder', 'children'),
             [Input('data-auto-update', 'n_intervals')],)
def update_data(n):
    confirmed_data, epicurves, rcurves, countries_list, data_dates = covid.get_covid_data()


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
