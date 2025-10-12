"""
AdCopySurge Role-Based Access Control (RBAC) System
Comprehensive RBAC implementation with permissions, resources, hierarchical roles, and dynamic access control
"""

import os
import json
import redis
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from functools import wraps
import fnmatch
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    CAMPAIGN = "campaign"
    AD_CREATIVE = "ad_creative"
    ANALYTICS = "analytics"
    USER = "user"
    BILLING = "billing"
    SYSTEM = "system"
    ORGANIZATION = "organization"
    API = "api"
    REPORT = "report"
    INTEGRATION = "integration"

class Action(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"
    SHARE = "share"
    MANAGE = "manage"
    ADMIN = "admin"

class PermissionEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class Permission:
    """Individual permission definition"""
    id: str
    name: str
    description: str
    resource_type: ResourceType
    action: Action
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def matches(self, resource_type: ResourceType, action: Action, context: Dict[str, Any] = None) -> bool:
        """Check if permission matches the requested resource and action"""
        if self.resource_type != resource_type or self.action != action:
            return False
        
        # Check conditions if present
        if self.conditions and context:
            return self._evaluate_conditions(context)
        
        return True
    
    def _evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate permission conditions against context"""
        for condition_key, condition_value in self.conditions.items():
            context_value = context.get(condition_key)
            
            if isinstance(condition_value, dict):
                # Complex condition (e.g., {"operator": "in", "values": ["value1", "value2"]})
                operator = condition_value.get("operator", "eq")
                values = condition_value.get("values", [])
                
                if operator == "eq" and context_value != values[0]:
                    return False
                elif operator == "in" and context_value not in values:
                    return False
                elif operator == "not_in" and context_value in values:
                    return False
                elif operator == "gt" and context_value <= values[0]:
                    return False
                elif operator == "lt" and context_value >= values[0]:
                    return False
                elif operator == "regex" and not re.match(values[0], str(context_value)):
                    return False
            else:
                # Simple condition (direct value comparison)
                if context_value != condition_value:
                    return False
        
        return True

@dataclass
class Role:
    """Role definition with permissions and hierarchy"""
    id: str
    name: str
    description: str
    permissions: List[str] = field(default_factory=list)  # Permission IDs
    parent_roles: List[str] = field(default_factory=list)  # Parent role IDs for hierarchy
    is_system_role: bool = False
    is_active: bool = True
    organization_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourcePolicy:
    """Resource-specific access policy"""
    id: str
    resource_type: ResourceType
    resource_id: Optional[str]  # Specific resource ID or None for type-level policy
    resource_pattern: Optional[str]  # Pattern for matching multiple resources
    effect: PermissionEffect
    principals: List[str]  # User IDs or role IDs
    actions: List[Action]
    conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

@dataclass
class UserRoleAssignment:
    """User role assignment with context"""
    user_id: str
    role_id: str
    organization_id: Optional[str] = None
    resource_context: Dict[str, Any] = field(default_factory=dict)
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_by: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

@dataclass
class AccessRequest:
    """Access request for evaluation"""
    user_id: str
    resource_type: ResourceType
    resource_id: Optional[str]
    action: Action
    context: Dict[str, Any] = field(default_factory=dict)
    organization_id: Optional[str] = None

@dataclass
class AccessDecision:
    """Result of access evaluation"""
    allowed: bool
    reason: str
    matched_permissions: List[str] = field(default_factory=list)
    matched_policies: List[str] = field(default_factory=list)
    user_roles: List[str] = field(default_factory=list)
    evaluation_time_ms: float = 0.0

class RBACManager:
    """Comprehensive RBAC management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        
        # Initialize system permissions and roles
        self.system_permissions = self._load_system_permissions()
        self.system_roles = self._load_system_roles()
        
        # Cache settings
        self.cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes
        self.enable_cache = self.config.get('enable_cache', True)
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default RBAC configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/4'),
            'cache_ttl': 300,
            'enable_cache': True,
            'enable_audit_log': True,
            'max_role_hierarchy_depth': 10,
            'default_organization_id': 'default',
            'super_admin_role': 'super_admin',
            'enable_resource_policies': True,
            'enable_time_based_access': True
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for RBAC data"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for RBAC: {e}")
            return None
    
    def _load_system_permissions(self) -> Dict[str, Permission]:
        """Load system-defined permissions"""
        permissions = {}
        
        # Define comprehensive permissions for AdCopySurge
        permission_definitions = [
            # Campaign permissions
            ("campaign.create", "Create Campaigns", ResourceType.CAMPAIGN, Action.CREATE),
            ("campaign.read", "View Campaigns", ResourceType.CAMPAIGN, Action.READ),
            ("campaign.update", "Edit Campaigns", ResourceType.CAMPAIGN, Action.UPDATE),
            ("campaign.delete", "Delete Campaigns", ResourceType.CAMPAIGN, Action.DELETE),
            ("campaign.manage", "Manage Campaigns", ResourceType.CAMPAIGN, Action.MANAGE),
            
            # Ad Creative permissions
            ("ad_creative.create", "Create Ad Creatives", ResourceType.AD_CREATIVE, Action.CREATE),
            ("ad_creative.read", "View Ad Creatives", ResourceType.AD_CREATIVE, Action.READ),
            ("ad_creative.update", "Edit Ad Creatives", ResourceType.AD_CREATIVE, Action.UPDATE),
            ("ad_creative.delete", "Delete Ad Creatives", ResourceType.AD_CREATIVE, Action.DELETE),
            ("ad_creative.approve", "Approve Ad Creatives", ResourceType.AD_CREATIVE, Action.APPROVE),
            ("ad_creative.reject", "Reject Ad Creatives", ResourceType.AD_CREATIVE, Action.REJECT),
            
            # Analytics permissions
            ("analytics.read", "View Analytics", ResourceType.ANALYTICS, Action.READ),
            ("analytics.export", "Export Analytics", ResourceType.ANALYTICS, Action.EXPORT),
            ("analytics.manage", "Manage Analytics", ResourceType.ANALYTICS, Action.MANAGE),
            
            # User management permissions
            ("user.create", "Create Users", ResourceType.USER, Action.CREATE),
            ("user.read", "View Users", ResourceType.USER, Action.READ),
            ("user.update", "Edit Users", ResourceType.USER, Action.UPDATE),
            ("user.delete", "Delete Users", ResourceType.USER, Action.DELETE),
            ("user.manage", "Manage Users", ResourceType.USER, Action.MANAGE),
            
            # Billing permissions
            ("billing.read", "View Billing", ResourceType.BILLING, Action.READ),
            ("billing.update", "Update Billing", ResourceType.BILLING, Action.UPDATE),
            ("billing.manage", "Manage Billing", ResourceType.BILLING, Action.MANAGE),
            
            # System permissions
            ("system.read", "View System Info", ResourceType.SYSTEM, Action.READ),
            ("system.update", "Update System", ResourceType.SYSTEM, Action.UPDATE),
            ("system.manage", "Manage System", ResourceType.SYSTEM, Action.MANAGE),
            ("system.admin", "System Administration", ResourceType.SYSTEM, Action.ADMIN),
            
            # Organization permissions
            ("organization.create", "Create Organizations", ResourceType.ORGANIZATION, Action.CREATE),
            ("organization.read", "View Organizations", ResourceType.ORGANIZATION, Action.READ),
            ("organization.update", "Edit Organizations", ResourceType.ORGANIZATION, Action.UPDATE),
            ("organization.delete", "Delete Organizations", ResourceType.ORGANIZATION, Action.DELETE),
            ("organization.manage", "Manage Organizations", ResourceType.ORGANIZATION, Action.MANAGE),
            
            # API permissions
            ("api.read", "API Read Access", ResourceType.API, Action.READ),
            ("api.create", "API Write Access", ResourceType.API, Action.CREATE),
            ("api.manage", "API Management", ResourceType.API, Action.MANAGE),
            
            # Report permissions
            ("report.create", "Create Reports", ResourceType.REPORT, Action.CREATE),
            ("report.read", "View Reports", ResourceType.REPORT, Action.READ),
            ("report.update", "Edit Reports", ResourceType.REPORT, Action.UPDATE),
            ("report.delete", "Delete Reports", ResourceType.REPORT, Action.DELETE),
            ("report.export", "Export Reports", ResourceType.REPORT, Action.EXPORT),
            
            # Integration permissions
            ("integration.create", "Create Integrations", ResourceType.INTEGRATION, Action.CREATE),
            ("integration.read", "View Integrations", ResourceType.INTEGRATION, Action.READ),
            ("integration.update", "Edit Integrations", ResourceType.INTEGRATION, Action.UPDATE),
            ("integration.delete", "Delete Integrations", ResourceType.INTEGRATION, Action.DELETE),
            ("integration.manage", "Manage Integrations", ResourceType.INTEGRATION, Action.MANAGE),
        ]
        
        for perm_id, name, resource_type, action in permission_definitions:
            permissions[perm_id] = Permission(
                id=perm_id,
                name=name,
                description=f"Permission to {action.value} {resource_type.value}",
                resource_type=resource_type,
                action=action
            )
        
        return permissions
    
    def _load_system_roles(self) -> Dict[str, Role]:
        """Load system-defined roles"""
        roles = {}
        
        # Define system roles
        role_definitions = [
            {
                "id": "super_admin",
                "name": "Super Administrator",
                "description": "Full system access",
                "permissions": list(self.system_permissions.keys()),
                "is_system_role": True
            },
            {
                "id": "admin",
                "name": "Administrator",
                "description": "Organization administrator",
                "permissions": [
                    "campaign.manage", "ad_creative.manage", "analytics.manage",
                    "user.manage", "billing.manage", "report.manage",
                    "integration.manage"
                ],
                "is_system_role": True
            },
            {
                "id": "campaign_manager",
                "name": "Campaign Manager",
                "description": "Manage campaigns and ad creatives",
                "permissions": [
                    "campaign.create", "campaign.read", "campaign.update", "campaign.delete",
                    "ad_creative.create", "ad_creative.read", "ad_creative.update", "ad_creative.delete",
                    "analytics.read", "report.create", "report.read", "report.export"
                ],
                "is_system_role": True
            },
            {
                "id": "creative_manager",
                "name": "Creative Manager",
                "description": "Manage ad creatives and approve content",
                "permissions": [
                    "ad_creative.create", "ad_creative.read", "ad_creative.update", "ad_creative.delete",
                    "ad_creative.approve", "ad_creative.reject",
                    "analytics.read", "report.read"
                ],
                "is_system_role": True
            },
            {
                "id": "analyst",
                "name": "Analyst",
                "description": "View analytics and create reports",
                "permissions": [
                    "campaign.read", "ad_creative.read", "analytics.read", "analytics.export",
                    "report.create", "report.read", "report.update", "report.export"
                ],
                "is_system_role": True
            },
            {
                "id": "viewer",
                "name": "Viewer",
                "description": "Read-only access",
                "permissions": [
                    "campaign.read", "ad_creative.read", "analytics.read", "report.read"
                ],
                "is_system_role": True
            },
            {
                "id": "api_user",
                "name": "API User",
                "description": "API access for integrations",
                "permissions": [
                    "api.read", "api.create", "campaign.read", "campaign.create", "campaign.update",
                    "ad_creative.read", "ad_creative.create", "ad_creative.update"
                ],
                "is_system_role": True
            }
        ]
        
        for role_def in role_definitions:
            roles[role_def["id"]] = Role(**role_def)
        
        return roles
    
    # Permission Management
    
    def create_permission(self, permission: Permission) -> bool:
        """Create a new permission"""
        try:
            if self.redis_client:
                permission_data = asdict(permission)
                permission_data['resource_type'] = permission.resource_type.value
                permission_data['action'] = permission.action.value
                permission_data['created_at'] = permission.created_at.isoformat()
                
                key = f"rbac:permission:{permission.id}"
                self.redis_client.set(key, json.dumps(permission_data))
                
                # Add to permissions index
                self.redis_client.sadd("rbac:permissions", permission.id)
                
                logger.info(f"Created permission: {permission.id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating permission {permission.id}: {e}")
            return False
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID"""
        try:
            # Check system permissions first
            if permission_id in self.system_permissions:
                return self.system_permissions[permission_id]
            
            if self.redis_client:
                key = f"rbac:permission:{permission_id}"
                permission_data = self.redis_client.get(key)
                
                if permission_data:
                    data = json.loads(permission_data)
                    return Permission(
                        id=data['id'],
                        name=data['name'],
                        description=data['description'],
                        resource_type=ResourceType(data['resource_type']),
                        action=Action(data['action']),
                        conditions=data.get('conditions', {}),
                        created_at=datetime.fromisoformat(data['created_at'])
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting permission {permission_id}: {e}")
            return None
    
    def list_permissions(self, resource_type: Optional[ResourceType] = None) -> List[Permission]:
        """List all permissions, optionally filtered by resource type"""
        permissions = []
        
        try:
            # Add system permissions
            for perm in self.system_permissions.values():
                if resource_type is None or perm.resource_type == resource_type:
                    permissions.append(perm)
            
            # Add custom permissions from Redis
            if self.redis_client:
                permission_ids = self.redis_client.smembers("rbac:permissions")
                
                for perm_id in permission_ids:
                    perm = self.get_permission(perm_id)
                    if perm and (resource_type is None or perm.resource_type == resource_type):
                        permissions.append(perm)
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error listing permissions: {e}")
            return []
    
    # Role Management
    
    def create_role(self, role: Role) -> bool:
        """Create a new role"""
        try:
            if self.redis_client:
                role_data = asdict(role)
                role_data['created_at'] = role.created_at.isoformat()
                if role.updated_at:
                    role_data['updated_at'] = role.updated_at.isoformat()
                
                key = f"rbac:role:{role.id}"
                self.redis_client.set(key, json.dumps(role_data))
                
                # Add to roles index
                self.redis_client.sadd("rbac:roles", role.id)
                
                # Add to organization index if specified
                if role.organization_id:
                    self.redis_client.sadd(f"rbac:org_roles:{role.organization_id}", role.id)
                
                logger.info(f"Created role: {role.id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating role {role.id}: {e}")
            return False
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID"""
        try:
            # Check system roles first
            if role_id in self.system_roles:
                return self.system_roles[role_id]
            
            if self.redis_client:
                key = f"rbac:role:{role_id}"
                role_data = self.redis_client.get(key)
                
                if role_data:
                    data = json.loads(role_data)
                    return Role(
                        id=data['id'],
                        name=data['name'],
                        description=data['description'],
                        permissions=data.get('permissions', []),
                        parent_roles=data.get('parent_roles', []),
                        is_system_role=data.get('is_system_role', False),
                        is_active=data.get('is_active', True),
                        organization_id=data.get('organization_id'),
                        created_at=datetime.fromisoformat(data['created_at']),
                        updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
                        metadata=data.get('metadata', {})
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting role {role_id}: {e}")
            return None
    
    def update_role(self, role: Role) -> bool:
        """Update an existing role"""
        try:
            role.updated_at = datetime.now(timezone.utc)
            return self.create_role(role)  # Redis SET overwrites
            
        except Exception as e:
            logger.error(f"Error updating role {role.id}: {e}")
            return False
    
    def delete_role(self, role_id: str) -> bool:
        """Delete a role"""
        try:
            if self.redis_client:
                # Check if it's a system role
                if role_id in self.system_roles:
                    logger.error(f"Cannot delete system role: {role_id}")
                    return False
                
                # Remove role
                key = f"rbac:role:{role_id}"
                self.redis_client.delete(key)
                
                # Remove from indexes
                self.redis_client.srem("rbac:roles", role_id)
                
                # Remove from organization indexes
                org_keys = self.redis_client.keys("rbac:org_roles:*")
                for org_key in org_keys:
                    self.redis_client.srem(org_key, role_id)
                
                # Remove user assignments
                assignment_keys = self.redis_client.keys(f"rbac:user_role:*:{role_id}")
                for key in assignment_keys:
                    self.redis_client.delete(key)
                
                logger.info(f"Deleted role: {role_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {e}")
            return False
    
    def list_roles(self, organization_id: Optional[str] = None) -> List[Role]:
        """List all roles, optionally filtered by organization"""
        roles = []
        
        try:
            # Add system roles
            for role in self.system_roles.values():
                if role.is_active:
                    roles.append(role)
            
            # Add custom roles from Redis
            if self.redis_client:
                if organization_id:
                    role_ids = self.redis_client.smembers(f"rbac:org_roles:{organization_id}")
                else:
                    role_ids = self.redis_client.smembers("rbac:roles")
                
                for role_id in role_ids:
                    role = self.get_role(role_id)
                    if role and role.is_active:
                        roles.append(role)
            
            return roles
            
        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            return []
    
    # User Role Assignment
    
    def assign_role_to_user(self, assignment: UserRoleAssignment) -> bool:
        """Assign a role to a user"""
        try:
            if self.redis_client:
                assignment_data = asdict(assignment)
                assignment_data['assigned_at'] = assignment.assigned_at.isoformat()
                if assignment.expires_at:
                    assignment_data['expires_at'] = assignment.expires_at.isoformat()
                
                key = f"rbac:user_role:{assignment.user_id}:{assignment.role_id}"
                if assignment.organization_id:
                    key += f":{assignment.organization_id}"
                
                self.redis_client.set(key, json.dumps(assignment_data))
                
                # Add to user roles index
                user_roles_key = f"rbac:user_roles:{assignment.user_id}"
                self.redis_client.sadd(user_roles_key, assignment.role_id)
                
                # Invalidate cache
                self._invalidate_user_cache(assignment.user_id)
                
                logger.info(f"Assigned role {assignment.role_id} to user {assignment.user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error assigning role to user: {e}")
            return False
    
    def revoke_role_from_user(self, user_id: str, role_id: str, organization_id: Optional[str] = None) -> bool:
        """Revoke a role from a user"""
        try:
            if self.redis_client:
                key = f"rbac:user_role:{user_id}:{role_id}"
                if organization_id:
                    key += f":{organization_id}"
                
                self.redis_client.delete(key)
                
                # Remove from user roles index
                user_roles_key = f"rbac:user_roles:{user_id}"
                self.redis_client.srem(user_roles_key, role_id)
                
                # Invalidate cache
                self._invalidate_user_cache(user_id)
                
                logger.info(f"Revoked role {role_id} from user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error revoking role from user: {e}")
            return False
    
    def get_user_roles(self, user_id: str, organization_id: Optional[str] = None) -> List[Role]:
        """Get all roles assigned to a user"""
        try:
            if self.redis_client:
                # Get role IDs
                role_ids = self.redis_client.smembers(f"rbac:user_roles:{user_id}")
                
                roles = []
                for role_id in role_ids:
                    # Check if assignment is still valid
                    assignment_key = f"rbac:user_role:{user_id}:{role_id}"
                    if organization_id:
                        assignment_key += f":{organization_id}"
                    
                    assignment_data = self.redis_client.get(assignment_key)
                    if assignment_data:
                        assignment = json.loads(assignment_data)
                        
                        # Check if assignment is active and not expired
                        if assignment.get('is_active', True):
                            expires_at = assignment.get('expires_at')
                            if not expires_at or datetime.fromisoformat(expires_at) > datetime.now(timezone.utc):
                                role = self.get_role(role_id)
                                if role:
                                    roles.append(role)
                
                return roles
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting user roles for {user_id}: {e}")
            return []
    
    def get_user_permissions(self, user_id: str, organization_id: Optional[str] = None) -> Set[Permission]:
        """Get all effective permissions for a user"""
        permissions = set()
        
        try:
            # Check cache first
            cache_key = f"rbac:user_permissions:{user_id}"
            if organization_id:
                cache_key += f":{organization_id}"
            
            if self.enable_cache and self.redis_client:
                cached_permissions = self.redis_client.get(cache_key)
                if cached_permissions:
                    perm_ids = json.loads(cached_permissions)
                    for perm_id in perm_ids:
                        perm = self.get_permission(perm_id)
                        if perm:
                            permissions.add(perm)
                    return permissions
            
            # Get user roles
            user_roles = self.get_user_roles(user_id, organization_id)
            
            # Collect permissions from roles (including hierarchy)
            processed_roles = set()
            for role in user_roles:
                self._collect_role_permissions(role, permissions, processed_roles)
            
            # Cache the result
            if self.enable_cache and self.redis_client:
                perm_ids = [perm.id for perm in permissions]
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(perm_ids))
            
            return permissions
            
        except Exception as e:
            logger.error(f"Error getting user permissions for {user_id}: {e}")
            return set()
    
    def _collect_role_permissions(self, role: Role, permissions: Set[Permission], processed_roles: Set[str], depth: int = 0):
        """Recursively collect permissions from role hierarchy"""
        if depth > self.config.get('max_role_hierarchy_depth', 10):
            logger.warning(f"Maximum role hierarchy depth exceeded for role {role.id}")
            return
        
        if role.id in processed_roles:
            return  # Avoid circular dependencies
        
        processed_roles.add(role.id)
        
        # Add direct permissions
        for perm_id in role.permissions:
            perm = self.get_permission(perm_id)
            if perm:
                permissions.add(perm)
        
        # Add parent role permissions
        for parent_role_id in role.parent_roles:
            parent_role = self.get_role(parent_role_id)
            if parent_role and parent_role.is_active:
                self._collect_role_permissions(parent_role, permissions, processed_roles, depth + 1)
    
    # Access Control Evaluation
    
    def check_access(self, request: AccessRequest) -> AccessDecision:
        """Check if access should be granted for the request"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Get user permissions
            user_permissions = self.get_user_permissions(request.user_id, request.organization_id)
            
            # Get user roles for context
            user_roles = self.get_user_roles(request.user_id, request.organization_id)
            user_role_ids = [role.id for role in user_roles]
            
            # Check direct permissions
            matched_permissions = []
            for permission in user_permissions:
                if permission.matches(request.resource_type, request.action, request.context):
                    matched_permissions.append(permission.id)
            
            # Check resource policies if enabled
            matched_policies = []
            if self.config.get('enable_resource_policies'):
                matched_policies = self._check_resource_policies(request, user_role_ids)
            
            # Make access decision
            allowed = len(matched_permissions) > 0 or len(matched_policies) > 0
            
            # Generate reason
            if allowed:
                reason = f"Access granted via permissions: {', '.join(matched_permissions[:3])}"
                if matched_policies:
                    reason += f" and policies: {', '.join(matched_policies[:3])}"
            else:
                reason = f"No matching permissions for {request.action.value} on {request.resource_type.value}"
            
            # Calculate evaluation time
            end_time = datetime.now(timezone.utc)
            evaluation_time = (end_time - start_time).total_seconds() * 1000
            
            decision = AccessDecision(
                allowed=allowed,
                reason=reason,
                matched_permissions=matched_permissions,
                matched_policies=matched_policies,
                user_roles=user_role_ids,
                evaluation_time_ms=evaluation_time
            )
            
            # Log access decision if enabled
            if self.config.get('enable_audit_log'):
                self._log_access_decision(request, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Error checking access for user {request.user_id}: {e}")
            return AccessDecision(
                allowed=False,
                reason=f"Error during access evaluation: {str(e)}",
                evaluation_time_ms=0.0
            )
    
    def _check_resource_policies(self, request: AccessRequest, user_role_ids: List[str]) -> List[str]:
        """Check resource-specific policies"""
        matched_policies = []
        
        try:
            if self.redis_client:
                # Get policies for resource type
                policy_keys = self.redis_client.keys(f"rbac:policy:{request.resource_type.value}:*")
                
                for policy_key in policy_keys:
                    policy_data = self.redis_client.get(policy_key)
                    if policy_data:
                        policy = self._deserialize_resource_policy(json.loads(policy_data))
                        
                        if self._policy_matches_request(policy, request, user_role_ids):
                            matched_policies.append(policy.id)
            
            return matched_policies
            
        except Exception as e:
            logger.error(f"Error checking resource policies: {e}")
            return []
    
    def _policy_matches_request(self, policy: ResourcePolicy, request: AccessRequest, user_role_ids: List[str]) -> bool:
        """Check if a policy matches the request"""
        # Check if policy is expired
        if policy.expires_at and policy.expires_at < datetime.now(timezone.utc):
            return False
        
        # Check action
        if request.action not in policy.actions:
            return False
        
        # Check resource match
        if policy.resource_id and policy.resource_id != request.resource_id:
            return False
        
        if policy.resource_pattern and request.resource_id:
            if not fnmatch.fnmatch(request.resource_id, policy.resource_pattern):
                return False
        
        # Check principals (user or roles)
        principal_match = False
        if request.user_id in policy.principals:
            principal_match = True
        else:
            for role_id in user_role_ids:
                if role_id in policy.principals:
                    principal_match = True
                    break
        
        if not principal_match:
            return False
        
        # Check conditions
        if policy.conditions:
            for condition_key, condition_value in policy.conditions.items():
                if not self._evaluate_policy_condition(condition_key, condition_value, request.context):
                    return False
        
        return policy.effect == PermissionEffect.ALLOW
    
    def _evaluate_policy_condition(self, condition_key: str, condition_value: Any, context: Dict[str, Any]) -> bool:
        """Evaluate a policy condition"""
        context_value = context.get(condition_key)
        
        if isinstance(condition_value, dict):
            operator = condition_value.get("operator", "eq")
            values = condition_value.get("values", [])
            
            if operator == "eq":
                return context_value == values[0] if values else False
            elif operator == "in":
                return context_value in values
            elif operator == "not_in":
                return context_value not in values
            elif operator == "gt":
                return context_value > values[0] if values else False
            elif operator == "lt":
                return context_value < values[0] if values else False
            elif operator == "regex":
                return bool(re.match(values[0], str(context_value))) if values else False
        else:
            return context_value == condition_value
        
        return False
    
    # Utility Methods
    
    def _invalidate_user_cache(self, user_id: str):
        """Invalidate cached permissions for a user"""
        if self.redis_client:
            cache_keys = self.redis_client.keys(f"rbac:user_permissions:{user_id}*")
            if cache_keys:
                self.redis_client.delete(*cache_keys)
    
    def _log_access_decision(self, request: AccessRequest, decision: AccessDecision):
        """Log access decision for audit purposes"""
        try:
            if self.redis_client:
                log_entry = {
                    'user_id': request.user_id,
                    'resource_type': request.resource_type.value,
                    'resource_id': request.resource_id,
                    'action': request.action.value,
                    'organization_id': request.organization_id,
                    'allowed': decision.allowed,
                    'reason': decision.reason,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'evaluation_time_ms': decision.evaluation_time_ms
                }
                
                # Store with TTL (e.g., 90 days)
                key = f"rbac:audit:{datetime.now(timezone.utc).strftime('%Y%m%d')}:{secrets.token_urlsafe(8)}"
                self.redis_client.setex(key, 86400 * 90, json.dumps(log_entry))
                
        except Exception as e:
            logger.error(f"Error logging access decision: {e}")
    
    def _deserialize_resource_policy(self, data: Dict[str, Any]) -> ResourcePolicy:
        """Deserialize resource policy from stored data"""
        return ResourcePolicy(
            id=data['id'],
            resource_type=ResourceType(data['resource_type']),
            resource_id=data.get('resource_id'),
            resource_pattern=data.get('resource_pattern'),
            effect=PermissionEffect(data['effect']),
            principals=data['principals'],
            actions=[Action(action) for action in data['actions']],
            conditions=data.get('conditions', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )


# Decorators for access control

def require_permission(resource_type: ResourceType, action: Action, resource_id_param: str = None):
    """Decorator to require specific permission for a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id and resource_id from function parameters
            # This is a simplified implementation - in practice, you'd extract from request context
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            resource_id = kwargs.get(resource_id_param) if resource_id_param else None
            
            if not user_id:
                raise PermissionError("User ID not provided")
            
            # Create RBAC manager and check access
            rbac = RBACManager()
            request = AccessRequest(
                user_id=str(user_id),
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                context=kwargs
            )
            
            decision = rbac.check_access(request)
            if not decision.allowed:
                raise PermissionError(f"Access denied: {decision.reason}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(role_id: str):
    """Decorator to require specific role for a function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or (args[0] if args else None)
            
            if not user_id:
                raise PermissionError("User ID not provided")
            
            rbac = RBACManager()
            user_roles = rbac.get_user_roles(str(user_id))
            user_role_ids = [role.id for role in user_roles]
            
            if role_id not in user_role_ids:
                raise PermissionError(f"Role '{role_id}' required")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Utility functions

def create_rbac_manager(config: Dict[str, Any] = None) -> RBACManager:
    """Factory function to create RBAC manager"""
    return RBACManager(config)