<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';

    /* Props */
    let { video, interact }: {
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    const hasDesc     = $derived(!!video.description);
    const hasComments = $derived((interact.comments?.length ?? 0) > 0);
    const hasPlatform = $derived(!!(video.views || video.likes));
    const hasAny      = $derived(hasDesc || hasComments || hasPlatform);

    type Tab = 'description' | 'comments' | 'platform';

    let activeTab = $state<Tab>(
        video.description                       ? 'description'
        : (interact.comments?.length ?? 0) > 0 ? 'comments'
        : (video.views || video.likes)          ? 'platform'
        : 'description'
    );
    let expanded = $state(false);

    function fmtCount(n: number): string {
        if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
        if (n >= 1_000)     return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
        return String(n);
    }

    function formatDate(s: string): string {
        if (!s) return '';
        const d = new Date(s.replace(' ', 'T'));
        if (isNaN(d.getTime())) return s.slice(0, 10);
        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="scene-box">
    <div class="scene-tabs">
        <button
            class="scene-tab"
            class:active={activeTab === 'description'}
            disabled={!hasDesc}
            onclick={() => activeTab = 'description'}
        >description</button>
        <button
            class="scene-tab"
            class:active={activeTab === 'comments'}
            disabled={!hasComments}
            onclick={() => activeTab = 'comments'}
        >comments</button>
        <button
            class="scene-tab"
            class:active={activeTab === 'platform'}
            disabled={!hasPlatform}
            onclick={() => activeTab = 'platform'}
        >platform</button>
    </div>
    {#if !hasAny}
        <p class="nothing-here">nothing here</p>
    {:else}
        <div class="scene-content" class:expanded>
            {#if activeTab === 'description'}
                <p class="description-text">{video.description}</p>
            {:else if activeTab === 'comments'}
                <div class="comments-list">
                    {#each interact.comments ?? [] as [text, dt]}
                        <div class="comment-row">
                            <span class="comment-text">{text}</span>
                            <span class="comment-dt">{formatDate(dt)}</span>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="platform-stats">
                    {#if video.views}
                        <div class="platform-row">
                            <span class="plat-label">views</span>
                            <span class="plat-val">{fmtCount(video.views)}</span>
                        </div>
                    {/if}
                    {#if video.likes}
                        <div class="platform-row">
                            <span class="plat-label">likes</span>
                            <span class="plat-val">{fmtCount(video.likes)}</span>
                        </div>
                    {/if}
                </div>
            {/if}
        </div>
        <button class="expand-bar" onclick={() => expanded = !expanded} title={expanded ? 'collapse' : 'expand'}>
            <span class="expand-icon">{expanded ? '▲' : '▼'}</span>
        </button>
    {/if}
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .scene-box {
        border: 1px solid #1e1e1e;
        border-radius: 6px;
        overflow: hidden;
        background: #090909;
    }

    .nothing-here {
        padding: 1rem;
        font-size: 0.72rem;
        color: #333;
        letter-spacing: 0.04em;
        margin: 0;
        text-align: center;
        user-select: none;
        cursor: default;
    }

    /* tabs */
    .scene-tabs {
        display: flex;
        border-bottom: 1px solid #1a1a1a;
    }

    .scene-tab {
        all: unset;
        cursor: pointer;
        font-family: inherit;
        font-size: 0.68rem;
        letter-spacing: 0.04em;
        color: #555;
        padding: 0.4rem 0.75rem;
        border-right: 1px solid #1a1a1a;
        transition: color 0.12s, background 0.12s;
    }
    .scene-tab:last-child { border-right: none; }
    .scene-tab:hover:not(:disabled):not(.active) { color: #999; background: #0f0f0f; }
    .scene-tab.active { color: #bbb; }
    .scene-tab:disabled { color: #282828; cursor: default; }

    /* content */
    .scene-content {
        max-height: 6rem;
        overflow: hidden;
        padding: 0.65rem 0.75rem;
        box-sizing: border-box;
    }
    .scene-content.expanded {
        max-height: 26rem;
        overflow-y: auto;
    }
    .scene-content::-webkit-scrollbar { width: 4px; }
    .scene-content::-webkit-scrollbar-track { background: #0d0d0d; }
    .scene-content::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }

    .description-text {
        color: #aaa;
        font-size: 0.85rem;
        line-height: 1.65;
        margin: 0;
    }

    /* comments */
    .comment-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid #141414;
    }
    .comment-row:last-child { border-bottom: none; }
    .comment-text { font-size: 0.83rem; color: #bbb; flex: 1; min-width: 0; }
    .comment-dt   { font-size: 0.7rem; color: #555; white-space: nowrap; flex-shrink: 0; }

    /* platform */
    .platform-stats { display: flex; flex-direction: column; gap: 0.35rem; }
    .platform-row   { display: flex; align-items: center; gap: 0.6rem; }
    .plat-label { font-size: 0.68rem; color: #555; letter-spacing: 0.04em; min-width: 3rem; }
    .plat-val   { font-size: 0.82rem; color: #999; }

    /* expand bar */
    .expand-bar {
        all: unset;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0.2rem 0;
        border-top: 1px solid #1a1a1a;
        cursor: pointer;
        background: #090909;
        transition: background 0.12s;
    }
    .expand-bar:hover { background: #111; }
    .expand-icon { font-size: 0.5rem; color: #333; line-height: 1; }
    .expand-bar:hover .expand-icon { color: #555; }
</style>
