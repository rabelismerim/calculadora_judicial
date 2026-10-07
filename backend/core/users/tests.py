from core.abstract.tests import AbstractTest, generate_name


class UserTest(AbstractTest):
    """User related tests"""

    path = 'users'


class UserDetailTest(AbstractTest):
    """User related tests"""

    path = 'user/detail'


class GroupTest(AbstractTest):
    """User related tests"""

    path = 'groups'


class SignStatusTest(AbstractTest):
    """User related tests"""

    path = 'drfmsal_signstatus'
