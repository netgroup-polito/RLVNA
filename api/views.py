from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import generics, status
from simplejson import JSONDecoder
from .serializers import RyuControllerSerializer, TopologySerializer, MLModelSerializer, TrafficHostsSerializer, DownloadDataSerializer
from .models import  RyuController, Topology, MLModel, TrafficHosts, DownloadData
from rest_framework.views import APIView
from rest_framework.response import Response
from .geni_utilities.config_geni import Experiment

# Create your views here.

class TopologyView(APIView):
    serializer_class = TopologySerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_topology = serializer.data.get('topology')
            print(input_topology)
            topo = Topology(topology=input_topology)
            #experiment.save()

            exp = Experiment()
            res = exp.create_topology(topo)

            #return Response(ExperimentSerializer(experiment).data, status=status.HTTP_201_CREATED)
            return Response(res, status=status.HTTP_201_CREATED)
        return Response({'Bad Request: Invalid data. '}, status=status.HTTP_400_BAD_REQUEST)

#TODO
class RyuControllerView(APIView):
    serializer_class = RyuControllerSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_data_frequency = serializer.data.get('data_frequency')
            input_support_switches = serializer.data.get('support_switches')
            ryu = RyuController(data_frequency=input_data_frequency, support_switches=input_support_switches)
            
            exp = Experiment()
            res = exp.configure_controller(ryu)

            return Response(res, status=status.HTTP_201_CREATED)
        return Response({'Bad Request: Invalid data. '}, status=status.HTTP_400_BAD_REQUEST)

class MLModelView(APIView):
    serializer_class = MLModelSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_num_support_switches = serializer.data.get('num_support_switches')
            input_op_penalty = serializer.data.get('op_penalty')
            input_helped_switches = serializer.data.get('helped_switches')
            input_data_frequency = serializer.data.get('data_frequency')

            model = MLModel(num_support_switches=input_num_support_switches, op_penalty=input_op_penalty, helped_switches=input_helped_switches, data_frequency=input_data_frequency)

            exp = Experiment()
            res = exp.configure_model(model)

            return Response(res, status=status.HTTP_201_CREATED)
        return Response({'Bad Request: Invalid data. '}, status=status.HTTP_400_BAD_REQUEST)

class TrafficHostsView(APIView):
    serializer_class = TrafficHostsSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_iperf_num = serializer.data.get('iperf_num')
            input_traffic_type = serializer.data.get('traffic_type')
            cfg = TrafficHosts(iperf_num=input_iperf_num, traffic_type=input_traffic_type)

            exp = Experiment()
            # res1 = exp.configure_hosts(cfg, 'train')
            res2 = exp.configure_hosts(cfg, 'test')

            return Response(res2, status=status.HTTP_201_CREATED)
        return Response({'Bad Request: Invalid data. '}, status=status.HTTP_400_BAD_REQUEST)

class DownloadDataView(APIView):
    serializer_class = DownloadDataSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            input_file = serializer.data.get('file')
            exp = Experiment()
            res2 = exp.download_file(input_file)

            return Response(res2, status=status.HTTP_201_CREATED)
        return Response({'Bad Request: Invalid data. '}, status=status.HTTP_400_BAD_REQUEST)
        
