from django.db import models

# Create your models here.

class Topology(models.Model):
    topology = models.JSONField(null=False)

class RyuController(models.Model):
    data_frequency = models.IntegerField(null=False, default=1)
    support_switches = models.JSONField(null=False)

class MLModel(models.Model):
    num_support_switches = models.IntegerField(null=False)
    op_penalty = models.IntegerField(null=False)
    helped_switches = models.CharField(null=False, max_length=1024)
    data_frequency = models.IntegerField(null=False, default=1)

class TrafficHosts(models.Model):
    iperf_num = models.IntegerField(null=False, default=1)
    traffic_type = models.CharField(null=False, max_length=1024)

class DownloadData(models.Model):
    file = models.CharField(null=False, max_length=1024)