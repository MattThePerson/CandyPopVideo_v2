<script>
    import "../app.css";
    import '../fonts.css';
    import Header from "$lib/components/Header.svelte";
    import Footer from "$lib/components/Footer.svelte";
</script>

<Header />
<main>
    <slot />
</main>
<Footer />

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
