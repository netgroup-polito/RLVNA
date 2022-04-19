from django.urls import path
from .views import RyuControllerView, TopologyView, MLModelView, TrafficHostsView, DownloadDataView

urlpatterns = [
    path('topology', TopologyView.as_view()), #Reserve resources for the topology + Docker + configure OVS
    path('ryu', RyuControllerView.as_view()), #config.ini ryu + run ryu controller
    path('model', MLModelView.as_view()),      #config2.ini model + run model
    path('traffic', TrafficHostsView.as_view()),      #run host traffic
    path('download', DownloadDataView.as_view()),      #download host traffic
]