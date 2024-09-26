import os
import time
from datetime import datetime, date, timedelta
# PARAMETERS
CONFIGS = {
    "SECRET_KEY": os.urandom(30), # Set the secret key for session authentication
    "PERMANENT_SESSION_LIFETIME": timedelta(minutes=60)   
}
SQL_CONFIG = dict(
        database="portfolio_platform",
        user="postgres",
        host="db",
        port="5432",
        password="password"
)
CACHE_CONFIG = {
        'CACHE_TYPE': 'redis',
        # 'CACHE_REDIS_USER': 'default',
        'CACHE_REDIS_HOST': 'redis',
        'CACHE_REDIS_PORT': 6379,
        # 'CACHE_REDIS_PASSWORD': '5rP99RevPMW94rswBXAL',
        # 'CACHE_KEY_PREFIX': 'railway_redis_'
}
role_map = dict(max_sharpe='最大化夏普比率',
                max_sortino='最大化索提諾比率', 
                min_volatility='最小化波動率', 
                quadratic_utility='最大化效用函數')
