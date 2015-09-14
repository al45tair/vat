vat package
===========

.. py:module:: vat

Functions
---------

.. autofunction:: check_details

Classes
-------

.. autoclass:: MemberState()
   :members:

   .. py:attribute:: code

   The two-character EU VAT code for the member state.
   
   .. py:attribute:: iso

   The two-character ISO 3166-2 code for the member state.
   
   .. py:attribute:: name

   The English language name of the member state.
   
   .. py:attribute:: standard_rate

   The standard rate of VAT applicable (e.g. 20% = 0.2).
   
   .. note::

      Deprecated in favour of using a :py:class:`vat.RateCache` object.
      (This attribute is now a property that uses an internal
      :py:class:`vat.RateCache` to look up the value required.)

   .. py:attribute:: reduced_rates

   A tuple of reduced rates of VAT that might apply, or `None` if none.
   
   .. note::

      Deprecated in favour of using a :py:class:`vat.RateCache` object.
      (This attribute is now a property that uses an internal
      :py:class:`vat.RateCache` to look up the value required.)

   .. py:attribute:: super_reduced_rate

   The super-reduced rate, if applicable, or `None` if none exists.
   
   .. note::

      Deprecated in favour of using a :py:class:`vat.RateCache` object.
      (This attribute is now a property that uses an internal
      :py:class:`vat.RateCache` to look up the value required.)

   .. py:attribute:: parking_rate

   The “parking” rate, if applicable, or `None` if none exists.
   
   .. note::

      Deprecated in favour of using a :py:class:`vat.RateCache` object.
      (This attribute is now a property that uses an internal
      :py:class:`vat.RateCache` to look up the value required.)

   .. py:attribute:: currency

   The ISO currency code for the currency used in this member state.
   
   .. py:attribute:: special_scheme_threshold

   The threshold for the special scheme for acquisitions (a
   :py:class:`Threshold` object).
   
   .. py:attribute:: distance_selling_threshold

   The distance selling threshold (a :py:class:`Threshold` object).
   
   .. py:attribute:: small_enterprise_threshold

   The threshold below which small businesses are not required to register for
   VAT (a :py:class:`Threshold` object).
   
   .. py:attribute:: number_format

   A :py:class:`re.RegexObject` matching the VAT number format for this member
   state.

.. autoclass:: Threshold
   :members:

   .. py:attribute:: currency

   The ISO currency code for the currency of this threshold.

   .. py:attribute:: amount

   The amount, as a :py:class:`decimal.Decimal`, of the threshold.

.. py:class:: VIESResponseBase
              VIESResponse
              VIESApproxResponse              
   
   Imported from :py:mod:`vat.vies` for convenient access.

   See :py:class:`vat.vies.VIESResponseBase`,
   :py:class:`vat.vies.VIESResponse` and :py:class:`vat.vies.VIESApproxResponse`.

.. py:class:: VIESException
              VIESSOAPException
              VIESHTTPException

   Imported from :py:mod:`vat.vies` for convenient access.

   See :py:class:`vat.vies.VIESException`,
   :py:class:`vat.vies.VIESSOAPException` and
   :py:class:`vat.vies.VIESHTTPException`.

.. autoclass:: RateCache()

   .. py:method:: regions(member_state)

      Retrieve a list of regions for the given member state, if any.
      Regions may have their own VAT rates.

   .. py:method:: standard_rates(member_state, region=None)

      Retrieve the set of standard rates for the given member state
      and (optional) region.  Each rate is represented by a
      :py:class:`vat.Rate` object.

      .. note::

         This method returns a *list* of rates, and you need to use the date
         and detail information to find the appropriate one.  There may in
         general be multiple rates with different application dates, *and*
         there may be rates with detail specifications in the list.

   .. py:method:: standard_rate(member_state, region=None)

      Return today's standard rate for the given member state.  Works by
      picking the most recent rate before today that does not have a detail
      specification.

   .. py:method:: reduced_rates(member_state, region=None)

      Retrieve the set of reduced rates for the given member state,
      optionally for the specified region.

      .. note::

         As of 1st September 2015, most member states are not providing
         reduced information via the web service.  If we find that a member
         state has not provided the necessary information, we fall back to a
         built-in table.

         A consequence of this is that the detail information for the rates
         in the fall-back data is very uniform.  You should make no
         assumptions about the detail information, as the data returned by the
         web service is set by individual member states.

   .. py:method:: reduced_rate(member_state, region=None)

      Return today's reduced rate for the given member state and (optional)
      region.

      .. warning::

         Take care!  This will return, in general, one possible reduced rate.
         It is *not* necessarily the correct reduced rate for your purpose.
         It’s probably safer to use the :py:meth:`reduced_rates` method
         instead, and find the proper rate yourself.

   .. py:method:: category_rates(member_state, category, region=None)

      Retrieve the set of rates for the given member state, category and
      (optional) region.

   .. py:method:: category_rate(member_state, category, region=None)

      Return today's rate for the given member state, category and (optional)
      region.

   .. py:method:: categories(member_state, region=None)

      Returns a list of categories defined for the specified member state and
      (optional) region.

.. autoclass:: Rate
   :members:

   .. py:attribute:: rate

      The VAT rate as a :py:class:`decimal.Decimal`.

   .. py:attribute:: application_date

      A :py:class:`datetime.date` as of which this rate applies.

   .. py:attribute:: detail

      If set, provides additional textual information about this rate.  This
      field is entirely free-format and its contents may not be consistent
      from member state to member state.  Indeed, they are very likely not in
      the same language!

.. py:class:: VRWSException
              VRWSErrorException
              VRWSSOAPException
              VRWSHTTPException

   Imported from :py:mod:`vat.vrws` for convenient access.

   See :py:class:`vat.vrws.VRWSException`,
   :py:class:`vat.vrws.VRWSErrorException`,
   :py:class:`vat.vrws.VRWSSOAPException` and
   :py:class:`vat.vrws.VRWSHTTPException`.


Data
----

.. py:data:: member_states

   A list of all the member states of the European Union, as
   :py:class:`MemberState` objects.

.. py:data:: BROADCASTING
             TELECOMS
             ESERVICES

   Category constants.  There may be other categories besides these ones, but
   these are known to be defined at present.
