"""
This module defines a Api's classes that provides HTTP methods for managing Comment objects models.
It is extended from an AbstractViewApi class and includes a CheckHasPermission permission class for authorization.
Api's responds with JSON data and uses rest_framework.schemas.openapi.AutoSchema to generate the API documents.
Api's classes use the Comment model and schema Comment to work with data.
"""


from calculation.comment.schemas import CommentSchema
from calculation.comment.models import Comment
from core.abstract.views import AbstractViewApi

from rest_framework import permissions
from core.permission.views import CheckHasPermission
from utils import _

class CommentApi(AbstractViewApi):
    """Define the CommentApi view class for handling HTTP methods related to Comment.

    This view class extends the AbstractViewApi class, which provides a basic implementation
    for common API actions. The CommentApi supports HTTP POST and GET methods, and uses the CommentSchema
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
        To retrieve comment with a matching description:
        ```
        GET /api/v1/comment/?comment=comment_name
        ```
    """
    http_method_names = ['get']
    serializer_class = CommentSchema
    permission_classes = [permissions.IsAuthenticated, CheckHasPermission]
    model = Comment

    docs = {
        'init': _("""Represents the entire Comment.
                """),
        'get': _("""This method handles GET requests for the view. It retrieves a specific Comment object using the given
            calculation_id from the query parameters and serializes the result into JSON format before returning it as
             an HTTP response.

                Returns:
                    JsonResponse: An HTTP response containing the serialized Comment data retrieved.
                """)
    }

    query_params = [
        {
            "name": "comment",
            "field": "comment__icontains",
            "in": "query",
            "required": False,
            "description": _("comment"),
            "schema": {"type": "string"}
        }
    ]
