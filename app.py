# A review of global data center energy estimates from 2007 - 2021
#
# Authors:
# - David Mytton, Centre for Environmental Policy, Imperial College London,
#   London, SW7 1NE, UK.
# - Masaō Ashtine, Oxford e-Research Centre, University of Oxford, Oxford, UK.
#
# Correspondence:** <david@davidmytton.co.uk>.
#
# SPDX-License-Identifier: CC-BY-4.0

import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Load data
estimates = pd.read_csv('data/estimates.csv', keep_default_na=False)
sources = pd.read_csv('data/sources.csv', keep_default_na=False)

# Set up app
title = 'A review of data center energy estimates published 2007 - 2021'
app = dash.Dash(title=title)

#
# Basic stats
#
# De-dup on authors to get the count
publications_analyzed = sources.drop_duplicates(subset=['Authors'])
total_publications_analyzed = len(publications_analyzed.index)

# Numbers/counts of things included in the review.
total_estimates = len(estimates.index)

result = estimates.query('Geography == \"Global\"')
total_estimates_global = len(result.index)

result = estimates.query('Geography == \"USA\"')
total_estimates_us = len(result.index)

result = estimates.query(
    'Geography == \"EU25\" or \
    Geography == \"EU27\" or \
    Geography == \"EU28\" or \
    Geography == \"Europe\" or \
    Geography == \"Western Europe\"')
total_estimates_europe = len(result.index)

# There is a row for each entry in Table S1, which doesn't map to anything
# relevant for visualizing. As such, we de-dup so a source and target only
# appears once. This provides the true citation count for each source.
sources_unique = sources.drop_duplicates(
    subset=['Authors', 'Source (Grouped for Visualisations)'])

total_sources_unique = len(sources_unique.index)


#
# Figure 1
#
# Ideally this would use a break in the y axis to show all the values, but
# that does not seem possible with Plotly.
#
# https://stackoverflow.com/a/65766964/2183 is an option for bar charts but
# probably wouldn't work for a box plot due to the integrated error bars.
#
# Fall back solution is a check box option to exclude estimates >2000 TWh
# (default = true).
@app.callback(
    Output("fig-1", "figure"),
    [Input("fig-1-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query(
            'Geography == \"Global\" and (`Estimate year` == 2020 or `Estimate year` == 2025 or `Estimate year` == 2030)')
    else:
        figresult = estimates.query(
            'Geography == \"Global\" and (`Estimate year` == 2020 or `Estimate year` == 2025 or `Estimate year` == 2030) and `Value (TWh)` < 2000')

    fig = px.box(figresult,
                 x='Estimate year',
                 y='Value (TWh)',
                 template='simple_white')
    fig.update_layout(font_family='sans-serif')

    # Show values
    for s in figresult['Estimate year'].unique():
        # Max
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].max(),
                           text="max = " + str(
                               figresult[figresult['Estimate year'] == s]['Value (TWh)'].max()),
                           yshift=10,
                           showarrow=False)

        # Count
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].max(),
                           text="n = " + str(
                               len(figresult[figresult['Estimate year'] == s]['Value (TWh)'])),
                           yshift=25,
                           showarrow=False)

        # Median
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].median(),
                           text="median = " +
                           str(figresult[figresult['Estimate year']
                               == s]['Value (TWh)'].median()),
                           yshift=10,
                           showarrow=False)

        # Min
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].min(),
                           text="min = " + str(
                               figresult[figresult['Estimate year'] == s]['Value (TWh)'].min()),
                           yshift=-10,
                           showarrow=False)

    return fig


#
# Figure 2
#
# Check box option to exclude estimates >2000 TWh (default = true).
@app.callback(
    Output("fig-2", "figure"),
    [Input("fig-2-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query(
            'Geography == \"Global\" and `Estimate year` >= 2010')
    else:
        figresult = estimates.query(
            'Geography == \"Global\" and `Estimate year` >= 2010 and `Value (TWh)` < 2000')

    fig = px.box(figresult,
                 x='Estimate year',
                 y='Value (TWh)',
                 template='simple_white')
    fig.update_layout(font_family='sans-serif')

    # Show estimate counts
    for s in figresult['Estimate year'].unique():
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].max(),
                           text="n = " + str(
                               len(figresult[figresult['Estimate year'] == s]['Value (TWh)'])),
                           yshift=10,
                           showarrow=False)

    return fig


#
# Figure 3
#
# Define colors
# From https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
COLOR_NOTFOUND_DARK = '#f1a340'  # Orange
COLOR_NOTFOUND_LIGHT = '#fcdfba'  # Light orange
COLOR_FOUND_DARK = 'black'
COLOR_FOUND_LIGHT = 'lightgray'

# Build the lists
labels = []  # Labels (unique)
colors_node = []  # Colors mapped to labels
colors_link = []  # Colors mapped to links
sources = []  # Index for each source for a link, mapped to label
targets = []  # Target for each link, mapped to label
values = []  # Value for each node, which determines its size, mapped to label

# Loop through every row and build the lists to create the Sankey
for index, row in sources_unique.iterrows():
    # Set the color based on the source reliability classification, but hard
    # code any sources which are also in the review
    # Colors from https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
    if row['Source Reliability'] == 'EL' \
            or row['Source Reliability'] == 'PD':
        color_node = COLOR_FOUND_DARK
        color_link = COLOR_FOUND_LIGHT
    else:
        color_node = COLOR_NOTFOUND_DARK
        color_link = COLOR_NOTFOUND_LIGHT

    # Determine if we need to create a new label
    if row['Authors'] not in labels:
        color_node = COLOR_FOUND_DARK
        color_link = COLOR_FOUND_LIGHT

        labels.append(row['Authors'])
        colors_node.append(color_node)

    if row['Source (Grouped for Visualisations)'] not in labels:
        labels.append(row['Source (Grouped for Visualisations)'])
        colors_node.append(color_node)

    # Create the node and link
    sources.append(labels.index(row['Source (Grouped for Visualisations)']))
    targets.append(labels.index(row['Authors']))
    colors_link.append(color_link)

    # Link size is always 1 because there's no useful alternative to size them on
    # The size of the node is determined automatically based on the number of
    # links, which is the same as the number of references
    values.append(1)

# Create the figure
fig3 = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        label=labels,
        color=colors_node,
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=colors_link,
    ))])

fig3.update_layout(font_family='sans-serif', height=5000)
# fig.write_image('figure.pdf', width=2000)

#
# Run server
#
app.layout = html.Div([
    dcc.Markdown(f'''
# {title}

## Authors

* David Mytton, Centre for Environmental Policy, Imperial College London,
  London, SW7 1NE, UK.
* Masaō Ashtine, Oxford e-Research Centre, University of Oxford, Oxford, UK.

**Correspondence:** <david@davidmytton.co.uk>.

## Summary

> TODO
    '''),
    html.H2('Stats'),
    dcc.Markdown(f'''
- Publications analyzed: {total_publications_analyzed}.
- Total estimates: {total_estimates}.
- Key sources: {total_sources_unique}.
- Estimates by country:
    - Global: {total_estimates_global}.
    - US: {total_estimates_us}.
    - Europe: {total_estimates_europe}.
    '''),
    html.H2('Figure 1'),
    dcc.Markdown('''
Global data center energy estimate ranges (in TWh) plotted by the year the estimate applies to (Estimate year). All estimate values are provided in Table S2.
    '''),
    dcc.Checklist(
        id='fig-1-exclude',
        options=[{'value': 'true', 'label': 'Exclude estimates >2000 TWh'}],
        value=['true'],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='fig-1'),
    html.H2('Figure 2'),
    dcc.Markdown('''
Global data center energy estimates for 2010-2030 as ranges (in TWh) plotted by the year the estimate applies to (Estimate year). All estimate values are provided in Table S2.
    '''),
    dcc.Checklist(
        id='fig-2-exclude',
        options=[{'value': 'true', 'label': 'Exclude estimates >2000 TWh'}],
        value=['true'],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='fig-2'),
    html.H2('Figure 3'),
    dcc.Markdown('''
Sankey diagram showing data center energy estimate publications analyzed in this review with their key sources. Sources in orange indicate that source could not be found. Node size based on the number of independent citations from  publications analyzed. See Table S1 for the full list of publications, sources and reasons for sources that could not be found.
    '''),
    dcc.Graph(figure=fig3),
])

app.run_server(debug=True)
