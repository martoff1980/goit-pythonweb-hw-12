Endpoints
=========

This section lists all available API endpoints grouped by routers.

Auth Router
---------------

.. automodule:: main
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: rate_limit_handler, contacts_router, admin_router, user_router, AuthMiddleware, limiter, cache_user


Admin Router
---------------

.. automodule:: routers.admin
    :members:
    :undoc-members:
    :show-inheritance:


Contacts Router
---------------

.. automodule:: routers.contacts
    :members:
    :undoc-members:
    :show-inheritance:
    

Users Router
------------

.. automodule:: routers.users
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: get_redis, get_current_user, get_user_by_id


Email Router
------------

.. automodule:: services.email
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: create_email_confirmation_token, verify_email_token, get_user_by_email, send_verification_email