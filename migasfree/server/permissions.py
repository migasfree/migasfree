# -*- coding: utf-8 *-*

from rest_framework import permissions


class PublicPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated()


class IsAdminOrIsSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        # allow user to list all users if logged in user is supersuser
        return view.action == 'retrieve' or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        # allow logged in user to view own details,
        # allows superuser to view all records
        return request.user.is_superuser or obj == request.user
