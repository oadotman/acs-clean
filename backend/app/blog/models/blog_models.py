from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SCHEDULED = "scheduled"


class PostCategory(str, Enum):
    EDUCATIONAL = "educational"
    CASE_STUDY = "case_study"
    TOOL_FOCUSED = "tool_focused"
    INDUSTRY_INSIGHTS = "industry_insights"


class Author(BaseModel):
    name: str
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    social_links: Optional[Dict[str, str]] = None


class Tag(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


class Category(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    color: Optional[str] = None


class SEOData(BaseModel):
    title: str = Field(..., max_length=60)
    meta_description: str = Field(..., min_length=110, max_length=160)
    canonical_url: Optional[HttpUrl] = None
    primary_keyword: str
    secondary_keywords: List[str] = []
    focus_keyphrases: List[str] = []
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[HttpUrl] = None
    twitter_card_type: str = "summary_large_image"
    schema_markup: Optional[Dict[str, Any]] = None


class ContentStats(BaseModel):
    word_count: int
    read_time: int  # in minutes
    heading_count: int
    image_count: int
    link_count: int
    internal_links: List[str] = []
    external_links: List[str] = []


class BlogMetadata(BaseModel):
    views: int = 0
    shares: int = 0
    likes: int = 0
    comments_count: int = 0
    engagement_rate: float = 0.0
    bounce_rate: Optional[float] = None
    avg_time_on_page: Optional[int] = None  # seconds


class BlogPostBase(BaseModel):
    title: str = Field(..., min_length=10, max_length=100)
    slug: str = Field(..., min_length=3, max_length=100)
    excerpt: str = Field(..., min_length=50, max_length=300)
    content: str = Field(..., min_length=100)
    status: PostStatus = PostStatus.DRAFT
    category: PostCategory
    tags: List[str] = []
    featured_image: Optional[HttpUrl] = None
    hero_image: Optional[HttpUrl] = None
    author: Author
    seo: SEOData
    scheduled_at: Optional[datetime] = None
    
    @validator('slug')
    def slug_must_be_valid(cls, v):
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=100)
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    excerpt: Optional[str] = Field(None, min_length=50, max_length=300)
    content: Optional[str] = Field(None, min_length=100)
    status: Optional[PostStatus] = None
    category: Optional[PostCategory] = None
    tags: Optional[List[str]] = None
    featured_image: Optional[HttpUrl] = None
    hero_image: Optional[HttpUrl] = None
    author: Optional[Author] = None
    seo: Optional[SEOData] = None
    scheduled_at: Optional[datetime] = None


class BlogPost(BlogPostBase):
    id: str  # This will be the filename without extension
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    content_stats: ContentStats
    metadata: BlogMetadata = BlogMetadata()


class BlogPostList(BaseModel):
    id: str
    title: str
    slug: str
    excerpt: str
    status: PostStatus
    category: PostCategory
    tags: List[str]
    featured_image: Optional[HttpUrl] = None
    author: Author
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    content_stats: ContentStats
    metadata: BlogMetadata


class BlogPostDetail(BlogPost):
    related_posts: List[BlogPostList] = []
    table_of_contents: List[Dict[str, Any]] = []
    content_html: str = ""
    breadcrumbs: List[Dict[str, str]] = []
    cta_variations: List[Dict[str, str]] = []
    lead_magnets: List[Dict[str, str]] = []
    social_snippets: Dict[str, str] = {}


class BlogPostSearch(BaseModel):
    query: str
    category: Optional[PostCategory] = None
    tags: Optional[List[str]] = None
    status: Optional[PostStatus] = PostStatus.PUBLISHED
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    sort_by: str = Field("published_at", pattern="^(published_at|created_at|title|views)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class BlogPostResponse(BaseModel):
    posts: List[BlogPostList]
    total: int
    limit: int
    offset: int
    has_more: bool


class SitemapEntry(BaseModel):
    url: str
    last_modified: datetime
    change_frequency: str = "weekly"
    priority: float = Field(0.8, ge=0.0, le=1.0)


class RSSItem(BaseModel):
    title: str
    link: str
    description: str
    pub_date: datetime
    guid: str
    author: str
    category: str
