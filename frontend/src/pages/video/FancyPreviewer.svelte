<!-- pages/video/FancyPreviewer.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import InteractionsRow from './InteractionsRow.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    const posterUrl = `/media/get/poster/${hash}`;

    // --- Media state ---
    let previewUrls   = $state<string[]>([]);
    let thumbsLoading = $state(true);
    let teaserUrl        = $state<string | null>(null);
    let videoEl          = $state<HTMLVideoElement | undefined>(undefined);
    let teaserPaused     = $state(false);
    let teaserProgress   = $state(0); // 0–100
    let thumbsGenerating = $state(false);
    let teaserGenerating = $state(false);
    let genPopup         = $state<'thumbs' | 'teaser' | null>(null);

    type Mode = 'poster' | 'thumbs' | 'teaser';
    let mode       = $state<Mode>('poster');
    let currentIdx = $state(0);
    let pendingIdx = $state<number | null>(null);
    let crossfading = $state(false);

    // Incremented on every manual jump to abort in-flight crossfade async.
    let cycleGen = 0;

    // --- Auto-cycle (persisted to localStorage) ---
    const AC_KEY  = 'fp_autocycle';
    let autoCycle = $state(
        typeof localStorage !== 'undefined'
            ? localStorage.getItem(AC_KEY) !== 'false'
            : true
    );
    let cycleTimer: ReturnType<typeof setTimeout> | null = null;
    const CYCLE_MS = 5000;

    // --- Aspect ratio ---
    let containerEl: HTMLDivElement | undefined;
    let mediaAspect  = $state(16 / 9);

    // --- Pip drag ---
    let isDragging = false;
    let ribbonEl:   HTMLDivElement | undefined;

    // --- Derived ---
    const displayBase = $derived(
        mode === 'thumbs' && previewUrls.length > 0
            ? previewUrls[currentIdx]
            : posterUrl
    );
    const displayCross = $derived(
        pendingIdx !== null && previewUrls.length > 0
            ? previewUrls[pendingIdx]
            : null
    );

    const title        = $derived(video.title || video.scene_title || video.filename || '');
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
        return h > 0 ? `${h}h ${String(m).padStart(2, '0')}m ${sec}s` : `${m}m ${sec}s`;
    }

    function fmtBitrate(bps: number) { return bps ? Math.round(bps / 1000) + ' kbps' : ''; }
    function fmtFilesize(mb: number)  { return mb  ? (mb >= 1000 ? (mb / 1024).toFixed(1) + ' GB' : Math.round(mb) + ' MB') : ''; }

    const TAG_LIMIT   = 7;
    let tagsExpanded  = $state(false);
    let descExpanded  = $state(false);
    const visibleTags = $derived(tagsExpanded ? (video.tags ?? []) : (video.tags ?? []).slice(0, TAG_LIMIT));
    const hiddenCount = $derived((video.tags?.length ?? 0) - TAG_LIMIT);

    const stats = $derived([
        video.duration_seconds ? { label: 'Duration',   value: formatDuration(video.duration_seconds) } : null,
        video.height           ? { label: 'Resolution', value: `${video.height}p` }                    : null,
        video.fps              ? { label: 'Frame rate', value: `${video.fps} fps` }                    : null,
        video.bitrate          ? { label: 'Bitrate',    value: fmtBitrate(video.bitrate) }             : null,
        video.filesize_mb      ? { label: 'File size',  value: fmtFilesize(video.filesize_mb) }        : null,
    ].filter(Boolean) as { label: string; value: string }[]);

    function searchHref(key: string, value: string) {
        return `/search?${key}=${encodeURIComponent(value)}`;
    }

    // Play/pause teaser video when mode changes. Tracked because videoEl is $state.
    $effect(() => {
        if (!videoEl) return;
        if (mode === 'teaser') { teaserPaused = false; videoEl.play().catch(() => {}); }
        else videoEl.pause();
    });

    function pauseTeaser()   { if (!videoEl) return; teaserPaused ? videoEl.play().catch(() => {}) : videoEl.pause(); }
    function restartTeaser() { if (!videoEl) return; videoEl.currentTime = 0; videoEl.play().catch(() => {}); }

    async function generateThumbs() {
        genPopup = null;
        thumbsGenerating = true;
        try {
            await fetch(`/media/ensure/preview-thumbs/${hash}`);
            const res = await fetch(`/media/get/preview-thumbs/${hash}?large=true`);
            if (res.ok) {
                const files: string[] = await res.json();
                previewUrls = files.map(f => `/media/preview/${hash}/previewthumbs/${f}`);
            }
        } finally {
            thumbsGenerating = false;
        }
    }

    async function generateTeaser() {
        genPopup = null;
        teaserGenerating = true;
        try {
            await fetch(`/media/ensure/teaser-large/${hash}`);
            const res = await fetch(`/media/preview/${hash}/teaser_large.mp4`, { method: 'HEAD' });
            if (res.ok) teaserUrl = `/media/preview/${hash}/teaser_large.mp4`;
        } finally {
            teaserGenerating = false;
        }
    }

    onMount(async () => {
        updateMediaWidth();
        window.addEventListener('resize', updateMediaWidth);
        document.addEventListener('visibilitychange', onVisibility);

        // Fetch teaser existence + preview thumbs in parallel.
        // Priority: teaser > thumbs > poster.
        const teaserPath = `/media/preview/${hash}/teaser_large.mp4`;
        const [teaserRes, thumbsRes] = await Promise.allSettled([
            fetch(teaserPath, { method: 'HEAD' }),
            fetch(`/media/get/preview-thumbs/${hash}?large=true`),
        ]);

        if (teaserRes.status === 'fulfilled' && teaserRes.value.ok) {
            teaserUrl = teaserPath;
            mode = 'teaser';
        }

        if (thumbsRes.status === 'fulfilled' && thumbsRes.value.ok) {
            const files: string[] = await (thumbsRes.value as Response).json();
            if (files.length > 0) {
                previewUrls = files.map(f => `/media/preview/${hash}/previewthumbs/${f}`);
                if (mode !== 'teaser') { mode = 'thumbs'; scheduleCycle(); }
            }
        }

        thumbsLoading = false;
    });

    onDestroy(() => {
        clearCycle();
        window.removeEventListener('resize', updateMediaWidth);
        document.removeEventListener('visibilitychange', onVisibility);
    });

    function onVisibility() {
        if (document.visibilityState === 'hidden') {
            clearCycle();
        } else if (autoCycle && mode === 'thumbs') {
            scheduleCycle();
        }
    }

    function updateMediaWidth() {
        if (!containerEl) return;
        const mw = Math.min(containerEl.clientHeight * mediaAspect, containerEl.clientWidth);
        containerEl.style.setProperty('--media-col-w', `${mw}px`);
    }

    // Read true aspect ratio from the first loaded image; update shadow width.
    function onBaseImgLoad(e: Event) {
        const img = e.target as HTMLImageElement;
        if (!img.naturalWidth || !img.naturalHeight) return;
        const ar = img.naturalWidth / img.naturalHeight;
        if (Math.abs(ar - mediaAspect) > 0.05) { mediaAspect = ar; updateMediaWidth(); }
    }

    function onVideoMetadata(e: Event) {
        const v = e.target as HTMLVideoElement;
        if (!v.videoWidth || !v.videoHeight) return;
        const ar = v.videoWidth / v.videoHeight;
        if (Math.abs(ar - mediaAspect) > 0.05) { mediaAspect = ar; updateMediaWidth(); }
    }

    // --- Auto-cycle ---
    function scheduleCycle() {
        clearCycle();
        if (!autoCycle || mode !== 'thumbs' || previewUrls.length <= 1) return;
        cycleTimer = setTimeout(advanceCycle, CYCLE_MS);
    }

    function clearCycle() {
        if (cycleTimer !== null) { clearTimeout(cycleTimer); cycleTimer = null; }
    }

    async function advanceCycle() {
        if (previewUrls.length <= 1) return;
        const gen  = ++cycleGen;
        const next = (currentIdx + 1) % previewUrls.length;
        pendingIdx  = next;
        crossfading = true;
        await new Promise<void>(r => setTimeout(r, 500));
        if (gen !== cycleGen) return; // manual jump happened mid-fade
        currentIdx  = next;
        crossfading = false;
        pendingIdx  = null;
        scheduleCycle();
    }

    function jumpTo(idx: number) {
        cycleGen++;        // abort any in-flight advanceCycle
        clearCycle();
        currentIdx  = idx;
        crossfading = false;
        pendingIdx  = null;
        scheduleCycle();
    }

    function toggleAutoCycle() {
        autoCycle = !autoCycle;
        localStorage.setItem(AC_KEY, String(autoCycle));
        if (autoCycle) scheduleCycle(); else clearCycle();
    }

    function setMode(m: Mode) {
        if (m === mode) return;
        clearCycle();
        mode        = m;
        currentIdx  = 0;
        crossfading = false;
        pendingIdx  = null;
        if (m === 'thumbs') scheduleCycle();
    }

    // --- Pip drag (pointer-capture on ribbon container) ---
    function onRibbonPointerDown(e: PointerEvent) {
        isDragging = true;
        (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
        hitPip(e);
    }

    function onRibbonPointerMove(e: PointerEvent) {
        if (!isDragging) return;
        hitPip(e);
    }

    function onRibbonPointerUp() { isDragging = false; }

    function hitPip(e: PointerEvent) {
        if (!ribbonEl || previewUrls.length === 0) return;
        const rect  = ribbonEl.getBoundingClientRect();
        const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const idx   = Math.min(Math.floor(ratio * previewUrls.length), previewUrls.length - 1);
        if (idx !== currentIdx) jumpTo(idx);
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="fancy-previewer" bind:this={containerEl}>

    <!-- Media layers — right-aligned, width follows aspect ratio via --media-col-w -->
    <div class="fp-media">
        <img class="fp-img-base" class:hidden={mode === 'teaser'} src={displayBase} alt="" onload={onBaseImgLoad} />
        <img class="fp-img-cross" class:is-fading={crossfading} class:hidden={mode === 'teaser'} src={displayCross ?? displayBase} alt="" />
        {#if teaserUrl}
            <video
                class="fp-teaser-video"
                class:is-active={mode === 'teaser'}
                bind:this={videoEl}
                src={teaserUrl}
                muted
                playsinline
                onloadedmetadata={onVideoMetadata}
                onpause={() => { teaserPaused = true; }}
                onplay={() => { teaserPaused = false; }}
                onended={() => setMode(previewUrls.length > 0 ? 'thumbs' : 'poster') }
                ontimeupdate={(e) => { const v = e.target as HTMLVideoElement; if (v.duration) teaserProgress = (v.currentTime / v.duration) * 100; }}
            ></video>
        {/if}
    </div>

    <!-- Solid black zone fills left of media area -->
    <div class="fp-dark-zone"></div>

    <!-- Gradient shadow bleeds from the left edge of the media inward -->
    <div class="fp-shadow-zone"></div>

    <!-- Info panel: bottom-left, inside the dark+shadow gradient zone -->
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

    <!-- Interactions row: bottom-left -->
    <div class="fp-interact">
        <InteractionsRow {hash} {interact} />
    </div>

    <!-- Preview media controls: bottom-right -->
    <div class="fp-controls">

        <!-- Mode tabs -->
        <div class="fp-modes">
            <button
                class="fp-mode-btn"
                class:active={mode === 'poster'}
                onclick={() => setMode('poster')}
            >Poster</button>

            <button
                class="fp-mode-btn"
                class:active={mode === 'thumbs' && previewUrls.length > 0}
                onclick={() => {
                    if (previewUrls.length > 0) setMode('thumbs');
                    else if (!thumbsGenerating && !thumbsLoading) genPopup = genPopup === 'thumbs' ? null : 'thumbs';
                }}
            >
                Thumbs
                {#if thumbsGenerating}
                    <span class="fp-spinner"></span>
                {:else if !thumbsLoading && previewUrls.length === 0}
                    <span class="fp-mode-badge">none</span>
                {/if}
            </button>

            <button
                class="fp-mode-btn"
                class:active={mode === 'teaser'}
                onclick={() => {
                    if (teaserUrl) setMode('teaser');
                    else if (!teaserGenerating && !thumbsLoading) genPopup = genPopup === 'teaser' ? null : 'teaser';
                }}
            >
                Teaser
                {#if teaserGenerating}
                    <span class="fp-spinner"></span>
                {:else if !teaserUrl && !thumbsLoading}
                    <span class="fp-mode-badge">none</span>
                {/if}
            </button>
        </div>

        <!-- Inline generation confirm popup -->
        {#if genPopup}
            <div class="fp-gen-popup">
                <p class="fp-gen-msg">
                    {genPopup === 'thumbs'
                        ? 'Generate ML preview thumbs? (~2 min)'
                        : 'Generate large teaser video? (~1 min)'}
                </p>
                <div class="fp-gen-btns">
                    <button class="fp-gen-confirm" onclick={genPopup === 'thumbs' ? generateThumbs : generateTeaser}>Generate</button>
                    <button class="fp-gen-cancel"  onclick={() => genPopup = null}>Cancel</button>
                </div>
            </div>
        {/if}

        <!-- Teaser playback controls -->
        {#if mode === 'teaser'}
            <div class="fp-cycle-row">
                <button class="fp-ac-btn" onclick={pauseTeaser} title={teaserPaused ? 'Resume' : 'Pause'} aria-label={teaserPaused ? 'Resume teaser' : 'Pause teaser'}>{teaserPaused ? '►' : 'II'}</button>
                <button class="fp-ac-btn" onclick={restartTeaser} title="Restart" aria-label="Restart teaser">↺</button>
                <div class="fp-video-progress" style="width: {teaserProgress}%"></div>
            </div>
        {/if}

        <!-- Cycle controls: visible in thumbs mode -->
        {#if mode === 'thumbs'}
            {#if previewUrls.length > 0}
                <div class="fp-cycle-row">
                    <button
                        class="fp-ac-btn"
                        class:is-active={autoCycle}
                        onclick={toggleAutoCycle}
                        title={autoCycle ? 'Disable auto-cycle' : 'Enable auto-cycle'}
                        aria-label={autoCycle ? 'Disable auto-cycle' : 'Enable auto-cycle'}
                        aria-pressed={autoCycle}
                    >
                        {#if autoCycle && previewUrls.length > 1}
                            {#key currentIdx}
                                <div class="fp-progress" style="animation-duration: {CYCLE_MS}ms"></div>
                            {/key}
                        {/if}
                        <span class="fp-ac-icon">↻</span>
                    </button>

                    <div
                        class="fp-ribbon"
                        bind:this={ribbonEl}
                        role="group"
                        aria-label="Thumbnail selector"
                        onpointerdown={onRibbonPointerDown}
                        onpointermove={onRibbonPointerMove}
                        onpointerup={onRibbonPointerUp}
                        onpointercancel={onRibbonPointerUp}
                    >
                        {#each previewUrls as _, i}
                            <div
                                class="fp-pip"
                                class:is-active={i === currentIdx}
                                role="button"
                                tabindex={-1}
                                aria-label="Thumbnail {i + 1}"
                            ></div>
                        {/each}
                    </div>
                </div>
            {/if}
        {/if}

    </div>


</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .fancy-previewer {
        position: absolute;
        inset: 0;
        z-index: 1000;
        overflow: hidden;
        background: #000;
        border-bottom: 1px solid rgba(236, 237, 227, 0.3);
        --media-col-w: 100%; /* JS overrides with aspect-ratio-correct value */
    }

    /* ── Media area: right-aligned, sized to aspect ratio ── */
    .fp-media {
        position: absolute;
        top: 0;
        right: 0;
        width: var(--media-col-w);
        height: 100%;
        overflow: hidden;
    }

    .fp-img-base,
    .fp-img-cross {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
        display: block;
        user-select: none;
        filter: sepia(0.1) grayscale(0.07) brightness(0.93);
    }

    .fp-img-cross { opacity: 0; }

    /* Only apply the transition while the fade is in progress. Removing the class
       makes opacity snap back to 0 instantly (no fade-away artifact). */
    .fp-img-cross.is-fading {
        opacity: 1;
        transition: opacity 0.5s ease;
    }

    .fp-img-base.hidden,
    .fp-img-cross.hidden { display: none; }

    .fp-teaser-video {
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: none;
    }
    .fp-teaser-video.is-active { display: block; }

    /* ── Dark zone: solid black filling left of media area ── */
    .fp-dark-zone {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        width: calc(100% - var(--media-col-w));
        background: #000;
        pointer-events: none;
    }

    /* ── Shadow zone: gradient bleed from left edge of media area ── */
    .fp-shadow-zone {
        position: absolute;
        top: 0;
        left: calc(100% - var(--media-col-w));
        right: 0;
        bottom: 0;
        pointer-events: none;
        box-shadow:
            inset 2.5em -2.5em 3.5em #000,
            inset 6em -6em 11em #000d,
            inset 0 0 0 #0000
        ;
        /*box-shadow: inset 4em -1em 5em #000, inset 7em -13em 14em #000;*/
    }

    /* ── Info panel ── */
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

    .fp-year   { font-size: 0.95rem; font-weight: 600; color: #888; }

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

    .fp-actor { color: #999; text-decoration: none; transition: color 0.12s; }
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

    .fp-stat { font-size: 0.88rem; font-weight: 500; color: #666; letter-spacing: 0.02em; cursor: default; }
    .fp-sep  { font-size: 0.5rem; color: #333; vertical-align: middle; }

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

    .fp-desc-wrap { max-width: 27rem; max-height: 3.6rem; overflow: hidden; margin-left: 1.8rem; }
    .fp-desc-wrap.fp-desc-expanded { max-height: none; }
    .fp-desc { margin: 0; font-size: 0.82rem; color: #666; line-height: 1.5; }

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

    /* ── Interactions row ── */
    .fp-interact {
        position: absolute;
        bottom: 1rem;
        left: 2rem;
        z-index: 20;
    }

    /* ── Controls panel: top-left ── */
    .fp-controls {
        position: absolute;
        top: 0.75rem;
        left: 0.75rem;
        z-index: 20;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
    }

    /* Mode tab strip */
    .fp-modes {
        display: flex;
        gap: 1px;
        background: rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 5px;
        padding: 2px;
        backdrop-filter: blur(6px);
    }

    .fp-mode-btn {
        background: none;
        border: none;
        color: #777;
        font-size: 0.67rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.22rem 0.55rem;
        border-radius: 3px;
        cursor: pointer;
        transition: color 0.15s, background 0.15s;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-family: inherit;
    }
    .fp-mode-btn:hover:not(:disabled) { color: #bbb; }
    .fp-mode-btn.active {
        background: rgba(255, 255, 255, 0.09);
        color: #d0d0d0;
    }

    .fp-mode-btn:disabled { cursor: not-allowed; color: #555; }

    .fp-mode-badge {
        font-size: 0.58rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        color: #3a3a3a;
        opacity: 0.8;
    }

    /* Cycle row: auto-cycle toggle + pip ribbon / teaser controls */
    .fp-cycle-row {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        background: rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 5px;
        padding: 0.28rem 0.5rem;
        backdrop-filter: blur(6px);
        position: relative;
        overflow: hidden;
    }

    .fp-video-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 2px;
        background: rgba(255, 255, 255, 0.45);
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.25);
        border-radius: 0 1px 1px 0;
        pointer-events: none;
        transition: width 0.25s linear;
    }

    /* Auto-cycle toggle button */
    .fp-ac-btn {
        width: 1.1rem;
        height: 1.1rem;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 3px;
        color: #555;
        font-size: 0.65rem;
        line-height: 1;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: color 0.15s, background 0.15s, border-color 0.15s;
        flex-shrink: 0;
        font-family: inherit;
        position: relative;
        overflow: hidden;
    }
    .fp-ac-btn:hover {
        color: #777;
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(255, 255, 255, 0.18);
    }
    .fp-ac-btn.is-active {
        color: #D79C29;
        border-color: rgba(215, 156, 41, 0.45);
        background: rgba(215, 156, 41, 0.1);
    }

    .fp-ac-icon {
        position: relative;
        z-index: 1;
    }

    .fp-progress {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 0%;
        background: rgba(215, 156, 41, 0.28);
        animation: fp-fill linear forwards;
        pointer-events: none;
    }

    @keyframes fp-fill {
        from { height: 0%; }
        to   { height: 100%; }
    }

    /* Pip ribbon */
    .fp-ribbon {
        display: flex;
        align-items: center;
        gap: 3px;
        cursor: pointer;
        user-select: none;
        padding: 5px 1px;
        max-width: 40rem;
    }

    .fp-pip {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        flex-shrink: 0;
        transition: background 0.12s, border-color 0.12s, transform 0.12s;
        pointer-events: none; /* ribbon container handles all pointer events */
    }
    .fp-pip.is-active {
        background: rgba(255, 255, 255, 0.82);
        border-color: rgba(255, 255, 255, 0.9);
        transform: scale(1.2);
    }

    /* Inline spinner inside mode buttons */
    .fp-spinner {
        display: inline-block;
        width: 0.55rem;
        height: 0.55rem;
        border: 1.5px solid rgba(255, 255, 255, 0.12);
        border-top-color: rgba(255, 255, 255, 0.55);
        border-radius: 50%;
        animation: fp-spin 0.7s linear infinite;
        flex-shrink: 0;
    }

    @keyframes fp-spin { to { transform: rotate(360deg); } }

    /* Generation confirm popup */
    .fp-gen-popup {
        background: rgba(10, 10, 10, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        padding: 0.45rem 0.6rem;
        backdrop-filter: blur(8px);
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        min-width: 13rem;
    }

    .fp-gen-msg {
        margin: 0;
        font-size: 0.67rem;
        color: #999;
        letter-spacing: 0.02em;
        line-height: 1.4;
    }

    .fp-gen-btns {
        display: flex;
        gap: 0.3rem;
    }

    .fp-gen-confirm,
    .fp-gen-cancel {
        all: unset;
        cursor: pointer;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-family: inherit;
        transition: color 0.12s, background 0.12s;
    }

    .fp-gen-confirm {
        background: rgba(215, 156, 41, 0.18);
        border: 1px solid rgba(215, 156, 41, 0.35);
        color: #D79C29;
    }
    .fp-gen-confirm:hover {
        background: rgba(215, 156, 41, 0.28);
        border-color: rgba(215, 156, 41, 0.55);
    }

    .fp-gen-cancel {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #555;
    }
    .fp-gen-cancel:hover { color: #888; background: rgba(255, 255, 255, 0.07); }
</style>
