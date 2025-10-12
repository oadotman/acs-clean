import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from ..models.blog_models import (
    BlogPostList,
    BlogPostDetail,
    SitemapEntry,
    RSSItem,
    PostStatus
)


class SEOService:
    def __init__(self, base_url: str = "https://adcopysurge.com"):
        """Initialize SEO service with base URL"""
        self.base_url = base_url.rstrip('/')
    
    def generate_sitemap(self, posts: List[BlogPostList], additional_urls: List[SitemapEntry] = None) -> str:
        """Generate XML sitemap for blog posts"""
        
        # Create root element
        urlset = Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        urlset.set('xmlns:news', 'http://www.google.com/schemas/sitemap-news/0.9')
        urlset.set('xmlns:xhtml', 'http://www.w3.org/1999/xhtml')
        
        # Add blog posts
        for post in posts:
            if post.status != PostStatus.PUBLISHED:
                continue
                
            url_elem = SubElement(urlset, 'url')
            
            # Location
            loc = SubElement(url_elem, 'loc')
            loc.text = f"{self.base_url}/blog/{post.slug}"
            
            # Last modified
            lastmod = SubElement(url_elem, 'lastmod')
            lastmod.text = (post.updated_at or post.created_at).strftime('%Y-%m-%d')
            
            # Change frequency
            changefreq = SubElement(url_elem, 'changefreq')
            changefreq.text = 'weekly'
            
            # Priority
            priority = SubElement(url_elem, 'priority')
            priority.text = '0.8'
        
        # Add additional URLs (like category pages, main blog page)
        if additional_urls:
            for entry in additional_urls:
                url_elem = SubElement(urlset, 'url')
                
                loc = SubElement(url_elem, 'loc')
                loc.text = entry.url
                
                lastmod = SubElement(url_elem, 'lastmod')
                lastmod.text = entry.last_modified.strftime('%Y-%m-%d')
                
                changefreq = SubElement(url_elem, 'changefreq')
                changefreq.text = entry.change_frequency
                
                priority = SubElement(url_elem, 'priority')
                priority.text = str(entry.priority)
        
        # Pretty print XML
        rough_string = tostring(urlset, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")[23:]  # Remove XML declaration line
    
    def generate_rss_feed(self, posts: List[BlogPostList], feed_title: str = "AdCopySurge Blog", 
                         feed_description: str = "Latest insights on ad copy optimization and digital marketing") -> str:
        """Generate RSS feed for blog posts"""
        
        # Create RSS root
        rss = Element('rss')
        rss.set('version', '2.0')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        
        # Channel element
        channel = SubElement(rss, 'channel')
        
        # Feed metadata
        title = SubElement(channel, 'title')
        title.text = feed_title
        
        description = SubElement(channel, 'description')
        description.text = feed_description
        
        link = SubElement(channel, 'link')
        link.text = f"{self.base_url}/blog"
        
        # Self reference
        atom_link = SubElement(channel, 'atom:link')
        atom_link.set('href', f"{self.base_url}/blog/rss.xml")
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')
        
        # Feed info
        language = SubElement(channel, 'language')
        language.text = 'en-us'
        
        pub_date = SubElement(channel, 'pubDate')
        pub_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        last_build_date = SubElement(channel, 'lastBuildDate')
        last_build_date.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        generator = SubElement(channel, 'generator')
        generator.text = 'AdCopySurge Blog System'
        
        # Add items (posts)
        for post in posts[:20]:  # Latest 20 posts
            if post.status != PostStatus.PUBLISHED:
                continue
                
            item = SubElement(channel, 'item')
            
            # Title
            item_title = SubElement(item, 'title')
            item_title.text = post.title
            
            # Link
            item_link = SubElement(item, 'link')
            item_link.text = f"{self.base_url}/blog/{post.slug}"
            
            # Description
            item_description = SubElement(item, 'description')
            item_description.text = post.excerpt
            
            # Author
            author = SubElement(item, 'author')
            author.text = f"{post.author.email or 'blog@adcopysurge.com'} ({post.author.name})"
            
            # Category
            category = SubElement(item, 'category')
            category.text = post.category.value.replace('_', ' ').title()
            
            # GUID
            guid = SubElement(item, 'guid')
            guid.set('isPermaLink', 'true')
            guid.text = f"{self.base_url}/blog/{post.slug}"
            
            # Publication date
            pub_date = SubElement(item, 'pubDate')
            pub_date.text = (post.published_at or post.created_at).strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Convert to string
        rough_string = tostring(rss, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def generate_robots_txt(self, additional_rules: List[str] = None) -> str:
        """Generate robots.txt content"""
        
        robots_content = [
            "User-agent: *",
            "Allow: /",
            "",
            "# Blog specific rules",
            "Allow: /blog/",
            "Allow: /blog/category/",
            "Allow: /blog/tag/",
            "",
            "# Disallow admin areas",
            "Disallow: /admin/",
            "Disallow: /api/",
            "",
            "# Sitemap",
            f"Sitemap: {self.base_url}/sitemap.xml",
            f"Sitemap: {self.base_url}/blog/sitemap.xml",
            ""
        ]
        
        if additional_rules:
            robots_content.extend(additional_rules)
        
        return "\n".join(robots_content)
    
    def generate_json_ld_article(self, post: BlogPostDetail) -> Dict[str, Any]:
        """Generate JSON-LD structured data for a blog post"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": post.title,
            "description": post.excerpt,
            "author": {
                "@type": "Person",
                "name": post.author.name,
                "url": f"{self.base_url}/author/{post.author.name.lower().replace(' ', '-')}"
            },
            "publisher": {
                "@type": "Organization",
                "name": "AdCopySurge",
                "url": self.base_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.base_url}/images/logo.png",
                    "width": 300,
                    "height": 60
                }
            },
            "datePublished": (post.published_at or post.created_at).isoformat(),
            "dateModified": post.updated_at.isoformat(),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.base_url}/blog/{post.slug}"
            },
            "articleSection": post.category.value.replace('_', ' ').title(),
            "keywords": ", ".join(post.tags),
            "wordCount": post.content_stats.word_count,
            "timeRequired": f"PT{post.content_stats.read_time}M"
        }
        
        # Add image if available
        if post.featured_image or post.hero_image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": str(post.featured_image or post.hero_image),
                "width": 1200,
                "height": 630
            }
        
        # Add breadcrumb
        if post.breadcrumbs:
            breadcrumb_list = {
                "@type": "BreadcrumbList",
                "itemListElement": []
            }
            
            for i, crumb in enumerate(post.breadcrumbs):
                breadcrumb_list["itemListElement"].append({
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": crumb["name"],
                    "item": f"{self.base_url}{crumb['url']}"
                })
            
            schema["breadcrumb"] = breadcrumb_list
        
        return schema
    
    def generate_json_ld_blog(self, posts: List[BlogPostList]) -> Dict[str, Any]:
        """Generate JSON-LD structured data for blog listing page"""
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": "AdCopySurge Blog",
            "description": "Expert insights on ad copy optimization, digital marketing strategies, and conversion rate optimization.",
            "url": f"{self.base_url}/blog",
            "publisher": {
                "@type": "Organization",
                "name": "AdCopySurge",
                "url": self.base_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{self.base_url}/images/logo.png",
                    "width": 300,
                    "height": 60
                }
            },
            "blogPost": []
        }
        
        # Add recent posts
        for post in posts[:10]:
            if post.status != PostStatus.PUBLISHED:
                continue
                
            blog_post = {
                "@type": "BlogPosting",
                "headline": post.title,
                "description": post.excerpt,
                "url": f"{self.base_url}/blog/{post.slug}",
                "datePublished": (post.published_at or post.created_at).isoformat(),
                "dateModified": post.updated_at.isoformat(),
                "author": {
                    "@type": "Person",
                    "name": post.author.name
                },
                "articleSection": post.category.value.replace('_', ' ').title(),
                "keywords": ", ".join(post.tags),
                "wordCount": post.content_stats.word_count,
                "timeRequired": f"PT{post.content_stats.read_time}M"
            }
            
            if post.featured_image:
                blog_post["image"] = {
                    "@type": "ImageObject",
                    "url": str(post.featured_image),
                    "width": 1200,
                    "height": 630
                }
            
            schema["blogPost"].append(blog_post)
        
        return schema
    
    def generate_open_graph_tags(self, post: BlogPostDetail) -> Dict[str, str]:
        """Generate Open Graph meta tags for social sharing"""
        
        og_tags = {
            "og:type": "article",
            "og:title": post.seo.og_title or post.title,
            "og:description": post.seo.og_description or post.excerpt,
            "og:url": f"{self.base_url}/blog/{post.slug}",
            "og:site_name": "AdCopySurge",
            "article:published_time": (post.published_at or post.created_at).isoformat(),
            "article:modified_time": post.updated_at.isoformat(),
            "article:author": post.author.name,
            "article:section": post.category.value.replace('_', ' ').title()
        }
        
        # Add image
        if post.seo.og_image or post.featured_image or post.hero_image:
            og_tags["og:image"] = str(post.seo.og_image or post.featured_image or post.hero_image)
            og_tags["og:image:width"] = "1200"
            og_tags["og:image:height"] = "630"
            og_tags["og:image:alt"] = f"{post.title} - AdCopySurge Blog"
        
        # Add tags
        for tag in post.tags:
            og_tags[f"article:tag"] = tag
        
        return og_tags
    
    def generate_twitter_card_tags(self, post: BlogPostDetail) -> Dict[str, str]:
        """Generate Twitter Card meta tags"""
        
        twitter_tags = {
            "twitter:card": post.seo.twitter_card_type,
            "twitter:site": "@AdCopySurge",
            "twitter:title": post.seo.og_title or post.title,
            "twitter:description": post.seo.og_description or post.excerpt,
            "twitter:creator": f"@{post.author.social_links.get('twitter', 'AdCopySurge')}" if post.author.social_links else "@AdCopySurge"
        }
        
        # Add image
        if post.seo.og_image or post.featured_image or post.hero_image:
            twitter_tags["twitter:image"] = str(post.seo.og_image or post.featured_image or post.hero_image)
            twitter_tags["twitter:image:alt"] = f"{post.title} - AdCopySurge Blog"
        
        return twitter_tags
    
    def get_default_sitemap_entries(self) -> List[SitemapEntry]:
        """Get default sitemap entries for blog-related pages"""
        
        return [
            SitemapEntry(
                url=f"{self.base_url}/blog",
                last_modified=datetime.now(timezone.utc),
                change_frequency="daily",
                priority=0.9
            ),
            SitemapEntry(
                url=f"{self.base_url}/blog/category/educational",
                last_modified=datetime.now(timezone.utc),
                change_frequency="weekly",
                priority=0.7
            ),
            SitemapEntry(
                url=f"{self.base_url}/blog/category/case-study",
                last_modified=datetime.now(timezone.utc),
                change_frequency="weekly",
                priority=0.7
            ),
            SitemapEntry(
                url=f"{self.base_url}/blog/category/tool-focused",
                last_modified=datetime.now(timezone.utc),
                change_frequency="weekly",
                priority=0.7
            ),
            SitemapEntry(
                url=f"{self.base_url}/blog/category/industry-insights",
                last_modified=datetime.now(timezone.utc),
                change_frequency="weekly",
                priority=0.7
            )
        ]
