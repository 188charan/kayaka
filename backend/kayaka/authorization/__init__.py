"""Pure role-based access control: permission codes and role -> permission maps.

This package holds no models and imports no other Kayaka domain module (it sits just above
`core`). Membership-aware checks that need the database live in `kayaka.tenancy.access`, which
is allowed to import from here. Keeping the RBAC vocabulary dependency-free lets every layer
reference the same permission codes without import cycles.
"""
