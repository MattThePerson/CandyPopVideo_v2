<script lang="ts">
    import Spinner from './Spinner.svelte';

    type OverlayState = 'hidden' | 'drop-target' | 'loading' | 'error';

    let overlayState: OverlayState = $state('hidden');
    let errorMsg = $state('');
    let dragCount = 0;

    $effect(() => {
        function onDragEnter(e: DragEvent) {
            e.preventDefault();
            dragCount++;
            if (overlayState === 'hidden') overlayState = 'drop-target';
        }
        function onDragLeave() {
            dragCount = Math.max(0, dragCount - 1);
            if (dragCount === 0 && overlayState === 'drop-target') overlayState = 'hidden';
        }
        function onDragOver(e: DragEvent) {
            e.preventDefault();
        }
        async function onDrop(e: DragEvent) {
            e.preventDefault();
            dragCount = 0;
            if (overlayState !== 'drop-target') return;

            const file = e.dataTransfer?.files[0];
            if (!file) { overlayState = 'hidden'; return; }

            overlayState = 'loading';
            try {
                const res = await fetch(`/api/query/find-by-filename?filename=${encodeURIComponent(file.name)}`);
                const data = await res.json();
                const matches: Array<{ hash: string; title: string }> = data.matches;

                if (matches.length === 1) {
                    window.open(`/video/${matches[0].hash}`, '_blank');
                    overlayState = 'hidden';
                } else if (matches.length === 0) {
                    errorMsg = `No video found for "${file.name}"`;
                    overlayState = 'error';
                } else {
                    errorMsg = `${matches.length} videos match "${file.name}" — filename is not unique`;
                    overlayState = 'error';
                }
            } catch {
                errorMsg = 'Request failed';
                overlayState = 'error';
            }
        }

        document.addEventListener('dragenter', onDragEnter);
        document.addEventListener('dragleave', onDragLeave);
        document.addEventListener('dragover', onDragOver);
        document.addEventListener('drop', onDrop);
        return () => {
            document.removeEventListener('dragenter', onDragEnter);
            document.removeEventListener('dragleave', onDragLeave);
            document.removeEventListener('dragover', onDragOver);
            document.removeEventListener('drop', onDrop);
        };
    });

    function dismiss() {
        overlayState = 'hidden';
    }

    $effect(() => {
        if (overlayState !== 'error') return;
        function onKey() { dismiss(); }
        window.addEventListener('keydown', onKey);
        return () => window.removeEventListener('keydown', onKey);
    });
</script>

<!--
========================================================================================================================
    //region HTML
========================================================================================================================
-->

{#if overlayState !== 'hidden'}
<div
    class="backdrop"
    class:clickable={overlayState === 'error'}
    onclick={overlayState === 'error' ? dismiss : undefined}
    role="presentation"
>
    <div class="panel" class:panel-error={overlayState === 'error'}>
        {#if overlayState === 'drop-target'}
            <svg class="drop-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3v13M5 11l7 7 7-7"/>
                <path d="M3 20h18"/>
            </svg>
            <p class="label">Drop to open video</p>
        {:else if overlayState === 'loading'}
            <Spinner size={48} bg="#0a0f0f" />
        {:else if overlayState === 'error'}
            <p class="error-text">{errorMsg}</p>
            <p class="dismiss-hint">Press any key or click to dismiss</p>
        {/if}
    </div>
</div>
{/if}

<!--
========================================================================================================================
    //region CSS
========================================================================================================================
-->

<style>
    .backdrop {
        position: fixed;
        inset: 0;
        background: rgba(6, 10, 10, 0.88);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }

    .backdrop.clickable {
        cursor: pointer;
    }

    .panel {
        border: 2px dashed #3EA7A7;
        border-radius: 12px;
        padding: 3rem 4rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        background: rgba(10, 15, 15, 0.6);
        min-width: 20rem;
    }

    .panel-error {
        border-color: #c04040;
        border-style: solid;
    }

    .drop-icon {
        width: 52px;
        height: 52px;
        color: #3EA7A7;
    }

    .label {
        color: #ecede3;
        font-size: 1.1rem;
        margin: 0;
    }

    .error-text {
        color: #e07070;
        font-size: 0.95rem;
        margin: 0;
        text-align: center;
        max-width: 28rem;
    }

    .dismiss-hint {
        color: #555;
        font-size: 0.78rem;
        margin: 0;
    }
</style>
