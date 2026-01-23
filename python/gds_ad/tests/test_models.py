"""Test suite for Active Directory models."""


from gds_ad.models import ADGroup, ADUser, GroupCategory, GroupScope


class TestADGroup:
    """Tests for ADGroup model."""

    def test_create_basic_group(self):
        """Test creating a basic ADGroup."""
        group = ADGroup(
            name="SQL_Admin",
            distinguished_name="CN=SQL_Admin,OU=Groups,DC=example,DC=com",
        )
        assert group.name == "SQL_Admin"
        assert group.distinguished_name == "CN=SQL_Admin,OU=Groups,DC=example,DC=com"
        assert group.category == GroupCategory.SECURITY
        assert group.scope is None
        assert group.description is None
        assert group.members == []

    def test_create_group_with_all_fields(self):
        """Test creating an ADGroup with all fields."""
        group = ADGroup(
            name="SQL_Admin",
            distinguished_name="CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            category=GroupCategory.SECURITY,
            scope=GroupScope.GLOBAL,
            description="SQL Server Administrators",
            members=["CN=User1,DC=example,DC=com"],
        )
        assert group.name == "SQL_Admin"
        assert group.category == GroupCategory.SECURITY
        assert group.scope == GroupScope.GLOBAL
        assert group.description == "SQL Server Administrators"
        assert len(group.members) == 1

    def test_from_ldap_entry_security_group(self):
        """Test creating ADGroup from LDAP entry for security group."""
        entry = {
            "dn": "CN=SQL_Admin,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["SQL_Admin"],
                "sAMAccountName": ["SQL_Admin"],
                "distinguishedName": ["CN=SQL_Admin,OU=Groups,DC=example,DC=com"],
                "groupType": [-2147483646],  # Security, Global
                "description": ["SQL Server Administrators"],
            },
        }
        group = ADGroup.from_ldap_entry(entry)

        assert group.name == "SQL_Admin"
        assert group.distinguished_name == "CN=SQL_Admin,OU=Groups,DC=example,DC=com"
        assert group.category == GroupCategory.SECURITY
        assert group.scope == GroupScope.GLOBAL
        assert group.description == "SQL Server Administrators"

    def test_from_ldap_entry_distribution_group(self):
        """Test creating ADGroup from LDAP entry for distribution group."""
        entry = {
            "dn": "CN=All_Staff,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["All_Staff"],
                "groupType": [2],  # Distribution, Global
            },
        }
        group = ADGroup.from_ldap_entry(entry)

        assert group.name == "All_Staff"
        assert group.category == GroupCategory.DISTRIBUTION
        assert group.scope == GroupScope.GLOBAL

    def test_from_ldap_entry_domain_local_scope(self):
        """Test creating ADGroup with Domain Local scope."""
        entry = {
            "dn": "CN=Local_Group,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["Local_Group"],
                "groupType": [-2147483644],  # Security, Domain Local
            },
        }
        group = ADGroup.from_ldap_entry(entry)

        assert group.scope == GroupScope.DOMAIN_LOCAL

    def test_from_ldap_entry_universal_scope(self):
        """Test creating ADGroup with Universal scope."""
        entry = {
            "dn": "CN=Universal_Group,OU=Groups,DC=example,DC=com",
            "attributes": {
                "cn": ["Universal_Group"],
                "groupType": [-2147483640],  # Security, Universal
            },
        }
        group = ADGroup.from_ldap_entry(entry)

        assert group.scope == GroupScope.UNIVERSAL


class TestADUser:
    """Tests for ADUser model."""

    def test_create_basic_user(self):
        """Test creating a basic ADUser."""
        user = ADUser(
            username="jdoe",
            distinguished_name="CN=John Doe,OU=Users,DC=example,DC=com",
        )
        assert user.username == "jdoe"
        assert user.distinguished_name == "CN=John Doe,OU=Users,DC=example,DC=com"
        assert user.display_name is None
        assert user.email is None
        assert user.enabled is True
        assert user.groups == []

    def test_create_user_with_all_fields(self):
        """Test creating an ADUser with all fields."""
        user = ADUser(
            username="jdoe",
            distinguished_name="CN=John Doe,OU=Users,DC=example,DC=com",
            display_name="John Doe",
            email="jdoe@example.com",
            enabled=True,
            groups=["CN=SQL_Admin,DC=example,DC=com"],
        )
        assert user.username == "jdoe"
        assert user.display_name == "John Doe"
        assert user.email == "jdoe@example.com"
        assert user.enabled is True
        assert len(user.groups) == 1

    def test_from_ldap_entry_enabled_user(self):
        """Test creating ADUser from LDAP entry for enabled user."""
        entry = {
            "dn": "CN=John Doe,OU=Users,DC=example,DC=com",
            "attributes": {
                "sAMAccountName": ["jdoe"],
                "displayName": ["John Doe"],
                "mail": ["jdoe@example.com"],
                "userAccountControl": [512],  # Normal account, enabled
            },
        }
        user = ADUser.from_ldap_entry(entry)

        assert user.username == "jdoe"
        assert user.distinguished_name == "CN=John Doe,OU=Users,DC=example,DC=com"
        assert user.display_name == "John Doe"
        assert user.email == "jdoe@example.com"
        assert user.enabled is True

    def test_from_ldap_entry_disabled_user(self):
        """Test creating ADUser from LDAP entry for disabled user."""
        entry = {
            "dn": "CN=Disabled User,OU=Users,DC=example,DC=com",
            "attributes": {
                "sAMAccountName": ["disabled"],
                "userAccountControl": [514],  # Normal account + ACCOUNTDISABLE
            },
        }
        user = ADUser.from_ldap_entry(entry)

        assert user.username == "disabled"
        assert user.enabled is False

    def test_from_ldap_entry_missing_optional_fields(self):
        """Test creating ADUser from LDAP entry with missing optional fields."""
        entry = {
            "dn": "CN=Minimal User,OU=Users,DC=example,DC=com",
            "attributes": {
                "sAMAccountName": ["minimal"],
            },
        }
        user = ADUser.from_ldap_entry(entry)

        assert user.username == "minimal"
        assert user.display_name is None
        assert user.email is None
        assert user.enabled is True  # Default when userAccountControl not present


class TestGroupCategory:
    """Tests for GroupCategory enum."""

    def test_security_value(self):
        """Test Security category value."""
        assert GroupCategory.SECURITY.value == "Security"

    def test_distribution_value(self):
        """Test Distribution category value."""
        assert GroupCategory.DISTRIBUTION.value == "Distribution"


class TestGroupScope:
    """Tests for GroupScope enum."""

    def test_scope_values(self):
        """Test GroupScope enum values."""
        assert GroupScope.DOMAIN_LOCAL.value == "DomainLocal"
        assert GroupScope.GLOBAL.value == "Global"
        assert GroupScope.UNIVERSAL.value == "Universal"
