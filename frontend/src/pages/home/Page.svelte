<script lang="ts">
    import { onMount } from 'svelte';
    import type { VideoData } from '$lib/types/video';
    import VideoCard from '$lib/components/VideoCard.svelte';

    let video = $state<VideoData | null>(null);
    let error = $state<string | null>(null);
    let similar_videos = $state<Array<VideoData>>([]);

    onMount(async () => {
        try {
            const hash = await fetch('/api/get/random-video-hash').then(r => r.json()).then(r => r['hash'] as string);
            video = await fetch(`/api/get/video-data/${hash}`).then(r => r.json()) as VideoData;
            const result = await fetch(`/api/query/get/similar-videos/${hash}`).then(r => r.json());
            similar_videos = (result.Videos as Array<VideoData>).slice(1,9);
        } catch (e) {
            error = String(e);
        }
    });
</script>

<div class="p-8">
    <h2 class="mb-4 text-[#aaa] uppercase tracking-widest text-sm font-semibold">
        Today's Spotlight
    </h2>
    <!-- spotlight -->
    {#if error}
        <p class="text-red-400">{error}</p>
    {:else if video === null}
        <p class="text-[#555]">Loading...</p>
    {:else}
        <VideoCard {video} size="large" />
    {/if}
    <!-- similar videos -->
    <div class="similar-videos-section">
	    {#each similar_videos as video}
	     	<VideoCard {video} size="small" />
	    {/each}
    </div>
</div>
