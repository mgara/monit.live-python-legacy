class MemoryCPUProcessStats(models.Model):
    process_id = models.ForeignKey('Process')
    date_last = models.DateTimeField()
    cpu_percent = models.FloatField(null=True)
    memory_percent = models.FloatField(null=True)
    memory_kilobyte = models.PositiveIntegerField(null=True)

    @classmethod
    def create(
            cls,
            process,
            tz_str,
            unixtimestamp,
            cpu_percent,
            memory_percent,
            memory_kilobyte
    ):
        entry = cls()
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entry.process_id = process
        entry.cpu_percent = cpu_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.memory_percent = memory_percent
        entry.save()
        return entry

    @classmethod
    def to_carbon(cls, entry, server_name, processname):
        metric = "{}.process.{}.cpu_percent".format(
            server_name, processname)
        collect_metric_from_datetime(
            metric, entry.cpu_percent, entry.date_last)
        metric = "{}.process.{}.memory_percent".format(
            server_name, processname)
        collect_metric_from_datetime(
            metric, entry.memory_percent, entry.date_last)
        metric = "{}.process.{}.memory_kilobyte".format(
            server_name, processname)
        collect_metric_from_datetime(
            metric, entry.memory_kilobyte, entry.date_last)

    @classmethod
    def to_elasticsearch(cls, entry, server_name, processname):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_process_{}_cpu_percent'.format(server_name, processname)] = entry.cpu_percent
        _doc['{}_process_{}_memory_percent'.format(server_name, processname)] = entry.memory_percent
        _doc['{}_process_{}_memory_kilobyte'.format(server_name, processname)] = entry.memory_kilobyte

        publish_to_elasticsearch(
            "monit",
            "process-stats",
            _doc
            )
