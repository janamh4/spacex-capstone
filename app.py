import os
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

np.random.seed(42)
years = list(range(1980, 2014))
recession_years = [1980, 1981, 1982, 1991, 2000, 2001, 2007, 2008, 2009]
vehicle_types = ['Superminicar', 'Small Family Car', 'Medium Family Car', 'Executive Car', 'Sports']

data = []
for year in years:
    is_recession = 1 if year in recession_years else 0
    for month in range(1, 13):
        for vtype in vehicle_types:
            base_sales = np.random.randint(1000, 5000)
            if is_recession:
                base_sales = int(base_sales * 0.6)
            data.append({
                'Year': year,
                'Month': month,
                'Vehicle_Type': vtype,
                'Automobile_Sales': base_sales,
                'Advertising_Expenditure': np.random.uniform(100, 500),
                'unemployment_rate': np.random.uniform(6, 12) if is_recession else np.random.uniform(3, 6),
                'Recession': is_recession,
            })

df = pd.DataFrame(data)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': '24px',
            'padding': '20px 0'
        }
    ),

    html.Div([
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'},
            ],
            placeholder='Select a report type',
            style={'width': '45%', 'marginRight': '20px'}
        ),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': str(y), 'value': y} for y in range(1980, 2014)],
            placeholder='Select a year',
            style={'width': '45%'}
        ),
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'margin': '20px auto',
        'maxWidth': '900px'
    }),

    html.Div(id='output-container', style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'justifyContent': 'center',
        'padding': '20px'
    }),
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f9f9f9', 'minHeight': '100vh'})


@callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def update_year_dropdown(selected_statistics):
    return selected_statistics != 'Yearly Statistics'


@callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_output(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        recession_data = df[df['Recession'] == 1]

        yearly_avg = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(
            yearly_avg, x='Year', y='Automobile_Sales',
            title='Yearly Average Automobile Sales During Recession',
            markers=True
        ))

        avg_sales_vt = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.bar(
            avg_sales_vt, x='Vehicle_Type', y='Automobile_Sales',
            title='Average Sales by Vehicle Type During Recession',
            color='Vehicle_Type'
        ))

        adv_exp = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(
            adv_exp, values='Advertising_Expenditure', names='Vehicle_Type',
            title='Advertising Expenditure Share by Vehicle Type (Recession)'
        ))

        unemp_data = recession_data.groupby('Vehicle_Type')['unemployment_rate'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(
            unemp_data, x='Vehicle_Type', y='unemployment_rate',
            title='Average Unemployment Rate by Vehicle Type During Recession',
            color='Vehicle_Type'
        ))

        return [
            html.Div([R_chart1, R_chart2], style={'display': 'flex', 'width': '100%', 'flexWrap': 'wrap'}),
            html.Div([R_chart3, R_chart4], style={'display': 'flex', 'width': '100%', 'flexWrap': 'wrap'}),
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year:
        yearly_data = df[df['Year'] == input_year]

        yearly_trend = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(
            yearly_trend, x='Year', y='Automobile_Sales',
            title='Yearly Automobile Sales Trend (All Years)',
            markers=True
        ))

        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(
            monthly_sales, x='Month', y='Automobile_Sales',
            title=f'Monthly Sales for {input_year}',
            markers=True
        ))

        vtype_sales = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].sum().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(
            vtype_sales, x='Vehicle_Type', y='Automobile_Sales',
            title=f'Vehicle Type Sales in {input_year}',
            color='Vehicle_Type'
        ))

        adv_exp_year = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(
            adv_exp_year, values='Advertising_Expenditure', names='Vehicle_Type',
            title=f'Advertising Expenditure by Vehicle Type in {input_year}'
        ))

        return [
            html.Div([Y_chart1, Y_chart2], style={'display': 'flex', 'width': '100%', 'flexWrap': 'wrap'}),
            html.Div([Y_chart3, Y_chart4], style={'display': 'flex', 'width': '100%', 'flexWrap': 'wrap'}),
        ]

    return [html.P("Please select a report type to view the charts.",
                   style={'color': '#888', 'textAlign': 'center', 'width': '100%', 'marginTop': '40px'})]


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=False, host='0.0.0.0', port=port)
