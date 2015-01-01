vat.gb package
==============

.. py:module:: vat.gb

The :py:mod:`vat.gb` module contains VAT code specific to the United Kingdom.

EC Sales Lists - vat.gb.ecsl
----------------------------

.. py:module:: vat.gb.ecsl

EC Sales Lists are a requirement where you are making B2B sales to other
member states within the European Union.  See `VAT: how to report your EU
sales`_ for more information.

.. _`VAT: how to report your EU sales`: https://www.gov.uk/vat-how-to-report-your-eu-sales

.. autofunction:: generate

.. py:data:: B2B_GOODS
             B2B_INTERMEDIARY
             B2B_SERVICES

Used to specify the type of sale being reported.

Mini One Stop Shop - vat.gb.moss
--------------------------------

.. py:module:: vat.gb.moss

The Mini One Stop Shop is a service run by HMRC that allows you to report
sales of e-services into EU member states without requiring you to register
separately in every tax jurisdiction.  See `VAT on digital services in the
EU`_ for more information.

.. _`VAT on digital services in the EU`: https://www.gov.uk/vat-on-digital-services-in-the-eu

.. autofunction:: generate

.. py:data:: STANDARD_RATE
             REDUCED_RATE

Used to specify the type of VAT rate being used.
