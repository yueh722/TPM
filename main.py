#coding=utf-8
from flask import Flask, render_template, request, redirect, url_for, g, session, flash, jsonify
# from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from markupsafe import escape
from werkzeug.security import generate_password_hash, check_password_hash 
from datetime import datetime, date, timedelta
from flask_cors import CORS

import os
import json
import time
import random
import string
import logging
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
import plotly
import plotly.express as px
from portfolio_builder import MVO
from config import *
from logging.handlers import RotatingFileHandler
pd.options.plotting.backend = "plotly"

#####################
# Create a file handler
file_handler = RotatingFileHandler('flask.log', maxBytes=1024 * 1024 * 10, backupCount=10)
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
#####################

app = Flask(__name__)
app.config.from_mapping(CONFIGS)
app.config.update(CACHE_CONFIG)
cache = Cache(app)
CORS(app, resources={r"/*": {"origins": "*"}})

app.logger.addHandler(file_handler)

# Load Assets
with open('assets_tw.json') as f:
    data_tw = json.load(f)
with open('assets_us.json') as f:
    data_us = json.load(f)

def login_required():
    if not 'username' in session:

        
        session['username'] = 'yueh722'
        session['user_id'] = 4
        session['privilege'] = False
        session['update_freq'] = 100
        session['lastCreateTime'] = 1717749444.6265938#time.time()
        #session['tw'] = 0
        
        return True

        #return False
    else:
        return True

    


def get_stock(conn, stock_list, tw):
    print("Stock List:", stock_list)
    print("TW:", tw)
    # Query DB
    if tw==1:
        sql="SELECT ticker, date, price FROM stock_price_tw where ticker = ANY(%s);"
        with conn:
            with conn.cursor() as curs:
                curs.execute(sql, (stock_list, ))
                data= curs.fetchall()
    else:
        sql1="SELECT ticker, date, price FROM stock_price where ticker = ANY(%s)"
        sql2="SELECT ticker, date, price FROM stock_price_tw where ticker = ANY(%s) ;"
        with conn:
            with conn.cursor() as curs:
                curs.execute(sql1, (stock_list,))
                data_us= curs.fetchall()
                curs.execute(sql2, (stock_list,))
                data_tw= curs.fetchall()
                data = data_us+data_tw

    dfStock = pd.DataFrame(data, columns=['ticker', 'date', 'price'])
    dfStock['date'] = pd.to_datetime(dfStock['date'])
    dfStock = dfStock.drop_duplicates()
    g = dfStock.groupby('ticker')
    port = pd.concat([g.get_group(t).set_index('date')['price'] for t in stock_list], axis=1, join='inner')
    port.columns=stock_list
    return port
def rolling_optimize(ret, lookback=126, backtest=126, role="max_sharpe", gamma=None):
    n, num = ret.shape
    period = (n - lookback)//backtest+1
    weights = []
    start = []
    rets = []
    for i in range(period):
        curr = i*backtest+lookback
        data_train = ret.iloc[curr-lookback:curr, :].to_numpy()
        data_test = ret.iloc[curr:curr+backtest, :]
        if len(data_test) == 0:
            break
        w = MVO.opt(data_train, role=role, gamma=gamma)
        start.append(data_test.index[0])
        weights.append(w)
        rets.append(data_test.to_numpy()@w)
    weight = pd.DataFrame(weights, columns=ret.columns, index=pd.to_datetime(start))
    rets = np.hstack(rets)
    equally_weighted = ret.iloc[lookback:, :].to_numpy()@np.ones(num)/num
    rets = pd.DataFrame(np.vstack([rets, equally_weighted]).T, columns=['Portfolio', 'Equally'], index=ret.index[lookback:])
    return weight, rets

# Define the route for the index pages
@app.route('/')
# @cache.cached(timeout=300)
def index():
    conn = psycopg2.connect(**SQL_CONFIG)
    cur = conn.cursor()
    # Number of effective users
    cur.execute("select count(b.a) as num_effective_users from (select min(id) as a from strategy group by username) as b")
    num_effective_users = cur.fetchone()[0]
    # Number of effective strategies
    cur.execute("select count(id) as num_effective_strategies from strategy where annual_sr!=0")
    num_effective_strategies = cur.fetchone()[0]
    cur.close()
    conn.close()

    return render_template('base.html',num_effective_users=num_effective_users, num_effective_strategies=num_effective_strategies)

# Login Page
@app.route('/login')
def login():
    if 'username' in session:
        return render_template('base.html')
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    # Get the username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')
    ## Connect to the database
    conn = psycopg2.connect(**SQL_CONFIG)
    with conn:
        with conn.cursor() as curs:
            curs.execute("select * from users where username = %s;", (username, ))
            data = curs.fetchone()
    conn.close()

    # Authentication
    if (data is None) or (username is None) or (password is None):
        flash('使用者代號不對或密碼不對，請再試一次。', 'danger')
        return render_template('login.html')
    elif check_password_hash(data[2], password):
        session['username'] = username.split('@')[0]
        session['user_id'] = data[0]
        session['privilege'] = data[-1]
        session['update_freq'] = 100
        session['lastCreateTime'] = time.time()
        session['tw'] = 1
        session['currStockList'] = []
        #flash(f"成功登入，歡迎您 {session['username']} !", 'success')

        flash(f"成功登入，歡迎您 {session['username']} ! "
          f"User ID: {session['user_id']}, Privilege: {session['privilege']}, "
          f"Last Create Time: {session['lastCreateTime']}, TW: {session['tw']}, "
          f"Current Stock List: {session['currStockList']}", 'success')

        app.logger.info(f"User logged in: username={session['username']},ser_id={session['user_id']}, "
                        f"privilege={session['privilege']}, lastCreateTime={session['lastCreateTime']}, "
                        f"tw={session['tw']}, currStockList={session['currStockList']}")

        return redirect(url_for('index'))
    else:
        flash('使用者代號不對或密碼不對，請再試一次。', 'danger')
        return render_template('login.html')

# Registration Page
@app.route('/registration')
def registration():
    if login_required():
        return redirect(url_for('index'))
    return render_template('registration.html')

@app.route('/registration', methods=['POST'])
def registration_post():
    # Get the username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')
    rep_password = request.form.get('rep-password')
    # check password
    if not password is None and password == rep_password:
        conn = psycopg2.connect(**SQL_CONFIG)
        ## Connect to the database
        with conn.cursor() as curs:
            curs.execute("select * from users where username = %s;", (username, ))
            data = curs.fetchone()
        if data is None:
            with conn:
                with conn.cursor() as curs:
                    curs.execute("insert into users (username, password) values (%s, %s);", (username, generate_password_hash(password)))
            # conn.commit()
        else:
            flash('使用者已存在。', 'warning')
            return redirect(url_for('login'))
        conn.close()
        name = username.split('@')[0]
        flash(f'註冊成功！ 歡迎您, {name}。', 'success')
        return redirect(url_for('login'))
    else:
        flash('密碼不符合，請再次輸入。', 'warning')
        return redirect(url_for('registration'))
        
# Logout Page
@app.route('/logout', methods=['GET'])
def logout():
    if login_required():
        pass
    else:
        flash('請先登入。', 'warning')
        return redirect(url_for('login'))
    if 'username' in session:
        session.clear()
    flash(f"成功登出!", 'success')
    return redirect(url_for('index'))



@app.route('/strategy')
# @cache.cached(timeout=60)
def strategy():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    session['tw'] = 0
    return render_template('strategy_tw.html', data_us = data_us, data_tw=data_tw, stock=['TSLA'])




@app.route('/strategy_tw')
# @cache.cached(timeout=60)
def strategy_tw():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    session['tw'] = 1
    return render_template('strategy_tw.html', data_tw=data_tw, stock=['2330.TW'])


@app.route('/postStock', methods=['POST'])
def submit_stock_list():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))

    #Parse stock_list and check for 'TW' or 'TWO'
    stock_list = request.form.get('stockList') # this is string
    stock_list = json.loads(stock_list) # Load stock_list as list

    session['currStockList'] = stock_list

    #檢查是台股或美股
    contains_tw = any('.TW' in stock or '.TWO' in stock for stock in stock_list)

    if contains_tw:
        session['tw'] = 1
    else:
        session['tw'] = 0

    if not 'tw' in session:
        return redirect(url_for('index'))


    # Update Session
    app.logger.info("UPDATE ASSET")
    if session['update_freq']==0:
        app.logger.info("Too Frequent")
        return 'update to frquent!'
    else: 
        session['update_freq']-=1
   

    ## Query DB
    conn = psycopg2.connect(**SQL_CONFIG)
    port = get_stock(conn, stock_list, session['tw'])
    if len(port.index) > 1008:
        port = port.iloc[-1008:, :]
    conn.close()
    port = port.iloc[::3, :]
    port = port/port.iloc[0, :]

    fig = port.plot(title='資產價格變化', labels=dict(index="Date", value="Price", variable="Assets"))
    fig['layout'] = {}
    # 序列化
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # for key in request.form:
    #     app.logger.info("KEY: %s, ", key)
    #     print(key, request.form[key])
    # Do something with the stock list heres
    return graphJSON

@app.route('/postPort', methods=['POST'])
def buildPort():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))

    #Parse stock_list and check for 'TW' or 'TWO'
    stock_list = request.form.get('stockList') # this is string
    stock_list = json.loads(stock_list) # Load stock_list as list

    session['currStockList'] = stock_list

    #檢查是台股或美股
    contains_tw = any('.TW' in stock or '.TWO' in stock for stock in stock_list)

    if contains_tw:
        session['tw'] = 1
    else:
        session['tw'] = 0

    if not 'tw' in session:
        return redirect(url_for('index'))

    #if 'lastCreateTime' not in session or session['lastCreateTime'] is None:
    #   session['lastCreateTime'] = 0

    # Stop frequently building strategy
    if time.time() - session['lastCreateTime'] < 60:
        less = round(time.time()-session['lastCreateTime'], 1)
        print(f"UNTIL: {less}")
        return f'<span>投資組合建立時間間隔(或與登入時間間隔)必須大於60秒！還差: {less} 秒。</span>'
    session['lastCreateTime'] = time.time()
    # for key in request.form:
    #     print(key, request.form[key], type(request.form[key]))
    
    # Portfolio Info , random name generator
    name = request.form.get('name')
    if name == '':
        prefix=''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        name= prefix + f"-{round(time.time()%100, 2)}"

    # Opt Parameters
    comp = request.form.get('comp')
    ts = request.form.get('ts')
    # ts = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
    role = request.form.get('role')
    lookback = int(request.form.get('lookback'))
    backtest = int(request.form.get('frequency'))
    gamma = float(request.form.get('gamma'))/100
    comment = request.form.get('comment')
    stock_list = json.loads(request.form.get('stockList'))


    # Algorithm MVO
    print(f"{'-'*10}Enter Algorithms{'-'*10}")
    # Query DB
    market_asset = '0050.TW' if session['tw']==1 else 'SPY'
    conn = psycopg2.connect(**SQL_CONFIG)
    if market_asset in stock_list:
        port = get_stock(conn, stock_list, session['tw'])
        market = port[market_asset]
    else:
        port = get_stock(conn, stock_list+[market_asset], session['tw'])
        market = port[market_asset]
        port = port[stock_list]
    # Optimization
    n = len(port.index)
    if n < lookback+backtest+63:
        return f'''<span>投資組合無法建立，資料長度與所選參數不符。</span>'''
    elif n > 1009+lookback:
        port = port.iloc[-(1009+lookback):, :]
        market = market.iloc[-1009:]
    else:
        market = market.iloc[lookback:]

    length, num = port.shape   
    ret = port.pct_change().dropna()
    weight, rets = rolling_optimize(ret, lookback, backtest, role=role, gamma=gamma)
    weight.index = weight.index.astype(str)
   
    rets.index = rets.index.astype(str)
    rets= rets.round(5)
    

    # Get portfolio info.
    info = MVO.portfolio_info(np.array([1]), rets['Portfolio'].to_numpy().reshape(-1, 1), market.pct_change().dropna().to_numpy())
    data = (ts, name, session.get('username').split('@')[0], comp, role, info['annual_ret'],
            info['vol'], info['mdd'], info['annual_sr'],
            info['beta'], info['alpha'], info['var10'], info['R2'], gamma, True, comment, stock_list, json.dumps(weight.to_dict(orient="split")), json.dumps(rets.to_dict(orient="split")))
    sql='insert into strategy \
        (date, name, username,\
            competition, role, annual_ret,\
            vol, mdd, annual_sr, beta, alpha,\
            var10, R2, gamma, tw, notes, assets, weight, ret)\
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;'
    with conn:
        with conn.cursor() as curs:
            #print("DATA : ",data)
            curs.execute(sql, data)

            strategy_id = curs.fetchone()[0]
    conn.close()
    print(f"{'-'*10}Strategy write in Success{'-'*10}")
    return f'''<span>投資組合已完成建立，請點擊 <a class="badge rounded-pill text-bg-info" href="/result_view?strategy_id={strategy_id}">{strategy_id}</a>查詢分析結果。</span>'''



@app.route('/custom')
# @cache.cached(timeout=60)
def custom():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    return render_template('custom.html')

@app.route('/custom', methods=['POST'])
def custom_post():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    port = pd.read_csv(request.files['csv_file'], index_col=0, parse_dates=True)
    role = request.form.get('role')
    lookback = int(request.form.get('lookback'))
    backtest = int(request.form.get('frequency'))
    gamma = float(request.form.get('gamma'))/100
    # Optimization
    n = len(port.index)
    if n < lookback+backtest+63:
        return f'''<span>投資組合無法建立，資料長度與所選參數不符。</span>'''
    elif n > 1009+lookback:
        port = port.iloc[-(1009+lookback):, :]
    else:
        pass
    length, num = port.shape   
    ret = port.pct_change().dropna()
    weight, rets = rolling_optimize(ret, lookback, backtest, role=role, gamma=gamma)
    weight.index = weight.index.astype(str)
    rets.index = rets.index.astype(str)
    rets= rets.round(5)

    info = MVO.portfolio_info(np.array([1]), rets['Portfolio'].to_numpy().reshape(-1, 1), np.zeros(len(ret)-lookback))
    info['username'] = session.get('username').split('@')[0]
    info['role'] = role_map[role]
    info['id']='Custom data'
    info['name']='Custom data'
    info['date'] = '-'
    info['alpha'] = '-'
    info['beta'] = '-'
    info['r2'] = '-'
    info['assets'] = list(port.columns)
    # Plotting weight
    fig = px.bar(weight)
    fig['layout'] = {}
    info['weight'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Plotting weight
    fig = (rets+1).cumprod().iloc[::5, :].plot()
    fig['layout'] = {}
    info['ret'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Plotting ret bars
    rets.index.name = 'date'
    rets.index = pd.to_datetime(rets.index)
    ret_hist = rets.to_period('Q').groupby('date').apply(lambda x: (x+1).prod()-1)
    ret_hist.index = ret_hist.index.astype(str)
    fig = px.bar(ret_hist)
    fig['layout'] = {}
    info['bar'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('result_view.html', data=info)

@cache.memoize(60)
def getStrategy():
    conn = psycopg2.connect(**SQL_CONFIG)
    with conn:
        with conn.cursor() as curs:
            sql="select id, date, name, username, annual_ret, vol, annual_sr, mdd\
                    from strategy order by id desc limit 50"
            curs.execute(sql)
            data= curs.fetchall()
    conn.close()
    return data

@cache.memoize(60)
def getPostStrategy(role, comp):
    if role == "my":
        conn = psycopg2.connect(**SQL_CONFIG)
        with conn:
            with conn.cursor() as curs:
                sql=f"select id, date, name, username, annual_ret, vol, annual_sr, mdd\
                            from strategy where username=%s order by id desc limit 50;"
                curs.execute(sql, (session['username'], ))
                data= curs.fetchall()
        conn.close()
        return data
    if role in ['id', 'annual_ret', 'annual_sr', 'vol']:
        pass
    else:
        role='id'
    if role == 'vol':
        order= 'asc'
    else:
        order= 'desc'
    if comp == 'none':
        comp=None
    conn = psycopg2.connect(**SQL_CONFIG)
    with conn:
        with conn.cursor() as curs:
            if comp is None:
                sql=f"select id, date, name, username, annual_ret, vol, annual_sr, mdd\
                        from strategy order by {escape(role)} {escape(order)} limit 50"
                curs.execute(sql)
            else:
                sql=f"select id, date, name, username, annual_ret, vol, annual_sr, mdd\
                            from strategy where competition=%s order by {escape(role)} {escape(order)} limit 50;"
                curs.execute(sql, (comp, ))
            data= curs.fetchall()
    conn.close()
    return data

@app.route('/result_PostStrategy', methods=[ 'POST'])
def result_PostStrategy():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))

    role = request.form.get('role')
    comp = request.form.get('competition')
    data = getPostStrategy(role, comp)
    return jsonify(data)


@app.route('/result', methods=['GET', 'POST'])
def result():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    if request.method=='GET':
        data = getStrategy()
        return render_template('result.html', strategy_data=data)
    elif request.method=='POST':
        role = request.form.get('role')
        comp = request.form.get('competition')
        data = getPostStrategy(role, comp)
        return render_template('result.html', strategy_data=data)

@app.route('/result_view')
def result_view():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    if not 'strategy_id' in request.args:
        return redirect(url_for('index'))
    else:
        sid = request.args.get('strategy_id')
    strategy_id = request.args.get('strategy_id')
    sql="""select * from strategy where id=%s;"""
    conn = psycopg2.connect(**SQL_CONFIG)
    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            curs.execute(sql, (sid, ))
            data= curs.fetchone()
    conn.close()
    # Processing data
    data = dict(data)
    data['role'] = role_map[data['role']]
    w = data['weight']
    r = data['ret']
    w = pd.DataFrame(w['data'], columns=w['columns'], index=w['index'])
    r = pd.DataFrame(r['data'], columns=r['columns'], index=r['index'])
    # Plotting weight
    fig = px.bar(w)
    fig['layout'] = {}
    data['weight'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Plotting weight
    fig = (r+1).cumprod().iloc[::5, :].plot()
    fig['layout'] = {}
    data['ret'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    # Plotting ret bars
    r.index.name = 'date'
    r.index = pd.to_datetime(r.index)
    ret_hist = r.to_period('Q').groupby('date').apply(lambda x: (x+1).prod()-1)
    ret_hist.index = ret_hist.index.astype(str)
    fig = px.bar(ret_hist)
    fig['layout'] = {}
    data['bar'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    session['currStockList'] = data['assets']
    return render_template('result_view.html', data=data)

@app.route('/copy_portfolio')
def copy_portfolio():
    if login_required():
        pass
    else:
        flash('使用投組功能請先登入。', 'warning')
        return redirect(url_for('login'))
    if not 'tw' in session:
        return redirect(url_for('index'))
    session['tw'] = 0
    return render_template('strategy_tw.html', data_us = data_us, data_tw=data_tw, stock=session['currStockList'])
    
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug = True)
