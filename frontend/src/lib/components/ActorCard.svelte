<script lang="ts">
    import { onMount } from 'svelte';
    import { navigate } from '$lib/router/router.svelte';

    /* Props */
    let { name, dateReleased = '' }: { name: string; dateReleased?: string } = $props();

    let profilePic = $state<string | null>(null);
    let videoCount = $state<number | null>(null);
    let ageAtScene = $state<number | null>(null);
    let aka        = $state<string | null>(null);

    function searchLink() {
        return `/search?actor=${encodeURIComponent(name)}`;
    }

    function navSearch(e: MouseEvent) {
        e.preventDefault();
        navigate(searchLink());
    }

    function yearDiff(dob: string, ref: string): number | null {
        if (!dob || dob.length < 4 || !ref || ref.length < 4) return null;
        const refDate = ref.length === 4 ? ref + '-06-01' : ref;
        const a = Date.parse(dob);
        const b = Date.parse(refDate);
        if (isNaN(a) || isNaN(b)) return null;
        return Math.max(Math.floor((b - a) / (1000 * 60 * 60 * 24 * 365)), 18);
    }

    onMount(async () => {
        const [infoRes, countRes] = await Promise.allSettled([
            fetch(`/api/get/actor/${encodeURIComponent(name)}`).then(r => r.ok ? r.json() : null),
            fetch(`/api/get/actor-video-count/${encodeURIComponent(name)}`).then(r => r.ok ? r.json() : null),
        ]);

        if (infoRes.status === 'fulfilled' && infoRes.value) {
            const data = infoRes.value;
            if (data.galleries?.length) profilePic = `/static/actor-store${data.galleries[0]}`;
            if (data.aka?.length)       aka = Array.isArray(data.aka) ? data.aka[0] : data.aka;
            if (data.date_of_birth)     ageAtScene = yearDiff(data.date_of_birth, dateReleased);
        }
        if (countRes.status === 'fulfilled' && countRes.value) {
            videoCount = countRes.value.video_count ?? null;
        }
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<a class="actor-card" href={searchLink()} onclick={navSearch} title={aka ? `actor (aka: ${aka})` : 'actor'}>
    <div class="pic-container">
        {#if profilePic}
            <img src={profilePic} alt={name} />
        {:else}
            <svg class="placeholder" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="256" cy="130" rx="110" ry="130"/>
                <path d="M36,478C36,391,134,320,256,320s220,71,220,158C476,497,461,512,442,512H70C51,512,36,497,36,478z"/>
            </svg>
        {/if}
    </div>
    <div class="info">
        <div class="name">{name}</div>
        <div class="meta">{videoCount !== null ? `${videoCount} videos` : '·'}</div>
        {#if ageAtScene !== null}
            <div class="meta age" title="Age at time of scene">{ageAtScene} y/o ITS</div>
        {/if}
    </div>
</a>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .actor-card {
        display: flex;
        align-items: center;
        background: #000;
        text-decoration: none;
        border-radius: 3rem;
        border: 1px solid #ffffff22;
        transition: box-shadow 0.15s;
    }
    .actor-card:hover { box-shadow: inset 0 0 6px #ffffff22; }

    .pic-container {
        --s: 4.5rem;
        width: var(--s);
        height: var(--s);
        min-width: var(--s);
        background: #3a3a3a;
        border-radius: 50%;
        overflow: hidden;
        display: flex;
        align-items: flex-end;
        justify-content: center;
    }
    .actor-card:hover .pic-container { outline: 1px solid #ffffff33; }

    img {
        width: 100%;
        height: auto;
        transform: scale(200%) translateY(-5%);
        transform-origin: top center;
        display: block;
    }

    .placeholder {
        width: 80%;
        height: 80%;
        fill: #111;
        transform: translateY(0.35rem);
    }

    .info {
        padding: 4px 1.4rem 4px 0.5rem;
        white-space: nowrap;
        min-width: 5rem;
    }

    .name {
        font-size: 15px;
        color: #eee;
        font-weight: 500;
    }

    .meta {
        font-size: 12px;
        color: #777;
        margin-left: 0.3rem;
        margin-top: 1px;
    }

    .age { color: #666; }
</style>
