<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';
    import type { VideoData } from '$lib/types/video';
    import Spinner from '$lib/components/Spinner.svelte';
    import CoverageBar from './CoverageBar.svelte';
    import type { ViewingRow } from './types';

    interface Entry {
        hash:       string;
        video?:     VideoData;
        viewings:   ViewingRow[];
        lastViewed: Date;
        totalSec:   number;
    }

    let loading = $state(true);
    let error   = $state<string | null>(null);
    let entries = $state<Entry[]>([]);

    function timeAgo(dt: Date): string {
        const diff = Date.now() - dt.getTime();
        const m = Math.floor(diff / 60000);
        if (m < 1)   return 'just now';
        if (m < 60)  return `${m}m ago`;
        const h = Math.floor(m / 60);
        if (h < 24)  return `${h}h ago`;
        const d = Math.floor(h / 24);
        if (d < 7)   return `${d}d ago`;
        return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }

    function fmtSec(s: number): string {
        if (s < 60)  return `${Math.round(s)}s`;
        const m = Math.floor(s / 60);
        if (m >= 60) return `${Math.floor(m / 60)}h ${m % 60}m`;
        return `${m}m`;
    }

    function coverage(viewings: ViewingRow[], duration: number): number {
        if (!duration) return 0;
        const sorted = [...viewings].sort((a, b) => a.time_start - b.time_start);
        let covered = 0, end = 0;
        for (const v of sorted) {
            if (v.time_start >= end) { covered += v.duration_sec; end = v.time_start + v.duration_sec; }
            else if (v.time_start + v.duration_sec > end) { covered += v.time_start + v.duration_sec - end; end = v.time_start + v.duration_sec; }
        }
        return Math.min(100, (covered / duration) * 100);
    }

    function getTitle(v?: VideoData): string {
        return v ? (v.scene_title || v.title || v.filename) : 'Unknown';
    }

    onMount(async () => {
        try {
            const rows: ViewingRow[] = await fetch('/api/interact/viewings?limit=500').then(r => r.json());
            const byHash = new Map<string, { viewings: ViewingRow[]; lastDt: Date; total: number }>();
            for (const v of rows) {
                if (!byHash.has(v.video_hash)) {
                    byHash.set(v.video_hash, { viewings: [], lastDt: new Date(v.datetime), total: 0 });
                }
                const e = byHash.get(v.video_hash)!;
                e.viewings.push(v);
                e.total += v.duration_sec;
                const dt = new Date(v.datetime);
                if (dt > e.lastDt) e.lastDt = dt;
            }
            const top = [...byHash.entries()].slice(0, 30);
            const videoMap = new Map<string, VideoData>();
            await Promise.all(top.map(async ([h]) => {
                try { videoMap.set(h, await fetch(`/api/get/video-data/${h}`).then(r => r.json())); }
                catch { /* ignore */ }
            }));
            entries = top.map(([hash, data]) => ({
                hash,
                video:      videoMap.get(hash),
                viewings:   data.viewings,
                lastViewed: data.lastDt,
                totalSec:   data.total,
            }));
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if loading}
    <div class="flex justify-center py-20"><Spinner /></div>
{:else if error}
    <p class="text-red-400 p-8">{error}</p>
{:else if entries.length === 0}
    <div class="empty"><p>No viewing history yet.</p></div>
{:else}
    <div class="tape-list">
        {#each entries as entry (entry.hash)}
            {@const dur  = entry.video?.duration_seconds ?? 0}
            {@const cov  = coverage(entry.viewings, dur)}
            {@const title = getTitle(entry.video)}
            <div class="tape-row">

                <button
                    type="button"
                    class="thumb-btn"
                    onclick={() => navigate(`/video/${entry.hash}`)}
                    aria-label="Watch {title}"
                >
                    <img src="/media/get/poster/{entry.hash}" alt="" class="thumb" />
                    <div class="play-hover">▶</div>
                </button>

                <div class="tape-body">
                    <div class="tape-head">
                        <div class="tape-left">
                            <div class="tape-title">{title}</div>
                            <div class="tape-meta">
                                {#if entry.video?.studio}
                                    <span class="studio">{entry.video.studio}</span>
                                {/if}
                                {#if entry.video?.actors?.length}
                                    <span class="actors">{entry.video.actors.slice(0, 3).join(', ')}</span>
                                {/if}
                            </div>
                        </div>
                        <div class="tape-right">
                            <span class="ago">{timeAgo(entry.lastViewed)}</span>
                            <button
                                type="button"
                                class="resume-btn"
                                onclick={() => navigate(`/video/${entry.hash}`)}
                            >↗ resume</button>
                        </div>
                    </div>

                    <div class="bar-row">
                        <CoverageBar viewings={entry.viewings} duration={dur} />
                    </div>

                    <div class="tape-foot">
                        <span class="watched">{fmtSec(entry.totalSec)} watched</span>
                        {#if dur > 0}<span class="cov">{cov.toFixed(0)}% coverage</span>{/if}
                        <span class="segs">{entry.viewings.length} clip{entry.viewings.length !== 1 ? 's' : ''}</span>
                    </div>
                </div>

            </div>
        {/each}
    </div>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .tape-list {
        display: flex;
        flex-direction: column;
        gap: 1px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 8px;
        overflow: hidden;
    }

    .tape-row {
        display: flex;
        gap: 1.1rem;
        background: #0e0e0e;
        padding: 0.9rem 1.1rem;
        transition: background 0.12s;
    }
    .tape-row:hover { background: #131313; }

    .thumb-btn {
        flex-shrink: 0;
        width: 72px;
        height: 100px;
        background: linear-gradient(145deg, #1a1030, #0d1a26);
        border: none;
        padding: 0;
        cursor: pointer;
        position: relative;
        border-radius: 4px;
        overflow: hidden;
    }
    .thumb { width: 100%; height: 100%; object-fit: cover; display: block; }

    .play-hover {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(0,0,0,0);
        color: white;
        font-size: 1.3rem;
        opacity: 0;
        transition: opacity 0.12s, background 0.12s;
    }
    .thumb-btn:hover .play-hover { opacity: 1; background: rgba(0,0,0,0.5); }

    .tape-body {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 0.45rem;
        justify-content: center;
    }

    .tape-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
    .tape-left { flex: 1; min-width: 0; }
    .tape-right { flex-shrink: 0; display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; }

    .tape-title {
        font-size: 0.9rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #d8d8d8;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .tape-meta { font-size: 0.75rem; color: #555; margin-top: 2px; }
    .studio { color: #3EA7A7; margin-right: 0.45rem; }
    .actors { color: #666; }

    .ago { font-size: 0.72rem; color: #4a4a4a; font-family: 'Inter', sans-serif; }

    .resume-btn {
        background: rgba(204, 105, 179, 0.1);
        border: 1px solid rgba(204, 105, 179, 0.28);
        color: rgb(204, 105, 179);
        font-size: 0.74rem;
        font-family: 'Inter', sans-serif;
        padding: 0.18rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.12s;
    }
    .resume-btn:hover { background: rgba(204, 105, 179, 0.22); }

    .tape-foot {
        display: flex;
        gap: 0.9rem;
        font-size: 0.7rem;
        font-family: 'Inter', sans-serif;
        color: #444;
    }
    .watched { color: #666; }
    .cov     { color: rgba(204, 105, 179, 0.75); }
    .segs    { color: #3a3a3a; }

    .empty { text-align: center; padding: 5rem; color: #555; }
</style>
