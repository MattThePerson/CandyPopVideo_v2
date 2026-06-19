<script lang="ts">
    import type { CatalogueTab, ItemInfo } from './types';

    /* Props */
    let { item, tab }: { item: ItemInfo; tab: CatalogueTab } = $props();

    const SEARCH_PARAM: Record<CatalogueTab, string> = {
        actors:      'actor',
        studios:     'studio',
        collections: 'collection',
        tags:        'tags',
    };

    function titleCase(s: string): string {
        return s.replace(/\b\w/g, c => c.toUpperCase());
    }

    // Returns { relative: "3 days ago", exact: "2025-06-01T14:30" }
    function formatRelativeDate(iso: string): { relative: string; exact: string } {
        const diffDays = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
        let relative: string;
        if      (diffDays === 0)   relative = 'today';
        else if (diffDays === 1)   relative = 'yesterday';
        else if (diffDays < 30)    relative = `${diffDays} days ago`;
        else if (diffDays < 365)   relative = `${Math.floor(diffDays / 30)} months ago`;
        else                       relative = `${Math.floor(diffDays / 365)} years ago`;
        return { relative, exact: iso };
    }

    const searchLink = $derived(`/search?${SEARCH_PARAM[tab]}=${encodeURIComponent(item.name)}`);
    const label      = $derived(titleCase(item.name));
    const date       = $derived(formatRelativeDate(item.newest_video));
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div class="item-row">
    <span class="new-badge">
        {#if item.new_video_count > 0}{item.new_video_count} new{/if}
    </span>
    <span class="name-section">
        <a href={searchLink} class="item-name">{label}</a>
        <span class="dot-sep"></span>
        <span class="item-count">{item.video_count}</span>
    </span>
    <span class="item-date" title={date.exact}>updated {date.relative}</span>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .item-row {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        padding: 0.2rem 0;
    }

    .new-badge {
        width: 4rem;
        text-align: right;
        color: #e03030;
        font-size: 0.8rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .name-section {
        display: flex;
        align-items: baseline;
        flex: 1;
        min-width: 0;
        gap: 0.4rem;
    }

    .item-name {
        font-size: 1rem;
        color: #ccc;
        text-decoration: none;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .item-name:hover {
        color: #ffd209;
        text-decoration: underline;
    }

    .dot-sep {
        flex: 1;
        border-bottom: 2px dotted #444;
        align-self: flex-end;
        margin-bottom: 0.25rem;
        min-width: 1rem;
    }

    .item-count {
        font-size: 1rem;
        color: #888;
        flex-shrink: 0;
    }

    .item-date {
        font-size: 0.75rem;
        color: #555;
        white-space: nowrap;
        flex-shrink: 0;
        cursor: default;
    }
</style>
