import json
import time
import numpy as np
import pandas as pd
from scipy.optimize import minimize

class MVO(object):
    @staticmethod
    def portfolio_info(w, ret, market_ret, rf=0):
        # return and drawdown
        retPort = ret@w # T-dimensional array
        cum_ret = (retPort+1).cumprod()
        rolling_max=np.maximum.accumulate(cum_ret)
        mdd = np.max((rolling_max - cum_ret)/rolling_max)

        ## Sharpe Ratio
        stdPort = np.std(retPort) 
        vol = stdPort*15.87451
        annual_ret = np.mean(retPort) * 252
        annual_sr = (annual_ret-rf) / vol

        ## alpha, beta
        cov = np.cov(retPort, market_ret)
        beta = cov[0, 1] / cov[1, 1]
        alpha = annual_ret - rf - beta*(np.mean(market_ret) * 252 - rf)
        R2 = cov[0, 1]**2/(cov[0, 0] * cov[1, 1])

        ## n-day 95% VaR
        var10 = -annual_ret*(10/252) +  1.645*vol*(10/252)**(1/2)
        d = dict(annual_ret = annual_ret,
                vol=vol,
                mdd=mdd,
                annual_sr=annual_sr,
                beta=beta,
                alpha=alpha, 
                var10=var10,
                R2=R2) 
        return {key: round(d[key], 2) for key in d}
    @staticmethod
    def sharpe_ratio(w, ret):
        cov = np.cov(ret.T)
        # print(cov.shape, w.shape)
        retPort = ret@w # T-dimensional array
        stdPort = np.std(retPort) 
        return np.mean(retPort)/stdPort
    @staticmethod
    def sharpe_grad(w, ret, cov):
        manual_ret = np.mean(ret, axis=0)
        # print(cov.shape, w.shape)
        retPort = ret@w # T-dimensional array
        stdPort = np.std(retPort) 
        g1=manual_ret/stdPort
        g2=np.mean(retPort)*stdPort**(-3)*cov@w
        return g1-g2
    @staticmethod
    def sortino_ratio(w, ret):
        retPort = ret@w # T-dimensional array
        stdPort = np.std(np.maximum(-retPort, 0))
        return np.mean(retPort)/stdPort
    @staticmethod
    def sortino_grad(w, ret, cov_sor):
        manual_ret = np.mean(ret, axis=0)
        # print(cov.shape, w.shape)
        retPort = ret@w # T-dimensional arrayss
        stdPort = np.std(retPort) 
        g1=manual_ret/stdPort
        g2=np.mean(retPort)*stdPort**(-3)*cov_sor@w
        return g1-g2
    @staticmethod
    def sortino_ratio(w, ret):
        retPort = ret@w # T-dimensional array
        stdPort = np.std(np.maximum(-retPort, 0))
        return np.mean(retPort)/stdPort
    @staticmethod
    def sortino_grad(w, ret, cov_sor):
        manual_ret = np.mean(ret, axis=0)
        # print(cov.shape, w.shape)
        retPort = ret@w # T-dimensional arrayss
        stdPort = np.std(retPort) 
        g1=manual_ret/stdPort
        g2=np.mean(retPort)*stdPort**(-3)*cov_sor@w
        return g1-g2
    # equivalent opt problem with min vol
    @staticmethod
    def volatility(w, ret):
        retPort = ret@w # T-dimensional array
        return np.std(retPort) 
    @staticmethod
    def volatility_grad(w, ret, cov):
        retPort = ret@w # T-dimensional array
        stdPort = np.std(retPort)
        return cov@w/stdPort
    @staticmethod
    def quadratic_utility(w, ret, gamma):
        retPort = ret@w # T-dimensional array
        varPort = np.var(retPort) 
        return np.mean(retPort) - 0.5*gamma*varPort
    @staticmethod
    def quadratic_utility_grad(w, ret, cov, gamma):
        manual_ret = np.mean(ret, axis=0)
        return manual_ret - gamma*cov@w
    @classmethod
    def opt(cls, ret, gamma=0, role="max_sharpe"):
        n = ret.shape[1]
        init=np.ones(n)/n
        if role=="max_sharpe":
            if n==1:
                cov=np.array(np.cov(ret.T))  
            else:
                cov=np.cov(ret.T)
            loss = lambda w: -cls.sharpe_ratio(w, ret) 
            grad = lambda w: -cls.sharpe_grad(w, ret, cov)
        elif role=="max_sortino":
            if n==1:
                cov = np.cov(np.maximum(ret, 0).T)
            else:
                cov = np.array(np.cov(np.maximum(ret, 0).T))
            loss = lambda w: -cls.sortino_ratio(w, ret)
            grad = lambda w: -cls.sortino_grad(w, ret, cov)
        elif role=="min_volatility":
            if n==1:
                cov=np.array(np.cov(ret.T))
            else:
                cov=np.cov(ret.T) 
            loss = lambda w: cls.volatility(w, ret)
            grad = lambda w: cls.volatility_grad(w, ret, cov)
        elif role=="quadratic_utility":
            if n==1:
                cov=np.array(np.cov(ret.T)) 
            else:
                cov=np.cov(ret.T)
            loss = lambda w: -cls.quadratic_utility(w, ret, gamma)
            grad = lambda w: -cls.quadratic_utility_grad(w, ret, cov, gamma)
        else:
            return init
        if n==1:
            bnds = [[0,1]]
        else:
            bnds = [[0, 0.6] for i in range(n)]
        opts = {'maxiter': 1000, 'disp': False}
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        result = minimize(loss, init, method="SLSQP",\
                          options=opts, bounds=bnds, tol = None, jac = grad, constraints=cons)
        sol = result['x']
        return np.round(sol, 2)




    
    
        




        
    
