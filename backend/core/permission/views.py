from rest_framework import permissions


class CheckHasPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        option = {
            'GET': 'view',
            'PUT': 'change',
            'POST': 'add',
            'DELETE': 'delete',
        }

        return request.user.has_permission(f'{option.get(request.method)}_{view.model.__name__.lower()}')
