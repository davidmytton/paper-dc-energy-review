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

config = {
    'toImageButtonOptions': {
        'format': 'svg',  # one of png, svg, jpeg, webp
    }
}


#
# Basic stats
#
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


#
# Figure 1
#
# Global data center energy estimates for 2020, 2025 and 2030.
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
                 template='plotly_white')
    fig.update_layout(font_family='sans-serif', font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_layout(yaxis_range=[0, 2000])

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
# Global data center energy estimates for 2010-2030.
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
                 template='plotly_white')
    fig.update_layout(font_family='sans-serif', font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='black')
    fig.update_layout(yaxis_range=[0, 2000])

    # Show estimate counts
    for s in figresult['Estimate year'].unique():
        fig.add_annotation(x=s,
                           y=figresult[figresult['Estimate year']
                                       == s]['Value (TWh)'].max(),
                           text=str(
                               len(figresult[figresult['Estimate year'] == s]['Value (TWh)'])),
                           yshift=10,
                           showarrow=False)

    return fig


#
# Generate a sankey diagram from the items passed through
#
# items = pandas.DataFrame
#

def sankey(items):
    # Define colors
    COLOR_FOUND_DARK = 'black'
    COLOR_FOUND_LIGHT = 'lightgray'
    COLOR_CITATIONS_GTE1000_DARK = '#ffc6cf'  # Citations >= 1000 = Dark red
    COLOR_CITATIONS_GTE1000_LIGHT = '#ffc6cf'  # Citations >= 1000 = Light red
    COLOR_CITATIONS_GTE500_DARK = '#ffea9c'  # Citations >= 500 = Dark yellow
    COLOR_CITATIONS_GTE500_LIGHT = '#ffea9c'  # Citations >= 500 = Light yellow
    COLOR_CITATIONS_GTE100_DARK = '#c6eece'  # Citations >= 100 = Dark green
    COLOR_CITATIONS_GTE100_LIGHT = '#c6eece'  # Citations >= 100 = Light green
    # From https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
    COLOR_NOTFOUND_DARK = '#f1a340'  # Orange
    COLOR_NOTFOUND_LIGHT = '#fcdfba'  # Light orange

    # Build the lists
    labels = []  # Labels (unique)
    colors_node = []  # Colors mapped to labels
    colors_link = []  # Colors mapped to links
    sources = []  # Index for each source for a link, mapped to label
    targets = []  # Target for each link, mapped to label
    values = []  # Value for each node, which determines its size, mapped to label

    # Loop through every row and build the lists to create the Sankey
    for index, row in items.iterrows():
        # Determine if we need to create a new label
        if row['Authors'] not in labels:
            if row['Citation Count'] >= 1000:
                color_node = COLOR_CITATIONS_GTE1000_DARK
                color_link = COLOR_CITATIONS_GTE1000_LIGHT
            elif row['Citation Count'] >= 500:
                color_node = COLOR_CITATIONS_GTE500_DARK
                color_link = COLOR_CITATIONS_GTE500_LIGHT
            elif row['Citation Count'] >= 100:
                color_node = COLOR_CITATIONS_GTE100_DARK
                color_link = COLOR_CITATIONS_GTE100_LIGHT
            else:
                color_node = COLOR_FOUND_DARK
                color_link = COLOR_FOUND_LIGHT

            labels.append(row['Authors'])
            colors_node.append(color_node)

        # Set the color based on the source reliability classification, but hard
        # code any sources which are also in the review
        # Colors from https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
        if row['Source (Grouped for Visualisations)'] == 'IDC':
            color_node = COLOR_NOTFOUND_DARK
            color_link = COLOR_NOTFOUND_LIGHT
        elif row['Source Reliability'] == 'EL' \
                or row['Source Reliability'] == 'PD':
            color_node = COLOR_FOUND_DARK
            color_link = COLOR_FOUND_LIGHT
        else:
            color_node = COLOR_NOTFOUND_DARK
            color_link = COLOR_NOTFOUND_LIGHT

        if row['Source (Grouped for Visualisations)'] not in labels:
            labels.append(row['Source (Grouped for Visualisations)'])
            colors_node.append(color_node)

        # Create the node and link
        sources.append(labels.index(
            row['Source (Grouped for Visualisations)']))
        targets.append(labels.index(row['Authors']))
        colors_link.append(color_link)

        # Link size is always 1 because there's no useful alternative to size them on
        # The size of the node is determined automatically based on the number of
        # links, which is the same as the number of references
        values.append(1)

    return labels, colors_node, colors_link, sources, targets, values


#
# De-dup the sources
#
sources_unique = sources.drop_duplicates(
    subset=['Authors', 'Source (Grouped for Visualisations)'])

#
# Figure 4
#
# Sankey diagram showing the flow of citations
#
sources_fig4 = sources_unique.query(
    'Authors == \"Corcoran & Andrae, 2013\" or Authors == \"Andrae & Edler, 2015\" or Authors == \"The Shift Project, 2019\"')
labels, colors_node, colors_link, sources, targets, values = sankey(
    sources_fig4)

# Create the figure
fig4 = go.Figure(data=[go.Sankey(
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

fig4.update_layout(font_family='sans-serif', height=1000)

#
# Figure 5
#
# Sankey diagram showing the flow of citations
#
sources_fig5 = sources_unique.query(
    'Authors == \"Van Heddeghem et al., 2014\" or Authors == \"Shehabi et al., 2016\" or Authors == \"Malmodin & Lunden, 2018a\"')
labels, colors_node, colors_link, sources, targets, values = sankey(
    sources_fig5)

# Create the figure
fig5 = go.Figure(data=[go.Sankey(
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

fig5.update_layout(font_family='sans-serif', height=1000)

#
# Figure X
#
# Sankey diagram showing data center energy estimate publications analyzed in
# this review that have >=100 citations
#
sources_figx = sources_unique.query('`Citation Count` >= 100')
labels, colors_node, colors_link, sources, targets, values = sankey(
    sources_figx)

# Create the figure
figx = go.Figure(data=[go.Sankey(
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

figx.update_layout(font_family='sans-serif', height=2000)


#
# Run server
#
app.layout = html.Div([
    dcc.Markdown(f'''
# {title}

# Authors

* David Mytton, Centre for Environmental Policy, Imperial College London,
  London, SW7 1NE, UK.
* Masaō Ashtine, Oxford e-Research Centre, University of Oxford, Oxford, UK.

**Correspondence:** <david@davidmytton.co.uk>.

# Summary

> Data centers are a critical component of Information Technology (IT), providing a reliable environment for computer equipment such as servers and storage systems. Reliance on data centers for everyday activities has seen increased scrutiny of their environmental impact. In this review, we analyze original data center energy estimates published between 2007 and 2021. Breaking down 46 individual publications into 676 data provenance traces, we map citations used by each publication to assess reliability and highlight methodological challenges. We show that 38% of sources were from peer-reviewed publications and 31% were from non-peer reviewed reports with many lacking clear methodologies and data provenance. We also highlight issues with source availability - there is a general reliance on private data from IDC and Gartner, 11% of sources had broken URLs, and 10% were cited with insufficient detail to locate. These findings pose challenges for the reliability and reproducibility of estimates important for planning the energy systems of the future.
    '''),
    html.H2('Stats'),
    dcc.Markdown(f'''
- Total estimates: {total_estimates}.
- Estimates by country:
    - Global: {total_estimates_global}.
    - US: {total_estimates_us}.
    - Europe: {total_estimates_europe}.
    '''),
    html.H2('Figure 1'),
    dcc.Markdown('''
Global data center energy estimates for 2020, 2025 and 2030 as ranges (in TWh) plotted by the year the estimate applies to (estimate year). This figure demonstrates the wide range of estimates across publications and should not be used as an analysis or projection of data center energy values themselves - caution should be used when comparing estimates due to a wide range of methods and system boundaries. n = number of estimates, which are provided in Table S2.
    '''),
    dcc.Checklist(
        id='fig-1-exclude',
        options=[{'value': 'true', 'label': 'Exclude estimates >2000 TWh'}],
        value=['true'],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='fig-1', config=config),
    html.H2('Figure 2'),
    dcc.Markdown('''
Global data center energy estimates for 2010-2030 as ranges (in TWh) plotted by the year to which the estimate applies (estimate year). This figure demonstrates the wide range of estimates across publications and should not be used as an analysis or projection of data center energy values themselves - caution should be used when comparing estimates due to a wide range of methods and system boundaries. Number above each box indicates the estimate count, which are provided in Table S2.
    '''),
    dcc.Checklist(
        id='fig-2-exclude',
        options=[{'value': 'true', 'label': 'Exclude estimates >2000 TWh'}],
        value=['true'],
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='fig-2', config=config),
    html.H2('Figure 4'),
    dcc.Markdown('''
Sankey diagram showing the flow of citations between Corcoran & Andrae, 2013, Andrae & Edler, 2015, and The Shift Project, 2019. Sources in orange indicate that source could not be found. See Table S1 for the full list of publications, sources, and reasons for sources that could not be found.
    '''),
    dcc.Graph(figure=fig4, config=config),
    html.H2('Figure 5'),
    dcc.Markdown('''
Sankey diagram showing the flow of citations between three highly cited publications - Malmodin & Lundén, 2018a cites Shehabi et al., 2016 which cites Van Heddeghem et al., 2014. Sources in orange indicate that source could not be found. Colored nodes on the right (for end publications) indicate citation count from Google Scholar (green >= 100, yellow >= 500, red >= 1000 citations). See Table S1 for the full list of publications, sources, and reasons for sources that could not be found.
    '''),
    dcc.Graph(figure=fig5, config=config),
    html.H2('Figure X'),  # Not currently used
    dcc.Markdown('''**Not in manuscript.**
Sankey diagram showing data center energy estimate publications analyzed in this review that have more >100 citations, and the key sources they cite. Sources in orange indicate that source could not be found. Colored nodes indicate citation count from Google Scholar (green >= 100, yellow >= 500, red >= 1000 citations). See Table S1 for the full list of publications, sources, and reasons for sources that could not be found.
    '''),
    dcc.Graph(figure=figx),
])

app.run_server(debug=True)
