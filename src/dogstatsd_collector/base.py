from collections import defaultdict


class DogstatsdCollector(object):
    """
    A singleton for collecting DogStatsD-style metrics with tags. Collects
    metrics in-memory and then emits them when flush() is called. Each series
    (metric and all combination of tag key-value pairs) is emitted separately.

    :type dogstatsd: datadog.DogStatsD
    :param dogstatsd: The DogStatsD object to use for emitting metrics.
    """

    #: The DogStatsD metrics supported by the collector.
    SUPPORTED_DOGSTATSD_METRICS = ['histogram', 'increment']

    def __init__(self, dogstatsd):
        self.dogstatsd = dogstatsd
        for metric in self.SUPPORTED_DOGSTATSD_METRICS:
            setattr(
                self,
                '_{}s'.format(metric),
                defaultdict(lambda: defaultdict(float))
            )

    def increment(self, metric, value=1, tags=None):
        """
        Track a DogStatsD counter metric. See <TODO>
        """
        self._record_metric('increment', metric, value, tags)

    def histogram(self, metric, value, tags=None):
        """
        Track a DogStatsD histogram metric. See <TODO>
        """
        self._record_metric('histogram', metric, value, tags)

    def flush(self):
        """
        Flush all metrics, emitting each metric once per series (combination of
        tag key-valuepairs).
        """
        for metric_type in self.SUPPORTED_DOGSTATSD_METRICS:
            self._flush_metric(metric_type)

    def _flush_metric(self, metric_type):
        container = self._get_metric_container(metric_type)
        dogstatsd_method = getattr(self.dogstatsd, metric_type)
        for metric, series in container.items():
            for series, value in series.items():
                dogstatsd_method(metric, value, tags=sorted(list(series)))

    def _record_metric(self, metric_type, metric, value, tags=None):
        if tags is None:
            tags = []
        key = frozenset(tags)
        self._get_metric_container(metric_type)[metric][key] += value

    def _get_metric_container(self, metric_type):
        attr = '_{}s'.format(metric_type)
        return getattr(self, attr)
