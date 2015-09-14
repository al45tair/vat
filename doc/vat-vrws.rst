vat.vrws package
================

.. py:module:: vat.vrws

Functions
---------

.. py:function:: get_rates

   Obtain VAT rates for the specified country.  Returns a :py:class:`Rates` on
   success, or in case of error raises an exception.

   .. :param str country:

   The two character EU VAT country code.

   .. :param datetime.date date:

   If set, only dates in force on the specified date will be returned (optional).

   .. :param bool fetch_reduced:

   If `True`, the default, include reduced rates (optional).

   .. :param bool fetch_category:

   If `True`, the default, include category rates (optional).

   .. :param bool fetch_region:

   If `True`, the default, include regional rates (optional).

   .. note::

      You should probably use the :py:class:`vat.RateCache` object rather than
      this function.  Not only does this avoid hitting the EU web service more
      often than necessary, but :py:class:`vat.RateCache` keeps back-up
      information on reduced rates that were not (as of 1st September 2015)
      available through the web service.

.. py:function:: get_changes

   Retrieve any VAT rates that changed during the specified period.  Returns a
   :py:class:`Rates` on success, or in case of error raises an exception.

   .. :param datetime.date from_date:

   Returns VAT rates that changed after this date.

   .. :param datetime.date to_date:

   Returns only VAT rates that changed before this date (optional).

   .. :param country:

   A two character EU VAT country code (optional).  If specified, restricts
   results to that country only.

Classes
-------

.. py:class:: VRWSException

   The base class of all exceptions raised by this module.

.. py:class:: VRWSSOAPException

   Represents a SOAP fault encountered when trying to talk to VIES.

   .. py:attribute:: code

   The SOAP fault code.

   .. py:attribute:: string

   A description of the fault.

   .. py:attribute:: actor

   Used to indicate the source of the fault.

   .. py:attribute:: detail

   Provides additional information about the fault.

.. autoclass:: VRWSHTTPException

   Represents an HTTP error encountered when trying to talk to VIES.

   .. py:attribute:: code

   The HTTP error code (e.g. 403).

   .. py:attribute:: message

   The message sent by the far end; usually this is a textual description of
   the error code, but it can be more specific than that.

.. py:class:: VRWSErrorException

   Represents an error raised by the VRWS system.

   .. py:attribute:: code

   A numeric code identifying the error.

   .. py:attribute:: reason

   A string describing the error.

.. py:class:: Rates

   A collection of VAT rate information.

   .. py:attribute:: types

   A dictionary keyed on rate type.  Each entry is a list of applicable
   :py:class:`Rate` objects.  The module includes constants for the following
   rate types:

     ===================  =============
     Constant             Meaning
     ===================  =============
     :py:data:`STANDARD`  Standard rate
     :py:data:`REDUCED`   Reduced rate
     ===================  =============

   .. note::

      In general there can be more than one rate per type.  You may need to
      inspect the attributes of the :py:class:`Rate` object to determine
      which rate is applicable.

   .. py:attribute:: categories

   A dictionary keyed on rate category.  Each entry is a list of applicable
   :py:class:`Rate` objects.  The module includes constants for the following
   categories:

     =======================  ==========================
     Constant                 Meaning
     =======================  ==========================
     :py:data:`BROADCASTING`  Broadcasting
     :py:data:`TELECOMS`      Telecommunication Services
     :py:data:`ESERVICES`     E-Services
     =======================  ==========================

   .. note::

      Again, there can be multiple rates in each category, and you may need to
      use :py:attr:`Rate.detail` to distinguish them.

   .. py:attribute:: regions

   A dictionary keyed on region.  Each entry is a :py:class:`Rates` object.

.. py:class:: Rate

   Represents an individual VAT rate.

   .. py:attribute:: rate

   A :py:class:`decimal.Decimal` holding the percentage rate.

   .. py:attribute:: application_date

   The date from which this rate applies.

   .. py:attribute:: detail

   Any notes that apply to this rate.  For instance, if this rate applies to a
   specific type of product, or has special requirements associated with it.

   .. note::

      There is no standard format for the :py:attr:`Rate.detail` attribute and
      it may be written in the language of the associated member state.

Constants
---------

.. py:data:: STANDARD
             REDUCED

   VAT rate types.  There may be additional rate types in future.

.. py:data:: BROADCASTING
             TELECOMS
             ESERVICES

   VAT categories.  There may be additional categories in future.
