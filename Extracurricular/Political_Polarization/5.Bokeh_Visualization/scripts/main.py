from src.polarization_visualization1 import *
from src.polarization_visualization2 import *
from bokeh.plotting import curdoc
graph1 = createPolarizationgGraph()
graph2 = createDWGraph()

curdoc().add_root(column(graph1,graph2))

# curdoc().add_root(createPolarizationgGraph())
# curdoc().add_root(createDWGraph())