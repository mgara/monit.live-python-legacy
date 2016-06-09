# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import logging

from datetime import datetime
from datetime import timedelta
from optparse import make_option
from pytz import timezone
from djangomonitcollector.datacollector.models.aggregation_periods import AggregationPeriod

from djangomonitcollector.datacollector.models import\
    Process,\
    Net,\
    System,\
    FileSystem

from djangomonitcollector.datacollector.models import\
    MemoryCPUProcessAggregatedStats,\
    FsAndDiskAggregatedUsageStats,\
    MemoryCPUAggregatedSystemStats,\
    NetAggregatedStats


from djangomonitcollector.datacollector.models import\
    FsAndDiskUsageStats,\
    MemoryCPUProcessStats,\
    MemoryCPUSystemStats,\
    NetStats

FILENAME = '/var/log/kairos/monit_collector_data_aggregator.log'
FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'


'''
granularity = models.IntegerField(choices=GRANULARITY)
period = models.IntegerField(choices=PERIOD)
number_of_period = models.IntegerField()
'''


class Command(BaseCommand):
    help = 'This program will aggregate data, to be used in a cron job'
    option_list = BaseCommand.option_list + (
        make_option('--log', dest='log', default='INFO'),
        make_option("--verbose", action="store_true", dest="verbose"),
    )

    # create logger with 'spam_application'
    logger = logging.getLogger('monit_collector_data_aggregator')

    def handle(self, *args, **options):
        log_level = eval('logging.' + options['log'].upper())

        self.logger.setLevel(log_level)
        lh = logging.FileHandler(FILENAME)
        formatter = logging.Formatter(FORMAT)

        if options['verbose']:
            lh = logging.StreamHandler()
        lh.setLevel(log_level)
        lh.setFormatter(formatter)
        self.logger.addHandler(lh)

        utc_tz = timezone("UTC")

        all_aggregations = AggregationPeriod.objects.all()

        sorted_aggregation = []
        for aggregation_rule in all_aggregations:
            if (aggregation_rule.period == 2):
                aggregation_rule.hours = 24*aggregation_rule.number_of_period
            elif (aggregation_rule.period == 3):
                aggregation_rule.hours = 31*24 * \
                    aggregation_rule.number_of_period
            elif (aggregation_rule.period == 4):
                aggregation_rule.hours = 365*24 * \
                    aggregation_rule.number_of_period
            else:
                aggregation_rule.hours = aggregation_rule.number_of_period

            aggregation_tuple = (
                aggregation_rule.hours, aggregation_rule.granularity, aggregation_rule.id)
            sorted_aggregation.append(aggregation_tuple)
        sorted_aggregation = sorted(
            sorted_aggregation,
            key=lambda aggregation: aggregation[0]
        )

        oldnow = datetime.utcnow().replace(tzinfo=utc_tz)
        now = oldnow.replace(second=0, microsecond=0)

        self.logger.info(
            "Started Aggregation Job At [{}] -> [{}]".format(oldnow, now))
        self.logger.debug(
            "Configured [{}] Aggregation Periods:".format(len(sorted_aggregation)))

        for aggregation_rule in sorted_aggregation:
            self.logger.debug("[{}] hours -> Rolling Period : [{}] ".format(
                aggregation_rule[0],
                timedelta(seconds=aggregation_rule[1])
            )
            )

        '''
        Process,\
        Net,\
        System,\
        FileSystem

        FsAndDiskUsageStats,\
        MemoryCPUProcessStats,\
        MemoryCPUSystemStats,\
        NetStats

        MemoryCPUProcessAggregatedStats,\
        FsAndDiskAggregatedUsageStats,\
        MemoryCPUAggregatedSystemStats,\
        NetAggregatedStats
        '''

        all_fs = FileSystem.objects.all()
        all_nets = Net.objects.all()
        all_process = Process.objects.all()
        all_system = System.objects.all()

        for aggregation_rule in sorted_aggregation:
            td = timedelta(hours=aggregation_rule[0])
            date_limit = now - td
            rolling_period = timedelta(seconds=aggregation_rule[1])
            hours_limit = aggregation_rule[0]
            rule_id = aggregation_rule[2]

            self.logger.info("Applying Aggregation for first threshold")
            self.logger.debug("Applying rolling period of [{}] (h:mm:ss) on [{}] hours old data -> Prior to [{}]".format(
                rolling_period,
                hours_limit,
                date_limit)
            )

            _blocks_percent = []
            _blocks_usage = []
            _inode_percent = []
            _inode_usage = []

            for fs in all_fs:
                self.logger.info(
                    "Applying Aggregation for Filesystem [{}]".format(fs.name))
                fs_stat_objects = FsAndDiskUsageStats.objects.filter(
                    date_last__lt=date_limit,
                    fs_id=fs
                )

                data_len = len(fs_stat_objects)
                if data_len == 0:
                    continue
                self.logger.debug("Found [{}] match.".format(data_len))
                first_item = fs_stat_objects[0].date_last
                _start = first_item
                _end = (_start + rolling_period)

                j = 0
                i = 0
                init = None
                for x in range(0, data_len):
                    i += 1
                    _blocks_percent.append(fs_stat_objects[x].blocks_percent)
                    _blocks_usage.append(fs_stat_objects[x].blocks_usage)
                    _inode_percent.append(fs_stat_objects[x].inode_percent)
                    _inode_usage.append(fs_stat_objects[x].inode_usage)

                    if fs_stat_objects[x].date_last >= _end:
                        j += 1
                        i = 0
                        _start = _end
                        _end = _start + rolling_period
                        date_last = _start
                        blocks_percent = median(_blocks_percent)
                        blocks_usage = median(_blocks_usage)
                        inode_percent = median(_inode_percent)
                        inode_usage = median(_inode_usage)

                        if not init:
                            init = inode_usage
                        else:
                            if inode_usage > init:
                                init = inode_usage
                                print inode_usage

                        #  FsAndDiskAggregatedUsageStats.create()
                    # if j == 9:
                    #    return

                fs_stat_objects = FsAndDiskAggregatedUsageStats.objects.filter(
                    date_last__lt=date_limit,
                    fs_id=fs,
                    rule_id=rule_id
                )


def median(array):
    """Calculate median of the given list.
    """
    # TODO: use statistics.median in Python 3
    array = sorted(array)
    half, odd = divmod(len(array), 2)
    if odd:
        return array[half]
    return (array[half - 1] + array[half]) / 2.0
