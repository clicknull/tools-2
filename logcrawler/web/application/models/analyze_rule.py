from django.db import models

from idc import IDCConfig


class AnalyzeRuleManager(models.Manager):

    foreign_entries = {"IDC_name": 0, "IDC_ip_address_port": 0, "service_name": 0}

    def filterX(self, **kwargs):
        params = {}
        for key in kwargs:
            if key.split("__", 1)[0] in self.foreign_entries:
                params["idc_collect__" + key] = kwargs[key]
            else:
                params[key] = kwargs[key]
        return self.filter(**params)

    def createX(self, **kwargs):
        schargs = {}
        for key in self.foreign_entries:
            schargs[key] = kwargs[key]
            del kwargs[key]
        kwargs["idc_collect"] = IDCConfig.objects.get(**schargs)
        return self.create(**kwargs)

    def updateX(self, coordinate, **kwargs):
        schargs = {}
        for key in self.foreign_entries:
            if key in kwargs:
                schargs[key] = kwargs[key]
                del kwargs[key]
        if len(schargs) > 0:
            kwargs["idc_collect"] = IDCConfig.objects.get(**schargs)
        return self.filterX(**coordinate).update(**kwargs)

    def deleteX(self, coordinate):
        return self.filterX(**coordinate).delete()

    def get_value_list(self, key):
        if key in self.foreign_entries:
            return list(IDCConfig.objects.values_list(key, flat=True).distinct())
        else:
            return list(self.values_list(key, flat=True).distinct())


class AnalyzeRule(models.Model):
    MANNER_CHOICES = (("onserver", ""), ("sendtokafka", ""), ("sendtokafka", "onserver&sendtokafka"))
    STATUS_CHOICES = (("active", ""), ("inactive", ""))

    id = models.AutoField(primary_key=True)
    idc_collect = models.ForeignKey(IDCConfig, db_column='idc_collect')
    regexp = models.CharField(max_length=255)
    dealwith_manner = models.CharField(max_length=45, null=True, default="onserver", choices=MANNER_CHOICES, db_column='dealwith_manner')
    parameters = models.CharField(max_length=400)
    status = models.CharField(max_length=45, null=True, default="inactive", choices=STATUS_CHOICES, db_column="status")
    timestamp = models.DateTimeField(auto_now=True)

    objects = AnalyzeRuleManager()

    class Meta:
        app_label = "application"
        db_table = u"analyze_rule"
        unique_together = ("idc_collect", "regexp")

    def render_json(self):
        id = self.id
        idc_collect = self.idc_collect.get_dict_of_uniques()

        IDC_name = idc_collect["IDC_name"]
        IDC_ip_address_port = idc_collect["IDC_ip_address_port"]
        service_name = idc_collect["service_name"]
        regexp = self.regexp
        dealwith_manner = self.dealwith_manner
        parameters = self.parameters
        status = self.status
        if self.timestamp:
            timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = self.timestamp

        json_obj = locals()
        del json_obj['self']
        del json_obj['idc_collect']
        return json_obj
