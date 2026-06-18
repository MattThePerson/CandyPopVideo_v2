<script lang="ts">
    import './app.css'
    import { onMount } from 'svelte';
    import { routerState, initRouter, matchRoute } from './lib/router/router.svelte';
    import Header from './lib/components/Header.svelte';
    import Footer from './lib/components/Footer.svelte';

    onMount(() => initRouter());

    let match = $derived(matchRoute(routerState.path));
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<Header />

<main class="flex flex-col items-center min-h-[40rem]">
    {#if match}
        {@const PageComponent = match.route.component}
        <PageComponent {...match.params} />
    {:else}
        <p class="p-8">Page not found.</p>
    {/if}
</main>

<Footer />
