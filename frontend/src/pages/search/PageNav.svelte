<script lang="ts">
    /* Props */
    let {
        page,
        totalPages,
        onNavigate,
    }: {
        page:       number;
        totalPages: number;
        onNavigate: (p: number) => void;
    } = $props();

    /* Builds the list of page slots to render, inserting '...' where pages are skipped. */
    function pageList(current: number, total: number): (number | '...')[] {
        if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
        const left  = Math.max(2,         current - 1);
        const right = Math.min(total - 1, current + 1);
        return [
            1,
            ...(left  > 2         ? ['...' as const] : []),
            ...Array.from({ length: right - left + 1 }, (_, i) => left + i),
            ...(right < total - 1 ? ['...' as const] : []),
            total,
        ];
    }

    const slots = $derived(pageList(page, totalPages));
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<nav class="page-nav">
    <button
        class="nav-btn"
        disabled={page <= 1}
        onclick={() => onNavigate(page - 1)}
    >←</button>

    {#each slots as slot}
        {#if slot === '...'}
            <span class="ellipsis">…</span>
        {:else}
            <button
                class="page-btn"
                class:active={slot === page}
                onclick={() => onNavigate(slot)}
            >{slot}</button>
        {/if}
    {/each}

    <button
        class="nav-btn"
        disabled={page >= totalPages}
        onclick={() => onNavigate(page + 1)}
    >→</button>
</nav>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .page-nav {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
        margin-top: 2rem;
        padding-bottom: 1rem;
    }

    .nav-btn,
    .page-btn {
        background: #111;
        color: #aaa;
        border: 1px solid #2a2a2a;
        border-radius: 4px;
        padding: 0.3rem 0.65rem;
        font-size: 0.85rem;
        cursor: pointer;
        transition: border-color 0.12s, color 0.12s;
        min-width: 2.1rem;
    }

    .nav-btn:hover:not(:disabled),
    .page-btn:hover:not(.active) {
        border-color: #555;
        color: #eee;
    }

    .nav-btn:disabled {
        opacity: 0.25;
        cursor: default;
    }

    .page-btn.active {
        border-color: #752868;
        color: #fff;
        background: #2a0f25;
        cursor: default;
    }

    .ellipsis {
        color: #444;
        font-size: 0.85rem;
        padding: 0 0.2rem;
        user-select: none;
    }
</style>
