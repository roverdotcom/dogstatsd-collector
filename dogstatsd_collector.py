from collections import defaultdict


class DogstatsdCollector(object):
    SUPPORTED_DOGSTATSD_METRICS = ['histogram', 'increment']

    def __init__(self, dogstatsd):
        self.dogstatsd = dogstatsd
        for metric in self.SUPPORTED_DOGSTATSD_METRICS:
            setattr(self, '_{}s'.format(metric), {})

    def increment(self, metric, value=1, tags=None):
        self._record_metric('increment', metric, value, tags)

    def histogram(self, metric, value, tags=None):
        self._record_metric('histogram', metric, value, tags)

    def flush(self):
        for metric_type in self.SUPPORTED_DOGSTATSD_METRICS:
            self._flush_metric(metric_type)

    def _flush_metric(self, metric_type):
        container = self._get_metric_container(metric_type)
        for metric, series in container.items():
            for series, value in series.items():
                getattr(
                    self.dogstatsd,
                    metric_type
                )(metric, value, tags=sorted(list(series)))

    def _record_metric(self, metric_type, metric, value, tags=None):
        if tags is None:
            tags = []
        key = frozenset(tags)
        metric_dict = self._get_metric_container(
            metric_type
        ).setdefault(
            metric,
            defaultdict(int)
        )
        metric_dict[key] += value

    def _get_metric_container(self, metric_type):
        attr = '_{}s'.format(metric_type)
        return getattr(self, attr)
