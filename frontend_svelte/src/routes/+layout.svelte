<script>
    import { onMount } from "svelte";
    import "../app.css";
    import '../fonts.css';
    import Header from "$lib/components/Header.svelte";
    import Footer from "$lib/components/Footer.svelte";
    
    let showFooter = false;
    onMount(() => {
        console.log(window.location.pathname);
        showFooter = (window.location.pathname !== '/catalogue');
        console.log(showFooter);
    });
    
</script>

<Header />
<main>
    <slot />
</main>
{#if showFooter}
    <Footer />
{/if}

<style>
    main {
        min-height: 40rem;
        padding: 1rem;
        display: flex;
        justify-content: center;
    }
    
    :global {
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            color: white;
        }

        body {
            background: #040404;
        }
    }
</style>
