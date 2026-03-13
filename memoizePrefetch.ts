interface CacheParams {
    key: string;
    ttl: number;
    prefetchThreshold?: number;
}

export const memoizePrefetch = async <T>(
    fastify: FastifyInstance,
    fn: () => Promise<T | undefined>,
    {
        key,
        ttl,
        prefetchThreshold,
    }: CacheParams
): Promise<T | undefined> => {

    if (!fastify.redis) {
        fastify.log.warn('Redis client not available, skipping memoization');
        return await fn();
    }

    const [cachedValue, ttlRemaining] = await Promise.all([
        fastify.redis.get(key),
        fastify.redis.ttl(key),
    ]);

    const shouldFetch =
        !cachedValue ||
        !ttlRemaining ||
        (prefetchThreshold && ttlRemaining / ttl < prefetchThreshold);

    fastify.log.debug(
        { key, ttl, ttlRemaining, prefetchThreshold, isCached: !!cachedValue, shouldFetch },
        'Cache parameters'
    );

    if (!shouldFetch) {
        return JSON.parse(cachedValue) as T;
    }

    fastify.log.debug({ key }, 'Fetching');

    const fetchAndCache = fn
        .catch((error: unknown) => {
            if (!cachedValue) {
                throw error;
            }

            fastify.log.warn(
                { error },
                'Fetch function threw an error. Ignoring because a cached value is available.'
            );

            return undefined;
        })
        .then((result) => {
            if (result) {
                fastify.log.debug({ key }, 'Caching result');
                fastify.redis.setex(key, ttl, JSON.stringify(result)).catch(() => {
                    /* noop */
                });
            } else {
                fastify.log.warn({ key }, 'Empty response, not caching');
            }

            return result;
        });

    if (cachedValue) {
        fastify.log.debug({ key }, 'Using cached value. Prefetch will continue.');
        return JSON.parse(cachedValue) as T;
    }

    fastify.log.debug({ key }, 'No cached value. Prefetch will wait for fetch to complete.');
    return await fetchAndCache;
};