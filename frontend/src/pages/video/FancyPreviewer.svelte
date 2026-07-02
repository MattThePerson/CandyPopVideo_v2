<!-- pages/video/FancyPreviewer.svelte -->
<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import InteractionsRow from './InteractionsRow.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    const posterUrl = `/media/get/poster/${hash}`;

    // Carousel state
    let previewUrls = $state<string[]>([]);
    let stripEl: HTMLDivElement | undefined;
    let rafId: number | null = null;
    let offset = 0;
    let lastTime: number | null = null;
    let paused = $state(false);
    let locked = $state(false);
    const SCROLL_SPEED = 80; // px per second

    const displayUrls = $derived(previewUrls.length > 0 ? previewUrls : [posterUrl]);

    const title = $derived(video.title || video.scene_title || video.filename || '');
    const dateReleased = $derived(
        video.date_released
            ? video.date_released.split(/[ T]/)[0].replace(/-/g, '.')
            : null
    );

    function formatDuration(s: number): string {
        if (!s) return '';
        const h   = Math.floor(s / 3600);
        const m   = Math.floor((s % 3600) / 60);
        const sec = String(Math.floor(s % 60)).padStart(2, '0');
        if (h > 0) return `${h}h ${String(m).padStart(2, '0')}m ${sec}s`;
        return `${m}m ${sec}s`;
    }

    function formatBitrate(bps: number): string {
        if (!bps) return '';
        return Math.round(bps / 1000) + ' kbps';
    }

    function formatFilesize(mb: number): string {
        if (!mb) return '';
        return mb >= 1000 ? (mb / 1024).toFixed(1) + ' GB' : Math.round(mb) + ' MB';
    }

    const TAG_LIMIT  = 7;
    let tagsExpanded = $state(false);
    let descExpanded = $state(false);
    const visibleTags = $derived(tagsExpanded ? (video.tags ?? []) : (video.tags ?? []).slice(0, TAG_LIMIT));
    const hiddenCount = $derived((video.tags?.length ?? 0) - TAG_LIMIT);

    const stats = $derived([
        video.duration_seconds ? { label: 'Duration',    value: formatDuration(video.duration_seconds) } : null,
        video.height           ? { label: 'Resolution',  value: `${video.height}p` }                    : null,
        video.fps              ? { label: 'Frame rate',  value: `${video.fps} fps` }                    : null,
        video.bitrate          ? { label: 'Bitrate',     value: formatBitrate(video.bitrate) }          : null,
        video.filesize_mb      ? { label: 'File size',   value: formatFilesize(video.filesize_mb) }     : null,
    ].filter(Boolean) as { label: string; value: string }[]);

    function searchHref(key: string, value: string): string {
        return `/search?${key}=${encodeURIComponent(value)}`;
    }

    onMount(async () => {
        try {
            const res = await fetch(`/media/get/preview-thumbs/${hash}?large=true`);
            if (res.ok) {
                const filenames: string[] = await res.json();
                if (filenames.length > 0) {
                    previewUrls = filenames.map(f =>
                        `/media/preview/${hash}/previewthumbs/${f}`
                    );
                    // Wait for Svelte to commit the new <img> elements to the DOM,
                    // then wait for at least the first image to have an intrinsic size
                    // so scrollWidth is non-zero when the carousel starts.
                    await tick();
                }
            }
        } catch { /* fall back to poster */ }

        document.addEventListener('visibilitychange', onVisibilityChange);
        startCarousel();
    });

    onDestroy(() => {
        if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null; }
        document.removeEventListener('visibilitychange', onVisibilityChange);
    });

    // Resets lastTime so the first RAF tick after the tab becomes visible again
    // doesn't produce a huge dt spike from all the time elapsed while hidden.
    function onVisibilityChange() {
        if (document.visibilityState === 'visible') lastTime = null;
    }

    function onWheel(e: WheelEvent) {
        e.preventDefault();
        if (!stripEl) return;
        const viewWidth  = stripEl.parentElement?.clientWidth ?? 0;
        const totalWidth = stripEl.scrollWidth;
        const delta = e.deltaY + e.deltaX;
        offset = Math.max(0, Math.min(offset + delta * 2, totalWidth - viewWidth));
        stripEl.style.transform = `translateX(-${offset}px)`;
    }

    function startCarousel() {
        lastTime = null;
        function tick(ts: number) {
            if (lastTime === null) { lastTime = ts; }
            const dt = (ts - lastTime) / 1000;
            lastTime = ts;

            if (stripEl) {
                const viewWidth  = stripEl.parentElement?.clientWidth ?? 0;
                const totalWidth = stripEl.scrollWidth;
                if (!paused) {
                    offset += SCROLL_SPEED * dt;
                    if (offset >= totalWidth - viewWidth) {
                        offset = 0;
                    }
                }
                stripEl.style.transform = `translateX(-${offset}px)`;
            }

            rafId = requestAnimationFrame(tick);
        }
        rafId = requestAnimationFrame(tick);
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="fancy-previewer" onwheel={onWheel}>

    <!-- Scrolling image strip; falls back to poster when no preview thumbs exist -->
    <div class="fp-reel">
        <div class="fp-strip" bind:this={stripEl}>
            {#each displayUrls as url}
                <div class="fp-img-wrap">
                    <img class="fp-img" src={url} alt="" />
                </div>
            {/each}
        </div>
    </div>

    <!-- Interactions panel: bottom-left of the player -->
    <div class="fp-interact">
        <InteractionsRow {hash} {interact} />
    </div>

    <!-- Solid black strip on the far left -->
    <div class="fp-black-strip"></div>

    <!-- Pause button: hover to freeze scroll, top-left inside the black strip -->
    <button
        class="fp-pause-btn"
        class:is-paused={paused}
        class:is-locked={locked}
        onmouseenter={() => { paused = true; }}
        onmouseleave={() => { paused = locked; }}
        onclick={() => { locked = !locked; paused = locked; }}
        aria-label={locked ? 'Resume scroll' : 'Pause scroll'}
    >
        {#if locked}▶{:else}⏸{/if}
    </button>

    <!-- Inset box-shadow fades: start 5rem in so they blend into the black strip -->
    <div class="fp-shadow"></div>
    <div class="fp-shadow-deep"></div>

    <!-- Info panel anchored bottom-left, inside the dark gradient zone -->
    <div class="fp-info">
        <div class="fp-meta-line">
            {#if video.collection}
                <a class="fp-collection" href={searchHref('collection', video.collection)} title="Collection">{video.collection}</a>
            {/if}
            {#if dateReleased}
                <span class="fp-year" title="Date released">{dateReleased}</span>
            {/if}
            {#if video.studio}
                <a class="fp-studio" href={searchHref('studio', video.studio)} title="Studio">{video.studio}</a>
            {/if}
        </div>

        <h2 class="fp-title">{title}</h2>

        {#if video.actors?.length}
            <p class="fp-actors">
                {#each video.actors as actor, i}
                    {#if i > 0}<span class="fp-actor-sep">◆</span>{/if}
                    <a class="fp-actor" href={searchHref('actor', actor)} title="Actor">{actor}</a>
                {/each}
            </p>
        {/if}

        {#if stats.length}
            <div class="fp-stats">
                {#each stats as stat, i}
                    {#if i > 0}<span class="fp-sep">◆</span>{/if}
                    <span class="fp-stat" title={stat.label}>{stat.value}</span>
                {/each}
            </div>
        {/if}

        {#if video.tags?.length}
            <div class="fp-tags">
                {#each visibleTags as tag}
                    <a class="fp-tag" href={searchHref('tags', tag)} title="Tag">{tag}</a>
                {/each}
                {#if hiddenCount > 0 && !tagsExpanded}
                    <button class="fp-tag fp-tag-more" onclick={() => tagsExpanded = true}>+{hiddenCount} more</button>
                {:else if tagsExpanded}
                    <button class="fp-tag fp-tag-more" onclick={() => tagsExpanded = false}>show less</button>
                {/if}
            </div>
        {/if}

        {#if video.description}
            <div class="fp-desc-wrap" class:fp-desc-expanded={descExpanded}>
                <p class="fp-desc">{video.description}</p>
            </div>
            <button class="fp-desc-toggle" onclick={() => descExpanded = !descExpanded}>
                {descExpanded ? 'hide description' : 'show full description'}
            </button>
        {/if}
    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    /* Background: #000 prevents any white flash while images load */
    .fancy-previewer {
        position: absolute;
        inset: 0;
        z-index: 1000;
        overflow: hidden;
        background: #000;
        border-bottom: 1px solid rgba(236, 237, 227, 0.3);
    }

    /* Reel viewport: clips the strip */
    .fp-reel {
        position: absolute;
        inset: 0;
        overflow: hidden;
    }

    /* Strip: images laid out side-by-side in a single row, translated by JS */
    .fp-strip {
        display: flex;
        height: 100%;
    }

    /* Wrapper clips each image to 85% of its natural 16:9 width (= 13.6:9 ratio) */
    .fp-img-wrap {
        height: 100%;
        flex-shrink: 0;
        overflow: hidden;
        aspect-ratio: 13.6 / 9;
    }

    /* Image fills the wrapper; object-fit:cover centers and clips both sides equally */
    .fp-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center center;
        display: block;
        border: none;
        outline: none;
        user-select: none;
        filter: sepia(0.1) grayscale(0.07) brightness(0.93);
    }

    .fp-pause-btn {
        position: absolute;
        top: 0.75rem;
        left: 0.75rem;
        z-index: 30;
        width: 2rem;
        height: 2rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        color: rgba(255, 255, 255, 0.3);
        font-size: 0.7rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.15s, color 0.15s, border-color 0.15s;
    }
    .fp-pause-btn:hover,
    .fp-pause-btn.is-paused {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(255, 255, 255, 0.25);
        color: rgba(255, 255, 255, 0.7);
    }
    .fp-pause-btn.is-locked {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.35);
        color: rgba(255, 255, 255, 0.85);
    }

    /* Solid black strip on the leftmost 14rem — no fade, pure black */
    .fp-black-strip {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: 14rem;
        background: #000;
        pointer-events: none;
    }

    /* Shadow elements shifted 14rem right so they blend into the black strip */
    .fp-shadow,
    .fp-shadow-deep {
        position: absolute;
        top: 0;
        left: 14rem;
        right: 0;
        bottom: 0;
        pointer-events: none;
    }

    /* Tight shadow: crisp darkness right at the left and bottom edges */
    .fp-shadow {
        box-shadow: inset 9em -5em 8em #000;
    }

    /* Wide shadow: broad deep zone extending inward from the same two edges */
    .fp-shadow-deep {
        box-shadow: inset 24em -13em 20em #000;
    }

    /* Interactions panel pinned to bottom-left */
    .fp-interact {
        position: absolute;
        bottom: 1rem;
        left: 2rem;
        z-index: 20;
    }

    /* Info panel: top aligned to vertical centre of the player */
    .fp-info {
        position: absolute;
        bottom: 15%;
        left: 0;
        padding: 0 2rem 0 1.75rem;
        max-width: 37rem;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        z-index: 20;
    }

    .fp-meta-line {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        flex-wrap: wrap;
        margin-left: 0.9rem;
    }

    .fp-collection {
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #D79C29;
        background: rgba(215, 156, 41, 0.1);
        border: 1px solid rgba(215, 156, 41, 0.28);
        border-radius: 3px;
        padding: 0.12rem 0.45rem;
        text-decoration: none;
        transition: color 0.12s, background 0.12s, border-color 0.12s;
    }
    .fp-collection:hover {
        color: #e8b030;
        background: rgba(215, 156, 41, 0.2);
        border-color: rgba(215, 156, 41, 0.55);
    }

    .fp-year {
        font-size: 0.95rem;
        font-weight: 600;
        color: #888;
    }

    .fp-studio {
        font-size: 0.95rem;
        font-weight: 500;
        color: #bbb;
        text-decoration: none;
        transition: color 0.12s;
    }
    .fp-studio:hover { color: #eee; }

    .fp-title {
        margin: 0;
        font-size: 1.95rem;
        font-weight: 700;
        color: #c8c9c0;
        line-height: 1.2;
        text-shadow: 0 2px 14px rgba(0, 0, 0, 0.95);
    }

    .fp-actors {
        margin: 0 0 0 1.8rem;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.5;
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.95);
        max-width: 27rem;
    }

    .fp-actor {
        color: #999;
        text-decoration: none;
        transition: color 0.12s;
    }
    .fp-actor:hover { color: #fff; text-decoration: underline; }

    .fp-actor-sep {
        font-size: 0.55rem;
        color: #3a3a3a;
        vertical-align: middle;
        padding: 0 0.45rem;
    }

    .fp-stats {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        flex-wrap: wrap;
        margin-top: 0.05rem;
        margin-left: 0.9rem;
    }

    .fp-stat {
        font-size: 0.88rem;
        font-weight: 500;
        color: #666;
        letter-spacing: 0.02em;
        cursor: default;
    }

    .fp-sep {
        font-size: 0.5rem;
        color: #333;
        vertical-align: middle;
    }

    .fp-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        row-gap: 3px;
        margin-left: 0.9rem;
    }

    .fp-tag {
        white-space: nowrap;
        font-size: 0.67rem;
        font-weight: 700;
        background: rgba(20, 20, 20, 0.7);
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #777;
        text-decoration: none;
        transition: color 0.12s, background 0.12s;
    }
    .fp-tag:hover { color: #aaa; background: rgba(45, 45, 45, 0.85); }

    .fp-tag-more {
        all: unset;
        cursor: pointer;
        white-space: nowrap;
        font-size: 0.67rem;
        font-weight: 700;
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #555;
        border: 1px solid #2a2a2a;
        transition: color 0.12s, border-color 0.12s;
    }
    .fp-tag-more:hover { color: #999; border-color: #555; }

    .fp-desc-wrap {
        max-width: 27rem;
        max-height: 3.6rem;
        overflow: hidden;
        margin-left: 1.8rem;
    }
    .fp-desc-wrap.fp-desc-expanded { max-height: none; }

    .fp-desc {
        margin: 0;
        font-size: 0.82rem;
        color: #666;
        line-height: 1.5;
    }

    .fp-desc-toggle {
        all: unset;
        cursor: pointer;
        font-size: 0.72rem;
        color: #555;
        max-width: 27rem;
        margin-left: 1.8rem;
        display: block;
        text-align: center;
        transition: color 0.12s;
    }
    .fp-desc-toggle:hover { color: #999; }
</style>
