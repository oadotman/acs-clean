import re
from typing import List, Dict, Tuple, Any
import markdown
from markdown.extensions import toc, codehilite, tables, fenced_code
from markdown.extensions.toc import TocExtension


class MarkdownProcessor:
    def __init__(self):
        """Initialize the markdown processor with extensions"""
        self.md = markdown.Markdown(
            extensions=[
                TocExtension(
                    toc_depth="2-4",
                    permalink=True,
                    permalink_class="permalink",
                    permalink_title="Permanent link",
                    baselevel=1
                ),
                codehilite.CodeHiliteExtension(
                    css_class="highlight",
                    use_pygments=True,
                    linenums=False
                ),
                tables.TableExtension(),
                fenced_code.FencedCodeExtension(),
                'nl2br',
                'sane_lists'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
    
    def process(self, markdown_content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process markdown content and return HTML with table of contents
        
        Args:
            markdown_content: Raw markdown content
            
        Returns:
            Tuple of (processed_html, table_of_contents)
        """
        # Reset the markdown processor
        self.md.reset()
        
        # Process the markdown
        html_content = self.md.convert(markdown_content)
        
        # Extract table of contents
        toc_data = self._extract_toc()
        
        # Post-process HTML for AdCopySurge specific styling
        html_content = self._post_process_html(html_content)
        
        return html_content, toc_data
    
    def _extract_toc(self) -> List[Dict[str, Any]]:
        """Extract table of contents from the markdown processor"""
        toc_items = []
        
        if hasattr(self.md, 'toc_tokens'):
            for item in self.md.toc_tokens:
                toc_items.append({
                    'anchor': item['anchor'],
                    'title': item['name'],
                    'level': item['level']
                })
        
        return toc_items
    
    def _post_process_html(self, html_content: str) -> str:
        """Post-process HTML for AdCopySurge styling and functionality"""
        
        # Add responsive classes to images
        html_content = re.sub(
            r'<img([^>]*?)>',
            r'<img\1 class="blog-image" loading="lazy">',
            html_content
        )
        
        # Add target="_blank" to external links
        html_content = re.sub(
            r'<a href="(https?://[^"]*)"([^>]*)>',
            r'<a href="\1"\2 target="_blank" rel="noopener noreferrer">',
            html_content
        )
        
        # Add classes to headings for styling
        for level in range(1, 7):
            html_content = re.sub(
                f'<h{level}([^>]*)>',
                f'<h{level}\\1 class="blog-heading blog-h{level}">',
                html_content
            )
        
        # Add classes to paragraphs
        html_content = re.sub(
            r'<p>',
            r'<p class="blog-paragraph">',
            html_content
        )
        
        # Add classes to lists
        html_content = re.sub(
            r'<ul>',
            r'<ul class="blog-list blog-ul">',
            html_content
        )
        html_content = re.sub(
            r'<ol>',
            r'<ol class="blog-list blog-ol">',
            html_content
        )
        
        # Add classes to blockquotes
        html_content = re.sub(
            r'<blockquote>',
            r'<blockquote class="blog-blockquote">',
            html_content
        )
        
        # Add classes to code blocks
        html_content = re.sub(
            r'<pre>',
            r'<pre class="blog-code-block">',
            html_content
        )
        
        # Add classes to inline code
        html_content = re.sub(
            r'<code>([^<]+)</code>',
            r'<code class="blog-inline-code">\1</code>',
            html_content
        )
        
        # Add classes to tables
        html_content = re.sub(
            r'<table>',
            r'<div class="blog-table-wrapper"><table class="blog-table">',
            html_content
        )
        html_content = re.sub(
            r'</table>',
            r'</table></div>',
            html_content
        )
        
        return html_content
    
    def extract_excerpt(self, markdown_content: str, max_length: int = 200) -> str:
        """Extract a clean excerpt from markdown content"""
        # Remove markdown formatting
        clean_text = re.sub(r'[#*_`\[\]()]', '', markdown_content)
        
        # Remove extra whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Truncate to max length
        if len(clean_text) <= max_length:
            return clean_text
        
        # Find last complete sentence within limit
        truncated = clean_text[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.7:  # At least 70% of desired length
            return clean_text[:last_sentence_end + 1]
        else:
            # Fallback to word boundary
            last_space = truncated.rfind(' ')
            if last_space > 0:
                return clean_text[:last_space] + '...'
            else:
                return truncated + '...'
    
    def get_reading_time(self, markdown_content: str, words_per_minute: int = 200) -> int:
        """Calculate estimated reading time in minutes"""
        # Remove markdown formatting for word count
        clean_text = re.sub(r'[#*_`\[\]()]+', '', markdown_content)
        word_count = len(clean_text.split())
        
        # Calculate reading time (minimum 1 minute)
        reading_time = max(1, word_count // words_per_minute)
        return reading_time
    
    def extract_first_image(self, markdown_content: str) -> str:
        """Extract the first image URL from markdown content"""
        image_match = re.search(r'!\[.*?\]\((.*?)\)', markdown_content)
        return image_match.group(1) if image_match else None
    
    def validate_markdown(self, markdown_content: str) -> Dict[str, Any]:
        """Validate markdown content and return analysis"""
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'stats': {}
        }
        
        # Check for basic structure
        if not re.search(r'^#\s', markdown_content, re.MULTILINE):
            validation_results['warnings'].append("No H1 heading found")
        
        # Check for images
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', markdown_content))
        validation_results['stats']['images'] = image_count
        
        if image_count == 0:
            validation_results['warnings'].append("No images found")
        
        # Check for links
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', markdown_content))
        validation_results['stats']['links'] = link_count
        
        # Check word count
        word_count = len(markdown_content.split())
        validation_results['stats']['words'] = word_count
        
        if word_count < 300:
            validation_results['warnings'].append("Content is quite short (less than 300 words)")
        
        # Check for headings structure
        headings = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
        validation_results['stats']['headings'] = len(headings)
        
        if len(headings) < 3:
            validation_results['warnings'].append("Consider adding more headings for better structure")
        
        return validation_results
