/**
 * Production-Safe Logger Utility
 *
 * Replaces console.log statements throughout the application with
 * environment-aware logging that:
 * - Only logs in development mode
 * - Prevents console pollution in production
 * - Improves performance (no unnecessary string formatting)
 * - Prevents sensitive data leakage in production
 *
 * Usage:
 *   import logger from 'utils/logger';
 *
 *   logger.log('Debug info', data);      // Only in development
 *   logger.warn('Warning message');      // Only in development
 *   logger.error('Error occurred', err); // Always logged
 *   logger.info('Info message');         // Only in development
 */

const isDevelopment = process.env.NODE_ENV === 'development';
const isTest = process.env.NODE_ENV === 'test';

/**
 * Sanitize sensitive data before logging
 * Removes common sensitive fields from objects
 */
const sanitize = (data) => {
  if (!data || typeof data !== 'object') {
    return data;
  }

  const sensitiveKeys = [
    'password',
    'token',
    'secret',
    'apiKey',
    'api_key',
    'authorization',
    'cookie',
    'session',
    'credit_card',
    'ssn',
    'credentials'
  ];

  const sanitized = Array.isArray(data) ? [...data] : { ...data };

  Object.keys(sanitized).forEach(key => {
    const lowerKey = key.toLowerCase();
    if (sensitiveKeys.some(sensitive => lowerKey.includes(sensitive))) {
      sanitized[key] = '[REDACTED]';
    } else if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
      sanitized[key] = sanitize(sanitized[key]);
    }
  });

  return sanitized;
};

/**
 * Format log message with timestamp in development
 */
const formatMessage = (level, ...args) => {
  if (!isDevelopment) return args;

  const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
  const levelBadge = {
    log: '📝',
    info: 'ℹ️',
    warn: '⚠️',
    error: '❌',
    debug: '🔍'
  }[level] || '📝';

  return [`[${timestamp}] ${levelBadge}`, ...args];
};

const logger = {
  /**
   * Standard logging - development only
   */
  log: (...args) => {
    if (isDevelopment && !isTest) {
      console.log(...formatMessage('log', ...args.map(sanitize)));
    }
  },

  /**
   * Info logging - development only
   */
  info: (...args) => {
    if (isDevelopment && !isTest) {
      console.info(...formatMessage('info', ...args.map(sanitize)));
    }
  },

  /**
   * Warning logging - development only
   */
  warn: (...args) => {
    if (isDevelopment && !isTest) {
      console.warn(...formatMessage('warn', ...args.map(sanitize)));
    }
  },

  /**
   * Error logging - ALWAYS logged (production + development)
   * Errors should always be visible for debugging
   */
  error: (...args) => {
    if (!isTest) {
      console.error(...formatMessage('error', ...args));
    }
  },

  /**
   * Debug logging - development only
   * Use for verbose debugging that you don't want in production
   */
  debug: (...args) => {
    if (isDevelopment && !isTest) {
      console.debug(...formatMessage('debug', ...args.map(sanitize)));
    }
  },

  /**
   * Table logging - development only
   * Useful for displaying structured data
   */
  table: (data) => {
    if (isDevelopment && !isTest) {
      console.table(sanitize(data));
    }
  },

  /**
   * Group logging - development only
   * Useful for grouping related log messages
   */
  group: (label) => {
    if (isDevelopment && !isTest) {
      console.group(formatMessage('log', label)[1]);
    }
  },

  groupEnd: () => {
    if (isDevelopment && !isTest) {
      console.groupEnd();
    }
  },

  /**
   * Time logging - development only
   * Useful for performance measurement
   */
  time: (label) => {
    if (isDevelopment && !isTest) {
      console.time(label);
    }
  },

  timeEnd: (label) => {
    if (isDevelopment && !isTest) {
      console.timeEnd(label);
    }
  },

  /**
   * Force log - ALWAYS logs regardless of environment
   * Use sparingly, only for critical system messages
   */
  force: (...args) => {
    console.log(...formatMessage('log', ...args));
  },

  /**
   * Conditional logging based on custom condition
   */
  if: (condition, ...args) => {
    if (condition && isDevelopment && !isTest) {
      console.log(...formatMessage('log', ...args.map(sanitize)));
    }
  }
};

// Export as default
export default logger;

// Also export individual methods for destructuring
export const { log, info, warn, error, debug, table, group, groupEnd, time, timeEnd, force } = logger;
