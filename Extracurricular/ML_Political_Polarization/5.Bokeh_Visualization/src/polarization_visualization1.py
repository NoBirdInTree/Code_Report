import pandas as pd
from bokeh.layouts import column, row
from bokeh.plotting import curdoc
from bokeh.models import MultiChoice, Select, Slider
from bokeh.plotting import figure, ColumnDataSource
import os
def createPolarizationgGraph():
    # Load data
    p = os.path.join(os.path.dirname(__file__),'..','data','full_output.tsv')
    m_collection = pd.read_csv(p,sep='\t')
    # m_collection = pd.read_csv('/Users/tylerliu/N_RA/Bokeh_Visualization/data/full_output.tsv',sep='\t')
    m_collection.name = m_collection.name.apply(str.strip)
    m_collection.name = m_collection.name.apply(str.title)
    colname = ['name','chamber_x','party','icpsr','nominate_dim1']
    m1 = m_collection[colname + ['tsne_dim1','tsne_dim2']]
    m1 = m1.rename(columns={'tsne_dim1':'estimated_polarization1','tsne_dim2':'estimated_polarization2','party':'party_int'})
    m2 = m_collection[colname + ['pca_dim1', 'pca_dim2']]
    m2 = m2.rename(columns={'pca_dim1': 'estimated_polarization1', 'pca_dim2': 'estimated_polarization2','party':'party_int'})
    m3 = m_collection[colname + ['svd_dim1', 'svd_dim2']]
    m3 = m3.rename(columns={'svd_dim1': 'estimated_polarization1', 'svd_dim2': 'estimated_polarization2','party':'party_int'})
    m4 = None
    merge = {'TSNE': m1, 'PCA': m2, 'SVD': m3, 'UMAP': m4}

    p = os.path.join(os.path.dirname(__file__),'..','data','Moderate members of Congress - Feuille 1.csv')
    feature_poli = pd.read_csv(p)
    # feature_poli = pd.read_csv('/Users/tylerliu/N_RA/Bokeh_Visualization/data/Moderate members of Congress - Feuille 1.csv')
    feature_poli = feature_poli.rename(columns={'Name ': 'name'})
    feature_poli = feature_poli[['name','Party','State', 'Caucus/Informal Group Affiliation']]
    feature_dict = {}
    for i in m_collection.name:
        feature_dict[i] = set()
        feature_dict[i].add(m_collection[m_collection.name==i].chamber_x.values[0])
        feature_dict[i].add('Republican') if m_collection[m_collection.name == i].party.values[0] == 1 else feature_dict[i].add('Democratic')
        if i in set(feature_poli['name']):
            poli = feature_poli[feature_poli['name'] == i]
            for j in ['Party', 'State', 'Caucus/Informal Group Affiliation']:
                feature_dict[i].add(poli[j].values[0])
    # -------------------------------------------------------

    # prepare some data
    def createOneDot_for_p1(method,who):
        target_df = merge[method]
        target_df = target_df[target_df.name == who]
        colors = [
            "#%02x%02x%02x" % (120 * (int(r) + 1), int(255 * (1 - abs(nom))), -120 * (int(r) - 1)) for r, nom in
            zip(target_df.party_int, target_df.nominate_dim1)
        ]
        s = ColumnDataSource(data=dict(
            x=target_df.estimated_polarization1,
            y=target_df.estimated_polarization2,
            name=target_df.name,
            colors=colors,
            true_DW_Nominate=target_df.nominate_dim1,
        ))
        if (target_df.chamber_x == 'House of Representatives').iloc[0]:
            dot = p1.circle('x', 'y', fill_color='colors', fill_alpha=0.8, line_color=None, source=s, size=11)
        else:
            dot = p1.square('x', 'y', fill_color='colors', fill_alpha=0.8, line_color=None, source=s, size=11)
        dot.visible = False
        return dot

    TOOLS = "crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"
    TOOLTIPS1 = [("Name", "@name"),("Actual DW-Nominate Score", "@true_DW_Nominate"),]

    # create a new plot with the tools above, and explicit ranges
    x_lim1 = (min(m1.estimated_polarization1)*1.1,max(m1.estimated_polarization1)*1.1)
    y_lim1 = (min(m1.estimated_polarization2)*1.1,max(m1.estimated_polarization2)*1.1)
    p1 = figure(title="Politicians who meet any one of conditions from the right multichoice boxes will be displayed here", tooltips=TOOLTIPS1, tools=TOOLS, x_range=x_lim1, y_range=y_lim1,
               x_axis_label='TSNE\'s dimension 1',y_axis_label='TSNE\'s dimension 2',plot_width=700, plot_height=700,toolbar_location="below")

    # add renderers for p1
    p1_renderer_collection = {'TSNE':{},'PCA':{},'SVD':{}}
    for i in ['TSNE','PCA','SVD']:
        for j in m1.name:
            p1_renderer_collection[i][j] = createOneDot_for_p1(i,j)
    # one more key for the storage of the plot information
    p1_renderer_collection['plot_info'] = {'group': {'House of Representatives','Senate'},'method':'TSNE','buffer':set(),'alpha':0.1}
    for k,v in p1_renderer_collection.items():
        if k == p1_renderer_collection['plot_info']['method']:
            for x,y in v.items():
                y.visible = True


    # --- create select and multichoice boxes
    # p1
    select_method = Select(title='Select which dimension reduction method',
                           value=p1_renderer_collection['plot_info']['method'],
                            options=['TSNE', 'PCA', 'SVD'])
    mutlichoice_group_SH = MultiChoice(title='Select politicians from senate or house of representative to display',
                          value=['House of Representatives', 'Senate'],options=list(set(m1.chamber_x)))
    mutlichoice_group_PARTY = MultiChoice(title='Select the politicians from which party to display',
                          value=[],options=list(set(feature_poli['Party'])))
    mutlichoice_group_STATE = MultiChoice(title='Select the politicians from which state to display',
                          value=[],options=list(set(feature_poli['State'])))
    mutlichoice_group_AFFILIATION = MultiChoice(title='Select the politicians from which Caucus / Informal Group Affiliation to display',
                          value=[],options=list(set(feature_poli['Caucus/Informal Group Affiliation'])))
    multichoice_who = MultiChoice(title='Select the individual politicians to display',value=[], options=list(m1.name))
    slider_alpha = Slider(start=0, end=0.8, value=0.1, step=.05, title="Alpha (Transparency)")

    # --- handler for p1 ----------
    def change_p1_visibility():
        method = p1_renderer_collection['plot_info']['method']
        group_to_display = p1_renderer_collection['plot_info']['group']
        alpha = p1_renderer_collection['plot_info']['alpha']
        for k,v in p1_renderer_collection[method].items():
            individual_feature = {k}.union(feature_dict[k])
            v.visible = True
            if individual_feature.intersection(group_to_display):
                v.glyph.fill_alpha = 0.8
            else:
                v.glyph.fill_alpha = alpha


    def handler_method(attr,old,new):
        if old == new:
            return
        for k,v in p1_renderer_collection[old].items():
            v.visible = False
        p1_renderer_collection['plot_info']['method'] = new
        change_p1_visibility()
        if new == 'PCA':
            (p1.x_range.start, p1.x_range.end) = (1.7, -1.7)
            (p1.y_range.start, p1.y_range.end) = (1.8, -1.8)
            (p1.xaxis.axis_label,p1.yaxis.axis_label) = ('PCA\'s dimension 1','PCA\'s dimension 2')
        elif new == 'SVD':
            (p1.x_range.start, p1.x_range.end) = (1.7, -1.7)
            (p1.y_range.start, p1.y_range.end) = (1.8, -1.8)
            (p1.xaxis.axis_label, p1.yaxis.axis_label) = ('SVD\'s dimension 1', 'SVD\'s dimension 2')
        elif new == 'UMAP':
            (p1.x_range.start, p1.x_range.end) = (1.7, -1.7)
            (p1.y_range.start, p1.y_range.end) = (1.8, -1.8)
            (p1.xaxis.axis_label, p1.yaxis.axis_label) = ('UMAP\'s dimension 1', 'UMAP\'s dimension 2')
        else:
            (p1.x_range.start, p1.x_range.end) = x_lim1
            (p1.y_range.start, p1.y_range.end) = y_lim1
            (p1.xaxis.axis_label, p1.yaxis.axis_label) = ('TSNE\'s dimension 1', 'TSNE\'s dimension 2')

    def handler_multichoice_group_SH(attr,old,new):
        update(old, new)

    def handler_multichoice_group_PARTY(attr, old, new):
        update(old, new)

    def handler_multichoice_group_STATE(attr, old, new):
        update(old, new)

    def handler_multichoice_group_AFFILIATION(attr, old, new):
        update(old, new)

    def handler_multichoice_who(attr,old,new):
        update(old,new)

    def update(old,new):
        p1_renderer_collection['plot_info']['group'] = p1_renderer_collection['plot_info']['group'] - set(old)
        p1_renderer_collection['plot_info']['group'] = p1_renderer_collection['plot_info']['group'].union(set(new))
        change_p1_visibility()

    def handler_slider_alpha(attr,old,new):
        if old == new:
            return
        p1_renderer_collection['plot_info']['alpha'] = new
        change_p1_visibility()

    # p1's handler
    select_method.on_change('value',handler_method)
    mutlichoice_group_SH.on_change('value', handler_multichoice_group_SH)
    mutlichoice_group_PARTY.on_change('value', handler_multichoice_group_PARTY)
    mutlichoice_group_STATE.on_change('value', handler_multichoice_group_STATE)
    mutlichoice_group_AFFILIATION.on_change('value', handler_multichoice_group_AFFILIATION)
    multichoice_who.on_change('value',handler_multichoice_who)

    slider_alpha.on_change('value',handler_slider_alpha)
    # curdoc().add_root(row(p1,column(slider_alpha,select_method,mutlichoice_group_SH,mutlichoice_group_PARTY,
    #                                 mutlichoice_group_STATE,mutlichoice_group_AFFILIATION,multichoice_who)))
    return row(p1,column(slider_alpha,select_method,mutlichoice_group_SH,mutlichoice_group_PARTY,mutlichoice_group_STATE,mutlichoice_group_AFFILIATION,multichoice_who))