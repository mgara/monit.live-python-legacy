class MemoryCPUSystemStats():

    @classmethod
    def create(cls,
               system,
               tz_str,
               data_timestamp,
               load_avg01,
               load_avg05,
               load_avg15,
               cpu_user,
               cpu_system,
               cpu_wait,
               memory_percent,
               memory_kilobyte,
               swap_percent,
               swap_kilobyte
               ):
        entry = cls()
        tz = timezone(tz_str)
        entry.date_last = datetime.datetime.fromtimestamp(data_timestamp, tz)
        entry.load_avg01 = load_avg01
        entry.load_avg05 = load_avg05
        entry.load_avg15 = load_avg15
        entry.cpu_user = cpu_user
        entry.cpu_system = cpu_system
        entry.cpu_wait = cpu_wait
        entry.memory_percent = memory_percent
        entry.memory_kilobyte = memory_kilobyte
        entry.swap_percent = swap_percent
        entry.swap_kilobyte = swap_kilobyte
        entry.save()
        return entry

    @classmethod
    def to_carbon(cls, entry, server_name):
        metric = "{}.system.load.avg01".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.load_avg01, entry.date_last)
        metric = "{}.system.load.avg05".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.load_avg05, entry.date_last)

        metric = "{}.system.cpu.user".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.cpu_user, entry.date_last)
        metric = "{}.system.cpu.system".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.cpu_system, entry.date_last)
        metric = "{}.system.cpu.wait".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.cpu_wait, entry.date_last)

        metric = "{}.system.memory.percent".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.memory_percent, entry.date_last)
        metric = "{}.system.memory.kilobyte".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.memory_kilobyte, entry.date_last)

        metric = "{}.system.swap.percent".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.swap_percent, entry.date_last)
        metric = "{}.system.swap.kilobyte".format(
            server_name)
        collect_metric_from_datetime(
            metric, entry.swap_kilobyte, entry.date_last)

    @classmethod
    def to_elasticsearch(cls, entry, server_name):
        _doc = dict()
        _doc['timestamp'] = entry.date_last
        _doc['{}_system_load_avg01'.format(server_name)] = entry.load_avg01
        _doc['{}_system_load_avg05'.format(server_name)] = entry.load_avg05
        _doc['{}_system_load_avg15'.format(server_name)] = entry.load_avg15
        _doc['{}_system_cpu_user'.format(server_name)] = entry.cpu_user
        _doc['{}_system_cpu_system'.format(server_name)] = entry.cpu_system
        _doc['{}_system_cpu_wait'.format(server_name)] = entry.cpu_wait
        _doc['{}_system_memory_percent'.format(server_name)] = entry.memory_percent
        _doc['{}_system_memory_kilobyte'.format(server_name)] = entry.memory_kilobyte
        _doc['{}_system_swap_percent'.format(server_name)] = entry.swap_percent
        _doc['{}_system_swap_kilobyte'.format(server_name)] = entry.swap_kilobyte

        publish_to_elasticsearch(
            "monit",
            "system-stats",
            _doc
            )


def broadcast_to_websocket_channel(server, system):
    response = dict()
    response['channel'] = str(server.id).replace("-", "_")

    response['cpu_user_last'] = system.cpu_user_last
    response['cpu_system_last'] = system.cpu_user_last
    response['cpu_wait_last'] = system.cpu_wait_last

    response['memory_percent_last'] = system.memory_percent_last
    response['memory_kilobyte_last'] = system.memory_kilobyte_last

    response['load_avg1_last'] = system.load_avg01_last
    response['load_avg5_last'] = system.load_avg05_last
    response['load_avg15_last'] = system.load_avg15_last

    # formatted
    response['cpu_user_last_progress_bar'] = percent_to_bar(system.cpu_user_last)
    response['cpu_wait_last_progress_bar'] = percent_to_bar(system.cpu_wait_last)
    response['cpu_system_last_progress_bar'] = percent_to_bar(system.cpu_system_last)

    response['memory_last_progress_bar'] = percent_to_bar(system.memory_percent_last)
    response['memory_last_kb_formatted'] = kb_formatting(system.memory_kilobyte_last)

    response['uptime'] = time_str(server.uptime)
    response_str = json.dumps(response)
    to_queue(response_str)
