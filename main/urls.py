from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
        path('', views.index, name='index'),
        path('strategy', views.strategy, name='strategy'),
        path('add-strategy', views.add_strategy, name='add_strategy'),
        path('delete-strategy/<num>', views.delete_strategy, name='delete_strategy'),
        path('strategy-detail/<num>', views.strategy_detail, name='strategy_detail'),
        path('save-code/<num>', views.save_code, name='save_code'),
        path('run-code/<num>', views.run_code, name='run_code'),
        path('data/get-charts/<num>', views.get_charts, name='get_charts'),
        path('data/get-log/<num>', views.get_log, name='get_log'),
        path('data/get-progress/<num>', views.get_progress, name='get_progress'),
        path('logout-user', views.logout_user, name='logout_user'),
        path('data/prices/<code>/<date>', views.get_prices, name='get_prices'),
        path('detail/<code>', views.detail, name='detail'),
        path('data/price-change/<code>/<date>', views.price_change, name='price_change'),
        path('data/fund-info/<code>/<date>/<freq>/<item>', views.fund_info, name='fund_info'),
        #url(r'^$', views.index, name='index'),
]
