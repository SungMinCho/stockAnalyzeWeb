from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
        path('', views.index, name='index'),
        path('strategy', views.strategy, name='strategy'),
        path('strategy-detail/<num>', views.strategy_detail, name='strategy_detail'),
        path('data/get-charts/<num>', views.get_charts, name='get_charts'),
        path('logout-user', views.logout_user, name='logout_user'),
        path('data/prices/<code>/<date>', views.get_prices, name='get_prices'),
        path('detail/<code>', views.detail, name='detail'),
        path('data/price-change/<code>/<date>', views.price_change, name='price_change'),
        path('data/fund-info/<code>/<date>/<freq>/<item>', views.fund_info, name='fund_info'),
        #url(r'^$', views.index, name='index'),
]
