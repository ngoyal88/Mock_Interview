"""Supported company labels/slugs for pickers and target-company prefs.

Product catalog — not Fantastic.jobs org sync. `id` is the stable slug.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class SupportedCompany:
    id: str
    label: str
    aliases: tuple[str, ...] = ()


SUPPORTED_COMPANIES: Final[tuple[SupportedCompany, ...]] = (
    SupportedCompany(id="google", label="Google"),
    SupportedCompany(id="microsoft", label="Microsoft"),
    SupportedCompany(id="amazon", label="Amazon"),
    SupportedCompany(id="meta", label="Meta", aliases=("Facebook",)),
    SupportedCompany(id="apple", label="Apple"),
    SupportedCompany(id="netflix", label="Netflix"),
    SupportedCompany(id="uber", label="Uber"),
    SupportedCompany(id="airbnb", label="Airbnb"),
    SupportedCompany(id="stripe", label="Stripe"),
    SupportedCompany(id="atlassian", label="Atlassian"),
    SupportedCompany(id="salesforce", label="Salesforce"),
    SupportedCompany(id="adobe", label="Adobe"),
    SupportedCompany(id="oracle", label="Oracle"),
    SupportedCompany(id="ibm", label="IBM"),
    SupportedCompany(id="nvidia", label="Nvidia"),
    SupportedCompany(id="tesla", label="Tesla"),
    SupportedCompany(id="openai", label="OpenAI"),
    SupportedCompany(id="anthropic", label="Anthropic"),
    SupportedCompany(id="databricks", label="Databricks"),
    SupportedCompany(id="snowflake", label="Snowflake"),
    SupportedCompany(id="palantir", label="Palantir"),
    SupportedCompany(id="bloomberg", label="Bloomberg"),
    SupportedCompany(id="goldman-sachs", label="Goldman Sachs"),
    SupportedCompany(id="jpmorgan-chase", label="JPMorgan Chase", aliases=("JPMorgan", "Chase")),
    SupportedCompany(id="walmart-global-tech", label="Walmart Global Tech"),
    SupportedCompany(id="flipkart", label="Flipkart"),
    SupportedCompany(id="phonepe", label="PhonePe"),
    SupportedCompany(id="razorpay", label="Razorpay"),
    SupportedCompany(id="zomato", label="Zomato"),
    SupportedCompany(id="swiggy", label="Swiggy"),
    SupportedCompany(id="cred", label="CRED"),
    SupportedCompany(id="meesho", label="Meesho"),
    SupportedCompany(id="zoho", label="Zoho"),
    SupportedCompany(id="freshworks", label="Freshworks"),
    SupportedCompany(id="tcs", label="TCS", aliases=("Tata Consultancy Services",)),
    SupportedCompany(id="infosys", label="Infosys"),
    SupportedCompany(id="wipro", label="Wipro"),
    SupportedCompany(id="accenture", label="Accenture"),
    SupportedCompany(id="deloitte", label="Deloitte"),
)

COMPANY_LABELS: Final[tuple[str, ...]] = tuple(company.label for company in SUPPORTED_COMPANIES)
COMPANY_SLUGS: Final[tuple[str, ...]] = tuple(company.id for company in SUPPORTED_COMPANIES)
COMPANY_SLUG_SET: Final[frozenset[str]] = frozenset(COMPANY_SLUGS)
COMPANY_LABEL_SET: Final[frozenset[str]] = frozenset(COMPANY_LABELS)
