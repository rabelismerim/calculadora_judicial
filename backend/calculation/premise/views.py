"""
This module defines a Api's classes that provides HTTP methods for managing Premise objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Premise model and schema Premise to work with data.
"""
import datetime
from calculation.models import Calculation
from calculation.premise.schemas import PremiseSchema
from calculation.premise.models import Premise
from config.settings import INDEX_VARIATION_END, INDEX_VARIATION_RJ
from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from rates.models import Rate
from utils import _

docs = {
    'init': _("""Represents the assumptions (observations) that were used in the calculation. Ex: the value was 
        updated using the TST index. Some assumptions are loaded automatically when creating the calculation. Others 
        can be selected by the user.
                """),
    'get': _("""This method handles GET requests for the view. It retrieves a specific Premise object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Premise data retrieved.
                """),
    'post': _("""Create Premise object from request data and return Premise detail.
                Returns:
                    JsonResponse: A JSON response containing the created Funds
                     object detail.

                Raises:
                    serializers.ValidationError: If the input data is invalid.
                    """)
}


class PremiseApi(AbstractViewApi):
    """Define the PremiseApi view class for handling HTTP methods related to Premise.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The PremiseApi supports HTTP POST and GET methods, and uses the PremiseSchema
    serializer for input/output validation. The view requires authenticated users with appropriate
    permissions to access the API endpoints, as specified by the IsAuthenticated and CheckHasPermission
    permission classes.

    Attributes:
        http_method_names (list): A list of HTTP methods supported by this view.
        serializer_class (class): The serializer class for input/output validation.
        permission_classes (list): A list of permission classes for user authentication and authorization.
        model (class): The model class associated with this view.

        query_params (list): A list of dictionaries, each specifying a query parameter for the API.

    Examples:
        To retrieve premise with a matching description:
        ```
        GET /api/v1/premise/?premise=premise_name
        ```
    """
    http_method_names = ['get', 'post']
    serializer_class = PremiseSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Premise

    docs = docs.copy()

    query_params = [
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": _("Premise"),
            "schema": {"type": "string"}
        }
    ]


class PremiseCreator:
    def __init__(self, calculation: Calculation):
        self.__calculation = calculation
        self.__premise_ids = []

        self.__create_premise_default_interest()
        self.__create_premise_rate()
        self.__create_premise_appeal_credit()
        self.__create_premise_recurral_deposit()
        self.__create_premise_advocative_hours()
        self.__create_premise_agreement()
        self.__save_premises()

    def __create_new_premise(self, description) -> Premise:
        """Helper method to create a new Premise that is not stored in the database."""
        return self._append_premise(Premise.objects.get_or_create(**description)[0])

    def _append_premise(self, premise: Premise) -> Premise:
        """Include premise id in list to save"""
        self.__premise_ids.append(premise.id)
        return premise

    def __create_premise_default_interest(self):
        """
        Creates a new premise object based on the calculation data using the following logic:
            - If the date of RJ filing is missing, returns None.
            - If the rate is IPCA-E/SELIC and the calculation is related to citation,
              uses the SELIC rate and calculates the moratory interest from the date of citation to the date of RJ
               request.
            - If the rate is IPCA-E/SELIC and the calculation is related to filing of the complaint,
              uses the SELIC rate and calculates the moratory interest from the date of filing to the date of RJ
               request.
            - If the date of RJ filing is before the date of RJ request,
              calculates the moratory interest using the default interest rate from the date of filing to the date of
               RJ request.
            - Otherwise, no moratory interest is applied.

        Excel Statement A68
            =IF($B$19=0;"PREENCHER FICHA DE ANÁLISE";IF(AND('Ficha de Análise'!$D$65="IPCA-E/SELIC";'Ficha de Análise
            '!$F$66="citação");"Houve incidência de juros moratórios através da taxa SELIC, desde a data da citação até
             a data do pedido de RJ.";IF(AND('Ficha de Análise'!$D$65="IPCA-E/SELIC";'Ficha de Análise'!$F$66="ajuizam
             ento da Reclamação Trabalhista");"Houve incidência de juros moratórios através da taxa SELIC, desde a data
              do ajuizamento da Reclamação Trabalhista até a data do pedido de RJ.";IF($B$19<$B$18;"Houve incidência de
               juros moratórios de 1% ao mês, desde a data de ajuizamento da Reclamação Trabalhista até a data do
               pedido de RJ.";"Não foram aplicados juros moratórios, em virtude da data de ajuizamento da Reclamação
               Trabalhista
            """

        date_rj_filing = self.__calculation.get_date_rj_filing()
        date_rj_request = self.__calculation.get_date_rj_request()
        is_ipca_e_selic = self.__calculation.get_rate().is_ipca_e_selic()
        is_citation = self.__calculation.is_citation()
        is_filing = self.__calculation.is_filing()
        default_interest = self.__calculation.get_default_interest()

        if not date_rj_filing:
            return
        elif is_ipca_e_selic and is_citation:
            comment = {
                'description': "Houve incidência de juros moratórios através da taxa SELIC, desde a data da citação "
                               "até a data do pedido de RJ.",
                'description_en': "Default interest was levied at the SELIC rate, from the date of service of process "
                                  "to the date of RJ's request.",
                'description_pt_br': "Houve incidência de juros moratórios através da taxa SELIC, desde a data da "
                                     "citação até a data do pedido de RJ."
            }
        elif is_ipca_e_selic and is_filing == "ajuizamento da Reclamação Trabalhista":
            comment = {
                'description': "Houve incidência de juros moratórios através da taxa SELIC, desde a data do "
                               "ajuizamento da Reclamação Trabalhista até a data do pedido de RJ.",
                'description_en': "There was interest on arrears at the SELIC rate, from the date of filing of the "
                                  "Labor Complaint to the date of RJ's request.",
                'description_pt_br': "Houve incidência de juros moratórios através da taxa SELIC, desde a data do "
                                     "ajuizamento da Reclamação Trabalhista até a data do pedido de RJ."
            }
        elif date_rj_filing < date_rj_request:
            comment = {
                'description': "Houve incidência de juros moratórios de {}% ao mês, desde a data de "
                               "ajuizamento da Reclamação Trabalhista até a data do pedido de RJ."
                .format(default_interest),
                'description_en': "There was arrears interest of {}% per month, from the filing date of the Labor "
                                  "Complaint to the date of RJ's request.".format(default_interest),
                'description_pt_br': "Houve incidência de juros moratórios de {}% ao mês, desde a data de "
                                     "ajuizamento da Reclamação Trabalhista até a data do pedido de RJ."
                .format(default_interest)
            }
        else:
            comment = {
                'description': "Não foram aplicados juros moratórios, em virtude da data de ajuizamento da "
                               "Reclamação Trabalhista ser igual ou posterior à data do pedido de RJ.",
                'description_en': "No arrears interest was applied, due to the filing date of the Labor Complaint "
                                  "being equal to or later than the date of RJ's request.",
                'description_pt_br': "Não foram aplicados juros moratórios, em virtude da data de ajuizamento da "
                                     "Reclamação Trabalhista ser igual ou posterior à data do pedido de RJ. "
            }
        self.__create_new_premise(comment)

    def __create_premise_rate(self):
        """
        Creates a new premise based on the fields of the associated `Calculation` model.

        This method determines the content of the premise's description based on various fields of
        the associated `Calculation` model. First, it checks if the rate used to calculate the credit
        is the IPCA-E/SELIC index, in which case it sets the comment to indicate that the credit was
        updated based on that index. If the date the calculation was approved is not available, it sets
        the comment to instruct the user to fill in that field.

        If the rate is the TST index and the calculation was approved after the `INDEX_VARIATION_END`
        date, and the request for the RJ was made before the `INDEX_VARIATION_RJ` date, it assumes
        that the TST index did not change since September 2017 and sets the comment accordingly to
        use the value of the approved principal. In all other cases, it sets the comment to indicate
        that the credit was updated based on the specified index.

        Excel Statement A66

        =IF('Ficha de Análise'!D65="IPCA-E/SELIC";"O crédito foi atualizado pelo índice IPCA-E desde a data base das
         verbas até a data do pedido de RJ";IF(OR($B$20="";$N$5="";$Q$5="");"PREENCHER FICHA DE ANÁLISE E CÉLULAS N13
          E Q13";IF(AND($N$5="Sim";$B$20="TST";$Q$5>=42979;$B$18<44531);"Considerando que o índice do TST não teve
           variação desde setembro/2017 e que o cálculo homologado foi atualizado até "&TEXT($Q$5;"dd/mm/aaaa")&"
           , utilizamos o valor do principal homologado.";"O crédito foi atualizado pelo índice "&B20&" desde a data
            base das verbas até a data do pedido de RJ.")))
        """
        date_rj_request: datetime.date or None = self.__calculation.get_date_rj_request()
        rate: Rate = self.__calculation.get_rate()
        is_tst: bool = rate.is_tst()
        is_ipca_e_selic: bool = rate.is_ipca_e_selic()
        appeal_credit: bool = self.__calculation.get_appeal_credit()
        date_approved_calculation: datetime.date or None = self.__calculation.get_date_approved_calculation()
        if not date_rj_request:
            return
        if is_ipca_e_selic:
            comment = {
                'description': "O crédito foi atualizado pelo índice IPCA-E desde a data base das verbas até a data "
                               "do pedido de RJ.",
                'description_en': "The credit was updated by the IPCA-E index from the base date of the funds to the "
                                  "order date from RJ.",
                'description_pt_br': "O crédito foi atualizado pelo índice IPCA-E desde a data base das verbas até a "
                                     "data do pedido de RJ."
            }
        elif not date_approved_calculation:
            comment = {
                'description': "Preencher data do cálculo homologado.",
                'description_en': "Fill in the approved calculation date.",
                'description_pt_br': "Preencher data do cálculo homologado."
            }
        # TODO ver se essas datas podem ser alteradas depois
        elif appeal_credit and is_tst and date_approved_calculation >= INDEX_VARIATION_END \
                and date_rj_request < INDEX_VARIATION_RJ:
            comment = {
                'description': "Considerando que o índice do TST não teve variação desde setembro/2017 e que o "
                               "cálculo homologado foi atualizado até {}, utilizamos o valor do principal homologado"
                               ".".format(date_approved_calculation),
                'description_en': "Considering that the TST index has not changed since September/2017 and that the "
                                  "calculation approved has been updated to {}, we use the value of the approved "
                                  "principal.".format(date_approved_calculation),
                'description_pt_br': "Considerando que o índice do TST não teve variação desde setembro/2017 e que o "
                                     "cálculo homologado foi atualizado até {}, utilizamos o valor do principal "
                                     "homologado .".format(date_approved_calculation),
            }
        else:
            comment = {
                'description': "O crédito foi atualizado pelo índice {} desde a data base das verbas até a data do "
                               "pedido de RJ.".format(rate.index),
                'description_en': "The credit was updated by the index {} from the base date of the funds to the date "
                                  "of the order from RJ.".format(rate.index),
                'description_pt_br': "O crédito foi atualizado pelo índice {} desde a data base das verbas até a data "
                                     "do pedido de RJ.".format(rate.index)
            }

        self.__create_new_premise(comment)

    def __create_premise_appeal_credit(self):
        """
        Creates a new premise if a dismissal exists and either there is no appeal credit,
        or the dismissal period plus 10 days is greater than the date of the RJ request.

        Excel Statement A70
            =IF(OR(N5="não";'Ficha de Análise'!$D$62+10>$B$18);"Para realização do cálculo foram consideradas somente
            as verbas concursais.";IF('Ficha de Análise'!$D$62="";"PREENCHER FICHA DE ANÁLISE";"EXCLUIR LINHA"))
        """
        appeal_credit: bool = self.__calculation.get_appeal_credit()
        date_rj_request = self.__calculation.get_date_rj_request()
        dismissal = self.__calculation.get_dismissal()
        comment = None
        if not dismissal:
            comment = {
                'description': "Preencher data de demissão",
                'description_en': "Fill in the resignation date",
                'description_pt_br': "Preencher data de demissão"
            }

        if not date_rj_request:
            comment = {
                'description': "Preencher data do pedido de Recuperação AJ.",
                'description_en': "Fill in the date of the AJ Recovery request",
                'description_pt_br': "Preencher data do pedido de Recuperação AJ."
            }

        if comment:
            self.__create_new_premise(comment)
            return

        dismissal = dismissal + datetime.timedelta(days=10)
        if not appeal_credit or dismissal > date_rj_request:
            comment = {
                'description': "Para realização do cálculo foram consideradas somente as verbas concursais.",
                'description_en': "To carry out the calculation, only the tender amounts were considered.",
                'description_pt_br': "Para realização do cálculo foram consideradas somente as verbas concursais."
            }
            self.__create_new_premise(comment)

    def __create_premise_recurral_deposit(self):
        """
        Creates a new premise based on appeal deposit information.

        This method obtains the appeal deposit amount and the number of pages where this information is located from
        the Calculation object. If the appeal deposit amount is available, it creates a comment with information
        on the pages where this amount is located. If the page number is not available, the comment reminds the user
        to fill out the appeal deposit withdrawal page. The comment is then used to create a new Premise object.

        Excel Statement A72
            =IF($N$7="";"PREENCHER CÉLULA N16";IF($N$7="NÃO";"EXCLUIR LINHA";"O valor de depósito recursal descontado
             no cálculo foi informado às fls."&$Q$7&" da Reclamação Trabalhista."))
        """
        appeal_deposit: bool = self.__calculation.get_appeal_deposit()
        num_pag_fls_appeal_deposit: str or None = self.__calculation.get_num_pag_fls_appeal_deposit()

        if appeal_deposit:
            if not num_pag_fls_appeal_deposit:
                comment = {
                    'description': "Preencher a página do levantamento de depósito recursal.",
                    'description_en': "Fill out the appeal deposit withdrawal page.",
                    'description_pt_br': "Preencher a página do levantamento de depósito recursal.",
                }
            else:
                comment = {
                    'description': "O valor de depósito recursal descontado no cálculo foi informado às fls.{} da "
                                   "Reclamação Trabalhista.".format(num_pag_fls_appeal_deposit),
                    'description_en': "The appeal deposit amount discounted in the calculation was informed on pages"
                                      " {} of Labour Complaint.".format(num_pag_fls_appeal_deposit),
                    'description_pt_br': "O valor de depósito recursal descontado no cálculo foi informado às fls.{} "
                                         "da Reclamação Trabalhista.".format(num_pag_fls_appeal_deposit),
                }
            self.__create_new_premise(comment)

    def __create_premise_updated_date(self):
        """
        Creates a new premise with date information. He first checks if he has the date of the credit qualification
        certificate. If there is no date, it creates the premise that lacks the date. If available, the comment
        explains that the creditor's calculator has been updated as of the indicated date.

        Excel Statement A74
            =IF($N$9="";"PREENCHER CÉLULA N17";"O cálculo apresentado pelo credor foi atualizado até
            "&TEXT(N9;"dd/mm/aaaa")&".")
        """

        date_credit_auth: datetime.date or None = self.__calculation.get_date_credit_auth()

        if not date_credit_auth:
            comment = {
                'description': "Preencher data da certidão de habilitação de crédito.",
                'description_en': "Fill in the date of the credit qualification certificate.",
                'description_pt_br': "Preencher data da certidão de habilitação de crédito.",
            }
        else:
            comment = {
                'description': "O cálculo apresentado pelo credor foi atualizado até {}.".format(date_credit_auth),
                'description_en': "The calculation presented by the creditor was updated up to {}.".format(
                    date_credit_auth),
                'description_pt_br': "O cálculo apresentado pelo credor foi atualizado até {}.".format(
                    date_credit_auth),
            }
        self.__create_new_premise(comment)

    def __create_premise_advocative_hours(self):
        """
        Creates a new premise with date information. He first checks if he has the date of the credit qualification
        certificate. If there is no date, it creates the premise that lacks the date. If available, the comment
        explains that the creditor's calculator has been updated as of the indicated date.

        Excel Statement A76
            =IFERROR(IF($N$10="";"PREENCHER CÉLULA N18";IF($N$10="NÃO";"EXCLUIR LINHA";IF($B$23>0;"A Administradora
            Judicial considerou honorários advocatícios de "&$B$23*100&"% sobre o crédito em favor do Patrono
            "&$A$50&".";"PREENCHER CÉLULA D11 E B20 OU EXCLUIR LINHA")));"O valor dos honorários ao advogado é
            extraconcursal, uma vez que seu arbitramento ocorreu após o pedido de recuperação judicial.")
        """

        has_advocative_hours: bool = self.__calculation.get_has_advocative_hours()
        advocative_hours: float = self.__calculation.get_advocative_hours()
        lawyer: str = self.__calculation.get_lawyer()

        if not has_advocative_hours:
            return
        elif advocative_hours > 0:
            comment = {
                'description': "A Administradora Judicial considerou honorários advocatícios de {}% sobre o crédito "
                               "em favor do Patrono {}.".format(advocative_hours, lawyer),
                'description_en': "The Trustee considered attorney fees of {}% on the claim "
                                  "in favor of Patron {}.".format(advocative_hours, lawyer),
                'description_pt_br': "A Administradora Judicial considerou honorários advocatícios de {}% sobre o "
                                     "crédito em favor do Patrono {}.".format(advocative_hours, lawyer),
            }
        else:
            comment = {
                'description': "O valor dos honorários ao advogado é extraconcursal, uma vez que seu arbitramento "
                               "ocorreu após o pedido de recuperação judicial.",
                'description_en': "The value of the lawyer's fees is extra-bankruptcy, since its arbitration "
                                  "occurred after the request for judicial recovery.",
                'description_pt_br': "O valor dos honorários ao advogado é extraconcursal, uma vez que seu "
                                     "arbitramento ocorreu após o pedido de recuperação judicial.",
            }

        self.__create_new_premise(comment)

    def __create_premise_agreement(self):
        """
        Creates a new premise with date information. He first checks if he has the date of the credit qualification
        certificate. If there is no date, it creates the premise that lacks the date. If available, the comment
        explains that the creditor's calculator has been updated as of the indicated date.

        Excel Statement A76
            =IFERROR(IF($N$10="";"PREENCHER CÉLULA N18";IF($N$10="NÃO";"EXCLUIR LINHA";IF($B$23>0;"A Administradora
            Judicial considerou honorários advocatícios de "&$B$23*100&"% sobre o crédito em favor do Patrono
            "&$A$50&".";"PREENCHER CÉLULA D11 E B20 OU EXCLUIR LINHA")));"O valor dos honorários ao advogado é
            extraconcursal, uma vez que seu arbitramento ocorreu após o pedido de recuperação judicial.")
        """

        is_agreement: bool = self.__calculation.is_agreement()
        if is_agreement:
            # TODO ver se o indice e o valor de juros podem ser alterados
            comment = {
                'description': "O valor do acordo foi atualizado pelo índice TST e acrescido de juros de mora de 1% "
                               "ao mês desde o vencimento das parcelas até a data do pedido de RJ.",
                'description_en': "The value of the agreement was updated by the TST index and increased by default "
                                  "interest of 1% per month from the due date of the installments to the date of the "
                                  "RJ request.",
                'description_pt_br': "O valor do acordo foi atualizado pelo índice TST e acrescido de juros de mora de "
                                     "1% ao mês desde o vencimento das parcelas até a data do pedido de RJ.",
            }
        else:
            comment = {
                'description': "O valor dos honorários ao advogado é extraconcursal, uma vez que seu arbitramento "
                               "ocorreu após o pedido de recuperação judicial.",
                'description_en': "The value of the lawyer's fees is extra-bankruptcy, since its arbitration "
                                  "occurred after the request for judicial recovery.",
                'description_pt_br': "O valor dos honorários ao advogado é extraconcursal, uma vez que seu "
                                     "arbitramento ocorreu após o pedido de recuperação judicial.",
            }

        self.__create_new_premise(comment)

    def __save_premises(self):
        """Save the premises created in the calculation object"""
        if self.__premise_ids:
            self.__calculation.premises.add(*self.__premise_ids)
            self.__calculation.save()
