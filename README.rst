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

.. |commits-since| image:: https://img.shields.io/github/commits-since/roverdotcom/dogstatsd-collector/v0.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/roverdotcom/dogstatsd-collector/compare/v0.0.1...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/dogstatsd-collector.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/dogstatsd-collector

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/dogstatsd-collector.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/dogstatsd-collector


.. end-badges

`dogstatsd-collector` is a library to make it easy to collect DataDog-style
StatsD counters and histograms with tags and control when they are flushed. It
gives you a drop-in wrapper for the DogStatsD library for counters and
histograms and allows you to defer flushing the metrics until you choose to. This
capability enables you to collect StatsD metrics at arbitrary granularity, for
example on a per-web request or per-job basis.

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

::

    collector = DogstatsdCollector(dogstatsd)
    ...
    collector.histogram('query', tags=['database:master','verb:insert'])
    collector.histogram('query', tags=['database:master','verb:update'])
    collector.histogram('query', tags=['database:master','verb:update'])
    collector.histogram('query', tags=['database:replica','verb:select'])
    collector.histogram('query', tags=['database:replica','verb:select'])

Then, at the end of your web request, when you flush the collector, the
following metrics will be pushed to DogStatsD:

::

    collector.flush()
    # 'query,1,database:master|verb:insert'
    # 'query,2,database:master|verb:update'
    # 'query,2,database:replica|verb:select'

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

The ``DogstatsdCollector`` object is a singleton that provides an identical
interface as the DogStatsD ``increment`` and ``histogram`` methods. As you
invoke these methods, you collect counters and histograms for each series
(determined by any tags you include). After calling ``flush()``, each series is
separately emitted as a StatsD metric.

Simple Request Metrics
----------------------

You can collect various metrics over a request and emit them at the end of the
request to get per-request granularity.

In Django:

TODO

In Flask:

TODO

Celery Task Metrics
-------------------

Same as above, but over a Celery task.

TODO

Metrics Within a Function
-------------------------

Emit a set of metrics for a particular function you execute.

TODO

Thread Safety
=============

The DogstatsdCollector singleton is **not threadsafe.** TODO

More Documentation
==================

Full documentation can be found on ReadTheDocs:

https://dogstatsd-collector.readthedocs.io/

Development
===========

To run the all tests run::

    tox
