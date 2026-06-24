<script lang="ts">
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import ActorCard from '$lib/components/ActorCard.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    let isFav       = $state(interact.is_favourite);
    let likes       = $state(interact.likes);
    let rating      = $state(interact.rating ?? '');
    let favBusy     = $state(false);
    let ratingOpen  = $state(false);
    let ratingBusy  = $state(false);

    // Fav-date popup
    let favDate      = $state(interact.favourited_date ?? '');
    let popupOpen    = $state(false);
    let popupVal     = $state('');
    let popupBusy    = $state(false);
    let popupStatus  = $state<'idle' | 'success' | 'error' | 'same'>('idle');
    let popupInputEl = $state<HTMLInputElement | null>(null);

    const displayTitle = (video.title || video.scene_title || video.filename).replaceAll(';', ':');

    const GRADES = ['C', 'C+', 'B', 'B+', 'A', 'A+', 'S', 'S+'] as const;

    const GRADE_COLORS: Record<string, string> = {
        'C':  '#888',
        'C+': '#aaa',
        'B':  '#5b8def',
        'B+': '#89b4f8',
        'A':  '#56b56e',
        'A+': '#76d275',
        'S':  '#D79C29',
        'S+': '#D79C29',
    };

    function gradeColor(g: string): string {
        return GRADE_COLORS[g] ?? '#888';
    }

    // ── Fav ────────────────────────────────────────────────────

    async function toggleFav() {
        if (favBusy) return;
        favBusy = true;
        try {
            const res = await fetch(`/api/interact/favourites/${isFav ? 'remove' : 'add'}/${hash}`, { method: 'POST' });
            if (res.ok) isFav = !isFav;
        } catch { /* ignore */ } finally {
            favBusy = false;
        }
    }

    function openFavPopup(e: MouseEvent) {
        if (!isFav) return;
        e.preventDefault();
        popupVal    = favDate;
        popupStatus = 'idle';
        popupOpen   = true;
    }

    function closeFavPopup() {
        popupOpen   = false;
        popupStatus = 'idle';
    }

    async function saveFavDate() {
        const val = popupVal.trim();
        console.debug('[fav-popup] saveFavDate called, val:', JSON.stringify(val), 'favDate:', JSON.stringify(favDate));

        if (val === favDate) {
            console.debug('[fav-popup] value unchanged, skipping');
            popupStatus = 'same';
            popupInputEl?.focus();
            return;
        }
        if (!val) {
            popupStatus = 'error';
            popupInputEl?.focus();
            return;
        }

        popupBusy = true;
        popupStatus = 'idle';
        const url = `/api/interact/favourites/update-time/${hash}/${encodeURIComponent(val)}`;
        console.debug('[fav-popup] POSTing to:', url);
        try {
            const res = await fetch(url, { method: 'POST' });
            console.debug('[fav-popup] response status:', res.status);
            if (res.ok) {
                favDate     = val;
                popupStatus = 'success';
                setTimeout(() => { popupOpen = false; popupStatus = 'idle'; }, 900);
            } else {
                const body = await res.text();
                console.debug('[fav-popup] error body:', body);
                popupStatus = 'error';
                popupInputEl?.focus();
            }
        } catch (err) {
            console.debug('[fav-popup] fetch threw:', err);
            popupStatus = 'error';
            popupInputEl?.focus();
        } finally {
            popupBusy = false;
        }
    }

    // Focus input when popup opens
    $effect(() => {
        if (popupOpen && popupInputEl) {
            popupInputEl.focus();
            popupInputEl.select();
        }
    });

    // Close fav popup on click outside
    $effect(() => {
        if (!popupOpen) return;
        const onClick = (e: MouseEvent) => {
            if (!(e.target as Element).closest('.fav-wrapper')) closeFavPopup();
        };
        document.addEventListener('click', onClick);
        return () => document.removeEventListener('click', onClick);
    });

    // Close fav popup on Escape
    $effect(() => {
        if (!popupOpen) return;
        const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') closeFavPopup(); };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    });

    // ── Rating ─────────────────────────────────────────────────

    // Optimistic — reverts on error. Clicking current grade clears the rating.
    async function setRating(grade: string) {
        if (ratingBusy) return;
        const prev = rating;
        const next = grade === rating ? '' : grade;
        rating = next;
        ratingOpen = false;
        ratingBusy = true;
        try {
            const res = await fetch(`/api/interact/rating/update/${hash}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rating: next }),
            });
            if (!res.ok) rating = prev;
        } catch {
            rating = prev;
        } finally {
            ratingBusy = false;
        }
    }

    // Close rating picker on click outside
    $effect(() => {
        if (!ratingOpen) return;
        const onClick = (e: MouseEvent) => {
            if (!(e.target as Element).closest('.rating-area')) ratingOpen = false;
        };
        document.addEventListener('click', onClick);
        return () => document.removeEventListener('click', onClick);
    });

    // ── Likes ──────────────────────────────────────────────────

    // Optimistic — increments immediately; backend returns plain text not JSON.
    async function addLike() {
        likes += 1;
        try {
            const res = await fetch(`/api/interact/likes/add/${hash}`, { method: 'POST' });
            if (!res.ok) likes -= 1;
        } catch { likes -= 1; }
    }

    // Optimistic — decrements down to 0. Called on right-click.
    async function removeLike(e: MouseEvent) {
        e.preventDefault();
        if (likes <= 0) return;
        likes -= 1;
        try {
            const res = await fetch(`/api/interact/likes/remove/${hash}`, { method: 'POST' });
            if (!res.ok) likes += 1;
        } catch { likes += 1; }
    }

    // ── Info / path ────────────────────────────────────────────

    function parentDir(p: string): string {
        const i = Math.max(p.lastIndexOf('/'), p.lastIndexOf('\\'));
        return i > 0 ? p.slice(0, i) : p;
    }

    function copyParentPath() {
        navigator.clipboard.writeText(parentDir(video.path)).catch(() => {});
    }

    // ── Formatters ─────────────────────────────────────────────

    function formatDuration(d: string): string {
        const parts = d.split(':').map(Number);
        if (parts.length === 3) {
            const [h, m, s] = parts;
            if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            return `${m}:${String(s).padStart(2, '0')}`;
        }
        return d;
    }

    function formatViewtime(seconds: number): string {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        if (h > 0) return `${h}h ${m}m`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
    }

    function formatDate(s: string): string {
        if (!s) return '';
        const d = new Date(s.replace(' ', 'T'));
        if (isNaN(d.getTime())) return s.slice(0, 10);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }

    function fmtCount(n: number): string {
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
        return String(n);
    }

    function formatBitrate(kbps: number): string {
        return (Math.floor(kbps / 100) / 10).toFixed(1) + ' MB/s';
    }

    function formatFilesize(mb: number): string {
        if (mb >= 1000) return (Math.floor(mb / 100) / 10).toFixed(1) + ' GB';
        return Math.floor(mb) + ' MB';
    }

    function searchLink(key: string, val: string): string {
        return `/search?${key}=${encodeURIComponent(val)}`;
    }

    function navSearch(e: MouseEvent, key: string, val: string) {
        e.preventDefault();
        navigate(searchLink(key, val));
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="video-info-section">

    <!-- LEFT: about -->
    <div class="about-container">

        <!-- Quick stats -->
        <div class="quick-stats-bar">
            {#if video.duration}<span title="duration">{formatDuration(video.duration)}</span>{/if}
            {#if video.resolution}<span class="sep"></span><span title="resolution">{video.resolution}p</span>{/if}
            {#if video.fps}<span class="sep"></span><span title="framerate">{video.fps} fps</span>{/if}
            {#if video.bitrate}<span class="sep"></span><span title="bitrate">{formatBitrate(video.bitrate)}</span>{/if}
            {#if video.filesize_mb}<span class="sep"></span><span title="filesize">{formatFilesize(video.filesize_mb)}</span>{/if}
        </div>

        <!-- Title + fav bookmark -->
        <div class="title-bar">
            <div class="fav-wrapper">
                <button
                    class="fav-bookmark"
                    class:is-fav={isFav}
                    onclick={toggleFav}
                    oncontextmenu={openFavPopup}
                    disabled={favBusy}
                    title={isFav ? 'Favourited — right-click to edit date' : 'Add to favourites'}
                >
                    <!-- off -->
                    <svg class="bm-off" width="28" height="28" viewBox="-4 0 30 30" xmlns="http://www.w3.org/2000/svg">
                        <path d="M437,177 C437,178.104 436.104,179 435,179 L428,172 L421,179 C419.896,179 419,178.104 419,177 L419,155 C419,153.896 419.896,153 421,153 L435,153 C436.104,153 437,153.896 437,155 L437,177 L437,177 Z M435,151 L421,151 C418.791,151 417,152.791 417,155 L417,177 C417,179.209 418.791,181 421,181 L428,174 L435,181 C437.209,181 439,179.209 439,177 L439,155 C439,152.791 437.209,151 435,151 L435,151 Z" transform="translate(-417 -151)"/>
                    </svg>
                    <!-- on -->
                    <svg class="bm-on" width="28" height="28" viewBox="-4 0 30 30" xmlns="http://www.w3.org/2000/svg">
                        <path d="M437,153 L423,153 C420.791,153 419,154.791 419,157 L419,179 C419,181.209 420.791,183 423,183 L430,176 L437,183 C439.209,183 441,181.209 441,179 L441,157 C441,154.791 439.209,153 437,153" transform="translate(-419 -153)"/>
                    </svg>
                </button>

                {#if popupOpen}
                    <div class="fav-popup">
                        <span class="fav-popup-label">favourited date</span>
                        <input
                            bind:this={popupInputEl}
                            bind:value={popupVal}
                            class="fav-popup-input"
                            class:ok={popupStatus === 'success'}
                            class:err={popupStatus === 'error'}
                            class:same={popupStatus === 'same'}
                            type="text"
                            placeholder="YYYY-MM-DD HH:MM:SS"
                            disabled={popupBusy}
                            onkeydown={(e) => {
                                if (e.key === 'Enter')  { e.preventDefault(); e.stopPropagation(); saveFavDate(); }
                                if (e.key === 'Escape') { e.stopPropagation(); closeFavPopup(); }
                            }}
                        />
                        {#if popupStatus === 'success'}
                            <span class="fav-popup-feedback ok">✓ saved</span>
                        {:else if popupStatus === 'error'}
                            <span class="fav-popup-feedback err">✗ invalid date</span>
                        {:else if popupStatus === 'same'}
                            <span class="fav-popup-feedback same">no change</span>
                        {/if}
                    </div>
                {/if}
            </div>
            <h1 class="title">{displayTitle}</h1>
        </div>

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
                    {#if video.studio && video.line}
                        <span class="studio-sep"></span>
                    {/if}
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

        <!-- Tags -->
        {#if video.tags?.length}
            <div class="tags-bar">
                {#each video.tags as tag}
                    <a class="tag-chip" href={searchLink('tag', tag)}
                       onclick={(e) => navSearch(e, 'tag', tag)}
                       title="tag">{tag}</a>
                {/each}
            </div>
        {/if}

    </div>

    <!-- RIGHT: interactions panel -->
    <div class="interactions-container">

        <!-- Horizontal buttons bar -->
        <div class="buttons-bar">
            <button class="ib-btn like" class:active={likes > 0} onclick={addLike} oncontextmenu={removeLike} title="Like (right-click to remove)">
                ♥ {likes}
            </button>
            <div class="rating-area">
                <button
                    class="ib-btn rate"
                    class:rated={!!rating}
                    style={rating ? `color: ${gradeColor(rating)}; border-color: ${gradeColor(rating)}66` : ''}
                    onclick={() => ratingOpen = !ratingOpen}
                    title="Rate"
                ><span class="rate-label">{rating || '★'}</span></button>
                {#if ratingOpen}
                    <div class="rating-picker">
                        {#each GRADES as grade}
                            <button
                                class="grade-btn"
                                class:current={rating === grade}
                                style="color: {gradeColor(grade)}; border-color: {gradeColor(grade)}55"
                                onclick={() => setRating(grade)}
                                disabled={ratingBusy}
                            >{grade}</button>
                        {/each}
                    </div>
                {/if}
            </div>
            <button class="ib-btn stub" title="Custom tags — coming soon">🏷</button>
            <button class="ib-btn stub" title="Comments — coming soon">💬</button>
        </div>

        <!-- info block -->
        <div class="info-block">
            <div class="info-row">
                <span class="info-label">watched</span>
                <span class="info-val">{interact.viewtime > 0 ? formatViewtime(interact.viewtime) : '0s'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">last seen</span>
                <span class="info-val">{interact.last_viewed ? formatDate(interact.last_viewed) : 'never'}</span>
            </div>
            {#if video.path}
                <div class="info-row">
                    <span class="info-label">dir</span>
                    <button class="copy-path" onclick={copyParentPath} title="Click to copy path">
                        {parentDir(video.path)}
                    </button>
                </div>
            {/if}
            {#if video.views || video.likes}
                <div class="info-row platform-stats">
                    {#if video.views}<span title="platform views">▶ {fmtCount(video.views)} views</span>{/if}
                    {#if video.likes}<span title="platform likes">♥ {fmtCount(video.likes)} likes</span>{/if}
                </div>
            {/if}
        </div>

    </div>

</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .video-info-section {
        display: flex;
        justify-content: space-between;
        width: 100%;
        padding: 0.5rem 9% 1.5rem;
        background: #080808;
        border-top: 1px solid #ffffff22;
        border-bottom: 1px solid #ffffff18;
        box-sizing: border-box;
    }

    /* ── LEFT COLUMN ─────────────────────────────────────────── */

    .about-container {
        display: flex;
        flex-direction: column;
        min-width: 0;
        flex: 1;
    }

    /* quick-stats-bar */
    .quick-stats-bar {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin-left: 3.6rem;
        margin-bottom: 0.15rem;
    }
    .quick-stats-bar span {
        font-size: 13px;
        color: #999;
    }
    .sep {
        width: 5px;
        height: 5px;
        background: #666;
        transform: rotate(45deg);
        flex-shrink: 0;
        display: inline-block;
    }

    /* title-bar */
    .title-bar {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.25rem;
    }

    .fav-bookmark {
        all: unset;
        cursor: pointer;
        flex-shrink: 0;
        width: 2rem;
        height: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0.85;
        transition: opacity 0.15s;
    }
    .fav-bookmark:hover { opacity: 1; }
    .fav-bookmark:disabled { cursor: default; opacity: 0.4; }

    .fav-bookmark svg { display: none; }
    .fav-bookmark:not(.is-fav) .bm-off { display: block; }
    .fav-bookmark.is-fav .bm-on  { display: block; }

    .bm-off path { fill: #999; }
    .bm-on  path { fill: #D79C29; }

    /* fav popup */
    .fav-wrapper {
        position: relative;
        flex-shrink: 0;
    }

    .fav-popup {
        position: absolute;
        top: calc(100% + 6px);
        left: 0;
        z-index: 200;
        display: flex;
        flex-direction: column;
        gap: 4px;
        background: #1a1a1a;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        padding: 0.5rem 0.65rem;
        min-width: 220px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
    }

    .fav-popup-label {
        font-size: 0.7rem;
        color: #666;
        letter-spacing: 0.04em;
    }

    .fav-popup-input {
        background: #0d0d0d;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        color: #ddd;
        font-size: 0.8rem;
        font-family: inherit;
        padding: 0.25rem 0.45rem;
        outline: none;
        width: 100%;
        box-sizing: border-box;
        transition: border-color 0.12s;
    }
    .fav-popup-input:focus { border-color: #555; }
    .fav-popup-input.ok   { border-color: #2a7a2a; }
    .fav-popup-input.err  { border-color: #7a2a2a; }
    .fav-popup-input.same { border-color: #7a5a1a; }

    .fav-popup-feedback { font-size: 0.7rem; letter-spacing: 0.02em; }
    .fav-popup-feedback.ok   { color: #4caf50; }
    .fav-popup-feedback.err  { color: #ef5350; }
    .fav-popup-feedback.same { color: #D79C29; }

    .title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ecede3;
        line-height: 1.3;
    }

    /* year-studio-bar */
    .year-studio-bar {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-left: 3.4rem;
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
    .studios a { color: #bbb; text-decoration: none; }
    .studios a:hover { text-decoration: underline; color: #eee; }

    .studio-sep {
        width: 5px;
        height: 5px;
        background: #e33;
        transform: rotate(45deg);
        flex-shrink: 0;
    }

    /* actors */
    .actors-container {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.4rem;
        margin-left: 1.8rem;
    }

    /* tags */
    .tags-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        row-gap: 3px;
        margin: 0.5rem 1rem;
        max-width: 38rem;
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

    .info-block {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        border: 1px solid #1e1e1e;
        border-radius: 6px;
        padding: 0.5rem 0.8rem;
        min-width: 24rem;
    }

    .info-row {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .info-label {
        font-size: 0.7rem;
        color: #555;
        text-transform: lowercase;
        letter-spacing: 0.04em;
        min-width: 5rem;
        flex-shrink: 0;
    }

    .info-val {
        font-size: 0.78rem;
        color: #888;
    }

    .copy-path {
        all: unset;
        cursor: pointer;
        font-size: 0.75rem;
        color: #666;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 32rem;
        transition: color 0.1s;
    }
    .copy-path:hover { color: #aaa; }
    .copy-path:hover::after { content: ' ⎘'; }

    .platform-stats {
        gap: 1rem;
    }
    .platform-stats span {
        font-size: 0.75rem;
        color: #555;
    }

    /* ── RIGHT COLUMN ────────────────────────────────────────── */

    .interactions-container {
        flex-shrink: 0;
        min-width: 260px;
        width: fit-content;
        padding-left: 1.5rem;
        padding-top: 0.6rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    /* buttons bar */
    .buttons-bar {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .ib-btn {
        all: unset;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-family: inherit;
        padding: 0.5rem 0.9rem;
        border-radius: 6px;
        border: 1px solid #2a2a2a;
        background: #111;
        color: #777;
        transition: color 0.12s, border-color 0.12s, background 0.12s;
        white-space: nowrap;
    }
    .ib-btn:hover { color: #bbb; border-color: #444; }

    .ib-btn.like.active { color: #e05575; border-color: #7a2a40; background: #180008; }
    .ib-btn.like.active:hover { color: #f07; border-color: #a03; }

    .ib-btn.rate.rated { font-weight: 700; }

    .rate-label {
        display: inline-block;
        text-align: center;
        width: 1.6em;
    }

    .ib-btn.stub { cursor: default; opacity: 0.35; font-size: 1rem; }
    .ib-btn.stub:hover { color: #777; border-color: #2a2a2a; }

    /* rating picker */
    .rating-area {
        position: relative;
    }

    .rating-picker {
        position: absolute;
        top: calc(100% + 5px);
        left: 0;
        z-index: 100;
        display: flex;
        gap: 3px;
        background: #141414;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 5px 6px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    }

    .grade-btn {
        all: unset;
        cursor: pointer;
        font-size: 0.72rem;
        font-weight: 700;
        font-family: inherit;
        padding: 0.2rem 0.35rem;
        border-radius: 4px;
        border: 1px solid #2a2a2a;
        color: #888;
        transition: color 0.1s, border-color 0.1s, background 0.1s;
    }
    .grade-btn:hover { background: #1e1e1e; }
    .grade-btn.current { background: #1a1a1a; font-weight: 700; }
    .grade-btn:disabled { cursor: default; opacity: 0.5; }

</style>
