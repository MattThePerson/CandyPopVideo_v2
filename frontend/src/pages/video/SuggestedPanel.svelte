<!-- pages/video/SuggestedPanel.svelte -->
<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import DefaultCard from '$lib/components/cards/DefaultCard.svelte';

    /* Props */
    let { suggested = [], loading = false, onRefetch }: {
        suggested?: VideoData[];
        loading?: boolean;
        onRefetch?: (p: { ignoreLast: string; popMult: number; platMult: number; poolSize: number }) => void;
    } = $props();

    let sidebarOpen   = $state(false);
    let hasBeenOpened = $state(false);
    let loadedCount   = $state(2);

    $effect(() => { if (suggested.length) loadedCount = 2; });

    const visibleVideos = $derived(suggested.slice(0, loadedCount));
    const canLoadMore   = $derived(loadedCount < suggested.length);
    const nextHref      = $derived(suggested[0] ? `/video/${suggested[0].hash}` : null);

    let wrapEl:    HTMLDivElement    | undefined;
    let sidebarEl: HTMLDivElement    | undefined;
    let popupEl:   HTMLDivElement    | undefined;
    let gearBtnEl: HTMLButtonElement | undefined;

    let sidebarMaxHeight    = $state('0px');
    let sidebarBottomOffset = $state('3rem');

    async function loadNext() {
        loadedCount++;
        await tick();
        if (sidebarEl) sidebarEl.scrollTo({ top: sidebarEl.scrollHeight, behavior: 'smooth' });
    }

    // max-height = distance from viewport top to the buttons row, minus a top buffer.
    function updateMaxHeight() {
        if (!wrapEl) return;
        const topPx = wrapEl.getBoundingClientRect().top;
        sidebarMaxHeight = `${Math.max(0, topPx - 100)}px`;
    }

    function toggleSidebar() {
        if (!sidebarOpen) { hasBeenOpened = true; updateMaxHeight(); }
        sidebarOpen = !sidebarOpen;
    }

    function onDocClick(e: MouseEvent) {
        const t = e.target as Node;
        if (sidebarOpen  && wrapEl  && !wrapEl.contains(t))  sidebarOpen  = false;
        if (settingsOpen && popupEl && !popupEl.contains(t)
            && gearBtnEl && !gearBtnEl.contains(t))          settingsOpen = false;
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

    // ── Settings ──────────────────────────────────────────────────────────────

    let settingsOpen  = $state(false);
    let ignoreLast    = $state('24h');
    let popMult       = $state('1.0');
    let platMult      = $state('1.0');
    let poolSize      = $state('128');
    let ignoreLastErr = $state(false);
    let popMultErr    = $state(false);
    let platMultErr   = $state(false);
    let poolSizeErr   = $state(false);

    const DURATION_RE = /^\d+(\.\d+)?\s*(ns|us|µs|ms|s|m|h|days?|d)$/i;

    function validate(): boolean {
        ignoreLastErr = !DURATION_RE.test(ignoreLast.trim());
        popMultErr    = isNaN(+popMult)  || +popMult  < 0 || +popMult  > 5;
        platMultErr   = isNaN(+platMult) || +platMult < 0 || +platMult > 5;
        poolSizeErr   = !Number.isInteger(+poolSize)  || +poolSize <= 0;
        return !ignoreLastErr && !popMultErr && !platMultErr && !poolSizeErr;
    }

    function onFieldKeydown(e: KeyboardEvent) {
        if (e.key !== 'Enter') return;
        (e.currentTarget as HTMLElement).blur();
        if (validate()) onRefetch?.({ ignoreLast: ignoreLast.trim(), popMult: +popMult, platMult: +platMult, poolSize: +poolSize });
    }

    function restoreDefaults() {
        ignoreLast = '24h'; popMult = '1.0'; platMult = '1.0'; poolSize = '128';
        ignoreLastErr = false; popMultErr = false; platMultErr = false; poolSizeErr = false;
        onRefetch?.({ ignoreLast: '24h', popMult: 1, platMult: 1, poolSize: 128 });
    }

    function toggleSettings() { settingsOpen = !settingsOpen; }

    // Push the overlay up by the popup height when settings are open.
    $effect(() => {
        sidebarBottomOffset = settingsOpen && popupEl
            ? `calc(3rem + ${popupEl.getBoundingClientRect().height + 6}px)`
            : '3rem';
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="sp-wrap" bind:this={wrapEl}>

    <div class="sp-sidebar" class:is-open={sidebarOpen} aria-hidden={!sidebarOpen} style="bottom: {sidebarBottomOffset}">
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
        <div class="sp-settings-wrap">
            {#if settingsOpen}
                <div class="sp-popup" bind:this={popupEl}>
                    <div class="sp-popup-row">
                        <label class="sp-lbl">Ignore last</label>
                        <input class="sp-inp" class:sp-err={ignoreLastErr} bind:value={ignoreLast} onkeydown={onFieldKeydown} />
                    </div>
                    <div class="sp-popup-row">
                        <label class="sp-lbl">Popularity ×</label>
                        <input class="sp-inp" class:sp-err={popMultErr}    bind:value={popMult}    onkeydown={onFieldKeydown} />
                    </div>
                    <div class="sp-popup-row">
                        <label class="sp-lbl">Platform ×</label>
                        <input class="sp-inp" class:sp-err={platMultErr}   bind:value={platMult}   onkeydown={onFieldKeydown} />
                    </div>
                    <div class="sp-popup-row">
                        <label class="sp-lbl">Pool size</label>
                        <input class="sp-inp" class:sp-err={poolSizeErr}   bind:value={poolSize}   onkeydown={onFieldKeydown} />
                    </div>
                    <button class="sp-restore" onclick={restoreDefaults}>Restore defaults</button>
                </div>
            {/if}
            <button class="sp-btn sp-gear" class:active={settingsOpen} onclick={toggleSettings} bind:this={gearBtnEl} aria-label="Suggestion settings">⚙</button>
        </div>
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
       overflow: hidden clips the translateX'd inner as it slides.
       bottom is set via inline style so the settings popup can push it up. */
    .sp-sidebar {
        position: absolute;
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

    /* ── Settings popup ── */

    .sp-settings-wrap {
        position: relative;
    }

    .sp-popup {
        position: absolute;
        bottom: calc(100% + 6px);
        right: 0;
        z-index: 2002;
        background: #1a1a1a;
        border: 1px solid #3a3a3a;
        border-radius: 5px;
        padding: 0.6rem 0.75rem;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        min-width: 12.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    }

    .sp-popup-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.8rem;
    }

    .sp-lbl {
        font-size: 0.63rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #666;
        white-space: nowrap;
    }

    .sp-inp {
        all: unset;
        box-sizing: border-box;
        font-size: 0.7rem;
        font-family: monospace;
        color: #ccc;
        background: #111;
        border: 1px solid #333;
        border-radius: 3px;
        padding: 0.18rem 0.4rem;
        width: 4.5rem;
        text-align: right;
        transition: border-color 0.15s;
    }
    .sp-inp:focus { border-color: #555; outline: none; }
    .sp-inp.sp-err { border-color: #800; color: #f66; }

    .sp-restore {
        all: unset;
        cursor: pointer;
        font-family: inherit;
        font-size: 0.6rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #444;
        text-align: center;
        padding-top: 0.35rem;
        margin-top: 0.1rem;
        border-top: 1px solid #2a2a2a;
        transition: color 0.15s;
    }
    .sp-restore:hover { color: #777; }

    .sp-gear { font-size: 0.9rem; padding: 0.22rem 0.48rem; }

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
