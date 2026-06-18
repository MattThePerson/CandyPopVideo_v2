<!-- pages/video/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import VideoPlayer from './VideoPlayer.svelte';
    import VideoDetails from './VideoDetails.svelte';

    /* Props */
    let { hash }: { hash: string } = $props();

    let video     = $state<VideoData | null>(null);
    let interact  = $state<VideoInteractions | null>(null);
    let loadError = $state<string | null>(null);

    onMount(async () => {
        try {
            [video, interact] = await Promise.all([
                fetch(`/api/get/video-data/${hash}`).then(r => r.json()) as Promise<VideoData>,
                fetch(`/api/interact/get/${hash}`).then(r => r.json()) as Promise<VideoInteractions>,
            ]);
        } catch (e) {
            loadError = String(e);
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page">

    <div class="player-wrap">
        {#if loadError}
            <div class="player-error">{loadError}</div>
        {:else if !video}
            <div class="player-center">
                <Spinner size={52} />
            </div>
        {:else}
            <VideoPlayer {hash} title={video.title || video.filename} />
        {/if}
    </div>

    {#if video && interact}
        <VideoDetails {hash} {video} {interact} />
    {/if}

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .page {
        width: 100%;
        padding-bottom: 4rem;
    }

    .player-wrap {
        width: 100%;
        height: 45rem;
        background: #000;
        position: relative;
    }

    .player-center {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .player-error {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #f87171;
        font-size: 0.9rem;
    }
</style>
