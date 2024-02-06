import django.dispatch

gen_calc = django.dispatch.Signal()  # Signal to generate the Statement calculation
new_calc = django.dispatch.Signal()  # Signal generated where new calculation
update_calc = django.dispatch.Signal()  # Signal generated where updated calculation
gen_total_funds = django.dispatch.Signal()  # signal to generate total statement  calculation
gen_statement_funds = django.dispatch.Signal()  # signal to generate statement funds calculation
gen_statement_integrations = django.dispatch.Signal()  # signal to generate statement integrations calculation
gen_statement_documents = django.dispatch.Signal()  # signal to generate statement documents calculation
gen_statement_danos = django.dispatch.Signal()  # signal to generate statement danos calculation
gen_statement_total_documents = django.dispatch.Signal()  # signal to generate statement documents total calculation
gen_statement_irrf = django.dispatch.Signal()  # signal to generate statement irrf calculation
gen_total_statement_funds = django.dispatch.Signal()  # signal to generate the total calculation of the funds
gen_total_statement_integrations = django.dispatch.Signal()  # signal to generate the total calculation of the
# integrations
