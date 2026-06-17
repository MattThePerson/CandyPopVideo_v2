<script lang="ts">
    import { onMount } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import type { VideoInteractions } from '$lib/types/video';
    import type { CardSize } from '$lib/stores/settings.svelte';
    import { navigate } from '$lib/router/router.svelte';

    let { video, size }: { video: VideoData; size: CardSize } = $props();

    const sizeMap: Record<CardSize, { width: string; aspectRatio: string }> = {
        small:  { width: '20.5rem', aspectRatio: '14/9' },
        medium: { width: '25rem',   aspectRatio: '16/9' },
        large:  { width: '33rem',   aspectRatio: '18/9' },
        xl:     { width: '40rem',   aspectRatio: '19/9' },
    };
    let dims = $derived(sizeMap[size]);

    // ── Interactions ────────────────────────────────────────────────────────────

    let interactions = $state<VideoInteractions | null>(null);
    let isFavourite = $state(false);
    let favLoading = $state(false);

    onMount(async () => {
        try {
            const data = await fetch(`/api/interact/get/${video.hash}`).then(r => r.json()) as VideoInteractions;
            interactions = data;
            isFavourite = data.is_favourite;
        } catch { /* non-critical */ }
    });

    async function toggleFavourite() {
        if (favLoading) return;
        favLoading = true;
        const was = isFavourite;
        isFavourite = !was;
        try {
            await fetch(`/api/interact/favourites/${was ? 'remove' : 'add'}/${video.hash}`, { method: 'POST' });
        } catch {
            isFavourite = was;
        }
        favLoading = false;
    }

    // ── Sprite-sheet teaser ──────────────────────────────────────────────────

    interface SpriteCue { x: number; y: number; w: number; h: number; }

    type TeaserState = 'idle' | 'loading' | 'loaded' | 'failed';
    let teaserState = $state<TeaserState>('idle');
    let spriteCues = $state<SpriteCue[]>([]);
    let spriteSheetSrc = $state('');
    let spriteSheetNW = $state(0);
    let spriteSheetNH = $state(0);
    let showSprite = $state(false);
    let spriteStyle = $state('');

    let spriteLoaded = $derived(teaserState === 'loaded');

    function parseVtt(text: string): SpriteCue[] {
        const cues: SpriteCue[] = [];
        const re = /xywh=(\d+),(\d+),(\d+),(\d+)/g;
        let m;
        while ((m = re.exec(text)) !== null) {
            cues.push({ x: +m[1], y: +m[2], w: +m[3], h: +m[4] });
        }
        return cues;
    }

    async function ensureSprite() {
        if (teaserState !== 'idle') return;
        teaserState = 'loading';
        fetch(`/media/ensure/teaser-thumbs-small/${video.hash}`).catch(() => {});
        try {
            const vttRes = await fetch(`/static/preview-media/0x${video.hash}/teaser_thumbs_small.vtt`);
            if (!vttRes.ok) { teaserState = 'failed'; return; }
            const cues = parseVtt(await vttRes.text());
            if (!cues.length) { teaserState = 'failed'; return; }
            const img = new Image();
            img.src = `/static/preview-media/0x${video.hash}/teaser_thumbs_small.jpg`;
            await new Promise<void>(res => { img.onload = () => res(); img.onerror = () => res(); });
            if (!img.naturalWidth) { teaserState = 'failed'; return; }
            spriteCues = cues;
            spriteSheetSrc = img.src;
            spriteSheetNW = img.naturalWidth;
            spriteSheetNH = img.naturalHeight;
            teaserState = 'loaded';
        } catch {
            teaserState = 'failed';
        }
    }

    function handleMouseEnter() {
        ensureSprite();
    }

    function handleMouseMove(e: MouseEvent) {
        if (!spriteLoaded || !spriteCues.length) return;
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        const pct = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
        const idx = Math.min(Math.floor(pct * spriteCues.length), spriteCues.length - 1);
        const cue = spriteCues[idx];
        const scale = rect.width / cue.w;
        spriteStyle = `background-image:url('${spriteSheetSrc}');background-size:${spriteSheetNW * scale}px ${spriteSheetNH * scale}px;background-position:-${cue.x * scale}px -${cue.y * scale}px;`;
        showSprite = true;
    }

    function handleMouseLeave() {
        showSprite = false;
        spriteStyle = '';
    }

    // ── Actor / tag expansion ────────────────────────────────────────────────

    let actorsExpanded = $state(false);
    let actors = $derived(video.actors ?? []);
    let displayedActors = $derived(actorsExpanded ? actors : actors.slice(0, 4));
    let remainingActors = $derived(!actorsExpanded && actors.length > 4 ? actors.length - 4 : 0);

    let tagsExpanded = $state(false);
    let tags = $derived(video.tags ?? []);
    let displayedTags = $derived.by(() => {
        if (tagsExpanded) return tags;
        let count = 0;
        const shown: string[] = [];
        for (const tag of tags) {
            if (count && count + tag.length > 50) break;
            shown.push(tag);
            count += tag.length + 1;
        }
        return shown;
    });
    let remainingTags = $derived(!tagsExpanded && tags.length > displayedTags.length ? tags.length - displayedTags.length : 0);

    function tagStyle(tag: string): string {
        if (tag.startsWith('character: ')) return 'color:#bbb!important;background:#1e3259;';
        if (tag.startsWith('source: '))    return 'color:#bbb!important;background:#11975a58;';
        return '';
    }

    // ── Formatting ───────────────────────────────────────────────────────────

    function formatDuration(d: string): string {
        return d.startsWith('0:') ? d.slice(2) : d;
    }
    function formatBitrate(kbps: number): string {
        return Math.round(kbps / 100) / 10 + 'mb';
    }
    function formatViews(n: number): string {
        if (n >= 1_000_000_000) return (n / 1_000_000_000).toFixed(1).replace('.0', '') + 'B';
        if (n >= 1_000_000)     return (n / 1_000_000).toFixed(1).replace('.0', '') + 'M';
        if (n >= 1_000)         return (n / 1_000).toFixed(1).replace('.0', '') + 'K';
        return String(n);
    }
    function formatViewtime(sec: number): string {
        if (!sec) return '';
        const h = Math.floor(sec / 3600);
        const m = Math.floor((sec % 3600) / 60);
        const s = Math.floor(sec % 60);
        const parts: string[] = [];
        if (h) parts.push(`${h}h`);
        if (m) parts.push(`${m}m`);
        if (s || !parts.length) parts.push(`${s}s`);
        return parts.join(' ');
    }
    function timeAgo(dateStr: string): string {
        const diff = Math.floor((Date.now() - new Date(dateStr.replace(' ', 'T')).getTime()) / 1000);
        const units: [number, string][] = [
            [31536000, 'year'], [2592000, 'month'], [604800, 'week'],
            [86400, 'day'], [3600, 'hour'], [60, 'minute'], [1, 'second'],
        ];
        for (const [secs, name] of units) {
            const n = Math.floor(diff / secs);
            if (n >= 1) return `${n} ${name}${n !== 1 ? 's' : ''}`;
        }
        return 'just now';
    }
    function formatDateReleased(d: string): string {
        return d.replaceAll('-', '.');
    }
    function isNew(dateAdded: string): boolean {
        return (Date.now() - new Date(dateAdded.replace(' ', 'T')).getTime()) / 1000 < 604800;
    }

    let displayTitle = $derived.by(() => {
        let t = video.title || video.scene_title || video.filename || video.hash;
        t = t.replaceAll(';', ':');
        if (video.dvd_code) t = `[${video.dvd_code}] ${t}`;
        return t.length > 80 ? t.slice(0, 80) + '…' : t;
    });

    let addedAgo    = $derived(video.date_added ? timeAgo(video.date_added) : '');
    let isNewVideo  = $derived(video.date_added ? isNew(video.date_added) : false);
    let viewtimeStr = $derived(interactions ? formatViewtime(interactions.viewtime) : '');
</script>

<div class="card" style="width:{dims.width}">

    <!-- THUMBNAIL -->
    <a
        class="thumb"
        href="/video/{video.hash}"
        style="aspect-ratio:{dims.aspectRatio}"
        onmouseenter={handleMouseEnter}
        onmousemove={handleMouseMove}
        onmouseleave={handleMouseLeave}
    >
        <img class="poster" class:hidden={showSprite} src="/media/get/poster/{video.hash}" alt="" />

        {#if showSprite && spriteStyle}
            <div class="sprite-overlay" style={spriteStyle}></div>
        {/if}

        <div class="stats">
            <!-- top-left: collection + NEW -->
            <div class="stat-topleft">
                {#if video.collection}
                    <button class="collection-badge"
                        onclick={(e) => { e.preventDefault(); navigate(`/search?collection=${encodeURIComponent(video.collection)}`); }}>
                        {video.collection}
                    </button>
                {/if}
                {#if isNewVideo}
                    <span class="new-badge">NEW</span>
                {/if}
            </div>
            <!-- top-right: resolution + bitrate -->
            <div class="stat-topright">
                {#if video.resolution}
                    <span class="chip">{video.resolution}p</span>
                {/if}
                {#if video.bitrate}
                    <span class="chip">{formatBitrate(video.bitrate)}</span>
                {/if}
            </div>
            <!-- bottom-right: duration -->
            {#if video.duration}
                <span class="chip duration-chip">{formatDuration(video.duration)}</span>
            {/if}
            <!-- bottom-left: views -->
            {#if video.views > 0}
                <span class="chip views-chip">{formatViews(video.views)}</span>
            {/if}
        </div>
    </a>

    <!-- CARD INFO -->
    <div class="card-info">

        <!-- DETAILS BAR -->
        <div class="details-bar">
            <div class="details-left">
                {#if interactions}
                    {#if viewtimeStr}
                        <span title="view time">{viewtimeStr}</span>
                    {:else}
                        <span class="muted">not watched</span>
                    {/if}
                    {#if interactions.likes > 0}
                        <span class="likes-row">
                            {interactions.likes}
                            <svg width="10" height="10" viewBox="0 0 16 16">
                                <path d="M8 14s-6-4.35-6-8a4 4 0 0 1 6-3.46A4 4 0 0 1 14 6c0 3.65-6 8-6 8z" fill="rgba(255,0,0,0.77)"/>
                            </svg>
                        </span>
                    {/if}
                    {#if interactions.rating}
                        <span class="rating" title="rating">{interactions.rating}</span>
                    {/if}
                {:else}
                    <span class="muted">vt unknown</span>
                {/if}
            </div>
            <div>
                {#if addedAgo}
                    <span title="date added">{addedAgo} ago</span>
                {/if}
            </div>
        </div>

        <!-- TITLE BAR -->
        <div class="title-bar">
            <button
                class="fav-btn"
                class:loaded={interactions !== null}
                class:is-fav={isFavourite}
                title="toggle favourite"
                onclick={toggleFavourite}
                aria-label="toggle favourite"
            >
                <svg class="off" viewBox="0 0 24 24" fill="none">
                    <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"
                          stroke="rgba(245,245,220,0.8)" stroke-width="1.5"/>
                </svg>
                <svg class="on" viewBox="0 0 24 24" fill="none">
                    <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z"
                          fill="rgba(236,195,59,0.8)"/>
                </svg>
            </button>
            <a class="title-link" href="/video/{video.hash}" title={displayTitle}>
                <h2>{displayTitle}</h2>
            </a>
        </div>

        <!-- STUDIO + ACTORS -->
        <div class="studio-actors">
            {#if video.studio || video.date_released}
                <div class="year-studio-row">
                    {#if video.date_released}
                        <span class="year">{formatDateReleased(video.date_released)}</span>
                    {/if}
                    <div class="studios-row">
                        {#if video.studio}
                            <a href="/search?studio={encodeURIComponent(video.studio)}">{video.studio}</a>
                        {/if}
                        {#if video.studio && video.line}
                            <span class="sep"></span>
                        {/if}
                        {#if video.line}
                            <a href="/search?studio={encodeURIComponent(video.line)}">{video.line}</a>
                        {/if}
                    </div>
                </div>
            {/if}
            {#if actors.length > 0}
                <div class="actors-row">
                    {#each displayedActors as actor, i}
                        {#if i > 0}<span class="sep"></span>{/if}
                        <a href="/search?actor={encodeURIComponent(actor)}">{actor}</a>
                    {/each}
                    {#if remainingActors > 0}
                        <span class="sep"></span>
                        <button class="expand-btn" onclick={() => actorsExpanded = true}>
                            +{remainingActors} more
                        </button>
                    {/if}
                </div>
            {/if}
        </div>

        <!-- TAGS -->
        {#if tags.length > 0}
            <div class="tags-bar">
                {#each displayedTags as tag}
                    <a href="/search?tags={encodeURIComponent(tag)}" class="tag" style={tagStyle(tag)}>
                        {tag}
                    </a>
                {/each}
                {#if remainingTags > 0}
                    <button class="tag expand-tag-btn" onclick={() => tagsExpanded = true}>
                        +{remainingTags} more
                    </button>
                {/if}
            </div>
        {/if}

    </div>
</div>

<style>
    .card {
        border: 1px solid #88888819;
        border-radius: 0.5rem;
        outline: 0.5px solid #4441;
        background: black;
        display: inline-block;
        vertical-align: top;
        cursor: default;
    }

    /* ── Thumbnail ── */

    .thumb {
        position: relative;
        display: flex;
        justify-content: center;
        align-items: center;
        background: #111;
        border-radius: 5px 5px 0 0;
        width: 100%;
        overflow: hidden;
        user-select: none;
        -webkit-user-drag: none;
    }

    .poster {
        height: 100%;
        width: 100%;
        object-fit: cover;
        display: block;
    }

    .poster.hidden { display: none; }

    .sprite-overlay {
        position: absolute;
        inset: 0;
        pointer-events: none;
    }

    /* ── Stats overlay ── */

    .stats {
        position: absolute;
        inset: 0;
        pointer-events: none;
    }

    .stat-topleft {
        position: absolute;
        top: 4px;
        left: 7px;
        display: flex;
        gap: 3px;
        pointer-events: auto;
    }

    .stat-topright {
        position: absolute;
        top: 3px;
        right: 4px;
        display: flex;
        gap: 3px;
    }

    .collection-badge {
        font-size: 13px;
        padding: 0 5px 1.5px;
        color: #fffd;
        border: 1.8px solid #fffd;
        border-radius: 7px;
        background: #000b;
        text-decoration: none;
    }
    .collection-badge:hover { opacity: 0.8; }

    .new-badge {
        font-size: 11px;
        padding: 2px 5px 0;
        color: rgb(255, 27, 27);
        border: 1.8px solid rgb(255, 32, 32);
        border-radius: 7px;
        background: #000b;
    }

    .chip {
        background: #0009;
        padding: 1px 4px 0;
        color: white;
        border-radius: 5px;
        font-size: 0.78rem;
    }

    .duration-chip {
        position: absolute;
        right: 4px;
        bottom: 4px;
    }

    .views-chip {
        position: absolute;
        left: 4px;
        bottom: 4px;
        color: #ddd;
    }

    /* ── Card info ── */

    .card-info {
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
        min-height: 8rem;
        overflow: hidden;
    }

    /* Details bar */

    .details-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.71rem;
        color: #999;
        padding: 0.25rem 0.7rem;
    }

    .details-left {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .muted { color: #555; }

    .likes-row {
        display: flex;
        align-items: center;
        gap: 1.5px;
    }

    .rating {
        font-family: 'Jaro', sans-serif;
        font-size: 0.8rem;
        color: #bb9;
    }

    /* Title bar */

    .title-bar {
        display: flex;
        align-items: flex-start;
        padding: 0 4px;
    }

    .fav-btn {
        all: unset;
        height: 1.3rem;
        min-width: 1.2rem;
        margin: 0.1rem 0.6rem;
        padding: 0.2rem;
        cursor: pointer;
        flex-shrink: 0;
    }

    .fav-btn svg {
        display: none;
        height: 100%;
        width: auto;
    }

    .fav-btn.loaded.is-fav   :global(svg.on)  { display: block; }
    .fav-btn.loaded:not(.is-fav) :global(svg.off) { display: block; }
    .fav-btn:active svg { opacity: 0.8; }

    .title-link { text-decoration: none; }

    .title-link h2 {
        font-size: 1.3rem;
        letter-spacing: -0.6px;
        font-weight: 400;
        margin: 0;
        color: #eee;
        text-align: left;
    }

    /* Studio + actors */

    .studio-actors {
        margin: 0.1rem 1rem 0 2rem;
        display: flex;
        flex-direction: column;
        gap: 0.2rem;
    }

    .year-studio-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: #bbb;
        margin-left: 1.2rem;
    }

    .year {
        font-weight: bold;
        font-size: 0.85rem;
        margin-right: 0.2rem;
    }

    .studios-row {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #777;
        font-size: 1rem;
    }

    .actors-row {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.3rem;
        font-family: 'Inter', sans-serif;
        color: #888;
        font-size: 1rem;
        margin-bottom: 5px;
    }

    .studios-row a,
    .actors-row a {
        text-decoration: none;
        color: inherit;
        white-space: nowrap;
    }

    .studios-row a:hover,
    .actors-row a:hover { text-decoration: underline; }

    .sep {
        display: inline-block;
        height: 4px;
        width: 4px;
        background: #fa09;
        transform: rotate(45deg);
        flex-shrink: 0;
        user-select: none;
    }

    .expand-btn {
        all: unset;
        cursor: pointer;
        color: #888;
        font-size: inherit;
        white-space: nowrap;
    }
    .expand-btn:hover { color: #aaa; }

    /* Tags */

    .tags-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 3px;
        margin: 0.5rem;
        margin-top: auto;
    }

    .tag {
        white-space: nowrap;
        font-family: sans-serif;
        font-size: 0.67rem;
        font-weight: bold;
        background: #151515;
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #888 !important;
        text-decoration: none;
    }

    .tag:hover { text-decoration: none !important; }

    .expand-tag-btn {
        all: unset;
        cursor: pointer;
        white-space: nowrap;
        font-family: sans-serif;
        font-size: 0.67rem;
        font-weight: bold;
        background: #222;
        border-radius: 5px;
        padding: 1.5px 6px;
        color: #ccc !important;
    }
</style>
