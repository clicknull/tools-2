from django.db import models


class IDCConfig(models.Model):
    status_CHOICES = (("active", ""), ("inactive", ""))
    currentSTATUS_CHOICES = (("online", ""), ("offline", ""))
    service_name_CHOICES = (("haproxy_access", ""), ("php_error", ""))

    id = models.AutoField(primary_key=True)
    IDC_name = models.CharField(max_length=45)
    IDC_ip_address_port = models.CharField(max_length=21)
    description = models.CharField(max_length=45, null=True, default="description", db_column="description")
    service_name = models.CharField(max_length=45, null=True, default="haproxy_access", choices=service_name_CHOICES, db_column="service_name")

    collect_interval_minutes = models.IntegerField(null=True, default=1)
    delay_minutes = models.IntegerField(null=True, default=1)
    max_delay_minutes = models.IntegerField(null=True, default=2)
    status = models.CharField(max_length=11, null=True, default="inactive", choices=status_CHOICES, db_column="status")
    current_status = models.CharField(max_length=11, null=True, default="offline", choices=currentSTATUS_CHOICES, db_column="current_status")
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "application"
        db_table = u"IDC_collect"
        unique_together = ("IDC_name", "IDC_ip_address_port", "service_name")

    def render_json(self):
        id = self.id
        IDC_name = self.IDC_name
        IDC_ip_address_port = self.IDC_ip_address_port
        description = self.description
        service_name = self.service_name
        collect_interval_minutes = self.collect_interval_minutes
        delay_minutes = self.delay_minutes
        max_delay_minutes = self.max_delay_minutes
        status = self.status
        current_status = self.current_status
        if self.timestamp:
            timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = self.timestamp
        json_obj = locals()
        del json_obj['self']
        return json_obj

    def get_dict_of_uniques(self):
        IDC_name = self.IDC_name
        IDC_ip_address_port = self.IDC_ip_address_port
        service_name = self.service_name
        uniques = locals()
        del uniques['self']
        return uniques
