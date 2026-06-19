<script lang="ts">
    import { tick } from 'svelte';

    /* Props */
    let { lines, running }: { lines: string[]; running: boolean } = $props();

    let logEl: HTMLDivElement | undefined;

    // Scroll to bottom whenever lines change
    $effect(() => {
        void lines.length;
        tick().then(() => { if (logEl) logEl.scrollTop = logEl.scrollHeight; });
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="log-card">
    <div class="log-header">
        <span class="log-title">JOB OUTPUT</span>
        {#if running}
            <span class="dot running"></span>
            <span class="status-label">Running</span>
        {:else if lines.length > 0}
            <span class="dot done"></span>
            <span class="status-label">Done</span>
        {:else}
            <span class="status-label idle">Idle</span>
        {/if}
    </div>
    <div class="log-body" bind:this={logEl}>
        {#if lines.length === 0}
            <span class="empty">No job output yet. Start a scan or media generation to see output here.</span>
        {:else}
            {#each lines as line (line)}
                <div class="line">{line}</div>
            {/each}
        {/if}
    </div>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .log-card {
        background: #090d0d;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        height: calc(100vh - 5.5rem);
        min-height: 280px;
    }

    .log-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.65rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        flex-shrink: 0;
    }

    .log-title {
        font-size: 0.68rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        color: #444;
        font-weight: 600;
        flex: 1;
    }

    .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .dot.running { background: #01b8b8; animation: pulse 1.2s ease-in-out infinite; }
    .dot.done    { background: #4caf50; }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.25; }
    }

    .status-label      { font-size: 0.72rem; color: #555; }
    .status-label.idle { color: #2e2e2e; }

    .log-body {
        flex: 1;
        overflow-y: auto;
        padding: 0.75rem 1rem;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.77rem;
        line-height: 1.65;
        color: #999;
    }

    .empty {
        color: #2e2e2e;
        font-style: italic;
        font-family: inherit;
    }

    .line {
        white-space: pre-wrap;
        word-break: break-all;
    }
</style>
