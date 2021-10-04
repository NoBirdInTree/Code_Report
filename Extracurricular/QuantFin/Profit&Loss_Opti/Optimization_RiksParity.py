from scipy.optimize import minimize
import numpy as np

def calculate_portfolio_var(w,V):
    w = np.matrix(w)
    return (w*V*w.T)


def calculate_risk_contri(w,V):
    w = np.matrix(w)
    sigma = np.sqrt(calculate_portfolio_var(w,V))
    MRC = V*w.T / sigma
    RC = np.multiply(MRC,w.T)
    return RC


def risk_budget_objective(w,args):
    V, risk_contri = args[0],args[1]
    sigma = np.sqrt(calculate_portfolio_var(w,V))
    risk_target = np.asmatrix(np.multiply(sigma,risk_contri))
    asset_RC = calculate_risk_contri(w,V)
    J = sum(np.square(asset_RC-risk_target.T))[0,0]
    return J

def get_weight(V,w=None,risk_contri = None):
    if not w: w = [1/V.shape[0]] * V.shape[0]
    if not risk_contri: risk_contri = [1/V.shape[0]] * V.shape[0]
    V = np.asmatrix(V)
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # 限制条件一：全部投资
            {'type': 'ineq', 'fun': lambda w: w - 1e-6})  # 限制条件二：不可做空
    res = minimize(risk_budget_objective,w,args=[V,risk_contri],method='SLSQP',constraints=cons,options={'disp':True})
    w_rb = np.asmatrix(res.x)
    return w_rb

def avg_weight(n):
    return [1/n]*n

