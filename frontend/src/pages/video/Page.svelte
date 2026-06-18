<!-- pages/video/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import VideoPlayer from './VideoPlayer.svelte';
    import VideoDetails from './VideoDetails.svelte';
    import RelatedVideos from './RelatedVideos.svelte';
    import SimilarVideos from '$lib/components/SimilarVideos.svelte';

    /* Props */
    let { hash }: { hash: string } = $props();

    let video          = $state<VideoData | null>(null);
    let interact       = $state<VideoInteractions | null>(null);
    let loadError      = $state<string | null>(null);
    let similar        = $state<VideoData[]>([]);
    let relatedHashes  = $state(new Set<string>());
    let similarLoading = $state(false);
    let queryTime      = $state<number | null>(null);

    onMount(async () => {
        try {
            [video, interact] = await Promise.all([
                fetch(`/api/get/video-data/${hash}`).then(r => r.json()) as Promise<VideoData>,
                fetch(`/api/interact/get/${hash}`).then(r => r.json()) as Promise<VideoInteractions>,
            ]);
        } catch (e) {
            loadError = String(e);
            return;
        }

        similarLoading = true;
        try {
            const res = await fetch(`/api/query/get/similar-videos/${hash}`).then(r => r.json());
            similar   = (res.Videos as VideoData[]).filter(v => v.hash !== hash);
            queryTime = res.TimeTaken as number;
        } catch {
            similar   = [];
            queryTime = null;
        } finally {
            similarLoading = false;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page">

    <!-- video player -->
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

    <!-- video details -->
    {#if video && interact}
        <VideoDetails {hash} {video} {interact} />
    {/if}

    <!-- related videos -->
    {#if video}
        <RelatedVideos {video} onRelatedLoaded={(hashes) => { relatedHashes = hashes; }} />
    {/if}

    <!-- similar videos -->
    {#if video}
        <SimilarVideos {video} {similar} loading={similarLoading} {queryTime} {relatedHashes} />
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
