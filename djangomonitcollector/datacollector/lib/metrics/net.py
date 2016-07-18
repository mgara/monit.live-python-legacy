
class NetStats():
    @classmethod
    def create(cls,
               net,
               tz_str,
               unixtimestamp,
               download_packet,
               download_bytes,
               download_errors,
               upload_packet,
               upload_bytes,
               upload_errors,
               ):
        entity = cls()
        tz = timezone(tz_str)
        entity.date_last = datetime.datetime.fromtimestamp(unixtimestamp, tz)
        entity.download_bytes = download_bytes
        entity.download_errors = download_errors
        entity.download_packet = download_packet
        entity.upload_bytes = upload_bytes
        entity.upload_errors = upload_errors
        entity.upload_packet = upload_packet
        return entity

    @classmethod
    def to_carbon(cls, entry, server_name, net):
        metric = "{}.net.{}.download.packet".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.download_packet, entry.date_last)

        metric = "{}.net.{}.download.bytes".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.download_bytes, entry.date_last)

        metric = "{}.net.{}.download.errors".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.download_errors, entry.date_last)

        metric = "{}.net.{}.upload.packet".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.upload_packet, entry.date_last)

        metric = "{}.net.{}.upload.bytes".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.upload_bytes, entry.date_last)

        metric = "{}.net.{}.upload.errors".format(
            server_name, net)
        collect_metric_from_datetime(
            metric, entry.upload_errors, entry.date_last)

    @classmethod
    def to_elasticsearch(cls, entry, server_name, net):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_net_{}_download_packet'.format(server_name, net)] = entry.download_packet
        _doc['{}_net_{}_download_bytes'.format(server_name, net)] = entry.download_bytes
        _doc['{}_net_{}_download_errors'.format(server_name, net)] = entry.download_errors
        _doc['{}_net_{}_upload_packet'.format(server_name, net)] = entry.upload_packet
        _doc['{}_net_{}_upload_bytes'.format(server_name, net)] = entry.upload_bytes
        _doc['{}_net_{}_upload_errors'.format(server_name, net)] = entry.upload_errors

        publish_to_elasticsearch(
            "monit",
            "net-stats",
            _doc
            )
