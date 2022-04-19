from rest_framework import serializers
from .models import RyuController, Topology, MLModel, TrafficHosts, DownloadData


class TopologySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Topology
        fields = ('id', 'topology')


class RyuControllerSerializer(serializers.ModelSerializer):
    class Meta: 
        model = RyuController
        fields = ('id', 'data_frequency', 'support_switches')
        

class MLModelSerializer(serializers.ModelSerializer):
    class Meta: 
        model = MLModel
        fields = ('id', 'num_support_switches', 'op_penalty', 'helped_switches', 'data_frequency')

class TrafficHostsSerializer(serializers.ModelSerializer):
    class Meta: 
        model = TrafficHosts
        fields = ('id', 'iperf_num', 'traffic_type')

class DownloadDataSerializer(serializers.ModelSerializer):
    class Meta: 
        model = DownloadData
        fields = ('id', 'file')