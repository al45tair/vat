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
   
   .. py:attribute:: reduced_rates

   A tuple of reduced rates of VAT that might apply, or `None` if none.
   
   .. py:attribute:: super_reduced_rate

   The super-reduced rate, if applicable, or `None` if none exists.
   
   .. py:attribute:: parking_rate

   The “parking” rate, if applicable, or `None` if none exists.
   
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

Data
----

.. py:data:: member_states

   A list of all the member states of the European Union, as
   :py:class:`MemberState` objects.

