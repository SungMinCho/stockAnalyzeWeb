from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
        path('', views.index, name='index'),
        path('strategy', views.strategy, name='strategy'),
        path('logout-user', views.logout_user, name='logout_user'),
        path('data/prices/<code>/<date>', views.get_prices, name='get_prices'),
        path('detail/<code>', views.detail, name='detail'),
        #url(r'^$', views.index, name='index'),
]
