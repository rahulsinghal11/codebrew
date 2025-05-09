import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
from pathlib import Path
import json

class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__)
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.setup_layout()
        
    def load_data(self):
        """Load and process data for visualization"""
        try:
            with open(self.data_dir / 'sample_suggestion.json', 'r') as f:
                suggestions = json.load(f)
            return pd.DataFrame(suggestions)
        except FileNotFoundError:
            return pd.DataFrame()
            
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            html.H1('CodeBrew Analytics Dashboard'),
            
            html.Div([
                html.H2('Code Analysis Metrics'),
                dcc.Graph(id='metrics-graph'),
            ]),
            
            html.Div([
                html.H2('Recent Suggestions'),
                html.Div(id='suggestions-table')
            ]),
            
            dcc.Interval(
                id='interval-component',
                interval=30*1000,  # Update every 30 seconds
                n_intervals=0
            )
        ])
        
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port)

if __name__ == '__main__':
    dashboard = Dashboard()
    dashboard.run_server() 