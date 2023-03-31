# -*- coding: utf-8 -*-
"""3.1 The model of a vertical well.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UH7-gbKqTHf3m4H95WqC-EBI66_DxKKd
"""

import numpy as np
import anaflow
import scipy.special as sc
import matplotlib.pyplot as plt
from mpmath import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.special import kn, iv, expi
mp.dps = 15; mp.pretty = True

"""##Задача
###Рассмотрим неустановившийся приток жидкости к вертикальной скважине, полностью вскрывшей бесконечный однородный пласт толщины h с начальным давлением pi.

###Исходные данные
"""

q = 0.00092  # [m3/c] - дебит скважины
B = 1.25  # [m3/m3] - объемный коэффициент
k = 50*1e-15  # [m2] - изотропная проницаемость
h = 9.144  # [m] - толщина пласта
f = 0.3  # [] - пористость
c = 1.47*1e-9  # [1/Pa] - сжимаемость флюида
cf = 1 * 1e-9  # [1/Pa] - сжимаемость породы
ct = (c + cf)  # [1/Pa] - общая породы
rw = 0.1524  # [m] - радиус ствола скважины
r = 0.1524  # [m] - радиальная координата и расстояние
mu = 3*1e-3  # [Pa*c] - вязкость
eta = k / (mu * f * ct)  # коэф пьезопроводности
l = rw
PI = 3.44738E+7

"""# Решение относительно распределения давления
$$ \Delta p(s) = \dfrac {qB\mu}{2\pi k h} \dfrac{K_0 (\sqrt{\dfrac{s}{\eta}}r)}{s\sqrt{\dfrac{s}{\eta}}r_w K_1(\sqrt{\dfrac{s}{\eta}}r_w)}$$

## Решение для линейного источника
$$ \Delta p(r,t) = - \dfrac {q B \mu} {4 \pi k h} E_i(- \dfrac {r^2} {4 \eta t})$$
"""

# Решение для линейного источника
def pd_ei (r, t, q = q, B = B, k = k, h = h, mu = mu, eta = eta, f = f):
    return -q * B * mu /(4 * np.pi * k * h) * sc.expi(-r ** 2 /(4 * eta * t))

# Решение с учетом конечного радиуса скважины
def pd_lapl (s, r = r, r_w = rw, q = q, B = B, k = k, h = h, mu = mu, eta = eta, f = f):
    return q * B * mu / (2 * np.pi * k * h) * sc.kn(0, r * (s / eta) ** 0.5) /(s * r_w * (s / eta)** 0.5 * sc.kn(1, r_w * (s / eta) ** 0.5))

# Решение с учетом конечного радиуса скважины
def pd_lapl_1 (s, r = r, r_w = rw, q = q, B = B, k = k, h = h, mu = mu, eta = eta, f = f):
    return q * B * mu / (2 * np.pi * k * h) * besselk(0, r * (s / eta) ** 0.5) /(s * r_w * (s / eta)** 0.5 * besselk(1, r_w * (s / eta) ** 0.5))

# Решение с учетом конечного радиуса скважины
def pd_lapl_2 (s, r = r, r_w = rw, q = q, B = B, k = k, h = h, mu = mu, eta = eta, f = f):
    return q * B * mu / (2 * np.pi * k * h * s) * sc.kn(0, (s) ** 0.5)

# реализация функции расчета безразмерного давления на основе преобразования Лапласа
def pd_line_source_lapl(r, t):
    fp = lambda p: pd_lapl_1(p)
    return invertlaplace(fp, t, method='stehfest', degree = 5)

pd_ls_func = np.vectorize(pd_line_source_lapl)

#path = 'https://raw.githubusercontent.com/AvtomonovPavel/Method-of-sources/main/Examples/example_3.1.1'
#df = pd.read_table(path, sep='\s+', engine = 'python')

t = np.logspace(-1, 4, 100)
fig, ax1 = plt.subplots()
fig.set_size_inches(16, 8)
pd_ls = anaflow.get_lap_inv(pd_lapl)
ax1.plot(t, pd_ls(t)/100000, label = 'Конечный радиус ')
plt.title("Вертикальная скважина")
ax1.plot(t, pd_ei(r, t)/100000, label = ' Линейный источник')
#ax1.plot(df['dTime'], (df['p-p@dt=0'])/100000,'o', label = 'Результаты коммерческого симмулятора')
#ax1.set_xscale('log')
#ax1.set_yscale('log')
ax1.legend()
ax1.grid()
plt.xlabel("t, c")
plt.ylabel("dP, Па")

# !/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import dash
from dash import html
import numpy as np
from dash import dcc
import pprint
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State


params_geo_table = [
    'Объемный коэффициент, м3/м3', 'Проницаемость, мД', 'Толщина пласта, м', 'Пористость',
    'Полная сжимаемость, 1/МПа', 'Вязкость нефти, мПа', 'Начальное пластовое давление, МПа'
]
values_geo_table = [1.25, 50, 9.144, 0.3, 0.00247, 3, 34.47 ]
params_well_table = [
    'Тип скважины', 'X координата', 'Y координата', 'Z координата',
    'Радиус скважины, м', 'Дебит скважины, м3/сут'
]
# Инициализация
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP] , suppress_callback_exceptions = True)
def change_wells_graph(value):
    trace_list = []
    print(value)
    trace_list.append(go.Scatter(visible=True, x=value,
                                 y=[1, 21, 31], line=dict(color='red', dash='dot'), name="Клапан 1"))

    traces = [trace_list]
    data = [val for sublist in traces for val in sublist]

    figure = {'data': data,
              'layout': go.Layout(
                  paper_bgcolor='white',
                  plot_bgcolor='white',
                  margin={'b': 10, 'r': 0, 'l': 60, 't': 20},
                  hovermode='x',
                  height=750,
                  # title={'text': 'Зависимость давления', 'font': {'color': 'Black'}, 'x': 0.55},
                  xaxis={'tickcolor': 'black', 'position': 1},
                  yaxis1={'title': 'MD', 'tickcolor': 'black', 'tickfont': {'color': 'black', },
                          'position': 0.01, },
                  yaxis2={'title': 'TVD', 'tickcolor': 'red', 'tickfont': {'color': 'red', },
                          'autorange': "reversed", "linecolor": 'black', 'overlaying': 'y', 'position': 0.9},

              ),

              }

    return figure
def change_pagecontent(pathname):
    if pathname == "/":
        return [
            html.Div([
                dbc.Row([
                    dbc.Col([html.Div('Анализ работы скважины')], width=12,
                            style={'font-size': 48, 'textAlign': 'center', 'font-style': 'oblique', 'margin-top': 10,
                                   'color': 'black'}),
                ]),
                dbc.Row([
                    dbc.Col([html.Div('Автомонов П.Ю. (avtpavel1@gmail.com)')], width=12,
                            style={'font-size': 40, 'textAlign': 'center', 'font-style': 'normal', 'color': 'black',
                                   'block-size': '80px'}),
                ]),

                dbc.Row([
                    dbc.Col([html.Div('Цели и задачи проекта:')], width=12,
                            style={'font-size': 40, 'textAlign': 'start', 'font-style': 'normal','margin-left': 15,
                                   'font-weight': ' bold', 'color': 'black', 'font-optical': 'sizing: none',
                                   'background-color': '#edf3f4'}),
                ]),

                dbc.Row([
                    dbc.Col([html.Div(' Функционал:')], width=12,
                            style={'font-size': 40, 'margin-top': 10, 'font-style': 'normal',
                                   'color': 'black', 'font-weight': ' bold', 'background-color': '#edf3f4', 'margin-left': 15,}),
                ]),
            ],style=CONTSTYLE_new ),
        ]
    elif (pathname == "/page1"):
        return [
            html.Div([
                dcc.Store(id='local_param', storage_type='local'),
                dcc.Store(id='local_contur', storage_type='local'),
                dcc.Store(id='local_teplo', storage_type='local'),
                dcc.Store(id='local_line', storage_type='local'),
                dbc.Row([
                    dbc.Col([html.Div('Анализ работы скважины')], width=12,
                            style={'font-size': 48, 'textAlign': 'center', 'font-style': 'oblique', 'margin-top': 10,
                                   'color': 'black'}),
                ]),
                html.Hr(),
                html.Div(id="number-out"),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Div('Геолого-физическая характеристика пласта')], width=12,
                                    style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique', 'margin-top': 10,
                                            'color': 'black'}),
                                 ]),
                        dbc.Row([
                        dash_table.DataTable(
                            id='table-geo',
                            columns=(
                                [{'id': 'Parameter', 'name': 'Parameter'}] +
                                [{'id': 'Value', 'name': 'Value'}]
                            ),
                            data=[
                                dict(Parameter=params_geo_table[i], Value = values_geo_table[i])
                                for i in range(len(params_geo_table))
                            ],
                            editable=True
                        ),
                    ])], width=6, style = {'margin-left': 14}),

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Div('Выберите модель пласта')], width=12,
                                    style={'font-size': 24, 'textAlign': 'left', 'font-style': 'oblique',
                                           'margin-top': 10,
                                           'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(id='dropdown-model-reservoir', options=['Бесконечный', 'Круговой', 'Прямоугольный параллелепипед'], value='Бесконечный')
                                ]),
                            ]),
                        dbc.Row([
                            dbc.Col([html.Div('Выберите модель границ')], width=12,
                                    style={'font-size': 24, 'textAlign': 'left', 'font-style': 'oblique',
                                           'margin-top': 10,
                                           'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(id='dropdown-model-boundary', options = ['Непротекаемые', 'Постоянное давление', 'Смешанные'], value = 'Непротекаемые')
                                ]),
                            ]),

                        ], style = {'margin-top': 60}),
            ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Div('Характеристика скважины')], width=12,
                                style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                       'margin-top': 10,
                                       'color': 'black'}),
                        ]),
                        dbc.Row([
                            dash_table.DataTable(
                                id='table_wells',
                                columns=[{'name': 'Скважина',
                                         'id': 'Well'}]+[{
                                    'name': '{}'.format(i),
                                    'id': '{}'.format(i),
                                    #'deletable': True,
                                    #'renamable': True
                                } for i in params_well_table],
                                data=[

                                ],
                                editable=True,
                                row_deletable=True,
                            ),



                            dbc.Button('Add Row', id='editing-rows-button', n_clicks=0),
                            html.Div(id='editing-prune-data-output')
                        ])], width=6, style={'margin-left': 14}),

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Div('Расстановка скважин')], width=12,
                                    style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                       'margin-top': 10,
                                           'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id="graph_wells", config={'displayModeBar': True}, animate=False)
                            ], style = {}),
                        ]),


                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Button( "Start / Stop", id='submit-val', n_clicks=0),
                        html.Div(id='container-button-basic',
                                 children='Press submit')],  style={"margin-left":14})
                    ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Div('Изменение параметров работы скважин')], width=12,
                                style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                       'margin-top': 10,
                                       'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id = "graph_param_wells",figure=go.Figure(
                                    data=[go.Scatter(x=[100, 200, 300], y=[300, 200, 300], marker=dict(size=18))],
                                    layout=go.Layout(height=500, width=700, paper_bgcolor="rgba(0, 0, 0, 0)", margin=dict(l=0, r=0, t=0, b=0))))
                            ], style={}),
                        ])], width=6, style={'margin-left': 14}),

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Div('Контурная карта давлений')
                                     ], width=12,
                                    style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                           'margin-top': 10,
                                           'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                     dcc.Dropdown(id='dropdown-contur', options=['XY', 'XZ', 'YZ'], value='XY'),
                                     ], width=4,
                                    style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                           'margin-top': 10,
                                           'color': 'black'},

                            ),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id = "graph_contur", figure=go.Figure(
                                    data=[go.Scatter(x=[100, 200, 300], y=[300, 200, 300], marker=dict(size=18))],
                                    layout=go.Layout(height=500, width=700, paper_bgcolor="rgba(0, 0, 0, 0)", margin=dict(l=0, r=0, t=0, b=0))))
                            ], style={}),
                        ]),

                    ]),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                html.Div('Тепловая карта давлений')], width=12,
                                style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                       'margin-top': 10,
                                       'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(id='dropdown-contur', options=['XY', 'XZ', 'YZ'], value='XY'),
                            ], width=4,
                                style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                       'margin-top': 10,
                                       'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id = "graph_teplo", figure=go.Figure(
                                    data=[go.Scatter(x=[100, 200, 300], y=[300, 200, 300], marker=dict(size=18))],
                                    layout=go.Layout(height=500, width=700, paper_bgcolor="rgba(0, 0, 0, 0)",margin=dict(l=0, r=0, t=0, b=0))))
                            ], style={}),
                        ])], width=6, style={'margin-left': 14}),

                    dbc.Col([
                        dbc.Row([
                            dbc.Col([html.Div('Линии тока')], width=12,
                                    style={'font-size': 24, 'textAlign': 'center', 'font-style': 'oblique',
                                           'margin-top': 10,
                                           'color': 'black'}),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dcc.Graph(id = "graph_line", figure=go.Figure(
                                    data=[go.Scatter(x=[100, 200, 300], y=[300, 200, 300], marker=dict(size=18))],
                                    layout=go.Layout(height=500, width=700, paper_bgcolor="rgba(0, 0, 0, 0)", margin=dict(l=0, r=0, t=0, b=0))))
                            ], style={}),
                        ]),

                    ]),
                ]),
                dbc.Row([
                    dbc.Col([html.Div('Модель скважины')], width=12,
                            style={'font-size': 48, 'textAlign': 'center', 'font-style': 'oblique', 'margin-top': 10,
                                   'color': 'black','background-color':'#edf3f4'}),
                ]),

            ], style=CONTSTYLE_new),
        ]







# СТИЛИ

SIDESTYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "background-color": "#8ea9c1",
}
CONTSTYLE_new  = {
    "left": "16rem",
    "right": 0,
    "background-color": "#d6e4ea",
}
CONTSTYLE = {
    "margin-left": "16rem",
    "margin-right": "0rem",
    "bottom": 0,
    "background-color": "#d6e4ea",
}


app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(
        [
            html.P("АРС",
                   style={'color': 'black', 'textAlign': 'Center', 'font-size': 60
                          }),
            html.Hr(style={'color': 'black'}),
            dbc.Nav(
                [
                    dbc.NavLink("Титульный лист", href="/", active="exact",
                                style={'color': 'black', 'textAlign': 'Center', 'font-size': 28, 'font-style': 'oblique'
                                       }),
                    dbc.NavLink("Расчетный модуль", href="/page1", active="exact",
                                style={'color': 'black', 'textAlign': 'Center', 'font-size': 28, 'font-style': 'oblique'
                                       }),
                ], vertical=True, pills=True),
            html.P("Version 1.0",
                   style={'color': 'black', 'textAlign': 'Center', 'font-size': 32, "margin-top": "200%",
                          'font-style': 'oblique'
                          }),
            html.P("Автомонов П.Ю.",
                   style={'color': 'black', 'textAlign': 'Center', 'font-size': 32, "margin-top": "0%",
                          'font-style': 'oblique'
                          }),
            html.P("avtpavel1@gmail.com",
                   style={'color': 'black', 'textAlign': 'Center', 'font-size': 26, "margin-top": "0%",
                          'font-style': 'oblique'
                          })
        ],
        style=SIDESTYLE,
    ),
    html.Div(id="page-content", children=[
    ], style=CONTSTYLE)
])


#################################################################################################################

# Callbacks

@app.callback(
    Output('table_wells', 'columns'),
    Input('editing-columns-button', 'n_clicks'),
    State('table_wells-name', 'value'),
    State('table_wells', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@app.callback(
    Output("graph_wells", 'figure'),
    Input('table_wells', 'data'),
    Input('table_wells', 'columns'))
def display_output(rows, columns):
    colors = []
    types = []
    type_wells = [row.get('Тип скважины', None) for row in rows]
    for i in type_wells:
        if (i == "0"):
            colors.append("blue")
            types.append("Добывающая")
        elif((i == "1")):
            colors.append("red")
            types.append("Добывающая")
        else:
            types.append("Неверно определен тип")

    return {
        'data':
            [go.Scatter(x=([row.get('X координата', None) for row in rows]),
                        y=([row.get('Y координата', None) for row in rows]),
                        mode='markers',
                        marker=dict(size=18, color=colors),
                        showlegend=True)
            ],
        'layout' : {'height':'250', 'width':'700', 'paper_bgcolor':"rgba(0, 0, 0, 0)",'plot_bgcolor':"rgba(0, 0, 0, 0)", 'margin':dict(l=10, r=0, t=0, b=15)}
    }


# CALLBACKS OF ZERO PAGE
@app.callback(Output("page-content", "children"),
              [Input("url", "pathname")])
def pagecontent(pathname):
    return change_pagecontent(pathname)
@app.callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
)
def update_output(n_clicks):
    return ' The button has been clicked {} times'.format(
        n_clicks
    )

@app.callback(
    Output('table_wells', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table_wells', 'data'),
    State('table_wells', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(Output('local_param', 'data'),
              Output('local_contur', 'data'),
              Input('table-geo', 'data'),
              Input('table_wells', 'data'),
              Input('submit-val', 'n_clicks'))
def on_data(rows_in_geo, rows_in_wells, n_clicks):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate
    # Data from geoTable
    B = float(rows_in_geo[0]['Value'])
    k = float(rows_in_geo[1]['Value']) * 10 ** (-15)  # [m2]
    h = float(rows_in_geo[2]['Value'])
    f = float(rows_in_geo[3]['Value'])
    ct = float(rows_in_geo[4]['Value']) * 10 ** (-6)
    mu = float(rows_in_geo[5]['Value']) * 10 ** (-3)
    PI = float(rows_in_geo[6]['Value']) * 10 ** (6)

    #q = [row.get('Дебит скважины, м3/сут', None) / 86400 for row in rows_in_wells]
    #rw = [row.get('Радиус скважины, м', None) for row in rows_in_wells]
    #r = rw[0]
    t = np.logspace(-1, 4, 100)
    result_well_param = []
    result_well_param.append([i for i in t])
    result_well_param.append(pd_ei(0.1, t, q = 0.00092, B = B, k = k, h = h, mu = mu, eta = eta, f = f) / 1000000)

    # зададим параметры воронки депрессии
    r_e = 300

    # зададим координатную сетку основываясь на параметрах
    x = np.linspace(-r_e, r_e, 100)
    y = np.linspace(-r_e, r_e, 100)
    z = np.linspace(-h / 2, h / 2, 100)
    # рассчитаем вспомогательные вектора для построения сетки
    xv, yv = np.meshgrid(x, y)
    xvz, zvz = np.meshgrid(x, z)
    # зададим координаты скважины
    xwell1 = 0
    ywell1 = 0
    zwell1 = z
    # рассчитаем значение давлений во всех точках сетки
    p_mesh_full = pd_ei(r=((xv - xwell1) ** 2 + (yv - ywell1) ** 2 + (
    [[(zvz[i][j] - zwell1[i]) ** 2 for i in range(x.size)] for j in range(y.size)])) ** 0.5,
                        t=100000000, q = 0.00092, B = B, k = k, h = h, mu = mu, eta = eta, f = f)
    p_mesh_xz = pd_ei(r=((xv - xwell1) ** 2 + (0) ** 2 + (
    [[(zvz[i][j] - zwell1[i]) ** 2 for i in range(x.size)] for j in range(y.size)])) ** 0.5,
                      t=100000000, q = 0.00092, B = B, k = k, h = h, mu = mu, eta = eta, f = f)
    result_contur = []
    result_contur.append(list(x))
    result_contur.append(list(y))
    result_contur.append(list(p_mesh_full))
    # удалим значения за контуром, так как в данном случае они не имеют смысла
    # p_mesh[np.where(p_mesh > pres)] = pres
    if (n_clicks %2 == 1):
        return result_well_param, result_contur
    else:
        return [[0], [0]], [[0], [0], [0]]

@app.callback(Output("graph_param_wells", 'figure'),
              Input('submit-val', 'n_clicks'),
              Input('local_param', 'modified_timestamp'),
              State('local_param', 'data'))
def on_data(n_clicks, ts, data):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate
    if ts is None:
        raise PreventUpdate
    return {
        'data':
            [go.Scatter(x=data[0],
                        y=data[1],
                        marker=dict(size=18))
             ],
        'layout': {'height': '250', 'width': '700', 'paper_bgcolor': "rgba(0, 0, 0, 0)",
                   'plot_bgcolor': "rgba(0, 0, 0, 0)", 'margin': dict(l=10, r=0, t=0, b=15)}
    }

@app.callback(Output("graph_contur", 'figure'),
              Input('submit-val', 'n_clicks'),
              Input('local_contur', 'modified_timestamp'),
              State('local_contur', 'data'))
def on_data(n_clicks, ts, data):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate
    if ts is None:
        raise PreventUpdate
    #print(list(data))
    #print([i for i in np.array(data[0])])
    return {
        'data':[go.Contour( x = data[0],
                            y = data[1],
                            z = data[2])
             ],
        'layout' : {'height':'250', 'width':'700', 'paper_bgcolor':"rgba(0, 0, 0, 0)",'plot_bgcolor':"rgba(0, 0, 0, 0)", 'margin':dict(l=10, r=0, t=0, b=15)}
    }


# Запуск
if __name__ == '__main__':
    app.run_server(debug = True)





