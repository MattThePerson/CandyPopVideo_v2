<script lang="ts">
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import ActorCard from './ActorCard.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    let isFav   = $state(interact.is_favourite);
    let likes   = $state(interact.likes);
    let favBusy = $state(false);

    // Fav-date popup
    let favDate        = $state(interact.favourited_date ?? '');
    let popupOpen      = $state(false);
    let popupVal       = $state('');
    let popupBusy      = $state(false);
    let popupStatus    = $state<'idle' | 'success' | 'error' | 'same'>('idle');
    let popupInputEl   = $state<HTMLInputElement | null>(null);

    const displayTitle = (video.title || video.scene_title || video.filename).replaceAll(';', ':');

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

    // Close on click outside
    $effect(() => {
        if (!popupOpen) return;
        const onClick = (e: MouseEvent) => {
            if (!(e.target as Element).closest('.fav-wrapper')) closeFavPopup();
        };
        document.addEventListener('click', onClick);
        return () => document.removeEventListener('click', onClick);
    });

    // Close on Escape
    $effect(() => {
        if (!popupOpen) return;
        const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') closeFavPopup(); };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    });

    // Optimistic — increments immediately; backend returns plain text not JSON.
    async function addLike() {
        likes += 1;
        try {
            const res = await fetch(`/api/interact/likes/add/${hash}`, { method: 'POST' });
            if (!res.ok) likes -= 1;
        } catch {
            likes -= 1;
        }
    }

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
        if (h > 0) return `${h}h ${m}m ${s}s`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
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

        <!-- Description -->
        {#if video.description}
            <div class="description-box">
                <h5>description:</h5>
                <p>{video.description}</p>
            </div>
        {/if}

        <!-- Interaction quick-bar (likes, rating, viewtime) — will move to right panel -->
        <div class="quick-interact">
            <button class="like-btn" class:liked={likes > 0} onclick={addLike} title="Like this video">♥ {likes}</button>
            {#if interact.rating}
                <span class="rating-badge">{interact.rating}</span>
            {/if}
            {#if interact.viewtime > 0}
                <span class="viewtime">{formatViewtime(interact.viewtime)} watched</span>
            {/if}
        </div>

    </div>

    <!-- RIGHT: interactions panel (coming next) -->
    <div class="interactions-container">
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
        text-transform: lowercase;
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

    .fav-popup-feedback {
        font-size: 0.7rem;
        letter-spacing: 0.02em;
    }
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

    /* description */
    .description-box {
        max-width: 40rem;
        background: rgba(220, 220, 220, 0.06);
        border-radius: 0.8rem;
        padding: 0.3rem 0.7rem;
        margin-top: 0.3rem;
    }
    .description-box h5 {
        padding-bottom: 3px;
        padding-left: 0.8rem;
        color: #777;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .description-box p {
        color: #bbb;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    /* quick interact (temporary, moves to right panel) */
    .quick-interact {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-top: 0.5rem;
        margin-left: 1rem;
    }
    .like-btn {
        all: unset;
        cursor: pointer;
        font-size: 0.8rem;
        color: #888;
        padding: 0.2rem 0.6rem;
        border: 1px solid #333;
        border-radius: 4px;
        background: #111;
        transition: color 0.12s, border-color 0.12s;
    }
    .like-btn:hover { color: #e06; border-color: #e06; }
    .like-btn.liked { color: #e05575; border-color: #a0334d; background: #1a0008; }

    .rating-badge {
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 800;
        background: #1a1a1a;
        border: 1px solid #444;
        color: #D79C29;
        letter-spacing: 0.05em;
    }
    .viewtime { font-size: 0.75rem; color: #555; }

    /* ── RIGHT COLUMN ────────────────────────────────────────── */

    .interactions-container {
        flex-shrink: 0;
        width: 260px;
        padding-left: 1.5rem;
    }
</style>
