<script lang="ts">
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    let isFav   = $state(interact.is_favourite);
    let likes   = $state(interact.likes);
    let favBusy = $state(false);

    async function toggleFav() {
        if (favBusy) return;
        favBusy = true;
        const was = isFav;
        isFav = !was;
        try {
            await fetch(`/api/interact/favourites/${was ? 'remove' : 'add'}/${hash}`, { method: 'POST' });
        } catch {
            isFav = was;
        } finally {
            favBusy = false;
        }
    }

    async function addLike() {
        try {
            const data = await fetch(`/api/interact/likes/add/${hash}`, { method: 'POST' }).then(r => r.json());
            if (data?.likes !== undefined) likes = data.likes;
        } catch { /* ignore */ }
    }

    function formatViewtime(seconds: number): string {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);
        if (h > 0) return `${h}h ${m}m ${s}s`;
        if (m > 0) return `${m}m ${s}s`;
        return `${s}s`;
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

<div class="details">

    <div class="title-row">
        <h1 class="title">{video.title || video.scene_title || video.filename}</h1>
        {#if video.date_released}
            <span class="year">{video.date_released.slice(0, 4)}</span>
        {/if}
    </div>

    {#if video.studio || video.line}
        <div class="meta-row">
            {#if video.studio}
                <a class="chip chip-studio" href={searchLink('studio', video.studio)}
                   onclick={(e) => navSearch(e, 'studio', video.studio)}>{video.studio}</a>
            {/if}
            {#if video.line}
                <a class="chip chip-line" href={searchLink('studio', video.line)}
                   onclick={(e) => navSearch(e, 'studio', video.line)}>{video.line}</a>
            {/if}
        </div>
    {/if}

    {#if video.actors?.length}
        <div class="meta-row">
            {#each video.actors as actor}
                <a class="chip chip-actor" href={searchLink('actor', actor)}
                   onclick={(e) => navSearch(e, 'actor', actor)}>{actor}</a>
            {/each}
        </div>
    {/if}

    <div class="meta-row specs">
        {#if video.duration}<span class="spec">{video.duration}</span>{/if}
        {#if video.resolution}<span class="spec">{video.resolution}p</span>{/if}
        {#if video.bitrate}<span class="spec">{video.bitrate} kbps</span>{/if}
        {#if video.fps}<span class="spec">{video.fps} fps</span>{/if}
        {#if video.filesize_mb}<span class="spec">{video.filesize_mb.toFixed(0)} MB</span>{/if}
    </div>

    {#if video.collection}
        <div class="meta-row">
            <a class="chip chip-collection" href={searchLink('collection', video.collection)}
               onclick={(e) => navSearch(e, 'collection', video.collection)}>{video.collection}</a>
            {#if video.parent_dir && video.parent_dir !== video.collection}
                <span class="subdir">{video.parent_dir}</span>
            {/if}
        </div>
    {/if}

    {#if video.tags?.length}
        <div class="meta-row tags-row">
            {#each video.tags as tag}
                <a class="chip chip-tag" href={searchLink('tag', tag)}
                   onclick={(e) => navSearch(e, 'tag', tag)}>{tag}</a>
            {/each}
        </div>
    {/if}

    <div class="interact-row">
        <button
            class="interact-btn fav-btn"
            class:active={isFav}
            onclick={toggleFav}
            disabled={favBusy}
            title={isFav ? 'Remove from favourites' : 'Add to favourites'}
        >
            {isFav ? '♥ Favourited' : '♡ Favourite'}
        </button>

        <button class="interact-btn" onclick={addLike} title="Like">
            ♦ {likes}
        </button>

        {#if interact.rating}
            <span class="rating-badge">{interact.rating}</span>
        {/if}

        {#if interact.viewtime > 0}
            <span class="viewtime">{formatViewtime(interact.viewtime)} watched</span>
        {/if}
    </div>

    {#if video.description}
        <p class="description">{video.description}</p>
    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .details {
        max-width: 72rem;
        margin: 0 auto;
        padding: 1.25rem 1rem 0;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .title-row {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        flex-wrap: wrap;
    }

    .title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ecede3;
        line-height: 1.3;
    }

    .year {
        font-size: 0.9rem;
        color: #888;
        flex-shrink: 0;
    }

    .meta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        align-items: center;
    }

    .chip {
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none;
        transition: opacity 0.15s;
    }
    .chip:hover { opacity: 0.8; }

    .chip-actor      { background: #2a0d1a; color: #FF2C91; border: 1px solid #5a1535; }
    .chip-studio     { background: #1a1a2a; color: #7b93cc; border: 1px solid #2a3050; }
    .chip-line       { background: #1a1a2a; color: #5a7bbb; border: 1px solid #2a3050; }
    .chip-collection { background: #1a2a1a; color: #6bbf6b; border: 1px solid #2a502a; }
    .chip-tag        { background: #1e1e1e; color: #aaa;    border: 1px solid #333;    }

    .specs { gap: 0.6rem; }
    .spec {
        font-size: 0.75rem;
        color: #888;
        background: #111;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 0.15rem 0.45rem;
    }

    .subdir { font-size: 0.75rem; color: #555; }

    .tags-row { gap: 0.3rem; }

    .interact-row {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 0.6rem;
        margin-top: 0.25rem;
    }

    .interact-btn {
        padding: 0.3rem 0.9rem;
        border-radius: 5px;
        font-size: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        border: 1px solid #333;
        background: #111;
        color: #aaa;
        transition: background 0.15s, color 0.15s, border-color 0.15s;
    }
    .interact-btn:hover:not(:disabled) {
        background: #1e1e1e;
        color: #eee;
        border-color: #555;
    }
    .interact-btn:disabled { opacity: 0.5; cursor: default; }

    .fav-btn.active { background: #2a0d1a; color: #FF2C91; border-color: #5a1535; }

    .rating-badge {
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 800;
        background: #1a1a1a;
        border: 1px solid #444;
        color: #D79C29;
        letter-spacing: 0.05em;
    }

    .viewtime { font-size: 0.78rem; color: #666; }

    .description {
        font-size: 0.85rem;
        color: #888;
        line-height: 1.6;
        max-width: 60ch;
        margin-top: 0.25rem;
    }
</style>
