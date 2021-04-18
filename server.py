
from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa_viz.VegaVisualization import VegaServer
from mesa_viz.VegaSpec  import GridChart

from model import SimpleModel

COLORS = {"Yes": "#00AA00", "No": "#880000", "Unknown": "#000000"}
Height = 10
Witdth = 10


def voter_portrayal(voter):
    if voter is None:
        return

    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = voter.pos
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[voter.condition]
    return portrayal


canvas_element = CanvasGrid(voter_portrayal, Height, Witdth, 500, 500)
tree_chart = ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
)
pie_chart = PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
)

model_params = {
    # "height": Height,
    # "width": Witdth,
    # "proposal": UserSettableParameter('choice', 'proposal to choice', value="Increase the supply of HNY token.", choices=['Create a big house', 'Got me a lot of money', 'Found a great gold'])
}
# the origin chart
server = ModularServer(
    SimpleModel, [canvas_element, tree_chart, pie_chart], "Vote Simulation", model_params
)

# the changed chart
grid = GridChart()
vega_server = VegaServer(
    SimpleModel, [grid], "Vote Simulation", model_params, n_simulations=3
)