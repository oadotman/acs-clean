import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const BlogContext = createContext();

export const useBlog = () => {
  const context = useContext(BlogContext);
  if (!context) {
    throw new Error('useBlog must be used within a BlogProvider');
  }
  return context;
};

export const BlogProvider = ({ children }) => {
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [popularPosts, setPopularPosts] = useState([]);
  const [trendingPosts, setTrendingPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 20,
    offset: 0,
    hasMore: false
  });

  const API_BASE = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000/api';
  const BLOG_ENABLED = process.env.REACT_APP_BLOG_ENABLED !== 'false';

  // API call helper
  const apiCall = useCallback(async (url, options = {}) => {
    if (!BLOG_ENABLED) {
      console.warn('Blog functionality is disabled');
      // Return empty data structure based on endpoint
      if (url.includes('/categories')) return [];
      if (url.includes('/popular') || url.includes('/trending')) return [];
      return { posts: [], total: 0, limit: 20, offset: 0, has_more: false };
    }
    
    try {
      const response = await axios({
        url: `${API_BASE}${url}`,
        ...options
      });
      return response.data;
    } catch (error) {
      console.error(`API Error (${url}):`, error);
      
      // Handle specific error cases
      if (error.response?.status === 502 || error.response?.status === 503) {
        console.warn(`Blog service temporarily unavailable (${error.response.status}), returning empty data`);
        if (url.includes('/categories')) return [];
        if (url.includes('/popular') || url.includes('/trending')) return [];
        return { posts: [], total: 0, limit: 20, offset: 0, has_more: false };
      }
      
      if (error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error('An error occurred while loading blog data');
      }
      
      throw error;
    }
  }, [API_BASE, BLOG_ENABLED]);

  // Fetch blog posts
  const fetchPosts = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        limit: params.limit || 20,
        offset: params.offset || 0,
        sort_by: params.sortBy || 'published_at',
        sort_order: params.sortOrder || 'desc',
        ...(params.category && { category: params.category }),
        ...(params.status && { status: params.status })
      });

      const data = await apiCall(`/blog/?${queryParams}`);
      
      if (params.append) {
        setPosts(prevPosts => [...prevPosts, ...data.posts]);
      } else {
        setPosts(data.posts);
      }
      
      setPagination({
        total: data.total,
        limit: data.limit,
        offset: data.offset,
        hasMore: data.has_more
      });

      return data;
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Search posts
  const searchPosts = useCallback(async (query, filters = {}) => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: query,
        limit: filters.limit || 20,
        offset: filters.offset || 0,
        ...(filters.category && { category: filters.category }),
        ...(filters.tags && { tags: filters.tags.join(',') }),
        sort_by: filters.sortBy || 'published_at',
        sort_order: filters.sortOrder || 'desc'
      });

      const data = await apiCall(`/blog/search?${queryParams}`);
      setSearchResults(data);
      return data;
    } catch (error) {
      console.error('Error searching posts:', error);
      setSearchResults({ posts: [], total: 0, limit: 20, offset: 0, has_more: false });
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Get single post
  const getPost = useCallback(async (slug) => {
    setLoading(true);
    try {
      const data = await apiCall(`/blog/${slug}`);
      return data;
    } catch (error) {
      console.error(`Error fetching post ${slug}:`, error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Get posts by category
  const getPostsByCategory = useCallback(async (category, params = {}) => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        limit: params.limit || 20,
        offset: params.offset || 0
      });

      const data = await apiCall(`/blog/categories/${category}?${queryParams}`);
      return data;
    } catch (error) {
      console.error(`Error fetching posts by category ${category}:`, error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Get posts by tag
  const getPostsByTag = useCallback(async (tag, params = {}) => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        limit: params.limit || 20,
        offset: params.offset || 0
      });

      const data = await apiCall(`/blog/tags/${tag}?${queryParams}`);
      return data;
    } catch (error) {
      console.error(`Error fetching posts by tag ${tag}:`, error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Track post view
  const trackPostView = useCallback(async (slug) => {
    try {
      await apiCall(`/blog/${slug}/view`, { method: 'POST' });
    } catch (error) {
      // Silent fail for analytics
      console.warn('Failed to track post view:', error);
    }
  }, [apiCall]);

  // Track post share
  const trackPostShare = useCallback(async (slug, platform) => {
    try {
      await apiCall(`/blog/${slug}/share?platform=${platform}`, { method: 'POST' });
    } catch (error) {
      // Silent fail for analytics
      console.warn('Failed to track post share:', error);
    }
  }, [apiCall]);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load categories
        const categoriesData = await apiCall('/blog/categories');
        setCategories(categoriesData);

        // Load popular posts
        const popularData = await apiCall('/blog/popular?limit=5');
        setPopularPosts(popularData);

        // Load trending posts
        const trendingData = await apiCall('/blog/trending?limit=5');
        setTrendingPosts(trendingData);
        
      } catch (error) {
        console.error('Error loading initial blog data:', error);
      }
    };

    loadInitialData();
  }, [apiCall]);

  // Clear search results
  const clearSearch = useCallback(() => {
    setSearchResults(null);
  }, []);

  // Load more posts (for infinite scroll)
  const loadMorePosts = useCallback(async () => {
    if (!pagination.hasMore || loading) return;

    const nextOffset = pagination.offset + pagination.limit;
    await fetchPosts({ 
      offset: nextOffset, 
      limit: pagination.limit, 
      append: true 
    });
  }, [pagination, loading, fetchPosts]);

  const contextValue = {
    // State
    posts,
    categories,
    popularPosts,
    trendingPosts,
    loading,
    searchResults,
    pagination,

    // Actions
    fetchPosts,
    searchPosts,
    clearSearch,
    getPost,
    getPostsByCategory,
    getPostsByTag,
    trackPostView,
    trackPostShare,
    loadMorePosts,

    // Utils
    formatCategory: (category) => category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    getPostUrl: (slug) => `/blog/${slug}`,
    getCategoryUrl: (category) => `/blog/category/${category}`,
    getTagUrl: (tag) => `/blog/tag/${encodeURIComponent(tag)}`,
  };

  return (
    <BlogContext.Provider value={contextValue}>
      {children}
    </BlogContext.Provider>
  );
};
