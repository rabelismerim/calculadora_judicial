"""
This module defines a Api's classes that provides HTTP methods for managing Scrapper objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Scrapper model and schema Scrapper to work with data.
"""
from apps.scrapper.schemas import ScrapperSchema
from apps.scrapper.models import Scrapper
from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _


class ScrapperApi(AbstractViewApi):
    """Define the ScrapperApi view class for handling HTTP methods related to Scrapper.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The ScrapperApi supports HTTP POST and GET methods, and uses the ScrapperSchema
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
        To retrieve scrapper with a matching description:
        ```
        GET /api/v1/scrapper/?scrapper=scrapper_name
        ```
    """
    http_method_names = ['get']
    serializer_class = ScrapperSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Scrapper

    docs = {
        'init': _("""Represents the entire Scrapper."""),
        'get': _("""This method handles GET requests for the view. It retrieves a specific Scrapper object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                :return:
                    - JsonResponse: An HTTP response containing the serialized Scrapper data retrieved.
                """)
    }

    query_params = [
        {
            "name": "scrapper",
            "field": "scrapper__icontains",
            "in": "query",
            "required": False,
            "description": _("scrapper"),
            "schema": {"type": "string"}
        }
    ]