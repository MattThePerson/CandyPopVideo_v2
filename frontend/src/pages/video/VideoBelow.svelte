<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import MainTab from './MainTab.svelte';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

    type Tab = 'main' | 'info' | 'thumbnails';
    let activeTab = $state<Tab>('main');
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<section class="video-below">
    <div class="tab-sidebar">
        <button class="tab-btn" class:active={activeTab === 'main'}       onclick={() => activeTab = 'main'}>main</button>
        <button class="tab-btn" class:active={activeTab === 'info'}       onclick={() => activeTab = 'info'}>info</button>
        <button class="tab-btn" class:active={activeTab === 'thumbnails'} onclick={() => activeTab = 'thumbnails'}>thumbnails</button>
    </div>
    <div class="tab-content">
        {#if activeTab === 'main'}
            <MainTab {hash} {video} {interact} />
        {:else}
            <div class="placeholder">coming soon</div>
        {/if}
    </div>
</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .video-below {
        display: flex;
        width: 100%;
        background: #080808;
        border-top: 1px solid #ffffff20;
        box-sizing: border-box;
    }

    .tab-sidebar {
        display: flex;
        flex-direction: column;
        padding: 1rem 0;
        border-right: 1px solid #1a1a1a;
        min-width: 5.5rem;
        flex-shrink: 0;
    }

    .tab-btn {
        all: unset;
        cursor: pointer;
        font-family: inherit;
        font-size: 0.7rem;
        color: #444;
        letter-spacing: 0.04em;
        padding: 0.45rem 0.75rem;
        text-align: left;
        width: 100%;
        box-sizing: border-box;
        border-left: 2px solid transparent;
        transition: color 0.12s, border-color 0.12s;
    }
    .tab-btn:hover:not(.active) { color: #777; }
    .tab-btn.active { color: #D79C29; border-left-color: #D79C29; }

    .tab-content {
        flex: 1;
        min-width: 0;
    }

    .placeholder {
        padding: 2rem;
        font-size: 0.75rem;
        color: #333;
        letter-spacing: 0.04em;
    }
</style>
