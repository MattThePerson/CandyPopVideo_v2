<!-- pages/dashboard/Page.svelte -->
<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { navigate, routerState } from '$lib/router/router.svelte';
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

    type TabId = 'worker' | 'content-filter' | 'problematic';

    function tabFromSearch(search: string): TabId {
        const t = new URLSearchParams(search).get('tab');
        if (t === 'content-filter' || t === 'problematic') return t;
        return 'worker';
    }

    function switchTab(tab: TabId) {
        activeTab = tab;
        navigate(tab === 'worker' ? '/dashboard' : `/dashboard?tab=${tab}`, { replace: true });
    }

    let stats          = $state<DashboardStats | null>(null);
    let mediaStatus    = $state<MediaStatusResponse | null>(null);
    let mediaLoading   = $state(false);
    let jobRunning     = $state(false);
    let logLines       = $state<string[]>([]);
    let overviewCounts = $state<OverviewCounts | null>(null);
    let configStatus   = $state<ConfigStatus | null>(null);
    let activeTab      = $state<TabId>(tabFromSearch(routerState.search));
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
        switchTab('worker');

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

    <!-- Tab bar -->
    <div class="tab-bar">
        <button class="tab" class:active={activeTab === 'worker'}         onclick={() => switchTab('worker')}>Worker</button>
        <button class="tab" class:active={activeTab === 'content-filter'} onclick={() => switchTab('content-filter')}>Content Filter</button>
        <button class="tab" class:active={activeTab === 'problematic'}    onclick={() => switchTab('problematic')}>Problematic Videos</button>
    </div>

    <!-- Two-column grid — always 2-col so left-col width is consistent across tabs -->
    <div class="grid">
        <div class="left-col">

            {#if activeTab === 'worker'}

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

            {:else if activeTab === 'content-filter'}

                <ContentFilterSection disabled={jobRunning} />

            {:else if activeTab === 'problematic'}

                <ProblematicVideos />

            {/if}

        </div>

        <!-- Right: job log (only rendered in worker tab) -->
        <div class="right-col">
            {#if activeTab === 'worker'}
                <JobLog lines={logLines} running={jobRunning} />
            {/if}
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
        gap: 0;
    }

    /* Top bar: edit-config button + overview side by side */
    .top-bar {
        display: flex;
        align-items: stretch;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
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

    /* Tab bar */
    .tab-bar {
        display: flex;
        gap: 0.2rem;
        margin-bottom: 1rem;
    }

    .tab {
        padding: 0.3rem 0.9rem;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.04em;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 5px;
        color: #484848;
        cursor: pointer;
        transition: color 0.12s, border-color 0.12s;
    }
    .tab:hover { color: #777; border-color: rgba(255,255,255,0.07); }
    .tab.active {
        color: #aaa;
        background: #0d1212;
        border-color: rgba(255,255,255,0.08);
    }

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
