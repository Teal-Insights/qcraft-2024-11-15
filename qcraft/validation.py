"""Input schema, domain, and value-map checks for bound Model arguments."""

from __future__ import annotations

from typing import Annotated, Literal

from . import data
from .excel import coerce_input_measure
from .runtime import RealBetween, require_annotated_domain


def _check_country(
    country: Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"],
) -> Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"]:
    """Validate `country` before the model reads it."""
    country = coerce_input_measure(country, dtype="string", series_id="country")
    require_annotated_domain(
        country,
        Literal["C\u00f4te d'Ivoire", "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Anguilla", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Costa Rica", "Croatia", "Cyprus", "Czech Republic", "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", "Gabon", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong SAR", "Hungary", "Iceland", "India", "Indonesia", "Iraq", "Ireland", "Islamic Republic of Iran", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea", "Kosovo", "Kuwait", "Kyrgyz Republic", "Lao P.D.R.", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Lithuania", "Luxembourg", "Macao SAR", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of Congo", "Romania", "Russia", "Rwanda", "Samoa", "San Marino", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovak Republic", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "St. Kitts and Nevis", "St. Lucia", "St. Vincent and the Grenadines", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "S\u00e3o Tom\u00e9 and Pr\u00edncipe", "Taiwan Province of China", "Tajikistan", "Tanzania", "Thailand", "The Bahamas", "The Gambia", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkmenistan", "Tuvalu", "T\u00fcrkiye", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "West Bank and Gaza", "Yemen", "Zambia", "Zimbabwe"],
        series_id="country",
    )
    return country


def _check_demography_scenario(
    demography_scenario: Literal["High", "Low", "Medium"],
) -> Literal["High", "Low", "Medium"]:
    """Validate `demography_scenario` before the model reads it."""
    demography_scenario = coerce_input_measure(demography_scenario, dtype="string", series_id="demography_scenario")
    require_annotated_domain(
        demography_scenario,
        Literal["High", "Low", "Medium"],
        series_id="demography_scenario",
    )
    return demography_scenario


def _check_productivity_start(
    productivity_start: Annotated[float, RealBetween(-100.0, 100.0)],
) -> Annotated[float, RealBetween(-100.0, 100.0)]:
    """Validate `productivity_start` before the model reads it."""
    productivity_start = coerce_input_measure(productivity_start, dtype="float", series_id="productivity_start")
    require_annotated_domain(
        productivity_start,
        Annotated[float, RealBetween(-100.0, 100.0)],
        series_id="productivity_start",
    )
    return productivity_start


def _check_productivity_end(
    productivity_end: Annotated[float, RealBetween(-100.0, 100.0)],
) -> Annotated[float, RealBetween(-100.0, 100.0)]:
    """Validate `productivity_end` before the model reads it."""
    productivity_end = coerce_input_measure(productivity_end, dtype="float", series_id="productivity_end")
    require_annotated_domain(
        productivity_end,
        Annotated[float, RealBetween(-100.0, 100.0)],
        series_id="productivity_end",
    )
    return productivity_end


def _check_inflation_start(
    inflation_start: Annotated[float, RealBetween(-100.0, 100.0)],
) -> Annotated[float, RealBetween(-100.0, 100.0)]:
    """Validate `inflation_start` before the model reads it."""
    inflation_start = coerce_input_measure(inflation_start, dtype="float", series_id="inflation_start")
    require_annotated_domain(
        inflation_start,
        Annotated[float, RealBetween(-100.0, 100.0)],
        series_id="inflation_start",
    )
    return inflation_start


def _check_inflation_end(
    inflation_end: Annotated[float, RealBetween(-100.0, 100.0)],
) -> Annotated[float, RealBetween(-100.0, 100.0)]:
    """Validate `inflation_end` before the model reads it."""
    inflation_end = coerce_input_measure(inflation_end, dtype="float", series_id="inflation_end")
    require_annotated_domain(
        inflation_end,
        Annotated[float, RealBetween(-100.0, 100.0)],
        series_id="inflation_end",
    )
    return inflation_end


def _check_interest_rate_mode(
    interest_rate_mode: Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"],
) -> Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"]:
    """Validate `interest_rate_mode` before the model reads it."""
    interest_rate_mode = coerce_input_measure(interest_rate_mode, dtype="string", series_id="interest_rate_mode")
    require_annotated_domain(
        interest_rate_mode,
        Literal["Interest-growth differential", "Nominal interest rate", "Real interest rate (a)"],
        series_id="interest_rate_mode",
    )
    return interest_rate_mode


def _check_real_interest_rate(
    real_interest_rate: Annotated[float, RealBetween(-20.0, 20.0)],
) -> Annotated[float, RealBetween(-20.0, 20.0)]:
    """Validate `real_interest_rate` before the model reads it."""
    real_interest_rate = coerce_input_measure(real_interest_rate, dtype="float", series_id="real_interest_rate")
    require_annotated_domain(
        real_interest_rate,
        Annotated[float, RealBetween(-20.0, 20.0)],
        series_id="real_interest_rate",
    )
    return real_interest_rate


def _check_fiscal_rule_enabled(fiscal_rule_enabled: Literal["No", "Yes"]) -> Literal["No", "Yes"]:
    """Validate `fiscal_rule_enabled` before the model reads it."""
    fiscal_rule_enabled = coerce_input_measure(fiscal_rule_enabled, dtype="string", series_id="fiscal_rule_enabled")
    require_annotated_domain(
        fiscal_rule_enabled,
        Literal["No", "Yes"],
        series_id="fiscal_rule_enabled",
    )
    return fiscal_rule_enabled


def _check_debt_target(
    debt_target: Annotated[float, RealBetween(0.0, 300.0)],
) -> Annotated[float, RealBetween(0.0, 300.0)]:
    """Validate `debt_target` before the model reads it."""
    debt_target = coerce_input_measure(debt_target, dtype="float", series_id="debt_target")
    require_annotated_domain(
        debt_target,
        Annotated[float, RealBetween(0.0, 300.0)],
        series_id="debt_target",
    )
    return debt_target


def _check_expenditure_rigidity(
    expenditure_rigidity: Annotated[float, RealBetween(0.0, 1.0)],
) -> Annotated[float, RealBetween(0.0, 1.0)]:
    """Validate `expenditure_rigidity` before the model reads it."""
    expenditure_rigidity = coerce_input_measure(expenditure_rigidity, dtype="float", series_id="expenditure_rigidity")
    require_annotated_domain(
        expenditure_rigidity,
        Annotated[float, RealBetween(0.0, 1.0)],
        series_id="expenditure_rigidity",
    )
    return expenditure_rigidity


def _check_discrete_revenue_shocks(
    discrete_revenue_shocks: data.DiscreteRevenueShocks,
) -> data.DiscreteRevenueShocks:
    """Validate `discrete_revenue_shocks` before the model reads it."""
    data.DISCRETE_REVENUE_SHOCKS.schema.validate(discrete_revenue_shocks)
    discrete_revenue_shocks = coerce_input_measure(discrete_revenue_shocks, dtype="float", series_id="discrete_revenue_shocks")
    for coordinate in data.DISCRETE_REVENUE_SHOCKS.required:
        require_annotated_domain(
            discrete_revenue_shocks[coordinate],
            Annotated[float, RealBetween(-100.0, 100.0)],
            series_id="discrete_revenue_shocks" + repr(coordinate),
        )
    return discrete_revenue_shocks


def _check_discrete_primary_expenditure_shocks(
    discrete_primary_expenditure_shocks: data.DiscretePrimaryExpenditureShocks,
) -> data.DiscretePrimaryExpenditureShocks:
    """Validate `discrete_primary_expenditure_shocks` before the model reads it."""
    data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.schema.validate(discrete_primary_expenditure_shocks)
    discrete_primary_expenditure_shocks = coerce_input_measure(discrete_primary_expenditure_shocks, dtype="float", series_id="discrete_primary_expenditure_shocks")
    for coordinate in data.DISCRETE_PRIMARY_EXPENDITURE_SHOCKS.required:
        require_annotated_domain(
            discrete_primary_expenditure_shocks[coordinate],
            Annotated[float, RealBetween(-100.0, 100.0)],
            series_id="discrete_primary_expenditure_shocks" + repr(coordinate),
        )
    return discrete_primary_expenditure_shocks


CHECKS = {
    "country": _check_country,
    "demography_scenario": _check_demography_scenario,
    "productivity_start": _check_productivity_start,
    "productivity_end": _check_productivity_end,
    "inflation_start": _check_inflation_start,
    "inflation_end": _check_inflation_end,
    "interest_rate_mode": _check_interest_rate_mode,
    "real_interest_rate": _check_real_interest_rate,
    "fiscal_rule_enabled": _check_fiscal_rule_enabled,
    "debt_target": _check_debt_target,
    "expenditure_rigidity": _check_expenditure_rigidity,
    "discrete_revenue_shocks": _check_discrete_revenue_shocks,
    "discrete_primary_expenditure_shocks": _check_discrete_primary_expenditure_shocks,
}
