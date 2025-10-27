/**
 * Query Timeout Utility
 * 
 * Wraps any promise with a timeout to prevent infinite hangs
 * Usage: const result = await withTimeout(myPromise, 10000);
 */

/**
 * Custom timeout error class for better error handling
 */
export class TimeoutError extends Error {
  constructor(message = 'Request timeout', timeoutMs) {
    super(message);
    this.name = 'TimeoutError';
    this.timeoutMs = timeoutMs;
    this.isTimeout = true;
  }
}

/**
 * Wraps a promise with a timeout
 * 
 * @param {Promise} promise - The promise to wrap
 * @param {number} timeoutMs - Timeout in milliseconds (default: 10000ms = 10 seconds)
 * @param {string} operationName - Optional name for logging/debugging
 * @returns {Promise} - The promise that will reject if timeout is reached
 * 
 * @example
 * const data = await withTimeout(
 *   supabase.from('users').select('*'),
 *   10000,
 *   'Fetch users'
 * );
 */
export const withTimeout = (promise, timeoutMs = 10000, operationName = 'Operation') => {
  // Create timeout promise that rejects after specified time
  const timeoutPromise = new Promise((_, reject) => {
    const timeoutId = setTimeout(() => {
      console.warn(`⏱️ ${operationName} timed out after ${timeoutMs}ms`);
      reject(new TimeoutError(
        `${operationName} timed out after ${timeoutMs}ms`,
        timeoutMs
      ));
    }, timeoutMs);

    // Store timeout ID on the promise so it can be cleared if needed
    timeoutPromise.timeoutId = timeoutId;
  });

  // Race between the actual promise and the timeout
  return Promise.race([promise, timeoutPromise]);
};

/**
 * Wraps a promise with timeout and retry logic
 * 
 * @param {Function} promiseFn - Function that returns a promise
 * @param {Object} options - Configuration options
 * @param {number} options.timeoutMs - Timeout per attempt (default: 10000)
 * @param {number} options.maxRetries - Maximum retry attempts (default: 3)
 * @param {number} options.retryDelayMs - Delay between retries (default: 1000)
 * @param {string} options.operationName - Operation name for logging
 * @returns {Promise} - The promise result or final error
 * 
 * @example
 * const data = await withTimeoutAndRetry(
 *   () => supabase.from('users').select('*'),
 *   { maxRetries: 3, timeoutMs: 10000 }
 * );
 */
export const withTimeoutAndRetry = async (
  promiseFn,
  {
    timeoutMs = 10000,
    maxRetries = 3,
    retryDelayMs = 1000,
    operationName = 'Operation'
  } = {}
) => {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`🔄 ${operationName} - Attempt ${attempt}/${maxRetries}`);
      
      // Execute with timeout
      const result = await withTimeout(
        promiseFn(),
        timeoutMs,
        `${operationName} (attempt ${attempt})`
      );
      
      console.log(`✅ ${operationName} succeeded on attempt ${attempt}`);
      return result;
      
    } catch (error) {
      lastError = error;
      
      // Log the error
      if (error.isTimeout) {
        console.warn(`⏱️ ${operationName} timed out on attempt ${attempt}/${maxRetries}`);
      } else {
        console.warn(`⚠️ ${operationName} failed on attempt ${attempt}/${maxRetries}:`, error.message);
      }
      
      // If this was the last attempt, throw the error
      if (attempt === maxRetries) {
        console.error(`❌ ${operationName} failed after ${maxRetries} attempts`);
        throw lastError;
      }
      
      // Wait before retrying (exponential backoff)
      const delay = retryDelayMs * Math.pow(2, attempt - 1);
      console.log(`⏳ Retrying ${operationName} in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
};

/**
 * Check if an error is a timeout error
 * 
 * @param {Error} error - The error to check
 * @returns {boolean} - True if it's a timeout error
 */
export const isTimeoutError = (error) => {
  return error instanceof TimeoutError || error?.isTimeout === true;
};

export default withTimeout;
