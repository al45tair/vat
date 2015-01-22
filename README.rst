==========
Python VAT
==========

.. image:: https://drone.io/bitbucket.org/al45tair/vat/status.png
   :target: https://drone.io/bitbucket.org/al45tair/vat/latest
   :alt: Build Status

What is this?
-------------

It’s a package of useful Python code relating to VAT, that’s what.  It
includes

- Tables mapping ISO alpha 2 country codes to VAT codes and vice-versa
- Tables of VAT number formats
- Tables of VAT rates, thresholds and registration periods
- Support for querying the VIES VAT database system (to check VAT details),
  *including fuzzy matching support for names and addresses*
- Utility functions for UK VAT (in the vat.gb package), including

  * EC sales list XML generation

  * Mini One Stop Shop (MOSS) return generation

A few words about VAT
---------------------

In the European Union, companies are expected to charge and account for Value
Added Tax (VAT).  This has a variety of other names (IVA, TVA, MwSt., USt.,
BTW, ДДС, ΦΠΑ, DPH, PDV, Moms, km, ALV, ÁFA, CBL, PVN, PVM, PTU, DDV, IGIC and
TAW), but it’s the same basic idea, and the rules are---to some
extent---harmonised.

From the consumer’s perspective, VAT is a sales tax. However, from a
business’ perspective, it is not; unlike a sales tax, businesses charge VAT to
*everybody*, whether or not they are a business customer, and are able to
offset the VAT they have to pay over to the tax authority against the VAT they
have themselves paid.

Sounds simple?  Hah!  You have *no* idea.

The first problem is that all of the different countries have their own rates
for VAT, and most of them have at least two rates that apply to different
categories of goods and services.  The second problem is cross-border
transactions; depending on the nature of the transaction, the supplier may or
may not be expected to charge VAT to the purchaser, and when they do not, the
purchaser will generally be expected to account for VAT under the “reverse
charge” rules (essentially by charging himself VAT, which will normally result
in no payment to the tax authority because the amount to be paid will be
offset entirely by itself).

There are all kinds of additional complications---some member states operate
registration thresholds, others don’t; some provide a grace period for
registration, in others you’ve broken the law if you make a supply that takes
you over the threshold; some allow you to register and submit returns
yourself, others require that you hire people to do it for you; and so on.

One further niggle is that **suppliers of electronic services outside of the
European Union are expected to charge VAT to their European customers**.  Many
don’t, with the result that their products can be priced more competitively
than would be possible for a company operating within the European Union.

DISCLAIMER
----------

**It is YOUR RESPONSIBILITY if you use this code to check that the rates and
thresholds you are using are the correct ones.  The author cannot be held
liable for errors in this material, particularly as much of it comes from
documents on the EU website that may be out of date and that themselves
include disclaimers.**

Documentation
-------------

The documentation for this package is available on `Read the Docs
<http://vat.readthedocs.org/en/latest>`_.
