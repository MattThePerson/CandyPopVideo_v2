export function createPager<T>(getItems: () => T[], batchSize: number) {
    let count = $state(batchSize);
    return {
        get visible() { return getItems().slice(0, count); },
        get hasMore() { return count < getItems().length; },
        loadMore() { count = Math.min(count + batchSize, getItems().length); },
        reset()    { count = batchSize; },
    };
}
