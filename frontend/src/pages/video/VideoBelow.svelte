<script lang="ts">
    import type { VideoData, VideoInteractions } from '$lib/types/video';

    /* Props */
    let { video, interact }: {
        video: VideoData;
        interact: VideoInteractions;
    } = $props();

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

<section class="video-below">

    {#if video.description}
        <div class="below-description">
            <h5>description</h5>
            <p>{video.description}</p>
        </div>
    {/if}

    {#if interact.comments?.length}
        <div class="below-comments">
            <h5>comments</h5>
            {#each interact.comments as [text, dt]}
                <div class="comment-row">
                    <span class="comment-text">{text}</span>
                    <span class="comment-dt">{formatDate(dt)}</span>
                </div>
            {/each}
        </div>
    {/if}

    <!-- Add comment — placeholder until backend route is implemented -->
    <div class="add-comment-stub">
        <input type="text" placeholder="Add a comment..." disabled />
        <button disabled>send</button>
    </div>

</section>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .video-below {
        width: 100%;
        padding: 1rem 9% 1.5rem;
        background: #080808;
        border-bottom: 1px solid #ffffff18;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    h5 {
        font-size: 0.7rem;
        font-weight: 600;
        color: #555;
        letter-spacing: 0.05em;
        text-transform: lowercase;
        margin-bottom: 0.4rem;
    }

    /* description */
    .below-description p {
        color: #aaa;
        font-size: 0.88rem;
        line-height: 1.65;
        max-width: 52rem;
    }

    /* comments */
    .below-comments {
        max-width: 52rem;
    }

    .comment-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        padding: 0.35rem 0;
        border-bottom: 1px solid #141414;
    }

    .comment-text {
        font-size: 0.85rem;
        color: #bbb;
        flex: 1;
        min-width: 0;
    }

    .comment-dt {
        font-size: 0.72rem;
        color: #555;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* add comment stub */
    .add-comment-stub {
        display: flex;
        gap: 0.5rem;
        max-width: 32rem;
        opacity: 0.35;
    }

    .add-comment-stub input {
        flex: 1;
        background: #111;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        color: #888;
        font-size: 0.82rem;
        font-family: inherit;
        padding: 0.3rem 0.6rem;
        outline: none;
    }

    .add-comment-stub button {
        all: unset;
        cursor: not-allowed;
        font-size: 0.78rem;
        font-family: inherit;
        padding: 0.3rem 0.75rem;
        border-radius: 4px;
        border: 1px solid #2a2a2a;
        background: #111;
        color: #666;
    }
</style>
