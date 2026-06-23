<!-- pages/video/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    import RenameOverlay from '$lib/components/RenameOverlay.svelte';
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

    let playerActive   = $state(true);
    let renameOpen     = $state(false);
    let undoInfo       = $state<{ oldFilename: string; newFilename: string } | null>(null);

    let keydownHandler: ((e: KeyboardEvent) => void) | undefined;

    $effect(() => {
        const parts: string[] = [];
        const label = video?.title || video?.scene_title || video?.filename;
        if (label)                    parts.push(label);
        if (video?.actors?.length)    parts.push(video.actors.join(', '));
        if (video?.studio)            parts.push(video.studio);
        parts.push('CandyPop');
        document.title = parts.join(' | ');
    });

    onMount(async () => {
        /* Resolve the sentinel 'random' hash to a real one and update the URL
           (replace so the back button skips the /video/random entry). */
        if (hash === 'random') {
            try {
                hash = await fetch('/api/get/random-video-hash')
                    .then(r => r.json()).then(r => r['hash'] as string);
                navigate(`/video/${hash}`, { replace: true });
            } catch (e) {
                loadError = String(e);
                return;
            }
        }

        try {
            [video, interact] = await Promise.all([
                fetch(`/api/get/video-data/${hash}`).then(r => r.json()) as Promise<VideoData>,
                fetch(`/api/interact/get/${hash}`).then(r => r.json()) as Promise<VideoInteractions>,
            ]);
        } catch (e) {
            loadError = String(e);
            return;
        }
        console.debug('video_data:', video);

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

        keydownHandler = (e: KeyboardEvent) => {
            if (e.key === 'F2' && video && !renameOpen) {
                renameOpen = true;
            }
            if (e.key === 'Escape' && undoInfo && !renameOpen) {
                undoInfo = null;
            }
        };
        window.addEventListener('keydown', keydownHandler);
    });

    onDestroy(() => {
        if (keydownHandler) window.removeEventListener('keydown', keydownHandler);
    });

    // Unloads the player, sends the rename request, restores player on any outcome.
    async function executeRename(newStem: string): Promise<{ ok: boolean; error?: string }> {
        playerActive = false;
        await tick();
        try {
            const res = await fetch(`/api/rename/${hash}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_stem: newStem }),
            });
            const data = await res.json();
            playerActive = true;
            if (!res.ok) return { ok: false, error: data.error ?? 'Rename failed' };
            const prevFilename = video!.filename;
            video = await fetch(`/api/get/video-data/${hash}`).then(r => r.json());
            renameOpen = false;
            undoInfo = { oldFilename: prevFilename, newFilename: data.new_filename as string };
            return { ok: true };
        } catch (e) {
            playerActive = true;
            return { ok: false, error: String(e) };
        }
    }

    // Optimistic — reverts undo info immediately; if undo fails, re-shows it.
    async function undoRename() {
        if (!undoInfo) return;
        const snapshot = undoInfo;
        undoInfo = null;
        const lastDot = snapshot.oldFilename.lastIndexOf('.');
        const oldStem = lastDot > 0 ? snapshot.oldFilename.slice(0, lastDot) : snapshot.oldFilename;
        const res = await fetch(`/api/rename/${hash}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ new_stem: oldStem }),
        });
        if (res.ok) {
            video = await fetch(`/api/get/video-data/${hash}`).then(r => r.json());
        } else {
            undoInfo = snapshot; // restore undo option if revert failed
        }
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="page">

    <!-- video player (unmounted during rename to release any file handle) -->
    <div class="player-wrap">
        {#if loadError}
            <div class="player-error">{loadError}</div>
        {:else if !video}
            <div class="player-center">
                <Spinner size={52} />
            </div>
        {:else if playerActive}
            <VideoPlayer
                {hash}
                title={video.filename}
                fps={video.fps}
                markers={interact?.markers ?? []}
                datedMarkers={interact?.dated_markers ?? []}
            />
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

<!-- rename overlay -->
{#if renameOpen && video}
    <RenameOverlay
        filename={video.filename}
        onClose={() => renameOpen = false}
        onRename={executeRename}
    />
{/if}

<!-- undo notification -->
{#if undoInfo}
    <div class="undo-bar">
        <span class="undo-msg">Renamed to <strong>{undoInfo.newFilename}</strong></span>
        <button class="undo-btn" onclick={undoRename}>Undo</button>
        <button class="undo-close" onclick={() => undoInfo = null} aria-label="Dismiss">✕</button>
    </div>
{/if}

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

    .undo-bar {
        position: fixed;
        bottom: 1.5rem;
        right: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: #1e1e1e;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        padding: 0.55rem 0.8rem;
        font-size: 0.83rem;
        color: #ccc;
        z-index: 900;
        max-width: min(420px, 90vw);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
    }

    .undo-msg {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .undo-btn {
        border: none;
        background: #f97316;
        color: #000;
        font-weight: 600;
        font-size: 0.78rem;
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        cursor: pointer;
        font-family: inherit;
        flex-shrink: 0;
    }

    .undo-btn:hover {
        opacity: 0.82;
    }

    .undo-close {
        border: none;
        background: none;
        color: #666;
        font-size: 0.8rem;
        cursor: pointer;
        padding: 0.1rem 0.2rem;
        line-height: 1;
        flex-shrink: 0;
    }

    .undo-close:hover {
        color: #aaa;
    }
</style>
