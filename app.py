# A comprehensive data provenance review of data center energy estimates
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
estimates = pd.read_csv("data/estimates.csv", keep_default_na=False)
sources = pd.read_csv("data/sources.csv", keep_default_na=False)

# Set up app
title = "A comprehensive data provenance review of data center energy estimates"
app = dash.Dash(title=title)

config = {
    "toImageButtonOptions": {
        "format": "svg",  # one of png, svg, jpeg, webp
    }
}


#
# Basic stats
#
# Numbers/counts of things included in the review.
total_estimates = len(estimates.index)

result = estimates.query('Geography == "Global"')
total_estimates_global = len(result.index)

result = estimates.query('Geography == "USA"')
total_estimates_us = len(result.index)

result = estimates.query(
    'Geography == "EU25" or \
    Geography == "EU27" or \
    Geography == "EU28" or \
    Geography == "Europe" or \
    Geography == "Western Europe"'
)
total_estimates_europe = len(result.index)


#
# Figure 2
#
# Global data center energy estimates for 2020 and 2030.
#
# Ideally this would use a break in the y axis to show all the values, but
# that does not seem possible with Plotly.
#
# https://stackoverflow.com/a/65766964/2183 is an option for bar charts but
# probably wouldn't work for a box plot due to the integrated error bars.
#
# Fall back solution is a check box option to exclude estimates >2000 TWh
# (default = true).
@app.callback(Output("fig-2", "figure"), [Input("fig-2-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query(
            '(Method == "Bottom-up" or Method == "Extrapolation") and Geography == "Global" and (`Estimate year` == 2010 or `Estimate year` == 2020 or or `Estimate year` == 2030)'
        )
    else:
        figresult = estimates.query(
            '(Method == "Bottom-up" or Method == "Extrapolation") and Geography == "Global" and (`Estimate year` == 2010 or `Estimate year` == 2020 or `Estimate year` == 2030) and `Value (TWh)` < 2000'
        )

    fig = px.box(figresult, x="Estimate year", y="Value (TWh)", template="plotly_white")
    fig.update_layout(font_family="sans-serif", font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_layout(yaxis_range=[0, 2000])

    # Show values
    for s in figresult["Estimate year"].unique():
        # Max
        fig.add_annotation(
            x=s,
            y=figresult[figresult["Estimate year"] == s]["Value (TWh)"].max(),
            text="max = "
            + str(figresult[figresult["Estimate year"] == s]["Value (TWh)"].max()),
            yshift=10,
            showarrow=False,
        )

        # Count
        fig.add_annotation(
            x=s,
            y=figresult[figresult["Estimate year"] == s]["Value (TWh)"].max(),
            text="n = "
            + str(len(figresult[figresult["Estimate year"] == s]["Value (TWh)"])),
            yshift=25,
            showarrow=False,
        )

        # Position the median annotation
        if s != 2010:
            yshift = 10  # On the median line
        else:
            yshift = 60  # Above the count, because there's no space

        # Median
        fig.add_annotation(
            x=s,
            y=figresult[figresult["Estimate year"] == s]["Value (TWh)"].median(),
            text="median = "
            + str(figresult[figresult["Estimate year"] == s]["Value (TWh)"].median()),
            yshift=yshift,
            showarrow=False,
        )

        # Min
        fig.add_annotation(
            x=s,
            y=figresult[figresult["Estimate year"] == s]["Value (TWh)"].min(),
            text="min = "
            + str(figresult[figresult["Estimate year"] == s]["Value (TWh)"].min()),
            yshift=-10,
            showarrow=False,
        )

    return fig


#
# Figure 4
#
# Global data center energy estimates for 2020 and 2030, grouped by estimate
# method.
#
# Ideally this would use a break in the y axis to show all the values, but that
# does not seem possible with Plotly.
#
# https://stackoverflow.com/a/65766964/2183 is an option for bar charts but
# probably wouldn't work for a box plot due to the integrated error bars.
#
# Fall back solution is a check box option to exclude estimates >2000 TWh
# (default = true).
@app.callback(Output("fig-4", "figure"), [Input("fig-4-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query(
            '(Method == "Bottom-up" or Method == "Extrapolation") and Geography == "Global" and (`Estimate year` == 2010 or `Estimate year` == 2020 or `Estimate year` == 2030)'
        )
    else:
        figresult = estimates.query(
            '(Method == "Bottom-up" or Method == "Extrapolation") and Geography == "Global" and (`Estimate year` == 2010 or `Estimate year` == 2020 or `Estimate year` == 2030) and `Value (TWh)` < 2000'
        )

    fig = px.box(
        figresult,
        x="Estimate year",
        y="Value (TWh)",
        template="plotly_white",
        color="Method",
    )
    fig.update_layout(font_family="sans-serif", font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_layout(yaxis_range=[0, 2000])

    # Show values
    for s in figresult["Estimate year"].unique():
        for m in figresult["Method"].unique():

            # Position annotations
            if m == "Extrapolation":
                xshift = -75
            elif m == "Bottom-up":
                xshift = 75

            # Max
            fig.add_annotation(
                x=s,
                y=figresult[figresult["Estimate year"] == s][figresult["Method"] == m][
                    "Value (TWh)"
                ].max(),
                text="max = "
                + str(
                    figresult[figresult["Estimate year"] == s][
                        figresult["Method"] == m
                    ]["Value (TWh)"].max()
                ),
                xshift=xshift,
                yshift=15,
                showarrow=False,
            )

            # Min
            fig.add_annotation(
                x=s,
                y=figresult[figresult["Estimate year"] == s][figresult["Method"] == m][
                    "Value (TWh)"
                ].min(),
                text="min = "
                + str(
                    figresult[figresult["Estimate year"] == s][
                        figresult["Method"] == m
                    ]["Value (TWh)"].min()
                ),
                xshift=xshift,
                yshift=-10,
                showarrow=False,
            )

            if s == 2010:
                yshift = 50
            else:
                if s == 2020 and m == "Extrapolation":
                    yshift = 50
                elif s == 2020 and m == "Bottom-up":
                    yshift = 45
                elif s == 2030 and m == "Extrapolation":
                    yshift = 50
                elif s == 2030 and m == "Bottom-up":
                    yshift = 50

            # Count
            fig.add_annotation(
                x=s,
                y=figresult[figresult["Estimate year"] == s][figresult["Method"] == m][
                    "Value (TWh)"
                ].max(),
                text="n = "
                + str(
                    len(
                        figresult[figresult["Estimate year"] == s][
                            figresult["Method"] == m
                        ]["Value (TWh)"]
                    )
                ),
                xshift=xshift,
                yshift=yshift,
                showarrow=False,
            )

            if s == 2010:
                yshift = 45
            else:
                if s == 2020 and m == "Extrapolation":
                    yshift = 170
                elif s == 2020 and m == "Bottom-up":
                    yshift = 30
                elif s == 2030 and m == "Extrapolation":
                    yshift = 180
                elif s == 2030 and m == "Bottom-up":
                    yshift = 70

            # Median
            fig.add_annotation(
                x=s,
                y=figresult[figresult["Estimate year"] == s][figresult["Method"] == m][
                    "Value (TWh)"
                ].median(),
                text="median = "
                + str(
                    figresult[figresult["Estimate year"] == s][
                        figresult["Method"] == m
                    ]["Value (TWh)"].median()
                ),
                xshift=xshift,
                yshift=yshift,
                showarrow=False,
            )

    return fig


#
# Figure 5a
#
# Global data center energy estimates for 2010-2030.
#
# Check box option to exclude estimates >2000 TWh (default = true).
@app.callback(Output("fig-5a", "figure"), [Input("fig-5a-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query('Geography == "Global" and `Estimate year` >= 2010')
    else:
        figresult = estimates.query(
            'Geography == "Global" and `Estimate year` >= 2010 and `Value (TWh)` < 2000',
            engine="python",
        )
    fig = px.box(figresult, x="Estimate year", y="Value (TWh)", template="plotly_white")
    fig.update_layout(font_family="sans-serif", font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_layout(yaxis_range=[0, 2000])

    # Show estimate counts
    for s in figresult["Estimate year"].unique():
        fig.add_annotation(
            x=s,
            y=figresult[figresult["Estimate year"] == s]["Value (TWh)"].max(),
            text=str(len(figresult[figresult["Estimate year"] == s]["Value (TWh)"])),
            yshift=10,
            showarrow=False,
        )

    return fig


#
# Figure 5b
#
# Global data center energy estimates for 2010-2030.
#
# Check box option to exclude estimates >2000 TWh (default = true).
@app.callback(Output("fig-5b", "figure"), [Input("fig-5b-exclude", "value")])
def generate_fig(exclude):
    if not exclude:
        figresult = estimates.query('Geography == "Global" and `Estimate year` >= 2010')
    else:
        figresult = estimates.query(
            'Geography == "Global" and `Estimate year` >= 2010 and `Value (TWh)` < 2000',
            engine="python",
        )
    fig = px.box(
        figresult,
        x="Estimate year",
        y="Value (TWh)",
        template="plotly_white",
        color="Method",
    )
    fig.update_layout(font_family="sans-serif", font_size=16)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black")
    fig.update_layout(yaxis_range=[0, 2000])

    return fig


#
# Generate a sankey diagram from the items passed through
#
# items = pandas.DataFrame
#
def sankey(items):
    # Define colors
    COLOR_FOUND_DARK = "black"
    COLOR_FOUND_LIGHT = "lightgray"
    COLOR_CITATIONS_GTE1000_DARK = "#ffc6cf"  # Citations >= 1000 = Dark red
    COLOR_CITATIONS_GTE1000_LIGHT = "#ffc6cf"  # Citations >= 1000 = Light red
    COLOR_CITATIONS_GTE500_DARK = "#ffea9c"  # Citations >= 500 = Dark yellow
    COLOR_CITATIONS_GTE500_LIGHT = "#ffea9c"  # Citations >= 500 = Light yellow
    COLOR_CITATIONS_GTE100_DARK = "#c6eece"  # Citations >= 100 = Dark green
    COLOR_CITATIONS_GTE100_LIGHT = "#c6eece"  # Citations >= 100 = Light green
    # From https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
    COLOR_NOTFOUND_DARK = "#f1a340"  # Orange
    COLOR_NOTFOUND_LIGHT = "#fcdfba"  # Light orange

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
        if row["Authors"] not in labels:
            if row["Citation Count"] >= 1000:
                color_node = COLOR_CITATIONS_GTE1000_DARK
                color_link = COLOR_CITATIONS_GTE1000_LIGHT
            elif row["Citation Count"] >= 500:
                color_node = COLOR_CITATIONS_GTE500_DARK
                color_link = COLOR_CITATIONS_GTE500_LIGHT
            elif row["Citation Count"] >= 100:
                color_node = COLOR_CITATIONS_GTE100_DARK
                color_link = COLOR_CITATIONS_GTE100_LIGHT
            else:
                color_node = COLOR_FOUND_DARK
                color_link = COLOR_FOUND_LIGHT

            labels.append(row["Authors"])
            colors_node.append(color_node)

        # Set the color based on the source reliability classification, but hard
        # code any sources which are also in the review
        # Colors from https://colorbrewer2.org/#type=diverging&scheme=PuOr&n=3
        if row["Source (Grouped for Visualisations)"] == "IDC":
            color_node = COLOR_NOTFOUND_DARK
            color_link = COLOR_NOTFOUND_LIGHT
        elif row["Source Reliability"] == "EL" or row["Source Reliability"] == "PD":
            color_node = COLOR_FOUND_DARK
            color_link = COLOR_FOUND_LIGHT
        else:
            color_node = COLOR_NOTFOUND_DARK
            color_link = COLOR_NOTFOUND_LIGHT

        if row["Source (Grouped for Visualisations)"] not in labels:
            labels.append(row["Source (Grouped for Visualisations)"])
            colors_node.append(color_node)

        # Create the node and link
        sources.append(labels.index(row["Source (Grouped for Visualisations)"]))
        targets.append(labels.index(row["Authors"]))
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
    subset=["Authors", "Source (Grouped for Visualisations)"]
)

#
# Figure 6
#
# Sankey diagram showing the flow of citations
#
sources_fig6 = sources_unique.query(
    'Authors == "Corcoran & Andrae, 2013" or Authors == "Andrae & Edler, 2015" or Authors == "The Shift Project, 2019"'
)
labels, colors_node, colors_link, sources, targets, values = sankey(sources_fig6)

# Create the figure
fig6 = go.Figure(
    data=[
        go.Sankey(
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
            ),
        )
    ]
)

fig6.update_layout(font_family="sans-serif", height=1000)

#
# Figure 7
# Sankey diagram showing the flow of citations
#
sources_fig7 = sources_unique.query(
    'Authors == "Van Heddeghem et al., 2014" or Authors == "Shehabi et al., 2016" or Authors == "Malmodin & Lunden, 2018a"'
)
labels, colors_node, colors_link, sources, targets, values = sankey(sources_fig6)

# Create the figure
fig7 = go.Figure(
    data=[
        go.Sankey(
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
            ),
        )
    ]
)

fig7.update_layout(font_family="sans-serif", height=1000)

#
# Figure X
#
# Sankey diagram showing data center energy estimate publications analyzed in
# this review that have >=100 citations
#
sources_figx = sources_unique.query("`Citation Count` >= 100")
labels, colors_node, colors_link, sources, targets, values = sankey(sources_figx)

# Create the figure
figx = go.Figure(
    data=[
        go.Sankey(
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
            ),
        )
    ]
)

figx.update_layout(font_family="sans-serif", height=2000)


#
# Run server
#
app.layout = html.Div(
    [
        dcc.Markdown(
            f"""
# {title}

# Authors

* David Mytton, Centre for Environmental Policy, Imperial College London,
  London, SW7 1NE, UK.
* Masaō Ashtine, Oxford e-Research Centre, University of Oxford, Oxford, UK.

**Correspondence:** <david@davidmytton.co.uk>.

# Summary

> Data centers are a critical component of Information Technology (IT),
> providing an environment for running computer equipment. Reliance on data
> centers for everyday activities has seen increased scrutiny of their energy
> footprint, yet the literature presents a wide range of estimates with
> challenging to validate calculations that makes it difficult to rely on their
> subsequent estimates. In this review, we analyze 46 original data center
> energy estimates published between 2007 and 2021 to assess their reliability
> through examining the 676 sources used. We show that 31% of sources were from
> peer-reviewed publications, 38% were from non-peer reviewed reports, and many
> lacked clear methodologies and data provenance. We also highlight issues with
> source availability - there is a reliance on private data from IDC (43%) and
> Cisco (30%), 11% of sources had broken web links, and 10% were cited with
> insufficient detail to locate. We make recommendations to 3 groups of
> stakeholders for how to improve and better understand the literature -
> end-users who make use of data center energy estimates e.g. journalists; the
> research community e.g. academics; and policy-makers or regulators within the
> energy sector e.g. grid operators.
    """
        ),
        html.H2("Stats"),
        dcc.Markdown(
            f"""
- Total estimates: {total_estimates}.
- Estimates by country:
    - Global: {total_estimates_global}.
    - US: {total_estimates_us}.
    - Europe: {total_estimates_europe}.
    """
        ),
        html.H2("Figure 2"),
        dcc.Markdown(
            """
Global data center energy estimates for 2010, 2020 and 2030 as ranges (in TWh)
plotted by the year the estimate applies to (estimate year). This figure
demonstrates the wide range of estimates across publications and should not be
used as an analysis or projection of data center energy values themselves -
caution should be used when comparing estimates due to a wide range of methods
and system boundaries. n = number of estimates. Excludes 5 estimates > 2,000
TWh with a range of 2,000 TWh to 8,253 TWh to allow for effective scaling of
the visualization. All estimates can be found in Table S2. """
        ),
        dcc.Checklist(
            id="fig-2-exclude",
            options=[{"value": "true", "label": "Exclude estimates >2000 TWh"}],
            value=["true"],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="fig-2", config=config),
        html.H2("Figure 4"),
        dcc.Markdown(
            """
Global data center energy estimates for 2010, 2020 and 2030 as ranges (in TWh)
plotted by the year the estimate applies to (estimate year) and grouped by
methodological classification. This figure demonstrates the wide range of
estimates across publications and highlights how the estimates vary by
methodology. It should not be used as an analysis or projection of data center
energy values themselves - caution should be used when comparing estimates due
to a wide range of methods and system boundaries. n = number of estimates.
Excludes 5 estimates > 2,000 TWh with a range of 2,000 TWh to 8,253 TWh to
allow for effective scaling of the visualization. All estimates can be found in
Table S2."""
        ),
        dcc.Checklist(
            id="fig-4-exclude",
            options=[{"value": "true", "label": "Exclude estimates >2000 TWh"}],
            value=["true"],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="fig-4", config=config),
        html.H2("Figure 5a"),
        dcc.Markdown(
            """
Global data center energy estimates for 2010-2030 as ranges (in TWh) plotted by
the year to which the estimate applies (estimate year). Number above each box
indicates the estimate count. Excludes 5 estimates > 2,000 TWh with a range of
2,000 TWh to 8,253 TWh to allow for effective scaling of the visualization. All
estimates can be found in Table S2."""
        ),
        dcc.Checklist(
            id="fig-5a-exclude",
            options=[{"value": "true", "label": "Exclude estimates >2000 TWh"}],
            value=["true"],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="fig-5a", config=config),
        html.H2("Figure 5b"),
        dcc.Checklist(
            id="fig-5b-exclude",
            options=[{"value": "true", "label": "Exclude estimates >2000 TWh"}],
            value=["true"],
            labelStyle={"display": "inline-block"},
        ),
        dcc.Graph(id="fig-5b", config=config),
        html.H2("Figure 6"),
        dcc.Markdown(
            """
Sankey diagram showing the flow of citations between Corcoran & Andrae, 201344,
Andrae & Edler, 201511, and The Shift Project, 201913. Each of these
publications has at least one missing source (indicated in orange), with the
sources used by The Shift Project, 201913 such as Gartner, IDC, and Statista
almost entirely unavailable or insufficiently referenced so as to locate the
original source. Although we assume these sources were available when
originally published, they are now unavailable which undermines the
replicability of the estimate today. See Table S1 for the full list of
publications, sources, and reasons for sources that could not be found.
    """
        ),
        dcc.Graph(figure=fig6, config=config),
        html.H2("Figure 7"),
        dcc.Markdown(
            """
Sankey diagram showing the flow of citations between three highly cited
publications - Malmodin & Lundén, 2018a54 cites Shehabi et al., 20169 which
cites Van Heddeghem et al., 201470. Sources in orange indicate that source
could not be found. This diagram highlights how publications can be undermined
by unavailable sources further down the chain, such as the use of non-public
data from IDC in both Malmodin & Lundén, 2018a and Shehabi et al., 2016.
Colored nodes on the right (for end publications) indicate citation count from
Google Scholar (green >= 100, yellow >= 500). See Table S1 for the full list of
publications, sources, and reasons for sources that could not be found.
    """
        ),
        dcc.Graph(figure=fig7, config=config),
        html.H2("Figure X"),  # Not currently used
        dcc.Markdown(
            """**Not in manuscript.**
Sankey diagram showing data center energy estimate publications analyzed in this review that have more >100 citations, and the key sources they cite. Sources in orange indicate that source could not be found. Colored nodes indicate citation count from Google Scholar (green >= 100, yellow >= 500, red >= 1000 citations). See Table S1 for the full list of publications, sources, and reasons for sources that could not be found.
    """
        ),
        dcc.Graph(figure=figx),
    ]
)

app.run_server(debug=True)
