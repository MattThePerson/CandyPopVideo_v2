<!-- pages/dashboard/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { navigate } from '../../lib/router/router.svelte';
    import ScanSection         from './ScanSection.svelte';
    import MediaSection        from './MediaSection.svelte';
    import JobLog              from './JobLog.svelte';
    import ContentFilterSection from './ContentFilterSection.svelte';
    import type { ScanOptions }  from './ScanSection.svelte';
    import type { MediaOptions } from './MediaSection.svelte';

    interface DashboardStats {
        total_videos:    number;
        linked_videos:   number;
        unlinked_videos: number;
        collections:     { name: string; count: number }[];
    }

    interface MediaTypeStatus { with: number; without: number; total: number; pct: number; }
    interface MediaStatusResponse {
        teaser_thumbs: MediaTypeStatus; seek_thumbs: MediaTypeStatus;
        teasers: MediaTypeStatus;       preview_thumbs: MediaTypeStatus;
    }

    let stats         = $state<DashboardStats | null>(null);
    let mediaStatus   = $state<MediaStatusResponse | null>(null);
    let mediaLoading  = $state(false);
    let jobRunning    = $state(false);
    let logLines      = $state<string[]>([]);
    let es: EventSource | null = null;

    async function fetchStats() {
        stats = await fetch('/api/dashboard/stats').then(r => r.json()).catch(() => null);
    }

    async function fetchMediaStatus() {
        mediaLoading = true;
        mediaStatus  = await fetch('/api/dashboard/media-status').then(r => r.json()).catch(() => null).finally(() => { mediaLoading = false; });
    }

    onMount(fetchStats);
    onDestroy(() => es?.close());

    // POSTs to endpoint then opens SSE for job output.
    async function startJob(endpoint: string, body: object = {}) {
        if (jobRunning) return;
        logLines = [];

        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }).catch(e => { logLines = [`[ERROR] ${e}`]; return null; });

        if (!res) return;
        if (res.status === 409) { logLines = ['[ERROR] A job is already running']; return; }
        if (!res.ok)            { logLines = [`[ERROR] ${res.status} ${res.statusText}`]; return; }

        jobRunning = true;
        es?.close();
        es = new EventSource('/api/dashboard/job-stream');

        es.onmessage = (e) => { logLines = [...logLines, e.data]; };

        es.addEventListener('done', () => {
            jobRunning = false;
            es?.close(); es = null;
            fetchStats();
        });

        es.onerror = () => {
            if (jobRunning) logLines = [...logLines, '[ERROR] Connection lost'];
            jobRunning = false;
            es?.close(); es = null;
        };
    }

    function handleScan(opts: ScanOptions)   { startJob('/api/dashboard/run-scan', opts); }
    function handleMedia(opts: MediaOptions)  { startJob('/api/dashboard/generate-media', opts); }
    function handleTfidf()                    { startJob('/api/dashboard/rebuild-tfidf'); }

    function fmt(n: number) { return n.toLocaleString(); }
    function pct(a: number, b: number) { return b > 0 ? ((a / b) * 100).toFixed(1) : '0.0'; }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="dashboard">

    <!-- Overview bar -->
    {#if stats}
        <div class="overview">
            <div class="overview-stats">
                <span class="stat-chip">{fmt(stats.total_videos)} videos</span>
                <span class="sep">·</span>
                <span class="stat-chip">{stats.collections.length} collections</span>
                {#if stats.unlinked_videos > 0}
                    <span class="sep">·</span>
                    <span class="stat-chip warn">{fmt(stats.unlinked_videos)} unlinked</span>
                {/if}
            </div>
            <div class="link-bar-track">
                <div class="link-bar-fill" style="width: {pct(stats.linked_videos, stats.total_videos)}%"></div>
            </div>
            <div class="coll-chips">
                {#each stats.collections as c}
                    <span class="coll-chip">{c.name} <span class="coll-count">{fmt(c.count)}</span></span>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Two-column grid -->
    <div class="grid">
        <!-- Left: controls -->
        <div class="left-col">
            <ContentFilterSection disabled={jobRunning} />
            <ScanSection  disabled={jobRunning} onStart={handleScan} />
            <MediaSection
                {stats}
                {mediaStatus}
                {mediaLoading}
                disabled={jobRunning}
                onStart={handleMedia}
                onRefreshStatus={fetchMediaStatus}
            />

            <!-- TF-IDF -->
            <section class="card">
                <h2 class="section-title">TF-IDF Model <span class="py-badge">Python</span></h2>
                <p class="card-desc">Search ranking and similar-videos. Rebuild after scanning new videos.</p>
                <button class="btn-secondary" disabled={jobRunning} onclick={handleTfidf}>
                    Rebuild TF-IDF Model
                </button>
            </section>

            <!-- Configuration -->
            <section class="card">
                <h2 class="section-title">Configuration</h2>
                <p class="card-desc">Edit config.yaml — collections, filename formats, preview media path.</p>
                <button class="btn-secondary" onclick={() => navigate('/config')}>Edit Config</button>
            </section>

            <!-- Maintenance -->
            {#if stats && stats.unlinked_videos > 0}
                <section class="card warn-card">
                    <h2 class="section-title">Maintenance</h2>
                    <p class="card-desc warn-text">
                        {fmt(stats.unlinked_videos)} videos are marked unlinked (file no longer found on disk).
                        Their interaction history is preserved. Re-scan after reconnecting drives.
                    </p>
                </section>
            {/if}
        </div>

        <!-- Right: job log (sticky) -->
        <div class="right-col">
            <JobLog lines={logLines} running={jobRunning} />
        </div>
    </div>

</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .dashboard {
        width: 100%;
        max-width: 1500px;
        padding: 1.5rem 2rem 3rem;
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
    }

    /* Overview */
    .overview {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.9rem 1.3rem;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }
    .overview-stats { display: flex; align-items: center; gap: 0.5rem; }
    .stat-chip { font-size: 0.9rem; color: #ccc; }
    .stat-chip.warn { color: #c8882a; }
    .sep { color: #333; }

    .link-bar-track { height: 3px; background: #1a2020; border-radius: 2px; overflow: hidden; }
    .link-bar-fill  { height: 100%; background: #01b8b8; border-radius: 2px; }

    .coll-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
    .coll-chip {
        font-size: 0.75rem; color: #666;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 4px; padding: 0.15rem 0.55rem;
    }
    .coll-count { color: #444; margin-left: 0.2rem; }

    /* Grid */
    .grid {
        display: grid;
        grid-template-columns: 1fr 340px;
        gap: 1.25rem;
        align-items: start;
    }

    .left-col { display: flex; flex-direction: column; gap: 1rem; }

    .right-col { position: sticky; top: 1rem; }

    /* Shared card style (for TF-IDF + Maintenance) */
    .card {
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }
    .warn-card { border-color: rgba(200, 136, 42, 0.2); }

    .section-title {
        font-size: 0.68rem; letter-spacing: 0.13em;
        text-transform: uppercase; color: #555; font-weight: 600; margin: 0;
    }

    .py-badge {
        font-size: 0.62rem; background: rgba(117, 40, 104, 0.35);
        color: #c080b8; border-radius: 3px;
        padding: 0 0.35rem; margin-left: 0.4rem;
        text-transform: none; letter-spacing: 0; font-weight: 500;
        vertical-align: middle;
    }

    .card-desc      { font-size: 0.82rem; color: #666; margin: 0; line-height: 1.5; }
    .warn-text      { color: #9a6020; }

    .btn-secondary {
        background: transparent;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #aaa; font-size: 0.83rem; border-radius: 5px;
        padding: 0.45rem 1rem; cursor: pointer; align-self: flex-start;
        transition: border-color 0.15s, color 0.15s;
    }
    .btn-secondary:hover:not(:disabled) { border-color: rgba(255,255,255,0.35); color: #ddd; }
    .btn-secondary:disabled { opacity: 0.35; cursor: not-allowed; }
</style>
