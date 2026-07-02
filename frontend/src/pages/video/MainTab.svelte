<script lang="ts">
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import ActorCard from '$lib/components/ActorCard.svelte';
    import SceneBox from './SceneBox.svelte';
    import InteractionsRow from './InteractionsRow.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    const displayTitle = (video.title || video.scene_title || video.filename).replaceAll(';', ':');

    // ── Helpers ────────────────────────────────────────────────

    function searchLink(key: string, val: string): string { return `/search?${key}=${encodeURIComponent(val)}`; }
    function navSearch(e: MouseEvent, key: string, val: string) { e.preventDefault(); navigate(searchLink(key, val)); }

    function formatDuration(d: string): string {
        const parts = d.split(':').map(Number);
        if (parts.length === 3) {
            const [h, m, s] = parts;
            if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            return `${m}:${String(s).padStart(2, '0')}`;
        }
        return d;
    }

    function formatBitrate(kbps: number): string { return (Math.floor(kbps / 100) / 10).toFixed(1) + ' MB/s'; }

    function formatFilesize(mb: number): string {
        if (mb >= 1000) return (Math.floor(mb / 100) / 10).toFixed(1) + ' GB';
        return Math.floor(mb) + ' MB';
    }

    function fmtCount(n: number): string {
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
        return String(n);
    }

    const TAG_LIMIT = 7;
    let tagsExpanded = $state(false);
    const visibleTags = $derived(tagsExpanded ? (video.tags ?? []) : (video.tags ?? []).slice(0, TAG_LIMIT));
    const hiddenCount = $derived((video.tags?.length ?? 0) - TAG_LIMIT);
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="main-tab">

    <!-- LEFT COLUMN -->
    <div class="left-col">
        <div class="left-content">

            <!-- Interactions row -->
            <InteractionsRow {hash} {interact} />

            <!-- Title -->
            <h1 class="title">{displayTitle}</h1>

            <!-- Year / collection / studio -->
            <div class="year-studio-bar">
                {#if video.collection}
                    <a class="collection-badge" href={searchLink('collection', video.collection)}
                       onclick={(e) => navSearch(e, 'collection', video.collection)}
                       title="collection">{video.collection}</a>
                {/if}
                {#if video.date_released}
                    <span class="year" title="release date: {video.date_released}">{video.date_released.slice(0, 4)}</span>
                {/if}
                {#if video.studio || video.line}
                    <div class="studios">
                        {#if video.studio}
                            <a href={searchLink('studio', video.studio)}
                               onclick={(e) => navSearch(e, 'studio', video.studio)}
                               title="studio">{video.studio}</a>
                        {/if}
                        {#if video.studio && video.line}<span class="studio-sep"></span>{/if}
                        {#if video.line}
                            <a href={searchLink('studio', video.line)}
                               onclick={(e) => navSearch(e, 'studio', video.line)}
                               title="line">{video.line}</a>
                        {/if}
                    </div>
                {/if}
            </div>

            <!-- Actors -->
            {#if video.actors?.length}
                <div class="actors-container">
                    {#each video.actors as actor}
                        <ActorCard name={actor} dateReleased={video.date_released} />
                    {/each}
                </div>
            {/if}

        </div>
    </div>

    <!-- RIGHT COLUMN -->
    <div class="right-col">

        <!-- Quick stats -->
        <div class="quick-stats-bar">
            {#if video.duration}<span title="duration">{formatDuration(video.duration)}</span>{/if}
            {#if video.height}<span class="sep"></span><span title="resolution">{video.height}p</span>{/if}
            {#if video.fps}<span class="sep"></span><span title="framerate">{video.fps} fps</span>{/if}
            {#if video.bitrate}<span class="sep"></span><span title="bitrate">{formatBitrate(video.bitrate)}</span>{/if}
            {#if video.filesize_mb}<span class="sep"></span><span title="filesize">{formatFilesize(video.filesize_mb)}</span>{/if}
            {#if video.views || video.likes}
                <span class="sep plat-sep"></span>
                {#if video.views}<span class="plat-stat" title="platform views">▶ {fmtCount(video.views)}</span>{/if}
                {#if video.views && video.likes}<span class="sep plat-sep"></span>{/if}
                {#if video.likes}<span class="plat-stat" title="platform likes">♥ {fmtCount(video.likes)}</span>{/if}
            {/if}
        </div>

        <!-- Tags -->
        {#if video.tags?.length}
            <div class="tags-bar">
                {#each visibleTags as tag}
                    <a class="tag-chip" href={searchLink('tag', tag)}
                       onclick={(e) => navSearch(e, 'tag', tag)}
                       title="tag">{tag}</a>
                {/each}
                {#if hiddenCount > 0 && !tagsExpanded}
                    <button class="tag-chip tag-more" onclick={() => tagsExpanded = true}>+{hiddenCount} more</button>
                {:else if tagsExpanded}
                    <button class="tag-chip tag-more" onclick={() => tagsExpanded = false}>show less</button>
                {/if}
            </div>
        {/if}

        <!-- Scene box -->
        <SceneBox {video} {interact} />

    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .main-tab {
        display: flex;
        justify-content: center;
        gap: 2rem;
        padding: 0.75rem 2.5rem 2rem;
        box-sizing: border-box;
    }

    /* ── LEFT COLUMN ─────────────────────────────────────────── */

    .left-col {
        flex: 55;
        min-width: 0;
        max-width: 40rem;
    }

    .left-content {
        display: flex;
        flex-direction: column;
    }

    /* title */
    .title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ecede3;
        line-height: 1.3;
        margin-bottom: 0.25rem;
    }

    /* year-studio-bar */
    .year-studio-bar {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.3rem;
    }

    .collection-badge {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 1px 8px;
        font-weight: 600;
        font-size: 14px;
        color: #ccc;
        text-decoration: none;
    }
    .collection-badge:hover { color: #fff; border-color: #fff; }

    .year {
        font-weight: 700;
        font-size: 16px;
        color: #ddd;
        cursor: default;
    }

    .studios {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 16px;
    }
    .studios a         { color: #bbb; text-decoration: none; }
    .studios a:hover   { text-decoration: underline; color: #eee; }
    .studio-sep        { width: 5px; height: 5px; background: #e33; transform: rotate(45deg); flex-shrink: 0; }

    .actors-container {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.4rem;
    }

    /* ── RIGHT COLUMN ────────────────────────────────────────── */

    .right-col {
        flex: 45;
        min-width: 0;
        max-width: 40rem;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        padding-top: 0.25rem;
    }

    .quick-stats-bar {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.45rem;
    }
    .quick-stats-bar span { font-size: 13px; color: #999; }

    .sep {
        width: 5px;
        height: 5px;
        background: #555;
        transform: rotate(45deg);
        flex-shrink: 0;
        display: inline-block;
    }
    .plat-sep { background: #383838; }
    .plat-stat { color: #c0c0c0 !important; font-weight: 600; }

    .tags-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        row-gap: 3px;
    }
    .tag-chip {
        white-space: nowrap;
        font-size: 0.67rem;
        font-weight: 700;
        background: #151515;
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #888;
        text-decoration: none;
    }
    .tag-chip:hover { background: #222; color: #aaa; }

    .tag-more {
        all: unset;
        cursor: pointer;
        white-space: nowrap;
        font-size: 0.67rem;
        font-weight: 700;
        background: none;
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #555;
        border: 1px solid #2a2a2a;
        transition: color 0.12s, border-color 0.12s;
    }
    .tag-more:hover { color: #999; border-color: #555; }
</style>
