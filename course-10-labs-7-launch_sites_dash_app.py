# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {'label': 'All sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options = dropdown_options,
                                    value = 'ALL',
                                    placeholder = 'Select a Launch Site here',
                                    searchable = True,
                                ),
                                html.Br(),
                                
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                step=1000,
                                                marks={0: '0', 5000: '5000', 9600: '9600'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df.groupby('Launch Site')['class'].mean().reset_index()
        fig = px.pie(data, values='class', 
                    names='Launch Site', 
                    title='Total Successful Launches for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data = filtered_df['class'].value_counts()
        fig = px.pie(data, 
                    values=data.values, 
                    names=data.index.map({1 : 'Success', 0 : 'Failure'}),
                    color=data.index,
                    color_discrete_map={1 : '#00CC96', 0 : '#EF553B'},
                    title=f'Distribution of Success Launches for Site {entered_site} Site')
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])
def get_payload_scatter_chart(entered_site,payload_value):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_value[0]) & (spacex_df['Payload Mass (kg)'] <= payload_value[1])]
    if entered_site == 'ALL':
        fig = px.scatter(filtered_df, 
                        x = 'Payload Mass (kg)', 
                        y = filtered_df['class'],
                        labels = {'class' : "Class"},
                        color = 'Booster Version Category',
                        title = 'Correlation between Payload and Launch Success at All Sites')
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, 
                        x = 'Payload Mass (kg)', 
                        y = filtered_df['class'],
                        labels = {'class' : "Class"},
                        color = 'Booster Version Category',
                        title = f'Correlation between Payload and Launch Success at Site {entered_site}')

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
