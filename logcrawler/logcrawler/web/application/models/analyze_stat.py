from django.db import models


class AnalyzeStatus(models.Model):
    AnalyzeSTATUS_CHOICES = (("analyzing", ""), ("done", ""), ("error", ""))

    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=500)

    filesize = models.IntegerField(null=True)
    filelines = models.IntegerField(null=True)
    collector_ip_address = models.CharField(max_length=45, null=True)
    start_timestamp = models.FloatField(null=True)
    end_timestamp = models.FloatField(null=True)
    status = models.CharField(max_length=11, null=True, choices=AnalyzeSTATUS_CHOICES, db_column="status")
    description = models.TextField(null=True)

    class Meta:
        app_label = "application"
        db_table = u"analyze_task"

    def render_json(self):
        id = self.id
        path = self.path
        filesize = self.filesize
        filelines = self.filelines
        collector_ip_address = self.collector_ip_address
        start_timestamp = self.start_timestamp
        end_timestamp = self.end_timestamp
        status = self.status
        description = self.description
        json_obj = locals()
        del json_obj['self']
        return json_obj
