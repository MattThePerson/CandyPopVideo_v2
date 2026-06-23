<!-- pages/home/Page.svelte -->
<script lang="ts">
    import { onMount } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import VideoCard from '$lib/components/VideoCard.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import SimilarVideos from '$lib/components/SimilarVideos.svelte';

    let video          = $state<VideoData | null>(null);
    let similar        = $state<VideoData[]>([]);
    let queryTime      = $state<number | null>(null);
    let error          = $state<string | null>(null);
    let similarLoading = $state(false);

    const today = new Date().toDateString();

    onMount(async () => {
        document.title = 'CandyPop';
        try {
            const hash = await fetch('/api/get/random-spotlight-video-hash').then(r => r.text());
            // const hash = await fetch('/api/get/random-video-hash')
            //     .then(r => r.json()).then(r => r['hash'] as string)
            video = await fetch(`/api/get/video-data/${hash}`)
                .then(r => r.json()) as VideoData;
            similarLoading = true;
            const res = await fetch(`/api/query/get/similar-videos/${hash}`)
                .then(r => r.json());
            similar   = (res.Videos as VideoData[]).slice(1);
            queryTime = res.TimeTaken as number;
        } catch (e) {
            error = String(e);
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

<div class="p-8">

    <!-- Spotlight -->
    <section class="flex flex-col items-center mb-8">
        <h2 class="mb-4 text-[#aaa] uppercase tracking-widest text-sm font-semibold">
            Spotlight · {today}
        </h2>
        {#if error}
            <p class="text-red-400">{error}</p>
        {:else if video === null}
            <div class="flex justify-center py-16">
                <Spinner />
            </div>
        {:else}
            <VideoCard {video} width="72rem" aspectRatio="21/9" />
        {/if}
    </section>

    <!-- Similar videos -->
    {#if video}
        <SimilarVideos {video} {similar} loading={similarLoading} {queryTime} />
    {/if}

</div>
