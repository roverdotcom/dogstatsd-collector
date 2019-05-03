from unittest import TestCase

from mock import MagicMock
from mock import call

from dogstatsd_collector import DogstatsdCollector


class DogstatsdCollectorTests(TestCase):
    def setUp(self):
        super(DogstatsdCollectorTests, self).setUp()
        self.dogstatsd = MagicMock()
        self.collector = DogstatsdCollector(self.dogstatsd)

    def test_ctor_initializes_histograms(self):
        self.assertTrue(hasattr(self.collector, '_histograms'))
        self.assertEqual(self.collector._histograms, {})

    def test_ctor_initializes_increments(self):
        self.assertTrue(hasattr(self.collector, '_increments'))
        self.assertEqual(self.collector._increments, {})

    def test_single_increment_without_tags(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=[])
        ], any_order=True)

    def test_single_increment_with_tags(self):
        metric_name = 'my.metric'
        tags = ['tag1:value1']
        self.collector.increment(metric_name, tags=tags)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=tags)
        ], any_order=True)

    def test_increment_supports_specified_value(self):
        metric_name = 'my.metric'
        tags = ['tag1:value1']
        self.collector.increment(metric_name, 5, tags=tags)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 5, tags=tags)
        ], any_order=True)

    def test_multiple_increment_with_tags(self):
        metric_name = 'my.metric'
        tags = ['tag1:value1']
        self.collector.increment(metric_name, tags=tags)
        self.collector.increment(metric_name, tags=tags)
        self.collector.increment(metric_name, tags=tags)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 3, tags=['tag1:value1'])
        ], any_order=True)

    def test_increment_with_multiple_values_for_one_tag(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 1, tags=['tag1:value2']),
            call(metric_name, 1, tags=['tag1:value3'])
        ], any_order=True)

    def test_multiple_increment_with_multiple_values_for_one_tag(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 2, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value2']),
            call(metric_name, 2, tags=['tag1:value3'])
        ], any_order=True)

    def test_single_increment_with_multiple_tags(self):
        metric_name = 'my.metric'
        tags1 = ['tag1:value1']
        tags2 = ['tag2:value1']
        tags3 = ['tag3:value1']
        self.collector.increment(metric_name, tags=tags1)
        self.collector.increment(metric_name, tags=tags2)
        self.collector.increment(metric_name, tags=tags3)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=tags1),
            call(metric_name, 1, tags=tags2),
            call(metric_name, 1, tags=tags3),
        ], any_order=True)

    def test_multiple_increment_with_multiple_tags(self):
        metric_name = 'my.metric'
        tags1 = ['tag1:value1']
        tags2 = ['tag2:value1']
        tags3 = ['tag3:value1']
        self.collector.increment(metric_name, tags=tags1)
        self.collector.increment(metric_name, tags=tags1)
        self.collector.increment(metric_name, tags=tags2)
        self.collector.increment(metric_name, tags=tags2)
        self.collector.increment(metric_name, tags=tags3)
        self.collector.increment(metric_name, tags=tags3)
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 2, tags=tags1),
            call(metric_name, 2, tags=tags2),
            call(metric_name, 2, tags=tags3),
        ], any_order=True)

    def test_single_increment_with_multiple_values_for_multiple_tags(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.increment(metric_name, tags=['tag2:value1'])
        self.collector.increment(metric_name, tags=['tag2:value2'])
        self.collector.increment(metric_name, tags=['tag2:value3'])
        self.collector.increment(metric_name, tags=['tag3:value1'])
        self.collector.increment(metric_name, tags=['tag3:value2'])
        self.collector.increment(metric_name, tags=['tag3:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 1, tags=['tag1:value2']),
            call(metric_name, 1, tags=['tag1:value3']),
            call(metric_name, 1, tags=['tag2:value1']),
            call(metric_name, 1, tags=['tag2:value2']),
            call(metric_name, 1, tags=['tag2:value3']),
            call(metric_name, 1, tags=['tag3:value1']),
            call(metric_name, 1, tags=['tag3:value2']),
            call(metric_name, 1, tags=['tag3:value3']),
        ], any_order=True)

    def test_multiple_increment_with_multiple_values_for_multiple_tags(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value2'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.increment(metric_name, tags=['tag1:value3'])
        self.collector.increment(metric_name, tags=['tag2:value1'])
        self.collector.increment(metric_name, tags=['tag2:value1'])
        self.collector.increment(metric_name, tags=['tag2:value2'])
        self.collector.increment(metric_name, tags=['tag2:value2'])
        self.collector.increment(metric_name, tags=['tag2:value3'])
        self.collector.increment(metric_name, tags=['tag2:value3'])
        self.collector.increment(metric_name, tags=['tag3:value1'])
        self.collector.increment(metric_name, tags=['tag3:value1'])
        self.collector.increment(metric_name, tags=['tag3:value2'])
        self.collector.increment(metric_name, tags=['tag3:value2'])
        self.collector.increment(metric_name, tags=['tag3:value3'])
        self.collector.increment(metric_name, tags=['tag3:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 2, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value2']),
            call(metric_name, 2, tags=['tag1:value3']),
            call(metric_name, 2, tags=['tag2:value1']),
            call(metric_name, 2, tags=['tag2:value2']),
            call(metric_name, 2, tags=['tag2:value3']),
            call(metric_name, 2, tags=['tag3:value1']),
            call(metric_name, 2, tags=['tag3:value2']),
            call(metric_name, 2, tags=['tag3:value3']),
        ], any_order=True)

    def test_increment_differentiates_among_series(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value1', 'tag2:value2']),
            call(metric_name, 3, tags=['tag1:value1', 'tag2:value2', 'tag3:value3']),
        ], any_order=True)

    def test_single_histogram_without_tags(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1)
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=[])
        ], any_order=True)

    def test_single_histogram_with_tags(self):
        metric_name = 'my.metric'
        tags = ['tag1:value1']
        self.collector.histogram(metric_name, 1, tags=tags)
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=tags)
        ], any_order=True)

    def test_multiple_histogram_with_tags(self):
        metric_name = 'my.metric'
        tags = ['tag1:value1']
        self.collector.histogram(metric_name, 1, tags=tags)
        self.collector.histogram(metric_name, 1, tags=tags)
        self.collector.histogram(metric_name, 1, tags=tags)
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 3, tags=['tag1:value1'])
        ], any_order=True)

    def test_histogram_with_multiple_values_for_one_tag(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 1, tags=['tag1:value2']),
            call(metric_name, 1, tags=['tag1:value3'])
        ], any_order=True)

    def test_multiple_histogram_with_multiple_values_for_one_tag(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 2, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value2']),
            call(metric_name, 2, tags=['tag1:value3'])
        ], any_order=True)

    def test_single_histogram_with_multiple_tags(self):
        metric_name = 'my.metric'
        tags1 = ['tag1:value1']
        tags2 = ['tag2:value1']
        tags3 = ['tag3:value1']
        self.collector.histogram(metric_name, 1, tags=tags1)
        self.collector.histogram(metric_name, 1, tags=tags2)
        self.collector.histogram(metric_name, 1, tags=tags3)
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=tags1),
            call(metric_name, 1, tags=tags2),
            call(metric_name, 1, tags=tags3),
        ], any_order=True)

    def test_multiple_histogram_with_multiple_tags(self):
        metric_name = 'my.metric'
        tags1 = ['tag1:value1']
        tags2 = ['tag2:value1']
        tags3 = ['tag3:value1']
        self.collector.histogram(metric_name, 1, tags=tags1)
        self.collector.histogram(metric_name, 1, tags=tags1)
        self.collector.histogram(metric_name, 1, tags=tags2)
        self.collector.histogram(metric_name, 1, tags=tags2)
        self.collector.histogram(metric_name, 1, tags=tags3)
        self.collector.histogram(metric_name, 1, tags=tags3)
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 2, tags=tags1),
            call(metric_name, 2, tags=tags2),
            call(metric_name, 2, tags=tags3),
        ], any_order=True)

    def test_single_histogram_with_multiple_values_for_multiple_tags(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value3'])
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 1, tags=['tag1:value2']),
            call(metric_name, 1, tags=['tag1:value3']),
            call(metric_name, 1, tags=['tag2:value1']),
            call(metric_name, 1, tags=['tag2:value2']),
            call(metric_name, 1, tags=['tag2:value3']),
            call(metric_name, 1, tags=['tag3:value1']),
            call(metric_name, 1, tags=['tag3:value2']),
            call(metric_name, 1, tags=['tag3:value3']),
        ], any_order=True)

    def test_multiple_histogram_with_multiple_values_for_multiple_tags(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag2:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag3:value3'])
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 2, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value2']),
            call(metric_name, 2, tags=['tag1:value3']),
            call(metric_name, 2, tags=['tag2:value1']),
            call(metric_name, 2, tags=['tag2:value2']),
            call(metric_name, 2, tags=['tag2:value3']),
            call(metric_name, 2, tags=['tag3:value1']),
            call(metric_name, 2, tags=['tag3:value2']),
            call(metric_name, 2, tags=['tag3:value3']),
        ], any_order=True)

    def test_histogram_differentiates_among_series(self):
        metric_name = 'my.metric'
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.flush()
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value1', 'tag2:value2']),
            call(metric_name, 3, tags=['tag1:value1', 'tag2:value2', 'tag3:value3']),
        ], any_order=True)

    def test_mix_of_increments_and_histograms(self):
        metric_name = 'my.metric'
        self.collector.increment(metric_name, tags=['tag1:value1'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.increment(metric_name, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.histogram(metric_name, 1, tags=['tag1:value1', 'tag2:value2', 'tag3:value3'])
        self.collector.flush()
        self.dogstatsd.increment.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value1', 'tag2:value2']),
            call(metric_name, 3, tags=['tag1:value1', 'tag2:value2', 'tag3:value3']),
        ], any_order=True)
        self.dogstatsd.histogram.assert_has_calls([
            call(metric_name, 1, tags=['tag1:value1']),
            call(metric_name, 2, tags=['tag1:value1', 'tag2:value2']),
            call(metric_name, 3, tags=['tag1:value1', 'tag2:value2', 'tag3:value3']),
        ], any_order=True)
