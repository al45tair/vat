vat.vies package
================

.. py:module:: vat.vies

Functions
---------

.. py:function:: check_vat

   Check a VAT number using VIES.  Returns a :py:class:`VIESResponse` on
   success, or in case of error raises an exception.

   .. :param str vat_number:

   The complete VAT number, including the two character EU VAT country code.

   .. note::

      You should probably use :py:func:`vat.check_details` rather than this
      function.

.. py:function:: check_vat_approx(vat_number, extra={}, requester=None)

   Check a VAT number using VIES, passing in additional information about the
   entity being checked.  Returns a :py:class:`VIESApproxResponse` on success,
   or raises an exception.

   .. :param str vat_number:

   The complete VAT number, including the two character EU VAT country code.

   .. :param dict extra:

   A dictionary containing additional information to be passed to VIES to
   check.  Available items are:

     ============  =================================
     Key           Value
     ============  =================================
     name          The name of the trader.
     company-type  The company type, if applicable.
     street        The street address of the trader.
     postcode      The postal code of the trader.
     city          The city of the trader.
     ============  =================================

   Note that company types are language and country specific.

   If the member state does fuzzy matching, passing these details will allow
   their system to try to match them.

   .. :param str requester:

   The requester’s VAT number (optional).

   .. note::

      You should probably use :py:func:`vat.check_details` rather than this
      function.

Classes
-------

.. py:class:: VIESException

   The base class of all exceptions raised by this module.

.. py:class:: VIESSOAPException

   Represents a SOAP fault encountered when trying to talk to VIES.

   .. py:attribute:: code

   The SOAP fault code.

   .. py:attribute:: string

   A description of the fault.

   .. py:attribute:: actor

   Used to indicate the source of the fault.

   .. py:attribute:: detail

   Provides additional information about the fault.

.. autoclass:: VIESHTTPException

   Represents an HTTP error encountered when trying to talk to VIES.

   .. py:attribute:: code

   The HTTP error code (e.g. 403).

   .. py:attribute:: message

   The message sent by the far end; usually this is a textual description of
   the error code, but it can be more specific than that.

.. py:class:: VIESResponseBase

   The base class of all VIES response classes.

   .. py:attribute:: country

   The EU VAT country code.

   .. py:attribute:: vat_number

   The VAT number *excluding* the country code.

   .. py:attribute:: request_date

   The date on which the request was submitted to VIES.

   .. py:attribute:: valid

   True if the VAT number is valid, False otherwise.

.. py:class:: VIESResponse
   
   Represents the response from VIES to a basic request.

   .. py:attribute:: name

   The trader’s name, if provided (not all member states do).

   .. py:attribute:: address

   The trader’s address, if provided (not all member states do).

.. py:class:: VIESApproxResponse

   Represents the response from VIES to a request to verify a complete set of
   details, including the trader’s name and address.

   Note that the details contained in the response are dependent on the member
   state in question.  Some member states try to fuzzy-match the information
   you pass in; other member states supply the trader information themselves;
   and there is at least one member state (Germany) that at time of writing
   does neither and (worse) returns the information you gave it.

   .. py:attribute:: trader_info

   A dictionary containing (any of) the following elements:

     ============  =================================
     Key           Value
     ============  =================================
     name          The name of the trader.
     company-type  The company type, if applicable.
     address       The full address of the trader.
     street        The street address of the trader.
     postcode      The postal code of the trader.
     city          The city of the trader.
     ============  =================================

   Note that the address may be specified using either the "address" field or
   the individual "street", "postcode" and "city" fields.

   .. py:attribute:: trader_match_info

   A dictionary containing the same keys as above, but for each item the value
   is one of

     ==============================  =========================================
     Value                           Meaning
     ==============================  =========================================
     :py:data:`MATCH_VALID`          The details matched those supplied.
     :py:data:`MATCH_INVALID`        The details did not match those supplied.
     :py:data:`MATCH_NOT_PROCESSED`  The details were not processed.
     ==============================  =========================================

   .. py:attribute:: request_id

   A unique request ID generated by the VIES system.  This can be stored and
   later used as proof that VIES was checked for these details.

Constants
---------

.. py:data:: MATCH_VALID
             MATCH_INVALID
             MATCH_NOT_PROCESSED

   Matching results.


