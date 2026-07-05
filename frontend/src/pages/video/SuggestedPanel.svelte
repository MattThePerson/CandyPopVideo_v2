<!-- pages/video/SuggestedPanel.svelte -->
<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import DefaultCard from '$lib/components/cards/DefaultCard.svelte';

    /* Props */
    let { suggested = [], loading = false }: {
        suggested?: VideoData[];
        loading?: boolean;
    } = $props();

    let sidebarOpen   = $state(false);
    let hasBeenOpened = $state(false);
    let loadedCount   = $state(2);

    // Reset load count when a new video's suggestions arrive.
    $effect(() => {
        if (suggested.length) loadedCount = 2;
    });

    const visibleVideos = $derived(suggested.slice(0, loadedCount));
    const canLoadMore   = $derived(loadedCount < suggested.length);
    const nextHref      = $derived(suggested[0] ? `/video/${suggested[0].hash}` : null);

    let wrapEl: HTMLDivElement | undefined;
    let sidebarEl: HTMLDivElement | undefined;

    async function loadNext() {
        loadedCount++;
        await tick();
        if (sidebarEl) sidebarEl.scrollTo({ top: sidebarEl.scrollHeight, behavior: 'smooth' });
    }
    let sidebarMaxHeight = $state('0px');

    // max-height = distance from viewport top to the buttons row, minus a top buffer
    // so the panel fills exactly between the header and the buttons.
    function updateMaxHeight() {
        if (!wrapEl) return;
        const topPx = wrapEl.getBoundingClientRect().top;
        sidebarMaxHeight = `${Math.max(0, topPx - 100)}px`;
    }

    function toggleSidebar() {
        if (!sidebarOpen) {
            hasBeenOpened = true;
            updateMaxHeight();
        }
        sidebarOpen = !sidebarOpen;
    }

    function onDocClick(e: MouseEvent) {
        if (!sidebarOpen) return;
        if (wrapEl && !wrapEl.contains(e.target as Node)) sidebarOpen = false;
    }

    onMount(() => {
        document.addEventListener('click', onDocClick);
        window.addEventListener('resize', updateMaxHeight);
        updateMaxHeight();
    });
    onDestroy(() => {
        document.removeEventListener('click', onDocClick);
        window.removeEventListener('resize', updateMaxHeight);
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="sp-wrap" bind:this={wrapEl}>

    <div class="sp-sidebar" class:is-open={sidebarOpen} aria-hidden={!sidebarOpen}>
        <div class="sp-inner" class:is-open={sidebarOpen} style="max-height: {sidebarMaxHeight}" bind:this={sidebarEl}>
        {#if hasBeenOpened}
            {#if loading && suggested.length === 0}
                <p class="sp-empty">Loading suggestions…</p>
            {:else if suggested.length === 0}
                <p class="sp-empty">No suggestions found.</p>
            {:else}
                <div class="sp-cards">
                    {#each visibleVideos as video (video.hash)}
                        <DefaultCard {video} size="small" width="100%" aspectRatio="16/9" />
                    {/each}
                </div>
                {#if canLoadMore}
                    <button class="sp-load-next" onclick={loadNext}>Load next</button>
                {/if}
            {/if}
        {/if}
        </div>
    </div>

    <!-- Buttons below the player, flushed right -->
    <div class="sp-buttons">
        <div class="sp-play-wrap">
            {#if nextHref}
                <div class="sp-play-preview" aria-hidden="true">
                    <DefaultCard video={suggested[0]} size="small" width="25.625em" aspectRatio="16/9" />
                </div>
                <a class="sp-btn sp-play" href={nextHref}>
                    Play Next <kbd>F4</kbd>
                </a>
            {:else}
                <span class="sp-btn sp-play sp-disabled">Play Next</span>
            {/if}
        </div>
        <button
            class="sp-btn sp-toggle"
            class:active={sidebarOpen}
            onclick={toggleSidebar}
        >
            Suggested
        </button>
    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .sp-wrap {
        position: relative;
    }

    /* Container: fixed at right: 0, never moves — no page overflow.
       overflow: hidden clips the translateX'd inner as it slides. */
    .sp-sidebar {
        position: absolute;
        bottom: 3rem;
        right: 0;
        width: 21rem;
        overflow: hidden;
        z-index: 2000;
        pointer-events: none;
    }
    .sp-sidebar.is-open {
        pointer-events: auto;
    }

    /* Inner: carries all visual styles and does the actual slide. */
    .sp-inner {
        width: 100%;
        display: flex;
        flex-direction: column;
        /* max-height is set via inline style — computed from wrapEl.getBoundingClientRect().top */
        overflow-y: auto;
        overflow-x: hidden;
        background: #222;
        border: 1px solid #555;
        backdrop-filter: blur(16px);
        box-shadow: -6px 0 24px rgba(0, 0, 0, 0.55);
        padding: 4px;
        border-radius: 0.1rem;
        transform: translateX(100%);
        transition: transform 0.25s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    .sp-inner.is-open {
        transform: translateX(0);
    }

    .sp-inner {
        scrollbar-width: thin;
        scrollbar-color: #777 transparent;
    }
    .sp-inner::-webkit-scrollbar       { width: 4px; }
    .sp-inner::-webkit-scrollbar-track { background: transparent; }
    .sp-inner::-webkit-scrollbar-thumb { background: #444; border-radius: 2px; }
    .sp-inner::-webkit-scrollbar-thumb:hover { background: #555; }

    .sp-cards {
        display: flex;
        flex-direction: column;
        font-size: 0.8rem;
        gap: 4px;
    }

    .sp-load-next {
        all: unset;
        cursor: pointer;
        display: block;
        box-sizing: border-box;
        width: 100%;
        text-align: center;
        font-size: 0.67rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #888;
        padding: 0.65rem;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        font-family: inherit;
        transition: color 0.15s, background 0.15s;
    }
    .sp-load-next:hover { color: #888; background: rgba(255, 255, 255, 0.04); }

    .sp-empty {
        margin: 0;
        padding: 1.1rem;
        font-size: 0.78rem;
        color: #555;
        text-align: center;
    }

    /* ── Buttons ── */

    .sp-play-wrap {
        position: relative;
    }

    .sp-play-preview {
        position: absolute;
        bottom: calc(100% + 6px);
        right: 0;
        font-size: 0.7rem;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.15s;
        z-index: 2001;
    }

    .sp-play-wrap:hover .sp-play-preview {
        opacity: 1;
    }

    .sp-buttons {
        display: flex;
        gap: 0.35rem;
        align-items: center;
        margin-right: 1rem;
    }

    .sp-btn {
        all: unset;
        cursor: pointer;
        font-size: 0.67rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.3rem 0.65rem;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(0, 0, 0, 0.55);
        color: #666;
        font-family: inherit;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        text-decoration: none;
        backdrop-filter: blur(6px);
        white-space: nowrap;
        transition: color 0.15s, background 0.15s, border-color 0.15s;
    }
    .sp-btn:hover { color: #bbb; border-color: rgba(255, 255, 255, 0.18); }

    .sp-play {
        color: #D79C29;
        background: rgba(215, 156, 41, 0.1);
        border-color: rgba(215, 156, 41, 0.3);
    }
    .sp-play:hover {
        color: #e8b030;
        background: rgba(215, 156, 41, 0.18);
        border-color: rgba(215, 156, 41, 0.5);
    }

    .sp-disabled {
        opacity: 0.35;
        cursor: default;
        pointer-events: none;
    }

    .sp-toggle.active {
        background: rgba(255, 255, 255, 0.09);
        color: #d0d0d0;
        border-color: rgba(255, 255, 255, 0.15);
    }

    kbd {
        font-size: 0.58rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 2px;
        padding: 0.05rem 0.28rem;
        font-family: inherit;
        letter-spacing: 0;
    }
</style>
