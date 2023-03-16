import django.dispatch

gen_calc = django.dispatch.Signal()  # Signal to generate the Statement calculation
gen_total_statement_funds = django.dispatch.Signal()  # signal to generate the total calculation of the funds
gen_total_statement_integrations = django.dispatch.Signal()  # signal to generate the total calculation of the
# integrations
