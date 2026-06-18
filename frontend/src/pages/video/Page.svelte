<!-- pages/video/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import { createPager } from '$lib/util/pager.svelte';
    import VideoPlayer from './VideoPlayer.svelte';
    import VideoDetails from './VideoDetails.svelte';
    import RelatedVideos from './RelatedVideos.svelte';

    /* Props */
    let { hash }: { hash: string } = $props();

    let video          = $state<VideoData | null>(null);
    let interact       = $state<VideoInteractions | null>(null);
    let loadError      = $state<string | null>(null);
    let similar        = $state<VideoData[]>([]);
    let relatedHashes  = $state(new Set<string>());
    let filterRelated  = $state(false);
    let similarLoading = $state(false);
    let queryTime      = $state<number | null>(null);

    const pager = createPager(
        () => filterRelated ? similar.filter(v => !relatedHashes.has(v.hash)) : similar,
        8
    );

    $effect(() => { filterRelated; pager.reset(); });

    onMount(async () => {
        try {
            [video, interact] = await Promise.all([
                fetch(`/api/get/video-data/${hash}`).then(r => r.json()) as Promise<VideoData>,
                fetch(`/api/interact/get/${hash}`).then(r => r.json()) as Promise<VideoInteractions>,
            ]);
        } catch (e) {
            loadError = String(e);
            return;
        }

        similarLoading = true;
        try {
            const res = await fetch(`/api/query/get/similar-videos/${hash}`).then(r => r.json());
            similar   = (res.Videos as VideoData[]).filter(v => v.hash !== hash);
            queryTime = res.TimeTaken as number;
        } catch {
            similar   = [];
            queryTime = null;
        } finally {
            similarLoading = false;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page">

    <!-- video player -->
    <div class="player-wrap">
        {#if loadError}
            <div class="player-error">{loadError}</div>
        {:else if !video}
            <div class="player-center">
                <Spinner size={52} />
            </div>
        {:else}
            <VideoPlayer {hash} title={video.title || video.filename} />
        {/if}
    </div>

    <!-- video details -->
    {#if video && interact}
        <VideoDetails {hash} {video} {interact} />
    {/if}

    <!-- related videos -->
    {#if video}
        <RelatedVideos {video} onRelatedLoaded={(hashes) => { relatedHashes = hashes; }} />
    {/if}

    <!-- similar vidoes -->
    {#if video}
        <section class="similar-section">
            <div class="similar-header">
                <h2 class="similar-title">
                    SIMILAR VIDEOS{queryTime !== null ? ` (${queryTime.toFixed(2)}s)` : ''}
                </h2>
                <button
                    class="filter-btn"
                    class:active={filterRelated}
                    onclick={() => { filterRelated = !filterRelated; }}
                >
                    {filterRelated ? 'SHOWING FILTERED' : 'FILTER RELATED'}
                </button>
            </div>

            {#if similarLoading}
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
            {:else if !similarLoading && similar.length > 0}
                <p class="no-results">All similar videos are hidden by the related filter.</p>
            {/if}
        </section>
    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .page {
        width: 100%;
        padding-bottom: 4rem;
    }

    .player-wrap {
        width: 100%;
        height: 45rem;
        background: #000;
        position: relative;
    }

    .player-center {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .player-error {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f87171;
        font-size: 0.9rem;
    }

    .similar-section {
        padding: 1.5rem 2rem 2rem;
        border-top: 1px solid #1a1a1a;
    }

    .similar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    .similar-title {
        color: #aaa;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
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
    .filter-btn:hover {
        border-color: #555;
        color: #ccc;
    }
    .filter-btn.active {
        border-color: #D79C29;
        color: #D79C29;
    }

    .card-grid {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 1rem;
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
