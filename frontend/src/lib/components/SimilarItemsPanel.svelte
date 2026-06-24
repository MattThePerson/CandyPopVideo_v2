<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';
    import Spinner from '$lib/components/Spinner.svelte';
    // @ts-ignore — no type declarations for this package
    import { detect as detectGender } from 'gender-detection';

    /* Props */
    let { type, target, onClose }: {
        type: 'performers' | 'studios';
        target: string;
        onClose: () => void;
    } = $props();

    let loading       = $state(true);
    let items         = $state<{ name: string; sim: number }[]>([]);
    let error         = $state<string | null>(null);
    let filterMale    = $state(false);
    let filterNumeric = $state(false);

    // Names come in lowercase from the DB; capitalize for dictionary lookup
    function isMale(name: string): boolean {
        const capitalized = name.replace(/\b\w/g, c => c.toUpperCase());
        return detectGender(capitalized) === 'male';
    }

    const visibleItems = $derived(items.filter(item => {
        if (filterMale    && isMale(item.name))       return false;
        if (filterNumeric && /\d/.test(item.name))    return false;
        return true;
    }));

    onMount(async () => {
        const endpoint = type === 'performers'
            ? `/api/query/get/similar-actors/${encodeURIComponent(target)}`
            : `/api/query/get/similar-studios/${encodeURIComponent(target)}`;
        try {
            const res = await fetch(endpoint);
            if (!res.ok) { error = `Request failed (${res.status})`; return; }
            const data = await res.json();
            const names: string[]               = data.NamesList  ?? [];
            const scores: Record<string, number> = data.SimScores ?? {};
            // skip index 0 — always the queried name itself
            items = names.slice(1).map(name => ({ name, sim: scores[name] ?? 0 }));
        } catch (e) {
            error = String(e);
        } finally {
            loading = false;
        }
    });

    function chipHref(name: string): string {
        const key = type === 'performers' ? 'actor' : 'studio';
        return `/search?${key}=${encodeURIComponent(name)}`;
    }

    function navChip(e: MouseEvent, name: string) {
        e.preventDefault();
        navigate(chipHref(name));
    }
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="expansion">
    <div class="expansion-header">
        <span class="expansion-title">
            similar {type} to <em>{target}</em>
        </span>
        <div class="expansion-actions">
            {#if type === 'performers'}
                <button
                    class="filter-btn"
                    class:active={filterMale}
                    onclick={() => filterMale = !filterMale}
                    title="Hide male-sounding names"
                >filter male</button>
            {/if}
            <button
                class="filter-btn"
                class:active={filterNumeric}
                onclick={() => filterNumeric = !filterNumeric}
                title="Hide names containing numbers"
            >filter numeric</button>
            <button class="close-btn" onclick={onClose} title="Close">×</button>
        </div>
    </div>

    <div class="item-list">
        {#if loading}
            <div class="status"><Spinner size={18} /></div>
        {:else if error}
            <div class="status error">{error}</div>
        {:else if visibleItems.length === 0}
            <div class="status muted">no results</div>
        {:else}
            {#each visibleItems as item}
                <a
                    class="item-chip"
                    href={chipHref(item.name)}
                    onclick={(e) => navChip(e, item.name)}
                >
                    <span class="chip-name">{item.name}</span>
                    <span class="chip-score">{(item.sim * 100).toFixed(0)}%</span>
                </a>
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
    .expansion {
        border-top: 1px solid #bbb2;
        padding: 0.4rem 0.5rem 0.5rem;
    }

    .expansion-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.4rem;
        gap: 0.5rem;
    }

    .expansion-title {
        font-size: 0.82rem;
        color: #888;
        font-family: 'Inter', sans-serif;
    }
    .expansion-title em {
        font-style: normal;
        color: #bbb;
    }

    .expansion-actions {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        flex-shrink: 0;
    }

    .filter-btn {
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        background: #111;
        color: #888;
        border: 1px solid #333;
        border-radius: 0.25rem;
        padding: 1px 6px;
        cursor: pointer;
    }
    .filter-btn:hover { color: #bbb; border-color: #555; }
    .filter-btn.active { color: #D79C29; border-color: #D79C29; }

    .close-btn {
        background: none;
        border: none;
        color: #555;
        font-size: 1.1rem;
        line-height: 1;
        cursor: pointer;
        padding: 0 2px;
    }
    .close-btn:hover { color: #ccc; }

    .item-list {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 0.5rem;
        overflow-x: auto;
        padding-bottom: 0.25rem;
        min-height: 2.5rem;
    }
    .item-list::-webkit-scrollbar       { height: 4px; }
    .item-list::-webkit-scrollbar-track { background: #111; }
    .item-list::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }

    .status {
        display: flex;
        align-items: center;
        padding: 0 0.25rem;
    }
    .status.muted { font-size: 0.85rem; color: #555; }
    .status.error { font-size: 0.85rem; color: #a04040; }

    .item-chip {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background: #0d0d0d;
        border: 1px solid #2a2a2a;
        border-radius: 1rem;
        padding: 3px 0.7rem 3px 0.7rem;
        text-decoration: none;
        white-space: nowrap;
        flex-shrink: 0;
        transition: border-color 0.1s;
    }
    .item-chip:hover { border-color: #555; }

    .chip-name {
        font-size: 0.85rem;
        color: #ccc;
    }

    .chip-score {
        font-size: 0.75rem;
        color: #555;
    }
</style>
