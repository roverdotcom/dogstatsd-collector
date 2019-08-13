from collections import defaultdict


class DogstatsdCollector(object):
    """
    A singleton for collecting DogStatsD-style metrics with tags. Collects
    metrics in-memory and then emits them when flush() is called. Each series
    (metric and all combination of tag key-value pairs) is emitted separately.

    :type dogstatsd: datadog.dogstatsd.base.DogStatsD
    :param dogstatsd: The DogStatsD object to use for emitting metrics.

    :type base_tags: list
    :param base_tags: A list of tags to be included on every metric emitted from
                      the collector. Should be of the form ['tag:value', ...]
    """

    #: The DogStatsD metrics supported by the collector.
    SUPPORTED_DOGSTATSD_METRICS = ['histogram', 'increment']

    def __init__(self, dogstatsd, base_tags=None):
        self.dogstatsd = dogstatsd
        for metric in self.SUPPORTED_DOGSTATSD_METRICS:
            setattr(
                self,
                '_{}s'.format(metric),
                defaultdict(lambda: defaultdict(float))
            )
        if base_tags is None:
            base_tags = []
        self.base_tags = base_tags

    def increment(self, metric, value=1, tags=None):
        """
        Track a DogStatsD counter metric.
        """
        self._record_metric('increment', metric, value, tags)

    def histogram(self, metric, value, tags=None):
        """
        Track a DogStatsD histogram metric.
        """
        self._record_metric('histogram', metric, value, tags)

    def flush(self):
        """
        Flush all metrics, emitting each metric once per series (combination of
        tag key-value pairs).
        """
        for metric_type in self.SUPPORTED_DOGSTATSD_METRICS:
            self._flush_metric(metric_type)

    def _flush_metric(self, metric_type):
        container = self._get_metric_container(metric_type)
        dogstatsd_method = getattr(self.dogstatsd, metric_type)
        for metric, series in container.items():
            for series, value in series.items():
                series = list(series)
                series.extend(self.base_tags)
                dogstatsd_method(metric, value, tags=sorted(series))

    def _record_metric(self, metric_type, metric, value, tags=None):
        if tags is None:
            tags = []
        key = frozenset(tags)
        self._get_metric_container(metric_type)[metric][key] += value

    def _get_metric_container(self, metric_type):
        attr = '_{}s'.format(metric_type)
        return getattr(self, attr)
