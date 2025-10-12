# ADR-004: Database Architecture Strategy

## Status
**ACCEPTED** - 2025-01-09

## Context

AdCopySurge currently uses a hybrid database approach:
- **Supabase** for authentication and user management
- **SQLAlchemy + PostgreSQL** for application data (ad analyses, projects, etc.)

This hybrid approach has created complexity and deployment challenges:
1. Dual schema management (Supabase SQL + SQLAlchemy models)
2. Authentication token mapping complexity between systems
3. Data consistency challenges across systems
4. Deployment orchestration complexity

For production deployment, we need to decide on a single-source-of-truth database architecture.

## Decision

**We will adopt a hybrid architecture with clear separation of concerns:**

### ✅ CHOSEN: Supabase for Auth + FastAPI PostgreSQL for Business Data

**Authentication & User Management:**
- **Supabase** handles: Authentication, JWT tokens, user sessions, password resets
- User profiles stored in Supabase `auth.users` table
- Lightweight Supabase `public.user_profiles` for display names, avatars

**Business Data & Core Features:**
- **FastAPI + PostgreSQL** handles: Ad analyses, projects, subscriptions, billing, analytics
- SQLAlchemy models as single source of truth
- Alembic for database migrations
- Full control over schema, indexes, and performance optimization

**Data Flow:**
```
Frontend → Supabase Auth → JWT Token → FastAPI Middleware → PostgreSQL Business Data
```

## Alternatives Considered

### Option A: Supabase Only
**Pros:** Single system, built-in auth, real-time features
**Cons:** 
- Limited control over complex queries
- Vendor lock-in
- Less flexibility for business logic
- Limited AI/ML integration capabilities

### Option B: FastAPI + PostgreSQL Only  
**Pros:** Full control, single system, better for complex business logic
**Cons:**
- Need to implement auth from scratch
- More complex user management
- No built-in real-time features

### Option C: Hybrid (Current Approach) ❌
**Cons:**
- Dual schema management overhead
- Complex authentication flow
- Data consistency challenges
- Deployment complexity

## Implementation Strategy

### Phase 1: Authentication Integration (Week 1)
1. **Implement Supabase JWT Middleware** in FastAPI
   ```python
   # Validate Supabase JWT on every request
   # Extract user_id from JWT 'sub' claim
   # Map to internal User model
   ```

2. **Database Schema Updates**
   ```sql
   ALTER TABLE users ADD COLUMN supabase_user_id UUID UNIQUE;
   CREATE INDEX idx_users_supabase_id ON users(supabase_user_id);
   ```

3. **User Model Updates**
   ```python
   class User(Base):
       id: int = Column(Integer, primary_key=True)
       supabase_user_id: UUID = Column(UUID, unique=True, nullable=False)
       email: str = Column(String, unique=True, nullable=False)
       # ... other business fields
   ```

### Phase 2: Data Migration (Week 2)
1. **Create migration scripts** for existing users
2. **Update API endpoints** to use new auth flow
3. **Test authentication integration** thoroughly

### Phase 3: Schema Cleanup (Week 3)
1. **Remove duplicate Supabase tables** (projects, analyses, etc.)
2. **Mark legacy endpoints as deprecated**
3. **Update documentation** with new architecture

## Benefits

### 🚀 **Performance & Scalability**
- Optimized PostgreSQL for complex business queries
- Custom indexes for ad analysis queries
- Better control over query performance

### 🔒 **Security & Compliance**
- Proven Supabase auth with Row Level Security
- JWT-based stateless authentication
- Fine-grained permission control in FastAPI

### 🛠 **Development Experience**
- SQLAlchemy ORM for complex business logic
- Type-safe database operations
- Familiar FastAPI patterns for team

### 🏗 **Deployment & DevOps**
- Single PostgreSQL instance to manage
- Alembic migrations for version control
- Better CI/CD integration

## Risks & Mitigations

### Risk: Authentication Complexity
**Mitigation:** 
- Comprehensive JWT middleware with proper error handling
- Fallback authentication strategies
- Extensive integration testing

### Risk: Supabase Vendor Lock-in for Auth
**Mitigation:**
- Auth concerns isolated to authentication only
- Can migrate to Auth0, Firebase Auth, or custom auth later
- Business data remains under full control

### Risk: Data Consistency Between Systems
**Mitigation:**
- Supabase user_id as foreign key in PostgreSQL
- Atomic operations within each system
- Proper error handling for cross-system operations

## Monitoring & Success Metrics

### Technical Metrics
- **API Response Time:** <200ms for business queries
- **Authentication Success Rate:** >99.9%
- **Database Query Performance:** Indexed queries <50ms
- **Error Rate:** <0.1% for auth middleware

### Operational Metrics  
- **Deployment Complexity:** Single PostgreSQL migration
- **Development Velocity:** Faster feature development
- **Bug Count:** Reduced data consistency bugs

## Timeline

- **Week 1:** JWT middleware + schema updates
- **Week 2:** Data migration + API updates  
- **Week 3:** Schema cleanup + documentation
- **Week 4:** Load testing + production readiness

## Approval

**Approved by:** Development Team
**Date:** 2025-01-09
**Review Date:** 2025-04-09 (Quarterly review)

---

## Implementation Checklist

### ✅ Completed
- [x] Architecture decision documented
- [x] JWT middleware design approved

### 🔄 In Progress  
- [ ] Implement Supabase JWT validation middleware
- [ ] Add supabase_user_id to User model
- [ ] Create Alembic migration for schema updates

### 📋 Todo
- [ ] Update authentication endpoints
- [ ] Create user data migration scripts
- [ ] Update API documentation
- [ ] Integration testing
- [ ] Performance testing
- [ ] Production deployment

## References

- [Supabase JWT Documentation](https://supabase.com/docs/guides/auth/jwt)
- [FastAPI JWT Authentication](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Migration Guide](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
