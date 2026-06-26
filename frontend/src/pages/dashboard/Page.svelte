<!-- pages/dashboard/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import ScanTfidfSection      from './ScanTfidfSection.svelte';
    import MediaSection          from './MediaSection.svelte';
    import JobLog                from './JobLog.svelte';
    import ContentFilterSection  from './ContentFilterSection.svelte';
    import ProblematicVideos     from './ProblematicVideos.svelte';
    import type { ScanOptions }  from './ScanTfidfSection.svelte';
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

    interface OverviewCounts { videos: number; collections: number; studios: number; actors: number; }
    interface ConfigStatus   { ok: boolean; errors: string[]; warnings: string[]; }

    let stats          = $state<DashboardStats | null>(null);
    let mediaStatus    = $state<MediaStatusResponse | null>(null);
    let mediaLoading   = $state(false);
    let jobRunning     = $state(false);
    let logLines       = $state<string[]>([]);
    let overviewCounts = $state<OverviewCounts | null>(null);
    let configStatus   = $state<ConfigStatus | null>(null);
    let es: EventSource | null = null;

    async function fetchStats() {
        stats = await fetch('/api/dashboard/stats').then(r => r.json()).catch(() => null);
    }

    async function fetchMediaStatus() {
        mediaLoading = true;
        mediaStatus  = await fetch('/api/dashboard/media-status').then(r => r.json()).catch(() => null).finally(() => { mediaLoading = false; });
    }

    // Derives filter-aware counts from the catalogue endpoint (which applies global filter).
    async function fetchOverviewCounts() {
        const res = await fetch('/api/query/get/catalogue', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ query_type: '', query_string: '', use_primary_actors: false, filter_actor: '', filter_studio: '', filter_collection: '', filter_tag: '' }),
        }).catch(() => null);
        if (!res?.ok) return;
        const cat = await res.json();
        overviewCounts = {
            videos:      (cat.collection_info ?? []).reduce((s: number, c: any) => s + (c.video_count ?? 0), 0),
            collections: cat.collection_info?.length  ?? 0,
            studios:     cat.studio_info?.length      ?? 0,
            actors:      cat.actor_info?.length       ?? 0,
        };
    }

    async function fetchConfigStatus() {
        const raw = await fetch('/api/config').then(r => r.ok ? r.text() : null).catch(() => null);
        if (!raw) return;
        configStatus = await fetch('/api/config/validate', {
            method:  'POST',
            headers: { 'Content-Type': 'text/plain' },
            body:    raw,
        }).then(r => r.json()).catch(() => null);
    }

    onMount(() => { document.title = 'Dashboard | CandyPop'; });
    onMount(fetchStats);
    onMount(fetchOverviewCounts);
    onMount(fetchConfigStatus);
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

        es.onmessage = (e) => {
            const line = e.data;
            if (line.startsWith('[SCAN] Processed')) {
                const last = logLines.findLastIndex(l => l.startsWith('[SCAN] Processed'));
                if (last >= 0) {
                    logLines = [...logLines.slice(0, last), line, ...logLines.slice(last + 1)];
                    return;
                }
            }
            logLines = [...logLines, line];
        };

        es.addEventListener('done', () => {
            jobRunning = false;
            es?.close(); es = null;
            fetchStats();
            fetchOverviewCounts();
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

    let configHasIssues = $derived(
        configStatus != null && (!configStatus.ok || configStatus.warnings.length > 0)
    );
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="dashboard">

    <!-- Top bar: edit config + stats overview -->
    <div class="top-bar">
        <a href="/config" class="edit-config-btn" class:has-issues={configHasIssues}>
            {#if configHasIssues}<span class="warn-icon">⚠</span>{/if}
            Edit Config
        </a>

        <div class="overview">
            {#if overviewCounts}
                <div class="overview-stats">
                    <span class="stat-chip">{fmt(overviewCounts.videos)} videos</span>
                    <span class="sep">·</span>
                    <span class="stat-chip">{overviewCounts.collections} collections</span>
                    <span class="sep">·</span>
                    <span class="stat-chip">{fmt(overviewCounts.studios)} studios</span>
                    <span class="sep">·</span>
                    <span class="stat-chip">{fmt(overviewCounts.actors)} actors</span>
                    {#if stats && stats.unlinked_videos > 0}
                        <span class="sep">·</span>
                        <span class="stat-chip warn">{fmt(stats.unlinked_videos)} unlinked</span>
                    {/if}
                </div>
            {/if}
        </div>
    </div>

    <!-- Two-column grid -->
    <div class="grid">
        <!-- Left: controls -->
        <div class="left-col">

            <!-- Scan + TF-IDF  |  Media Generation -->
            <div class="ops-row">
                <ScanTfidfSection
                    disabled={jobRunning}
                    onStartScan={handleScan}
                    onStartTfidf={handleTfidf}
                />
                <MediaSection
                    {stats}
                    {mediaStatus}
                    {mediaLoading}
                    disabled={jobRunning}
                    onStart={handleMedia}
                    onRefreshStatus={fetchMediaStatus}
                />
            </div>

            <!-- Content Filters -->
            <ContentFilterSection disabled={jobRunning} />

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

            <!-- Problematic videos -->
            <ProblematicVideos />
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

    /* Top bar: edit-config button + overview side by side */
    .top-bar {
        display: flex;
        align-items: stretch;
        gap: 0.75rem;
    }

    .edit-config-btn {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        white-space: nowrap;
        padding: 0.7rem 1.1rem;
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        color: #888;
        font-size: 0.83rem;
        text-decoration: none;
        transition: border-color 0.15s, color 0.15s;
        flex-shrink: 0;
    }
    .edit-config-btn:hover { border-color: rgba(255,255,255,0.18); color: #bbb; }
    .edit-config-btn.has-issues { border-color: rgba(200, 136, 42, 0.3); }

    .warn-icon { color: #c8882a; font-size: 0.78rem; }

    /* Overview */
    .overview {
        flex: 1;
        background: #0d1212;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 8px;
        padding: 0.9rem 1.4rem;
        display: flex;
        align-items: center;
    }
    .overview-stats {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        flex-wrap: wrap;
    }
    .stat-chip { font-size: 1.05rem; font-weight: 500; color: #dcddd4; }
    .stat-chip.warn { color: #c8882a; }
    .sep { color: #2a2a2a; font-size: 1.1rem; }

    /* Grid */
    .grid {
        display: grid;
        grid-template-columns: 1fr 340px;
        gap: 1.25rem;
        align-items: start;
    }

    .left-col { display: flex; flex-direction: column; gap: 1rem; }
    .right-col { position: sticky; top: 1rem; }

    /* Scan+TF-IDF and Media side by side */
    .ops-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        align-items: start;
    }

    /* Shared card style */
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

    .card-desc  { font-size: 0.82rem; color: #666; margin: 0; line-height: 1.5; }
    .warn-text  { color: #9a6020; }
</style>
