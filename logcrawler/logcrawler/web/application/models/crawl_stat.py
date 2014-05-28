from django.db import models


class CrawlStatus(models.Model):
    DOWNLOADSTATUS_CHOICES = (("downloading", ""), ("done", ""), ("error", ""))

    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=500)

    filesize = models.IntegerField(null=True)
    collector_ip_address = models.CharField(max_length=45, null=True)
    start_timestamp = models.FloatField(null=True)
    end_timestamp = models.FloatField(null=True)
    status = models.CharField(max_length=11, null=True, choices=DOWNLOADSTATUS_CHOICES, db_column="status")
    description = models.TextField(null=True)

    class Meta:
        app_label = "application"
        db_table = u"download_task"

    def render_json(self):
        id = self.id
        url = self.url
        filesize = self.filesize
        collector_ip_address = self.collector_ip_address
        start_timestamp = self.start_timestamp
        end_timestamp = self.end_timestamp
        status = self.status
        description = self.description
        json_obj = locals()
        del json_obj['self']
        return json_obj
