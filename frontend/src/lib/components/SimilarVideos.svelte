<script lang="ts">
    import Spinner from './Spinner.svelte';
    import VideoCard from './VideoCard.svelte';
    import { createPager } from '$lib/util/pager.svelte';
    import type { VideoData } from '$lib/types/video';

    /* Props */
    let {
        video,
        similar,
        loading,
        queryTime,
        relatedHashes,
    }: {
        video: VideoData;
        similar: VideoData[];
        loading: boolean;
        queryTime: number | null;
        relatedHashes?: Set<string>;
    } = $props();

    let filterRelated    = $state(false);
    let filterStudio     = $state(false);
    let filterCollection = $state(false);
    let filterActors     = $state(false);

    const relatedInSimilar = $derived(similar.filter(v => relatedHashes?.has(v.hash)).length);

    const activeFilterTags = $derived(
        [
            filterStudio     && video.studio          ? `studio: "${video.studio}"` : null,
            filterCollection && video.collection      ? `collection: "${video.collection}"` : null,
            filterActors     && video.actors?.length  ? `actors: "${video.actors.join(', ')}"` : null,
        ].filter(Boolean).join(' | ')
    );

    const pager = createPager(() => {
        let out = similar;
        if (filterRelated && relatedHashes) out = out.filter(v => !relatedHashes.has(v.hash));
        if (filterStudio)                   out = out.filter(v => v.studio === video.studio);
        if (filterCollection)               out = out.filter(v => v.collection === video.collection);
        if (filterActors)                   out = out.filter(v => v.actors?.some(a => video.actors?.includes(a)));
        return out;
    }, 8);

    $effect(() => { filterRelated; filterStudio; filterCollection; filterActors; pager.reset(); });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="similar-section">
    <div class="similar-header">
        <div class="similar-title-row">
            <h2 class="similar-title">SIMILAR VIDEOS</h2>
            {#if queryTime !== null}
                <span class="query-time">{queryTime.toFixed(2)}s</span>
            {/if}
            {#if activeFilterTags}
                <span class="active-filter-tags">{activeFilterTags}</span>
            {/if}
        </div>
        <div class="filter-btns">
            {#if relatedHashes !== undefined}
                <button
                    class="filter-btn"
                    class:active={filterRelated}
                    disabled={relatedInSimilar === 0}
                    onclick={() => { filterRelated = !filterRelated; }}
                >
                    FILTER RELATED{relatedInSimilar > 0 ? ` (${relatedInSimilar})` : ''}
                </button>
            {/if}
            <button
                class="filter-btn"
                class:active={filterStudio}
                disabled={!video.studio}
                onclick={() => { filterStudio = !filterStudio; }}
            >
                SAME STUDIO
            </button>
            <button
                class="filter-btn"
                class:active={filterCollection}
                disabled={!video.collection}
                onclick={() => { filterCollection = !filterCollection; }}
            >
                SAME COLLECTION
            </button>
            <button
                class="filter-btn"
                class:active={filterActors}
                disabled={!video.actors?.length}
                onclick={() => { filterActors = !filterActors; }}
            >
                SAME ACTORS
            </button>
        </div>
    </div>

    {#if loading}
        <div class="similar-center">
            <Spinner />
        </div>
    {:else if pager.visible.length > 0}
        <div class="card-grid">
            {#each pager.visible as v (v.hash)}
                <VideoCard video={v} />
            {/each}
        </div>
        {#if pager.hasMore}
            <div class="load-more-wrap">
                <button class="load-more" onclick={pager.loadMore}>
                    LOAD MORE RESULTS
                </button>
            </div>
        {/if}
    {:else if !loading && similar.length > 0}
        <p class="no-results">No results match the active filters.</p>
    {/if}
</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .similar-section {
        max-width: 120rem;
        width: 100%;
        margin: 0 auto;
        padding: 1.5rem 4rem 2rem;
        border-top: 1px solid #1a1a1a;
    }

    .similar-header {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin-bottom: 1rem;
        margin-left: 5rem;
    }

    .similar-title-row {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
    }

    .similar-title {
        color: #aaa;
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .query-time {
        font-size: 0.72rem;
        color: #444;
        font-weight: 400;
        letter-spacing: 0;
    }

    .active-filter-tags {
        font-size: 0.72rem;
        color: #666;
        font-style: italic;
        font-weight: 400;
        letter-spacing: 0;
    }

    .filter-btns {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .filter-btn {
        background: #111;
        border: 1px solid #2a2a2a;
        color: #666;
        border-radius: 4px;
        padding: 0.3rem 0.75rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s;
    }
    .filter-btn:hover:not(:disabled):not(.active) {
        border-color: #555;
        color: #ccc;
    }
    .filter-btn.active {
        border-color: #D79C29;
        color: #D79C29;
    }
    .filter-btn.active:hover:not(:disabled) {
        border-color: #b07e1a;
        color: #b07e1a;
    }
    .filter-btn:disabled {
        opacity: 0.3;
        cursor: default;
        pointer-events: none;
    }

    .card-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 3px;
    }

    .similar-center {
        display: flex;
        justify-content: center;
        padding: 3rem 0;
    }

    .no-results {
        color: #555;
        font-size: 0.85rem;
        padding: 1rem 0;
        margin-bottom: 50rem;
    }

    .load-more-wrap {
        display: flex;
        justify-content: center;
        margin-top: 1.5rem;
    }

    .load-more {
        background: #151515;
        color: #aaa;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 0.1em;
        cursor: pointer;
        transition: border-color 0.15s, color 0.15s;
    }
    .load-more:hover {
        border-color: #666;
        color: #eee;
    }
</style>
