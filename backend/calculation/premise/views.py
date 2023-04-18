"""
This module defines a Api's classes that provides HTTP methods for managing Premise objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Premise model and schema Premise to work with data.
"""
from calculation.models import Calculation
from calculation.premise.schemas import PremiseSchema
from calculation.premise.models import Premise
from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
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

    docs = docs

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
        self._premise_ids = []

    def _create_new_premise(self, description) -> Premise:
        """
        Helper method to create a new Premise that is not stored in the database.
        """
        return self._append_premise(Premise.objects.get_or_create(description=description)[0])

    def _append_premise(self, premise: Premise) -> Premise:
        """"""
        self._premise_ids.append(premise.id)
        return premise

    def _create_premise_default_interest(self):
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

        Excel
            =IF($B$19=0;"PREENCHER FICHA DE ANÁLISE";IF(AND('Ficha de Análise'!$D$65="IPCA-E/SELIC";'Ficha de Análise
            '!$F$66="citação");"Houve incidência de juros moratórios através da taxa SELIC, desde a data da citação até
             a data do pedido de RJ.";IF(AND('Ficha de Análise'!$D$65="IPCA-E/SELIC";'Ficha de Análise'!$F$66="ajuizamento
              da Reclamação Trabalhista");"Houve incidência de juros moratórios através da taxa SELIC, desde a data do
               ajuizamento da Reclamação Trabalhista até a data do pedido de RJ.";IF($B$19<$B$18;"Houve incidência de juros
                moratórios de 1% ao mês, desde a data de ajuizamento da Reclamação Trabalhista até a data do pedido de
                 RJ.";"Não foram aplicados juros moratórios, em virtude da data de ajuizamento da Reclamação Trabalhista
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
            comment = "Default interest was levied at the SELIC rate, from the date of service of process to the " \
                      "date of RJ's request."
        elif is_ipca_e_selic and is_filing == "ajuizamento da Reclamação Trabalhista":
            comment = "There was interest on arrears at the SELIC rate, from the date of filing of the Labor " \
                      "Complaint to the date of RJ's request. "
        elif date_rj_filing < date_rj_request:
            comment = "There was arrears interest of {}% per month, from the filing date of the Labor Complaint to " \
                      "the date of RJ's request.".format(default_interest)
        else:
            comment = "No arrears interest was applied, due to the filing date of the Labor Complaint being equal to " \
                      "or later than the date of RJ's request. "
        self._create_new_premise(str(comment))

    def create_premises(self):
        self._create_premise_default_interest()
        statement = self.__calculation.get_statement()
        if self._premise_ids and statement:
            statement.premises.add(*self._premise_ids)
            statement.save()
