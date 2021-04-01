import pandas as pd
from bokeh.layouts import column, row
from bokeh.plotting import curdoc
from bokeh.models import MultiChoice, Select, Slider
from bokeh.plotting import figure, ColumnDataSource
import os
def createDWGraph():
    # Load data
    # p = os.path.join(os.path.dirname(__file__),'..','data','full_output.tsv')
    # m_collection = pd.read_csv(p,sep='\t')
    m_collection = pd.read_csv('/Users/tylerliu/N_RA/Bokeh_Visualization/data/full_output.tsv',sep='\t')
    m_collection.name = m_collection.name.apply(str.strip)
    colname = ['name','chamber_x','party','icpsr','nominate_dim1']
    m1 = m_collection[colname + ['tsne_dim1','tsne_dim2']]
    m1 = m1.rename(columns={'tsne_dim1':'estimated_polarization','tsne_dim2':'estimated_polarization2','party':'party_int'})
    p = os.path.join(os.path.dirname(__file__),'..','data','nominate_prediction.tsv')
    m_DW = pd.read_csv(p, sep='\t')
    # m_DW = pd.read_csv('/Users/tylerliu/N_RA/Bokeh_Visualization/data/nominate_prediction.tsv', sep='\t')
    m_DW = pd.merge(m_DW,m1[['name','party_int','nominate_dim1','chamber_x']],on='name')
    m_DW.name = m_DW.name.apply(str.strip)
    m_DW.name = m_DW.name.apply(str.title)

    feature_dict = {}
    for i in m_DW.name:
        feature_dict[i] = m_DW[m_DW.name == i].test_set.values[0]

    # -------------------------------------------------------
    def createOneDot_for_p2(who):
        target_df = m_DW[m_DW.name == who]
        colors = [
            "#%02x%02x%02x" % (120 * (int(r) + 1), int(255 * (1 - abs(nom))), -120 * (int(r) - 1)) for r, nom in
            zip(target_df.party_int, target_df.nominate_dim1)
        ]
        s = ColumnDataSource(data=dict(
            x=target_df.pred,
            y=target_df.true,
            name=target_df.name,
            colors=colors,
            alpha=abs(target_df.nominate_dim1),
            true_DW_Nominate=target_df.true,
            pred_DW_Nominate=target_df.pred
        ))
        if (target_df.chamber_x == 'House of Representatives').iloc[0]:
            dot = p2.circle('x', 'y', fill_color='colors', fill_alpha=0.8, line_color=None, source=s, size=11)
        else:
            dot = p2.square('x', 'y', fill_color='colors', fill_alpha=0.8, line_color=None, source=s, size=11)
        return dot


    TOOLS = "crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"
    TOOLTIPS2 = [("Name", "@name"), ("Actual DW-Nominate Score", "@true_DW_Nominate"),
                 ("Predicted DW-Nominate Score", "@pred_DW_Nominate")]

    p2 = figure(title="Predicted VS. Actual DW-nominate Score",tooltips=TOOLTIPS2, tools=TOOLS,x_range=(-0.65,0.9),y_range=(-0.65,0.9),
                x_axis_label='Actual DW-Nominate Score',y_axis_label='Predicted DW-Nominate Score',plot_width=700, plot_height=700,toolbar_location="below")

    # add renderers for p2
    p2_renderer_collection = {}
    p2_renderer_collection['plot_info'] = {'group': {'Both training and testing data'},'buffer':set(),'alpha':0.1}
    p2_renderer_collection['dot_set'] = {}
    for i in m_DW.name:
        p2_renderer_collection['dot_set'][i] = createOneDot_for_p2(i)
    p2.line([-10, 10], [-10, 10], line_width=1, color='black')


    # p2
    select_test_train = Select(title='Select training or testing data to display',
                               value = 'Both training and testing data', options=['Both training and testing data', 'Training data', 'Testing data'])
    multichoice_DW = MultiChoice(value=[], options=list(m_DW.name))
    slider_alpha = Slider(start=0, end=0.8, value=0.1, step=.05, title="Alpha (Transparency)")


    # --- handler for p2 ----------
    def change_p2_visibility():
        alpha = p2_renderer_collection['plot_info']['alpha']
        if p2_renderer_collection['plot_info']['group'] == 'Both training and testing data':
            for k, v in p2_renderer_collection['dot_set'].items():
                v.glyph.fill_alpha = 0.8
        elif p2_renderer_collection['plot_info']['group'] == 'Testing data':
            for k, v in p2_renderer_collection['dot_set'].items():
                if feature_dict[k] == 1:
                    v.glyph.fill_alpha = 0.8
                else:
                    v.glyph.fill_alpha = alpha
        elif p2_renderer_collection['plot_info']['group'] == 'Training data':
            for k, v in p2_renderer_collection['dot_set'].items():
                if feature_dict[k] == 0:
                    v.glyph.fill_alpha = 0.8
                else:
                    v.glyph.fill_alpha = alpha
        else:
            politician_chosen = p2_renderer_collection['plot_info']['group']
            for k,v in p2_renderer_collection['dot_set'].items():
                if k in politician_chosen:
                    v.glyph.fill_alpha = 0.8
                else:
                    v.glyph.fill_alpha = alpha

    def handler_test_train(attr,old,new):
        p2_renderer_collection['plot_info']['group'] = new
        change_p2_visibility()

    def handler_multichoice_who(attr,old,new):
        p2_renderer_collection['plot_info']['group'] = set(new)
        change_p2_visibility()

    def handler_slider_alpha(attr,old,new):
        p2_renderer_collection['plot_info']['alpha'] = new
        if p2_renderer_collection['plot_info']['alpha'] != 'Both training and testing data':
            change_p2_visibility()
        else:
            return

    # p2's handler
    slider_alpha.on_change('value', handler_slider_alpha)
    select_test_train.on_change('value',handler_test_train)
    multichoice_DW.on_change('value',handler_multichoice_who)

    # curdoc().add_root(row(p2,column(slider_alpha,select_test_train,multichoice_DW)))
    return row(p2,column(slider_alpha,select_test_train,multichoice_DW))
