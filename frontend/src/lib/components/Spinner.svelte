<script lang="ts">
    /* Props */
    let { size = 52, bg = '#060A0A' }: { size?: number; bg?: string } = $props();
    const inner = Math.round(size * (24 / 27));
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

<div
    class="spinner"
    style="width:{size}px;height:{size}px;"
    role="status"
    aria-label="loading"
>
    <div class="inner" style="width:{inner}px;height:{inner}px;background:{bg}"></div>
</div>

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .spinner {
        border-radius: 50%;
        background: linear-gradient(0deg, rgba(255, 61, 0, 0.2) 33%, #ff3d00 100%);
        animation: spin 1s linear infinite;
        position: relative;
        flex-shrink: 0;
    }
    .inner {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        border-radius: 50%;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
