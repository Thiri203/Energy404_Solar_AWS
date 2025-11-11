"""
app_dash.py — Dash frontend for Energy404
-------------------------------------------
Interactive web interface for predicting rooftop solar potential.
Works with FastAPI backend (api.py) and prediction pipeline (predict.py).
"""
import os
import dash
from dash import dcc, html, Input, Output, State
import requests
from dash.exceptions import PreventUpdate

# ===== Configuration =====
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# ===== Initialize Dash App =====
app = dash.Dash(
    __name__,
    title="Energy404 - Solar Potential Estimator",
    suppress_callback_exceptions=True
)

# ===== Fetch metadata from API =====
def fetch_metadata():
    """Fetch cities, building types, and tilt range from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/metadata", timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Warning: Could not fetch metadata from API: {e}")
        # Fallback to hardcoded values
        return {
            "cities": ['Colombo', 'Maldives', 'Karachi', 'Beirut', 'Antigua', 'Izmir',
                      'Honduras', 'Panama', 'Nairobi', 'Lagos', 'LagosState',
                      'Samarkand', 'Accra', 'Mexico City', 'SouthAfrica', 'DarEsSalaam',
                      'Almaty', 'Manila', 'GreatDhakaRegion', 'Grenada'],
            "building_types": ['commercial', 'hotels', 'industrial', 'multifamily residential',
                             'peri-urban settlement', 'public health facilities',
                             'public sector', 'schools', 'single family residential',
                             'small commercial'],
            "tilt_range": [0, 60]
        }

metadata = fetch_metadata()
CITIES = sorted(metadata["cities"])
BUILDING_TYPES = sorted(metadata["building_types"])
TILT_MIN, TILT_MAX = metadata["tilt_range"]

# ===== Layout =====
app.layout = html.Div([
    # Header with Energy404 branding
    html.Div([
        html.Div([
            # Logo and title on the left
            html.Div([
                html.Div([
                    # Sun icon
                    html.Div("☀", style={
                        'fontSize': '3.5rem',
                        'marginRight': '0.35rem'
                    }),
                    html.Div([
                        html.H1("Energy404", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '700',
                            'color': '#78350f',
                            'margin': '0',
                            'lineHeight': '1'
                        }),
                        html.P("Solar Potential Estimator", style={
                            'fontSize': '0.875rem',
                            'color': '#92400e',
                            'margin': '0',
                            'marginTop': '0.15rem'
                        })
                    ])
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ])
        ], style={
            'maxWidth': '1400px',
            'margin': '0 auto',
            'padding': '1rem 1.5rem'
        })
    ], style={
        'backgroundColor': "#f9f9f9",
        'borderBottom': '1px solid #fbbf24'
    }),
    
    # Hero Section
    html.Div([
        html.Div([
            # Powered by badge
            html.Div([
                html.Span("⚡", style={'marginRight': '0.5rem'}),
                html.Span("Powered by LGBM+XGB+RF Ensemble Model")
            ], style={
                'display': 'inline-block',
                'padding': '0.5rem 1.25rem',
                'backgroundColor': '#fef3c7',
                'border': '1px solid #f59e0b',
                'borderRadius': '2rem',
                'fontSize': '0.875rem',
                'color': '#92400e',
                'fontWeight': '500',
                'marginBottom': '1.5rem'
            }),
            
            # Main heading
            html.H1("Estimate Annual Solar Energy Potential", style={
                'fontSize': '3.5rem',
                'fontWeight': '700',
                'color': '#1f2937',
                'marginBottom': '1rem',
                'lineHeight': '1.1'
            }),
            
            # Description
            html.P([
                "Use this tool to estimate annual ",
                html.Strong("solar energy potential (kWh/m²/year)", style={'color': '#1f2937'}),
                " for rooftops across 20 global cities using the tuned LGBM+XGB+RF ensemble model."
            ], style={
                'fontSize': '1.125rem',
                'color': '#6b7280',
                'maxWidth': '900px',
                'margin': '0 auto',
                'lineHeight': '1.6'
            })
        ], style={
            'textAlign': 'center',
            'marginBottom': '3rem'
        }),
        
        # Feature Cards
        html.Div([
            # 20 Global Cities
            html.Div([
                html.Div([
                    html.Div("☀", style={
                        'fontSize': '2rem',
                        'marginBottom': '1rem'
                    }),
                    html.H3("20 Global Cities", style={
                        'fontSize': '1.25rem',
                        'fontWeight': '600',
                        'color': '#1f2937',
                        'marginBottom': '0.5rem'
                    }),
                    html.P("Coverage across diverse climate zones worldwide", style={
                        'fontSize': '0.875rem',
                        'color': '#6b7280',
                        'lineHeight': '1.5'
                    })
                ], style={
                    'backgroundColor': '#fef3c7',
                    'padding': '2rem',
                    'borderRadius': '1rem',
                    'textAlign': 'center',
                    'height': '100%'
                })
            ], style={'flex': '1'}),
            
            # High Accuracy
            html.Div([
                html.Div([
                    html.Div("📈", style={
                        'fontSize': '2rem',
                        'marginBottom': '1rem'
                    }),
                    html.H3("High Accuracy", style={
                        'fontSize': '1.25rem',
                        'fontWeight': '600',
                        'color': '#1f2937',
                        'marginBottom': '0.5rem'
                    }),
                    html.P("Advanced ensemble machine learning model", style={
                        'fontSize': '0.875rem',
                        'color': '#6b7280',
                        'lineHeight': '1.5'
                    })
                ], style={
                    'backgroundColor': '#fef3c7',
                    'padding': '2rem',
                    'borderRadius': '1rem',
                    'textAlign': 'center',
                    'height': '100%'
                })
            ], style={'flex': '1'}),
            
            # Instant Results
            html.Div([
                html.Div([
                    html.Div("⚡", style={
                        'fontSize': '2rem',
                        'marginBottom': '1rem'
                    }),
                    html.H3("Instant Results", style={
                        'fontSize': '1.25rem',
                        'fontWeight': '600',
                        'color': '#1f2937',
                        'marginBottom': '0.5rem'
                    }),
                    html.P("Get predictions in real-time via API", style={
                        'fontSize': '0.875rem',
                        'color': '#6b7280',
                        'lineHeight': '1.5'
                    })
                ], style={
                    'backgroundColor': '#fef3c7',
                    'padding': '2rem',
                    'borderRadius': '1rem',
                    'textAlign': 'center',
                    'height': '100%'
                })
            ], style={'flex': '1'})
        ], style={
            'display': 'flex',
            'gap': '1.5rem',
            'marginBottom': '4rem'
        })
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '3rem 2rem'
    }),
    
    # Main Content - Two Column Layout
    html.Div([
        html.Div([
            # Left Column - Input Form
            html.Div([
                html.Div([
                    html.H2("Configuration", style={
                        'fontSize': '1.5rem',
                        'fontWeight': '600',
                        'color': '#1f2937',
                        'marginBottom': '1.5rem'
                    }),
                    
                    # City Selection
                    html.Div([
                        html.Label("City", style={
                            'display': 'block',
                            'fontSize': '0.875rem',
                            'fontWeight': '600',
                            'color': '#374151',
                            'marginBottom': '0.5rem'
                        }),
                        dcc.Dropdown(
                            id='city-dropdown',
                            options=[{'label': city, 'value': city} for city in CITIES],
                            value=CITIES[0],
                            clearable=False,
                            style={'borderRadius': '0.5rem'}
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    # Building Type Selection
                    html.Div([
                        html.Label("Building Type", style={
                            'display': 'block',
                            'fontSize': '0.875rem',
                            'fontWeight': '600',
                            'color': '#374151',
                            'marginBottom': '0.5rem'
                        }),
                        dcc.Dropdown(
                            id='building-type-dropdown',
                            options=[{'label': bt, 'value': bt} for bt in BUILDING_TYPES],
                            value=BUILDING_TYPES[0],
                            clearable=False,
                            style={'borderRadius': '0.5rem'}
                        )
                    ], style={'marginBottom': '1.5rem'}),
                    
                    # Tilt Angle Slider
                    html.Div([
                        html.Label("Tilt Angle", style={
                            'display': 'block',
                            'fontSize': '0.875rem',
                            'fontWeight': '600',
                            'color': '#374151',
                            'marginBottom': '0.5rem'
                        }),
                        html.Div(id='tilt-display', style={
                            'fontSize': '2.5rem',
                            'fontWeight': '700',
                            'color': '#92400e',
                            'textAlign': 'center',
                            'marginBottom': '0.5rem'
                        }),
                        dcc.Slider(
                            id='tilt-slider',
                            min=TILT_MIN,
                            max=TILT_MAX,
                            step=1,
                            value=20,
                            marks={i: str(i) + '°' for i in range(TILT_MIN, TILT_MAX + 1, 10)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ], style={'marginBottom': '2rem'}),
                    
                    # Calculate Button
                    html.Button(
                        "Calculate Potential",
                        id='predict-button',
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '1rem',
                            'fontSize': '1rem',
                            'fontWeight': '600',
                            'color': 'white',
                            'backgroundColor': '#92400e',
                            'border': 'none',
                            'borderRadius': '0.5rem',
                            'cursor': 'pointer'
                        }
                    )
                ], style={
                    'backgroundColor': 'white',
                    'padding': '2rem',
                    'borderRadius': '1rem',
                    'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
                })
            ], style={'flex': '1'}),
            
            # Right Column - Results
            html.Div([
                html.Div(id='results-container', children=[
                    html.Div([
                        html.H2("Prediction Results", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'color': '#1f2937',
                            'marginBottom': '2rem'
                        }),
                        html.Div([
                            html.Div("☀", style={
                                'fontSize': '3rem',
                                'marginBottom': '1rem',
                                'opacity': '0.3'
                            }),
                            html.H3("No prediction yet", style={
                                'fontSize': '1.25rem',
                                'fontWeight': '600',
                                'color': '#6b7280',
                                'marginBottom': '0.5rem'
                            }),
                            html.P("Select parameters and click \"Calculate Potential\" to see results", style={
                                'fontSize': '0.875rem',
                                'color': '#9ca3af',
                                'lineHeight': '1.5'
                            })
                        ], style={
                            'textAlign': 'center',
                            'padding': '3rem 1rem'
                        })
                    ], style={
                        'backgroundColor': 'white',
                        'padding': '2rem',
                        'borderRadius': '1rem',
                        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                        'height': '100%'
                    })
                ])
            ], style={'flex': '1'})
        ], style={
            'display': 'flex',
            'gap': '2rem'
        })
    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '0 2rem 4rem 2rem',
        'backgroundColor': '#fafaf9'
    })
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'backgroundColor': '#fafaf9',
    'minHeight': '100vh'
})

# ===== Callbacks =====

@app.callback(
    Output('tilt-display', 'children'),
    Input('tilt-slider', 'value')
)
def update_tilt_display(value):
    """Update the tilt angle display"""
    return f"{value}°"


@app.callback(
    Output('results-container', 'children'),
    Input('predict-button', 'n_clicks'),
    State('city-dropdown', 'value'),
    State('building-type-dropdown', 'value'),
    State('tilt-slider', 'value'),
    prevent_initial_call=True
)
def make_prediction(n_clicks, city, building_type, tilt):
    """Make prediction request to FastAPI backend"""
    if n_clicks == 0:
        raise PreventUpdate
    
    # Show loading state
    loading_state = html.Div([
        html.Div([
            html.Div("⌛", style={
                'fontSize': '3rem',
                'marginBottom': '1rem',
                'animation': 'spin 2s linear infinite'
            }),
            html.H3("Loading configuration...", style={
                'fontSize': '1.25rem',
                'fontWeight': '600',
                'color': '#6b7280'
            })
        ], style={
            'textAlign': 'center',
            'padding': '3rem 1rem'
        })
    ], style={
        'backgroundColor': 'white',
        'padding': '2rem',
        'borderRadius': '1rem',
        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
    })
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json={
                "city": city,
                "building_type": building_type,
                "tilt": tilt
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        predicted_value = data["predicted_kWh_per_m2"]
        
        # Return success result with exact card design from screenshots
        return html.Div([
            html.Div([
                html.H2("Prediction Results", style={
                    'fontSize': '1.5rem',
                    'fontWeight': '600',
                    'color': '#1f2937',
                    'marginBottom': '2rem'
                }),
                
                # Main result display
                html.Div([
                    html.Div(f"{predicted_value:.2f}", style={
                        'fontSize': '4rem',
                        'fontWeight': '700',
                        'color': '#92400e',
                        'lineHeight': '1'
                    }),
                    html.Div("kWh/m²/year", style={
                        'fontSize': '1.125rem',
                        'color': '#78716c',
                        'fontWeight': '500',
                        'marginTop': '0.5rem'
                    })
                ], style={
                    'textAlign': 'center',
                    'padding': '2rem',
                    'backgroundColor': '#fef3c7',
                    'borderRadius': '0.75rem',
                    'marginBottom': '1.5rem'
                }),
                
                # Parameters used
                html.Div([
                    html.Div([
                        html.Div("City", style={
                            'fontSize': '0.75rem',
                            'color': '#78716c',
                            'fontWeight': '600',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.05em',
                            'marginBottom': '0.25rem'
                        }),
                        html.Div(city, style={
                            'fontSize': '1rem',
                            'color': '#1f2937',
                            'fontWeight': '600'
                        })
                    ]),
                    html.Div([
                        html.Div("Building Type", style={
                            'fontSize': '0.75rem',
                            'color': '#78716c',
                            'fontWeight': '600',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.05em',
                            'marginBottom': '0.25rem'
                        }),
                        html.Div(building_type, style={
                            'fontSize': '1rem',
                            'color': '#1f2937',
                            'fontWeight': '600'
                        })
                    ]),
                    html.Div([
                        html.Div("Tilt Angle", style={
                            'fontSize': '0.75rem',
                            'color': '#78716c',
                            'fontWeight': '600',
                            'textTransform': 'uppercase',
                            'letterSpacing': '0.05em',
                            'marginBottom': '0.25rem'
                        }),
                        html.Div(f"{tilt}°", style={
                            'fontSize': '1rem',
                            'color': '#1f2937',
                            'fontWeight': '600'
                        })
                    ])
                ], style={
                    'display': 'grid',
                    'gridTemplateColumns': 'repeat(3, 1fr)',
                    'gap': '1rem',
                    'padding': '1.5rem',
                    'backgroundColor': '#fafaf9',
                    'borderRadius': '0.75rem'
                })
            ], style={
                'backgroundColor': 'white',
                'padding': '2rem',
                'borderRadius': '1rem',
                'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
            })
        ])
        
    except requests.exceptions.ConnectionError:
        return html.Div([
            html.Div([
                html.Div("⚠️", style={
                    'fontSize': '3rem',
                    'marginBottom': '1rem'
                }),
                html.H3("Connection Error", style={
                    'fontSize': '1.25rem',
                    'fontWeight': '600',
                    'color': '#991b1b',
                    'marginBottom': '0.5rem'
                }),
                html.P([
                    "Could not connect to the API. Please ensure the FastAPI backend is running at ",
                    html.Code(API_BASE_URL, style={
                        'backgroundColor': '#fee2e2',
                        'padding': '0.125rem 0.375rem',
                        'borderRadius': '0.25rem',
                        'fontSize': '0.875rem'
                    })
                ], style={
                    'fontSize': '0.875rem',
                    'color': '#6b7280'
                })
            ], style={
                'textAlign': 'center',
                'padding': '2rem',
                'backgroundColor': '#fef2f2',
                'border': '1px solid #fecaca',
                'borderRadius': '0.75rem'
            })
        ], style={
            'backgroundColor': 'white',
            'padding': '2rem',
            'borderRadius': '1rem',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        })
    
    except Exception as e:
        return html.Div([
            html.Div([
                html.Div("⚠️", style={
                    'fontSize': '3rem',
                    'marginBottom': '1rem'
                }),
                html.H3("Error", style={
                    'fontSize': '1.25rem',
                    'fontWeight': '600',
                    'color': '#991b1b',
                    'marginBottom': '0.5rem'
                }),
                html.P(f"An error occurred: {str(e)}", style={
                    'fontSize': '0.875rem',
                    'color': '#6b7280'
                })
            ], style={
                'textAlign': 'center',
                'padding': '2rem',
                'backgroundColor': '#fef2f2',
                'border': '1px solid #fecaca',
                'borderRadius': '0.75rem'
            })
        ], style={
            'backgroundColor': 'white',
            'padding': '2rem',
            'borderRadius': '1rem',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        })


# ===== Run Server =====
if __name__ == '__main__':
    print("\n" + "="*50)
    print("Energy404 Solar Potential Estimator")
    print("="*50)
    print(f"Frontend running at: http://0.0.0.0:8050")
    print(f"API backend expected at: {API_BASE_URL}")
    print("="*50 + "\n")
    app.run_server(debug=True, host='0.0.0.0', port=8050)
