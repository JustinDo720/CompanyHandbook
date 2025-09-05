from rest_framework import permissions 

class IsOwnerOrAdminHandbook(permissions.BasePermission):
    """
        Allow activites to only Owners + Admin 
    """
    def has_object_permission(self, request, view, obj):
        # Cecking if the user is an admin 
        if request.user.is_staff:
            return True 
        # We're trying to see if the Handbooks.comapny matches that of our requested user 
        #
        # Understand that obj.company is your instance and since your auth model is ComapnyUser then request.user should be the same as obj.company instance 
        return obj.company == request.user