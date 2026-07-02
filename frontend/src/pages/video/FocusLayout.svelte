<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';

    /* Props */
    let { hash, video, interact }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
    } = $props();
</script>
