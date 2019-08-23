========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/dogstatsd-collector/badge/?style=flat
    :target: https://readthedocs.org/projects/dogstatsd-collector
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/roverdotcom/dogstatsd-collector.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/roverdotcom/dogstatsd-collector

.. |codecov| image:: https://codecov.io/github/roverdotcom/dogstatsd-collector/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/roverdotcom/dogstatsd-collector

.. |version| image:: https://img.shields.io/pypi/v/dogstatsd-collector.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/dogstatsd-collector

.. |commits-since| image:: https://img.shields.io/github/commits-since/roverdotcom/dogstatsd-collector/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/roverdotcom/dogstatsd-collector/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/dogstatsd-collector.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/dogstatsd-collector

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/dogstatsd-collector.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/dogstatsd-collector


.. end-badges

``dogstatsd-collector`` is a library to make it easy to collect DataDog-style
StatsD `counters <https://docs.datadoghq.com/developers/dogstatsd/data_types/#counters>`_
and `histograms <https://docs.datadoghq.com/developers/dogstatsd/data_types/#histograms>`_
with tags and control when they are flushed. It
gives you a drop-in wrapper for the `DogStatsD
<https://docs.datadoghq.com/developers/dogstatsd/>`_ library for counters and
histograms and allows you to defer flushing the metrics until you choose to. This
capability enables you to collect StatsD metrics at arbitrary granularity, for
example on a per-web request or per-job basis (instead of the per-flush
interval basis).

Counters and histograms are tracked separately for each metric series (unique
set of tag key-value pairs) and a single metric is emitted for each series when
the collector is flushed. You don't have to think about tracking your metric
series separately; you just use the ``DogstatsdCollector`` object as you would the
normal ``DogStatsD`` object, and flush when you're ready; the library will take
care of emitting all the series for you.

* Free software: BSD 3-Clause License

Installation
============

::

    pip install dogstatsd-collector

Example Usage
=============

Imagine you want to track a distribution of the number of queries issued by
requests to your webapp, and tag them by which database is queried and which
verb is used. You collect the following metrics as you issue your queries:

.. code-block:: python

    collector = DogstatsdCollector(dogstatsd)
    ...
    collector.histogram('query', tags=['database:master','verb:insert'])
    collector.histogram('query', tags=['database:master','verb:update'])
    collector.histogram('query', tags=['database:master','verb:update'])
    collector.histogram('query', tags=['database:replica','verb:select'])
    collector.histogram('query', tags=['database:replica','verb:select'])

Then, at the end of your web request, when you flush the collector, the
following metrics will be pushed to ``DogStatsD`` (`shown in DogStatsD datagram
format
<https://docs.datadoghq.com/developers/dogstatsd/datagram_shell/#datagram-format>`_):

.. code-block:: python

    collector.flush()
    # query:1|h|#database:master,verb:insert
    # query:2|h|#database:master,verb:update
    # query:2|h|#database:replica,verb:select

Base Tags
---------

The collector object also supports specifying a set of base tags, which will be
included on every metric that gets emitted.

.. code-block:: python

    base_tags = ['mytag:myvalue']
    collector = DogstatsdCollector(dogstatsd, base_tags=base_tags)
    collector.histogram('query', tags=['database:master','verb:insert'])
    collector.histogram('query', tags=['database:master','verb:update'])
    collector.flush()
    # query:1|h|#database:master,verb:insert,mytag:myvalue
    # query:1|h|#database:master,verb:update,mytag:myvalue

Motivation
==========

The StatsD model is to run an agent on each server/container in your
infrastructure and periodically flush aggregations at a regular interval to a
centralized location. This model scales very well because the volume of metrics
sent to the centralized location grows very slowly even as you scale
your application; each StatsD agent calculates aggregations to flush to the
backend instead of every datapoint, so the storage volume is quite low even for
a large application with lots of volume.

A drawback to this model is that you don't have much control of the granularity
that your metrics represent. When your aggregations reach the centralized
location (DataDog in this case), you only know the counts or distributions
within the flush interval. You can't represent any other `execution
granularity` beyond "across X seconds" (where X is the flush interval). This
limitation precludes you from easily representings metrics on a "per-request"
basis, for example.

The purpose of this library is to make it simple to control when your StatsD
metrics are emitted so that you can defer emission of the metrics until a point
you determine. This allows you to represent a finer granularity than "across X
seconds" such as "across a web request" or "across a cron job." It also
preserves metric tags by emitting each series independently when the collector
is flushed, which ensures you don't lose any of the benefit of tagging
your metrics (such as aggregating/slicing in DataDog).

Patterns
========

The ``DogstatsdCollector`` object is a singleton that provides a similar
interface as the ``DogStatsD`` `increment
<https://datadogpy.readthedocs.io/en/latest/#datadog.dogstatsd.base.DogStatsd.increment>`_
and `histogram
<https://datadogpy.readthedocs.io/en/latest/#datadog.dogstatsd.base.DogStatsd.histogram>`_
methods. As you invoke these methods, you collect counters and histograms for
each series (determined by any tags you include). After calling ``flush()``,
each series is separately emitted as a StatsD metric.

Simple Request Metrics
----------------------

You can collect various metrics over a request and emit them at the end of the
request to get per-request granularity.

In Django:

.. code-block:: python

    from datadog.dogstatsd.base import DogStatsd
    from dogstatsd_collector import DogstatsdCollector
    
    # Middleware
    class MetricsMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response
            self.dogstatsd = DogStatsd()
    
        def __call__(self, request):
            request.metrics = DogstatsdCollector(self.dogstatsd)
            response = self.get_response(request)
            request.metrics.flush()
    
            return response
    
    # Inside a view
    def my_view(request):
        # Do some stuff...
        request.metrics.increment('my.count')
        request.metrics.histogram('my.time', 0.5)
        return HttpResponse('ok')

In Flask:

.. code-block:: python

    from datadog.dogstatsd.base import DogStatsd
    from dogstatsd_collector import DogstatsdCollector
    
    from flask import Flask
    from flask import request
    
    app = Flask(__name__)
    dogstatsd = DogStatsd()
    
    @app.before_request
    def init_metrics():
        request.metrics = DogstatsdCollector(dogstatsd)
    
    @app.after_request
    def flush_metrics():
        request.metrics.flush()
    
    @app.route('/')
    def my_view():
        # Do some stuff...
        request.metrics.increment('my.count')
        request.metrics.histogram('my.time', 0.5)
        return 'ok'


Celery Task Metrics
-------------------

Same as above, but over a Celery task.

.. code-block:: python

    from datadog.dogstatsd.base import DogStatsd
    from dogstatsd_collector import DogstatsdCollector
    
    from celery import Celery
    from celery import current_task
    from celery.signals import task_prerun
    from celery.signals import task_postrun
    
    app = Celery('tasks', broker='pyamqp://guest@localhost//')
    
    dogstatsd = DogStatsd()
    
    @task_prerun.connect
    def init_metrics(task_id, task, *args, **kwargs):
        task.request.metrics = DogstatsdCollector(dogstatsd)
    
    @task_postrun.connect
    def flush_metrics(task_id, task, *args, **kwargs):
        task.request.metrics.flush()
    
    @app.task
    def my_task():
        # Do some stuff...
        current_task.request.metrics.increment('my.count')
        current_task.request.metrics.histogram('my.time', 0.5)
    
Metrics Within a Function
-------------------------

Emit a set of metrics for a particular function you execute.

.. code-block:: python

    from datadog.dogstatsd.base import DogStatsd
    from dogstatsd_collector import DogstatsdCollector
    
    dogstatsd = DogStatsd()
    
    def do_stuff(metrics):
        # Do some stuff...
        metrics.increment('my.count')
        metrics.histogram('my.time', 0.5)
    
    metrics = DogstatsdCollector(dogstatsd)
    do_stuff(metrics)
    metrics.flush()

Thread Safety
=============

The ``DogstatsdCollector`` singleton is **not threadsafe.** Do not share a
single ``DogstatsdCollector`` object among multiple threads.

More Documentation
==================

Full documentation can be found on ReadTheDocs:

https://dogstatsd-collector.readthedocs.io/

Development
===========

To run the all tests run::

    tox
