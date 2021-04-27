
from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa_viz.VegaVisualization import VegaServer
from mesa_viz.VegaSpec import GridChart

from model import SimpleModel, Furtarchy

COLORS = {"Yes": "#00AA00", "No": "#883300", "Unknown": "#000000"}
COLORS1 = {"yes_token_price": "#00AA00", "no_token_price": "#880000"}
COLORS2 = {"yes_token": "#00AA00", "no_token": "#880000"}

Height = 10
Witdth = 10


def voter_portrayal(voter):
    if voter is None:
        return

    portrayal = {"Shape": "circle", "w": 1, "h": 1,
                 "Filled": "false", "Layer": 0, 'r': 1}
    (x, y) = voter.pos
    tokens = voter.token
    portrayal["x"] = x
    portrayal["y"] = y
    # token = round(voter.token,0)
    # yes_token = round(voter.yes_token, 0)
    # no_token = round(voter.no_token, 0)
    wealth = round(voter.wealth, 2)
    # portrayal['text'] ="{},{},{}".format(int(token), int(yes_token), int(no_token))
    portrayal['text'] = wealth
    if tokens > 10:
        condition = 'Yes'
    elif tokens < 10:
        condition = 'No'
    else:
        condition = 'Unknown'
    portrayal["Color"] = COLORS[condition]
    portrayal['text_color'] = "#ffffff"
    return portrayal


canvas_element = CanvasGrid(voter_portrayal, Height, Witdth, 500, 500)
tree_chart = ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS1.items()], data_collector_name='datacollector'
)
pie_chart = PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS2.items()],
    data_collector_name='countcollector'
)

model_params = {
    "b_number": UserSettableParameter('number', 'b_number', 30),
    'agent_number': UserSettableParameter('number', 'agent_number', 20)
    # "height": Height,
    # "width": Witdth,
    # "proposal": UserSettableParameter('choice', 'proposal to choice', value="Increase the supply of HNY token.", choices=['Create a big house', 'Got me a lot of money', 'Found a great gold'])
}
# the origin chart
# server = ModularServer(
#     SimpleModel, [canvas_element, tree_chart, pie_chart], "Vote Simulation"
# )

# # the changed chart
# grid = GridChart()
# vega_server = VegaServer(
#     SimpleModel, [grid], "Vote Simulation", {}, n_simulations=3
# )

futarchy_server = ModularServer(
    Furtarchy, [canvas_element, tree_chart,
                pie_chart], 'Futarchy Simulation', model_params
)
