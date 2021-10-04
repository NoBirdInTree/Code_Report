from scipy.optimize import minimize
import numpy as np
import pickle
from Win_Rate_Cal import getAbsTrue
import math

def stat(x):
    mu = np.mean(x,0)
    cov = (x*100).cov(0)
    return mu,cov

def fun_std(w,args):
    mu,cov = args[0],args[1]
    w = np.array(w)
    w = w / sum(w)
    std = math.sqrt(w.T.dot(cov).dot(w))
    return std

def fun_mean(w,args):
    mu,cov = args[0],args[1]
    w = np.array(w)
    w = w / sum(w)
    mean = w.T.dot(mu)
    return mean

def calpV(df,w):
    return

def get_MM_weight(df,r=0):
    mu, cov = stat(df)
    cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1},{'type': 'ineq', 'fun': lambda x: fun_mean(x,[mu,cov]) - r})
    res = minimize(fun_std,[1/len(mu) for i in range(len(mu))],args=[mu,cov],method='SLSQP',bounds = tuple((0,1) for i in range(len(mu))),constraints = cons)
    return res['x']
