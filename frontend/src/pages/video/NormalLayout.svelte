<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';
    import VideoBelow from './VideoBelow.svelte';
    import SimilarVideos from '$lib/components/SimilarVideos.svelte';
    import RelatedVideos from '$lib/components/RelatedVideos.svelte';

    /* Props */
    let { hash, video, interact, similar, similarLoading, queryTime, relatedHashes, onRelatedLoaded }: {
        hash: string;
        video: VideoData;
        interact: VideoInteractions;
        similar: VideoData[];
        similarLoading: boolean;
        queryTime: number | null;
        relatedHashes: Set<string>;
        onRelatedLoaded: (hashes: Set<string>) => void;
    } = $props();
</script>

<VideoBelow {hash} {video} {interact} />
<SimilarVideos {video} {similar} loading={similarLoading} {queryTime} {relatedHashes} />
<RelatedVideos {video} {onRelatedLoaded} />
