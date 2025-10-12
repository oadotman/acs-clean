"""
AdCopySurge GDPR Compliance System
Comprehensive GDPR compliance implementation with data mapping, consent management, user rights, and privacy controls
"""

import os
import json
import uuid
import redis
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from cryptography.fernet import Fernet
import base64
import hashlib
import requests
import asyncio
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCategory(Enum):
    PERSONAL_IDENTIFIERS = "personal_identifiers"
    CONTACT_INFORMATION = "contact_information"
    FINANCIAL_DATA = "financial_data"
    BEHAVIORAL_DATA = "behavioral_data"
    TECHNICAL_DATA = "technical_data"
    MARKETING_DATA = "marketing_data"
    ANALYTICS_DATA = "analytics_data"
    LOCATION_DATA = "location_data"
    BIOMETRIC_DATA = "biometric_data"
    HEALTH_DATA = "health_data"
    SENSITIVE_DATA = "sensitive_data"

class ProcessingPurpose(Enum):
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    FRAUD_PREVENTION = "fraud_prevention"
    LEGAL_COMPLIANCE = "legal_compliance"
    CUSTOMER_SUPPORT = "customer_support"
    SECURITY = "security"
    RESEARCH = "research"
    ADVERTISING = "advertising"
    PERSONALIZATION = "personalization"

class LegalBasis(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class ConsentStatus(Enum):
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"
    REFUSED = "refused"

class DataSubjectRight(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICT_PROCESSING = "restrict_processing"
    DATA_PORTABILITY = "data_portability"
    OBJECT = "object"
    OBJECT_AUTOMATED_PROCESSING = "object_automated_processing"

class RequestStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PARTIALLY_FULFILLED = "partially_fulfilled"

@dataclass
class DataElement:
    """Individual data element definition"""
    field_name: str
    data_category: DataCategory
    description: str
    is_personal: bool
    is_sensitive: bool
    retention_period_days: Optional[int] = None
    source_system: Optional[str] = None
    processing_purposes: List[ProcessingPurpose] = field(default_factory=list)
    legal_basis: List[LegalBasis] = field(default_factory=list)
    third_party_sharing: bool = False
    encryption_required: bool = False
    anonymization_possible: bool = True

@dataclass
class DataMap:
    """Data mapping for GDPR compliance"""
    id: str
    name: str
    description: str
    data_controller: str
    data_processor: Optional[str] = None
    data_elements: List[DataElement] = field(default_factory=list)
    processing_purposes: List[ProcessingPurpose] = field(default_factory=list)
    legal_basis: LegalBasis = LegalBasis.CONSENT
    retention_policy: Dict[str, Any] = field(default_factory=dict)
    third_party_transfers: List[Dict[str, Any]] = field(default_factory=list)
    security_measures: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

@dataclass
class ConsentRecord:
    """Individual consent record"""
    id: str
    user_id: str
    purpose: ProcessingPurpose
    status: ConsentStatus
    given_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    consent_method: Optional[str] = None  # e.g., "web_form", "email_opt_in", "api"
    consent_text: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if consent is currently valid"""
        if self.status != ConsentStatus.GIVEN:
            return False
        
        if self.expires_at and self.expires_at < datetime.now(timezone.utc):
            return False
        
        return True

@dataclass
class DataSubjectRequest:
    """Data subject rights request"""
    id: str
    user_id: str
    request_type: DataSubjectRight
    status: RequestStatus
    description: Optional[str] = None
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    processor_notes: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    verification_method: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Set deadline (30 days from submission as per GDPR)
        if not self.deadline:
            self.deadline = self.submitted_at + timedelta(days=30)

@dataclass
class DataBreachIncident:
    """Data breach incident record"""
    id: str
    title: str
    description: str
    discovered_at: datetime
    reported_at: Optional[datetime] = None
    affected_records_count: int = 0
    affected_data_categories: List[DataCategory] = field(default_factory=list)
    breach_type: str = ""  # e.g., "unauthorized_access", "data_loss", "system_breach"
    severity: str = "medium"  # low, medium, high, critical
    notification_required: bool = False
    supervisory_authority_notified: bool = False
    individuals_notified: bool = False
    containment_measures: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)
    status: str = "open"  # open, investigating, contained, closed
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def notification_deadline(self) -> datetime:
        """72-hour notification deadline for supervisory authority"""
        return self.discovered_at + timedelta(hours=72)
    
    @property
    def is_notification_overdue(self) -> bool:
        """Check if 72-hour notification deadline has passed"""
        return datetime.now(timezone.utc) > self.notification_deadline and not self.supervisory_authority_notified

class GDPRComplianceManager:
    """Comprehensive GDPR compliance management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.redis_client = self._init_redis()
        self.encryption_key = self._get_encryption_key()
        
        # Initialize data maps
        self.data_maps = self._load_data_maps()
        
        # GDPR settings
        self.consent_expiry_days = self.config.get('consent_expiry_days', 365)
        self.data_retention_default_days = self.config.get('data_retention_default_days', 730)  # 2 years
        self.request_processing_days = self.config.get('request_processing_days', 30)
        self.breach_notification_hours = self.config.get('breach_notification_hours', 72)
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default GDPR configuration"""
        return {
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/5'),
            'encryption_key': os.getenv('GDPR_ENCRYPTION_KEY'),
            'consent_expiry_days': 365,
            'data_retention_default_days': 730,
            'request_processing_days': 30,
            'breach_notification_hours': 72,
            'data_controller': {
                'name': 'AdCopySurge Inc.',
                'email': 'support@adcopysurge.com',
                'address': '123 Business St, City, Country',
                'phone': '+234-810-674-0579'
            },
            'supervisory_authority': {
                'name': 'Data Protection Authority',
                'email': 'report@dataprotection.gov',
                'phone': '+1-555-0100'
            },
            'enable_audit_log': True,
            'enable_automated_deletion': True,
            'enable_consent_management': True,
            'enable_breach_detection': True
        }
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for GDPR data"""
        try:
            client = redis.from_url(self.config['redis_url'], decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            logger.warning(f"Redis not available for GDPR: {e}")
            return None
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for sensitive GDPR data"""
        key_str = self.config.get('encryption_key')
        if key_str:
            return base64.urlsafe_b64decode(key_str.encode())
        else:
            key = Fernet.generate_key()
            logger.warning("GDPR encryption key not configured, using generated key (not persistent)")
            return key
    
    def _load_data_maps(self) -> Dict[str, DataMap]:
        """Load system data maps"""
        data_maps = {}
        
        # Define AdCopySurge data map
        adcopysurge_map = DataMap(
            id="adcopysurge_main",
            name="AdCopySurge Main Application",
            description="Primary data processing for AdCopySurge advertising platform",
            data_controller="AdCopySurge Inc.",
            data_elements=[
                # User Identity Data
                DataElement(
                    field_name="user_id",
                    data_category=DataCategory.PERSONAL_IDENTIFIERS,
                    description="Unique user identifier",
                    is_personal=True,
                    is_sensitive=False,
                    processing_purposes=[ProcessingPurpose.SERVICE_PROVISION, ProcessingPurpose.ANALYTICS],
                    legal_basis=[LegalBasis.CONTRACT]
                ),
                DataElement(
                    field_name="email",
                    data_category=DataCategory.CONTACT_INFORMATION,
                    description="User email address",
                    is_personal=True,
                    is_sensitive=False,
                    processing_purposes=[ProcessingPurpose.SERVICE_PROVISION, ProcessingPurpose.MARKETING],
                    legal_basis=[LegalBasis.CONTRACT, LegalBasis.CONSENT],
                    encryption_required=True
                ),
                DataElement(
                    field_name="first_name",
                    data_category=DataCategory.PERSONAL_IDENTIFIERS,
                    description="User first name",
                    is_personal=True,
                    is_sensitive=False,
                    processing_purposes=[ProcessingPurpose.SERVICE_PROVISION, ProcessingPurpose.PERSONALIZATION],
                    legal_basis=[LegalBasis.CONTRACT]
                ),
                DataElement(
                    field_name="last_name",
                    data_category=DataCategory.PERSONAL_IDENTIFIERS,
                    description="User last name",
                    is_personal=True,
                    is_sensitive=False,
                    processing_purposes=[ProcessingPurpose.SERVICE_PROVISION],
                    legal_basis=[LegalBasis.CONTRACT]
                ),
                # Technical Data
                DataElement(
                    field_name="ip_address",
                    data_category=DataCategory.TECHNICAL_DATA,
                    description="User IP address",
                    is_personal=True,
                    is_sensitive=False,
                    retention_period_days=90,
                    processing_purposes=[ProcessingPurpose.SECURITY, ProcessingPurpose.FRAUD_PREVENTION],
                    legal_basis=[LegalBasis.LEGITIMATE_INTERESTS]
                ),
                DataElement(
                    field_name="user_agent",
                    data_category=DataCategory.TECHNICAL_DATA,
                    description="Browser user agent string",
                    is_personal=False,
                    is_sensitive=False,
                    retention_period_days=90,
                    processing_purposes=[ProcessingPurpose.ANALYTICS, ProcessingPurpose.SECURITY],
                    legal_basis=[LegalBasis.LEGITIMATE_INTERESTS]
                ),
                # Behavioral Data
                DataElement(
                    field_name="campaign_interactions",
                    data_category=DataCategory.BEHAVIORAL_DATA,
                    description="User interactions with advertising campaigns",
                    is_personal=True,
                    is_sensitive=False,
                    retention_period_days=730,
                    processing_purposes=[ProcessingPurpose.ANALYTICS, ProcessingPurpose.ADVERTISING, ProcessingPurpose.PERSONALIZATION],
                    legal_basis=[LegalBasis.CONSENT, LegalBasis.LEGITIMATE_INTERESTS],
                    anonymization_possible=True
                ),
                # Financial Data
                DataElement(
                    field_name="billing_information",
                    data_category=DataCategory.FINANCIAL_DATA,
                    description="User billing and payment information",
                    is_personal=True,
                    is_sensitive=True,
                    retention_period_days=2555,  # 7 years for tax purposes
                    processing_purposes=[ProcessingPurpose.SERVICE_PROVISION, ProcessingPurpose.LEGAL_COMPLIANCE],
                    legal_basis=[LegalBasis.CONTRACT, LegalBasis.LEGAL_OBLIGATION],
                    encryption_required=True,
                    third_party_sharing=True  # Payment processors
                ),
            ],
            processing_purposes=[
                ProcessingPurpose.SERVICE_PROVISION,
                ProcessingPurpose.MARKETING,
                ProcessingPurpose.ANALYTICS,
                ProcessingPurpose.FRAUD_PREVENTION,
                ProcessingPurpose.CUSTOMER_SUPPORT
            ],
            legal_basis=LegalBasis.CONTRACT,
            retention_policy={
                "default_retention_days": 730,
                "categories": {
                    "technical_data": 90,
                    "behavioral_data": 730,
                    "financial_data": 2555
                }
            },
            third_party_transfers=[
                {
                    "recipient": "Analytics Provider",
                    "country": "United States",
                    "data_categories": ["behavioral_data", "technical_data"],
                    "safeguards": ["Standard Contractual Clauses", "Privacy Shield (if applicable)"],
                    "purpose": "Analytics and reporting"
                },
                {
                    "recipient": "Payment Processor",
                    "country": "Various",
                    "data_categories": ["financial_data", "contact_information"],
                    "safeguards": ["PCI DSS Compliance", "Standard Contractual Clauses"],
                    "purpose": "Payment processing"
                }
            ],
            security_measures=[
                "Encryption at rest and in transit",
                "Access controls and authentication",
                "Regular security audits",
                "Data pseudonymization",
                "Secure backup procedures",
                "Incident response plan"
            ]
        )
        
        data_maps["adcopysurge_main"] = adcopysurge_map
        return data_maps
    
    # Consent Management
    
    def record_consent(self, consent: ConsentRecord) -> bool:
        """Record user consent"""
        try:
            if self.redis_client:
                # Set expiry date if not provided
                if not consent.expires_at and self.consent_expiry_days > 0:
                    consent.expires_at = datetime.now(timezone.utc) + timedelta(days=self.consent_expiry_days)
                
                consent_data = asdict(consent)
                consent_data['given_at'] = consent.given_at.isoformat() if consent.given_at else None
                consent_data['withdrawn_at'] = consent.withdrawn_at.isoformat() if consent.withdrawn_at else None
                consent_data['expires_at'] = consent.expires_at.isoformat() if consent.expires_at else None
                consent_data['status'] = consent.status.value
                consent_data['purpose'] = consent.purpose.value
                
                # Store consent record
                key = f"gdpr:consent:{consent.user_id}:{consent.purpose.value}"
                self.redis_client.set(key, json.dumps(consent_data))
                
                # Add to user's consent index
                self.redis_client.sadd(f"gdpr:user_consents:{consent.user_id}", consent.purpose.value)
                
                # Log consent action
                self._log_privacy_action("consent_recorded", {
                    'user_id': consent.user_id,
                    'purpose': consent.purpose.value,
                    'status': consent.status.value,
                    'method': consent.consent_method,
                    'ip_address': consent.ip_address
                })
                
                logger.info(f"Recorded consent for user {consent.user_id}, purpose {consent.purpose.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            return False
    
    def withdraw_consent(self, user_id: str, purpose: ProcessingPurpose, reason: str = None) -> bool:
        """Withdraw user consent"""
        try:
            if self.redis_client:
                key = f"gdpr:consent:{user_id}:{purpose.value}"
                consent_data = self.redis_client.get(key)
                
                if consent_data:
                    consent = json.loads(consent_data)
                    consent['status'] = ConsentStatus.WITHDRAWN.value
                    consent['withdrawn_at'] = datetime.now(timezone.utc).isoformat()
                    
                    if reason:
                        consent['metadata']['withdrawal_reason'] = reason
                    
                    # Update consent record
                    self.redis_client.set(key, json.dumps(consent))
                    
                    # Trigger data processing restrictions
                    self._apply_consent_withdrawal(user_id, purpose)
                    
                    # Log withdrawal
                    self._log_privacy_action("consent_withdrawn", {
                        'user_id': user_id,
                        'purpose': purpose.value,
                        'reason': reason
                    })
                    
                    logger.info(f"Consent withdrawn for user {user_id}, purpose {purpose.value}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error withdrawing consent: {e}")
            return False
    
    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get all consent records for a user"""
        consents = []
        
        try:
            if self.redis_client:
                consent_purposes = self.redis_client.smembers(f"gdpr:user_consents:{user_id}")
                
                for purpose in consent_purposes:
                    key = f"gdpr:consent:{user_id}:{purpose}"
                    consent_data = self.redis_client.get(key)
                    
                    if consent_data:
                        data = json.loads(consent_data)
                        consent = ConsentRecord(
                            id=data['id'],
                            user_id=data['user_id'],
                            purpose=ProcessingPurpose(data['purpose']),
                            status=ConsentStatus(data['status']),
                            given_at=datetime.fromisoformat(data['given_at']) if data.get('given_at') else None,
                            withdrawn_at=datetime.fromisoformat(data['withdrawn_at']) if data.get('withdrawn_at') else None,
                            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
                            consent_method=data.get('consent_method'),
                            consent_text=data.get('consent_text'),
                            ip_address=data.get('ip_address'),
                            user_agent=data.get('user_agent'),
                            metadata=data.get('metadata', {})
                        )
                        consents.append(consent)
            
            return consents
            
        except Exception as e:
            logger.error(f"Error getting user consents for {user_id}: {e}")
            return []
    
    def check_consent_validity(self, user_id: str, purpose: ProcessingPurpose) -> bool:
        """Check if user has valid consent for a specific purpose"""
        try:
            if self.redis_client:
                key = f"gdpr:consent:{user_id}:{purpose.value}"
                consent_data = self.redis_client.get(key)
                
                if consent_data:
                    data = json.loads(consent_data)
                    
                    # Check status
                    if data['status'] != ConsentStatus.GIVEN.value:
                        return False
                    
                    # Check expiry
                    if data.get('expires_at'):
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if expires_at < datetime.now(timezone.utc):
                            return False
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking consent validity: {e}")
            return False
    
    # Data Subject Rights
    
    def submit_data_subject_request(self, request: DataSubjectRequest) -> bool:
        """Submit a data subject rights request"""
        try:
            if self.redis_client:
                request_data = asdict(request)
                request_data['request_type'] = request.request_type.value
                request_data['status'] = request.status.value
                request_data['submitted_at'] = request.submitted_at.isoformat()
                request_data['deadline'] = request.deadline.isoformat() if request.deadline else None
                request_data['completed_at'] = request.completed_at.isoformat() if request.completed_at else None
                
                # Store request
                key = f"gdpr:request:{request.id}"
                self.redis_client.set(key, json.dumps(request_data))
                
                # Add to user's requests index
                self.redis_client.sadd(f"gdpr:user_requests:{request.user_id}", request.id)
                
                # Add to processing queue
                self.redis_client.lpush("gdpr:request_queue", request.id)
                
                # Send notification
                self._send_request_notification(request)
                
                # Log request submission
                self._log_privacy_action("data_subject_request_submitted", {
                    'request_id': request.id,
                    'user_id': request.user_id,
                    'request_type': request.request_type.value,
                    'verification_method': request.verification_method
                })
                
                logger.info(f"Data subject request submitted: {request.id} ({request.request_type.value})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error submitting data subject request: {e}")
            return False
    
    def process_access_request(self, request_id: str) -> Dict[str, Any]:
        """Process data subject access request (Article 15)"""
        try:
            request = self._get_data_subject_request(request_id)
            if not request or request.request_type != DataSubjectRight.ACCESS:
                raise ValueError("Invalid access request")
            
            user_id = request.user_id
            
            # Collect all personal data for the user
            user_data = {
                'request_id': request_id,
                'user_id': user_id,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'data_controller': self.config['data_controller'],
                'personal_data': {},
                'processing_activities': [],
                'consent_records': [],
                'data_sources': []
            }
            
            # Get consent records
            consents = self.get_user_consents(user_id)
            user_data['consent_records'] = [asdict(consent) for consent in consents]
            
            # Collect data from each data map
            for data_map in self.data_maps.values():
                map_data = self._extract_user_data_from_map(user_id, data_map)
                if map_data:
                    user_data['personal_data'][data_map.id] = map_data
                    user_data['data_sources'].append({
                        'source': data_map.name,
                        'description': data_map.description,
                        'data_controller': data_map.data_controller,
                        'retention_policy': data_map.retention_policy
                    })
                    
                    # Add processing activities
                    for purpose in data_map.processing_purposes:
                        user_data['processing_activities'].append({
                            'purpose': purpose.value,
                            'legal_basis': data_map.legal_basis.value,
                            'data_categories': [element.data_category.value for element in data_map.data_elements]
                        })
            
            # Update request status
            self._update_request_status(request_id, RequestStatus.COMPLETED, user_data)
            
            logger.info(f"Access request processed: {request_id}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error processing access request {request_id}: {e}")
            self._update_request_status(request_id, RequestStatus.REJECTED, {'error': str(e)})
            raise
    
    def process_erasure_request(self, request_id: str) -> bool:
        """Process data subject erasure request (Article 17 - Right to be forgotten)"""
        try:
            request = self._get_data_subject_request(request_id)
            if not request or request.request_type != DataSubjectRight.ERASURE:
                raise ValueError("Invalid erasure request")
            
            user_id = request.user_id
            
            # Check if erasure is legally possible
            erasure_blocks = self._check_erasure_restrictions(user_id)
            if erasure_blocks:
                self._update_request_status(request_id, RequestStatus.REJECTED, {
                    'reason': 'Erasure not possible due to legal restrictions',
                    'restrictions': erasure_blocks
                })
                return False
            
            # Perform data erasure
            erasure_results = []
            
            for data_map in self.data_maps.values():
                try:
                    result = self._erase_user_data_from_map(user_id, data_map)
                    erasure_results.append({
                        'data_source': data_map.name,
                        'status': 'success' if result else 'failed',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                except Exception as e:
                    erasure_results.append({
                        'data_source': data_map.name,
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
            
            # Remove consent records
            self._erase_user_consents(user_id)
            
            # Update request status
            self._update_request_status(request_id, RequestStatus.COMPLETED, {
                'erasure_results': erasure_results,
                'completed_at': datetime.now(timezone.utc).isoformat()
            })
            
            # Log erasure action
            self._log_privacy_action("data_erasure_completed", {
                'request_id': request_id,
                'user_id': user_id,
                'erasure_results': erasure_results
            })
            
            logger.info(f"Erasure request processed: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing erasure request {request_id}: {e}")
            self._update_request_status(request_id, RequestStatus.REJECTED, {'error': str(e)})
            return False
    
    def process_portability_request(self, request_id: str) -> Dict[str, Any]:
        """Process data portability request (Article 20)"""
        try:
            request = self._get_data_subject_request(request_id)
            if not request or request.request_type != DataSubjectRight.DATA_PORTABILITY:
                raise ValueError("Invalid portability request")
            
            user_id = request.user_id
            
            # Collect portable data (only data processed based on consent or contract)
            portable_data = {
                'request_id': request_id,
                'user_id': user_id,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'format': 'JSON',
                'data_controller': self.config['data_controller'],
                'portable_data': {}
            }
            
            for data_map in self.data_maps.values():
                # Only include data processed based on consent or contract
                if data_map.legal_basis in [LegalBasis.CONSENT, LegalBasis.CONTRACT]:
                    map_data = self._extract_portable_data_from_map(user_id, data_map)
                    if map_data:
                        portable_data['portable_data'][data_map.id] = map_data
            
            # Update request status
            self._update_request_status(request_id, RequestStatus.COMPLETED, portable_data)
            
            logger.info(f"Portability request processed: {request_id}")
            return portable_data
            
        except Exception as e:
            logger.error(f"Error processing portability request {request_id}: {e}")
            self._update_request_status(request_id, RequestStatus.REJECTED, {'error': str(e)})
            raise
    
    # Data Breach Management
    
    def report_data_breach(self, breach: DataBreachIncident) -> bool:
        """Report a data breach incident"""
        try:
            if self.redis_client:
                breach_data = asdict(breach)
                breach_data['discovered_at'] = breach.discovered_at.isoformat()
                breach_data['reported_at'] = breach.reported_at.isoformat() if breach.reported_at else None
                breach_data['created_at'] = breach.created_at.isoformat()
                breach_data['affected_data_categories'] = [cat.value for cat in breach.affected_data_categories]
                
                # Store breach incident
                key = f"gdpr:breach:{breach.id}"
                self.redis_client.set(key, json.dumps(breach_data))
                
                # Add to breaches index
                self.redis_client.sadd("gdpr:breaches", breach.id)
                
                # Check if notification is required
                if breach.notification_required:
                    self._schedule_breach_notifications(breach)
                
                # Log breach
                self._log_privacy_action("data_breach_reported", {
                    'breach_id': breach.id,
                    'severity': breach.severity,
                    'affected_records': breach.affected_records_count,
                    'notification_required': breach.notification_required
                })
                
                logger.warning(f"Data breach reported: {breach.id} (severity: {breach.severity})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error reporting data breach: {e}")
            return False
    
    def check_overdue_breach_notifications(self) -> List[DataBreachIncident]:
        """Check for breaches that require overdue notifications"""
        overdue_breaches = []
        
        try:
            if self.redis_client:
                breach_ids = self.redis_client.smembers("gdpr:breaches")
                
                for breach_id in breach_ids:
                    key = f"gdpr:breach:{breach_id}"
                    breach_data = self.redis_client.get(key)
                    
                    if breach_data:
                        data = json.loads(breach_data)
                        
                        if (data['notification_required'] and 
                            not data['supervisory_authority_notified']):
                            
                            discovered_at = datetime.fromisoformat(data['discovered_at'])
                            notification_deadline = discovered_at + timedelta(hours=self.breach_notification_hours)
                            
                            if datetime.now(timezone.utc) > notification_deadline:
                                breach = self._deserialize_breach(data)
                                overdue_breaches.append(breach)
            
            return overdue_breaches
            
        except Exception as e:
            logger.error(f"Error checking overdue breach notifications: {e}")
            return []
    
    # Helper Methods
    
    def _apply_consent_withdrawal(self, user_id: str, purpose: ProcessingPurpose):
        """Apply data processing restrictions after consent withdrawal"""
        try:
            # Mark data for restriction or deletion based on purpose
            restriction_data = {
                'user_id': user_id,
                'purpose': purpose.value,
                'restricted_at': datetime.now(timezone.utc).isoformat(),
                'action': 'restrict_processing'
            }
            
            if self.redis_client:
                key = f"gdpr:restriction:{user_id}:{purpose.value}"
                self.redis_client.set(key, json.dumps(restriction_data))
                
            # Notify relevant systems about consent withdrawal
            # This would trigger updates in analytics, marketing, etc.
            logger.info(f"Applied processing restrictions for user {user_id}, purpose {purpose.value}")
            
        except Exception as e:
            logger.error(f"Error applying consent withdrawal restrictions: {e}")
    
    def _extract_user_data_from_map(self, user_id: str, data_map: DataMap) -> Dict[str, Any]:
        """Extract user data according to data map"""
        # This would connect to actual data sources
        # For now, return mock data structure
        extracted_data = {
            'data_map_id': data_map.id,
            'extraction_date': datetime.now(timezone.utc).isoformat(),
            'data_elements': {}
        }
        
        for element in data_map.data_elements:
            if element.is_personal:
                # Mock data extraction - in production, this would query actual databases
                extracted_data['data_elements'][element.field_name] = {
                    'value': f"[{element.field_name}_value_for_{user_id}]",
                    'category': element.data_category.value,
                    'is_sensitive': element.is_sensitive,
                    'processing_purposes': [p.value for p in element.processing_purposes],
                    'legal_basis': [b.value for b in element.legal_basis]
                }
        
        return extracted_data
    
    def _extract_portable_data_from_map(self, user_id: str, data_map: DataMap) -> Dict[str, Any]:
        """Extract portable data (structured format for data portability)"""
        # Only include data that the user provided or was generated based on their use
        portable_data = {
            'data_map_id': data_map.id,
            'export_date': datetime.now(timezone.utc).isoformat(),
            'format': 'JSON',
            'data': {}
        }
        
        for element in data_map.data_elements:
            if (element.is_personal and 
                element.data_category in [DataCategory.PERSONAL_IDENTIFIERS, 
                                        DataCategory.CONTACT_INFORMATION,
                                        DataCategory.BEHAVIORAL_DATA]):
                portable_data['data'][element.field_name] = f"[portable_{element.field_name}_{user_id}]"
        
        return portable_data
    
    def _erase_user_data_from_map(self, user_id: str, data_map: DataMap) -> bool:
        """Erase user data according to data map"""
        try:
            # In production, this would connect to actual data sources and perform deletions
            # For now, simulate the erasure process
            
            erasure_log = {
                'user_id': user_id,
                'data_map_id': data_map.id,
                'erased_at': datetime.now(timezone.utc).isoformat(),
                'elements_erased': []
            }
            
            for element in data_map.data_elements:
                if element.is_personal:
                    # Simulate erasure of each data element
                    erasure_log['elements_erased'].append({
                        'field_name': element.field_name,
                        'category': element.data_category.value,
                        'erasure_method': 'deletion' if not element.anonymization_possible else 'anonymization'
                    })
            
            # Store erasure log
            if self.redis_client:
                key = f"gdpr:erasure_log:{user_id}:{data_map.id}:{int(datetime.now(timezone.utc).timestamp())}"
                self.redis_client.set(key, json.dumps(erasure_log))
            
            return True
            
        except Exception as e:
            logger.error(f"Error erasing user data from {data_map.name}: {e}")
            return False
    
    def _erase_user_consents(self, user_id: str):
        """Erase user consent records"""
        try:
            if self.redis_client:
                # Get all consent purposes for user
                consent_purposes = self.redis_client.smembers(f"gdpr:user_consents:{user_id}")
                
                for purpose in consent_purposes:
                    key = f"gdpr:consent:{user_id}:{purpose}"
                    self.redis_client.delete(key)
                
                # Remove user consent index
                self.redis_client.delete(f"gdpr:user_consents:{user_id}")
                
                logger.info(f"Erased consent records for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error erasing user consents: {e}")
    
    def _check_erasure_restrictions(self, user_id: str) -> List[str]:
        """Check if there are legal restrictions preventing erasure"""
        restrictions = []
        
        # Check for legal obligations (e.g., tax records, audit trails)
        # This would check actual business requirements
        
        # Example restrictions:
        # - Financial records must be kept for 7 years
        # - Fraud prevention data
        # - Legal proceedings
        
        return restrictions
    
    def _schedule_breach_notifications(self, breach: DataBreachIncident):
        """Schedule required breach notifications"""
        try:
            # Schedule supervisory authority notification
            if not breach.supervisory_authority_notified:
                notification_data = {
                    'breach_id': breach.id,
                    'type': 'supervisory_authority',
                    'deadline': breach.notification_deadline.isoformat(),
                    'recipient': self.config['supervisory_authority']['email']
                }
                
                if self.redis_client:
                    key = f"gdpr:notification_queue:{breach.id}_sa"
                    self.redis_client.set(key, json.dumps(notification_data))
                    
                    # Set expiration to remind about deadline
                    ttl = int((breach.notification_deadline - datetime.now(timezone.utc)).total_seconds())
                    if ttl > 0:
                        self.redis_client.expire(key, ttl)
            
            logger.info(f"Scheduled breach notifications for {breach.id}")
            
        except Exception as e:
            logger.error(f"Error scheduling breach notifications: {e}")
    
    def _send_request_notification(self, request: DataSubjectRequest):
        """Send notification about data subject request"""
        try:
            # In production, this would send email notifications
            notification_data = {
                'request_id': request.id,
                'user_id': request.user_id,
                'request_type': request.request_type.value,
                'submitted_at': request.submitted_at.isoformat(),
                'deadline': request.deadline.isoformat() if request.deadline else None
            }
            
            logger.info(f"Would send notification for request {request.id}")
            
        except Exception as e:
            logger.error(f"Error sending request notification: {e}")
    
    def _get_data_subject_request(self, request_id: str) -> Optional[DataSubjectRequest]:
        """Get data subject request by ID"""
        try:
            if self.redis_client:
                key = f"gdpr:request:{request_id}"
                request_data = self.redis_client.get(key)
                
                if request_data:
                    data = json.loads(request_data)
                    return DataSubjectRequest(
                        id=data['id'],
                        user_id=data['user_id'],
                        request_type=DataSubjectRight(data['request_type']),
                        status=RequestStatus(data['status']),
                        description=data.get('description'),
                        submitted_at=datetime.fromisoformat(data['submitted_at']),
                        completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                        deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
                        processor_notes=data.get('processor_notes'),
                        response_data=data.get('response_data'),
                        verification_method=data.get('verification_method'),
                        metadata=data.get('metadata', {})
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting data subject request {request_id}: {e}")
            return None
    
    def _update_request_status(self, request_id: str, status: RequestStatus, response_data: Dict[str, Any] = None):
        """Update data subject request status"""
        try:
            if self.redis_client:
                key = f"gdpr:request:{request_id}"
                request_data = self.redis_client.get(key)
                
                if request_data:
                    data = json.loads(request_data)
                    data['status'] = status.value
                    
                    if status == RequestStatus.COMPLETED:
                        data['completed_at'] = datetime.now(timezone.utc).isoformat()
                    
                    if response_data:
                        data['response_data'] = response_data
                    
                    self.redis_client.set(key, json.dumps(data))
                    
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
    
    def _deserialize_breach(self, data: Dict[str, Any]) -> DataBreachIncident:
        """Deserialize breach incident from stored data"""
        return DataBreachIncident(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            discovered_at=datetime.fromisoformat(data['discovered_at']),
            reported_at=datetime.fromisoformat(data['reported_at']) if data.get('reported_at') else None,
            affected_records_count=data['affected_records_count'],
            affected_data_categories=[DataCategory(cat) for cat in data['affected_data_categories']],
            breach_type=data['breach_type'],
            severity=data['severity'],
            notification_required=data['notification_required'],
            supervisory_authority_notified=data['supervisory_authority_notified'],
            individuals_notified=data['individuals_notified'],
            containment_measures=data['containment_measures'],
            remediation_actions=data['remediation_actions'],
            status=data['status'],
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def _log_privacy_action(self, action: str, data: Dict[str, Any]):
        """Log privacy-related actions for audit purposes"""
        try:
            if self.config.get('enable_audit_log') and self.redis_client:
                log_entry = {
                    'action': action,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'data': data
                }
                
                # Store with TTL (e.g., 7 years for GDPR compliance)
                key = f"gdpr:audit:{datetime.now(timezone.utc).strftime('%Y%m%d')}:{uuid.uuid4().hex[:8]}"
                self.redis_client.setex(key, 86400 * 2555, json.dumps(log_entry))  # 7 years
                
        except Exception as e:
            logger.error(f"Error logging privacy action: {e}")


# Utility functions

def create_gdpr_manager(config: Dict[str, Any] = None) -> GDPRComplianceManager:
    """Factory function to create GDPR compliance manager"""
    return GDPRComplianceManager(config)