import os
import ipywidgets as widgets
from ipyleaflet import WidgetControl, Marker, basemaps, Map
from ipyfilechooser import FileChooser
from IPython.display import display
import pandas as pd


def main_toolbar(m):

    padding = "0px 0px 0px 5px"  # upper, right, bottom, left

    toolbar_button = widgets.ToggleButton(
        value=False,
        tooltip="Toolbar",
        icon="wrench",
        layout=widgets.Layout(width="28px", height="28px", padding=padding),
    )

    close_button = widgets.ToggleButton(
        value=False,
        tooltip="Close the tool",
        icon="times",
        button_style="primary",
        layout=widgets.Layout(height="28px", width="28px", padding=padding),
    )    

    toolbar = widgets.HBox([toolbar_button])

    def close_click(change):
        if change["new"]:
            toolbar_button.close()
            close_button.close()
            toolbar.close()
            
    close_button.observe(close_click, "value")

    rows = 2
    cols = 2
    grid = widgets.GridspecLayout(rows, cols, grid_gap="0px", layout=widgets.Layout(width="62px"))

    icons = ["folder-open", "map", "gears", "question"]

    for i in range(rows):
        for j in range(cols):
            grid[i, j] = widgets.Button(description="", button_style="primary", icon=icons[i*rows+j], 
                                        layout=widgets.Layout(width="28px", padding="0px"))

    toolbar = widgets.VBox([toolbar_button])

    def toolbar_click(change):
        if change["new"]:
            toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
        else:
            toolbar.children = [toolbar_button]
        
    toolbar_button.observe(toolbar_click, "value")

    toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")

    m.add_control(toolbar_ctrl)

    output = widgets.Output()
    output_ctrl = WidgetControl(widget=output, position="topright")

    buttons = widgets.ToggleButtons(
        value=None,
        options=["Apply", "Reset", "Close"],
        tooltips=["Apply", "Reset", "Close"],
        button_style="primary",
    )
    buttons.style.button_width = "80px"

    data_dir = os.path.abspath('./data')

    fc = FileChooser(data_dir)
    fc.use_dir_icons = True
    fc.filter_pattern = ['*.shp', '*.geojson', '*.csv']

    filechooser_widget = widgets.VBox([fc, buttons])

    def button_click(change):
        if change["new"] == "Apply" and fc.selected is not None:
            if fc.selected.endswith(".shp"):
                m.add_shapefile(fc.selected, layer_name="Shapefile")
            elif fc.selected.endswith(".geojson"):
                m.add_geojson(fc.selected, layer_name="GeoJSON")
            elif fc.selected.endswith(".csv"):
                GasLeaks = pd.read_csv(fc.selected)
                GasLeaks = GasLeaks[['Date', 'Latitude', 'Longitude', 'Pipe Material']]
                
                selection_slider = widgets.SelectionSlider(options=list(GasLeaks['Date']),
                                                value='1/3/1967',
                                                description='Slider',
                                                disabled=False,
                                                continuous_update=False,
                                                orientation='horizontal',
                                                readout=True)
                def plot_GasLeaks(date):
                    g = GasLeaks.loc[GasLeaks['Date'] == date]
                    for (index, row) in g.iterrows():
                        marker = Marker(location=[row.loc['Latitude'], row.loc['Longitude']])
                        m.add_layer(marker)
                    print(GasLeaks.loc[GasLeaks['Date'] == date])
                widgets.interact(plot_GasLeaks, date=selection_slider)

                display(m)
        elif change["new"] == "Reset":
            fc.reset()
        elif change["new"] == "Close":
            fc.reset()
            m.remove_control(output_ctrl)
    buttons.observe(button_click, "value")     

    def tool_click(b):    
        with output:
            output.clear_output()
            if b.icon == "folder-open":
                display(filechooser_widget)
                m.add_control(output_ctrl)
            elif b.icon == "gears":
                import whiteboxgui.whiteboxgui as wbt

                if hasattr(m, "whitebox") and m.whitebox is not None:
                    if m.whitebox in m.controls:
                        m.remove_control(m.whitebox)

                tools_dict = wbt.get_wbt_dict()
                wbt_toolbox = wbt.build_toolbox(
                    tools_dict, max_width="800px", max_height="500px"
                )

                wbt_control = WidgetControl(
                    widget=wbt_toolbox, position="bottomright"
                )                

                m.whitebox = wbt_control
                m.add_control(wbt_control)

    for i in range(rows):
        for j in range(cols):
            tool = grid[i, j]
            tool.on_click(tool_click)

def side_toolbar(m):
    toolbar_button = widgets.ToggleButton(
        value=False,
        tooltip="Toolbar",
        icon="times",
        button_style="primary",
        layout=widgets.Layout(height="28px", width="28px"),
)    
    dropdown = widgets.Dropdown(options=['Positron', 'DarkMatter', 'WorldStreetMap', 'DeLorme', 
                                                'WorldTopoMap', 'WorldImagery', 'NatGeoWorldMap', 'HikeBike', 
                                                'HyddaFull', 'Night', 'ModisTerra', 'Mapnik', 'HOT', 'OpenTopoMap', 
                                                'Toner', 'Watercolor'],
                                       value='Positron', 
                                       description='map types:')

    toolbar = widgets.HBox([toolbar_button])
    toolbar

    def toolbar_click(change):
        if change["new"]:
            toolbar.children = [toolbar_button,dropdown]
        else:
            toolbar.children = [toolbar_button]
    toolbar_button.observe(toolbar_click, "value")

    toolbar_ctrl = WidgetControl(widget=toolbar, position="bottomleft")
    m.add_control(toolbar_ctrl)

    def toggle_maps(map):
        if map == 'Positron': basemaps.CartoDB.Positron
        if map == 'DarkMatter': basemaps.CartoDB.DarkMatter
        if map == 'WorldStreetMap': basemaps.Esri.WorldStreetMap

    widgets.interact(toggle_maps,map=dropdown)