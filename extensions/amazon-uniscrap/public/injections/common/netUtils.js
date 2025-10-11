/**
 * Performs fetch request with automatic retry on network failures
 * @param {RequestInfo} input - URL or request object
 * @param {RequestInit} [init] - Request options
 * @param {number} [maxRetries=3] - Maximum retry attempts
 * @param {number} [retryDelay=1000] - Delay between retries in ms
 * @returns {Promise<Response>}
 */
async function fetchWithRetry(input, init, maxRetries = 3, retryDelay = 100) {
    let lastError;

    for (let attempt = 1; attempt <= maxRetries; ++attempt) {
        try {
            return await fetch(input, init);
        } catch (error) {
            lastError = error;

            // Check for network-related errors
            const isNetworkError = error instanceof TypeError ||
                /network|NETWORK|Failed to fetch/i.test(error.message);

            // Exit if not network error or no retries left
            if (!isNetworkError || attempt === maxRetries)
                break;

            // Exponential backoff delay
            const delay = retryDelay * Math.pow(2, attempt - 1);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }

    throw lastError;
}
